# -*- coding: utf-8 -*-
"""
Not Defteri - Bulut Senkronizasyon Modülü
Google Drive ve Dropbox entegrasyonu.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Optional, List, Dict
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar, QGroupBox,
    QRadioButton, QLineEdit, QMessageBox, QFileDialog, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont

# Opsiyonel: Bulut servisleri için kütüphaneler
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False


class BulutServisBase:
    """Bulut servisi temel sınıfı."""

    def __init__(self):
        self.baglantiDurumu = False

    def baglan(self) -> bool:
        """Servise bağlanır."""
        raise NotImplementedError

    def baglanti_kes(self):
        """Bağlantıyı keser."""
        self.baglantiDurumu = False

    def dosya_yukle(self, yerel_yol: str, uzak_yol: str) -> bool:
        """Dosya yükler."""
        raise NotImplementedError

    def dosya_indir(self, uzak_yol: str, yerel_yol: str) -> bool:
        """Dosya indirir."""
        raise NotImplementedError

    def dosyalari_listele(self, klasor: str = '') -> List[Dict]:
        """Dosyaları listeler."""
        raise NotImplementedError


class GoogleDriveServisi(BulutServisBase):
    """Google Drive entegrasyonu."""

    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self, credentials_path: str = None):
        super().__init__()
        self.credentials_path = credentials_path
        self.service = None
        self.klasor_id = None

    def baglan(self) -> bool:
        """Google Drive'a bağlanır."""
        if not GOOGLE_AVAILABLE:
            return False

        try:
            creds = None
            token_path = 'token.json'

            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                else:
                    if not self.credentials_path:
                        return False
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            self.service = build('drive', 'v3', credentials=creds)
            self.baglantiDurumu = True

            # Not Defteri klasörünü bul veya oluştur
            self._klasor_hazirla()

            return True
        except Exception as e:
            print(f"Google Drive bağlantı hatası: {e}")
            return False

    def _klasor_hazirla(self):
        """Not Defteri klasörünü hazırlar."""
        try:
            # Klasörü ara
            results = self.service.files().list(
                q="name='NotDefteri' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            items = results.get('files', [])

            if items:
                self.klasor_id = items[0]['id']
            else:
                # Klasör oluştur
                file_metadata = {
                    'name': 'NotDefteri',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                file = self.service.files().create(
                    body=file_metadata, fields='id'
                ).execute()
                self.klasor_id = file.get('id')
        except Exception as e:
            print(f"Klasör hazırlama hatası: {e}")

    def dosya_yukle(self, yerel_yol: str, uzak_ad: str) -> bool:
        """Dosyayı Google Drive'a yükler."""
        if not self.service or not self.klasor_id:
            return False

        try:
            file_metadata = {
                'name': uzak_ad,
                'parents': [self.klasor_id]
            }
            media = MediaFileUpload(yerel_yol, resumable=True)

            # Mevcut dosyayı kontrol et
            results = self.service.files().list(
                q=f"name='{uzak_ad}' and '{self.klasor_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id)'
            ).execute()

            items = results.get('files', [])

            if items:
                # Güncelle
                self.service.files().update(
                    fileId=items[0]['id'],
                    media_body=media
                ).execute()
            else:
                # Yeni yükle
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

            return True
        except Exception as e:
            print(f"Dosya yükleme hatası: {e}")
            return False

    def dosya_indir(self, uzak_ad: str, yerel_yol: str) -> bool:
        """Dosyayı Google Drive'dan indirir."""
        if not self.service or not self.klasor_id:
            return False

        try:
            results = self.service.files().list(
                q=f"name='{uzak_ad}' and '{self.klasor_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id)'
            ).execute()

            items = results.get('files', [])

            if not items:
                return False

            request = self.service.files().get_media(fileId=items[0]['id'])

            with open(yerel_yol, 'wb') as f:
                import io
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            return True
        except Exception as e:
            print(f"Dosya indirme hatası: {e}")
            return False


class DropboxServisi(BulutServisBase):
    """Dropbox entegrasyonu."""

    def __init__(self, access_token: str = None):
        super().__init__()
        self.access_token = access_token
        self.dbx = None

    def baglan(self) -> bool:
        """Dropbox'a bağlanır."""
        if not DROPBOX_AVAILABLE or not self.access_token:
            return False

        try:
            self.dbx = dropbox.Dropbox(self.access_token)
            self.dbx.users_get_current_account()
            self.baglantiDurumu = True
            return True
        except Exception as e:
            print(f"Dropbox bağlantı hatası: {e}")
            return False

    def dosya_yukle(self, yerel_yol: str, uzak_yol: str) -> bool:
        """Dosyayı Dropbox'a yükler."""
        if not self.dbx:
            return False

        try:
            with open(yerel_yol, 'rb') as f:
                self.dbx.files_upload(
                    f.read(),
                    f'/NotDefteri/{uzak_yol}',
                    mode=dropbox.files.WriteMode.overwrite
                )
            return True
        except Exception as e:
            print(f"Dropbox yükleme hatası: {e}")
            return False

    def dosya_indir(self, uzak_yol: str, yerel_yol: str) -> bool:
        """Dosyayı Dropbox'tan indirir."""
        if not self.dbx:
            return False

        try:
            self.dbx.files_download_to_file(yerel_yol, f'/NotDefteri/{uzak_yol}')
            return True
        except Exception as e:
            print(f"Dropbox indirme hatası: {e}")
            return False


class YerelKlasorServisi(BulutServisBase):
    """Yerel klasör senkronizasyonu (basit yedekleme)."""

    def __init__(self, hedef_klasor: str = None):
        super().__init__()
        self.hedef_klasor = hedef_klasor

    def baglan(self) -> bool:
        """Klasör erişimini kontrol eder."""
        if not self.hedef_klasor:
            return False

        try:
            os.makedirs(self.hedef_klasor, exist_ok=True)
            self.baglantiDurumu = True
            return True
        except Exception:
            return False

    def dosya_yukle(self, yerel_yol: str, uzak_ad: str) -> bool:
        """Dosyayı hedef klasöre kopyalar."""
        if not self.hedef_klasor:
            return False

        try:
            import shutil
            hedef = os.path.join(self.hedef_klasor, uzak_ad)
            shutil.copy2(yerel_yol, hedef)
            return True
        except Exception as e:
            print(f"Dosya kopyalama hatası: {e}")
            return False

    def dosya_indir(self, uzak_ad: str, yerel_yol: str) -> bool:
        """Dosyayı hedef klasörden kopyalar."""
        if not self.hedef_klasor:
            return False

        try:
            import shutil
            kaynak = os.path.join(self.hedef_klasor, uzak_ad)
            if os.path.exists(kaynak):
                shutil.copy2(kaynak, yerel_yol)
                return True
            return False
        except Exception:
            return False


class BulutSenkronizasyon:
    """Bulut senkronizasyon yöneticisi."""

    def __init__(self, veritabani_yolu: str, veritabani=None):
        self.vt_yolu = veritabani_yolu
        self.vt = veritabani
        self.servis: Optional[BulutServisBase] = None
        self.son_senkronizasyon: Optional[datetime] = None
        self.otomatik_sync = False
        self.sync_araligi = 30  # dakika

    def servis_ayarla(self, servis_tipi: str, **kwargs) -> bool:
        """
        Bulut servisini ayarlar.

        Args:
            servis_tipi: 'google', 'dropbox', 'yerel'
        """
        if servis_tipi == 'google':
            self.servis = GoogleDriveServisi(kwargs.get('credentials_path'))
        elif servis_tipi == 'dropbox':
            self.servis = DropboxServisi(kwargs.get('access_token'))
        elif servis_tipi == 'yerel':
            self.servis = YerelKlasorServisi(kwargs.get('hedef_klasor'))
        else:
            return False

        return self.servis.baglan()

    def senkronize_et(self) -> Dict:
        """
        Veritabanını senkronize eder.

        Returns:
            {'basarili': bool, 'mesaj': str}
        """
        if not self.servis or not self.servis.baglantiDurumu:
            return {'basarili': False, 'mesaj': 'Servis bağlı değil'}

        try:
            # Veritabanını yükle
            dosya_adi = os.path.basename(self.vt_yolu)
            basari = self.servis.dosya_yukle(self.vt_yolu, dosya_adi)

            if basari:
                self.son_senkronizasyon = datetime.now()
                if self.vt:
                    self.vt.ayar_kaydet('son_senkronizasyon',
                                       self.son_senkronizasyon.isoformat())
                return {'basarili': True, 'mesaj': 'Senkronizasyon başarılı'}
            else:
                return {'basarili': False, 'mesaj': 'Yükleme başarısız'}

        except Exception as e:
            return {'basarili': False, 'mesaj': str(e)}

    def geri_yukle(self) -> Dict:
        """
        Buluttan geri yükler.

        Returns:
            {'basarili': bool, 'mesaj': str}
        """
        if not self.servis or not self.servis.baglantiDurumu:
            return {'basarili': False, 'mesaj': 'Servis bağlı değil'}

        try:
            dosya_adi = os.path.basename(self.vt_yolu)
            yedek_yol = self.vt_yolu + '.bulut_yedek'

            basari = self.servis.dosya_indir(dosya_adi, yedek_yol)

            if basari and os.path.exists(yedek_yol):
                return {'basarili': True, 'mesaj': 'İndirme başarılı', 'yol': yedek_yol}
            else:
                return {'basarili': False, 'mesaj': 'İndirme başarısız'}

        except Exception as e:
            return {'basarili': False, 'mesaj': str(e)}


class BulutAyarlariDialog(QDialog):
    """Bulut senkronizasyon ayarları dialogu."""

    senkronizasyonYapildi = pyqtSignal()

    def __init__(self, parent=None, bulut_sync=None):
        super().__init__(parent)
        self.bulut_sync = bulut_sync
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Bulut Senkronizasyon')
        self.setMinimumSize(450, 400)

        yerlesim = QVBoxLayout(self)

        # Başlık
        baslik = QLabel('☁️ Bulut Senkronizasyon')
        baslik.setFont(QFont('Segoe UI', 14, QFont.Bold))
        yerlesim.addWidget(baslik)

        # Servis seçimi
        servis_grup = QGroupBox('Servis Seçimi')
        servis_yerlesim = QVBoxLayout(servis_grup)

        self.yerel_radio = QRadioButton('📁 Yerel Klasör (USB, Ağ Sürücüsü)')
        self.yerel_radio.setChecked(True)
        self.yerel_radio.toggled.connect(self._servis_degisti)
        servis_yerlesim.addWidget(self.yerel_radio)

        # Yerel klasör seçimi
        self.yerel_frame = QFrame()
        yerel_yerlesim = QHBoxLayout(self.yerel_frame)
        yerel_yerlesim.setContentsMargins(20, 5, 0, 5)

        self.klasor_input = QLineEdit()
        self.klasor_input.setPlaceholderText('Yedekleme klasörü seçin...')
        yerel_yerlesim.addWidget(self.klasor_input)

        klasor_btn = QPushButton('...')
        klasor_btn.setFixedWidth(40)
        klasor_btn.clicked.connect(self._klasor_sec)
        yerel_yerlesim.addWidget(klasor_btn)

        servis_yerlesim.addWidget(self.yerel_frame)

        self.google_radio = QRadioButton('🔵 Google Drive')
        self.google_radio.setEnabled(GOOGLE_AVAILABLE)
        self.google_radio.toggled.connect(self._servis_degisti)
        servis_yerlesim.addWidget(self.google_radio)

        if not GOOGLE_AVAILABLE:
            google_uyari = QLabel('   (google-api-python-client gerekli)')
            google_uyari.setStyleSheet('color: gray; font-size: 10px;')
            servis_yerlesim.addWidget(google_uyari)

        self.dropbox_radio = QRadioButton('🔷 Dropbox')
        self.dropbox_radio.setEnabled(DROPBOX_AVAILABLE)
        self.dropbox_radio.toggled.connect(self._servis_degisti)
        servis_yerlesim.addWidget(self.dropbox_radio)

        if not DROPBOX_AVAILABLE:
            dropbox_uyari = QLabel('   (dropbox kütüphanesi gerekli)')
            dropbox_uyari.setStyleSheet('color: gray; font-size: 10px;')
            servis_yerlesim.addWidget(dropbox_uyari)

        yerlesim.addWidget(servis_grup)

        # Durum
        durum_grup = QGroupBox('Durum')
        durum_yerlesim = QVBoxLayout(durum_grup)

        self.durum_label = QLabel('Bağlantı durumu: Bağlı değil')
        durum_yerlesim.addWidget(self.durum_label)

        self.son_sync_label = QLabel('Son senkronizasyon: -')
        self.son_sync_label.setStyleSheet('color: gray;')
        durum_yerlesim.addWidget(self.son_sync_label)

        yerlesim.addWidget(durum_grup)

        # İlerleme
        self.ilerleme = QProgressBar()
        self.ilerleme.hide()
        yerlesim.addWidget(self.ilerleme)

        # Butonlar
        buton_yerlesim = QHBoxLayout()

        self.baglan_btn = QPushButton('🔗 Bağlan')
        self.baglan_btn.clicked.connect(self._baglan)
        buton_yerlesim.addWidget(self.baglan_btn)

        self.sync_btn = QPushButton('🔄 Şimdi Senkronize Et')
        self.sync_btn.setEnabled(False)
        self.sync_btn.clicked.connect(self._senkronize)
        buton_yerlesim.addWidget(self.sync_btn)

        self.geri_yukle_btn = QPushButton('📥 Geri Yükle')
        self.geri_yukle_btn.setEnabled(False)
        self.geri_yukle_btn.clicked.connect(self._geri_yukle)
        buton_yerlesim.addWidget(self.geri_yukle_btn)

        yerlesim.addLayout(buton_yerlesim)

        # Kapat
        kapat_btn = QPushButton('Kapat')
        kapat_btn.clicked.connect(self.accept)
        yerlesim.addWidget(kapat_btn)

    def _servis_degisti(self):
        """Servis seçimi değiştiğinde."""
        self.yerel_frame.setVisible(self.yerel_radio.isChecked())

    def _klasor_sec(self):
        """Yerel klasör seçme."""
        klasor = QFileDialog.getExistingDirectory(self, 'Yedekleme Klasörü Seç')
        if klasor:
            self.klasor_input.setText(klasor)

    def _baglan(self):
        """Servise bağlan."""
        if not self.bulut_sync:
            return

        if self.yerel_radio.isChecked():
            klasor = self.klasor_input.text()
            if not klasor:
                QMessageBox.warning(self, 'Uyarı', 'Lütfen bir klasör seçin.')
                return
            basari = self.bulut_sync.servis_ayarla('yerel', hedef_klasor=klasor)
        elif self.google_radio.isChecked():
            basari = self.bulut_sync.servis_ayarla('google')
        elif self.dropbox_radio.isChecked():
            # Dropbox token girişi gerekir
            basari = False
        else:
            return

        if basari:
            self.durum_label.setText('Bağlantı durumu: ✅ Bağlı')
            self.sync_btn.setEnabled(True)
            self.geri_yukle_btn.setEnabled(True)
        else:
            self.durum_label.setText('Bağlantı durumu: ❌ Bağlantı başarısız')

    def _senkronize(self):
        """Senkronizasyon başlat."""
        if not self.bulut_sync:
            return

        self.ilerleme.show()
        self.ilerleme.setRange(0, 0)  # Belirsiz ilerleme

        sonuc = self.bulut_sync.senkronize_et()

        self.ilerleme.hide()

        if sonuc['basarili']:
            self.son_sync_label.setText(
                f"Son senkronizasyon: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            QMessageBox.information(self, 'Başarılı', sonuc['mesaj'])
            self.senkronizasyonYapildi.emit()
        else:
            QMessageBox.warning(self, 'Hata', sonuc['mesaj'])

    def _geri_yukle(self):
        """Buluttan geri yükle."""
        if not self.bulut_sync:
            return

        cevap = QMessageBox.warning(
            self, 'Geri Yükle',
            'Buluttaki yedek mevcut veritabanının üzerine yazılacak.\nDevam etmek istiyor musunuz?',
            QMessageBox.Yes | QMessageBox.No
        )

        if cevap != QMessageBox.Yes:
            return

        sonuc = self.bulut_sync.geri_yukle()

        if sonuc['basarili']:
            QMessageBox.information(
                self, 'Başarılı',
                f"Yedek indirildi: {sonuc.get('yol', '')}\nUygulamayı yeniden başlatın."
            )
        else:
            QMessageBox.warning(self, 'Hata', sonuc['mesaj'])
