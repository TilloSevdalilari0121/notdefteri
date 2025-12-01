# -*- coding: utf-8 -*-
"""
Not Defteri - Takvim Görünümü Modülü
Notları takvim üzerinde görüntüleme.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCalendarWidget, QFrame, QScrollArea, QListWidget,
    QListWidgetItem, QDialog, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QBrush


class TakvimWidget(QCalendarWidget):
    """Özelleştirilmiş takvim widget'ı."""

    tarihSecildi = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.not_tarihleri = {}  # {tarih_str: not_sayisi}
        self._stil_uygula()

        # Tarih seçim sinyali
        self.clicked.connect(self.tarihSecildi.emit)

    def _stil_uygula(self):
        """Takvim stilini uygular."""
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # Hafta günleri başlığı
        header_format = QTextCharFormat()
        header_format.setFontWeight(QFont.Bold)
        header_format.setForeground(QColor('#2c3e50'))
        self.setHeaderTextFormat(header_format)

        # Hafta sonu formatı
        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor('#e74c3c'))
        self.setWeekdayTextFormat(Qt.Saturday, weekend_format)
        self.setWeekdayTextFormat(Qt.Sunday, weekend_format)

    def not_tarihlerini_ayarla(self, tarihler: Dict[str, int]):
        """
        Not içeren tarihleri ayarlar.

        Args:
            tarihler: {tarih_str: not_sayisi} formatında
        """
        self.not_tarihleri = tarihler
        self.updateCells()

    def paintCell(self, painter, rect, date):
        """Takvim hücresini çizer."""
        super().paintCell(painter, rect, date)

        tarih_str = date.toString('yyyy-MM-dd')
        not_sayisi = self.not_tarihleri.get(tarih_str, 0)

        if not_sayisi > 0:
            # Not göstergesi çiz
            painter.save()

            # Daire gösterge
            indicator_size = 8
            x = rect.right() - indicator_size - 3
            y = rect.top() + 3

            if not_sayisi == 1:
                painter.setBrush(QBrush(QColor('#3498db')))
            elif not_sayisi <= 3:
                painter.setBrush(QBrush(QColor('#2ecc71')))
            else:
                painter.setBrush(QBrush(QColor('#e74c3c')))

            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x, y, indicator_size, indicator_size)

            painter.restore()


class GunNotlariWidget(QFrame):
    """Belirli bir güne ait notları gösteren widget."""

    notSecildi = pyqtSignal(int)  # not_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Arayüzü oluşturur."""
        self.setStyleSheet('''
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        ''')

        yerlesim = QVBoxLayout(self)

        # Başlık
        self.baslik = QLabel('Notlar')
        self.baslik.setFont(QFont('Segoe UI', 11, QFont.Bold))
        yerlesim.addWidget(self.baslik)

        # Not listesi
        self.liste = QListWidget()
        self.liste.setStyleSheet('''
            QListWidget {
                border: none;
                background: transparent;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        ''')
        self.liste.itemDoubleClicked.connect(self._not_sec)
        yerlesim.addWidget(self.liste)

    def notlari_goster(self, tarih: QDate, notlar: List[Dict]):
        """Belirli tarihin notlarını gösterir."""
        self.baslik.setText(f"📅 {tarih.toString('d MMMM yyyy')} ({len(notlar)} not)")
        self.liste.clear()

        for not_verisi in notlar:
            item = QListWidgetItem()

            # Başlık ve önizleme
            baslik = not_verisi.get('baslik', 'Başlıksız')
            icerik = not_verisi.get('icerik', '')[:50]
            if len(not_verisi.get('icerik', '')) > 50:
                icerik += '...'

            item.setText(f"📝 {baslik}\n   {icerik}")
            item.setData(Qt.UserRole, not_verisi.get('id'))

            # Favori gösterge
            if not_verisi.get('favori'):
                item.setText(f"⭐ {baslik}\n   {icerik}")

            self.liste.addItem(item)

        if not notlar:
            item = QListWidgetItem('Bu tarihte not bulunmuyor')
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(QColor('gray'))
            self.liste.addItem(item)

    def _not_sec(self, item: QListWidgetItem):
        """Not seçildiğinde."""
        not_id = item.data(Qt.UserRole)
        if not_id:
            self.notSecildi.emit(not_id)


class TakvimGorunumu(QWidget):
    """Takvim görünümü ana widget'ı."""

    notSecildi = pyqtSignal(int)  # not_id

    def __init__(self, parent=None, veritabani=None):
        super().__init__(parent)
        self.vt = veritabani
        self._arayuz_olustur()
        self._verileri_yukle()

    def _arayuz_olustur(self):
        """Arayüzü oluşturur."""
        ana_yerlesim = QHBoxLayout(self)
        ana_yerlesim.setContentsMargins(0, 0, 0, 0)

        # Sol: Takvim
        sol_panel = QFrame()
        sol_yerlesim = QVBoxLayout(sol_panel)

        # Navigasyon
        nav_yerlesim = QHBoxLayout()

        self.onceki_btn = QPushButton('◀ Önceki Ay')
        self.onceki_btn.clicked.connect(self._onceki_ay)
        nav_yerlesim.addWidget(self.onceki_btn)

        self.bugun_btn = QPushButton('Bugün')
        self.bugun_btn.clicked.connect(self._bugune_git)
        nav_yerlesim.addWidget(self.bugun_btn)

        self.sonraki_btn = QPushButton('Sonraki Ay ▶')
        self.sonraki_btn.clicked.connect(self._sonraki_ay)
        nav_yerlesim.addWidget(self.sonraki_btn)

        sol_yerlesim.addLayout(nav_yerlesim)

        # Takvim
        self.takvim = TakvimWidget()
        self.takvim.tarihSecildi.connect(self._tarih_secildi)
        self.takvim.currentPageChanged.connect(self._sayfa_degisti)
        sol_yerlesim.addWidget(self.takvim)

        # İstatistikler
        self.istatistik_label = QLabel('')
        self.istatistik_label.setStyleSheet('color: gray; font-size: 11px;')
        sol_yerlesim.addWidget(self.istatistik_label)

        ana_yerlesim.addWidget(sol_panel, 2)

        # Sağ: Günün notları
        self.gun_notlari = GunNotlariWidget()
        self.gun_notlari.notSecildi.connect(self.notSecildi.emit)
        ana_yerlesim.addWidget(self.gun_notlari, 1)

    def _verileri_yukle(self):
        """Takvim verilerini yükler."""
        if not self.vt:
            return

        # Bu ayki not tarihlerini getir
        self._ayin_notlarini_yukle()

        # Bugünün notlarını göster
        bugun = QDate.currentDate()
        self._tarih_secildi(bugun)

    def _ayin_notlarini_yukle(self):
        """Mevcut ayın not tarihlerini yükler."""
        if not self.vt:
            return

        # Ayın başı ve sonu
        current = self.takvim.selectedDate()
        ay_basi = QDate(current.year(), current.month(), 1)
        ay_sonu = QDate(current.year(), current.month(), current.daysInMonth())

        tarihler = {}

        try:
            with self.vt._baglanti_al() as baglanti:
                imlec = baglanti.cursor()
                imlec.execute('''
                    SELECT DATE(olusturma_tarihi) as tarih, COUNT(*) as sayi
                    FROM notlar
                    WHERE silindi = 0
                      AND DATE(olusturma_tarihi) BETWEEN ? AND ?
                    GROUP BY DATE(olusturma_tarihi)
                ''', (ay_basi.toString('yyyy-MM-dd'), ay_sonu.toString('yyyy-MM-dd')))

                for row in imlec.fetchall():
                    tarihler[row['tarih']] = row['sayi']

        except Exception as e:
            print(f"Takvim veri yükleme hatası: {e}")

        self.takvim.not_tarihlerini_ayarla(tarihler)

        # İstatistik
        toplam = sum(tarihler.values())
        gun_sayisi = len(tarihler)
        self.istatistik_label.setText(
            f"Bu ay: {toplam} not, {gun_sayisi} farklı gün"
        )

    def _tarih_secildi(self, tarih: QDate):
        """Tarih seçildiğinde."""
        if not self.vt:
            return

        tarih_str = tarih.toString('yyyy-MM-dd')

        try:
            with self.vt._baglanti_al() as baglanti:
                imlec = baglanti.cursor()
                imlec.execute('''
                    SELECT * FROM notlar
                    WHERE silindi = 0 AND DATE(olusturma_tarihi) = ?
                    ORDER BY olusturma_tarihi DESC
                ''', (tarih_str,))

                notlar = [dict(row) for row in imlec.fetchall()]

        except Exception as e:
            print(f"Günlük not yükleme hatası: {e}")
            notlar = []

        self.gun_notlari.notlari_goster(tarih, notlar)

    def _sayfa_degisti(self, yil: int, ay: int):
        """Takvim sayfası değiştiğinde."""
        self._ayin_notlarini_yukle()

    def _onceki_ay(self):
        """Önceki aya git."""
        self.takvim.showPreviousMonth()

    def _sonraki_ay(self):
        """Sonraki aya git."""
        self.takvim.showNextMonth()

    def _bugune_git(self):
        """Bugüne git."""
        self.takvim.setSelectedDate(QDate.currentDate())
        self.takvim.showToday()
        self._verileri_yukle()

    def yenile(self):
        """Verileri yeniler."""
        self._verileri_yukle()


class TakvimDialog(QDialog):
    """Takvim görünümü dialogu."""

    notSecildi = pyqtSignal(int)

    def __init__(self, parent=None, veritabani=None):
        super().__init__(parent)
        self.vt = veritabani
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('📅 Takvim Görünümü')
        self.setMinimumSize(800, 500)

        yerlesim = QVBoxLayout(self)

        # Takvim görünümü
        self.takvim_gorunumu = TakvimGorunumu(veritabani=self.vt)
        self.takvim_gorunumu.notSecildi.connect(self._not_secildi)
        yerlesim.addWidget(self.takvim_gorunumu)

        # Kapat butonu
        kapat_btn = QPushButton('Kapat')
        kapat_btn.clicked.connect(self.accept)
        yerlesim.addWidget(kapat_btn)

    def _not_secildi(self, not_id: int):
        """Not seçildiğinde."""
        self.notSecildi.emit(not_id)
        self.accept()
