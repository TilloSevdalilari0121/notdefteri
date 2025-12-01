# -*- coding: utf-8 -*-
"""
Not Defteri - İçe Aktarma Modülü
Farklı formatlardan ve uygulamalardan not içe aktarma.
"""

import os
import json
import re
import zipfile
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QListWidgetItem, QProgressBar,
    QGroupBox, QRadioButton, QCheckBox, QMessageBox, QTextEdit,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont


class IceAktarici:
    """Farklı formatlardan not içe aktaran sınıf."""

    DESTEKLENEN_FORMATLAR = {
        'txt': 'Düz Metin Dosyası',
        'md': 'Markdown Dosyası',
        'html': 'HTML Dosyası',
        'json': 'JSON Dosyası',
        'enex': 'Evernote Arşivi',
        'zip': 'ZIP Arşivi (Çoklu)',
    }

    def __init__(self, veritabani=None):
        self.vt = veritabani

    def dosya_ice_aktar(self, dosya_yolu: str, format_tipi: str = None) -> Dict:
        """
        Tek dosya içe aktarır.

        Returns:
            {'basarili': bool, 'not': dict veya None, 'mesaj': str}
        """
        if not os.path.exists(dosya_yolu):
            return {'basarili': False, 'not': None, 'mesaj': 'Dosya bulunamadı'}

        # Format belirleme
        if not format_tipi:
            _, uzanti = os.path.splitext(dosya_yolu)
            format_tipi = uzanti.lower().lstrip('.')

        try:
            if format_tipi == 'txt':
                return self._txt_ice_aktar(dosya_yolu)
            elif format_tipi == 'md':
                return self._md_ice_aktar(dosya_yolu)
            elif format_tipi == 'html':
                return self._html_ice_aktar(dosya_yolu)
            elif format_tipi == 'json':
                return self._json_ice_aktar(dosya_yolu)
            elif format_tipi == 'enex':
                return self._evernote_ice_aktar(dosya_yolu)
            elif format_tipi == 'zip':
                return self._zip_ice_aktar(dosya_yolu)
            else:
                return {'basarili': False, 'not': None, 'mesaj': f'Desteklenmeyen format: {format_tipi}'}

        except Exception as e:
            return {'basarili': False, 'not': None, 'mesaj': str(e)}

    def _txt_ice_aktar(self, dosya_yolu: str) -> Dict:
        """Düz metin dosyası içe aktarır."""
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()

        dosya_adi = os.path.splitext(os.path.basename(dosya_yolu))[0]

        not_verisi = {
            'baslik': dosya_adi,
            'icerik': icerik,
            'zengin_icerik': f'<pre>{icerik}</pre>',
        }

        return {'basarili': True, 'not': not_verisi, 'mesaj': 'Başarıyla içe aktarıldı'}

    def _md_ice_aktar(self, dosya_yolu: str) -> Dict:
        """Markdown dosyası içe aktarır."""
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()

        dosya_adi = os.path.splitext(os.path.basename(dosya_yolu))[0]

        # İlk satır başlık olabilir
        satirlar = icerik.split('\n')
        baslik = dosya_adi

        if satirlar and satirlar[0].startswith('# '):
            baslik = satirlar[0][2:].strip()
            icerik = '\n'.join(satirlar[1:]).strip()

        # Markdown'ı HTML'e çevir (basit)
        try:
            import markdown
            zengin_icerik = markdown.markdown(icerik, extensions=['extra'])
        except ImportError:
            zengin_icerik = f'<pre>{icerik}</pre>'

        not_verisi = {
            'baslik': baslik,
            'icerik': icerik,
            'zengin_icerik': zengin_icerik,
        }

        return {'basarili': True, 'not': not_verisi, 'mesaj': 'Başarıyla içe aktarıldı'}

    def _html_ice_aktar(self, dosya_yolu: str) -> Dict:
        """HTML dosyası içe aktarır."""
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            html_icerik = f.read()

        dosya_adi = os.path.splitext(os.path.basename(dosya_yolu))[0]

        # Başlığı bul
        baslik = dosya_adi
        baslik_match = re.search(r'<title>(.*?)</title>', html_icerik, re.IGNORECASE)
        if baslik_match:
            baslik = baslik_match.group(1)

        # Body içeriğini al
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_icerik, re.IGNORECASE | re.DOTALL)
        if body_match:
            zengin_icerik = body_match.group(1)
        else:
            zengin_icerik = html_icerik

        # Düz metni çıkar
        duz_metin = re.sub(r'<[^>]+>', '', zengin_icerik)
        duz_metin = re.sub(r'\s+', ' ', duz_metin).strip()

        not_verisi = {
            'baslik': baslik,
            'icerik': duz_metin,
            'zengin_icerik': zengin_icerik,
        }

        return {'basarili': True, 'not': not_verisi, 'mesaj': 'Başarıyla içe aktarıldı'}

    def _json_ice_aktar(self, dosya_yolu: str) -> Dict:
        """JSON dosyası içe aktarır."""
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            veri = json.load(f)

        # Tek not veya not listesi olabilir
        if isinstance(veri, list):
            # İlk notu al
            if not veri:
                return {'basarili': False, 'not': None, 'mesaj': 'JSON dosyası boş'}
            veri = veri[0]

        not_verisi = {
            'baslik': veri.get('baslik', veri.get('title', 'İçe Aktarılan Not')),
            'icerik': veri.get('icerik', veri.get('content', '')),
            'zengin_icerik': veri.get('zengin_icerik', veri.get('html', '')),
        }

        return {'basarili': True, 'not': not_verisi, 'mesaj': 'Başarıyla içe aktarıldı'}

    def _evernote_ice_aktar(self, dosya_yolu: str) -> Dict:
        """
        Evernote .enex dosyası içe aktarır.
        ENEX, XML tabanlı bir formattır.
        """
        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(dosya_yolu)
            root = tree.getroot()

            notlar = []

            for note in root.findall('.//note'):
                baslik = note.find('title')
                baslik = baslik.text if baslik is not None else 'Evernote Notu'

                content = note.find('content')
                if content is not None and content.text:
                    # ENEX içeriği CDATA içinde HTML
                    zengin_icerik = content.text
                    # CDATA'yı temizle
                    if zengin_icerik.startswith('<![CDATA['):
                        zengin_icerik = zengin_icerik[9:-3]
                else:
                    zengin_icerik = ''

                # Düz metni çıkar
                duz_metin = re.sub(r'<[^>]+>', '', zengin_icerik)

                notlar.append({
                    'baslik': baslik,
                    'icerik': duz_metin,
                    'zengin_icerik': zengin_icerik,
                })

            if notlar:
                return {
                    'basarili': True,
                    'not': notlar[0] if len(notlar) == 1 else notlar,
                    'mesaj': f'{len(notlar)} not içe aktarıldı'
                }
            else:
                return {'basarili': False, 'not': None, 'mesaj': 'ENEX dosyasında not bulunamadı'}

        except Exception as e:
            return {'basarili': False, 'not': None, 'mesaj': f'ENEX okuma hatası: {e}'}

    def _zip_ice_aktar(self, dosya_yolu: str) -> Dict:
        """ZIP arşivi içe aktarır."""
        try:
            notlar = []

            with zipfile.ZipFile(dosya_yolu, 'r') as zip_ref:
                for dosya_adi in zip_ref.namelist():
                    _, uzanti = os.path.splitext(dosya_adi)
                    uzanti = uzanti.lower().lstrip('.')

                    if uzanti in ['txt', 'md', 'html']:
                        with zip_ref.open(dosya_adi) as f:
                            icerik = f.read().decode('utf-8')

                        not_verisi = {
                            'baslik': os.path.splitext(os.path.basename(dosya_adi))[0],
                            'icerik': icerik,
                            'zengin_icerik': icerik if uzanti == 'html' else f'<pre>{icerik}</pre>',
                        }
                        notlar.append(not_verisi)

            if notlar:
                return {
                    'basarili': True,
                    'not': notlar,
                    'mesaj': f'{len(notlar)} not içe aktarıldı'
                }
            else:
                return {'basarili': False, 'not': None, 'mesaj': 'ZIP dosyasında uygun not bulunamadı'}

        except Exception as e:
            return {'basarili': False, 'not': None, 'mesaj': f'ZIP okuma hatası: {e}'}

    def notlari_kaydet(self, notlar: List[Dict], kategori_id: int = None) -> Dict:
        """
        Notları veritabanına kaydeder.

        Returns:
            {'basarili': int, 'basarisiz': int}
        """
        if not self.vt:
            return {'basarili': 0, 'basarisiz': len(notlar)}

        sonuc = {'basarili': 0, 'basarisiz': 0}

        for not_verisi in notlar:
            try:
                self.vt.not_ekle(
                    baslik=not_verisi.get('baslik', 'İçe Aktarılan Not'),
                    icerik=not_verisi.get('icerik', ''),
                    zengin_icerik=not_verisi.get('zengin_icerik', ''),
                    kategori_id=kategori_id
                )
                sonuc['basarili'] += 1
            except Exception:
                sonuc['basarisiz'] += 1

        return sonuc


class IceAktarmaDialog(QDialog):
    """İçe aktarma dialogu."""

    iceAktarildi = pyqtSignal(int)  # İçe aktarılan not sayısı

    def __init__(self, parent=None, veritabani=None):
        super().__init__(parent)
        self.vt = veritabani
        self.aktarici = IceAktarici(veritabani)
        self.secili_dosyalar = []
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('İçe Aktar')
        self.setMinimumSize(500, 450)

        yerlesim = QVBoxLayout(self)

        # Başlık
        baslik = QLabel('📥 Not İçe Aktar')
        baslik.setFont(QFont('Segoe UI', 14, QFont.Bold))
        yerlesim.addWidget(baslik)

        # Desteklenen formatlar
        format_info = QLabel(
            'Desteklenen formatlar: TXT, MD (Markdown), HTML, JSON, ENEX (Evernote), ZIP'
        )
        format_info.setStyleSheet('color: gray;')
        format_info.setWordWrap(True)
        yerlesim.addWidget(format_info)

        # Dosya seçme butonu
        dosya_yerlesim = QHBoxLayout()

        self.dosya_btn = QPushButton('📁 Dosya Seç')
        self.dosya_btn.clicked.connect(self._dosya_sec)
        dosya_yerlesim.addWidget(self.dosya_btn)

        self.klasor_btn = QPushButton('📂 Klasör Seç')
        self.klasor_btn.clicked.connect(self._klasor_sec)
        dosya_yerlesim.addWidget(self.klasor_btn)

        dosya_yerlesim.addStretch()

        yerlesim.addLayout(dosya_yerlesim)

        # Seçili dosyalar listesi
        yerlesim.addWidget(QLabel('Seçili dosyalar:'))

        self.dosya_listesi = QListWidget()
        self.dosya_listesi.setMaximumHeight(150)
        yerlesim.addWidget(self.dosya_listesi)

        # Seçenekler
        secenek_grup = QGroupBox('Seçenekler')
        secenek_yerlesim = QVBoxLayout(secenek_grup)

        self.kategori_check = QCheckBox('Tümünü aynı kategoriye ekle')
        secenek_yerlesim.addWidget(self.kategori_check)

        self.tarih_check = QCheckBox('Dosya değişiklik tarihini kullan')
        self.tarih_check.setChecked(True)
        secenek_yerlesim.addWidget(self.tarih_check)

        yerlesim.addWidget(secenek_grup)

        # İlerleme
        self.ilerleme = QProgressBar()
        self.ilerleme.hide()
        yerlesim.addWidget(self.ilerleme)

        # Durum etiketi
        self.durum_label = QLabel('')
        yerlesim.addWidget(self.durum_label)

        # Butonlar
        buton_yerlesim = QHBoxLayout()

        iptal_btn = QPushButton('İptal')
        iptal_btn.clicked.connect(self.reject)
        buton_yerlesim.addWidget(iptal_btn)

        buton_yerlesim.addStretch()

        self.aktar_btn = QPushButton('📥 İçe Aktar')
        self.aktar_btn.setEnabled(False)
        self.aktar_btn.clicked.connect(self._ice_aktar)
        buton_yerlesim.addWidget(self.aktar_btn)

        yerlesim.addLayout(buton_yerlesim)

    def _dosya_sec(self):
        """Dosya seçme dialogu."""
        formatlar = ' '.join([f'*.{f}' for f in IceAktarici.DESTEKLENEN_FORMATLAR.keys()])
        dosyalar, _ = QFileDialog.getOpenFileNames(
            self, 'Dosya Seç',
            '',
            f'Desteklenen Dosyalar ({formatlar});;Tüm Dosyalar (*.*)'
        )

        if dosyalar:
            self._dosyalari_ekle(dosyalar)

    def _klasor_sec(self):
        """Klasör seçme dialogu."""
        klasor = QFileDialog.getExistingDirectory(self, 'Klasör Seç')

        if klasor:
            dosyalar = []
            for dosya in os.listdir(klasor):
                _, uzanti = os.path.splitext(dosya)
                if uzanti.lower().lstrip('.') in IceAktarici.DESTEKLENEN_FORMATLAR:
                    dosyalar.append(os.path.join(klasor, dosya))

            if dosyalar:
                self._dosyalari_ekle(dosyalar)
            else:
                QMessageBox.information(self, 'Bilgi', 'Klasörde uygun dosya bulunamadı.')

    def _dosyalari_ekle(self, dosyalar: List[str]):
        """Dosyaları listeye ekler."""
        for dosya in dosyalar:
            if dosya not in self.secili_dosyalar:
                self.secili_dosyalar.append(dosya)

                item = QListWidgetItem(os.path.basename(dosya))
                item.setToolTip(dosya)
                self.dosya_listesi.addItem(item)

        self.aktar_btn.setEnabled(len(self.secili_dosyalar) > 0)
        self.durum_label.setText(f'{len(self.secili_dosyalar)} dosya seçili')

    def _ice_aktar(self):
        """İçe aktarma işlemini başlatır."""
        if not self.secili_dosyalar:
            return

        self.ilerleme.show()
        self.ilerleme.setMaximum(len(self.secili_dosyalar))
        self.ilerleme.setValue(0)

        basarili = 0
        basarisiz = 0

        for i, dosya in enumerate(self.secili_dosyalar):
            sonuc = self.aktarici.dosya_ice_aktar(dosya)

            if sonuc['basarili']:
                not_verisi = sonuc['not']

                # Tek not veya liste
                if isinstance(not_verisi, list):
                    notlar = not_verisi
                else:
                    notlar = [not_verisi]

                kayit_sonuc = self.aktarici.notlari_kaydet(notlar)
                basarili += kayit_sonuc['basarili']
                basarisiz += kayit_sonuc['basarisiz']
            else:
                basarisiz += 1

            self.ilerleme.setValue(i + 1)

        self.ilerleme.hide()
        self.durum_label.setText(f'Tamamlandı: {basarili} başarılı, {basarisiz} başarısız')

        if basarili > 0:
            self.iceAktarildi.emit(basarili)
            QMessageBox.information(
                self, 'Tamamlandı',
                f'{basarili} not başarıyla içe aktarıldı.'
            )
            self.accept()
        else:
            QMessageBox.warning(self, 'Hata', 'Hiçbir not içe aktarılamadı.')
