# -*- coding: utf-8 -*-
"""
Not Defteri - Yapılacaklar Listesi Modülü
Checkbox destekli yapılacaklar listesi.
"""

import re
from typing import List, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea, QProgressBar,
    QListWidget, QListWidgetItem, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor


class YapilacaklarYoneticisi:
    """Yapılacaklar listesi işlemlerini yöneten sınıf."""

    # [ ] ve [x] deseni
    YAPILACAK_DESENI = r'^(\s*[-*+]?\s*)\[([ xX])\]\s*(.*)$'

    def __init__(self):
        pass

    def yapilacaklari_ayikla(self, metin: str) -> List[Tuple[int, bool, str, int]]:
        """
        Metinden yapılacak maddelerini ayıklar.

        Returns:
            [(satir_no, tamamlandi_mi, metin, girinti_seviyesi), ...]
        """
        yapilacaklar = []
        satirlar = metin.split('\n')

        for i, satir in enumerate(satirlar):
            match = re.match(self.YAPILACAK_DESENI, satir)
            if match:
                girinti = len(match.group(1))
                tamamlandi = match.group(2).lower() == 'x'
                icerik = match.group(3).strip()
                yapilacaklar.append((i, tamamlandi, icerik, girinti))

        return yapilacaklar

    def durumu_degistir(self, metin: str, satir_no: int) -> str:
        """
        Belirtilen satırdaki yapılacak maddesinin durumunu değiştirir.

        Returns:
            Güncellenmiş metin
        """
        satirlar = metin.split('\n')

        if satir_no < 0 or satir_no >= len(satirlar):
            return metin

        satir = satirlar[satir_no]
        match = re.match(self.YAPILACAK_DESENI, satir)

        if match:
            girinti = match.group(1)
            durum = match.group(2)
            icerik = match.group(3)

            yeni_durum = ' ' if durum.lower() == 'x' else 'x'
            satirlar[satir_no] = f'{girinti}[{yeni_durum}] {icerik}'

        return '\n'.join(satirlar)

    def yapilacak_ekle(self, metin: str, icerik: str, konum: int = -1) -> str:
        """
        Yeni yapılacak maddesi ekler.

        Args:
            metin: Mevcut metin
            icerik: Yeni madde içeriği
            konum: Eklenecek satır (varsayılan: sona)

        Returns:
            Güncellenmiş metin
        """
        yeni_satir = f'- [ ] {icerik}'
        satirlar = metin.split('\n') if metin else []

        if konum < 0 or konum >= len(satirlar):
            satirlar.append(yeni_satir)
        else:
            satirlar.insert(konum + 1, yeni_satir)

        return '\n'.join(satirlar)

    def yapilacak_sil(self, metin: str, satir_no: int) -> str:
        """Yapılacak maddesini siler."""
        satirlar = metin.split('\n')

        if 0 <= satir_no < len(satirlar):
            del satirlar[satir_no]

        return '\n'.join(satirlar)

    def istatistikler(self, metin: str) -> dict:
        """
        Yapılacaklar istatistiklerini hesaplar.

        Returns:
            {
                'toplam': int,
                'tamamlanan': int,
                'bekleyen': int,
                'yuzde': float
            }
        """
        yapilacaklar = self.yapilacaklari_ayikla(metin)

        toplam = len(yapilacaklar)
        tamamlanan = sum(1 for _, tamamlandi, _, _ in yapilacaklar if tamamlandi)

        return {
            'toplam': toplam,
            'tamamlanan': tamamlanan,
            'bekleyen': toplam - tamamlanan,
            'yuzde': (tamamlanan / toplam * 100) if toplam > 0 else 0
        }

    def tamamlananlari_temizle(self, metin: str) -> str:
        """Tamamlanan maddeleri metinden kaldırır."""
        satirlar = metin.split('\n')
        yeni_satirlar = []

        for satir in satirlar:
            match = re.match(self.YAPILACAK_DESENI, satir)
            if match:
                if match.group(2).lower() != 'x':
                    yeni_satirlar.append(satir)
            else:
                yeni_satirlar.append(satir)

        return '\n'.join(yeni_satirlar)

    def tumunu_tamamla(self, metin: str) -> str:
        """Tüm maddeleri tamamlandı olarak işaretler."""
        satirlar = metin.split('\n')

        for i, satir in enumerate(satirlar):
            match = re.match(self.YAPILACAK_DESENI, satir)
            if match:
                girinti = match.group(1)
                icerik = match.group(3)
                satirlar[i] = f'{girinti}[x] {icerik}'

        return '\n'.join(satirlar)


class YapilacakMaddesi(QFrame):
    """Tek bir yapılacak maddesi widget'ı."""

    durumDegisti = pyqtSignal(int, bool)  # satir_no, yeni_durum
    silindi = pyqtSignal(int)  # satir_no
    duzenlendi = pyqtSignal(int, str)  # satir_no, yeni_metin

    def __init__(self, satir_no: int, tamamlandi: bool, metin: str, girinti: int = 0, parent=None):
        super().__init__(parent)
        self.satir_no = satir_no
        self.girinti = girinti
        self._arayuz_olustur(tamamlandi, metin)

    def _arayuz_olustur(self, tamamlandi: bool, metin: str):
        """Widget arayüzünü oluşturur."""
        self.setFrameShape(QFrame.NoFrame)

        yerlesim = QHBoxLayout(self)
        yerlesim.setContentsMargins(self.girinti * 20, 2, 5, 2)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(tamamlandi)
        self.checkbox.stateChanged.connect(self._durum_degisti)
        yerlesim.addWidget(self.checkbox)

        # Metin etiketi
        self.metin_label = QLabel(metin)
        if tamamlandi:
            self.metin_label.setStyleSheet('text-decoration: line-through; color: gray;')
        yerlesim.addWidget(self.metin_label, 1)

        # Sil butonu (hover'da görünür)
        self.sil_btn = QPushButton('×')
        self.sil_btn.setFixedSize(20, 20)
        self.sil_btn.setStyleSheet('''
            QPushButton {
                background: transparent;
                border: none;
                color: #e74c3c;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #fee;
                border-radius: 10px;
            }
        ''')
        self.sil_btn.hide()
        self.sil_btn.clicked.connect(lambda: self.silindi.emit(self.satir_no))
        yerlesim.addWidget(self.sil_btn)

    def _durum_degisti(self, durum: int):
        """Durum değişikliği."""
        tamamlandi = durum == Qt.Checked
        if tamamlandi:
            self.metin_label.setStyleSheet('text-decoration: line-through; color: gray;')
        else:
            self.metin_label.setStyleSheet('')
        self.durumDegisti.emit(self.satir_no, tamamlandi)

    def enterEvent(self, event):
        """Mouse girişinde sil butonunu göster."""
        self.sil_btn.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse çıkışında sil butonunu gizle."""
        self.sil_btn.hide()
        super().leaveEvent(event)


class YapilacaklarWidget(QWidget):
    """Yapılacaklar listesi ana widget'ı."""

    icerikDegisti = pyqtSignal(str)  # Güncellenmiş metin

    def __init__(self, parent=None):
        super().__init__(parent)
        self.yonetici = YapilacaklarYoneticisi()
        self.metin = ''
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Widget arayüzünü oluşturur."""
        ana_yerlesim = QVBoxLayout(self)
        ana_yerlesim.setContentsMargins(0, 0, 0, 0)

        # Üst bar - İstatistikler ve aksiyonlar
        ust_yerlesim = QHBoxLayout()

        # İlerleme çubuğu
        self.ilerleme = QProgressBar()
        self.ilerleme.setMaximumHeight(8)
        self.ilerleme.setTextVisible(False)
        self.ilerleme.setStyleSheet('''
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 4px;
            }
        ''')
        ust_yerlesim.addWidget(self.ilerleme, 1)

        # İstatistik etiketi
        self.istatistik_label = QLabel('0/0')
        self.istatistik_label.setStyleSheet('color: gray; margin-left: 10px;')
        ust_yerlesim.addWidget(self.istatistik_label)

        # Menü butonu
        self.menu_btn = QPushButton('⋮')
        self.menu_btn.setFixedSize(25, 25)
        self.menu_btn.setStyleSheet('border: none;')
        self.menu_btn.clicked.connect(self._menu_goster)
        ust_yerlesim.addWidget(self.menu_btn)

        ana_yerlesim.addLayout(ust_yerlesim)

        # Yeni madde ekleme
        ekle_yerlesim = QHBoxLayout()

        self.yeni_madde_input = QLineEdit()
        self.yeni_madde_input.setPlaceholderText('Yeni yapılacak ekle...')
        self.yeni_madde_input.returnPressed.connect(self._yeni_madde_ekle)
        ekle_yerlesim.addWidget(self.yeni_madde_input)

        self.ekle_btn = QPushButton('+')
        self.ekle_btn.setFixedSize(30, 30)
        self.ekle_btn.clicked.connect(self._yeni_madde_ekle)
        ekle_yerlesim.addWidget(self.ekle_btn)

        ana_yerlesim.addLayout(ekle_yerlesim)

        # Scroll area - yapılacaklar listesi
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.liste_widget = QWidget()
        self.liste_yerlesim = QVBoxLayout(self.liste_widget)
        self.liste_yerlesim.setContentsMargins(0, 0, 0, 0)
        self.liste_yerlesim.setSpacing(2)
        self.liste_yerlesim.addStretch()

        self.scroll.setWidget(self.liste_widget)
        ana_yerlesim.addWidget(self.scroll)

    def metni_ayarla(self, metin: str):
        """Metni ayarlar ve listeyi günceller."""
        self.metin = metin
        self._listeyi_guncelle()

    def metni_getir(self) -> str:
        """Güncel metni döndürür."""
        return self.metin

    def _listeyi_guncelle(self):
        """Yapılacaklar listesini günceller."""
        # Mevcut widget'ları temizle
        while self.liste_yerlesim.count() > 1:
            item = self.liste_yerlesim.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Yapılacakları ayıkla ve ekle
        yapilacaklar = self.yonetici.yapilacaklari_ayikla(self.metin)

        for satir_no, tamamlandi, icerik, girinti in yapilacaklar:
            madde = YapilacakMaddesi(satir_no, tamamlandi, icerik, girinti)
            madde.durumDegisti.connect(self._madde_durumu_degisti)
            madde.silindi.connect(self._madde_silindi)
            self.liste_yerlesim.insertWidget(
                self.liste_yerlesim.count() - 1, madde
            )

        # İstatistikleri güncelle
        self._istatistikleri_guncelle()

    def _istatistikleri_guncelle(self):
        """İstatistikleri günceller."""
        stats = self.yonetici.istatistikler(self.metin)
        self.ilerleme.setValue(int(stats['yuzde']))
        self.istatistik_label.setText(f"{stats['tamamlanan']}/{stats['toplam']}")

    def _madde_durumu_degisti(self, satir_no: int, yeni_durum: bool):
        """Madde durumu değiştiğinde."""
        self.metin = self.yonetici.durumu_degistir(self.metin, satir_no)
        self._istatistikleri_guncelle()
        self.icerikDegisti.emit(self.metin)

    def _madde_silindi(self, satir_no: int):
        """Madde silindiğinde."""
        self.metin = self.yonetici.yapilacak_sil(self.metin, satir_no)
        self._listeyi_guncelle()
        self.icerikDegisti.emit(self.metin)

    def _yeni_madde_ekle(self):
        """Yeni madde ekler."""
        icerik = self.yeni_madde_input.text().strip()
        if icerik:
            self.metin = self.yonetici.yapilacak_ekle(self.metin, icerik)
            self.yeni_madde_input.clear()
            self._listeyi_guncelle()
            self.icerikDegisti.emit(self.metin)

    def _menu_goster(self):
        """Aksiyon menüsünü gösterir."""
        menu = QMenu(self)

        tumunu_tamamla = menu.addAction('✓ Tümünü Tamamla')
        tumunu_tamamla.triggered.connect(self._tumunu_tamamla)

        tamamlananlari_sil = menu.addAction('🗑 Tamamlananları Sil')
        tamamlananlari_sil.triggered.connect(self._tamamlananlari_sil)

        menu.exec_(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def _tumunu_tamamla(self):
        """Tüm maddeleri tamamlar."""
        self.metin = self.yonetici.tumunu_tamamla(self.metin)
        self._listeyi_guncelle()
        self.icerikDegisti.emit(self.metin)

    def _tamamlananlari_sil(self):
        """Tamamlanan maddeleri siler."""
        self.metin = self.yonetici.tamamlananlari_temizle(self.metin)
        self._listeyi_guncelle()
        self.icerikDegisti.emit(self.metin)
