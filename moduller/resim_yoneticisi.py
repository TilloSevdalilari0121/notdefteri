# -*- coding: utf-8 -*-
"""
Not Defteri - Resim Yönetici Modülü
Notlara resim ekleme, yapıştırma ve sürükle-bırak desteği.
"""

import os
import base64
import hashlib
import shutil
from datetime import datetime
from typing import Optional, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QDialog, QFrame, QScrollArea, QGridLayout,
    QMenu, QAction, QSlider, QSpinBox, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import (
    QPixmap, QImage, QDrag, QPainter, QColor, QClipboard,
    QDragEnterEvent, QDropEvent, QImageReader
)


class ResimYoneticisi:
    """Resim dosyalarını yöneten sınıf."""

    DESTEKLENEN_FORMATLAR = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg']
    MAX_BOYUT_MB = 10  # Maksimum dosya boyutu

    def __init__(self, veritabani_yolu: str):
        """
        Args:
            veritabani_yolu: Veritabanı dosyasının bulunduğu klasör
        """
        self.ana_klasor = os.path.dirname(veritabani_yolu)
        self.resim_klasoru = os.path.join(self.ana_klasor, 'resimler')
        os.makedirs(self.resim_klasoru, exist_ok=True)

    def resim_kaydet(self, kaynak_yol: str = None, pixmap: QPixmap = None,
                     orijinal_ad: str = None) -> Optional[str]:
        """
        Resmi kaydeder ve benzersiz dosya adı döndürür.

        Args:
            kaynak_yol: Kaynak dosya yolu
            pixmap: QPixmap nesnesi (clipboard'dan)
            orijinal_ad: Orijinal dosya adı

        Returns:
            Kaydedilen dosya adı veya None
        """
        try:
            if kaynak_yol:
                # Dosyadan yükle
                dosya_uzantisi = os.path.splitext(kaynak_yol)[1].lower().lstrip('.')
                if dosya_uzantisi not in self.DESTEKLENEN_FORMATLAR:
                    return None

                # Dosya boyutu kontrolü
                boyut_mb = os.path.getsize(kaynak_yol) / (1024 * 1024)
                if boyut_mb > self.MAX_BOYUT_MB:
                    return None

                # Benzersiz isim oluştur
                hash_str = hashlib.md5(open(kaynak_yol, 'rb').read()).hexdigest()[:8]
                zaman = datetime.now().strftime('%Y%m%d_%H%M%S')
                yeni_ad = f'{zaman}_{hash_str}.{dosya_uzantisi}'

                hedef_yol = os.path.join(self.resim_klasoru, yeni_ad)
                shutil.copy2(kaynak_yol, hedef_yol)

                return yeni_ad

            elif pixmap and not pixmap.isNull():
                # Pixmap'ten kaydet
                zaman = datetime.now().strftime('%Y%m%d_%H%M%S')
                yeni_ad = f'{zaman}_clipboard.png'
                hedef_yol = os.path.join(self.resim_klasoru, yeni_ad)

                pixmap.save(hedef_yol, 'PNG')
                return yeni_ad

            return None
        except Exception as e:
            print(f"Resim kaydetme hatası: {e}")
            return None

    def resim_yolu_getir(self, dosya_adi: str) -> str:
        """Resmin tam yolunu döndürür."""
        return os.path.join(self.resim_klasoru, dosya_adi)

    def resim_sil(self, dosya_adi: str) -> bool:
        """Resmi siler."""
        try:
            yol = self.resim_yolu_getir(dosya_adi)
            if os.path.exists(yol):
                os.remove(yol)
                return True
            return False
        except Exception:
            return False

    def resim_base64(self, dosya_adi: str) -> Optional[str]:
        """Resmi base64 formatında döndürür."""
        try:
            yol = self.resim_yolu_getir(dosya_adi)
            with open(yol, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return None

    def kullanilmayan_resimleri_temizle(self, kullanilan_resimler: list):
        """Kullanılmayan resimleri temizler."""
        try:
            for dosya in os.listdir(self.resim_klasoru):
                if dosya not in kullanilan_resimler:
                    self.resim_sil(dosya)
        except Exception:
            pass

    def resim_boyutlandir(self, dosya_adi: str, max_genislik: int = 800,
                         max_yukseklik: int = 600) -> Optional[QPixmap]:
        """
        Resmi boyutlandırır.

        Returns:
            Boyutlandırılmış QPixmap
        """
        yol = self.resim_yolu_getir(dosya_adi)
        if not os.path.exists(yol):
            return None

        pixmap = QPixmap(yol)
        if pixmap.isNull():
            return None

        return pixmap.scaled(
            max_genislik, max_yukseklik,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )


class ResimDialog(QDialog):
    """Resim ekleme ve düzenleme dialogu."""

    resimEklendi = pyqtSignal(str, int, int)  # dosya_adi, genislik, yukseklik

    def __init__(self, parent=None, resim_yoneticisi=None):
        super().__init__(parent)
        self.resim_yoneticisi = resim_yoneticisi
        self.secili_dosya = None
        self.orijinal_pixmap = None
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Resim Ekle')
        self.setMinimumSize(600, 500)
        self.setAcceptDrops(True)

        yerlesim = QVBoxLayout(self)

        # Sürükle-bırak alanı
        self.drop_alan = QFrame()
        self.drop_alan.setMinimumHeight(200)
        self.drop_alan.setStyleSheet('''
            QFrame {
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #ecf0f1;
            }
        ''')

        drop_yerlesim = QVBoxLayout(self.drop_alan)
        drop_yerlesim.setAlignment(Qt.AlignCenter)

        # Önizleme etiketi
        self.onizleme_label = QLabel('📷\n\nResmi buraya sürükleyin\nveya aşağıdan seçin')
        self.onizleme_label.setAlignment(Qt.AlignCenter)
        self.onizleme_label.setStyleSheet('color: #7f8c8d; font-size: 14px;')
        drop_yerlesim.addWidget(self.onizleme_label)

        yerlesim.addWidget(self.drop_alan)

        # Butonlar
        buton_yerlesim = QHBoxLayout()

        self.dosya_sec_btn = QPushButton('📁 Dosyadan Seç')
        self.dosya_sec_btn.clicked.connect(self._dosya_sec)
        buton_yerlesim.addWidget(self.dosya_sec_btn)

        self.pano_btn = QPushButton('📋 Panodan Yapıştır')
        self.pano_btn.clicked.connect(self._panodan_yapistir)
        buton_yerlesim.addWidget(self.pano_btn)

        yerlesim.addLayout(buton_yerlesim)

        # Boyut ayarları
        boyut_frame = QFrame()
        boyut_frame.setStyleSheet('background-color: #f5f5f5; border-radius: 6px; padding: 10px;')
        boyut_yerlesim = QHBoxLayout(boyut_frame)

        boyut_yerlesim.addWidget(QLabel('Genişlik:'))
        self.genislik_spin = QSpinBox()
        self.genislik_spin.setRange(50, 2000)
        self.genislik_spin.setValue(400)
        self.genislik_spin.valueChanged.connect(self._boyut_degisti)
        boyut_yerlesim.addWidget(self.genislik_spin)

        boyut_yerlesim.addWidget(QLabel('Yükseklik:'))
        self.yukseklik_spin = QSpinBox()
        self.yukseklik_spin.setRange(50, 2000)
        self.yukseklik_spin.setValue(300)
        self.yukseklik_spin.valueChanged.connect(self._boyut_degisti)
        boyut_yerlesim.addWidget(self.yukseklik_spin)

        self.oran_koru_check = QPushButton('🔗')
        self.oran_koru_check.setCheckable(True)
        self.oran_koru_check.setChecked(True)
        self.oran_koru_check.setToolTip('En-boy oranını koru')
        self.oran_koru_check.setFixedSize(30, 30)
        boyut_yerlesim.addWidget(self.oran_koru_check)

        boyut_yerlesim.addStretch()

        yerlesim.addWidget(boyut_frame)

        # Alt butonlar
        alt_yerlesim = QHBoxLayout()

        self.iptal_btn = QPushButton('İptal')
        self.iptal_btn.clicked.connect(self.reject)
        alt_yerlesim.addWidget(self.iptal_btn)

        alt_yerlesim.addStretch()

        self.ekle_btn = QPushButton('Resmi Ekle')
        self.ekle_btn.setEnabled(False)
        self.ekle_btn.clicked.connect(self._resmi_ekle)
        alt_yerlesim.addWidget(self.ekle_btn)

        yerlesim.addLayout(alt_yerlesim)

    def _dosya_sec(self):
        """Dosya seçme dialogunu açar."""
        formatlar = ' '.join([f'*.{f}' for f in ResimYoneticisi.DESTEKLENEN_FORMATLAR])
        dosya, _ = QFileDialog.getOpenFileName(
            self, 'Resim Seç',
            '',
            f'Resim Dosyaları ({formatlar});;Tüm Dosyalar (*.*)'
        )

        if dosya:
            self._resim_yukle(dosya)

    def _panodan_yapistir(self):
        """Panodan resim yapıştırır."""
        pano = QApplication.clipboard()
        pixmap = pano.pixmap()

        if not pixmap.isNull():
            self.orijinal_pixmap = pixmap
            self._onizleme_goster(pixmap)
            self.secili_dosya = None
            self._boyut_ayarla(pixmap.width(), pixmap.height())
            self.ekle_btn.setEnabled(True)
        else:
            QMessageBox.warning(self, 'Uyarı', 'Panoda resim bulunamadı.')

    def _resim_yukle(self, dosya_yolu: str):
        """Resmi yükler ve önizleme gösterir."""
        pixmap = QPixmap(dosya_yolu)
        if not pixmap.isNull():
            self.orijinal_pixmap = pixmap
            self.secili_dosya = dosya_yolu
            self._onizleme_goster(pixmap)
            self._boyut_ayarla(pixmap.width(), pixmap.height())
            self.ekle_btn.setEnabled(True)

    def _onizleme_goster(self, pixmap: QPixmap):
        """Önizleme gösterir."""
        onizleme = pixmap.scaled(
            self.drop_alan.width() - 40,
            self.drop_alan.height() - 40,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.onizleme_label.setPixmap(onizleme)

    def _boyut_ayarla(self, genislik: int, yukseklik: int):
        """Boyut değerlerini ayarlar."""
        self.genislik_spin.blockSignals(True)
        self.yukseklik_spin.blockSignals(True)

        self.genislik_spin.setValue(min(genislik, 800))
        self.yukseklik_spin.setValue(min(yukseklik, 600))

        self.genislik_spin.blockSignals(False)
        self.yukseklik_spin.blockSignals(False)

    def _boyut_degisti(self, deger: int):
        """Boyut değiştiğinde oran koruma."""
        if not self.oran_koru_check.isChecked() or not self.orijinal_pixmap:
            return

        sender = self.sender()
        oran = self.orijinal_pixmap.width() / self.orijinal_pixmap.height()

        if sender == self.genislik_spin:
            self.yukseklik_spin.blockSignals(True)
            self.yukseklik_spin.setValue(int(deger / oran))
            self.yukseklik_spin.blockSignals(False)
        else:
            self.genislik_spin.blockSignals(True)
            self.genislik_spin.setValue(int(deger * oran))
            self.genislik_spin.blockSignals(False)

    def _resmi_ekle(self):
        """Resmi kaydeder ve ekler."""
        if not self.resim_yoneticisi:
            return

        if self.secili_dosya:
            dosya_adi = self.resim_yoneticisi.resim_kaydet(kaynak_yol=self.secili_dosya)
        elif self.orijinal_pixmap:
            dosya_adi = self.resim_yoneticisi.resim_kaydet(pixmap=self.orijinal_pixmap)
        else:
            return

        if dosya_adi:
            self.resimEklendi.emit(
                dosya_adi,
                self.genislik_spin.value(),
                self.yukseklik_spin.value()
            )
            self.accept()
        else:
            QMessageBox.warning(self, 'Hata', 'Resim kaydedilemedi.')

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Sürükleme girişi."""
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Bırakma olayı."""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if url.isLocalFile():
                self._resim_yukle(url.toLocalFile())
        elif event.mimeData().hasImage():
            image = event.mimeData().imageData()
            if image:
                pixmap = QPixmap.fromImage(image)
                self.orijinal_pixmap = pixmap
                self._onizleme_goster(pixmap)
                self._boyut_ayarla(pixmap.width(), pixmap.height())
                self.ekle_btn.setEnabled(True)


class ResimOnizleyici(QLabel):
    """Resim önizleme ve bağlam menüsü widget'ı."""

    silindi = pyqtSignal(str)  # dosya_adi
    boyutDegisti = pyqtSignal(str, int, int)  # dosya_adi, genislik, yukseklik

    def __init__(self, dosya_adi: str, resim_yoneticisi, parent=None):
        super().__init__(parent)
        self.dosya_adi = dosya_adi
        self.resim_yoneticisi = resim_yoneticisi
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu_goster)

    def _menu_goster(self, pos):
        """Bağlam menüsünü gösterir."""
        menu = QMenu(self)

        kopyala = menu.addAction('📋 Kopyala')
        kopyala.triggered.connect(self._kopyala)

        menu.addSeparator()

        sil = menu.addAction('🗑 Sil')
        sil.triggered.connect(lambda: self.silindi.emit(self.dosya_adi))

        menu.exec_(self.mapToGlobal(pos))

    def _kopyala(self):
        """Resmi panoya kopyalar."""
        yol = self.resim_yoneticisi.resim_yolu_getir(self.dosya_adi)
        pixmap = QPixmap(yol)
        if not pixmap.isNull():
            QApplication.clipboard().setPixmap(pixmap)
