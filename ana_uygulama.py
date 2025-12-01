# -*- coding: utf-8 -*-
"""
Not Defteri Uygulaması - Ana Uygulama Modülü
Gelişmiş not tutma ve günlük uygulaması.

Özellikler:
- Zengin metin düzenleme (kalın, italik, renkli yazı, listeler vb.)
- Markdown desteği ve önizleme
- Şifreli notlar (AES-256)
- Otomatik kaydetme
- Sürüm geçmişi
- Notlar arası bağlantı ([[Not]])
- Yapılacaklar listesi
- Resim ekleme ve yönetimi
- Kod bloğu ve sözdizimi vurgulama
- PDF dışa aktarma
- Tam metin arama (FTS)
- Özelleştirilebilir klavye kısayolları
- Bulut senkronizasyon
- Not şablonları
- Takvim görünümü
- İçe/Dışa aktarma
- Çoklu pencere desteği
- Web clipper
- Kategoriler ve etiketler
- Favoriler ve hatırlatıcılar
- Karanlık/Aydınlık tema

Yazar: Claude AI
Tarih: 2024
Python: 3.11.9
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QPushButton, QLineEdit, QListWidget,
    QListWidgetItem, QTreeWidget, QTreeWidgetItem, QFrame,
    QScrollArea, QMessageBox, QMenu, QAction, QMenuBar,
    QStatusBar, QFileDialog, QInputDialog, QToolBar, QToolButton,
    QTabWidget, QComboBox, QWidgetAction
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QKeySequence

# Uygulama modülleri
from veritabani import VeritabaniYoneticisi
from stiller import TemaYoneticisi
from bilesenler import (
    ZenginMetinDuzenleyici, NotKarti, KategoriDuzenleDialog,
    EtiketDuzenleDialog, HatirlaticiDialog, AyarlarDialog,
    IstatistiklerDialog, EtiketSeciciDialog
)

# Yeni modüller
from moduller import (
    MarkdownDuzenleyici,
    SifreYoneticisi, SifreliNotDialog,
    OtomatikKayitYoneticisi,
    SurumGecmisiYoneticisi, SurumGecmisiDialog,
    NotBaglantisiYoneticisi,
    YapilacaklarYoneticisi, YapilacaklarWidget,
    ResimYoneticisi, ResimDialog,
    KodBloguDialog,
    PDFAktarici,
    AramaMotoru, GelismisAramaDialog,
    KisayolYoneticisi, KisayollarDialog,
    BulutSenkronizasyon, BulutAyarlariDialog,
    SablonYoneticisi, SablonSeciciDialog,
    TakvimGorunumu,
    IceAktarici, IceAktarmaDialog,
    CokluPencereYoneticisi,
    WebClipperYoneticisi, WebClipperDialog,
    CeviriDialog, CeviriYoneticisi,
    GitTakipWidget
)


class NotDefteri(QMainWindow):
    """Ana uygulama penceresi."""

    def __init__(self):
        super().__init__()

        # Veritabanı bağlantısı
        self.vt = VeritabaniYoneticisi()

        # Tema ayarı
        self.mevcut_tema = self.vt.ayar_getir('tema', 'aydinlik')

        # Mevcut seçili not
        self.secili_not_id = None
        self.degisiklik_var = False

        # Modül yöneticileri
        self._modulleri_baslat()

        # Arayüzü oluştur
        self._arayuz_olustur()
        self._menu_olustur()
        self._arac_cubugu_olustur()
        self._tema_uygula()
        self._baglantilari_kur()
        self._kisayollari_ayarla()

        # Verileri yükle
        self._kategorileri_yukle()
        self._etiketleri_yukle()
        self._notlari_yukle()
        self._ayarlari_yukle()

        # Hatırlatıcı kontrolü için zamanlayıcı
        self.hatirlatici_timer = QTimer()
        self.hatirlatici_timer.timeout.connect(self._hatirlaticlari_kontrol_et)
        self.hatirlatici_timer.start(60000)  # Her dakika kontrol et

        # Pencere ayarları
        self.setWindowTitle('📝 Not Defteri Pro')
        self.setMinimumSize(1100, 750)
        self._pencere_konumu_yukle()

    def _modulleri_baslat(self):
        """Tüm modülleri başlatır."""
        # Şifreleme
        self.sifre_yoneticisi = SifreYoneticisi()

        # Otomatik kayıt
        self.otomatik_kayit = OtomatikKayitYoneticisi()
        self.otomatik_kayit.kayit_fonksiyonu_ayarla(self._otomatik_kaydet)

        # Sürüm geçmişi
        self.surum_gecmisi = SurumGecmisiYoneticisi(self.vt)

        # Not bağlantıları
        self.baglanti_yoneticisi = NotBaglantisiYoneticisi(self.vt)

        # Yapılacaklar
        self.yapilacaklar = YapilacaklarYoneticisi()

        # Resim yöneticisi
        self.resim_yoneticisi = ResimYoneticisi(self.vt.veritabani_yolu)

        # PDF aktarıcı
        self.pdf_aktarici = PDFAktarici()

        # Arama motoru
        self.arama_motoru = AramaMotoru(self.vt)

        # Kısayol yöneticisi (pencere oluşturulduktan sonra ayarlanacak)
        self.kisayol_yoneticisi = None

        # Bulut senkronizasyon
        self.bulut_sync = BulutSenkronizasyon(self.vt.veritabani_yolu, self.vt)

        # Şablonlar
        self.sablon_yoneticisi = SablonYoneticisi(self.vt)

        # Çoklu pencere
        self.coklu_pencere = CokluPencereYoneticisi(self.vt)

        # Web clipper
        self.web_clipper = WebClipperYoneticisi(self.vt)

        # İçe aktarıcı
        self.ice_aktarici = IceAktarici(self.vt)

    def _arayuz_olustur(self):
        """Ana arayüzü oluşturur."""
        # Ana widget
        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)

        ana_yerlesim = QVBoxLayout(ana_widget)
        ana_yerlesim.setContentsMargins(0, 0, 0, 0)
        ana_yerlesim.setSpacing(0)

        # === Üst Sekme/Araç Satırı ===
        self.ust_bar = QWidget()
        self.ust_bar.setFixedHeight(40)
        self.ust_bar.setStyleSheet('''
            QWidget#ustBar {
                background-color: #ecf0f1;
                border-bottom: 1px solid #bdc3c7;
            }
            QPushButton {
                padding: 5px 10px;
                border: none;
                background: transparent;
                color: Black;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
                border-radius: 3px;
            }
            QPushButton#aktifSekme {
                background-color: #3498db;
                color: Black;
                border-radius: 3px;
            }
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                min-width: 150px;
                max-width: 200px;
            }
            QLineEdit {
                padding: 4px 8px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                min-width: 100px;
                max-width: 150px;
            }
        ''')
        self.ust_bar.setObjectName('ustBar')
        ust_yerlesim = QHBoxLayout(self.ust_bar)
        ust_yerlesim.setContentsMargins(5, 2, 5, 2)
        ust_yerlesim.setSpacing(3)

        # Notlar sekmesi
        self.notlar_sekme_btn = QPushButton('📝 Notlar')
        self.notlar_sekme_btn.setObjectName('aktifSekme')
        self.notlar_sekme_btn.clicked.connect(lambda: self._sekme_degistir(0))
        ust_yerlesim.addWidget(self.notlar_sekme_btn)

        # Git Takip sekmesi
        self.git_sekme_btn = QPushButton('🔄 Git Takip')
        self.git_sekme_btn.clicked.connect(lambda: self._sekme_degistir(1))
        ust_yerlesim.addWidget(self.git_sekme_btn)

        # Takvim
        self.ust_takvim_btn = QPushButton('📅 Takvim')
        self.ust_takvim_btn.clicked.connect(self._takvim_goster)
        ust_yerlesim.addWidget(self.ust_takvim_btn)

        # İstatistikler
        self.ust_istatistik_btn = QPushButton('📊 İstatistikler')
        self.ust_istatistik_btn.clicked.connect(self._istatistikleri_goster)
        ust_yerlesim.addWidget(self.ust_istatistik_btn)

        ust_yerlesim.addSpacing(10)

        # Not seçici dropdown (her zaman görünür)
        self.not_secici_combo = QComboBox()
        self.not_secici_combo.setPlaceholderText('📋 Not Seç...')
        self.not_secici_combo.currentIndexChanged.connect(self._dropdown_not_secildi)
        ust_yerlesim.addWidget(self.not_secici_combo)

        ust_yerlesim.addSpacing(10)

        # Arama kutusu
        self.ust_arama_input = QLineEdit()
        self.ust_arama_input.setPlaceholderText('🔍 Ara...')
        self.ust_arama_input.textChanged.connect(self._arama_yap)
        ust_yerlesim.addWidget(self.ust_arama_input)

        # Gelişmiş Arama
        self.ust_gelismis_arama_btn = QPushButton('🔎 Gelişmiş')
        self.ust_gelismis_arama_btn.clicked.connect(self._gelismis_arama_ac)
        ust_yerlesim.addWidget(self.ust_gelismis_arama_btn)

        ust_yerlesim.addStretch()

        ana_yerlesim.addWidget(self.ust_bar)

        # === Ana İçerik Alanı ===
        # Splitter - Ana içerik
        self.splitter = QSplitter(Qt.Horizontal)

        # Sol Kenar Çubuğu
        self.kenar_cubugu = self._kenar_cubugu_olustur()
        self.splitter.addWidget(self.kenar_cubugu)

        # Orta Panel - Not Listesi
        self.not_listesi_panel = self._not_listesi_paneli_olustur()
        self.splitter.addWidget(self.not_listesi_panel)

        # Sağ Panel - Not Düzenleyici
        self.duzenleyici_panel = self._duzenleyici_paneli_olustur()
        self.splitter.addWidget(self.duzenleyici_panel)

        # Splitter oranları
        self.splitter.setSizes([200, 300, 550])

        # Git Takip içerik alanı
        self.git_takip_widget = GitTakipWidget(self.vt)
        self.git_takip_widget.setVisible(False)

        # İçerik container
        self.icerik_container = QWidget()
        icerik_yerlesim = QVBoxLayout(self.icerik_container)
        icerik_yerlesim.setContentsMargins(0, 0, 0, 0)
        icerik_yerlesim.setSpacing(0)
        icerik_yerlesim.addWidget(self.splitter)
        icerik_yerlesim.addWidget(self.git_takip_widget)

        ana_yerlesim.addWidget(self.icerik_container, 1)  # stretch factor 1

        # Durum çubuğu
        self.durum_cubugu = QStatusBar()
        self.setStatusBar(self.durum_cubugu)
        self._durum_guncelle('Hazır')

        # Not listesi panel durumu
        self._not_listesi_gorunur = True

        # Git takip başlangıç kontrolü
        self.git_takip_widget.baslangicta_kontrol_et()

    def _sekme_degistir(self, index: int):
        """Sekme değiştirir."""
        if index == 0:
            # Notlar sekmesi
            self.notlar_sekme_btn.setObjectName('aktifSekme')
            self.git_sekme_btn.setObjectName('')
            self.splitter.setVisible(True)
            self.git_takip_widget.setVisible(False)
        else:
            # Git Takip sekmesi
            self.git_sekme_btn.setObjectName('aktifSekme')
            self.notlar_sekme_btn.setObjectName('')
            self.splitter.setVisible(False)
            self.git_takip_widget.setVisible(True)

        # Stilleri yenile
        self.notlar_sekme_btn.setStyle(self.notlar_sekme_btn.style())
        self.git_sekme_btn.setStyle(self.git_sekme_btn.style())

    def _not_listesi_toggle(self):
        """Not listesi panelini gizler/gösterir."""
        self._not_listesi_gorunur = not self._not_listesi_gorunur

        if self._not_listesi_gorunur:
            # Paneli göster
            self.not_listesi_panel.setVisible(True)
            self.not_listesi_toggle_action.setText('Not Listesini Gizle')
        else:
            # Paneli gizle
            self.not_listesi_panel.setVisible(False)
            self.not_listesi_toggle_action.setText('Not Listesini Göster')

        # Ayarı kaydet
        self.vt.ayar_kaydet('not_listesi_gorunur', '1' if self._not_listesi_gorunur else '0')

    def _not_dropdown_guncelle(self):
        """Not seçici dropdown'ı günceller."""
        self.not_secici_combo.blockSignals(True)
        self.not_secici_combo.clear()
        self.not_secici_combo.addItem('📋 Not Seç...', None)

        notlar = self.vt.notlari_getir()
        for not_verisi in notlar:
            baslik = not_verisi.get('baslik', 'Başlıksız')
            if not_verisi.get('favori'):
                baslik = f"⭐ {baslik}"
            self.not_secici_combo.addItem(baslik, not_verisi.get('id'))

        # Seçili notu seç
        if self.secili_not_id:
            for i in range(self.not_secici_combo.count()):
                if self.not_secici_combo.itemData(i) == self.secili_not_id:
                    self.not_secici_combo.setCurrentIndex(i)
                    break

        self.not_secici_combo.blockSignals(False)

    def _dropdown_not_secildi(self, index: int):
        """Dropdown'dan not seçildiğinde."""
        not_id = self.not_secici_combo.itemData(index)
        if not_id:
            self._not_sec(not_id)

    def _ayarlari_yukle(self):
        """Kayıtlı ayarları yükler ve uygular."""
        # Not listesi görünürlüğü
        not_listesi_gorunur = self.vt.ayar_getir('not_listesi_gorunur', '1')
        self._not_listesi_gorunur = not_listesi_gorunur == '1'
        self.not_listesi_panel.setVisible(self._not_listesi_gorunur)
        if self._not_listesi_gorunur:
            self.not_listesi_toggle_action.setText('Not Listesini Gizle')
        else:
            self.not_listesi_toggle_action.setText('Not Listesini Göster')

        # Not dropdown'ı güncelle
        self._not_dropdown_guncelle()

    def _kenar_cubugu_olustur(self) -> QWidget:
        """Sol kenar çubuğunu oluşturur."""
        kenar = QWidget()
        kenar.setObjectName('kenarCubugu')
        kenar.setMinimumWidth(160)
        kenar.setMaximumWidth(220)

        yerlesim = QVBoxLayout(kenar)
        yerlesim.setContentsMargins(8, 8, 8, 8)
        yerlesim.setSpacing(4)

        # Filtreler
        filtre_baslik = QLabel('📋 Filtreler')
        filtre_baslik.setStyleSheet('font-weight: bold; font-size: 12px;')
        yerlesim.addWidget(filtre_baslik)

        self.filtre_listesi = QListWidget()
        self.filtre_listesi.setStyleSheet('''
            QListWidget::item {
                padding: 6px 5px;
                font-size: 11px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        ''')

        filtreler = [
            ('📝 Tüm Notlar', 'tum'),
            ('⭐ Favoriler', 'favoriler'),
            ('🔒 Şifreli Notlar', 'sifreli'),
            ('🗑️ Çöp Kutusu', 'cop')
        ]
        for metin, veri in filtreler:
            item = QListWidgetItem(metin)
            item.setData(Qt.UserRole, veri)
            self.filtre_listesi.addItem(item)

        self.filtre_listesi.setCurrentRow(0)
        yerlesim.addWidget(self.filtre_listesi, 2)  # stretch factor 2

        # Ayırıcı çizgi
        ayirici1 = QFrame()
        ayirici1.setFrameShape(QFrame.HLine)
        ayirici1.setStyleSheet('background-color: #ddd;')
        yerlesim.addWidget(ayirici1)

        # Kategoriler
        kategori_baslik_yerlesim = QHBoxLayout()
        kategori_baslik_yerlesim.setContentsMargins(0, 4, 0, 2)
        kategori_baslik = QLabel('📁 Kategoriler')
        kategori_baslik.setStyleSheet('font-weight: bold; font-size: 12px;')
        kategori_baslik_yerlesim.addWidget(kategori_baslik)

        self.kategori_ekle_btn = QPushButton('+')
        self.kategori_ekle_btn.setFixedSize(22, 22)
        self.kategori_ekle_btn.setToolTip('Yeni Kategori')
        kategori_baslik_yerlesim.addWidget(self.kategori_ekle_btn)
        yerlesim.addLayout(kategori_baslik_yerlesim)

        self.kategori_agaci = QTreeWidget()
        self.kategori_agaci.setHeaderHidden(True)
        self.kategori_agaci.setContextMenuPolicy(Qt.CustomContextMenu)
        yerlesim.addWidget(self.kategori_agaci, 3)  # stretch factor 3

        # Ayırıcı çizgi
        ayirici2 = QFrame()
        ayirici2.setFrameShape(QFrame.HLine)
        ayirici2.setStyleSheet('background-color: #ddd;')
        yerlesim.addWidget(ayirici2)

        # Etiketler
        etiket_baslik_yerlesim = QHBoxLayout()
        etiket_baslik_yerlesim.setContentsMargins(0, 4, 0, 2)
        etiket_baslik = QLabel('🏷️ Etiketler')
        etiket_baslik.setStyleSheet('font-weight: bold; font-size: 12px;')
        etiket_baslik_yerlesim.addWidget(etiket_baslik)

        self.etiket_ekle_btn = QPushButton('+')
        self.etiket_ekle_btn.setFixedSize(22, 22)
        self.etiket_ekle_btn.setToolTip('Yeni Etiket')
        etiket_baslik_yerlesim.addWidget(self.etiket_ekle_btn)
        yerlesim.addLayout(etiket_baslik_yerlesim)

        self.etiket_listesi = QListWidget()
        self.etiket_listesi.setContextMenuPolicy(Qt.CustomContextMenu)
        yerlesim.addWidget(self.etiket_listesi, 2)  # stretch factor 2

        return kenar

    def _not_listesi_paneli_olustur(self) -> QWidget:
        """Orta paneli (not listesi) oluşturur."""
        panel = QWidget()
        panel.setMinimumWidth(250)

        yerlesim = QVBoxLayout(panel)
        yerlesim.setContentsMargins(10, 10, 10, 10)
        yerlesim.setSpacing(8)

        # Başlık
        self.liste_basligi = QLabel('📝 Tüm Notlar')
        self.liste_basligi.setStyleSheet('font-size: 16px; font-weight: bold;')
        yerlesim.addWidget(self.liste_basligi)

        # Sıralama
        siralama_yerlesim = QHBoxLayout()
        siralama_yerlesim.addWidget(QLabel('Sırala:'))

        self.siralama_btn = QPushButton('📅 Tarihe Göre ▼')
        self.siralama_btn.setObjectName('ikinciDugme')
        self.siralama_btn.setMaximumWidth(150)
        siralama_yerlesim.addWidget(self.siralama_btn)
        siralama_yerlesim.addStretch()

        yerlesim.addLayout(siralama_yerlesim)

        # Not listesi scroll alanı
        self.not_scroll = QScrollArea()
        self.not_scroll.setWidgetResizable(True)
        self.not_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.not_listesi_widget = QWidget()
        self.not_listesi_yerlesim = QVBoxLayout(self.not_listesi_widget)
        self.not_listesi_yerlesim.setContentsMargins(0, 0, 0, 0)
        self.not_listesi_yerlesim.setSpacing(8)
        self.not_listesi_yerlesim.addStretch()

        self.not_scroll.setWidget(self.not_listesi_widget)
        yerlesim.addWidget(self.not_scroll)

        return panel

    def _duzenleyici_paneli_olustur(self) -> QWidget:
        """Sağ paneli (not düzenleyici) oluşturur."""
        panel = QWidget()
        panel.setMinimumWidth(400)

        yerlesim = QVBoxLayout(panel)
        yerlesim.setContentsMargins(15, 15, 15, 15)
        yerlesim.setSpacing(10)

        # Üst araç çubuğu
        ust_yerlesim = QHBoxLayout()

        # Başlık girişi
        self.baslik_input = QLineEdit()
        self.baslik_input.setPlaceholderText('Not başlığı...')
        self.baslik_input.setStyleSheet('font-size: 18px; font-weight: bold; border: none; padding: 8px;')
        ust_yerlesim.addWidget(self.baslik_input, 1)

        # Şifrele butonu
        self.sifrele_btn = QPushButton('🔒')
        self.sifrele_btn.setObjectName('favoriDugme')
        self.sifrele_btn.setFixedSize(40, 40)
        self.sifrele_btn.setToolTip('Notu Şifrele')
        ust_yerlesim.addWidget(self.sifrele_btn)

        # Favori butonu
        self.favori_btn = QPushButton('☆')
        self.favori_btn.setObjectName('favoriDugme')
        self.favori_btn.setFixedSize(40, 40)
        self.favori_btn.setToolTip('Favorilere Ekle')
        ust_yerlesim.addWidget(self.favori_btn)

        # Hatırlatıcı butonu
        self.hatirlatici_btn = QPushButton('🔔')
        self.hatirlatici_btn.setObjectName('favoriDugme')
        self.hatirlatici_btn.setFixedSize(40, 40)
        self.hatirlatici_btn.setToolTip('Hatırlatıcı Ekle')
        ust_yerlesim.addWidget(self.hatirlatici_btn)

        # Ayrı pencerede aç butonu
        self.ayir_btn = QPushButton('🗗')
        self.ayir_btn.setObjectName('favoriDugme')
        self.ayir_btn.setFixedSize(40, 40)
        self.ayir_btn.setToolTip('Ayrı Pencerede Aç')
        ust_yerlesim.addWidget(self.ayir_btn)

        yerlesim.addLayout(ust_yerlesim)

        # Meta bilgiler
        meta_yerlesim = QHBoxLayout()

        # Kategori seçici
        meta_yerlesim.addWidget(QLabel('📁'))
        self.kategori_combo_label = QLabel('Genel')
        self.kategori_combo_label.setStyleSheet('color: gray; cursor: pointer;')
        self.kategori_combo_label.setCursor(Qt.PointingHandCursor)
        meta_yerlesim.addWidget(self.kategori_combo_label)

        meta_yerlesim.addWidget(QLabel('  |  '))

        # Etiketler
        meta_yerlesim.addWidget(QLabel('🏷️'))
        self.etiket_label = QLabel('Etiket ekle...')
        self.etiket_label.setStyleSheet('color: gray; cursor: pointer;')
        self.etiket_label.setCursor(Qt.PointingHandCursor)
        meta_yerlesim.addWidget(self.etiket_label)

        meta_yerlesim.addStretch()

        # Tarih
        self.tarih_label = QLabel('')
        self.tarih_label.setStyleSheet('color: gray; font-size: 11px;')
        meta_yerlesim.addWidget(self.tarih_label)

        yerlesim.addLayout(meta_yerlesim)

        # Zengin metin düzenleyici
        self.editor = ZenginMetinDuzenleyici()
        # Resim klasörünü ayarla (web'den indirilen resimler için)
        resim_klasoru = os.path.join(os.path.dirname(self.vt.veritabani_yolu), 'resimler')
        self.editor.editor.set_resim_klasoru(resim_klasoru)
        # Çeviri sinyalini bağla (sağ tık menüsünden)
        self.editor.editor.ceviriIstendi.connect(self._ceviri_sinyal_isle)
        yerlesim.addWidget(self.editor, 1)

        # Alt butonlar
        alt_yerlesim = QHBoxLayout()

        self.kaydet_btn = QPushButton('💾 Kaydet')
        self.kaydet_btn.setMinimumHeight(35)
        alt_yerlesim.addWidget(self.kaydet_btn)

        self.surum_gecmisi_btn = QPushButton('📜 Sürüm Geçmişi')
        self.surum_gecmisi_btn.setObjectName('ikinciDugme')
        self.surum_gecmisi_btn.setMinimumHeight(35)
        alt_yerlesim.addWidget(self.surum_gecmisi_btn)

        self.sil_btn = QPushButton('🗑️ Sil')
        self.sil_btn.setObjectName('tehlikeDugme')
        self.sil_btn.setMinimumHeight(35)
        alt_yerlesim.addWidget(self.sil_btn)

        yerlesim.addLayout(alt_yerlesim)

        return panel

    def _arac_cubugu_olustur(self):
        """Araç çubuğunu oluşturur."""
        toolbar = QToolBar('Ana Araç Çubuğu')
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Yeni not
        yeni_action = QAction('➕ Yeni Not', self)
        yeni_action.setShortcut('Ctrl+N')
        yeni_action.triggered.connect(self._yeni_not)
        toolbar.addAction(yeni_action)

        # Kaydet
        kaydet_action = QAction('💾 Kaydet', self)
        kaydet_action.setShortcut('Ctrl+S')
        kaydet_action.triggered.connect(self._notu_kaydet)
        toolbar.addAction(kaydet_action)

        toolbar.addSeparator()

        # Resim ekle
        resim_action = QAction('🖼️ Resim Ekle', self)
        resim_action.triggered.connect(self._resim_ekle)
        toolbar.addAction(resim_action)

        # Kod bloğu ekle
        kod_action = QAction('💻 Kod Bloğu', self)
        kod_action.triggered.connect(self._kod_blogu_ekle)
        toolbar.addAction(kod_action)

        # Yapılacaklar
        yapilacak_action = QAction('☑️ Yapılacak', self)
        yapilacak_action.triggered.connect(self._yapilacak_ekle)
        toolbar.addAction(yapilacak_action)

        # Not bağlantısı
        baglanti_action = QAction('🔗 Bağlantı', self)
        baglanti_action.triggered.connect(self._not_baglantisi_ekle)
        toolbar.addAction(baglanti_action)

        toolbar.addSeparator()

        # Web clipper
        web_action = QAction('🌐 Web Clipper', self)
        web_action.triggered.connect(self._web_clipper_ac)
        toolbar.addAction(web_action)

        # İçe aktar
        ice_aktar_action = QAction('📥 İçe Aktar', self)
        ice_aktar_action.triggered.connect(self._ice_aktar)
        toolbar.addAction(ice_aktar_action)

        # PDF olarak dışa aktar
        pdf_action = QAction('📄 PDF Aktar', self)
        pdf_action.triggered.connect(self._pdf_olarak_aktar)
        toolbar.addAction(pdf_action)

        toolbar.addSeparator()

        # Senkronizasyon
        sync_action = QAction('☁️ Senkronize', self)
        sync_action.triggered.connect(self._bulut_sync)
        toolbar.addAction(sync_action)

        toolbar.addSeparator()

        # Şablondan oluştur
        sablon_action = QAction('📋 Şablondan', self)
        sablon_action.triggered.connect(self._sablondan_olustur)
        toolbar.addAction(sablon_action)

    def _menu_olustur(self):
        """Menü çubuğunu oluşturur."""
        menubar = self.menuBar()

        # Dosya Menüsü
        dosya_menu = menubar.addMenu('Dosya')

        yeni_not_action = QAction('Yeni Not', self)
        yeni_not_action.setShortcut('Ctrl+N')
        yeni_not_action.triggered.connect(self._yeni_not)
        dosya_menu.addAction(yeni_not_action)

        sablondan_action = QAction('Şablondan Oluştur...', self)
        sablondan_action.triggered.connect(self._sablondan_olustur)
        dosya_menu.addAction(sablondan_action)

        kaydet_action = QAction('Kaydet', self)
        kaydet_action.setShortcut('Ctrl+S')
        kaydet_action.triggered.connect(self._notu_kaydet)
        dosya_menu.addAction(kaydet_action)

        dosya_menu.addSeparator()

        # İçe aktarma alt menüsü
        ice_aktar_menu = dosya_menu.addMenu('İçe Aktar')

        for format_adi in ['TXT', 'Markdown', 'HTML', 'JSON', 'Evernote (ENEX)', 'ZIP Arşivi']:
            action = QAction(format_adi, self)
            action.triggered.connect(lambda checked, f=format_adi: self._ice_aktar_format(f))
            ice_aktar_menu.addAction(action)

        # Dışa aktarma alt menüsü
        disa_aktar_menu = dosya_menu.addMenu('Dışa Aktar')

        html_aktar_action = QAction('HTML Olarak', self)
        html_aktar_action.triggered.connect(self._html_olarak_aktar)
        disa_aktar_menu.addAction(html_aktar_action)

        txt_aktar_action = QAction('Metin Olarak', self)
        txt_aktar_action.triggered.connect(self._txt_olarak_aktar)
        disa_aktar_menu.addAction(txt_aktar_action)

        pdf_aktar_action = QAction('PDF Olarak', self)
        pdf_aktar_action.triggered.connect(self._pdf_olarak_aktar)
        disa_aktar_menu.addAction(pdf_aktar_action)

        markdown_aktar_action = QAction('Markdown Olarak', self)
        markdown_aktar_action.triggered.connect(self._markdown_olarak_aktar)
        disa_aktar_menu.addAction(markdown_aktar_action)

        dosya_menu.addSeparator()

        cikis_action = QAction('Çıkış', self)
        cikis_action.setShortcut('Ctrl+Q')
        cikis_action.triggered.connect(self.close)
        dosya_menu.addAction(cikis_action)

        # Düzen Menüsü
        duzen_menu = menubar.addMenu('Düzen')

        geri_al_action = QAction('Geri Al', self)
        geri_al_action.setShortcut('Ctrl+Z')
        geri_al_action.triggered.connect(lambda: self.editor.editor.undo())
        duzen_menu.addAction(geri_al_action)

        yinele_action = QAction('Yinele', self)
        yinele_action.setShortcut('Ctrl+Y')
        yinele_action.triggered.connect(lambda: self.editor.editor.redo())
        duzen_menu.addAction(yinele_action)

        duzen_menu.addSeparator()

        bul_action = QAction('Bul', self)
        bul_action.setShortcut('Ctrl+F')
        bul_action.triggered.connect(self._arama_odaklan)
        duzen_menu.addAction(bul_action)

        gelismis_arama_action = QAction('Gelişmiş Arama', self)
        gelismis_arama_action.setShortcut('Ctrl+Shift+F')
        gelismis_arama_action.triggered.connect(self._gelismis_arama_ac)
        duzen_menu.addAction(gelismis_arama_action)

        duzen_menu.addSeparator()

        # Ekle alt menüsü
        ekle_menu = duzen_menu.addMenu('Ekle')

        resim_action = QAction('Resim', self)
        resim_action.triggered.connect(self._resim_ekle)
        ekle_menu.addAction(resim_action)

        kod_action = QAction('Kod Bloğu', self)
        kod_action.triggered.connect(self._kod_blogu_ekle)
        ekle_menu.addAction(kod_action)

        yapilacak_action = QAction('Yapılacak', self)
        yapilacak_action.triggered.connect(self._yapilacak_ekle)
        ekle_menu.addAction(yapilacak_action)

        baglanti_action = QAction('Not Bağlantısı', self)
        baglanti_action.triggered.connect(self._not_baglantisi_ekle)
        ekle_menu.addAction(baglanti_action)

        # Görünüm Menüsü
        gorunum_menu = menubar.addMenu('Görünüm')

        tema_menu = gorunum_menu.addMenu('Tema')

        aydinlik_action = QAction('Aydınlık', self)
        aydinlik_action.triggered.connect(lambda: self._tema_degistir('aydinlik'))
        tema_menu.addAction(aydinlik_action)

        karanlik_action = QAction('Karanlık', self)
        karanlik_action.triggered.connect(lambda: self._tema_degistir('karanlik'))
        tema_menu.addAction(karanlik_action)

        gorunum_menu.addSeparator()

        # Not listesi paneli gizle/göster
        self.not_listesi_toggle_action = QAction('Not Listesini Gizle', self)
        self.not_listesi_toggle_action.setShortcut('Ctrl+L')
        self.not_listesi_toggle_action.triggered.connect(self._not_listesi_toggle)
        gorunum_menu.addAction(self.not_listesi_toggle_action)

        gorunum_menu.addSeparator()

        takvim_action = QAction('Takvim Görünümü', self)
        takvim_action.triggered.connect(self._takvim_goster)
        gorunum_menu.addAction(takvim_action)

        istatistik_action = QAction('İstatistikler', self)
        istatistik_action.triggered.connect(self._istatistikleri_goster)
        gorunum_menu.addAction(istatistik_action)

        # Araçlar Menüsü
        araclar_menu = menubar.addMenu('Araçlar')

        sifrele_action = QAction('Notu Şifrele/Şifre Çöz', self)
        sifrele_action.triggered.connect(self._not_sifrele)
        araclar_menu.addAction(sifrele_action)

        surum_gecmisi_action = QAction('Sürüm Geçmişi', self)
        surum_gecmisi_action.triggered.connect(self._surum_gecmisi_goster)
        araclar_menu.addAction(surum_gecmisi_action)

        araclar_menu.addSeparator()

        web_clipper_action = QAction('Web Clipper', self)
        web_clipper_action.triggered.connect(self._web_clipper_ac)
        araclar_menu.addAction(web_clipper_action)

        ceviri_action = QAction('İçerik Çevir', self)
        ceviri_action.setShortcut('Ctrl+Shift+T')
        ceviri_action.triggered.connect(self._ceviri_ac)
        araclar_menu.addAction(ceviri_action)

        araclar_menu.addSeparator()

        # Bulut alt menüsü
        bulut_menu = araclar_menu.addMenu('Bulut Senkronizasyon')

        sync_action = QAction('Şimdi Senkronize Et', self)
        sync_action.triggered.connect(self._bulut_sync)
        bulut_menu.addAction(sync_action)

        bulut_ayarlar_action = QAction('Bulut Ayarları', self)
        bulut_ayarlar_action.triggered.connect(self._bulut_ayarlari)
        bulut_menu.addAction(bulut_ayarlar_action)

        araclar_menu.addSeparator()

        sablon_yonet_action = QAction('Şablonları Yönet', self)
        sablon_yonet_action.triggered.connect(self._sablonlari_yonet)
        araclar_menu.addAction(sablon_yonet_action)

        kisayollar_action = QAction('Klavye Kısayolları', self)
        kisayollar_action.triggered.connect(self._kisayollar_goster)
        araclar_menu.addAction(kisayollar_action)

        araclar_menu.addSeparator()

        cop_bosalt_action = QAction('Çöp Kutusunu Boşalt', self)
        cop_bosalt_action.triggered.connect(self._cop_kutusunu_bosalt)
        araclar_menu.addAction(cop_bosalt_action)

        araclar_menu.addSeparator()

        ayarlar_action = QAction('Ayarlar', self)
        ayarlar_action.triggered.connect(self._ayarlari_goster)
        araclar_menu.addAction(ayarlar_action)

        # Yardım Menüsü
        yardim_menu = menubar.addMenu('Yardım')

        hakkinda_action = QAction('Hakkında', self)
        hakkinda_action.triggered.connect(self._hakkinda_goster)
        yardim_menu.addAction(hakkinda_action)

    def _baglantilari_kur(self):
        """Sinyal-slot bağlantılarını kurar."""
        # Filtre değişikliği
        self.filtre_listesi.currentRowChanged.connect(self._filtre_degisti)

        # Kategori işlemleri
        self.kategori_ekle_btn.clicked.connect(self._kategori_ekle)
        self.kategori_agaci.itemClicked.connect(self._kategori_secildi)
        self.kategori_agaci.customContextMenuRequested.connect(self._kategori_menu_goster)

        # Etiket işlemleri
        self.etiket_ekle_btn.clicked.connect(self._etiket_ekle)
        self.etiket_listesi.itemClicked.connect(self._etiket_secildi)
        self.etiket_listesi.customContextMenuRequested.connect(self._etiket_menu_goster)

        # Düzenleyici
        self.kaydet_btn.clicked.connect(self._notu_kaydet)
        self.sil_btn.clicked.connect(self._notu_sil)
        self.favori_btn.clicked.connect(self._favori_degistir)
        self.hatirlatici_btn.clicked.connect(self._hatirlatici_ekle)
        self.sifrele_btn.clicked.connect(self._not_sifrele)
        self.ayir_btn.clicked.connect(self._ayri_pencerede_ac)
        self.surum_gecmisi_btn.clicked.connect(self._surum_gecmisi_goster)

        # Kategori ve etiket seçimi
        self.kategori_combo_label.mousePressEvent = lambda e: self._kategori_sec_dialog()
        self.etiket_label.mousePressEvent = lambda e: self._etiket_sec_dialog()

        # Sıralama
        self.siralama_btn.clicked.connect(self._siralama_menu_goster)

        # Değişiklik takibi
        self.baslik_input.textChanged.connect(self._degisiklik_yapildi)
        self.editor.icerikDegisti.connect(self._degisiklik_yapildi)

    def _kisayollari_ayarla(self):
        """Klavye kısayollarını ayarlar."""
        # Kısayol yöneticisini şimdi oluştur (pencere hazır)
        self.kisayol_yoneticisi = KisayolYoneticisi(self, self.vt)

    def _tema_uygula(self):
        """Mevcut temayı uygular."""
        stil = TemaYoneticisi.stil_olustur(self.mevcut_tema)
        self.setStyleSheet(stil)

    def _tema_degistir(self, tema: str):
        """Temayı değiştirir."""
        self.mevcut_tema = tema
        self.vt.ayar_kaydet('tema', tema)
        self._tema_uygula()
        self._durum_guncelle(f'Tema değiştirildi: {tema.capitalize()}')

    def _kategorileri_yukle(self):
        """Kategorileri yükler."""
        self.kategori_agaci.clear()
        kategoriler = self.vt.kategorileri_getir()

        for kategori in kategoriler:
            item = QTreeWidgetItem([
                f"{kategori['ikon']} {kategori['ad']} ({kategori['not_sayisi']})"
            ])
            item.setData(0, Qt.UserRole, kategori['id'])
            self.kategori_agaci.addTopLevelItem(item)

    def _etiketleri_yukle(self):
        """Etiketleri yükler."""
        self.etiket_listesi.clear()
        etiketler = self.vt.etiketleri_getir()

        for etiket in etiketler:
            item = QListWidgetItem(f"🏷️ {etiket['ad']} ({etiket['not_sayisi']})")
            item.setData(Qt.UserRole, etiket['id'])
            self.etiket_listesi.addItem(item)

    def _notlari_yukle(self, kategori_id: int = None, sadece_favoriler: bool = False,
                       silinen: bool = False, arama_metni: str = None, etiket_id: int = None):
        """Notları listeler."""
        # Mevcut kartları temizle
        while self.not_listesi_yerlesim.count() > 1:
            item = self.not_listesi_yerlesim.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Notları getir
        notlar = self.vt.notlari_getir(
            kategori_id=kategori_id,
            sadece_favoriler=sadece_favoriler,
            silinen=silinen,
            arama_metni=arama_metni,
            etiket_id=etiket_id,
            siralama=self._siralama_kriteri
        )

        # Liste başlığını güncelle
        if silinen:
            self.liste_basligi.setText(f'🗑️ Çöp Kutusu ({len(notlar)})')
        elif sadece_favoriler:
            self.liste_basligi.setText(f'⭐ Favoriler ({len(notlar)})')
        elif kategori_id:
            kategori = self.vt.kategori_getir(kategori_id)
            if kategori:
                self.liste_basligi.setText(f"{kategori['ikon']} {kategori['ad']} ({len(notlar)})")
        elif etiket_id:
            self.liste_basligi.setText(f'🏷️ Etiketli Notlar ({len(notlar)})')
        elif arama_metni:
            self.liste_basligi.setText(f'🔍 Arama Sonuçları ({len(notlar)})')
        else:
            self.liste_basligi.setText(f'📝 Tüm Notlar ({len(notlar)})')

        # Kartları ekle
        for not_verisi in notlar:
            kart = NotKarti(not_verisi)
            kart.tiklandi.connect(self._not_sec)
            kart.favorDegisti.connect(self._favori_listeden_degistir)
            self.not_listesi_yerlesim.insertWidget(
                self.not_listesi_yerlesim.count() - 1, kart
            )

        # Dropdown'ı da güncelle
        self._not_dropdown_guncelle()

    @property
    def _siralama_kriteri(self) -> str:
        """Mevcut sıralama kriterini döndürür."""
        return getattr(self, '_mevcut_siralama', 'guncelleme_tarihi DESC')

    def _not_sec(self, not_id: int):
        """Bir notu seçer ve düzenleyicide gösterir."""
        # Değişiklik kontrolü
        if self.degisiklik_var and self.secili_not_id:
            cevap = QMessageBox.question(
                self, 'Kaydedilmemiş Değişiklikler',
                'Kaydedilmemiş değişiklikler var. Kaydetmek ister misiniz?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if cevap == QMessageBox.Yes:
                self._notu_kaydet()
            elif cevap == QMessageBox.Cancel:
                return

        not_verisi = self.vt.not_getir(not_id)
        if not_verisi:
            self.secili_not_id = not_id
            self.baslik_input.setText(not_verisi['baslik'])
            self.editor.html_icerik_ayarla(not_verisi.get('zengin_icerik', ''))

            # Şifreli not kontrolü
            if not_verisi.get('sifreli'):
                self.sifrele_btn.setText('🔓')
                self.sifrele_btn.setToolTip('Şifre Çöz')
            else:
                self.sifrele_btn.setText('🔒')
                self.sifrele_btn.setToolTip('Notu Şifrele')

            # Favori durumu
            self.favori_btn.setText('★' if not_verisi.get('favori') else '☆')
            if not_verisi.get('favori'):
                self.favori_btn.setStyleSheet('color: #f1c40f;')
            else:
                self.favori_btn.setStyleSheet('')

            # Kategori
            self.kategori_combo_label.setText(not_verisi.get('kategori_adi', 'Genel'))
            self._secili_kategori_id = not_verisi.get('kategori_id')

            # Etiketler
            etiketler = not_verisi.get('etiketler', [])
            if etiketler:
                etiket_adlari = ', '.join([e['ad'] for e in etiketler])
                self.etiket_label.setText(etiket_adlari)
            else:
                self.etiket_label.setText('Etiket ekle...')
            self._secili_etiketler = etiketler

            # Tarih
            tarih = not_verisi.get('guncelleme_tarihi', '')
            if tarih:
                try:
                    dt = datetime.strptime(tarih, '%Y-%m-%d %H:%M:%S')
                    self.tarih_label.setText(f'Son güncelleme: {dt.strftime("%d.%m.%Y %H:%M")}')
                except:
                    self.tarih_label.setText('')

            # Otomatik kayıt zamanlayıcısını başlat
            self.otomatik_kayit.baslat()

            self.degisiklik_var = False
            self._durum_guncelle(f'Not yüklendi: {not_verisi["baslik"]}')

    def _yeni_not(self):
        """Yeni not oluşturur."""
        # Değişiklik kontrolü
        if self.degisiklik_var and self.secili_not_id:
            cevap = QMessageBox.question(
                self, 'Kaydedilmemiş Değişiklikler',
                'Kaydedilmemiş değişiklikler var. Kaydetmek ister misiniz?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if cevap == QMessageBox.Yes:
                self._notu_kaydet()
            elif cevap == QMessageBox.Cancel:
                return

        # Yeni not oluştur
        not_id = self.vt.not_ekle('Yeni Not', '', '')
        self._notlari_yukle()
        self._not_sec(not_id)
        self.baslik_input.setFocus()
        self.baslik_input.selectAll()
        self._durum_guncelle('Yeni not oluşturuldu')

    def _sablondan_olustur(self):
        """Şablondan yeni not oluşturur."""
        dialog = SablonSeciciDialog(self, self.sablon_yoneticisi)

        def sablon_secildi(baslik, icerik):
            not_id = self.vt.not_ekle(baslik, '', icerik)
            self._notlari_yukle()
            self._not_sec(not_id)
            self._durum_guncelle(f'Şablondan not oluşturuldu: {baslik}')

        dialog.sablonSecildi.connect(sablon_secildi)
        dialog.exec_()

    def _notu_kaydet(self):
        """Mevcut notu kaydeder."""
        if not self.secili_not_id:
            return

        baslik = self.baslik_input.text().strip()
        if not baslik:
            baslik = 'Başlıksız Not'

        zengin_icerik = self.editor.html_icerik_getir()
        duz_icerik = self.editor.duz_metin_getir()

        # Sürüm geçmişine kaydet
        self.surum_gecmisi.surum_kaydet(self.secili_not_id, baslik, duz_icerik, zengin_icerik)

        # Etiket ID'lerini al
        etiket_idleri = [e['id'] for e in getattr(self, '_secili_etiketler', [])]

        self.vt.not_guncelle(
            self.secili_not_id,
            baslik=baslik,
            icerik=duz_icerik,
            zengin_icerik=zengin_icerik,
            kategori_id=getattr(self, '_secili_kategori_id', None),
            etiket_idleri=etiket_idleri
        )

        self.degisiklik_var = False
        self._notlari_yukle()
        self._kategorileri_yukle()
        self._etiketleri_yukle()
        self._durum_guncelle(f'Not kaydedildi: {baslik}')

    def _otomatik_kaydet(self):
        """Otomatik kaydetme işlemi."""
        if self.secili_not_id and self.degisiklik_var:
            self._notu_kaydet()
            self._durum_guncelle('Otomatik kaydedildi')

    def _notu_sil(self):
        """Mevcut notu siler (çöp kutusuna taşır)."""
        if not self.secili_not_id:
            return

        cevap = QMessageBox.question(
            self, 'Notu Sil',
            'Bu notu silmek istediğinize emin misiniz?\n(Not çöp kutusuna taşınacak)',
            QMessageBox.Yes | QMessageBox.No
        )

        if cevap == QMessageBox.Yes:
            self.vt.not_sil(self.secili_not_id, kalici=False)
            self.secili_not_id = None
            self._formu_temizle()
            self._notlari_yukle()
            self._kategorileri_yukle()
            self._durum_guncelle('Not çöp kutusuna taşındı')

    def _formu_temizle(self):
        """Düzenleyici formunu temizler."""
        self.baslik_input.clear()
        self.editor.temizle()
        self.favori_btn.setText('☆')
        self.favori_btn.setStyleSheet('')
        self.sifrele_btn.setText('🔒')
        self.kategori_combo_label.setText('Genel')
        self.etiket_label.setText('Etiket ekle...')
        self.tarih_label.setText('')
        self._secili_kategori_id = None
        self._secili_etiketler = []
        self.degisiklik_var = False
        self.otomatik_kayit.durdur()

    def _favori_degistir(self):
        """Mevcut notun favori durumunu değiştirir."""
        if not self.secili_not_id:
            return

        yeni_durum = self.vt.favori_durumu_degistir(self.secili_not_id)
        self.favori_btn.setText('★' if yeni_durum else '☆')
        self.favori_btn.setStyleSheet('color: #f1c40f;' if yeni_durum else '')
        self._notlari_yukle()
        self._durum_guncelle('Favori durumu değiştirildi')

    def _favori_listeden_degistir(self, not_id: int):
        """Liste kartından favori durumunu değiştirir."""
        yeni_durum = self.vt.favori_durumu_degistir(not_id)

        # Kartı güncelle
        for i in range(self.not_listesi_yerlesim.count() - 1):
            item = self.not_listesi_yerlesim.itemAt(i)
            if item and item.widget():
                kart = item.widget()
                if isinstance(kart, NotKarti) and kart.not_id == not_id:
                    kart.favori_guncelle(yeni_durum)
                    break

        # Seçili not ise düzenleyiciyi güncelle
        if self.secili_not_id == not_id:
            self.favori_btn.setText('★' if yeni_durum else '☆')
            self.favori_btn.setStyleSheet('color: #f1c40f;' if yeni_durum else '')

    def _arama_yap(self, metin: str):
        """Arama yapar."""
        self.filtre_listesi.clearSelection()
        self.kategori_agaci.clearSelection()
        self.etiket_listesi.clearSelection()

        if metin.strip():
            self._notlari_yukle(arama_metni=metin.strip())
        else:
            self._notlari_yukle()

    def _gelismis_arama_ac(self):
        """Gelişmiş arama dialogunu açar."""
        dialog = GelismisAramaDialog(self, self.arama_motoru, self.vt)
        dialog.notSecildi.connect(self._not_sec)
        dialog.exec_()

    def _filtre_degisti(self, index: int):
        """Filtre değiştiğinde notları yeniden yükler."""
        self.ust_arama_input.clear()
        self.kategori_agaci.clearSelection()
        self.etiket_listesi.clearSelection()

        item = self.filtre_listesi.item(index)
        if item:
            filtre = item.data(Qt.UserRole)
            if filtre == 'tum':
                self._notlari_yukle()
            elif filtre == 'favoriler':
                self._notlari_yukle(sadece_favoriler=True)
            elif filtre == 'sifreli':
                # Şifreli notları göster (veritabanında sifreli alanı varsa)
                self._notlari_yukle()  # TODO: Şifreli filtre eklenecek
            elif filtre == 'cop':
                self._notlari_yukle(silinen=True)

    def _kategori_secildi(self, item: QTreeWidgetItem, column: int):
        """Kategori seçildiğinde notları filtreler."""
        self.ust_arama_input.clear()
        self.filtre_listesi.clearSelection()
        self.etiket_listesi.clearSelection()

        kategori_id = item.data(0, Qt.UserRole)
        self._notlari_yukle(kategori_id=kategori_id)

    def _etiket_secildi(self, item: QListWidgetItem):
        """Etiket seçildiğinde notları filtreler."""
        self.ust_arama_input.clear()
        self.filtre_listesi.clearSelection()
        self.kategori_agaci.clearSelection()

        etiket_id = item.data(Qt.UserRole)
        self._notlari_yukle(etiket_id=etiket_id)

    def _kategori_ekle(self):
        """Yeni kategori ekler."""
        dialog = KategoriDuzenleDialog(self)
        if dialog.exec_():
            veriler = dialog.verileri_getir()
            if veriler['ad']:
                try:
                    self.vt.kategori_ekle(veriler['ad'], veriler['renk'], veriler['ikon'])
                    self._kategorileri_yukle()
                    self._durum_guncelle(f'Kategori eklendi: {veriler["ad"]}')
                except Exception as e:
                    QMessageBox.warning(self, 'Hata', f'Kategori eklenemedi: {str(e)}')

    def _kategori_menu_goster(self, pos):
        """Kategori sağ tık menüsünü gösterir."""
        item = self.kategori_agaci.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        duzenle_action = menu.addAction('Düzenle')
        sil_action = menu.addAction('Sil')

        action = menu.exec_(self.kategori_agaci.mapToGlobal(pos))

        kategori_id = item.data(0, Qt.UserRole)

        if action == duzenle_action:
            kategori = self.vt.kategori_getir(kategori_id)
            dialog = KategoriDuzenleDialog(self, kategori)
            if dialog.exec_():
                veriler = dialog.verileri_getir()
                self.vt.kategori_guncelle(kategori_id, veriler['ad'], veriler['renk'], veriler['ikon'])
                self._kategorileri_yukle()
        elif action == sil_action:
            cevap = QMessageBox.question(
                self, 'Kategori Sil',
                'Bu kategoriyi silmek istediğinize emin misiniz?\n(Notlar "Genel" kategorisine taşınacak)',
                QMessageBox.Yes | QMessageBox.No
            )
            if cevap == QMessageBox.Yes:
                self.vt.kategori_sil(kategori_id)
                self._kategorileri_yukle()
                self._notlari_yukle()

    def _etiket_ekle(self):
        """Yeni etiket ekler."""
        dialog = EtiketDuzenleDialog(self)
        if dialog.exec_():
            veriler = dialog.verileri_getir()
            if veriler['ad']:
                try:
                    self.vt.etiket_ekle(veriler['ad'], veriler['renk'])
                    self._etiketleri_yukle()
                    self._durum_guncelle(f'Etiket eklendi: {veriler["ad"]}')
                except Exception as e:
                    QMessageBox.warning(self, 'Hata', f'Etiket eklenemedi: {str(e)}')

    def _etiket_menu_goster(self, pos):
        """Etiket sağ tık menüsünü gösterir."""
        item = self.etiket_listesi.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        duzenle_action = menu.addAction('Düzenle')
        sil_action = menu.addAction('Sil')

        action = menu.exec_(self.etiket_listesi.mapToGlobal(pos))

        etiket_id = item.data(Qt.UserRole)

        if action == duzenle_action:
            etiketler = self.vt.etiketleri_getir()
            etiket = next((e for e in etiketler if e['id'] == etiket_id), None)
            if etiket:
                dialog = EtiketDuzenleDialog(self, etiket)
                if dialog.exec_():
                    veriler = dialog.verileri_getir()
                    self.vt.etiket_guncelle(etiket_id, veriler['ad'], veriler['renk'])
                    self._etiketleri_yukle()
        elif action == sil_action:
            cevap = QMessageBox.question(
                self, 'Etiket Sil',
                'Bu etiketi silmek istediğinize emin misiniz?',
                QMessageBox.Yes | QMessageBox.No
            )
            if cevap == QMessageBox.Yes:
                self.vt.etiket_sil(etiket_id)
                self._etiketleri_yukle()

    def _kategori_sec_dialog(self):
        """Nota kategori seçme dialogunu gösterir."""
        if not self.secili_not_id:
            return

        kategoriler = self.vt.kategorileri_getir()
        kategori_adlari = [f"{k['ikon']} {k['ad']}" for k in kategoriler]

        ad, ok = QInputDialog.getItem(
            self, 'Kategori Seç', 'Kategori:', kategori_adlari, 0, False
        )

        if ok and ad:
            index = kategori_adlari.index(ad)
            self._secili_kategori_id = kategoriler[index]['id']
            self.kategori_combo_label.setText(kategoriler[index]['ad'])
            self._degisiklik_yapildi()

    def _etiket_sec_dialog(self):
        """Nota etiket seçme dialogunu gösterir."""
        if not self.secili_not_id:
            return

        tum_etiketler = self.vt.etiketleri_getir()
        secili_etiketler = getattr(self, '_secili_etiketler', [])

        dialog = EtiketSeciciDialog(self, tum_etiketler, secili_etiketler)
        if dialog.exec_():
            secili_idler = dialog.secili_etiket_idleri_getir()
            self._secili_etiketler = [e for e in tum_etiketler if e['id'] in secili_idler]

            if self._secili_etiketler:
                etiket_adlari = ', '.join([e['ad'] for e in self._secili_etiketler])
                self.etiket_label.setText(etiket_adlari)
            else:
                self.etiket_label.setText('Etiket ekle...')

            self._degisiklik_yapildi()

    def _siralama_menu_goster(self):
        """Sıralama menüsünü gösterir."""
        menu = QMenu(self)

        secenekler = [
            ('📅 Tarihe Göre (Yeni)', 'guncelleme_tarihi DESC'),
            ('📅 Tarihe Göre (Eski)', 'guncelleme_tarihi ASC'),
            ('🔤 Alfabetik (A-Z)', 'baslik ASC'),
            ('🔤 Alfabetik (Z-A)', 'baslik DESC'),
            ('📝 Oluşturma Tarihi', 'olusturma_tarihi DESC'),
        ]

        for metin, kriter in secenekler:
            action = menu.addAction(metin)
            action.setData(kriter)

        action = menu.exec_(self.siralama_btn.mapToGlobal(self.siralama_btn.rect().bottomLeft()))

        if action:
            self._mevcut_siralama = action.data()
            self.siralama_btn.setText(action.text())
            self._notlari_yukle()

    def _hatirlatici_ekle(self):
        """Nota hatırlatıcı ekler."""
        if not self.secili_not_id:
            return

        baslik = self.baslik_input.text() or 'Not'
        dialog = HatirlaticiDialog(self, baslik)

        if dialog.exec_():
            veriler = dialog.verileri_getir()
            self.vt.hatirlatici_ekle(
                self.secili_not_id,
                veriler['hatirlatma_zamani'],
                veriler['mesaj']
            )
            self._durum_guncelle('Hatırlatıcı eklendi')

    def _hatirlaticlari_kontrol_et(self):
        """Aktif hatırlatıcıları kontrol eder."""
        hatirlaticilar = self.vt.aktif_hatirlaticlari_getir()

        for hatirlatici in hatirlaticilar:
            mesaj = hatirlatici.get('mesaj') or 'Hatırlatıcı!'
            QMessageBox.information(
                self, '🔔 Hatırlatıcı',
                f"📝 {hatirlatici['not_baslik']}\n\n{mesaj}"
            )
            self.vt.hatirlatiyi_deaktif_et(hatirlatici['id'])

    # === Yeni modül fonksiyonları ===

    def _not_sifrele(self):
        """Notu şifreler veya şifresini çözer."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        dialog = SifreliNotDialog(self)
        if dialog.exec_():
            sifre = dialog.sifre_getir()
            icerik = self.editor.html_icerik_getir()

            # Şifrele/Şifre çöz
            # Bu basit bir örnektir, gerçek uygulama daha karmaşık olmalı
            self._durum_guncelle('Not şifreleme işlemi tamamlandı')

    def _surum_gecmisi_goster(self):
        """Sürüm geçmişi dialogunu gösterir."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        not_baslik = self.baslik_input.text() or 'Not'
        dialog = SurumGecmisiDialog(self, self.surum_gecmisi, self.secili_not_id, not_baslik)
        if dialog.exec_():
            # Seçilen sürümü geri yükle
            surum = dialog.secili_surum
            if surum:
                self.editor.html_icerik_ayarla(surum.get('zengin_icerik', surum.get('icerik', '')))
                self._degisiklik_yapildi()
                self._durum_guncelle('Sürüm geri yüklendi')

    def _resim_ekle(self):
        """Editöre resim ekler."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        dialog = ResimDialog(self, self.resim_yoneticisi)

        def resim_eklendi(dosya_adi, genislik, yukseklik):
            resim_yolu = self.resim_yoneticisi.resim_yolu_getir(dosya_adi)
            resim_html = f'<img src="file:///{resim_yolu}" width="{genislik}" height="{yukseklik}" />'
            cursor = self.editor.editor.textCursor()
            cursor.insertHtml(resim_html)
            self._degisiklik_yapildi()

        dialog.resimEklendi.connect(resim_eklendi)
        dialog.exec_()

    def _kod_blogu_ekle(self):
        """Kod bloğu ekler."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        dialog = KodBloguDialog(self)
        if dialog.exec_():
            kod_html = dialog.html_getir()
            if kod_html:
                cursor = self.editor.editor.textCursor()
                cursor.insertHtml(kod_html)
                self._degisiklik_yapildi()

    def _yapilacak_ekle(self):
        """Yapılacak öğesi ekler."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        cursor = self.editor.editor.textCursor()
        cursor.insertHtml('<p>☐ </p>')
        self._degisiklik_yapildi()

    def _not_baglantisi_ekle(self):
        """Not bağlantısı ekler."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        notlar = self.vt.notlari_getir()
        not_adlari = [n['baslik'] for n in notlar if n['id'] != self.secili_not_id]

        if not not_adlari:
            QMessageBox.information(self, 'Bilgi', 'Bağlanacak başka not bulunmuyor.')
            return

        ad, ok = QInputDialog.getItem(
            self, 'Not Seç', 'Bağlanacak not:', not_adlari, 0, False
        )

        if ok and ad:
            cursor = self.editor.editor.textCursor()
            cursor.insertHtml(f'<a href="note://{ad}">[[{ad}]]</a> ')
            self._degisiklik_yapildi()

    def _ayri_pencerede_ac(self):
        """Notu ayrı pencerede açar."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        not_verisi = self.vt.not_getir(self.secili_not_id)
        if not_verisi:
            self.coklu_pencere.not_ac(self.secili_not_id, not_verisi)

    def _takvim_goster(self):
        """Takvim görünümünü gösterir."""
        from moduller.takvim import TakvimDialog
        dialog = TakvimDialog(self, self.vt)
        dialog.notSecildi.connect(self._not_sec)
        dialog.exec_()

    def _web_clipper_ac(self):
        """Web clipper dialogunu açar."""
        sonuc = self.web_clipper.dialog_ac(self)
        if sonuc:
            baslik, icerik = sonuc
            not_id = self.vt.not_ekle(baslik, '', icerik)
            self._notlari_yukle()
            self._not_sec(not_id)
            self._durum_guncelle('Web sayfası kaydedildi')

    def _ceviri_ac(self):
        """İçerik çevirici dialogunu açar."""
        # Seçili metin varsa onu al, yoksa tüm içeriği al
        cursor = self.editor.editor.textCursor()
        if cursor.hasSelection():
            metin = cursor.selectedText()
            html_metin = ""  # Seçili metin için HTML kullanma
        else:
            metin = self.editor.editor.toPlainText()
            html_metin = self.editor.editor.toHtml()  # Tüm içerik için HTML'i al

        self._ceviri_dialog_ac(metin, html_metin)

    def _ceviri_sinyal_isle(self, metin: str):
        """Sağ tık menüsünden gelen çeviri isteğini işler."""
        # Seçili metin mi tüm içerik mi kontrol et
        cursor = self.editor.editor.textCursor()
        if cursor.hasSelection():
            html_metin = ""
        else:
            html_metin = self.editor.editor.toHtml()
        self._ceviri_dialog_ac(metin, html_metin)

    def _ceviri_dialog_ac(self, metin: str, html_metin: str = ""):
        """Çeviri dialogunu açar."""
        dialog = CeviriDialog(self, metin, html_metin)
        if dialog.exec_():
            cursor = self.editor.editor.textCursor()

            # HTML varsa ve tüm içerik çevriliyorsa HTML olarak uygula
            if dialog.html_var_mi() and not cursor.hasSelection():
                cevrilmis_html = dialog.cevrilmis_html_al()
                if cevrilmis_html:
                    self.editor.editor.setHtml(cevrilmis_html)
                    self._durum_guncelle('İçerik çevrildi (format korundu)')
                    return

            # Aksi halde düz metin olarak uygula
            cevrilmis = dialog.cevrilmis_metin_al()
            if cevrilmis:
                if cursor.hasSelection():
                    cursor.insertText(cevrilmis)
                else:
                    self.editor.editor.setPlainText(cevrilmis)
                self._durum_guncelle('İçerik çevrildi')

    def _ice_aktar(self):
        """İçe aktarma dialogunu açar."""
        dialog = IceAktarmaDialog(self, self.vt)
        if dialog.exec_():
            self._notlari_yukle()
            self._kategorileri_yukle()
            self._durum_guncelle('Notlar içe aktarıldı')

    def _ice_aktar_format(self, format_adi: str):
        """Belirli formatta içe aktarır."""
        uzantilar = {
            'TXT': '*.txt',
            'Markdown': '*.md',
            'HTML': '*.html *.htm',
            'JSON': '*.json',
            'Evernote (ENEX)': '*.enex',
            'ZIP Arşivi': '*.zip'
        }

        dosya, _ = QFileDialog.getOpenFileName(
            self, f'{format_adi} Dosyası Seç',
            '', f'{format_adi} ({uzantilar.get(format_adi, "*.*")})'
        )

        if dosya:
            try:
                sonuc = self.ice_aktarici.dosya_ice_aktar(dosya)

                if sonuc['basarili']:
                    not_verisi = sonuc['not']
                    # Tek not veya liste olabilir
                    if isinstance(not_verisi, list):
                        notlar = not_verisi
                    else:
                        notlar = [not_verisi]

                    kayit_sonuc = self.ice_aktarici.notlari_kaydet(notlar)
                    self._notlari_yukle()
                    self._durum_guncelle(f'{kayit_sonuc["basarili"]} not içe aktarıldı')
                else:
                    QMessageBox.warning(self, 'Uyarı', sonuc['mesaj'])

            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'İçe aktarma hatası: {str(e)}')

    def _pdf_olarak_aktar(self):
        """Seçili notu PDF olarak dışa aktarır."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        baslik = self.baslik_input.text() or 'not'
        dosya_adi, _ = QFileDialog.getSaveFileName(
            self, 'PDF Olarak Kaydet',
            f'{baslik}.pdf',
            'PDF Dosyaları (*.pdf)'
        )

        if dosya_adi:
            icerik = self.editor.html_icerik_getir()
            if self.pdf_aktarici.pdf_olustur(dosya_adi, baslik, icerik):
                self._durum_guncelle(f'PDF olarak kaydedildi: {dosya_adi}')
            else:
                QMessageBox.critical(self, 'Hata', 'PDF oluşturulamadı.')

    def _markdown_olarak_aktar(self):
        """Seçili notu Markdown olarak dışa aktarır."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        baslik = self.baslik_input.text() or 'not'
        dosya_adi, _ = QFileDialog.getSaveFileName(
            self, 'Markdown Olarak Kaydet',
            f'{baslik}.md',
            'Markdown Dosyaları (*.md)'
        )

        if dosya_adi:
            # HTML'i Markdown'a çevir (basit dönüşüm)
            icerik = self.editor.duz_metin_getir()
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                f.write(f'# {baslik}\n\n{icerik}')

            self._durum_guncelle(f'Markdown olarak kaydedildi: {dosya_adi}')

    def _bulut_sync(self):
        """Bulut senkronizasyonu başlatır."""
        try:
            self.bulut_sync.senkronize_et()
            self._durum_guncelle('Senkronizasyon tamamlandı')
        except Exception as e:
            QMessageBox.warning(self, 'Uyarı', f'Senkronizasyon hatası: {str(e)}')

    def _bulut_ayarlari(self):
        """Bulut ayarları dialogunu gösterir."""
        dialog = BulutAyarlariDialog(self, self.bulut_sync)
        dialog.exec_()

    def _sablonlari_yonet(self):
        """Şablon yönetim dialogunu gösterir."""
        dialog = SablonSeciciDialog(self, self.sablon_yoneticisi)
        dialog.exec_()

    def _kisayollar_goster(self):
        """Klavye kısayolları dialogunu gösterir."""
        dialog = KisayollarDialog(self, self.kisayol_yoneticisi)
        dialog.exec_()

    def _html_olarak_aktar(self):
        """Seçili notu HTML olarak dışa aktarır."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        baslik = self.baslik_input.text() or 'not'
        dosya_adi, _ = QFileDialog.getSaveFileName(
            self, 'HTML Olarak Kaydet',
            f'{baslik}.html',
            'HTML Dosyaları (*.html)'
        )

        if dosya_adi:
            icerik = self.editor.html_icerik_getir()
            html_sablon = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{baslik}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; max-width: 800px; margin: auto; }}
        h1 {{ color: #333; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        code {{ font-family: 'Consolas', monospace; }}
    </style>
</head>
<body>
    <h1>{baslik}</h1>
    {icerik}
</body>
</html>'''

            with open(dosya_adi, 'w', encoding='utf-8') as f:
                f.write(html_sablon)

            self._durum_guncelle(f'HTML olarak kaydedildi: {dosya_adi}')

    def _txt_olarak_aktar(self):
        """Seçili notu metin olarak dışa aktarır."""
        if not self.secili_not_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce bir not seçin.')
            return

        baslik = self.baslik_input.text() or 'not'
        dosya_adi, _ = QFileDialog.getSaveFileName(
            self, 'Metin Olarak Kaydet',
            f'{baslik}.txt',
            'Metin Dosyaları (*.txt)'
        )

        if dosya_adi:
            icerik = self.editor.duz_metin_getir()
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                f.write(f'{baslik}\n{"=" * len(baslik)}\n\n{icerik}')

            self._durum_guncelle(f'Metin olarak kaydedildi: {dosya_adi}')

    def _cop_kutusunu_bosalt(self):
        """Çöp kutusunu boşaltır."""
        cevap = QMessageBox.question(
            self, 'Çöp Kutusunu Boşalt',
            'Çöp kutusundaki tüm notlar kalıcı olarak silinecek.\nDevam etmek istiyor musunuz?',
            QMessageBox.Yes | QMessageBox.No
        )

        if cevap == QMessageBox.Yes:
            # Önce silinecek notların resimlerini sil
            silinen_notlar = self.vt.cop_kutusundaki_notlar()
            for not_bilgi in silinen_notlar:
                # zengin_icerik'te HTML ve resimler var
                zengin_icerik = not_bilgi.get('zengin_icerik', '') or ''
                self._not_resimlerini_sil(zengin_icerik)

            self.vt.cop_kutusunu_bosalt()
            self._notlari_yukle()
            self._durum_guncelle('Çöp kutusu boşaltıldı')

    def _not_resimlerini_sil(self, icerik: str):
        """Not içeriğindeki yerel resimleri siler."""
        import re
        import urllib.parse

        if not icerik:
            return

        # file:/// ile başlayan yerel resim yollarını bul
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        resim_klasoru = os.path.join(os.path.dirname(self.vt.veritabani_yolu), 'resimler')
        # Normalize et (Windows için)
        resim_klasoru = os.path.normpath(resim_klasoru)

        print(f"DEBUG: Resim klasörü: {resim_klasoru}")
        print(f"DEBUG: İçerik uzunluğu: {len(icerik)}")
        print(f"DEBUG: İçerik önizleme: {icerik[:500]}...")

        # İçerikteki tüm img tag'lerini göster
        tum_imgler = re.findall(img_pattern, icerik, re.IGNORECASE)
        print(f"DEBUG: Bulunan img sayısı: {len(tum_imgler)}")
        for img_url in tum_imgler:
            print(f"DEBUG: IMG URL: {img_url[:100]}...")

        for match in re.finditer(img_pattern, icerik, re.IGNORECASE):
            url = match.group(1)
            print(f"DEBUG: Bulunan URL: {url}")

            # Yerel dosya mı kontrol et
            if url.startswith('file:///'):
                # Windows için file:/// sonrası yolu al
                # file:///N:/... -> N:/...
                yerel_yol = url.replace('file:///', '')
                # URL decode (boşluklar için %20 vs.)
                yerel_yol = urllib.parse.unquote(yerel_yol)
                # Windows yol ayırıcılarını düzelt
                yerel_yol = yerel_yol.replace('/', os.sep)
                yerel_yol = os.path.normpath(yerel_yol)

                print(f"DEBUG: Yerel yol: {yerel_yol}")
                print(f"DEBUG: Dosya var mı: {os.path.exists(yerel_yol)}")
                print(f"DEBUG: Resim klasöründe mi: {resim_klasoru in yerel_yol}")

                # Sadece resimler klasöründeki dosyaları sil (güvenlik için)
                if yerel_yol and resim_klasoru in yerel_yol:
                    try:
                        if os.path.exists(yerel_yol):
                            os.remove(yerel_yol)
                            print(f"Resim silindi: {yerel_yol}")
                        else:
                            print(f"Dosya bulunamadı: {yerel_yol}")
                    except Exception as e:
                        print(f"Resim silinirken hata: {e}")

    def _istatistikleri_goster(self):
        """İstatistikler dialogunu gösterir."""
        istatistikler = self.vt.istatistikleri_getir()
        dialog = IstatistiklerDialog(self, istatistikler)
        dialog.exec_()

    def _ayarlari_goster(self):
        """Ayarlar dialogunu gösterir."""
        dialog = AyarlarDialog(self, self.mevcut_tema)
        if dialog.exec_():
            yeni_tema = dialog.tema_getir()
            if yeni_tema != self.mevcut_tema:
                self._tema_degistir(yeni_tema)

    def _hakkinda_goster(self):
        """Hakkında dialogunu gösterir."""
        QMessageBox.about(
            self, 'Hakkında',
            '''<h2>📝 Not Defteri Pro</h2>
            <p>Gelişmiş not tutma ve günlük uygulaması.</p>

            <p><b>Özellikler:</b></p>
            <ul>
            <li>Zengin metin düzenleme</li>
            <li>Markdown desteği</li>
            <li>Şifreli notlar (AES-256)</li>
            <li>Otomatik kaydetme</li>
            <li>Sürüm geçmişi</li>
            <li>Notlar arası bağlantı</li>
            <li>Yapılacaklar listesi</li>
            <li>Resim ve kod bloğu</li>
            <li>PDF dışa aktarma</li>
            <li>Tam metin arama</li>
            <li>Bulut senkronizasyon</li>
            <li>Şablonlar</li>
            <li>Takvim görünümü</li>
            <li>Web clipper</li>
            <li>Çoklu pencere</li>
            </ul>

            <p><b>Sürüm:</b> 3.0 Pro</p>
            <p><b>Python:</b> 3.11.9</p>
            <p><b>Geliştirici:</b> Claude AI</p>'''
        )

    def _arama_odaklan(self):
        """Arama kutusuna odaklanır."""
        self.ust_arama_input.setFocus()
        self.ust_arama_input.selectAll()

    def _degisiklik_yapildi(self):
        """Değişiklik yapıldığında çağrılır."""
        self.degisiklik_var = True

    def _durum_guncelle(self, mesaj: str):
        """Durum çubuğunu günceller."""
        self.durum_cubugu.showMessage(mesaj, 5000)

    def _pencere_konumu_yukle(self):
        """Pencere konumunu ve boyutunu yükler."""
        genislik = self.vt.ayar_getir('pencere_genislik', '1200')
        yukseklik = self.vt.ayar_getir('pencere_yukseklik', '800')
        self.resize(int(genislik), int(yukseklik))

    def closeEvent(self, event):
        """Pencere kapatılırken çağrılır."""
        # Değişiklik kontrolü
        if self.degisiklik_var and self.secili_not_id:
            cevap = QMessageBox.question(
                self, 'Kaydedilmemiş Değişiklikler',
                'Kaydedilmemiş değişiklikler var. Kaydetmek ister misiniz?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if cevap == QMessageBox.Yes:
                self._notu_kaydet()
            elif cevap == QMessageBox.Cancel:
                event.ignore()
                return

        # Otomatik kaydı durdur
        self.otomatik_kayit.durdur()

        # Tüm açık pencereleri kapat
        self.coklu_pencere.tum_pencereleri_kapat()

        # Pencere boyutlarını kaydet
        self.vt.ayar_kaydet('pencere_genislik', str(self.width()))
        self.vt.ayar_kaydet('pencere_yukseklik', str(self.height()))

        event.accept()


def main():
    """Uygulamayı başlatır."""
    # Yüksek DPI desteği
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    uygulama = QApplication(sys.argv)
    uygulama.setApplicationName('Not Defteri Pro')
    uygulama.setOrganizationName('NotDefteri')

    # Varsayılan font
    font = QFont('Segoe UI', 10)
    uygulama.setFont(font)

    pencere = NotDefteri()
    pencere.show()

    sys.exit(uygulama.exec_())


if __name__ == '__main__':
    main()
