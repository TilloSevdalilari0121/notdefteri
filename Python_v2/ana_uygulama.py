# -*- coding: utf-8 -*-
"""
Not Defteri Uygulaması - Ana Uygulama Modülü
Gelişmiş not tutma ve günlük uygulaması.

Özellikler:
- Zengin metin düzenleme (kalın, italik, renkli yazı, listeler vb.)
- Kategorilere göre not organizasyonu
- Etiket sistemi
- Gelişmiş arama ve filtreleme
- Favori notlar
- Hatırlatıcılar
- Karanlık/Aydınlık tema desteği
- Dışa aktarma (HTML, TXT)
- Çöp kutusu

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
    QStatusBar, QFileDialog, QInputDialog, QToolBar
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

# Uygulama modülleri
from veritabani import VeritabaniYoneticisi
from stiller import TemaYoneticisi
from bilesenler import (
    ZenginMetinDuzenleyici, NotKarti, KategoriDuzenleDialog,
    EtiketDuzenleDialog, HatirlaticiDialog, AyarlarDialog,
    IstatistiklerDialog, EtiketSeciciDialog
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

        # Arayüzü oluştur
        self._arayuz_olustur()
        self._menu_olustur()
        self._tema_uygula()
        self._baglantilari_kur()

        # Verileri yükle
        self._kategorileri_yukle()
        self._etiketleri_yukle()
        self._notlari_yukle()

        # Hatırlatıcı kontrolü için zamanlayıcı
        self.hatirlatici_timer = QTimer()
        self.hatirlatici_timer.timeout.connect(self._hatirlaticlari_kontrol_et)
        self.hatirlatici_timer.start(60000)  # Her dakika kontrol et

        # Pencere ayarları
        self.setWindowTitle('📝 Not Defteri')
        self.setMinimumSize(1000, 700)
        self._pencere_konumu_yukle()

    def _arayuz_olustur(self):
        """Ana arayüzü oluşturur."""
        # Ana widget
        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)

        ana_yerlesim = QHBoxLayout(ana_widget)
        ana_yerlesim.setContentsMargins(0, 0, 0, 0)
        ana_yerlesim.setSpacing(0)

        # Splitter
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
        self.splitter.setSizes([200, 300, 500])

        ana_yerlesim.addWidget(self.splitter)

        # Durum çubuğu
        self.durum_cubugu = QStatusBar()
        self.setStatusBar(self.durum_cubugu)
        self._durum_guncelle('Hazır')

    def _kenar_cubugu_olustur(self) -> QWidget:
        """Sol kenar çubuğunu oluşturur."""
        kenar = QWidget()
        kenar.setObjectName('kenarCubugu')
        kenar.setMinimumWidth(180)
        kenar.setMaximumWidth(250)

        yerlesim = QVBoxLayout(kenar)
        yerlesim.setContentsMargins(10, 10, 10, 10)
        yerlesim.setSpacing(8)

        # Yeni Not Butonu
        self.yeni_not_btn = QPushButton('➕ Yeni Not')
        self.yeni_not_btn.setMinimumHeight(40)
        yerlesim.addWidget(self.yeni_not_btn)

        # Arama
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText('🔍 Ara...')
        self.arama_input.setObjectName('aramaCubugu')
        yerlesim.addWidget(self.arama_input)

        # Filtreler
        filtre_baslik = QLabel('📋 Filtreler')
        filtre_baslik.setStyleSheet('font-weight: bold; margin-top: 10px;')
        yerlesim.addWidget(filtre_baslik)

        self.filtre_listesi = QListWidget()
        self.filtre_listesi.setMaximumHeight(120)

        filtreler = [
            ('📝 Tüm Notlar', 'tum'),
            ('⭐ Favoriler', 'favoriler'),
            ('🗑️ Çöp Kutusu', 'cop')
        ]
        for metin, veri in filtreler:
            item = QListWidgetItem(metin)
            item.setData(Qt.UserRole, veri)
            self.filtre_listesi.addItem(item)

        self.filtre_listesi.setCurrentRow(0)
        yerlesim.addWidget(self.filtre_listesi)

        # Kategoriler
        kategori_baslik_yerlesim = QHBoxLayout()
        kategori_baslik = QLabel('📁 Kategoriler')
        kategori_baslik.setStyleSheet('font-weight: bold; margin-top: 10px;')
        kategori_baslik_yerlesim.addWidget(kategori_baslik)

        self.kategori_ekle_btn = QPushButton('+')
        self.kategori_ekle_btn.setFixedSize(25, 25)
        self.kategori_ekle_btn.setToolTip('Yeni Kategori')
        kategori_baslik_yerlesim.addWidget(self.kategori_ekle_btn)
        yerlesim.addLayout(kategori_baslik_yerlesim)

        self.kategori_agaci = QTreeWidget()
        self.kategori_agaci.setHeaderHidden(True)
        self.kategori_agaci.setContextMenuPolicy(Qt.CustomContextMenu)
        yerlesim.addWidget(self.kategori_agaci)

        # Etiketler
        etiket_baslik_yerlesim = QHBoxLayout()
        etiket_baslik = QLabel('🏷️ Etiketler')
        etiket_baslik.setStyleSheet('font-weight: bold; margin-top: 10px;')
        etiket_baslik_yerlesim.addWidget(etiket_baslik)

        self.etiket_ekle_btn = QPushButton('+')
        self.etiket_ekle_btn.setFixedSize(25, 25)
        self.etiket_ekle_btn.setToolTip('Yeni Etiket')
        etiket_baslik_yerlesim.addWidget(self.etiket_ekle_btn)
        yerlesim.addLayout(etiket_baslik_yerlesim)

        self.etiket_listesi = QListWidget()
        self.etiket_listesi.setMaximumHeight(150)
        self.etiket_listesi.setContextMenuPolicy(Qt.CustomContextMenu)
        yerlesim.addWidget(self.etiket_listesi)

        yerlesim.addStretch()

        # İstatistikler butonu
        self.istatistik_btn = QPushButton('📊 İstatistikler')
        self.istatistik_btn.setObjectName('ikinciDugme')
        yerlesim.addWidget(self.istatistik_btn)

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
        yerlesim.addWidget(self.editor, 1)

        # Alt butonlar
        alt_yerlesim = QHBoxLayout()

        self.kaydet_btn = QPushButton('💾 Kaydet')
        self.kaydet_btn.setMinimumHeight(35)
        alt_yerlesim.addWidget(self.kaydet_btn)

        self.sil_btn = QPushButton('🗑️ Sil')
        self.sil_btn.setObjectName('tehlikeDugme')
        self.sil_btn.setMinimumHeight(35)
        alt_yerlesim.addWidget(self.sil_btn)

        yerlesim.addLayout(alt_yerlesim)

        return panel

    def _menu_olustur(self):
        """Menü çubuğunu oluşturur."""
        menubar = self.menuBar()

        # Dosya Menüsü
        dosya_menu = menubar.addMenu('Dosya')

        yeni_not_action = QAction('Yeni Not', self)
        yeni_not_action.setShortcut('Ctrl+N')
        yeni_not_action.triggered.connect(self._yeni_not)
        dosya_menu.addAction(yeni_not_action)

        kaydet_action = QAction('Kaydet', self)
        kaydet_action.setShortcut('Ctrl+S')
        kaydet_action.triggered.connect(self._notu_kaydet)
        dosya_menu.addAction(kaydet_action)

        dosya_menu.addSeparator()

        html_aktar_action = QAction('HTML Olarak Dışa Aktar', self)
        html_aktar_action.triggered.connect(self._html_olarak_aktar)
        dosya_menu.addAction(html_aktar_action)

        txt_aktar_action = QAction('Metin Olarak Dışa Aktar', self)
        txt_aktar_action.triggered.connect(self._txt_olarak_aktar)
        dosya_menu.addAction(txt_aktar_action)

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

        istatistik_action = QAction('İstatistikler', self)
        istatistik_action.triggered.connect(self._istatistikleri_goster)
        gorunum_menu.addAction(istatistik_action)

        # Araçlar Menüsü
        araclar_menu = menubar.addMenu('Araçlar')

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
        # Yeni not
        self.yeni_not_btn.clicked.connect(self._yeni_not)

        # Arama
        self.arama_input.textChanged.connect(self._arama_yap)

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

        # Kategori ve etiket seçimi
        self.kategori_combo_label.mousePressEvent = lambda e: self._kategori_sec_dialog()
        self.etiket_label.mousePressEvent = lambda e: self._etiket_sec_dialog()

        # Sıralama
        self.siralama_btn.clicked.connect(self._siralama_menu_goster)

        # İstatistikler
        self.istatistik_btn.clicked.connect(self._istatistikleri_goster)

        # Değişiklik takibi
        self.baslik_input.textChanged.connect(self._degisiklik_yapildi)
        self.editor.icerikDegisti.connect(self._degisiklik_yapildi)

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

    def _notu_kaydet(self):
        """Mevcut notu kaydeder."""
        if not self.secili_not_id:
            return

        baslik = self.baslik_input.text().strip()
        if not baslik:
            baslik = 'Başlıksız Not'

        zengin_icerik = self.editor.html_icerik_getir()
        duz_icerik = self.editor.duz_metin_getir()

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
        self.kategori_combo_label.setText('Genel')
        self.etiket_label.setText('Etiket ekle...')
        self.tarih_label.setText('')
        self._secili_kategori_id = None
        self._secili_etiketler = []
        self.degisiklik_var = False

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

    def _filtre_degisti(self, index: int):
        """Filtre değiştiğinde notları yeniden yükler."""
        self.arama_input.clear()
        self.kategori_agaci.clearSelection()
        self.etiket_listesi.clearSelection()

        item = self.filtre_listesi.item(index)
        if item:
            filtre = item.data(Qt.UserRole)
            if filtre == 'tum':
                self._notlari_yukle()
            elif filtre == 'favoriler':
                self._notlari_yukle(sadece_favoriler=True)
            elif filtre == 'cop':
                self._notlari_yukle(silinen=True)

    def _kategori_secildi(self, item: QTreeWidgetItem, column: int):
        """Kategori seçildiğinde notları filtreler."""
        self.arama_input.clear()
        self.filtre_listesi.clearSelection()
        self.etiket_listesi.clearSelection()

        kategori_id = item.data(0, Qt.UserRole)
        self._notlari_yukle(kategori_id=kategori_id)

    def _etiket_secildi(self, item: QListWidgetItem):
        """Etiket seçildiğinde notları filtreler."""
        self.arama_input.clear()
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
        body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: auto; }}
        h1 {{ color: #333; }}
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
            self.vt.cop_kutusunu_bosalt()
            self._notlari_yukle()
            self._durum_guncelle('Çöp kutusu boşaltıldı')

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
            '''<h2>📝 Not Defteri</h2>
            <p>Gelişmiş not tutma ve günlük uygulaması.</p>

            <p><b>Özellikler:</b></p>
            <ul>
            <li>Zengin metin düzenleme</li>
            <li>Kategoriler ve etiketler</li>
            <li>Arama ve filtreleme</li>
            <li>Hatırlatıcılar</li>
            <li>Karanlık/Aydınlık tema</li>
            <li>Dışa aktarma</li>
            </ul>

            <p><b>Sürüm:</b> 2.0</p>
            <p><b>Python:</b> 3.11.9</p>
            <p><b>Geliştirici:</b> Claude AI</p>'''
        )

    def _arama_odaklan(self):
        """Arama kutusuna odaklanır."""
        self.arama_input.setFocus()
        self.arama_input.selectAll()

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
    uygulama.setApplicationName('Not Defteri')
    uygulama.setOrganizationName('NotDefteri')

    # Varsayılan font
    font = QFont('Segoe UI', 10)
    uygulama.setFont(font)

    pencere = NotDefteri()
    pencere.show()

    sys.exit(uygulama.exec_())


if __name__ == '__main__':
    main()
