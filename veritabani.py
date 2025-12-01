# -*- coding: utf-8 -*-
"""
Not Defteri Uygulaması - Veritabanı Modülü
SQLite veritabanı işlemlerini yönetir.

Yazar: Claude AI
Tarih: 2024
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple, Any
from contextlib import contextmanager


class VeritabaniYoneticisi:
    """
    SQLite veritabanı işlemlerini yöneten sınıf.
    Notlar, kategoriler, etiketler ve hatırlatıcılar için CRUD işlemleri sağlar.
    """

    def __init__(self, veritabani_yolu: str = None):
        """
        Veritabanı yöneticisini başlatır.

        Args:
            veritabani_yolu: Veritabanı dosyasının yolu. None ise varsayılan konum kullanılır.
        """
        if veritabani_yolu is None:
            # Uygulamanın çalıştığı klasöre kaydet
            uygulama_klasoru = os.path.dirname(os.path.abspath(__file__))
            veritabani_yolu = os.path.join(uygulama_klasoru, 'notlar.db')

        self.veritabani_yolu = veritabani_yolu
        self._tablolari_olustur()

    @contextmanager
    def _baglanti_al(self):
        """Veritabanı bağlantısı için context manager."""
        baglanti = sqlite3.connect(self.veritabani_yolu)
        baglanti.row_factory = sqlite3.Row
        try:
            yield baglanti
            baglanti.commit()
        except Exception as e:
            baglanti.rollback()
            raise e
        finally:
            baglanti.close()

    def _temizle_unicode(self, metin: str) -> str:
        """Geçersiz Unicode karakterleri temizler."""
        if metin is None:
            return None
        # Surrogate karakterleri temizle
        return metin.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='replace')

    def _tablolari_olustur(self):
        """Gerekli veritabanı tablolarını oluşturur."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()

            # Kategoriler tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS kategoriler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL UNIQUE,
                    renk TEXT DEFAULT '#3498db',
                    ikon TEXT DEFAULT '📁',
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Notlar tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS notlar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    baslik TEXT NOT NULL,
                    icerik TEXT,
                    zengin_icerik TEXT,
                    kategori_id INTEGER,
                    favori INTEGER DEFAULT 0,
                    silindi INTEGER DEFAULT 0,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (kategori_id) REFERENCES kategoriler(id)
                )
            ''')

            # Etiketler tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS etiketler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL UNIQUE,
                    renk TEXT DEFAULT '#9b59b6'
                )
            ''')

            # Not-Etiket ilişki tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS not_etiketleri (
                    not_id INTEGER,
                    etiket_id INTEGER,
                    PRIMARY KEY (not_id, etiket_id),
                    FOREIGN KEY (not_id) REFERENCES notlar(id) ON DELETE CASCADE,
                    FOREIGN KEY (etiket_id) REFERENCES etiketler(id) ON DELETE CASCADE
                )
            ''')

            # Hatırlatıcılar tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS hatirlaticilar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    not_id INTEGER,
                    hatirlatma_zamani TIMESTAMP NOT NULL,
                    mesaj TEXT,
                    aktif INTEGER DEFAULT 1,
                    FOREIGN KEY (not_id) REFERENCES notlar(id) ON DELETE CASCADE
                )
            ''')

            # Ayarlar tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS ayarlar (
                    anahtar TEXT PRIMARY KEY,
                    deger TEXT
                )
            ''')

            # Sürüm geçmişi tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS surum_gecmisi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    not_id INTEGER NOT NULL,
                    baslik TEXT,
                    icerik TEXT,
                    zengin_icerik TEXT,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (not_id) REFERENCES notlar(id) ON DELETE CASCADE
                )
            ''')

            # Git repoları tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS git_repolar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    isim TEXT NOT NULL,
                    son_commit_hash TEXT,
                    son_kontrol TEXT,
                    guncellendi INTEGER DEFAULT 0,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Uygulama ayarları tablosu
            imleç.execute('''
                CREATE TABLE IF NOT EXISTS ayarlar (
                    anahtar TEXT PRIMARY KEY,
                    deger TEXT
                )
            ''')

            # Varsayılan kategori ekle
            imleç.execute('''
                INSERT OR IGNORE INTO kategoriler (ad, renk, ikon)
                VALUES ('Genel', '#3498db', '📝')
            ''')

    # ==================== KATEGORİ İŞLEMLERİ ====================

    def kategori_ekle(self, ad: str, renk: str = '#3498db', ikon: str = '📁') -> int:
        """
        Yeni kategori ekler.

        Args:
            ad: Kategori adı
            renk: Kategori rengi (hex)
            ikon: Kategori ikonu (emoji)

        Returns:
            Oluşturulan kategorinin ID'si
        """
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute(
                'INSERT INTO kategoriler (ad, renk, ikon) VALUES (?, ?, ?)',
                (ad, renk, ikon)
            )
            return imleç.lastrowid

    def kategori_guncelle(self, kategori_id: int, ad: str = None, renk: str = None, ikon: str = None):
        """Mevcut kategoriyi günceller."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            guncellemeler = []
            degerler = []

            if ad is not None:
                guncellemeler.append('ad = ?')
                degerler.append(ad)
            if renk is not None:
                guncellemeler.append('renk = ?')
                degerler.append(renk)
            if ikon is not None:
                guncellemeler.append('ikon = ?')
                degerler.append(ikon)

            if guncellemeler:
                degerler.append(kategori_id)
                imleç.execute(
                    f'UPDATE kategoriler SET {", ".join(guncellemeler)} WHERE id = ?',
                    degerler
                )

    def kategori_sil(self, kategori_id: int):
        """Kategoriyi siler. İlişkili notlar 'Genel' kategorisine taşınır."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            # Önce genel kategorinin ID'sini bul
            imleç.execute('SELECT id FROM kategoriler WHERE ad = "Genel"')
            genel = imleç.fetchone()
            if genel:
                # Notları genel kategoriye taşı
                imleç.execute(
                    'UPDATE notlar SET kategori_id = ? WHERE kategori_id = ?',
                    (genel['id'], kategori_id)
                )
            # Kategoriyi sil
            imleç.execute('DELETE FROM kategoriler WHERE id = ? AND ad != "Genel"', (kategori_id,))

    def kategorileri_getir(self) -> List[dict]:
        """Tüm kategorileri getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                SELECT k.*, COUNT(n.id) as not_sayisi
                FROM kategoriler k
                LEFT JOIN notlar n ON k.id = n.kategori_id AND n.silindi = 0
                GROUP BY k.id
                ORDER BY k.ad
            ''')
            return [dict(row) for row in imleç.fetchall()]

    def kategori_getir(self, kategori_id: int) -> Optional[dict]:
        """Belirli bir kategoriyi getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('SELECT * FROM kategoriler WHERE id = ?', (kategori_id,))
            satir = imleç.fetchone()
            return dict(satir) if satir else None

    # ==================== NOT İŞLEMLERİ ====================

    def not_ekle(self, baslik: str, icerik: str = '', zengin_icerik: str = '',
                 kategori_id: int = None, etiket_idleri: List[int] = None) -> int:
        """
        Yeni not ekler.

        Args:
            baslik: Not başlığı
            icerik: Düz metin içerik
            zengin_icerik: HTML formatında zengin içerik
            kategori_id: Kategori ID'si
            etiket_idleri: Etiket ID'leri listesi

        Returns:
            Oluşturulan notun ID'si
        """
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()

            # Kategori belirtilmemişse genel kategoriyi kullan
            if kategori_id is None:
                imleç.execute('SELECT id FROM kategoriler WHERE ad = "Genel"')
                genel = imleç.fetchone()
                if genel:
                    kategori_id = genel['id']

            simdi = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            imleç.execute('''
                INSERT INTO notlar (baslik, icerik, zengin_icerik, kategori_id,
                                   olusturma_tarihi, guncelleme_tarihi)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (baslik, icerik, zengin_icerik, kategori_id, simdi, simdi))

            not_id = imleç.lastrowid

            # Etiketleri ekle
            if etiket_idleri:
                for etiket_id in etiket_idleri:
                    imleç.execute(
                        'INSERT OR IGNORE INTO not_etiketleri (not_id, etiket_id) VALUES (?, ?)',
                        (not_id, etiket_id)
                    )

            return not_id

    def not_guncelle(self, not_id: int, baslik: str = None, icerik: str = None,
                     zengin_icerik: str = None, kategori_id: int = None,
                     favori: bool = None, etiket_idleri: List[int] = None):
        """Mevcut notu günceller."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            guncellemeler = ['guncelleme_tarihi = ?']
            degerler = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]

            if baslik is not None:
                guncellemeler.append('baslik = ?')
                degerler.append(self._temizle_unicode(baslik))
            if icerik is not None:
                guncellemeler.append('icerik = ?')
                degerler.append(self._temizle_unicode(icerik))
            if zengin_icerik is not None:
                guncellemeler.append('zengin_icerik = ?')
                degerler.append(self._temizle_unicode(zengin_icerik))
            if kategori_id is not None:
                guncellemeler.append('kategori_id = ?')
                degerler.append(kategori_id)
            if favori is not None:
                guncellemeler.append('favori = ?')
                degerler.append(1 if favori else 0)

            degerler.append(not_id)
            imleç.execute(
                f'UPDATE notlar SET {", ".join(guncellemeler)} WHERE id = ?',
                degerler
            )

            # Etiketleri güncelle
            if etiket_idleri is not None:
                imleç.execute('DELETE FROM not_etiketleri WHERE not_id = ?', (not_id,))
                for etiket_id in etiket_idleri:
                    imleç.execute(
                        'INSERT OR IGNORE INTO not_etiketleri (not_id, etiket_id) VALUES (?, ?)',
                        (not_id, etiket_id)
                    )

    def not_sil(self, not_id: int, kalici: bool = False):
        """
        Notu siler.

        Args:
            not_id: Silinecek notun ID'si
            kalici: True ise kalıcı olarak siler, False ise çöp kutusuna taşır
        """
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            if kalici:
                imleç.execute('DELETE FROM notlar WHERE id = ?', (not_id,))
            else:
                imleç.execute('UPDATE notlar SET silindi = 1 WHERE id = ?', (not_id,))

    def not_geri_yukle(self, not_id: int):
        """Çöp kutusundan notu geri yükler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('UPDATE notlar SET silindi = 0 WHERE id = ?', (not_id,))

    def cop_kutusundaki_notlar(self) -> List[dict]:
        """Çöp kutusundaki notları döndürür (silmeden önce resimleri almak için)."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('SELECT id, icerik, zengin_icerik FROM notlar WHERE silindi = 1')
            return [dict(row) for row in imleç.fetchall()]

    def cop_kutusunu_bosalt(self):
        """Çöp kutusundaki tüm notları kalıcı olarak siler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('DELETE FROM notlar WHERE silindi = 1')

    def notlari_getir(self, kategori_id: int = None, sadece_favoriler: bool = False,
                      silinen: bool = False, arama_metni: str = None,
                      etiket_id: int = None, siralama: str = 'guncelleme_tarihi DESC') -> List[dict]:
        """
        Notları filtreli olarak getirir.

        Args:
            kategori_id: Belirli kategorideki notları filtreler
            sadece_favoriler: Sadece favori notları getirir
            silinen: Çöp kutusundaki notları getirir
            arama_metni: Başlık ve içerikte arama yapar
            etiket_id: Belirli etikete sahip notları getirir
            siralama: Sıralama kriteri

        Returns:
            Not listesi
        """
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()

            sorgu = '''
                SELECT DISTINCT n.*, k.ad as kategori_adi, k.renk as kategori_rengi, k.ikon as kategori_ikonu
                FROM notlar n
                LEFT JOIN kategoriler k ON n.kategori_id = k.id
                LEFT JOIN not_etiketleri ne ON n.id = ne.not_id
                WHERE 1=1
            '''
            parametreler = []

            # Silinmiş durumu filtresi
            sorgu += ' AND n.silindi = ?'
            parametreler.append(1 if silinen else 0)

            if kategori_id is not None:
                sorgu += ' AND n.kategori_id = ?'
                parametreler.append(kategori_id)

            if sadece_favoriler:
                sorgu += ' AND n.favori = 1'

            if arama_metni:
                sorgu += ' AND (n.baslik LIKE ? OR n.icerik LIKE ?)'
                arama = f'%{arama_metni}%'
                parametreler.extend([arama, arama])

            if etiket_id is not None:
                sorgu += ' AND ne.etiket_id = ?'
                parametreler.append(etiket_id)

            sorgu += f' ORDER BY {siralama}'

            imleç.execute(sorgu, parametreler)
            notlar = []
            for satir in imleç.fetchall():
                not_dict = dict(satir)
                # Notun etiketlerini getir
                imleç.execute('''
                    SELECT e.* FROM etiketler e
                    JOIN not_etiketleri ne ON e.id = ne.etiket_id
                    WHERE ne.not_id = ?
                ''', (not_dict['id'],))
                not_dict['etiketler'] = [dict(e) for e in imleç.fetchall()]
                notlar.append(not_dict)

            return notlar

    def not_getir(self, not_id: int) -> Optional[dict]:
        """Belirli bir notu getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                SELECT n.*, k.ad as kategori_adi, k.renk as kategori_rengi
                FROM notlar n
                LEFT JOIN kategoriler k ON n.kategori_id = k.id
                WHERE n.id = ?
            ''', (not_id,))
            satir = imleç.fetchone()
            if satir:
                not_dict = dict(satir)
                # Etiketleri getir
                imleç.execute('''
                    SELECT e.* FROM etiketler e
                    JOIN not_etiketleri ne ON e.id = ne.etiket_id
                    WHERE ne.not_id = ?
                ''', (not_id,))
                not_dict['etiketler'] = [dict(e) for e in imleç.fetchall()]
                return not_dict
            return None

    def favori_durumu_degistir(self, not_id: int) -> bool:
        """Notun favori durumunu değiştirir ve yeni durumu döndürür."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('SELECT favori FROM notlar WHERE id = ?', (not_id,))
            satir = imleç.fetchone()
            if satir:
                yeni_durum = 0 if satir['favori'] else 1
                imleç.execute('UPDATE notlar SET favori = ? WHERE id = ?', (yeni_durum, not_id))
                return bool(yeni_durum)
            return False

    # ==================== ETİKET İŞLEMLERİ ====================

    def etiket_ekle(self, ad: str, renk: str = '#9b59b6') -> int:
        """Yeni etiket ekler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('INSERT INTO etiketler (ad, renk) VALUES (?, ?)', (ad, renk))
            return imleç.lastrowid

    def etiket_guncelle(self, etiket_id: int, ad: str = None, renk: str = None):
        """Mevcut etiketi günceller."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            guncellemeler = []
            degerler = []

            if ad is not None:
                guncellemeler.append('ad = ?')
                degerler.append(ad)
            if renk is not None:
                guncellemeler.append('renk = ?')
                degerler.append(renk)

            if guncellemeler:
                degerler.append(etiket_id)
                imleç.execute(
                    f'UPDATE etiketler SET {", ".join(guncellemeler)} WHERE id = ?',
                    degerler
                )

    def etiket_sil(self, etiket_id: int):
        """Etiketi siler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('DELETE FROM etiketler WHERE id = ?', (etiket_id,))

    def etiketleri_getir(self) -> List[dict]:
        """Tüm etiketleri getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                SELECT e.*, COUNT(ne.not_id) as not_sayisi
                FROM etiketler e
                LEFT JOIN not_etiketleri ne ON e.id = ne.etiket_id
                GROUP BY e.id
                ORDER BY e.ad
            ''')
            return [dict(row) for row in imleç.fetchall()]

    # ==================== HATIRLATICI İŞLEMLERİ ====================

    def hatirlatici_ekle(self, not_id: int, hatirlatma_zamani: datetime, mesaj: str = '') -> int:
        """Yeni hatırlatıcı ekler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                INSERT INTO hatirlaticilar (not_id, hatirlatma_zamani, mesaj)
                VALUES (?, ?, ?)
            ''', (not_id, hatirlatma_zamani.strftime('%Y-%m-%d %H:%M:%S'), mesaj))
            return imleç.lastrowid

    def hatirlatici_sil(self, hatirlatici_id: int):
        """Hatırlatıcıyı siler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('DELETE FROM hatirlaticilar WHERE id = ?', (hatirlatici_id,))

    def aktif_hatirlaticlari_getir(self) -> List[dict]:
        """Aktif ve zamanı gelen hatırlatıcıları getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            simdi = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            imleç.execute('''
                SELECT h.*, n.baslik as not_baslik
                FROM hatirlaticilar h
                JOIN notlar n ON h.not_id = n.id
                WHERE h.aktif = 1 AND h.hatirlatma_zamani <= ?
                ORDER BY h.hatirlatma_zamani
            ''', (simdi,))
            return [dict(row) for row in imleç.fetchall()]

    def notun_hatirlaticilari(self, not_id: int) -> List[dict]:
        """Belirli bir notun hatırlatıcılarını getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                SELECT * FROM hatirlaticilar
                WHERE not_id = ? AND aktif = 1
                ORDER BY hatirlatma_zamani
            ''', (not_id,))
            return [dict(row) for row in imleç.fetchall()]

    def hatirlatiyi_deaktif_et(self, hatirlatici_id: int):
        """Hatırlatıcıyı deaktif eder."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('UPDATE hatirlaticilar SET aktif = 0 WHERE id = ?', (hatirlatici_id,))

    # ==================== AYAR İŞLEMLERİ ====================

    def ayar_kaydet(self, anahtar: str, deger: str):
        """Ayar kaydeder veya günceller."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                INSERT OR REPLACE INTO ayarlar (anahtar, deger) VALUES (?, ?)
            ''', (anahtar, deger))

    def ayar_getir(self, anahtar: str, varsayilan: str = None) -> Optional[str]:
        """Ayar değerini getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('SELECT deger FROM ayarlar WHERE anahtar = ?', (anahtar,))
            satir = imleç.fetchone()
            return satir['deger'] if satir else varsayilan

    # ==================== SÜRÜM GEÇMİŞİ İŞLEMLERİ ====================

    def surum_ekle(self, not_id: int, baslik: str, icerik: str, zengin_icerik: str) -> int:
        """Yeni sürüm ekler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            tarih = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Unicode karakterleri temizle
            baslik = self._temizle_unicode(baslik)
            icerik = self._temizle_unicode(icerik)
            zengin_icerik = self._temizle_unicode(zengin_icerik)
            imleç.execute('''
                INSERT INTO surum_gecmisi (not_id, baslik, icerik, zengin_icerik, tarih)
                VALUES (?, ?, ?, ?, ?)
            ''', (not_id, baslik, icerik, zengin_icerik, tarih))
            return imleç.lastrowid

    def surumleri_getir(self, not_id: int) -> List[dict]:
        """Notun tüm sürümlerini getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                SELECT * FROM surum_gecmisi
                WHERE not_id = ?
                ORDER BY tarih DESC
            ''', (not_id,))
            return [dict(row) for row in imleç.fetchall()]

    def surum_getir(self, surum_id: int) -> Optional[dict]:
        """Belirli bir sürümü getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('SELECT * FROM surum_gecmisi WHERE id = ?', (surum_id,))
            satir = imleç.fetchone()
            return dict(satir) if satir else None

    def surum_sil(self, surum_id: int):
        """Sürümü siler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('DELETE FROM surum_gecmisi WHERE id = ?', (surum_id,))

    # ==================== İSTATİSTİKLER ====================

    def istatistikleri_getir(self) -> dict:
        """Uygulama istatistiklerini getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()

            istatistikler = {}

            # Toplam not sayısı
            imleç.execute('SELECT COUNT(*) as sayi FROM notlar WHERE silindi = 0')
            istatistikler['toplam_not'] = imleç.fetchone()['sayi']

            # Favori not sayısı
            imleç.execute('SELECT COUNT(*) as sayi FROM notlar WHERE favori = 1 AND silindi = 0')
            istatistikler['favori_not'] = imleç.fetchone()['sayi']

            # Çöp kutusundaki not sayısı
            imleç.execute('SELECT COUNT(*) as sayi FROM notlar WHERE silindi = 1')
            istatistikler['silinen_not'] = imleç.fetchone()['sayi']

            # Kategori sayısı
            imleç.execute('SELECT COUNT(*) as sayi FROM kategoriler')
            istatistikler['kategori_sayisi'] = imleç.fetchone()['sayi']

            # Etiket sayısı
            imleç.execute('SELECT COUNT(*) as sayi FROM etiketler')
            istatistikler['etiket_sayisi'] = imleç.fetchone()['sayi']

            # Aktif hatırlatıcı sayısı
            imleç.execute('SELECT COUNT(*) as sayi FROM hatirlaticilar WHERE aktif = 1')
            istatistikler['aktif_hatirlatici'] = imleç.fetchone()['sayi']

            # Bu hafta oluşturulan notlar
            imleç.execute('''
                SELECT COUNT(*) as sayi FROM notlar
                WHERE silindi = 0 AND olusturma_tarihi >= date('now', '-7 days')
            ''')
            istatistikler['bu_hafta_not'] = imleç.fetchone()['sayi']

            return istatistikler

    # ==================== GIT REPO İŞLEMLERİ ====================

    def git_repo_ekle(self, url: str, isim: str) -> int:
        """Yeni git repo ekler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                INSERT OR REPLACE INTO git_repolar (url, isim)
                VALUES (?, ?)
            ''', (url, isim))
            return imleç.lastrowid

    def git_repo_sil(self, repo_id: int):
        """Git repo'yu siler."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('DELETE FROM git_repolar WHERE id = ?', (repo_id,))

    def git_repolari_getir(self) -> List[dict]:
        """Tüm git repolarını getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                SELECT * FROM git_repolar ORDER BY isim
            ''')
            return [dict(row) for row in imleç.fetchall()]

    def git_repo_guncelle(self, repo_id: int, son_commit_hash: str, son_kontrol: str, guncellendi: bool = False):
        """Git repo bilgilerini günceller."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                UPDATE git_repolar
                SET son_commit_hash = ?, son_kontrol = ?, guncellendi = ?
                WHERE id = ?
            ''', (son_commit_hash, son_kontrol, 1 if guncellendi else 0, repo_id))

    def git_repo_guncelleme_sifirla(self, repo_id: int):
        """Repo'nun güncellendi durumunu sıfırlar."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                UPDATE git_repolar SET guncellendi = 0 WHERE id = ?
            ''', (repo_id,))

    # ==================== AYARLAR İŞLEMLERİ ====================

    def ayar_kaydet(self, anahtar: str, deger: str):
        """Ayar kaydeder veya günceller."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('''
                INSERT OR REPLACE INTO ayarlar (anahtar, deger)
                VALUES (?, ?)
            ''', (anahtar, deger))

    def ayar_getir(self, anahtar: str, varsayilan: str = None) -> str:
        """Ayar değerini getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('SELECT deger FROM ayarlar WHERE anahtar = ?', (anahtar,))
            sonuc = imleç.fetchone()
            return sonuc['deger'] if sonuc else varsayilan

    def tum_ayarlari_getir(self) -> dict:
        """Tüm ayarları sözlük olarak getirir."""
        with self._baglanti_al() as baglanti:
            imleç = baglanti.cursor()
            imleç.execute('SELECT anahtar, deger FROM ayarlar')
            return {row['anahtar']: row['deger'] for row in imleç.fetchall()}