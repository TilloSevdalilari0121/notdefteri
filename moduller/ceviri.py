# -*- coding: utf-8 -*-
"""
Not Defteri Uygulaması - Çeviri Modülü
deep-translator kütüphanesi ile gelişmiş çeviri desteği.

Desteklenen Motorlar:
- Google Translate (ücretsiz, API key gerektirmez)
- MyMemory (ücretsiz, API key gerektirmez)
- Microsoft Translator (API key gerekli)
- DeepL (API key gerekli, en kaliteli)

Yazar: Claude AI
Tarih: 2024
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QComboBox, QProgressBar, QMessageBox, QSplitter,
    QWidget, QGroupBox, QCheckBox, QMenu, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor
import re
import html

# deep-translator import
try:
    from deep_translator import (
        GoogleTranslator,
        MyMemoryTranslator,
        LibreTranslator,
        single_detection,
        batch_detection
    )
    DEEP_TRANSLATOR_MEVCUT = True
except ImportError:
    DEEP_TRANSLATOR_MEVCUT = False
    print("Uyarı: deep-translator kütüphanesi yüklü değil. 'pip install deep-translator' ile yükleyin.")


class CeviriThread(QThread):
    """Arka planda çeviri yapan thread."""
    ilerleme = pyqtSignal(int)
    tamamlandi = pyqtSignal(str)
    hata = pyqtSignal(str)

    def __init__(self, metin: str, kaynak_dil: str, hedef_dil: str, motor: str = 'google'):
        super().__init__()
        self.metin = metin
        self.kaynak_dil = kaynak_dil
        self.hedef_dil = hedef_dil
        self.motor = motor

    def run(self):
        try:
            if not DEEP_TRANSLATOR_MEVCUT:
                self.hata.emit("deep-translator kütüphanesi yüklü değil.\npip install deep-translator")
                return

            sonuc = self._cevir(self.metin, self.kaynak_dil, self.hedef_dil)
            self.tamamlandi.emit(sonuc)
        except Exception as e:
            self.hata.emit(str(e))

    def _cevir(self, metin: str, kaynak: str, hedef: str) -> str:
        """Metni çevirir - tüm metni tek seferde çevirir (daha hızlı)."""
        try:
            # Motor seçimi
            if self.motor == 'google':
                translator = GoogleTranslator(source=kaynak, target=hedef)
            elif self.motor == 'mymemory':
                translator = MyMemoryTranslator(source=kaynak, target=hedef)
            else:
                translator = GoogleTranslator(source=kaynak, target=hedef)

            self.ilerleme.emit(10)

            # Uzun metinleri parçalara böl (5000 karakter sınırı)
            max_uzunluk = 4500

            if len(metin) > max_uzunluk:
                # Satır sonlarını koruyarak böl
                parcalar = self._metni_akilli_bol(metin, max_uzunluk)
                ceviriler = []
                toplam = len(parcalar)

                for i, parca in enumerate(parcalar):
                    if parca.strip():
                        ceviri = translator.translate(parca)
                        ceviriler.append(ceviri if ceviri else parca)
                    else:
                        ceviriler.append(parca)
                    self.ilerleme.emit(int((i + 1) / toplam * 90) + 10)

                return ''.join(ceviriler)
            else:
                self.ilerleme.emit(50)
                sonuc = translator.translate(metin)
                self.ilerleme.emit(100)
                return sonuc if sonuc else metin

        except Exception as e:
            print(f"Çeviri hatası: {e}")
            raise e

    def _metni_akilli_bol(self, metin: str, max_uzunluk: int) -> list:
        """Metni paragraf sınırlarında böler."""
        parcalar = []
        mevcut = ""

        for satir in metin.split('\n'):
            if len(mevcut) + len(satir) + 1 < max_uzunluk:
                mevcut += satir + '\n'
            else:
                if mevcut:
                    parcalar.append(mevcut)
                mevcut = satir + '\n'

        if mevcut:
            parcalar.append(mevcut)

        return parcalar

    def _paragraf_cevir(self, metin: str, kaynak: str, hedef: str) -> str:
        """Tek bir paragrafı çevirir."""
        if not metin.strip():
            return metin

        try:
            # Motor seçimi
            if self.motor == 'google':
                translator = GoogleTranslator(source=kaynak, target=hedef)
            elif self.motor == 'mymemory':
                translator = MyMemoryTranslator(source=kaynak, target=hedef)
            elif self.motor == 'libre':
                # LibreTranslate ücretsiz API
                translator = LibreTranslator(source=kaynak, target=hedef)
            else:
                translator = GoogleTranslator(source=kaynak, target=hedef)

            # Uzun metinleri parçalara böl (deep-translator 5000 karakter sınırı)
            max_uzunluk = 4500

            if len(metin) > max_uzunluk:
                parcalar = self._metni_bol(metin, max_uzunluk)
                ceviriler = []
                for parca in parcalar:
                    ceviri = translator.translate(parca)
                    ceviriler.append(ceviri if ceviri else parca)
                return ''.join(ceviriler)
            else:
                sonuc = translator.translate(metin)
                return sonuc if sonuc else metin

        except Exception as e:
            print(f"Paragraf çeviri hatası: {e}")
            return metin

    def _metni_bol(self, metin: str, max_uzunluk: int) -> list:
        """Metni cümlelere göre böler."""
        cumleler = re.split(r'([.!?]+\s*)', metin)
        parcalar = []
        mevcut_parca = ""

        for cumle in cumleler:
            if len(mevcut_parca) + len(cumle) < max_uzunluk:
                mevcut_parca += cumle
            else:
                if mevcut_parca:
                    parcalar.append(mevcut_parca)
                mevcut_parca = cumle

        if mevcut_parca:
            parcalar.append(mevcut_parca)

        return parcalar


class CeviriDialog(QDialog):
    """Çeviri diyaloğu."""

    # Desteklenen diller (Google Translate)
    DILLER = {
        'auto': 'Otomatik Algıla',
        'en': 'İngilizce',
        'tr': 'Türkçe',
        'de': 'Almanca',
        'fr': 'Fransızca',
        'es': 'İspanyolca',
        'it': 'İtalyanca',
        'pt': 'Portekizce',
        'ru': 'Rusça',
        'zh-CN': 'Çince (Basitleştirilmiş)',
        'zh-TW': 'Çince (Geleneksel)',
        'ja': 'Japonca',
        'ko': 'Korece',
        'ar': 'Arapça',
        'hi': 'Hintçe',
        'nl': 'Hollandaca',
        'pl': 'Lehçe',
        'sv': 'İsveççe',
        'da': 'Danca',
        'fi': 'Fince',
        'no': 'Norveççe',
        'el': 'Yunanca',
        'cs': 'Çekçe',
        'ro': 'Romence',
        'hu': 'Macarca',
        'uk': 'Ukraynaca',
        'id': 'Endonezce',
        'th': 'Tayca',
        'vi': 'Vietnamca'
    }

    MOTORLAR = [
        ('google', 'Google Translate (Önerilen)'),
        ('mymemory', 'MyMemory (Yavaş)')
    ]

    def __init__(self, parent=None, baslangic_metni: str = "", html_metin: str = ""):
        super().__init__(parent)
        self.setWindowTitle("İçerik Çevirici")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        self._ceviri_thread = None
        self._cevrilmis_metin = ""
        self._orijinal_html = html_metin  # Orijinal HTML'i sakla
        self._arayuz_olustur()

        if baslangic_metni:
            self.kaynak_metin.setPlainText(baslangic_metni)

    def _arayuz_olustur(self):
        """Arayüzü oluşturur."""
        ana_yerlesim = QVBoxLayout(self)

        # Üst ayarlar grubu
        ayar_grup = QGroupBox("Çeviri Ayarları")
        ayar_yerlesim = QHBoxLayout(ayar_grup)

        # Motor seçimi
        ayar_yerlesim.addWidget(QLabel("Motor:"))
        self.motor_combo = QComboBox()
        for kod, isim in self.MOTORLAR:
            self.motor_combo.addItem(isim, kod)
        self.motor_combo.setCurrentIndex(0)  # Google varsayılan
        self.motor_combo.setToolTip("Google Translate en iyi sonucu verir")
        ayar_yerlesim.addWidget(self.motor_combo)

        ayar_yerlesim.addWidget(QLabel("  |  "))

        # Kaynak dil
        ayar_yerlesim.addWidget(QLabel("Kaynak:"))
        self.kaynak_dil = QComboBox()
        for kod, isim in self.DILLER.items():
            self.kaynak_dil.addItem(isim, kod)
        self.kaynak_dil.setCurrentIndex(0)  # auto
        ayar_yerlesim.addWidget(self.kaynak_dil)

        ayar_yerlesim.addWidget(QLabel("→"))

        # Hedef dil
        ayar_yerlesim.addWidget(QLabel("Hedef:"))
        self.hedef_dil = QComboBox()
        for kod, isim in self.DILLER.items():
            if kod != 'auto':
                self.hedef_dil.addItem(isim, kod)
        # Türkçe varsayılan
        tr_index = self.hedef_dil.findData('tr')
        if tr_index >= 0:
            self.hedef_dil.setCurrentIndex(tr_index)
        ayar_yerlesim.addWidget(self.hedef_dil)

        ayar_yerlesim.addStretch()

        # Dilleri değiştir butonu
        self.dil_degistir_btn = QPushButton("⇄")
        self.dil_degistir_btn.setFixedWidth(30)
        self.dil_degistir_btn.setToolTip("Kaynak ve hedef dilleri değiştir")
        self.dil_degistir_btn.clicked.connect(self._dilleri_degistir)
        ayar_yerlesim.addWidget(self.dil_degistir_btn)

        ana_yerlesim.addWidget(ayar_grup)

        # Metin alanları (bölünmüş)
        splitter = QSplitter(Qt.Horizontal)

        # Kaynak metin
        kaynak_widget = QWidget()
        kaynak_yerlesim = QVBoxLayout(kaynak_widget)
        kaynak_yerlesim.setContentsMargins(0, 0, 0, 0)

        kaynak_baslik = QHBoxLayout()
        kaynak_baslik.addWidget(QLabel("Orijinal Metin:"))
        self.karakter_sayisi = QLabel("0 karakter")
        self.karakter_sayisi.setStyleSheet("color: gray;")
        kaynak_baslik.addStretch()
        kaynak_baslik.addWidget(self.karakter_sayisi)
        kaynak_yerlesim.addLayout(kaynak_baslik)

        self.kaynak_metin = QTextEdit()
        self.kaynak_metin.setFont(QFont("Segoe UI", 10))
        self.kaynak_metin.textChanged.connect(self._karakter_sayisi_guncelle)
        kaynak_yerlesim.addWidget(self.kaynak_metin)
        splitter.addWidget(kaynak_widget)

        # Çeviri
        hedef_widget = QWidget()
        hedef_yerlesim = QVBoxLayout(hedef_widget)
        hedef_yerlesim.setContentsMargins(0, 0, 0, 0)
        hedef_yerlesim.addWidget(QLabel("Çeviri:"))
        self.hedef_metin = QTextEdit()
        self.hedef_metin.setFont(QFont("Segoe UI", 10))
        self.hedef_metin.setReadOnly(True)
        hedef_yerlesim.addWidget(self.hedef_metin)
        splitter.addWidget(hedef_widget)

        ana_yerlesim.addWidget(splitter, 1)

        # İlerleme çubuğu
        self.ilerleme = QProgressBar()
        self.ilerleme.setVisible(False)
        ana_yerlesim.addWidget(self.ilerleme)

        # Düğmeler
        dugme_yerlesim = QHBoxLayout()

        self.cevir_btn = QPushButton("Çevir")
        self.cevir_btn.setDefault(True)
        self.cevir_btn.clicked.connect(self._cevir)
        self.cevir_btn.setStyleSheet("font-weight: bold; padding: 8px 20px;")
        dugme_yerlesim.addWidget(self.cevir_btn)

        self.temizle_btn = QPushButton("Temizle")
        self.temizle_btn.clicked.connect(self._temizle)
        dugme_yerlesim.addWidget(self.temizle_btn)

        self.kopyala_btn = QPushButton("Çeviriyi Kopyala")
        self.kopyala_btn.clicked.connect(self._kopyala)
        self.kopyala_btn.setEnabled(False)
        dugme_yerlesim.addWidget(self.kopyala_btn)

        dugme_yerlesim.addStretch()

        self.uygula_btn = QPushButton("Çeviriyi Uygula")
        self.uygula_btn.setEnabled(False)
        self.uygula_btn.clicked.connect(self._uygula)
        self.uygula_btn.setStyleSheet("font-weight: bold; padding: 8px 20px;")
        dugme_yerlesim.addWidget(self.uygula_btn)

        self.iptal_btn = QPushButton("İptal")
        self.iptal_btn.clicked.connect(self.reject)
        dugme_yerlesim.addWidget(self.iptal_btn)

        ana_yerlesim.addLayout(dugme_yerlesim)

        # Kütüphane kontrolü
        if not DEEP_TRANSLATOR_MEVCUT:
            self.cevir_btn.setEnabled(False)
            self.hedef_metin.setPlainText(
                "deep-translator kütüphanesi yüklü değil.\n\n"
                "Yüklemek için terminalde şu komutu çalıştırın:\n"
                "pip install deep-translator"
            )

    def _karakter_sayisi_guncelle(self):
        """Karakter sayısını günceller."""
        metin = self.kaynak_metin.toPlainText()
        self.karakter_sayisi.setText(f"{len(metin)} karakter")

    def _dilleri_degistir(self):
        """Kaynak ve hedef dilleri değiştirir."""
        kaynak_index = self.kaynak_dil.currentIndex()
        hedef_index = self.hedef_dil.currentIndex()

        # Auto seçiliyse değiştirme
        if self.kaynak_dil.currentData() == 'auto':
            return

        # Hedef dilde auto yok, index'i ayarla
        kaynak_kod = self.kaynak_dil.currentData()
        hedef_kod = self.hedef_dil.currentData()

        # Kaynak'ta hedef dili bul
        kaynak_yeni = self.kaynak_dil.findData(hedef_kod)
        if kaynak_yeni >= 0:
            self.kaynak_dil.setCurrentIndex(kaynak_yeni)

        # Hedef'te kaynak dili bul
        hedef_yeni = self.hedef_dil.findData(kaynak_kod)
        if hedef_yeni >= 0:
            self.hedef_dil.setCurrentIndex(hedef_yeni)

        # Metinleri de değiştir
        kaynak_text = self.kaynak_metin.toPlainText()
        hedef_text = self.hedef_metin.toPlainText()

        if hedef_text and hedef_text != "Çevriliyor...":
            self.kaynak_metin.setPlainText(hedef_text)
            self.hedef_metin.setPlainText(kaynak_text)

    def _cevir(self):
        """Çeviriyi başlatır."""
        metin = self.kaynak_metin.toPlainText()

        if not metin.strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen çevrilecek metin girin.")
            return

        kaynak = self.kaynak_dil.currentData()
        hedef = self.hedef_dil.currentData()
        motor = self.motor_combo.currentData()

        # UI güncelle
        self.cevir_btn.setEnabled(False)
        self.ilerleme.setVisible(True)
        self.ilerleme.setValue(0)
        self.hedef_metin.setPlainText("Çevriliyor...")

        # Thread başlat
        self._ceviri_thread = CeviriThread(metin, kaynak, hedef, motor)
        self._ceviri_thread.ilerleme.connect(self._ilerleme_guncelle)
        self._ceviri_thread.tamamlandi.connect(self._ceviri_tamamlandi)
        self._ceviri_thread.hata.connect(self._ceviri_hatasi)
        self._ceviri_thread.start()

    def _ilerleme_guncelle(self, deger: int):
        """İlerleme çubuğunu günceller."""
        self.ilerleme.setValue(deger)

    def _ceviri_tamamlandi(self, sonuc: str):
        """Çeviri tamamlandığında çağrılır."""
        self._cevrilmis_metin = sonuc
        self.hedef_metin.setPlainText(sonuc)
        self.cevir_btn.setEnabled(True)
        self.uygula_btn.setEnabled(True)
        self.kopyala_btn.setEnabled(True)
        self.ilerleme.setVisible(False)

    def _ceviri_hatasi(self, hata: str):
        """Çeviri hatası olduğunda çağrılır."""
        self.hedef_metin.setPlainText(f"Hata oluştu: {hata}")
        self.cevir_btn.setEnabled(True)
        self.ilerleme.setVisible(False)
        QMessageBox.critical(self, "Çeviri Hatası", f"Çeviri yapılırken hata oluştu:\n{hata}")

    def _temizle(self):
        """Metin alanlarını temizler."""
        self.kaynak_metin.clear()
        self.hedef_metin.clear()
        self._cevrilmis_metin = ""
        self.uygula_btn.setEnabled(False)
        self.kopyala_btn.setEnabled(False)

    def _kopyala(self):
        """Çeviriyi panoya kopyalar."""
        from PyQt5.QtWidgets import QApplication
        if self._cevrilmis_metin:
            QApplication.clipboard().setText(self._cevrilmis_metin)
            QMessageBox.information(self, "Kopyalandı", "Çeviri panoya kopyalandı.")

    def _uygula(self):
        """Çeviriyi uygular ve diyaloğu kapatır."""
        if self._cevrilmis_metin:
            self.accept()

    def cevrilmis_metin_al(self) -> str:
        """Çevrilmiş metni döndürür."""
        return self._cevrilmis_metin

    def cevrilmis_html_al(self) -> str:
        """Çevrilmiş HTML'i döndürür (orijinal formatı koruyarak)."""
        if not self._orijinal_html or not self._cevrilmis_metin:
            return ""

        # Orijinal ve çevrilmiş metinleri satır satır eşleştir
        orijinal_satirlar = self.kaynak_metin.toPlainText().split('\n')
        ceviri_satirlar = self._cevrilmis_metin.split('\n')

        # HTML içindeki metinleri değiştir
        sonuc_html = self._orijinal_html

        for orijinal, ceviri in zip(orijinal_satirlar, ceviri_satirlar):
            orijinal = orijinal.strip()
            ceviri = ceviri.strip()
            if orijinal and ceviri and orijinal != ceviri:
                # HTML içinde orijinal metni bul ve çeviri ile değiştir
                # Özel karakterleri escape et (hem pattern hem replacement için)
                orijinal_escaped = re.escape(orijinal)
                # Replacement string'de backslash'ları escape et
                ceviri_escaped = ceviri.replace('\\', '\\\\')
                # HTML tag'leri arasındaki metni değiştir
                sonuc_html = re.sub(
                    r'(>)(' + orijinal_escaped + r')(<)',
                    r'\g<1>' + ceviri_escaped + r'\g<3>',
                    sonuc_html
                )

        return sonuc_html

    def html_var_mi(self) -> bool:
        """Orijinal HTML olup olmadığını döndürür."""
        return bool(self._orijinal_html)


class CeviriYoneticisi:
    """Çeviri işlemlerini yöneten sınıf."""

    @staticmethod
    def hizli_cevir(metin: str, kaynak: str = 'auto', hedef: str = 'tr') -> str:
        """Metni hızlıca çevirir (senkron)."""
        if not DEEP_TRANSLATOR_MEVCUT:
            return metin

        try:
            translator = GoogleTranslator(source=kaynak, target=hedef)
            sonuc = translator.translate(metin)
            return sonuc if sonuc else metin
        except Exception as e:
            print(f"Hızlı çeviri hatası: {e}")
            return metin

    @staticmethod
    def toplu_cevir(metinler: list, kaynak: str = 'auto', hedef: str = 'tr') -> list:
        """Birden fazla metni çevirir."""
        if not DEEP_TRANSLATOR_MEVCUT:
            return metinler

        try:
            translator = GoogleTranslator(source=kaynak, target=hedef)
            sonuclar = translator.translate_batch(metinler)
            return sonuclar if sonuclar else metinler
        except Exception as e:
            print(f"Toplu çeviri hatası: {e}")
            return metinler

    @staticmethod
    def dil_algi(metin: str) -> str:
        """Metnin dilini algılar."""
        if not DEEP_TRANSLATOR_MEVCUT:
            return 'auto'

        try:
            dil = single_detection(metin[:500], api_key=None)
            return dil if dil else 'auto'
        except Exception as e:
            print(f"Dil algılama hatası: {e}")
            return 'auto'

    @staticmethod
    def desteklenen_diller() -> dict:
        """Desteklenen dilleri döndürür."""
        if not DEEP_TRANSLATOR_MEVCUT:
            return {}

        try:
            return GoogleTranslator().get_supported_languages(as_dict=True)
        except Exception:
            return CeviriDialog.DILLER
