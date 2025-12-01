# -*- coding: utf-8 -*-
"""
Not Defteri - Sürüm Geçmişi Modülü
Notların sürüm geçmişi ve geri yükleme.
"""

import difflib
from datetime import datetime
from typing import List, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextEdit, QLabel, QPushButton, QSplitter, QFrame, QMessageBox,
    QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor


class SurumGecmisiYoneticisi:
    """Not sürümlerini yöneten sınıf."""

    def __init__(self, veritabani):
        self.vt = veritabani
        self.max_surum = 50  # Maksimum saklanan sürüm sayısı

    def surum_kaydet(self, not_id: int, baslik: str, icerik: str, zengin_icerik: str):
        """
        Yeni sürüm kaydeder.

        Args:
            not_id: Not ID'si
            baslik: Not başlığı
            icerik: Düz metin içerik
            zengin_icerik: HTML içerik
        """
        # Mevcut sürüm sayısını kontrol et
        surumler = self.vt.surumleri_getir(not_id)
        if len(surumler) >= self.max_surum:
            # En eski sürümü sil
            self.vt.surum_sil(surumler[-1]['id'])

        # Yeni sürüm kaydet
        self.vt.surum_ekle(not_id, baslik, icerik, zengin_icerik)

    def surumleri_getir(self, not_id: int) -> List[dict]:
        """Notun tüm sürümlerini getirir."""
        return self.vt.surumleri_getir(not_id)

    def surum_getir(self, surum_id: int) -> Optional[dict]:
        """Belirli bir sürümü getirir."""
        return self.vt.surum_getir(surum_id)

    def geri_yukle(self, not_id: int, surum_id: int) -> bool:
        """
        Notu belirli bir sürüme geri yükler.

        Returns:
            Başarılı ise True
        """
        surum = self.surum_getir(surum_id)
        if not surum:
            return False

        # Mevcut durumu önce yeni sürüm olarak kaydet
        mevcut = self.vt.not_getir(not_id)
        if mevcut:
            self.surum_kaydet(
                not_id,
                mevcut['baslik'],
                mevcut.get('icerik', ''),
                mevcut.get('zengin_icerik', '')
            )

        # Geri yükle
        self.vt.not_guncelle(
            not_id,
            baslik=surum['baslik'],
            icerik=surum['icerik'],
            zengin_icerik=surum['zengin_icerik']
        )

        return True

    def fark_hesapla(self, eski_icerik: str, yeni_icerik: str) -> List[tuple]:
        """
        İki içerik arasındaki farkları hesaplar.

        Returns:
            [(islem, satir), ...] - islem: '+', '-', ' '
        """
        eski_satirlar = eski_icerik.splitlines(keepends=True)
        yeni_satirlar = yeni_icerik.splitlines(keepends=True)

        differ = difflib.Differ()
        farklar = list(differ.compare(eski_satirlar, yeni_satirlar))

        sonuc = []
        for satir in farklar:
            if satir.startswith('+ '):
                sonuc.append(('+', satir[2:]))
            elif satir.startswith('- '):
                sonuc.append(('-', satir[2:]))
            elif satir.startswith('  '):
                sonuc.append((' ', satir[2:]))
            # '?' satırlarını atla (fark göstergeleri)

        return sonuc

    def surumleri_temizle(self, not_id: int, kalan_surum: int = 5):
        """Eski sürümleri temizler, sadece belirtilen sayıda kalır."""
        surumler = self.surumleri_getir(not_id)
        silinecekler = surumler[kalan_surum:]

        for surum in silinecekler:
            self.vt.surum_sil(surum['id'])


class SurumGecmisiDialog(QDialog):
    """Sürüm geçmişi görüntüleme ve geri yükleme dialogu."""

    geriYuklendi = pyqtSignal(int)  # surum_id

    def __init__(self, parent=None, surum_yoneticisi=None, not_id: int = None, not_baslik: str = ''):
        super().__init__(parent)
        self.surum_yoneticisi = surum_yoneticisi
        self.not_id = not_id
        self.not_baslik = not_baslik
        self.secili_surum = None
        self._arayuz_olustur()
        self._surumleri_yukle()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle(f'Sürüm Geçmişi - {self.not_baslik}')
        self.setMinimumSize(800, 600)

        ana_yerlesim = QVBoxLayout(self)

        # Bilgi etiketi
        bilgi = QLabel(f'📝 "{self.not_baslik}" notunun sürüm geçmişi')
        bilgi.setFont(QFont('Segoe UI', 11, QFont.Bold))
        ana_yerlesim.addWidget(bilgi)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Sol: Sürüm listesi
        sol_frame = QFrame()
        sol_yerlesim = QVBoxLayout(sol_frame)
        sol_yerlesim.setContentsMargins(0, 0, 0, 0)

        sol_baslik = QLabel('Sürümler')
        sol_baslik.setFont(QFont('Segoe UI', 10, QFont.Bold))
        sol_yerlesim.addWidget(sol_baslik)

        self.surum_listesi = QListWidget()
        self.surum_listesi.currentItemChanged.connect(self._surum_secildi)
        sol_yerlesim.addWidget(self.surum_listesi)

        splitter.addWidget(sol_frame)

        # Sağ: İçerik önizleme
        sag_frame = QFrame()
        sag_yerlesim = QVBoxLayout(sag_frame)
        sag_yerlesim.setContentsMargins(0, 0, 0, 0)

        # Önizleme başlık
        self.onizleme_baslik = QLabel('Sürüm Detayı')
        self.onizleme_baslik.setFont(QFont('Segoe UI', 10, QFont.Bold))
        sag_yerlesim.addWidget(self.onizleme_baslik)

        # Tarih bilgisi
        self.tarih_label = QLabel('')
        self.tarih_label.setStyleSheet('color: gray;')
        sag_yerlesim.addWidget(self.tarih_label)

        # İçerik görünümü seçimi
        gorunum_yerlesim = QHBoxLayout()
        self.icerik_btn = QPushButton('İçerik')
        self.icerik_btn.setCheckable(True)
        self.icerik_btn.setChecked(True)
        self.icerik_btn.clicked.connect(lambda: self._gorunum_degistir('icerik'))

        self.fark_btn = QPushButton('Farklar')
        self.fark_btn.setCheckable(True)
        self.fark_btn.clicked.connect(lambda: self._gorunum_degistir('fark'))

        gorunum_yerlesim.addWidget(self.icerik_btn)
        gorunum_yerlesim.addWidget(self.fark_btn)
        gorunum_yerlesim.addStretch()
        sag_yerlesim.addLayout(gorunum_yerlesim)

        # İçerik alanı
        self.icerik_alani = QTextEdit()
        self.icerik_alani.setReadOnly(True)
        self.icerik_alani.setFont(QFont('Consolas', 10))
        sag_yerlesim.addWidget(self.icerik_alani)

        splitter.addWidget(sag_frame)
        splitter.setSizes([250, 550])

        ana_yerlesim.addWidget(splitter)

        # Butonlar
        buton_yerlesim = QHBoxLayout()

        self.geri_yukle_btn = QPushButton('🔄 Bu Sürüme Geri Yükle')
        self.geri_yukle_btn.setEnabled(False)
        self.geri_yukle_btn.clicked.connect(self._geri_yukle)
        buton_yerlesim.addWidget(self.geri_yukle_btn)

        buton_yerlesim.addStretch()

        kapat_btn = QPushButton('Kapat')
        kapat_btn.clicked.connect(self.reject)
        buton_yerlesim.addWidget(kapat_btn)

        ana_yerlesim.addLayout(buton_yerlesim)

    def _surumleri_yukle(self):
        """Sürüm listesini yükler."""
        if not self.surum_yoneticisi or not self.not_id:
            return

        self.surum_listesi.clear()
        surumler = self.surum_yoneticisi.surumleri_getir(self.not_id)

        for i, surum in enumerate(surumler):
            tarih = surum.get('tarih', '')
            if tarih:
                try:
                    dt = datetime.strptime(tarih, '%Y-%m-%d %H:%M:%S')
                    tarih_str = dt.strftime('%d.%m.%Y %H:%M')
                except:
                    tarih_str = tarih
            else:
                tarih_str = 'Bilinmiyor'

            # Sürüm numarası (en yeni = en büyük numara)
            surum_no = len(surumler) - i

            item = QListWidgetItem(f'v{surum_no} - {tarih_str}')
            item.setData(Qt.UserRole, surum)

            if i == 0:
                item.setText(f'v{surum_no} - {tarih_str} (Son)')
                item.setForeground(QColor('#2196F3'))

            self.surum_listesi.addItem(item)

    def _surum_secildi(self, item: QListWidgetItem):
        """Sürüm seçildiğinde çağrılır."""
        if not item:
            return

        self.secili_surum = item.data(Qt.UserRole)
        self.geri_yukle_btn.setEnabled(True)

        # Başlık güncelle
        self.onizleme_baslik.setText(f'📄 {self.secili_surum.get("baslik", "Başlıksız")}')

        # Tarih güncelle
        tarih = self.secili_surum.get('tarih', '')
        if tarih:
            try:
                dt = datetime.strptime(tarih, '%Y-%m-%d %H:%M:%S')
                self.tarih_label.setText(f'Kaydedilme: {dt.strftime("%d %B %Y, %H:%M:%S")}')
            except:
                self.tarih_label.setText(f'Kaydedilme: {tarih}')

        # İçeriği göster
        self._gorunum_degistir('icerik' if self.icerik_btn.isChecked() else 'fark')

    def _gorunum_degistir(self, mod: str):
        """Görünüm modunu değiştirir."""
        self.icerik_btn.setChecked(mod == 'icerik')
        self.fark_btn.setChecked(mod == 'fark')

        if not self.secili_surum:
            return

        if mod == 'icerik':
            self.icerik_alani.setPlainText(self.secili_surum.get('icerik', ''))
        else:
            self._farklari_goster()

    def _farklari_goster(self):
        """Mevcut not ile seçili sürüm arasındaki farkları gösterir."""
        if not self.secili_surum or not self.surum_yoneticisi:
            return

        # Mevcut içeriği al
        mevcut = self.surum_yoneticisi.vt.not_getir(self.not_id)
        if not mevcut:
            return

        mevcut_icerik = mevcut.get('icerik', '')
        surum_icerik = self.secili_surum.get('icerik', '')

        # Farkları hesapla
        farklar = self.surum_yoneticisi.fark_hesapla(surum_icerik, mevcut_icerik)

        # Renkli gösterim
        self.icerik_alani.clear()
        cursor = self.icerik_alani.textCursor()

        for islem, satir in farklar:
            format = QTextCharFormat()

            if islem == '+':
                format.setBackground(QColor('#e6ffed'))  # Yeşil - eklenen
                format.setForeground(QColor('#22863a'))
                satir = '+ ' + satir
            elif islem == '-':
                format.setBackground(QColor('#ffeef0'))  # Kırmızı - silinen
                format.setForeground(QColor('#cb2431'))
                satir = '- ' + satir
            else:
                satir = '  ' + satir

            cursor.insertText(satir, format)

    def _geri_yukle(self):
        """Seçili sürüme geri yükler."""
        if not self.secili_surum:
            return

        cevap = QMessageBox.question(
            self, 'Geri Yükle',
            'Bu sürüme geri yüklemek istediğinize emin misiniz?\n'
            'Mevcut içerik yeni bir sürüm olarak kaydedilecek.',
            QMessageBox.Yes | QMessageBox.No
        )

        if cevap == QMessageBox.Yes:
            basari = self.surum_yoneticisi.geri_yukle(
                self.not_id,
                self.secili_surum['id']
            )

            if basari:
                self.geriYuklendi.emit(self.secili_surum['id'])
                QMessageBox.information(self, 'Başarılı', 'Not başarıyla geri yüklendi.')
                self._surumleri_yukle()
            else:
                QMessageBox.warning(self, 'Hata', 'Geri yükleme başarısız oldu.')
