# -*- coding: utf-8 -*-
"""
Not Defteri Uygulaması - Git Repo Takip Modülü
GitHub/GitLab repolarındaki değişiklikleri takip eder.

Yazar: Claude AI
Tarih: 2024
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QFrame, QMenu,
    QDialog, QFormLayout, QDialogButtonBox, QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
import urllib.request
import urllib.parse
import json
import ssl
import re


class GitKontrolThread(QThread):
    """Arka planda repo değişikliklerini kontrol eden thread."""
    ilerleme = pyqtSignal(int, str)  # (yüzde, repo_adı)
    repo_guncellendi = pyqtSignal(dict)  # Güncellenen repo bilgisi
    tamamlandi = pyqtSignal()
    hata = pyqtSignal(str)

    def __init__(self, repolar: list):
        super().__init__()
        self.repolar = repolar

    def run(self):
        import time
        toplam = len(self.repolar)
        for i, repo in enumerate(self.repolar):
            try:
                self.ilerleme.emit(int((i / toplam) * 100), repo.get('isim', ''))

                # Rate limit'e takılmamak için istekler arası bekleme
                if i > 0:
                    time.sleep(1.5)

                son_commit = self._son_commit_al(repo['url'])

                if son_commit:
                    eski_hash = repo.get('son_commit_hash', '')
                    yeni_hash = son_commit.get('sha', '')[:7]

                    guncellendi = eski_hash and eski_hash != yeni_hash

                    repo_bilgi = {
                        'id': repo.get('id'),
                        'url': repo['url'],
                        'isim': repo.get('isim', ''),
                        'son_commit_hash': yeni_hash,
                        'son_commit_mesaj': son_commit.get('message', '')[:100],
                        'son_commit_tarih': son_commit.get('date', ''),
                        'son_kontrol': datetime.now().strftime('%d.%m.%Y %H:%M'),
                        'guncellendi': guncellendi
                    }
                    self.repo_guncellendi.emit(repo_bilgi)

            except Exception as e:
                # Rate limit veya diğer hatalar - sessizce devam et
                pass

        self.ilerleme.emit(100, '')
        self.tamamlandi.emit()

    def _son_commit_al(self, url: str) -> dict:
        """GitHub/GitLab reposunun son commit bilgisini alır."""
        # GitHub URL'sini API URL'sine çevir
        # https://github.com/user/repo -> https://api.github.com/repos/user/repo/commits

        github_match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', url)
        gitlab_match = re.match(r'https?://gitlab\.com/([^/]+)/([^/]+)', url)

        if github_match:
            user, repo = github_match.groups()
            repo = repo.replace('.git', '')
            api_url = f'https://api.github.com/repos/{user}/{repo}/commits?per_page=1'
            return self._github_commit_al(api_url)
        elif gitlab_match:
            user, repo = gitlab_match.groups()
            repo = repo.replace('.git', '')
            api_url = f'https://gitlab.com/api/v4/projects/{user}%2F{repo}/repository/commits?per_page=1'
            return self._gitlab_commit_al(api_url)

        return None

    def _github_commit_al(self, api_url: str) -> dict:
        """GitHub API'den son commit bilgisini alır."""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'NotDefteri-GitTakip/1.0',
                'Accept': 'application/vnd.github.v3+json'
            }

            request = urllib.request.Request(api_url, headers=headers)

            with urllib.request.urlopen(request, context=context, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            if data and len(data) > 0:
                commit = data[0]
                return {
                    'sha': commit.get('sha', ''),
                    'message': commit.get('commit', {}).get('message', ''),
                    'date': commit.get('commit', {}).get('author', {}).get('date', ''),
                    'author': commit.get('commit', {}).get('author', {}).get('name', '')
                }
        except Exception:
            # Rate limit veya diğer hatalar - sessizce None döndür
            pass

        return None

    def _gitlab_commit_al(self, api_url: str) -> dict:
        """GitLab API'den son commit bilgisini alır."""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'NotDefteri-GitTakip/1.0'
            }

            request = urllib.request.Request(api_url, headers=headers)

            with urllib.request.urlopen(request, context=context, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            if data and len(data) > 0:
                commit = data[0]
                return {
                    'sha': commit.get('id', ''),
                    'message': commit.get('message', ''),
                    'date': commit.get('created_at', ''),
                    'author': commit.get('author_name', '')
                }
        except Exception:
            # Rate limit veya diğer hatalar - sessizce None döndür
            pass

        return None


class RepoEkleDialog(QDialog):
    """Yeni repo ekleme diyaloğu."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Git Repo Ekle")
        self.setMinimumWidth(500)
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        yerlesim = QVBoxLayout(self)

        # Bilgi etiketi
        bilgi = QLabel("GitHub veya GitLab repo URL'si girin:")
        yerlesim.addWidget(bilgi)

        # Form
        form = QFormLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://github.com/kullanici/repo")
        self.url_input.textChanged.connect(self._url_degisti)
        form.addRow("Repo URL:", self.url_input)

        self.isim_input = QLineEdit()
        self.isim_input.setPlaceholderText("Otomatik algılanacak")
        form.addRow("Görünen İsim:", self.isim_input)

        yerlesim.addLayout(form)

        # Butonlar
        butonlar = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        butonlar.accepted.connect(self.accept)
        butonlar.rejected.connect(self.reject)
        yerlesim.addWidget(butonlar)

    def _url_degisti(self, url: str):
        """URL değiştiğinde ismi otomatik algıla."""
        match = re.match(r'https?://(?:github|gitlab)\.com/([^/]+)/([^/]+)', url)
        if match and not self.isim_input.text():
            user, repo = match.groups()
            repo = repo.replace('.git', '')
            self.isim_input.setPlaceholderText(f"{user}/{repo}")

    def repo_bilgisi_al(self) -> dict:
        """Girilen repo bilgilerini döndürür."""
        url = self.url_input.text().strip()
        isim = self.isim_input.text().strip()

        if not isim:
            match = re.match(r'https?://(?:github|gitlab)\.com/([^/]+)/([^/]+)', url)
            if match:
                user, repo = match.groups()
                isim = f"{user}/{repo}".replace('.git', '')

        return {
            'url': url,
            'isim': isim
        }


class GitTakipWidget(QWidget):
    """Git repo takip widget'ı."""

    def __init__(self, veritabani, parent=None):
        super().__init__(parent)
        self.vt = veritabani
        self._kontrol_thread = None
        self._arayuz_olustur()
        self._repolari_yukle()

    def _arayuz_olustur(self):
        yerlesim = QVBoxLayout(self)
        yerlesim.setContentsMargins(15, 15, 15, 15)
        yerlesim.setSpacing(10)

        # Başlık
        baslik_yerlesim = QHBoxLayout()

        baslik = QLabel("🔄 Git Repo Takip")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold;")
        baslik_yerlesim.addWidget(baslik)

        baslik_yerlesim.addStretch()

        # Kontrol butonu
        self.kontrol_btn = QPushButton("🔄 Kontrol Et")
        self.kontrol_btn.clicked.connect(self._repolari_kontrol_et)
        baslik_yerlesim.addWidget(self.kontrol_btn)

        # Ekle butonu
        self.ekle_btn = QPushButton("+ Repo Ekle")
        self.ekle_btn.clicked.connect(self._repo_ekle)
        baslik_yerlesim.addWidget(self.ekle_btn)

        yerlesim.addLayout(baslik_yerlesim)

        # İlerleme çubuğu
        self.ilerleme = QProgressBar()
        self.ilerleme.setVisible(False)
        yerlesim.addWidget(self.ilerleme)

        # Durum etiketi
        self.durum_label = QLabel("")
        self.durum_label.setStyleSheet("color: gray;")
        yerlesim.addWidget(self.durum_label)

        # Repo listesi
        self.repo_listesi = QListWidget()
        self.repo_listesi.setStyleSheet('''
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        ''')
        self.repo_listesi.setContextMenuPolicy(Qt.CustomContextMenu)
        self.repo_listesi.customContextMenuRequested.connect(self._sag_tik_menusu)
        self.repo_listesi.itemDoubleClicked.connect(self._repo_ac)
        yerlesim.addWidget(self.repo_listesi)

        # Bilgi kutusu
        bilgi_grup = QGroupBox("Bilgi")
        bilgi_yerlesim = QVBoxLayout(bilgi_grup)
        bilgi_label = QLabel(
            "• Repo eklemek için '+ Repo Ekle' butonunu kullanın\n"
            "• Değişiklikleri görmek için 'Kontrol Et' butonuna tıklayın\n"
            "• Repo'yu tarayıcıda açmak için çift tıklayın\n"
            "• Silmek için sağ tıklayın"
        )
        bilgi_label.setStyleSheet("color: gray; font-size: 11px;")
        bilgi_yerlesim.addWidget(bilgi_label)
        yerlesim.addWidget(bilgi_grup)

    def _repolari_yukle(self):
        """Veritabanından repoları yükler."""
        self.repo_listesi.clear()
        repolar = self.vt.git_repolari_getir()

        for repo in repolar:
            self._repo_item_ekle(repo)

        if not repolar:
            self.durum_label.setText("Henüz repo eklenmemiş. '+ Repo Ekle' ile başlayın.")
        else:
            self.durum_label.setText(f"{len(repolar)} repo takip ediliyor")

    def _repo_item_ekle(self, repo: dict):
        """Listeye repo item'ı ekler."""
        item = QListWidgetItem()

        # Güncelleme durumuna göre metin
        isim = repo.get('isim', 'Bilinmeyen Repo')
        son_kontrol = repo.get('son_kontrol', '')
        guncellendi = repo.get('guncellendi', False)
        son_commit_tarih = repo.get('son_commit_tarih', '')

        if guncellendi:
            # Tarihi formatla
            try:
                if son_commit_tarih:
                    if 'T' in son_commit_tarih:
                        dt = datetime.fromisoformat(son_commit_tarih.replace('Z', '+00:00'))
                        tarih_str = dt.strftime('%d.%m.%Y')
                    else:
                        tarih_str = son_commit_tarih
                else:
                    tarih_str = son_kontrol
                metin = f"🟢 {isim}\n   ↳ Güncellendi: {tarih_str}"
            except:
                metin = f"🟢 {isim}\n   ↳ Güncellendi"
            item.setForeground(QColor('#27ae60'))
        else:
            if son_kontrol:
                metin = f"⚪ {isim}\n   ↳ Son kontrol: {son_kontrol}"
            else:
                metin = f"⚪ {isim}\n   ↳ Henüz kontrol edilmedi"
            item.setForeground(QColor('#666'))

        item.setText(metin)
        item.setData(Qt.UserRole, repo)

        # Font ayarı
        font = QFont()
        font.setPointSize(11)
        item.setFont(font)

        self.repo_listesi.addItem(item)

    def _repo_ekle(self):
        """Yeni repo ekler."""
        dialog = RepoEkleDialog(self)
        if dialog.exec_():
            bilgi = dialog.repo_bilgisi_al()

            if not bilgi['url']:
                QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir URL girin.")
                return

            # URL kontrolü
            if not re.match(r'https?://(?:github|gitlab)\.com/', bilgi['url']):
                QMessageBox.warning(
                    self, "Uyarı",
                    "Sadece GitHub ve GitLab URL'leri destekleniyor.\n"
                    "Örnek: https://github.com/kullanici/repo"
                )
                return

            # Veritabanına ekle
            self.vt.git_repo_ekle(bilgi['url'], bilgi['isim'])
            self._repolari_yukle()
            self.durum_label.setText(f"'{bilgi['isim']}' eklendi")

    def _repo_sil(self, repo_id: int):
        """Repo'yu siler."""
        cevap = QMessageBox.question(
            self, "Repo Sil",
            "Bu repo'yu silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )

        if cevap == QMessageBox.Yes:
            self.vt.git_repo_sil(repo_id)
            self._repolari_yukle()

    def _sag_tik_menusu(self, pos):
        """Sağ tık menüsünü gösterir."""
        item = self.repo_listesi.itemAt(pos)
        if not item:
            return

        repo = item.data(Qt.UserRole)

        menu = QMenu(self)

        ac_action = menu.addAction("🌐 Tarayıcıda Aç")
        ac_action.triggered.connect(lambda: self._repo_ac(item))

        menu.addSeparator()

        sil_action = menu.addAction("🗑️ Sil")
        sil_action.triggered.connect(lambda: self._repo_sil(repo.get('id')))

        menu.exec_(self.repo_listesi.mapToGlobal(pos))

    def _repo_ac(self, item: QListWidgetItem):
        """Repo'yu tarayıcıda açar."""
        repo = item.data(Qt.UserRole)
        if repo and repo.get('url'):
            import webbrowser
            webbrowser.open(repo['url'])

    def _repolari_kontrol_et(self):
        """Tüm repoları kontrol eder."""
        repolar = self.vt.git_repolari_getir()

        if not repolar:
            QMessageBox.information(self, "Bilgi", "Kontrol edilecek repo yok.")
            return

        self.kontrol_btn.setEnabled(False)
        self.ilerleme.setVisible(True)
        self.ilerleme.setValue(0)

        self._kontrol_thread = GitKontrolThread(repolar)
        self._kontrol_thread.ilerleme.connect(self._ilerleme_guncelle)
        self._kontrol_thread.repo_guncellendi.connect(self._repo_guncellendi)
        self._kontrol_thread.tamamlandi.connect(self._kontrol_tamamlandi)
        self._kontrol_thread.start()

    def _ilerleme_guncelle(self, yuzde: int, repo_adi: str):
        """İlerleme çubuğunu günceller."""
        self.ilerleme.setValue(yuzde)
        if repo_adi:
            self.durum_label.setText(f"Kontrol ediliyor: {repo_adi}")

    def _repo_guncellendi(self, repo_bilgi: dict):
        """Repo güncellendiğinde çağrılır."""
        self.vt.git_repo_guncelle(
            repo_bilgi['id'],
            repo_bilgi['son_commit_hash'],
            repo_bilgi['son_kontrol'],
            repo_bilgi.get('guncellendi', False)
        )

    def _kontrol_tamamlandi(self):
        """Kontrol tamamlandığında çağrılır."""
        self.kontrol_btn.setEnabled(True)
        self.ilerleme.setVisible(False)
        self._repolari_yukle()
        self.durum_label.setText(f"Son kontrol: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    def baslangicta_kontrol_et(self):
        """Uygulama başladığında otomatik kontrol yapar."""
        # 2 saniye sonra kontrol et (UI yüklensin)
        QTimer.singleShot(2000, self._baslangic_kontrolu)

    def _baslangic_kontrolu(self):
        """Başlangıç kontrolü - sessiz mod."""
        repolar = self.vt.git_repolari_getir()
        if repolar:
            self.kontrol_btn.setEnabled(False)
            self.ilerleme.setVisible(True)
            self.ilerleme.setValue(0)
            self.durum_label.setText("Başlangıç kontrolü yapılıyor...")

            self._kontrol_thread = GitKontrolThread(repolar)
            self._kontrol_thread.ilerleme.connect(self._ilerleme_guncelle)
            self._kontrol_thread.repo_guncellendi.connect(self._repo_guncellendi)
            self._kontrol_thread.tamamlandi.connect(self._kontrol_tamamlandi)
            self._kontrol_thread.start()
