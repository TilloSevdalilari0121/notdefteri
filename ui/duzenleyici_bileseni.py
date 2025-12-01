# ui/duzenleyici_bileseni.py
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QTabWidget, QTextEdit, QWidget, QLabel, QMessageBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

class DuzenleyiciBileseni(QFrame):
    """
    Notları sekmeler içinde gösteren ve düzenleyen arayüz bileşeni.
    """
    durumDegisti = Signal(bool, bool) # Kaydedebilir, Silebilir durumlarını bildirir

    def __init__(self, veritabani_yoneticisi, parent=None):
        super().__init__(parent)
        self.db = veritabani_yoneticisi

        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(0, 0, 0, 0)

        self.sekme_kontrolu = QTabWidget()
        self.sekme_kontrolu.setTabsClosable(True)
        self.sekme_kontrolu.tabCloseRequested.connect(self._sekme_kapatma_istegi)
        self.sekme_kontrolu.currentChanged.connect(self._durumu_guncelle)

        # Hoş geldiniz sekmesi
        self.karsilama_sekmesi = QWidget()
        karsilama_layout = QVBoxLayout(self.karsilama_sekmesi)
        karsilama_label = QLabel("Profesyonel Not Defterine Hoş Geldiniz!")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        karsilama_label.setFont(font)
        karsilama_layout.addWidget(karsilama_label)
        karsilama_layout.addWidget(QLabel("Düzenlemeye başlamak için listeden bir not seçin veya yeni bir not oluşturun."))

        self.sekme_kontrolu.addTab(self.karsilama_sekmesi, "Hoş Geldiniz")

        self.ana_layout.addWidget(self.sekme_kontrolu)

    def _not_sekmesini_bul(self, not_id):
        """Verilen not ID'sine sahip açık sekmeyi bulur."""
        for i in range(self.sekme_kontrolu.count()):
            sekme = self.sekme_kontrolu.widget(i)
            # widget'ın 'not_id' özelliğini kontrol et
            if hasattr(sekme, 'not_id') and sekme.not_id == not_id:
                return sekme
        return None

    def notu_sekmede_ac(self, not_id):
        """Bir notu yeni bir sekmede açar veya zaten açıksa o sekmeye geçer."""
        mevcut_sekme = self._not_sekmesini_bul(not_id)
        if mevcut_sekme:
            self.sekme_kontrolu.setCurrentWidget(mevcut_sekme)
            return

        not_detay = self.db.get_not_detay(not_id)
        if not not_detay:
            return

        yeni_sekme = QWidget()
        yeni_sekme.not_id = not_id # Sekmeye özel veri ekle
        yeni_sekme.degisiklik_var = False

        sekme_layout = QVBoxLayout(yeni_sekme)
        sekme_layout.setContentsMargins(5, 5, 5, 5)

        zengin_metin_editoru = QTextEdit()
        zengin_metin_editoru.setHtml(not_detay['Icerik'] or "")
        zengin_metin_editoru.textChanged.connect(lambda: self._degisiklik_oldu(yeni_sekme))

        yeni_sekme.zengin_metin_editoru = zengin_metin_editoru # Kolay erişim için referans

        sekme_layout.addWidget(zengin_metin_editoru)

        index = self.sekme_kontrolu.addTab(yeni_sekme, not_detay['Baslik'])
        self.sekme_kontrolu.setCurrentIndex(index)

    def _degisiklik_oldu(self, sekme):
        """Metin değiştiğinde sekme başlığına '*' ekler."""
        sekme.degisiklik_var = True
        index = self.sekme_kontrolu.indexOf(sekme)
        mevcut_baslik = self.sekme_kontrolu.tabText(index)
        if not mevcut_baslik.endswith('*'):
            self.sekme_kontrolu.setTabText(index, mevcut_baslik + '*')
        self._durumu_guncelle()

    def _durumu_guncelle(self):
        """Ana penceredeki eylemlerin (Kaydet, Sil) durumunu günceller."""
        aktif_sekme = self.sekme_kontrolu.currentWidget()
        kaydedebilir = False
        silebilir = False

        if aktif_sekme and hasattr(aktif_sekme, 'not_id'):
            silebilir = True
            if aktif_sekme.degisiklik_var:
                kaydedebilir = True

        self.durumDegisti.emit(kaydedebilir, silebilir)

    def mevcut_notu_kaydet(self):
        """Aktif sekmedeki notu veritabanına kaydeder."""
        aktif_sekme = self.sekme_kontrolu.currentWidget()
        if not (aktif_sekme and hasattr(aktif_sekme, 'not_id') and aktif_sekme.degisiklik_var):
            return False

        not_id = aktif_sekme.not_id
        editor = aktif_sekme.zengin_metin_editoru
        icerik_html = editor.toHtml()
        icerik_metin = editor.toPlainText()

        # Başlığı ilk satırdan al
        baslik = icerik_metin.split('\n')[0][:100] or "Başlıksız Not"

        self.db.notu_guncelle(not_id, baslik, icerik_html, icerik_metin)

        aktif_sekme.degisiklik_var = False
        index = self.sekme_kontrolu.indexOf(aktif_sekme)
        self.sekme_kontrolu.setTabText(index, baslik)
        self._durumu_guncelle()
        return True # Kaydetme başarılı

    def mevcut_notu_sil(self):
        """Aktif notu siler."""
        aktif_sekme = self.sekme_kontrolu.currentWidget()
        if not (aktif_sekme and hasattr(aktif_sekme, 'not_id')):
            return

        not_id = aktif_sekme.not_id
        index = self.sekme_kontrolu.indexOf(aktif_sekme)
        baslik = self.sekme_kontrolu.tabText(index).strip('*')

        yanit = QMessageBox.question(
            self,
            "Notu Sil",
            f"'{baslik}' notunu kalıcı olarak silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if yanit == QMessageBox.StandardButton.Yes:
            self.db.notu_sil(not_id)
            self.sekme_kontrolu.removeTab(index)
            aktif_sekme.deleteLater()
            return True
        return False

    def _kullaniciya_kaydetmeyi_sor(self, sekme):
        """Verilen sekmedeki değişiklikler için kullanıcıya sorar ve seçimi döndürür."""
        index = self.sekme_kontrolu.indexOf(sekme)
        baslik = self.sekme_kontrolu.tabText(index).strip('*')
        yanit = QMessageBox.question(
            self,
            "Kaydedilmemiş Değişiklikler",
            f"'{baslik}' notundaki değişiklikleri kaydetmek istiyor musunuz?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )
        return yanit

    def _sekme_kapatma_istegi(self, index):
        """Bir sekme kapatılmak istendiğinde değişiklikleri kontrol eder."""
        kapatilacak_sekme = self.sekme_kontrolu.widget(index)

        if kapatilacak_sekme == self.karsilama_sekmesi:
            return

        kapat = True
        if hasattr(kapatilacak_sekme, 'degisiklik_var') and kapatilacak_sekme.degisiklik_var:
            yanit = self._kullaniciya_kaydetmeyi_sor(kapatilacak_sekme)

            if yanit == QMessageBox.StandardButton.Save:
                if not self.mevcut_notu_kaydet():
                    kapat = False # Kaydetme başarısız olursa kapatma
            elif yanit == QMessageBox.StandardButton.Cancel:
                kapat = False # Kullanıcı iptal ederse kapatma

        if kapat:
            self.sekme_kontrolu.removeTab(index)
            kapatilacak_sekme.deleteLater()

    def tum_sekmeleri_kapatmayi_dene(self):
        """Tüm açık sekmeleri kapatmayı dener. Başarısız olursa False döndürür."""
        # Tersten döngü, çünkü sekmeleri sileceğiz
        for i in range(self.sekme_kontrolu.count() - 1, -1, -1):
            sekme = self.sekme_kontrolu.widget(i)
            if sekme == self.karsilama_sekmesi:
                continue

            kapat = True
            if hasattr(sekme, 'degisiklik_var') and sekme.degisiklik_var:
                # O sekmeye geçiş yap ve kullanıcıya sor
                self.sekme_kontrolu.setCurrentWidget(sekme)
                yanit = self._kullaniciya_kaydetmeyi_sor(sekme)
                if yanit == QMessageBox.StandardButton.Save:
                    if not self.mevcut_notu_kaydet():
                        return False # Kaydetme başarısız, kapatmayı durdur
                elif yanit == QMessageBox.StandardButton.Cancel:
                    return False # Kullanıcı iptal etti, kapatmayı durdur
        return True # Tüm kontrollerden geçti
