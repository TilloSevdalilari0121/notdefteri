# ui/ana_pencere.py
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter, QStyleFactory, QApplication,
    QMenuBar, QToolBar, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from ui.gezgin_bileseni import GezginBileseni
from ui.not_listesi_bileseni import NotListesiBileseni
from ui.duzenleyici_bileseni import DuzenleyiciBileseni

class AnaPencere(QMainWindow):
    """
    Uygulamanın ana penceresi.
    Tüm modüler bileşenleri bir araya getirir ve aralarındaki iletişimi yönetir.
    """
    def __init__(self, veritabani_yoneticisi):
        super().__init__()
        self.db = veritabani_yoneticisi

        self.setWindowTitle("Profesyonel Not Defteri (Python)")
        self.setGeometry(100, 100, 1280, 768)

        # Ana widget ve layout
        merkezi_widget = QWidget()
        self.setCentralWidget(merkezi_widget)
        ana_layout = QHBoxLayout(merkezi_widget)

        # Splitter'lar ile modern düzen
        ana_splitter = QSplitter(Qt.Orientation.Horizontal)
        ana_layout.addWidget(ana_splitter)

        # Modüler bileşenleri oluştur
        self.gezgin = GezginBileseni(self.db)
        self.not_listesi = NotListesiBileseni(self.db)
        self.duzenleyici = DuzenleyiciBileseni(self.db)

        # Bileşenleri splitter'a ekle
        ana_splitter.addWidget(self.gezgin)
        ana_splitter.addWidget(self.not_listesi)
        ana_splitter.addWidget(self.duzenleyici)

        ana_splitter.setStretchFactor(0, 2) # Gezgin
        ana_splitter.setStretchFactor(1, 3) # Not Listesi
        ana_splitter.setStretchFactor(2, 6) # Düzenleyici

        self._eylemleri_olustur()
        self._menu_ve_arac_cubugunu_olustur()
        self._sinyal_slot_baglantilarini_kur()

        self._temayi_ayarla("Acik")

        # Başlangıçta verileri yükle
        self.gezgin.verileri_yukle()

    def _eylemleri_olustur(self):
        """Uygulama genelindeki eylemleri (QAction) oluşturur."""
        self.eylem_yeni_not = QAction("Yeni Not", self)
        self.eylem_kaydet = QAction("Kaydet", self)
        self.eylem_sil = QAction("Sil", self)
        self.eylem_cikis = QAction("Çıkış", self)

        self.eylem_kaydet.setEnabled(False)
        self.eylem_sil.setEnabled(False)

    def _menu_ve_arac_cubugunu_olustur(self):
        """Ana menüyü ve araç çubuğunu oluşturur."""
        menu_cubugu = self.menuBar()

        # Dosya Menüsü
        dosya_menusu = menu_cubugu.addMenu("&Dosya")
        dosya_menusu.addAction(self.eylem_yeni_not)
        dosya_menusu.addAction(self.eylem_kaydet)
        dosya_menusu.addAction(self.eylem_sil)
        dosya_menusu.addSeparator()
        dosya_menusu.addAction(self.eylem_cikis)

        # Görünüm Menüsü
        gorunum_menusu = menu_cubugu.addMenu("&Görünüm")
        tema_menusu = gorunum_menusu.addMenu("Tema")

        self.eylem_acik_tema = QAction("Açık", self)
        self.eylem_acik_tema.setCheckable(True)
        self.eylem_acik_tema.setChecked(True)
        self.eylem_acik_tema.triggered.connect(lambda: self._temayi_ayarla("Acik"))

        self.eylem_koyu_tema = QAction("Koyu", self)
        self.eylem_koyu_tema.setCheckable(True)
        self.eylem_koyu_tema.triggered.connect(lambda: self._temayi_ayarla("Koyu"))

        tema_menusu.addAction(self.eylem_acik_tema)
        tema_menusu.addAction(self.eylem_koyu_tema)

        # Araç Çubuğu
        arac_cubugu = QToolBar("Ana Araçlar")
        self.addToolBar(arac_cubugu)
        arac_cubugu.addAction(self.eylem_yeni_not)
        arac_cubugu.addAction(self.eylem_kaydet)
        arac_cubugu.addAction(self.eylem_sil)

    def _sinyal_slot_baglantilarini_kur(self):
        """Modüler bileşenler arasındaki iletişimi kurar."""
        # Gezgin veya Not Listesi'ndeki filtreler değiştiğinde not listesini güncelle
        self.gezgin.filtreDegisti.connect(self._filtre_degisti)
        self.not_listesi.filtreDegisti.connect(self._filtre_degisti)

        # Not listesinden bir not açma isteği geldiğinde düzenleyicide aç
        self.not_listesi.notAcmaIstegi.connect(self.duzenleyici.notu_sekmede_ac)

        # Düzenleyici'nin durumu değiştiğinde Kaydet/Sil eylemlerini güncelle
        self.duzenleyici.durumDegisti.connect(self._duzenleyici_durumu_degisti)

        # Eylemleri slotlara bağla
        self.eylem_cikis.triggered.connect(self.close)
        self.eylem_yeni_not.triggered.connect(self._yeni_not_olustur)
        self.eylem_kaydet.triggered.connect(self._notu_kaydet)
        self.eylem_sil.triggered.connect(self._notu_sil)

    # --- Slot Metodları ---

    def _filtre_degisti(self):
        """Gezgin veya arama kutusundan gelen sinyale göre not listesini günceller."""
        kategori_id = self.gezgin.get_secili_kategori_id()
        etiket_idler = self.gezgin.get_secili_etiket_idler()
        self.not_listesi.notlari_guncelle(kategori_id, etiket_idler)

    def _duzenleyici_durumu_degisti(self, kaydedebilir, silebilir):
        """Düzenleyiciden gelen sinyale göre eylemlerin durumunu ayarlar."""
        self.eylem_kaydet.setEnabled(kaydedebilir)
        self.eylem_sil.setEnabled(silebilir)

    def _yeni_not_olustur(self):
        """Yeni bir not oluşturur ve düzenleyicide açar."""
        kategori_id = self.gezgin.get_secili_kategori_id()
        if kategori_id == -1: # "Tüm Notlar" seçiliyse, ilk gerçek kategoriyi al
             kategoriler = self.db.get_kategoriler()
             if kategoriler:
                 kategori_id = kategoriler[0]['ID']
             else:
                 QMessageBox.warning(self, "Hata", "Lütfen önce bir kategori oluşturun.")
                 return

        yeni_not_id = self.db.yeni_not_ekle(kategori_id)
        self._filtre_degisti() # Not listesini yenile
        self.duzenleyici.notu_sekmede_ac(yeni_not_id)

    def _notu_kaydet(self):
        """Düzenleyicideki notu kaydeder ve listeyi yeniler."""
        if self.duzenleyici.mevcut_notu_kaydet():
            self._filtre_degisti()

    def _notu_sil(self):
        """Düzenleyicideki mevcut notu siler ve listeyi yeniler."""
        if self.duzenleyici.mevcut_notu_sil():
            self._filtre_degisti()

    def _temayi_ayarla(self, tema_adi):
        """Uygulama temasını ayarlar."""
        if tema_adi == "Koyu":
            self.eylem_acik_tema.setChecked(False)
            self.eylem_koyu_tema.setChecked(True)
            try:
                with open("ui/dark_theme.qss", "r") as f:
                    self.setStyleSheet(f.read())
            except FileNotFoundError:
                print("Koyu tema dosyası (dark_theme.qss) bulunamadı.")
        else: # Açık tema
            self.eylem_koyu_tema.setChecked(False)
            self.eylem_acik_tema.setChecked(True)
            self.setStyleSheet("") # Varsayılan stile dön
            QApplication.setStyle(QStyleFactory.create('Fusion'))

    def closeEvent(self, event):
        """Uygulama kapatılırken tüm sekmelerdeki kaydedilmemiş değişiklikleri kontrol eder."""
        sekme_sayisi = self.duzenleyici.sekme_kontrolu.count()
        for i in range(sekme_sayisi):
            sekme = self.duzenleyici.sekme_kontrolu.widget(i)
            if sekme and hasattr(sekme, 'degisiklik_var') and sekme.degisiklik_var:
                # _sekme_kapatma_istegi metodu kullanıcıya soracak ve gerekirse işlemi iptal edecektir.
                # Bu metodun içindeki Abort, Python'da doğrudan bir karşılığı olmadığı için,
                # metodun bir sonuç döndürmesini sağlamalıyız.
                # DuzenleyiciBileseni'ni bu senaryoyu işlemek için güncelleyelim.
                # Şimdilik, her sekmeyi kapatmayı deneyerek mantığı tetikleyebiliriz.
                pass # Bu mantığı Duzenleyici'ye taşıyalım.

        kapatilabilir = self.duzenleyici.tum_sekmeleri_kapatmayi_dene()
        if kapatilabilir:
            event.accept()
        else:
            event.ignore()
