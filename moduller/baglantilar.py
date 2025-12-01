# -*- coding: utf-8 -*-
"""
Not Defteri - Notlar Arası Bağlantı Modülü
[[Not Adı]] şeklinde notlar arası bağlantı desteği.
"""

import re
from typing import List, Optional, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QCompleter, QFrame, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt5.QtGui import (
    QTextCharFormat, QColor, QSyntaxHighlighter, QFont,
    QTextCursor, QTextDocument
)


class NotBaglantisiYoneticisi:
    """Notlar arası bağlantıları yöneten sınıf."""

    # [[Not Adı]] veya [[Not Adı|Görünen Metin]] formatı
    BAGLANTI_DESENI = r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'

    def __init__(self, veritabani):
        self.vt = veritabani

    def baglantilari_bul(self, metin: str) -> List[Tuple[str, str, int, int]]:
        """
        Metindeki tüm bağlantıları bulur.

        Returns:
            [(not_adi, gorunen_metin, baslangic, bitis), ...]
        """
        baglantilar = []
        for match in re.finditer(self.BAGLANTI_DESENI, metin):
            not_adi = match.group(1).strip()
            gorunen = match.group(2).strip() if match.group(2) else not_adi
            baglantilar.append((not_adi, gorunen, match.start(), match.end()))
        return baglantilar

    def baglanti_cozumle(self, not_adi: str) -> Optional[int]:
        """
        Bağlantı adından not ID'sini bulur.

        Returns:
            Not ID'si veya None
        """
        # Tam eşleşme ara
        notlar = self.vt.notlari_ara(not_adi)
        for not_verisi in notlar:
            if not_verisi['baslik'].lower() == not_adi.lower():
                return not_verisi['id']

        # Kısmi eşleşme
        if notlar:
            return notlar[0]['id']

        return None

    def geri_baglantilar(self, not_id: int) -> List[dict]:
        """
        Bu nota bağlantı veren notları bulur (backlinks).

        Returns:
            Bağlantı veren notların listesi
        """
        not_verisi = self.vt.not_getir(not_id)
        if not not_verisi:
            return []

        not_adi = not_verisi['baslik']
        desen = f'[[{not_adi}' # [[Not Adı ile başlayan

        return self.vt.baglanti_iceren_notlari_getir(desen)

    def baglanti_olustur(self, not_adi: str, gorunen_metin: str = None) -> str:
        """
        Bağlantı metni oluşturur.

        Args:
            not_adi: Bağlanılacak notun adı
            gorunen_metin: Görünecek metin (opsiyonel)

        Returns:
            [[Not Adı]] veya [[Not Adı|Görünen Metin]]
        """
        if gorunen_metin and gorunen_metin != not_adi:
            return f'[[{not_adi}|{gorunen_metin}]]'
        return f'[[{not_adi}]]'

    def not_onerileri(self, arama: str, limit: int = 10) -> List[str]:
        """
        Bağlantı için not önerileri döndürür.

        Returns:
            Not başlıkları listesi
        """
        if not arama:
            # Son güncellenen notları öner
            notlar = self.vt.notlari_getir(siralama='guncelleme_tarihi DESC')
        else:
            notlar = self.vt.notlari_ara(arama)

        return [n['baslik'] for n in notlar[:limit]]

    def baglanti_grafigi_olustur(self, not_id: int) -> dict:
        """
        Not için bağlantı grafiği oluşturur.

        Returns:
            {
                'merkez': not_id,
                'giden': [bağlantı verilen not ID'leri],
                'gelen': [bağlantı veren not ID'leri]
            }
        """
        not_verisi = self.vt.not_getir(not_id)
        if not not_verisi:
            return {'merkez': not_id, 'giden': [], 'gelen': []}

        # Giden bağlantılar
        icerik = not_verisi.get('icerik', '')
        baglantilar = self.baglantilari_bul(icerik)
        giden = []
        for not_adi, _, _, _ in baglantilar:
            baglanti_id = self.baglanti_cozumle(not_adi)
            if baglanti_id and baglanti_id not in giden:
                giden.append(baglanti_id)

        # Gelen bağlantılar (backlinks)
        geri_baglantilar = self.geri_baglantilar(not_id)
        gelen = [n['id'] for n in geri_baglantilar]

        return {
            'merkez': not_id,
            'giden': giden,
            'gelen': gelen
        }


class BaglantiVurgulayici(QSyntaxHighlighter):
    """[[Bağlantı]] sözdizimini vurgular."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Bağlantı formatı
        self.baglanti_format = QTextCharFormat()
        self.baglanti_format.setForeground(QColor('#9b59b6'))
        self.baglanti_format.setFontUnderline(True)

        # Geçersiz bağlantı formatı
        self.gecersiz_format = QTextCharFormat()
        self.gecersiz_format.setForeground(QColor('#e74c3c'))
        self.gecersiz_format.setFontUnderline(True)

        self.baglanti_yoneticisi = None

    def baglanti_yoneticisi_ayarla(self, yonetici: NotBaglantisiYoneticisi):
        """Bağlantı yöneticisini ayarlar."""
        self.baglanti_yoneticisi = yonetici

    def highlightBlock(self, text):
        """Metin bloğunu vurgular."""
        for match in re.finditer(NotBaglantisiYoneticisi.BAGLANTI_DESENI, text):
            baslangic = match.start()
            uzunluk = match.end() - match.start()
            not_adi = match.group(1).strip()

            # Bağlantının geçerli olup olmadığını kontrol et
            if self.baglanti_yoneticisi:
                not_id = self.baglanti_yoneticisi.baglanti_cozumle(not_adi)
                if not_id:
                    self.setFormat(baslangic, uzunluk, self.baglanti_format)
                else:
                    self.setFormat(baslangic, uzunluk, self.gecersiz_format)
            else:
                self.setFormat(baslangic, uzunluk, self.baglanti_format)


class BaglantiOnizleyici(QFrame):
    """Bağlantıların önizlemesini gösteren widget."""

    notaGit = pyqtSignal(int)  # not_id

    def __init__(self, parent=None, baglanti_yoneticisi=None):
        super().__init__(parent)
        self.baglanti_yoneticisi = baglanti_yoneticisi
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Arayüzü oluşturur."""
        self.setObjectName('baglantiOnizleyici')
        self.setFrameShape(QFrame.StyledPanel)
        self.setMaximumHeight(200)

        yerlesim = QVBoxLayout(self)
        yerlesim.setContentsMargins(10, 10, 10, 10)

        # Başlık
        self.baslik = QLabel('🔗 Bağlantılar')
        self.baslik.setFont(QFont('Segoe UI', 10, QFont.Bold))
        yerlesim.addWidget(self.baslik)

        # Bağlantı listesi
        self.baglanti_listesi = QListWidget()
        self.baglanti_listesi.itemDoubleClicked.connect(self._baglantiya_git)
        yerlesim.addWidget(self.baglanti_listesi)

    def baglantilar_goster(self, not_id: int):
        """Notun bağlantılarını gösterir."""
        self.baglanti_listesi.clear()

        if not self.baglanti_yoneticisi:
            return

        grafik = self.baglanti_yoneticisi.baglanti_grafigi_olustur(not_id)

        # Giden bağlantılar
        if grafik['giden']:
            baslik = QListWidgetItem('📤 Bağlantı Verilen Notlar')
            baslik.setFlags(Qt.NoItemFlags)
            baslik.setForeground(QColor('gray'))
            self.baglanti_listesi.addItem(baslik)

            for baglanti_id in grafik['giden']:
                not_verisi = self.baglanti_yoneticisi.vt.not_getir(baglanti_id)
                if not_verisi:
                    item = QListWidgetItem(f"  → {not_verisi['baslik']}")
                    item.setData(Qt.UserRole, baglanti_id)
                    self.baglanti_listesi.addItem(item)

        # Gelen bağlantılar (backlinks)
        if grafik['gelen']:
            baslik = QListWidgetItem('📥 Bu Nota Bağlantı Veren Notlar')
            baslik.setFlags(Qt.NoItemFlags)
            baslik.setForeground(QColor('gray'))
            self.baglanti_listesi.addItem(baslik)

            for baglanti_id in grafik['gelen']:
                not_verisi = self.baglanti_yoneticisi.vt.not_getir(baglanti_id)
                if not_verisi:
                    item = QListWidgetItem(f"  ← {not_verisi['baslik']}")
                    item.setData(Qt.UserRole, baglanti_id)
                    self.baglanti_listesi.addItem(item)

        if not grafik['giden'] and not grafik['gelen']:
            item = QListWidgetItem('Bağlantı bulunamadı')
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(QColor('gray'))
            self.baglanti_listesi.addItem(item)

    def _baglantiya_git(self, item: QListWidgetItem):
        """Bağlantılı nota gider."""
        not_id = item.data(Qt.UserRole)
        if not_id:
            self.notaGit.emit(not_id)


class BaglantiTamamlayici(QCompleter):
    """[[Bağlantı yazarken otomatik tamamlama."""

    def __init__(self, parent=None, baglanti_yoneticisi=None):
        super().__init__(parent)
        self.baglanti_yoneticisi = baglanti_yoneticisi
        self.model_data = QStringListModel()
        self.setModel(self.model_data)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)

    def onerileri_guncelle(self, arama: str = ''):
        """Önerileri günceller."""
        if self.baglanti_yoneticisi:
            oneriler = self.baglanti_yoneticisi.not_onerileri(arama)
            self.model_data.setStringList(oneriler)
