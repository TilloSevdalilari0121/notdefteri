# database/veritabani.py
import sqlite3
import os
from datetime import datetime

class VeritabaniYoneticisi:
    """
    Tüm SQLite veritabanı işlemlerini yöneten sınıf.
    """
    def __init__(self, dosya_adi="notlar.db"):
        """
        Veritabanı bağlantısını başlatır ve gerekirse tabloları kurar.
        """
        ana_dizin = os.path.join(os.path.expanduser("~"), "ProfesyonelNotDefteriPython")
        if not os.path.exists(ana_dizin):
            os.makedirs(ana_dizin)

        veritabani_yolu = os.path.join(ana_dizin, dosya_adi)

        self.baglanti = sqlite3.connect(veritabani_yolu)
        self.baglanti.row_factory = sqlite3.Row  # Sütun adlarıyla erişim için
        self.imlec = self.baglanti.cursor()
        self._veritabanini_kur()

    def _veritabanini_kur(self):
        """
        Gerekli tablolar veritabanında mevcut değilse oluşturur.
        """
        self.imlec.execute('''
            CREATE TABLE IF NOT EXISTS Kategoriler (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                KategoriAdi TEXT NOT NULL UNIQUE
            )
        ''')
        self.imlec.execute('''
            CREATE TABLE IF NOT EXISTS Etiketler (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                EtiketAdi TEXT NOT NULL UNIQUE
            )
        ''')
        self.imlec.execute('''
            CREATE TABLE IF NOT EXISTS Notlar (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                KategoriID INTEGER,
                Baslik TEXT,
                Icerik TEXT, -- Zengin metin (HTML olarak saklanacak)
                Icerik_Metin TEXT, -- Aranabilir düz metin
                OlusturmaTarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                GuncellemeTarihi TIMESTAMP,
                FOREIGN KEY(KategoriID) REFERENCES Kategoriler(ID)
            )
        ''')
        self.imlec.execute('''
            CREATE TABLE IF NOT EXISTS Not_Etiketler (
                NotID INTEGER,
                EtiketID INTEGER,
                PRIMARY KEY (NotID, EtiketID),
                FOREIGN KEY(NotID) REFERENCES Notlar(ID) ON DELETE CASCADE,
                FOREIGN KEY(EtiketID) REFERENCES Etiketler(ID) ON DELETE CASCADE
            )
        ''')

        # Varsayılan verileri ekle (sadece ilk oluşturmada)
        self.imlec.execute("SELECT COUNT(*) FROM Kategoriler")
        if self.imlec.fetchone()[0] == 0:
            self.imlec.execute('INSERT INTO Kategoriler (KategoriAdi) VALUES (?)', ("Genel",))
            self.imlec.execute('INSERT INTO Kategoriler (KategoriAdi) VALUES (?)', ("İş",))

        self.imlec.execute("SELECT COUNT(*) FROM Etiketler")
        if self.imlec.fetchone()[0] == 0:
            self.imlec.execute('INSERT INTO Etiketler (EtiketAdi) VALUES (?)', ("Önemli",))
            self.imlec.execute('INSERT INTO Etiketler (EtiketAdi) VALUES (?)', ("Proje X",))

        self.baglanti.commit()

    def get_kategoriler(self):
        """Tüm kategorileri veritabanından alır."""
        self.imlec.execute("SELECT ID, KategoriAdi FROM Kategoriler ORDER BY KategoriAdi")
        return self.imlec.fetchall()

    def get_etiketler(self):
        """Tüm etiketleri veritabanından alır."""
        self.imlec.execute("SELECT ID, EtiketAdi FROM Etiketler ORDER BY EtiketAdi")
        return self.imlec.fetchall()

    def get_not_detay(self, not_id):
        """Belirtilen ID'ye sahip tek bir notun tüm detaylarını alır."""
        self.imlec.execute("SELECT * FROM Notlar WHERE ID = ?", (not_id,))
        return self.imlec.fetchone()

    def get_nota_ait_etiket_idler(self, not_id):
        """Bir nota atanmış etiketlerin ID'lerini döndürür."""
        self.imlec.execute("SELECT EtiketID FROM Not_Etiketler WHERE NotID = ?", (not_id,))
        return [row['EtiketID'] for row in self.imlec.fetchall()]

    def notlari_getir(self, kategori_id=-1, etiket_idler=None, arama_metni=""):
        """Filtrelere göre not listesini döndürür."""
        parametreler = []
        sorgu_parcalari = ["SELECT DISTINCT n.ID, n.Baslik, n.GuncellemeTarihi FROM Notlar n"]
        kosullar = []

        if etiket_idler:
            sorgu_parcalari.append("INNER JOIN Not_Etiketler ne ON n.ID = ne.NotID")
            placeholders = ','.join('?' for _ in etiket_idler)
            kosullar.append(f"ne.EtiketID IN ({placeholders})")
            parametreler.extend(etiket_idler)

        if kategori_id != -1:
            kosullar.append("n.KategoriID = ?")
            parametreler.append(kategori_id)

        if arama_metni:
            kosullar.append("(n.Baslik LIKE ? OR n.Icerik_Metin LIKE ?)")
            parametreler.append(f"%{arama_metni}%")
            parametreler.append(f"%{arama_metni}%")

        if kosullar:
            sorgu_parcalari.append("WHERE " + " AND ".join(kosullar))

        sorgu_parcalari.append("ORDER BY n.GuncellemeTarihi DESC")

        final_sorgu = " ".join(sorgu_parcalari)

        self.imlec.execute(final_sorgu, tuple(parametreler))
        return self.imlec.fetchall()


    def yeni_not_ekle(self, kategori_id, baslik="Yeni Not"):
        """Veritabanına yeni bir not ekler ve ID'sini döndürür."""
        simdiki_zaman = datetime.now()
        self.imlec.execute(
            "INSERT INTO Notlar (KategoriID, Baslik, GuncellemeTarihi) VALUES (?, ?, ?)",
            (kategori_id, baslik, simdiki_zaman)
        )
        self.baglanti.commit()
        return self.imlec.lastrowid

    def notu_guncelle(self, not_id, baslik, icerik_html, icerik_metin):
        """Mevcut bir notu günceller."""
        simdiki_zaman = datetime.now()
        self.imlec.execute(
            """UPDATE Notlar SET
               Baslik = ?, Icerik = ?, Icerik_Metin = ?, GuncellemeTarihi = ?
               WHERE ID = ?""",
            (baslik, icerik_html, icerik_metin, simdiki_zaman, not_id)
        )
        self.baglanti.commit()

    def notu_sil(self, not_id):
        """Bir notu ve ilişkili etiketlerini siler."""
        self.imlec.execute("DELETE FROM Notlar WHERE ID = ?", (not_id,))
        # Not_Etiketler tablosundan silme işlemi CASCADE ile otomatik yapılır
        self.baglanti.commit()

    def not_etiketlerini_guncelle(self, not_id, etiket_idler):
        """Bir notun etiketlerini tamamen yeniden ayarlar."""
        # Önce mevcut etiketleri sil
        self.imlec.execute("DELETE FROM Not_Etiketler WHERE NotID = ?", (not_id,))
        # Sonra yeni etiketleri ekle
        for etiket_id in etiket_idler:
            self.imlec.execute("INSERT INTO Not_Etiketler (NotID, EtiketID) VALUES (?, ?)", (not_id, etiket_id))
        self.baglanti.commit()

    def baglantiyi_kapat(self):
        """Veritabanı bağlantısını kapatır."""
        if self.baglanti:
            self.baglanti.close()

if __name__ == '__main__':
    # Bu modülün doğrudan çalıştırıldığında test için kullanılmasını sağlar
    db = VeritabaniYoneticisi()
    print("Kategoriler:", db.get_kategoriler())
    print("Etiketler:", db.get_etiketler())
    db.baglantiyi_kapat()
