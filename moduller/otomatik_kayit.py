# -*- coding: utf-8 -*-
"""
Not Defteri - Otomatik Kayıt Modülü
Belirli aralıklarla otomatik kaydetme işlemi.
"""

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from datetime import datetime


class OtomatikKayitYoneticisi(QObject):
    """
    Otomatik kaydetme işlemlerini yöneten sınıf.
    Belirli aralıklarla ve değişiklik durumunda kaydetme yapar.
    """

    kayitYapildi = pyqtSignal()  # Kayıt yapıldığında
    kayitHatasi = pyqtSignal(str)  # Hata durumunda
    sonrakiKayitZamani = pyqtSignal(int)  # Kalan saniye

    def __init__(self, parent=None, aralik_saniye: int = 60):
        """
        Args:
            parent: Üst widget
            aralik_saniye: Otomatik kaydetme aralığı (saniye)
        """
        super().__init__(parent)

        self.aralik = aralik_saniye * 1000  # milisaniye
        self.aktif = True
        self.degisiklik_var = False
        self.kayit_fonksiyonu = None
        self.son_kayit = None

        # Ana timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._kaydet)

        # Geri sayım timer
        self.geri_sayim_timer = QTimer(self)
        self.geri_sayim_timer.timeout.connect(self._geri_sayim_guncelle)
        self.kalan_sure = self.aralik // 1000

    def baslat(self):
        """Otomatik kaydetmeyi başlatır."""
        if self.aktif:
            self.timer.start(self.aralik)
            self.geri_sayim_timer.start(1000)
            self.kalan_sure = self.aralik // 1000

    def durdur(self):
        """Otomatik kaydetmeyi durdurur."""
        self.timer.stop()
        self.geri_sayim_timer.stop()

    def sifirla(self):
        """Timer'ı sıfırlar (değişiklik yapıldığında)."""
        if self.aktif and self.timer.isActive():
            self.timer.stop()
            self.timer.start(self.aralik)
            self.kalan_sure = self.aralik // 1000

    def degisiklik_bildir(self):
        """Değişiklik yapıldığını bildirir."""
        self.degisiklik_var = True
        self.sifirla()

    def kayit_fonksiyonu_ayarla(self, fonksiyon):
        """Kayıt fonksiyonunu ayarlar."""
        self.kayit_fonksiyonu = fonksiyon

    def aralik_ayarla(self, saniye: int):
        """Kaydetme aralığını değiştirir."""
        self.aralik = saniye * 1000
        if self.timer.isActive():
            self.sifirla()

    def aktif_ayarla(self, durum: bool):
        """Otomatik kaydetmeyi aktif/pasif yapar."""
        self.aktif = durum
        if durum:
            self.baslat()
        else:
            self.durdur()

    def _kaydet(self):
        """Kaydetme işlemini gerçekleştirir."""
        if not self.degisiklik_var:
            return

        if self.kayit_fonksiyonu:
            try:
                self.kayit_fonksiyonu()
                self.degisiklik_var = False
                self.son_kayit = datetime.now()
                self.kayitYapildi.emit()
            except Exception as e:
                self.kayitHatasi.emit(str(e))

        self.kalan_sure = self.aralik // 1000

    def _geri_sayim_guncelle(self):
        """Geri sayımı günceller."""
        if self.kalan_sure > 0:
            self.kalan_sure -= 1
        self.sonrakiKayitZamani.emit(self.kalan_sure)

    def simdi_kaydet(self):
        """Hemen kaydetme yapar."""
        self._kaydet()
        self.sifirla()

    def son_kayit_zamani(self) -> str:
        """Son kayıt zamanını döndürür."""
        if self.son_kayit:
            return self.son_kayit.strftime('%H:%M:%S')
        return 'Henüz kaydedilmedi'


class OtomatikKayitWidget:
    """Otomatik kayıt durumunu gösteren widget için yardımcı sınıf."""

    @staticmethod
    def durum_metni(kalan_saniye: int, degisiklik_var: bool) -> str:
        """Durum çubuğu için metin oluşturur."""
        if not degisiklik_var:
            return "✓ Kaydedildi"

        if kalan_saniye > 0:
            dakika = kalan_saniye // 60
            saniye = kalan_saniye % 60
            if dakika > 0:
                return f"⏱ Otomatik kayıt: {dakika}d {saniye}s"
            return f"⏱ Otomatik kayıt: {saniye}s"

        return "💾 Kaydediliyor..."
