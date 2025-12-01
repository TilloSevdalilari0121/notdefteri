# -*- coding: utf-8 -*-
"""
Not Defteri - Tam Metin Arama Modülü
SQLite FTS (Full-Text Search) ile gelişmiş arama.
"""

import re
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QCheckBox, QComboBox,
    QGroupBox, QFormLayout, QFrame, QDateEdit, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QFont, QColor


class AramaMotoru:
    """Tam metin arama motoru."""

    def __init__(self, veritabani):
        self.vt = veritabani
        self._fts_tablo_olustur()

    def _fts_tablo_olustur(self):
        """FTS (Full-Text Search) tablosunu oluşturur."""
        try:
            with self.vt._baglanti_al() as baglanti:
                imleç = baglanti.cursor()

                # FTS5 tablosu oluştur
                imleç.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS notlar_fts USING fts5(
                        baslik,
                        icerik,
                        content='notlar',
                        content_rowid='id'
                    )
                ''')

                # Tetikleyiciler
                imleç.execute('''
                    CREATE TRIGGER IF NOT EXISTS notlar_ai AFTER INSERT ON notlar BEGIN
                        INSERT INTO notlar_fts(rowid, baslik, icerik)
                        VALUES (new.id, new.baslik, new.icerik);
                    END
                ''')

                imleç.execute('''
                    CREATE TRIGGER IF NOT EXISTS notlar_ad AFTER DELETE ON notlar BEGIN
                        INSERT INTO notlar_fts(notlar_fts, rowid, baslik, icerik)
                        VALUES('delete', old.id, old.baslik, old.icerik);
                    END
                ''')

                imleç.execute('''
                    CREATE TRIGGER IF NOT EXISTS notlar_au AFTER UPDATE ON notlar BEGIN
                        INSERT INTO notlar_fts(notlar_fts, rowid, baslik, icerik)
                        VALUES('delete', old.id, old.baslik, old.icerik);
                        INSERT INTO notlar_fts(rowid, baslik, icerik)
                        VALUES (new.id, new.baslik, new.icerik);
                    END
                ''')

        except Exception as e:
            print(f"FTS tablo oluşturma hatası: {e}")

    def fts_indeksi_yeniden_olustur(self):
        """FTS indeksini yeniden oluşturur."""
        try:
            with self.vt._baglanti_al() as baglanti:
                imleç = baglanti.cursor()

                # Mevcut FTS verilerini temizle
                imleç.execute("DELETE FROM notlar_fts")

                # Tüm notları yeniden indeksle
                imleç.execute('''
                    INSERT INTO notlar_fts(rowid, baslik, icerik)
                    SELECT id, baslik, icerik FROM notlar WHERE silindi = 0
                ''')

        except Exception as e:
            print(f"FTS indeks yenileme hatası: {e}")

    def ara(self, sorgu: str, limit: int = 50) -> List[dict]:
        """
        Tam metin araması yapar.

        Args:
            sorgu: Arama sorgusu
            limit: Maksimum sonuç sayısı

        Returns:
            Eşleşen notların listesi
        """
        if not sorgu.strip():
            return []

        try:
            with self.vt._baglanti_al() as baglanti:
                imleç = baglanti.cursor()

                # FTS sorgusu
                imleç.execute('''
                    SELECT n.*, k.ad as kategori_adi,
                           snippet(notlar_fts, 1, '<mark>', '</mark>', '...', 32) as onizleme,
                           bm25(notlar_fts) as skor
                    FROM notlar_fts
                    JOIN notlar n ON notlar_fts.rowid = n.id
                    LEFT JOIN kategoriler k ON n.kategori_id = k.id
                    WHERE notlar_fts MATCH ? AND n.silindi = 0
                    ORDER BY skor
                    LIMIT ?
                ''', (sorgu, limit))

                return [dict(row) for row in imleç.fetchall()]

        except Exception:
            # FTS başarısız olursa basit LIKE araması
            return self._basit_ara(sorgu, limit)

    def _basit_ara(self, sorgu: str, limit: int = 50) -> List[dict]:
        """Basit LIKE araması (FTS çalışmazsa)."""
        try:
            with self.vt._baglanti_al() as baglanti:
                imleç = baglanti.cursor()

                arama = f'%{sorgu}%'
                imleç.execute('''
                    SELECT n.*, k.ad as kategori_adi
                    FROM notlar n
                    LEFT JOIN kategoriler k ON n.kategori_id = k.id
                    WHERE n.silindi = 0 AND (n.baslik LIKE ? OR n.icerik LIKE ?)
                    ORDER BY n.guncelleme_tarihi DESC
                    LIMIT ?
                ''', (arama, arama, limit))

                return [dict(row) for row in imleç.fetchall()]

        except Exception as e:
            print(f"Basit arama hatası: {e}")
            return []

    def gelismis_ara(self, sorgu: str = None, kategori_id: int = None,
                     etiket_idleri: List[int] = None, baslangic_tarihi: str = None,
                     bitis_tarihi: str = None, sadece_favoriler: bool = False,
                     limit: int = 50) -> List[dict]:
        """
        Gelişmiş arama - çoklu filtre desteği.

        Args:
            sorgu: Metin sorgusu
            kategori_id: Kategori filtresi
            etiket_idleri: Etiket filtreleri
            baslangic_tarihi: Başlangıç tarihi (YYYY-MM-DD)
            bitis_tarihi: Bitiş tarihi (YYYY-MM-DD)
            sadece_favoriler: Sadece favoriler

        Returns:
            Eşleşen notların listesi
        """
        try:
            with self.vt._baglanti_al() as baglanti:
                imleç = baglanti.cursor()

                sql = '''
                    SELECT DISTINCT n.*, k.ad as kategori_adi
                    FROM notlar n
                    LEFT JOIN kategoriler k ON n.kategori_id = k.id
                    LEFT JOIN not_etiketleri ne ON n.id = ne.not_id
                    WHERE n.silindi = 0
                '''
                params = []

                # Metin sorgusu
                if sorgu:
                    sql += ' AND (n.baslik LIKE ? OR n.icerik LIKE ?)'
                    arama = f'%{sorgu}%'
                    params.extend([arama, arama])

                # Kategori filtresi
                if kategori_id:
                    sql += ' AND n.kategori_id = ?'
                    params.append(kategori_id)

                # Etiket filtreleri
                if etiket_idleri:
                    placeholders = ','.join(['?' for _ in etiket_idleri])
                    sql += f' AND ne.etiket_id IN ({placeholders})'
                    params.extend(etiket_idleri)

                # Tarih aralığı
                if baslangic_tarihi:
                    sql += ' AND n.olusturma_tarihi >= ?'
                    params.append(baslangic_tarihi)

                if bitis_tarihi:
                    sql += ' AND n.olusturma_tarihi <= ?'
                    params.append(bitis_tarihi + ' 23:59:59')

                # Favoriler
                if sadece_favoriler:
                    sql += ' AND n.favori = 1'

                sql += ' ORDER BY n.guncelleme_tarihi DESC LIMIT ?'
                params.append(limit)

                imleç.execute(sql, params)
                return [dict(row) for row in imleç.fetchall()]

        except Exception as e:
            print(f"Gelişmiş arama hatası: {e}")
            return []

    def son_aramalar_kaydet(self, sorgu: str):
        """Son aramayı kaydeder."""
        self.vt.ayar_kaydet(f'son_arama_{datetime.now().timestamp()}', sorgu)

    def son_aramalari_getir(self, limit: int = 10) -> List[str]:
        """Son aramaları getirir."""
        # Bu basit bir implementasyon, gerçek uygulamada ayrı tablo kullanılabilir
        try:
            with self.vt._baglanti_al() as baglanti:
                imleç = baglanti.cursor()
                imleç.execute('''
                    SELECT deger FROM ayarlar
                    WHERE anahtar LIKE 'son_arama_%'
                    ORDER BY anahtar DESC
                    LIMIT ?
                ''', (limit,))
                return [row['deger'] for row in imleç.fetchall()]
        except:
            return []


class AramaSonucuItem(QFrame):
    """Arama sonucu öğesi widget'ı."""

    tiklandi = pyqtSignal(int)  # not_id

    def __init__(self, not_verisi: dict, parent=None):
        super().__init__(parent)
        self.not_id = not_verisi['id']
        self._arayuz_olustur(not_verisi)

    def _arayuz_olustur(self, not_verisi: dict):
        """Arayüzü oluşturur."""
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet('''
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        ''')

        yerlesim = QVBoxLayout(self)
        yerlesim.setContentsMargins(10, 8, 10, 8)
        yerlesim.setSpacing(4)

        # Başlık satırı
        baslik_yerlesim = QHBoxLayout()

        baslik = QLabel(not_verisi['baslik'])
        baslik.setFont(QFont('Segoe UI', 11, QFont.Bold))
        baslik_yerlesim.addWidget(baslik)

        if not_verisi.get('favori'):
            favori = QLabel('⭐')
            baslik_yerlesim.addWidget(favori)

        baslik_yerlesim.addStretch()

        kategori = QLabel(not_verisi.get('kategori_adi', 'Genel'))
        kategori.setStyleSheet('color: #3498db; font-size: 11px;')
        baslik_yerlesim.addWidget(kategori)

        yerlesim.addLayout(baslik_yerlesim)

        # Önizleme (varsa highlight'lı)
        onizleme_metin = not_verisi.get('onizleme', not_verisi.get('icerik', '')[:100])
        onizleme = QLabel(onizleme_metin)
        onizleme.setStyleSheet('color: #666; font-size: 11px;')
        onizleme.setWordWrap(True)
        yerlesim.addWidget(onizleme)

        # Tarih
        tarih = not_verisi.get('guncelleme_tarihi', '')
        if tarih:
            try:
                dt = datetime.strptime(tarih, '%Y-%m-%d %H:%M:%S')
                tarih_str = dt.strftime('%d.%m.%Y')
            except:
                tarih_str = tarih
            tarih_label = QLabel(tarih_str)
            tarih_label.setStyleSheet('color: #999; font-size: 10px;')
            yerlesim.addWidget(tarih_label)

    def mousePressEvent(self, event):
        """Tıklama olayı."""
        if event.button() == Qt.LeftButton:
            self.tiklandi.emit(self.not_id)
        super().mousePressEvent(event)


class GelismisAramaDialog(QDialog):
    """Gelişmiş arama dialogu."""

    notSecildi = pyqtSignal(int)  # not_id

    def __init__(self, parent=None, arama_motoru=None, veritabani=None):
        super().__init__(parent)
        self.arama_motoru = arama_motoru
        self.vt = veritabani
        self._arayuz_olustur()

        # Arama gecikmesi için timer
        self.arama_timer = QTimer()
        self.arama_timer.setSingleShot(True)
        self.arama_timer.timeout.connect(self._arama_yap)

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Gelişmiş Arama')
        self.setMinimumSize(600, 500)

        ana_yerlesim = QVBoxLayout(self)

        # Arama kutusu
        arama_yerlesim = QHBoxLayout()

        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText('🔍 Ara...')
        self.arama_input.setStyleSheet('''
            QLineEdit {
                padding: 10px 15px;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        ''')
        self.arama_input.textChanged.connect(self._arama_degisti)
        arama_yerlesim.addWidget(self.arama_input)

        self.filtre_btn = QPushButton('🎛 Filtreler')
        self.filtre_btn.setCheckable(True)
        self.filtre_btn.clicked.connect(self._filtre_toggle)
        arama_yerlesim.addWidget(self.filtre_btn)

        ana_yerlesim.addLayout(arama_yerlesim)

        # Filtre paneli (başlangıçta gizli)
        self.filtre_panel = self._filtre_paneli_olustur()
        self.filtre_panel.hide()
        ana_yerlesim.addWidget(self.filtre_panel)

        # Sonuçlar
        self.sonuc_label = QLabel('Sonuçlar')
        self.sonuc_label.setStyleSheet('color: gray; margin-top: 10px;')
        ana_yerlesim.addWidget(self.sonuc_label)

        # Sonuç listesi
        from PyQt5.QtWidgets import QScrollArea
        self.sonuc_scroll = QScrollArea()
        self.sonuc_scroll.setWidgetResizable(True)
        self.sonuc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.sonuc_widget = QWidget()
        self.sonuc_yerlesim = QVBoxLayout(self.sonuc_widget)
        self.sonuc_yerlesim.setContentsMargins(0, 0, 0, 0)
        self.sonuc_yerlesim.setSpacing(8)
        self.sonuc_yerlesim.addStretch()

        self.sonuc_scroll.setWidget(self.sonuc_widget)
        ana_yerlesim.addWidget(self.sonuc_scroll)

        # Kapat butonu
        kapat_btn = QPushButton('Kapat')
        kapat_btn.clicked.connect(self.reject)
        ana_yerlesim.addWidget(kapat_btn)

    def _filtre_paneli_olustur(self) -> QFrame:
        """Filtre panelini oluşturur."""
        panel = QFrame()
        panel.setStyleSheet('''
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 10px;
            }
        ''')

        yerlesim = QHBoxLayout(panel)

        # Kategori filtresi
        kat_yerlesim = QVBoxLayout()
        kat_yerlesim.addWidget(QLabel('Kategori:'))
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItem('Tümü', None)
        if self.vt:
            for kat in self.vt.kategorileri_getir():
                self.kategori_combo.addItem(f"{kat['ikon']} {kat['ad']}", kat['id'])
        self.kategori_combo.currentIndexChanged.connect(self._filtre_degisti)
        kat_yerlesim.addWidget(self.kategori_combo)
        yerlesim.addLayout(kat_yerlesim)

        # Tarih aralığı
        tarih_yerlesim = QVBoxLayout()
        tarih_yerlesim.addWidget(QLabel('Tarih Aralığı:'))

        tarih_h = QHBoxLayout()
        self.baslangic_tarih = QDateEdit()
        self.baslangic_tarih.setDate(QDate.currentDate().addMonths(-1))
        self.baslangic_tarih.setCalendarPopup(True)
        tarih_h.addWidget(self.baslangic_tarih)

        tarih_h.addWidget(QLabel('-'))

        self.bitis_tarih = QDateEdit()
        self.bitis_tarih.setDate(QDate.currentDate())
        self.bitis_tarih.setCalendarPopup(True)
        tarih_h.addWidget(self.bitis_tarih)

        tarih_yerlesim.addLayout(tarih_h)
        yerlesim.addLayout(tarih_yerlesim)

        # Favoriler
        self.favori_check = QCheckBox('Sadece favoriler')
        self.favori_check.stateChanged.connect(self._filtre_degisti)
        yerlesim.addWidget(self.favori_check)

        return panel

    def _filtre_toggle(self):
        """Filtre panelini göster/gizle."""
        self.filtre_panel.setVisible(self.filtre_btn.isChecked())

    def _arama_degisti(self, metin: str):
        """Arama metni değiştiğinde."""
        self.arama_timer.start(300)  # 300ms gecikme

    def _filtre_degisti(self):
        """Filtre değiştiğinde."""
        self._arama_yap()

    def _arama_yap(self):
        """Aramayı gerçekleştirir."""
        if not self.arama_motoru:
            return

        # Mevcut sonuçları temizle
        while self.sonuc_yerlesim.count() > 1:
            item = self.sonuc_yerlesim.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sorgu = self.arama_input.text().strip()

        # Filtreleri al
        kategori_id = self.kategori_combo.currentData()

        baslangic = None
        bitis = None
        if self.filtre_btn.isChecked():
            baslangic = self.baslangic_tarih.date().toString('yyyy-MM-dd')
            bitis = self.bitis_tarih.date().toString('yyyy-MM-dd')

        sadece_favoriler = self.favori_check.isChecked()

        # Arama yap
        if sorgu or kategori_id or sadece_favoriler:
            sonuclar = self.arama_motoru.gelismis_ara(
                sorgu=sorgu,
                kategori_id=kategori_id,
                baslangic_tarihi=baslangic if self.filtre_btn.isChecked() else None,
                bitis_tarihi=bitis if self.filtre_btn.isChecked() else None,
                sadece_favoriler=sadece_favoriler
            )
        else:
            sonuclar = []

        # Sonuçları göster
        self.sonuc_label.setText(f'Sonuçlar ({len(sonuclar)})')

        for not_verisi in sonuclar:
            item = AramaSonucuItem(not_verisi)
            item.tiklandi.connect(self._not_secildi)
            self.sonuc_yerlesim.insertWidget(
                self.sonuc_yerlesim.count() - 1, item
            )

    def _not_secildi(self, not_id: int):
        """Not seçildiğinde."""
        self.notSecildi.emit(not_id)
        self.accept()
