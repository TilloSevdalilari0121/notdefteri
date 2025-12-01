# -*- coding: utf-8 -*-
"""
Not Defteri - Çoklu Pencere Modülü
Birden fazla notu aynı anda görüntüleme.
"""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QLineEdit, QFrame, QApplication,
    QDesktopWidget, QMenuBar, QMenu, QAction, QStatusBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QKeySequence


class AyrikNotPenceresi(QMainWindow):
    """Ayrı pencerede not görüntüleme."""

    kapatildi = pyqtSignal(int)  # not_id
    kaydedildi = pyqtSignal(int, str, str)  # not_id, baslik, icerik
    degisiklikYapildi = pyqtSignal(int)  # not_id

    def __init__(self, not_id: int, not_verisi: dict, parent=None):
        super().__init__(parent)
        self.not_id = not_id
        self.not_verisi = not_verisi
        self.degisiklik_var = False

        self._arayuz_olustur()
        self._menu_olustur()
        self._verileri_yukle()

    def _arayuz_olustur(self):
        """Pencere arayüzünü oluşturur."""
        self.setWindowTitle(f"📝 {self.not_verisi.get('baslik', 'Not')}")
        self.setMinimumSize(500, 400)

        # Pencere konumunu rastgele ayarla
        self._pencere_konumu_ayarla()

        # Merkezi widget
        merkez = QWidget()
        self.setCentralWidget(merkez)

        yerlesim = QVBoxLayout(merkez)
        yerlesim.setContentsMargins(15, 15, 15, 15)

        # Başlık
        self.baslik_input = QLineEdit()
        self.baslik_input.setFont(QFont('Segoe UI', 14, QFont.Bold))
        self.baslik_input.setStyleSheet('''
            QLineEdit {
                border: none;
                border-bottom: 2px solid #3498db;
                padding: 8px;
                background: transparent;
            }
            QLineEdit:focus {
                border-bottom-color: #2980b9;
            }
        ''')
        self.baslik_input.textChanged.connect(self._degisiklik_bildir)
        yerlesim.addWidget(self.baslik_input)

        # Meta bilgiler
        self.meta_label = QLabel()
        self.meta_label.setStyleSheet('color: gray; font-size: 11px; margin: 5px 0;')
        yerlesim.addWidget(self.meta_label)

        # İçerik editörü
        self.editor = QTextEdit()
        self.editor.setFont(QFont('Segoe UI', 11))
        self.editor.textChanged.connect(self._degisiklik_bildir)
        yerlesim.addWidget(self.editor)

        # Alt bar
        alt_yerlesim = QHBoxLayout()

        self.durum_label = QLabel('Hazır')
        self.durum_label.setStyleSheet('color: gray;')
        alt_yerlesim.addWidget(self.durum_label)

        alt_yerlesim.addStretch()

        self.kaydet_btn = QPushButton('💾 Kaydet')
        self.kaydet_btn.setShortcut(QKeySequence.Save)
        self.kaydet_btn.clicked.connect(self._kaydet)
        alt_yerlesim.addWidget(self.kaydet_btn)

        yerlesim.addLayout(alt_yerlesim)

        # Durum çubuğu
        self.statusBar().showMessage('Hazır')

    def _pencere_konumu_ayarla(self):
        """Pencere konumunu ekranın ortasına yakın rastgele ayarlar."""
        import random

        ekran = QDesktopWidget().availableGeometry()
        genislik = 600
        yukseklik = 500

        # Rastgele konum (ekranın %20-80 aralığında)
        min_x = int(ekran.width() * 0.1)
        max_x = int(ekran.width() * 0.7)
        min_y = int(ekran.height() * 0.1)
        max_y = int(ekran.height() * 0.5)

        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)

        self.setGeometry(x, y, genislik, yukseklik)

    def _menu_olustur(self):
        """Menü çubuğunu oluşturur."""
        menubar = self.menuBar()

        # Dosya menüsü
        dosya_menu = menubar.addMenu('Dosya')

        kaydet_action = QAction('Kaydet', self)
        kaydet_action.setShortcut('Ctrl+S')
        kaydet_action.triggered.connect(self._kaydet)
        dosya_menu.addAction(kaydet_action)

        dosya_menu.addSeparator()

        kapat_action = QAction('Kapat', self)
        kapat_action.setShortcut('Ctrl+W')
        kapat_action.triggered.connect(self.close)
        dosya_menu.addAction(kapat_action)

        # Düzen menüsü
        duzen_menu = menubar.addMenu('Düzen')

        geri_al = QAction('Geri Al', self)
        geri_al.setShortcut('Ctrl+Z')
        geri_al.triggered.connect(self.editor.undo)
        duzen_menu.addAction(geri_al)

        yinele = QAction('Yinele', self)
        yinele.setShortcut('Ctrl+Y')
        yinele.triggered.connect(self.editor.redo)
        duzen_menu.addAction(yinele)

    def _verileri_yukle(self):
        """Not verilerini yükler."""
        self.baslik_input.setText(self.not_verisi.get('baslik', ''))
        self.editor.setHtml(self.not_verisi.get('zengin_icerik', ''))

        # Meta bilgiler
        tarih = self.not_verisi.get('guncelleme_tarihi', '')
        kategori = self.not_verisi.get('kategori_adi', 'Genel')
        self.meta_label.setText(f'📁 {kategori}  |  📅 {tarih}')

        self.degisiklik_var = False

    def _degisiklik_bildir(self):
        """Değişiklik yapıldığını bildirir."""
        if not self.degisiklik_var:
            self.degisiklik_var = True
            self.setWindowTitle(f"📝 {self.baslik_input.text()} *")
            self.durum_label.setText('Kaydedilmemiş değişiklikler')
            self.degisiklikYapildi.emit(self.not_id)

    def _kaydet(self):
        """Notu kaydeder."""
        baslik = self.baslik_input.text().strip() or 'Başlıksız Not'
        icerik = self.editor.toHtml()

        self.kaydedildi.emit(self.not_id, baslik, icerik)

        self.degisiklik_var = False
        self.setWindowTitle(f"📝 {baslik}")
        self.durum_label.setText('Kaydedildi')
        self.statusBar().showMessage('Not kaydedildi', 3000)

    def closeEvent(self, event):
        """Pencere kapatılırken."""
        if self.degisiklik_var:
            from PyQt5.QtWidgets import QMessageBox

            cevap = QMessageBox.question(
                self, 'Kaydedilmemiş Değişiklikler',
                'Kaydedilmemiş değişiklikler var. Kaydetmek ister misiniz?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if cevap == QMessageBox.Yes:
                self._kaydet()
            elif cevap == QMessageBox.Cancel:
                event.ignore()
                return

        self.kapatildi.emit(self.not_id)
        event.accept()


class CokluPencereYoneticisi:
    """Çoklu pencere yöneticisi."""

    def __init__(self, veritabani=None):
        self.vt = veritabani
        self.acik_pencereler: Dict[int, AyrikNotPenceresi] = {}

    def not_ac(self, not_id: int, not_verisi: dict = None) -> AyrikNotPenceresi:
        """
        Notu ayrı pencerede açar.

        Returns:
            Oluşturulan pencere
        """
        # Zaten açık mı kontrol et
        if not_id in self.acik_pencereler:
            pencere = self.acik_pencereler[not_id]
            pencere.raise_()
            pencere.activateWindow()
            return pencere

        # Not verisini getir
        if not_verisi is None and self.vt:
            not_verisi = self.vt.not_getir(not_id)

        if not not_verisi:
            return None

        # Yeni pencere oluştur
        pencere = AyrikNotPenceresi(not_id, not_verisi)
        pencere.kapatildi.connect(self._pencere_kapatildi)
        pencere.kaydedildi.connect(self._not_kaydedildi)
        pencere.show()

        self.acik_pencereler[not_id] = pencere
        return pencere

    def pencere_kapat(self, not_id: int):
        """Pencereyi kapatır."""
        if not_id in self.acik_pencereler:
            self.acik_pencereler[not_id].close()

    def tum_pencereleri_kapat(self):
        """Tüm pencereleri kapatır."""
        for pencere in list(self.acik_pencereler.values()):
            pencere.close()

    def acik_not_idleri(self) -> List[int]:
        """Açık not ID'lerini döndürür."""
        return list(self.acik_pencereler.keys())

    def pencere_sayisi(self) -> int:
        """Açık pencere sayısını döndürür."""
        return len(self.acik_pencereler)

    def _pencere_kapatildi(self, not_id: int):
        """Pencere kapatıldığında çağrılır."""
        if not_id in self.acik_pencereler:
            del self.acik_pencereler[not_id]

    def _not_kaydedildi(self, not_id: int, baslik: str, icerik: str):
        """Not kaydedildiğinde çağrılır."""
        if self.vt:
            self.vt.not_guncelle(
                not_id,
                baslik=baslik,
                zengin_icerik=icerik,
                icerik=self._html_to_text(icerik)
            )

    def _html_to_text(self, html: str) -> str:
        """HTML'i düz metne çevirir."""
        import re
        metin = re.sub(r'<[^>]+>', '', html)
        metin = re.sub(r'\s+', ' ', metin)
        return metin.strip()

    def pencereleri_diz(self, stil: str = 'cascade'):
        """
        Açık pencereleri düzenler.

        Args:
            stil: 'cascade', 'tile_horizontal', 'tile_vertical'
        """
        if not self.acik_pencereler:
            return

        ekran = QDesktopWidget().availableGeometry()
        pencereler = list(self.acik_pencereler.values())

        if stil == 'cascade':
            self._cascade_diz(pencereler, ekran)
        elif stil == 'tile_horizontal':
            self._yatay_diz(pencereler, ekran)
        elif stil == 'tile_vertical':
            self._dikey_diz(pencereler, ekran)

    def _cascade_diz(self, pencereler: List[AyrikNotPenceresi], ekran):
        """Pencereleri cascade şeklinde dizer."""
        offset = 30
        x, y = 50, 50
        genislik = int(ekran.width() * 0.5)
        yukseklik = int(ekran.height() * 0.6)

        for i, pencere in enumerate(pencereler):
            pencere.setGeometry(x + i * offset, y + i * offset, genislik, yukseklik)
            pencere.raise_()

    def _yatay_diz(self, pencereler: List[AyrikNotPenceresi], ekran):
        """Pencereleri yatay olarak dizer."""
        sayı = len(pencereler)
        genislik = ekran.width() // sayı
        yukseklik = ekran.height()

        for i, pencere in enumerate(pencereler):
            pencere.setGeometry(i * genislik, 0, genislik, yukseklik)

    def _dikey_diz(self, pencereler: List[AyrikNotPenceresi], ekran):
        """Pencereleri dikey olarak dizer."""
        sayı = len(pencereler)
        genislik = ekran.width()
        yukseklik = ekran.height() // sayı

        for i, pencere in enumerate(pencereler):
            pencere.setGeometry(0, i * yukseklik, genislik, yukseklik)
