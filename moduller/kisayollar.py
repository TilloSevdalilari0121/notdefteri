# -*- coding: utf-8 -*-
"""
Not Defteri - Klavye Kısayolları Modülü
Özelleştirilebilir klavye kısayolları.
"""

from typing import Dict, Callable, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QKeySequenceEdit,
    QMessageBox, QShortcut, QWidget, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence, QFont


# Varsayılan kısayollar
VARSAYILAN_KISAYOLLAR = {
    # Dosya işlemleri
    'yeni_not': ('Ctrl+N', 'Yeni Not'),
    'kaydet': ('Ctrl+S', 'Kaydet'),
    'kapat': ('Ctrl+W', 'Notu Kapat'),
    'cikis': ('Ctrl+Q', 'Çıkış'),

    # Düzenleme
    'geri_al': ('Ctrl+Z', 'Geri Al'),
    'yinele': ('Ctrl+Y', 'Yinele'),
    'kes': ('Ctrl+X', 'Kes'),
    'kopyala': ('Ctrl+C', 'Kopyala'),
    'yapistir': ('Ctrl+V', 'Yapıştır'),
    'tumu_sec': ('Ctrl+A', 'Tümünü Seç'),

    # Biçimlendirme
    'kalin': ('Ctrl+B', 'Kalın'),
    'italik': ('Ctrl+I', 'İtalik'),
    'alti_cizili': ('Ctrl+U', 'Altı Çizili'),

    # Arama ve navigasyon
    'ara': ('Ctrl+F', 'Ara'),
    'gelismis_ara': ('Ctrl+Shift+F', 'Gelişmiş Arama'),
    'bul_degistir': ('Ctrl+H', 'Bul ve Değiştir'),
    'sonraki_not': ('Ctrl+Tab', 'Sonraki Not'),
    'onceki_not': ('Ctrl+Shift+Tab', 'Önceki Not'),

    # Görünüm
    'kenar_cubugu': ('Ctrl+\\', 'Kenar Çubuğunu Göster/Gizle'),
    'tam_ekran': ('F11', 'Tam Ekran'),
    'yakinlastir': ('Ctrl++', 'Yakınlaştır'),
    'uzaklastir': ('Ctrl+-', 'Uzaklaştır'),
    'sifirla_yakinlik': ('Ctrl+0', 'Yakınlığı Sıfırla'),

    # Kategoriler (Ctrl+1-9)
    'kategori_1': ('Ctrl+1', 'Kategori 1'),
    'kategori_2': ('Ctrl+2', 'Kategori 2'),
    'kategori_3': ('Ctrl+3', 'Kategori 3'),
    'kategori_4': ('Ctrl+4', 'Kategori 4'),
    'kategori_5': ('Ctrl+5', 'Kategori 5'),

    # Diğer
    'favori_ekle': ('Ctrl+D', 'Favorilere Ekle/Kaldır'),
    'not_sil': ('Delete', 'Notu Sil'),
    'hatirlatici': ('Ctrl+R', 'Hatırlatıcı Ekle'),
    'surum_gecmisi': ('Ctrl+Shift+H', 'Sürüm Geçmişi'),
    'ayarlar': ('Ctrl+,', 'Ayarlar'),
    'kisayollar': ('Ctrl+K', 'Kısayollar'),
    'yardim': ('F1', 'Yardım'),
}


class KisayolYoneticisi:
    """Klavye kısayollarını yöneten sınıf."""

    def __init__(self, parent_widget: QWidget, veritabani=None):
        """
        Args:
            parent_widget: Kısayolların bağlanacağı widget
            veritabani: Ayarları kaydetmek için veritabanı
        """
        self.parent = parent_widget
        self.vt = veritabani
        self.kisayollar: Dict[str, QShortcut] = {}
        self.fonksiyonlar: Dict[str, Callable] = {}
        self.mevcut_kisayollar = self._kisayollari_yukle()

    def _kisayollari_yukle(self) -> Dict[str, str]:
        """Kaydedilmiş kısayolları yükler."""
        kisayollar = {}

        for anahtar, (varsayilan, _) in VARSAYILAN_KISAYOLLAR.items():
            if self.vt:
                kaydedilen = self.vt.ayar_getir(f'kisayol_{anahtar}')
                kisayollar[anahtar] = kaydedilen if kaydedilen else varsayilan
            else:
                kisayollar[anahtar] = varsayilan

        return kisayollar

    def kisayol_kaydet(self, anahtar: str, yeni_kisayol: str):
        """Kısayolu kaydeder."""
        self.mevcut_kisayollar[anahtar] = yeni_kisayol
        if self.vt:
            self.vt.ayar_kaydet(f'kisayol_{anahtar}', yeni_kisayol)

        # Aktif kısayolu güncelle
        if anahtar in self.kisayollar:
            self.kisayollar[anahtar].setKey(QKeySequence(yeni_kisayol))

    def kisayol_sifirla(self, anahtar: str):
        """Kısayolu varsayılana sıfırlar."""
        if anahtar in VARSAYILAN_KISAYOLLAR:
            varsayilan, _ = VARSAYILAN_KISAYOLLAR[anahtar]
            self.kisayol_kaydet(anahtar, varsayilan)

    def tum_kisayollari_sifirla(self):
        """Tüm kısayolları varsayılana sıfırlar."""
        for anahtar in VARSAYILAN_KISAYOLLAR:
            self.kisayol_sifirla(anahtar)

    def kisayol_bagla(self, anahtar: str, fonksiyon: Callable):
        """
        Kısayola fonksiyon bağlar.

        Args:
            anahtar: Kısayol anahtarı (örn: 'yeni_not')
            fonksiyon: Çağrılacak fonksiyon
        """
        if anahtar not in self.mevcut_kisayollar:
            return

        kisayol_str = self.mevcut_kisayollar[anahtar]

        # Mevcut kısayolu kaldır
        if anahtar in self.kisayollar:
            self.kisayollar[anahtar].deleteLater()

        # Yeni kısayol oluştur
        kisayol = QShortcut(QKeySequence(kisayol_str), self.parent)
        kisayol.activated.connect(fonksiyon)

        self.kisayollar[anahtar] = kisayol
        self.fonksiyonlar[anahtar] = fonksiyon

    def kisayol_kaldir(self, anahtar: str):
        """Kısayolu kaldırır."""
        if anahtar in self.kisayollar:
            self.kisayollar[anahtar].deleteLater()
            del self.kisayollar[anahtar]

        if anahtar in self.fonksiyonlar:
            del self.fonksiyonlar[anahtar]

    def kisayol_getir(self, anahtar: str) -> Optional[str]:
        """Kısayol tuş kombinasyonunu döndürür."""
        return self.mevcut_kisayollar.get(anahtar)

    def aciklama_getir(self, anahtar: str) -> Optional[str]:
        """Kısayol açıklamasını döndürür."""
        if anahtar in VARSAYILAN_KISAYOLLAR:
            return VARSAYILAN_KISAYOLLAR[anahtar][1]
        return None

    def cakisma_kontrol(self, anahtar: str, yeni_kisayol: str) -> Optional[str]:
        """
        Kısayol çakışmasını kontrol eder.

        Returns:
            Çakışan kısayolun anahtarı veya None
        """
        for k, v in self.mevcut_kisayollar.items():
            if k != anahtar and v == yeni_kisayol:
                return k
        return None


class KisayollarDialog(QDialog):
    """Kısayolları görüntüleme ve düzenleme dialogu."""

    kisayolDegisti = pyqtSignal(str, str)  # anahtar, yeni_kisayol

    def __init__(self, parent=None, kisayol_yoneticisi=None):
        super().__init__(parent)
        self.yonetici = kisayol_yoneticisi
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Klavye Kısayolları')
        self.setMinimumSize(500, 600)

        yerlesim = QVBoxLayout(self)

        # Bilgi
        bilgi = QLabel('⌨️ Klavye Kısayolları')
        bilgi.setFont(QFont('Segoe UI', 14, QFont.Bold))
        yerlesim.addWidget(bilgi)

        aciklama = QLabel('Kısayolu değiştirmek için üzerine çift tıklayın.')
        aciklama.setStyleSheet('color: gray;')
        yerlesim.addWidget(aciklama)

        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(3)
        self.tablo.setHorizontalHeaderLabels(['İşlem', 'Kısayol', 'Varsayılan'])
        self.tablo.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tablo.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.tablo.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.tablo.setColumnWidth(1, 120)
        self.tablo.setColumnWidth(2, 100)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows)
        self.tablo.cellDoubleClicked.connect(self._hucre_duzenleme)

        self._tabloyu_doldur()
        yerlesim.addWidget(self.tablo)

        # Butonlar
        buton_yerlesim = QHBoxLayout()

        sifirla_btn = QPushButton('Tümünü Sıfırla')
        sifirla_btn.clicked.connect(self._tumunu_sifirla)
        buton_yerlesim.addWidget(sifirla_btn)

        buton_yerlesim.addStretch()

        kapat_btn = QPushButton('Kapat')
        kapat_btn.clicked.connect(self.accept)
        buton_yerlesim.addWidget(kapat_btn)

        yerlesim.addLayout(buton_yerlesim)

    def _tabloyu_doldur(self):
        """Tabloyu kısayollarla doldurur."""
        self.tablo.setRowCount(len(VARSAYILAN_KISAYOLLAR))

        for i, (anahtar, (varsayilan, aciklama)) in enumerate(VARSAYILAN_KISAYOLLAR.items()):
            # İşlem adı
            islem_item = QTableWidgetItem(aciklama)
            islem_item.setData(Qt.UserRole, anahtar)
            islem_item.setFlags(islem_item.flags() & ~Qt.ItemIsEditable)
            self.tablo.setItem(i, 0, islem_item)

            # Mevcut kısayol
            mevcut = self.yonetici.kisayol_getir(anahtar) if self.yonetici else varsayilan
            kisayol_item = QTableWidgetItem(mevcut)
            kisayol_item.setFlags(kisayol_item.flags() & ~Qt.ItemIsEditable)
            if mevcut != varsayilan:
                kisayol_item.setForeground(Qt.blue)
            self.tablo.setItem(i, 1, kisayol_item)

            # Varsayılan
            varsayilan_item = QTableWidgetItem(varsayilan)
            varsayilan_item.setFlags(varsayilan_item.flags() & ~Qt.ItemIsEditable)
            varsayilan_item.setForeground(Qt.gray)
            self.tablo.setItem(i, 2, varsayilan_item)

    def _hucre_duzenleme(self, row: int, column: int):
        """Hücre düzenleme - kısayol değiştirme."""
        if column != 1:  # Sadece kısayol sütunu düzenlenebilir
            return

        anahtar = self.tablo.item(row, 0).data(Qt.UserRole)
        mevcut = self.tablo.item(row, 1).text()

        dialog = KisayolDuzenlemeDialog(self, anahtar, mevcut, self.yonetici)
        if dialog.exec_():
            yeni_kisayol = dialog.kisayol_getir()
            if yeni_kisayol and yeni_kisayol != mevcut:
                if self.yonetici:
                    self.yonetici.kisayol_kaydet(anahtar, yeni_kisayol)
                self.tablo.item(row, 1).setText(yeni_kisayol)
                self.kisayolDegisti.emit(anahtar, yeni_kisayol)

    def _tumunu_sifirla(self):
        """Tüm kısayolları sıfırlar."""
        cevap = QMessageBox.question(
            self, 'Sıfırla',
            'Tüm kısayolları varsayılana sıfırlamak istediğinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No
        )

        if cevap == QMessageBox.Yes:
            if self.yonetici:
                self.yonetici.tum_kisayollari_sifirla()
            self._tabloyu_doldur()


class KisayolDuzenlemeDialog(QDialog):
    """Tek kısayol düzenleme dialogu."""

    def __init__(self, parent=None, anahtar: str = '', mevcut: str = '', yonetici=None):
        super().__init__(parent)
        self.anahtar = anahtar
        self.mevcut = mevcut
        self.yonetici = yonetici
        self.yeni_kisayol = mevcut
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Kısayol Düzenle')
        self.setMinimumWidth(350)

        yerlesim = QVBoxLayout(self)

        # Bilgi
        if self.anahtar in VARSAYILAN_KISAYOLLAR:
            aciklama = VARSAYILAN_KISAYOLLAR[self.anahtar][1]
        else:
            aciklama = self.anahtar

        bilgi = QLabel(f'"{aciklama}" için yeni kısayol belirleyin')
        yerlesim.addWidget(bilgi)

        # Kısayol girişi
        self.kisayol_edit = QKeySequenceEdit()
        self.kisayol_edit.setKeySequence(QKeySequence(self.mevcut))
        self.kisayol_edit.keySequenceChanged.connect(self._kisayol_degisti)
        yerlesim.addWidget(self.kisayol_edit)

        # Uyarı etiketi
        self.uyari_label = QLabel('')
        self.uyari_label.setStyleSheet('color: orange;')
        yerlesim.addWidget(self.uyari_label)

        # Butonlar
        buton_yerlesim = QHBoxLayout()

        temizle_btn = QPushButton('Temizle')
        temizle_btn.clicked.connect(lambda: self.kisayol_edit.clear())
        buton_yerlesim.addWidget(temizle_btn)

        buton_yerlesim.addStretch()

        iptal_btn = QPushButton('İptal')
        iptal_btn.clicked.connect(self.reject)
        buton_yerlesim.addWidget(iptal_btn)

        self.kaydet_btn = QPushButton('Kaydet')
        self.kaydet_btn.clicked.connect(self.accept)
        buton_yerlesim.addWidget(self.kaydet_btn)

        yerlesim.addLayout(buton_yerlesim)

    def _kisayol_degisti(self, keySequence: QKeySequence):
        """Kısayol değiştiğinde."""
        self.yeni_kisayol = keySequence.toString()

        # Çakışma kontrolü
        if self.yonetici:
            cakisan = self.yonetici.cakisma_kontrol(self.anahtar, self.yeni_kisayol)
            if cakisan:
                aciklama = self.yonetici.aciklama_getir(cakisan) or cakisan
                self.uyari_label.setText(f'⚠️ "{aciklama}" ile çakışıyor!')
                self.kaydet_btn.setEnabled(False)
            else:
                self.uyari_label.setText('')
                self.kaydet_btn.setEnabled(True)

    def kisayol_getir(self) -> str:
        """Girilen kısayolu döndürür."""
        return self.yeni_kisayol
