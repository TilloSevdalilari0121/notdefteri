# -*- coding: utf-8 -*-
"""
Not Defteri - Web Clipper Modülü
Web sayfalarından içerik kaydetme.
"""

import re
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse, urljoin
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QFrame, QProgressBar,
    QCheckBox, QGroupBox, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Opsiyonel: BeautifulSoup
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Opsiyonel: Readability
try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False


class WebSayfaIndirici(QThread):
    """Web sayfasını indiren thread."""

    tamamlandi = pyqtSignal(str, str)  # html, url
    hata = pyqtSignal(str)
    ilerleme = pyqtSignal(int)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        """Sayfayı indirir."""
        try:
            import urllib.request
            import ssl

            self.ilerleme.emit(20)

            # SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # User agent ayarla
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            request = urllib.request.Request(self.url, headers=headers)

            self.ilerleme.emit(40)

            with urllib.request.urlopen(request, context=context, timeout=30) as response:
                self.ilerleme.emit(60)
                html = response.read().decode('utf-8', errors='ignore')
                self.ilerleme.emit(100)
                self.tamamlandi.emit(html, self.url)

        except Exception as e:
            self.hata.emit(str(e))


class IcerikCikarici:
    """Web sayfasından içerik çıkarır."""

    @staticmethod
    def baslik_cikar(html: str) -> str:
        """Sayfa başlığını çıkarır."""
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            if title:
                return title.get_text().strip()

            # Open Graph title
            og_title = soup.find('meta', property='og:title')
            if og_title:
                return og_title.get('content', '').strip()
        else:
            # Regex ile başlık çıkar
            match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return 'Başlıksız Sayfa'

    @staticmethod
    def icerik_cikar(html: str, mod: str = 'tam', url: str = '') -> str:
        """
        Sayfa içeriğini çıkarır.

        Args:
            html: HTML içeriği
            mod: 'tam', 'makale', 'basit'
            url: Sayfa URL'i (site-specific işleme için)
        """
        if mod == 'makale' and READABILITY_AVAILABLE:
            try:
                doc = Document(html)
                return doc.summary()
            except:
                pass

        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, 'html.parser')

            # GitHub özel işleme
            if 'github.com' in url:
                return IcerikCikarici._github_icerik_cikar(soup, mod, url)

            # Script ve style etiketlerini kaldır
            for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
                script.decompose()

            # Resimlerin URL'lerini mutlak yap
            if url:
                IcerikCikarici._resimleri_duzelt(soup, url)

            if mod == 'basit':
                # Sadece metin
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                return '\n'.join(chunk for chunk in chunks if chunk)

            elif mod == 'makale':
                # Article veya main içeriği bul
                article = (
                    soup.find('article') or
                    soup.find('main') or
                    soup.find(class_=re.compile(r'content|article|post|entry|readme', re.IGNORECASE)) or
                    soup.find(id=re.compile(r'content|article|post|entry|readme', re.IGNORECASE))
                )
                if article:
                    # Gereksiz elementleri kaldır
                    for tag in article.find_all(['script', 'style', 'nav', 'footer', 'noscript']):
                        tag.decompose()
                    return IcerikCikarici._html_temizle(str(article))

            # Tam HTML (temizlenmiş)
            body = soup.find('body')
            if body:
                return IcerikCikarici._html_temizle(str(body))
            return IcerikCikarici._html_temizle(str(soup))

        else:
            # Basit regex temizleme
            # Script ve style kaldır
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

            if mod == 'basit':
                # HTML etiketlerini kaldır
                text = re.sub(r'<[^>]+>', '', html)
                text = re.sub(r'\s+', ' ', text)
                return text.strip()

            return html

    @staticmethod
    def _resimleri_duzelt(soup, base_url: str):
        """Resimlerin URL'lerini mutlak URL'lere çevirir."""
        if not base_url:
            return

        # Base domain'i çıkar
        parsed = urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"

        for img in soup.find_all('img'):
            src = img.get('src', '')

            # Boş src atla
            if not src:
                # data-src veya data-canonical-src dene
                src = img.get('data-src') or img.get('data-canonical-src') or ''
                if src:
                    img['src'] = src

            if not src:
                continue

            # GitHub camo proxy URL'lerini düzelt - data-canonical-src varsa onu kullan
            canonical = img.get('data-canonical-src')
            if canonical and 'camo.githubusercontent.com' in src:
                img['src'] = canonical
                continue

            # Zaten mutlak URL mi?
            if src.startswith(('http://', 'https://', 'data:')):
                continue

            # Relative URL'yi absolute yap
            if src.startswith('/'):
                # Root-relative URL (örn: /microsoft/agent-lightning/raw/...)
                absolute_url = base_domain + src
            else:
                # Path-relative URL
                absolute_url = urljoin(base_url, src)

            img['src'] = absolute_url

        # a tag'lerindeki linkleri de düzelt
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if href and not href.startswith(('http://', 'https://', '#', 'mailto:', 'javascript:')):
                if href.startswith('/'):
                    a['href'] = base_domain + href
                else:
                    a['href'] = urljoin(base_url, href)

    @staticmethod
    def _github_icerik_cikar(soup: 'BeautifulSoup', mod: str, base_url: str = '') -> str:
        """GitHub sayfaları için özel içerik çıkarma."""
        # README içeriğini bul
        readme = (
            soup.find('article', class_=re.compile(r'markdown-body', re.IGNORECASE)) or
            soup.find('div', class_=re.compile(r'markdown-body', re.IGNORECASE)) or
            soup.find(id='readme') or
            soup.find('article')
        )

        if readme:
            # Gereksiz elementleri kaldır
            for tag in readme.find_all(['script', 'style', 'clipboard-copy', 'template', 'tool-tip']):
                tag.decompose()

            # Resimlerin URL'lerini mutlak yap
            IcerikCikarici._resimleri_duzelt(readme, base_url)

            # data-* attribute'ları temizle
            for tag in readme.find_all(True):
                attrs_to_remove = [attr for attr in tag.attrs if attr.startswith('data-')]
                for attr in attrs_to_remove:
                    del tag[attr]

            if mod == 'basit':
                text = readme.get_text()
                lines = (line.strip() for line in text.splitlines())
                return '\n'.join(line for line in lines if line)

            # HTML içeriği
            html_content = str(readme)

            # Stil ekle (markdown-body için)
            styled_html = f'''
<style>
    .markdown-body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 14px;
        line-height: 1.6;
        word-wrap: break-word;
    }}
    .markdown-body h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
    .markdown-body h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
    .markdown-body h3 {{ font-size: 1.25em; }}
    .markdown-body code {{
        background-color: rgba(175,184,193,0.2);
        padding: 0.2em 0.4em;
        border-radius: 6px;
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
        font-size: 85%;
    }}
    .markdown-body pre {{
        background-color: #f6f8fa;
        padding: 16px;
        border-radius: 6px;
        overflow: auto;
    }}
    .markdown-body pre code {{ background: none; padding: 0; }}
    .markdown-body ul, .markdown-body ol {{ padding-left: 2em; }}
    .markdown-body li {{ margin: 0.25em 0; }}
    .markdown-body blockquote {{
        color: #57606a;
        border-left: 4px solid #d0d7de;
        padding: 0 1em;
        margin: 0;
    }}
    .markdown-body img {{ max-width: 100%; height: auto; }}
    .markdown-body a {{ color: #0969da; text-decoration: none; }}
    .markdown-body a:hover {{ text-decoration: underline; }}
    .markdown-body table {{ border-collapse: collapse; width: 100%; }}
    .markdown-body th, .markdown-body td {{ border: 1px solid #d0d7de; padding: 6px 13px; }}
    .markdown-body th {{ background-color: #f6f8fa; font-weight: 600; }}
</style>
<div class="markdown-body">
{html_content}
</div>
'''
            return styled_html

        # README bulunamazsa genel makale çıkarma
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            script.decompose()

        if mod == 'basit':
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            return '\n'.join(line for line in lines if line)

        body = soup.find('body')
        return str(body) if body else str(soup)

    @staticmethod
    def _html_temizle(html: str) -> str:
        """HTML'i temizler ve düzenler."""
        if not BS4_AVAILABLE:
            return html

        soup = BeautifulSoup(html, 'html.parser')

        # Boş tag'leri kaldır
        for tag in soup.find_all():
            if len(tag.get_text(strip=True)) == 0 and tag.name not in ['img', 'br', 'hr', 'input']:
                if not tag.find_all(['img', 'br', 'hr', 'input']):
                    tag.decompose()

        # Gereksiz attribute'ları temizle
        allowed_attrs = {'href', 'src', 'alt', 'title', 'class', 'id', 'width', 'height', 'style'}
        for tag in soup.find_all(True):
            attrs = dict(tag.attrs)
            for attr in attrs:
                if attr not in allowed_attrs:
                    del tag[attr]

        return str(soup)

    @staticmethod
    def resimler_cikar(html: str, base_url: str) -> list:
        """Sayfa resimlerini çıkarır."""
        resimler = []

        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    # Relative URL'leri absolute yap
                    absolute_url = urljoin(base_url, src)
                    alt = img.get('alt', '')
                    resimler.append({'url': absolute_url, 'alt': alt})
        else:
            # Regex ile
            for match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE):
                src = match.group(1)
                absolute_url = urljoin(base_url, src)
                resimler.append({'url': absolute_url, 'alt': ''})

        return resimler

    @staticmethod
    def meta_bilgileri_cikar(html: str) -> Dict:
        """Meta bilgilerini çıkarır."""
        meta = {
            'description': '',
            'keywords': '',
            'author': '',
            'og_image': '',
            'site_name': ''
        }

        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, 'html.parser')

            # Description
            desc = soup.find('meta', attrs={'name': 'description'})
            if desc:
                meta['description'] = desc.get('content', '')

            # Keywords
            keywords = soup.find('meta', attrs={'name': 'keywords'})
            if keywords:
                meta['keywords'] = keywords.get('content', '')

            # Author
            author = soup.find('meta', attrs={'name': 'author'})
            if author:
                meta['author'] = author.get('content', '')

            # Open Graph
            og_image = soup.find('meta', property='og:image')
            if og_image:
                meta['og_image'] = og_image.get('content', '')

            og_site = soup.find('meta', property='og:site_name')
            if og_site:
                meta['site_name'] = og_site.get('content', '')

        return meta


class WebClipperDialog(QDialog):
    """Web clipper dialogu."""

    notOlusturuldu = pyqtSignal(str, str)  # baslik, icerik

    def __init__(self, parent=None):
        super().__init__(parent)
        self.indirici = None
        self.html_icerik = None
        self.sayfa_url = None
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('🌐 Web Clipper')
        self.setMinimumSize(600, 500)

        yerlesim = QVBoxLayout(self)

        # URL girişi
        url_grup = QGroupBox('Web Sayfası')
        url_yerlesim = QHBoxLayout(url_grup)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://example.com/sayfa')
        self.url_input.returnPressed.connect(self._sayfayi_indir)
        url_yerlesim.addWidget(self.url_input)

        self.indir_btn = QPushButton('📥 İndir')
        self.indir_btn.clicked.connect(self._sayfayi_indir)
        url_yerlesim.addWidget(self.indir_btn)

        # Panodan yapıştır
        yapistir_btn = QPushButton('📋')
        yapistir_btn.setToolTip('Panodan URL yapıştır')
        yapistir_btn.clicked.connect(self._panodan_yapistir)
        url_yerlesim.addWidget(yapistir_btn)

        yerlesim.addWidget(url_grup)

        # İlerleme
        self.ilerleme = QProgressBar()
        self.ilerleme.setVisible(False)
        yerlesim.addWidget(self.ilerleme)

        # Seçenekler
        secenekler_grup = QGroupBox('Kaydetme Seçenekleri')
        secenekler_yerlesim = QVBoxLayout(secenekler_grup)

        # İçerik modu
        mod_yerlesim = QHBoxLayout()
        mod_yerlesim.addWidget(QLabel('İçerik Modu:'))

        self.mod_combo = QComboBox()
        self.mod_combo.addItems(['Tam Sayfa', 'Sadece Makale', 'Düz Metin'])
        self.mod_combo.currentIndexChanged.connect(self._onizleme_guncelle)
        mod_yerlesim.addWidget(self.mod_combo)
        mod_yerlesim.addStretch()

        secenekler_yerlesim.addLayout(mod_yerlesim)

        # Ekstra seçenekler
        self.resim_dahil = QCheckBox('Resimleri dahil et')
        self.resim_dahil.setChecked(True)
        secenekler_yerlesim.addWidget(self.resim_dahil)

        self.kaynak_ekle = QCheckBox('Kaynak URL ekle')
        self.kaynak_ekle.setChecked(True)
        secenekler_yerlesim.addWidget(self.kaynak_ekle)

        self.tarih_ekle = QCheckBox('Kaydetme tarihini ekle')
        self.tarih_ekle.setChecked(True)
        secenekler_yerlesim.addWidget(self.tarih_ekle)

        yerlesim.addWidget(secenekler_grup)

        # Başlık düzenleme
        baslik_yerlesim = QHBoxLayout()
        baslik_yerlesim.addWidget(QLabel('Başlık:'))

        self.baslik_input = QLineEdit()
        self.baslik_input.setPlaceholderText('Not başlığı')
        baslik_yerlesim.addWidget(self.baslik_input)

        yerlesim.addLayout(baslik_yerlesim)

        # Önizleme
        onizleme_label = QLabel('Önizleme:')
        onizleme_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        yerlesim.addWidget(onizleme_label)

        self.onizleme = QTextEdit()
        self.onizleme.setReadOnly(True)
        self.onizleme.setStyleSheet('''
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        ''')
        yerlesim.addWidget(self.onizleme)

        # Meta bilgiler
        self.meta_label = QLabel('')
        self.meta_label.setStyleSheet('color: gray; font-size: 11px;')
        self.meta_label.setWordWrap(True)
        yerlesim.addWidget(self.meta_label)

        # Butonlar
        buton_yerlesim = QHBoxLayout()
        buton_yerlesim.addStretch()

        iptal_btn = QPushButton('İptal')
        iptal_btn.clicked.connect(self.reject)
        buton_yerlesim.addWidget(iptal_btn)

        self.kaydet_btn = QPushButton('📝 Not Olarak Kaydet')
        self.kaydet_btn.clicked.connect(self._kaydet)
        self.kaydet_btn.setEnabled(False)
        buton_yerlesim.addWidget(self.kaydet_btn)

        yerlesim.addLayout(buton_yerlesim)

        # Uyarılar
        if not BS4_AVAILABLE:
            uyari = QLabel('⚠️ BeautifulSoup yüklü değil. Gelişmiş içerik çıkarma devre dışı.')
            uyari.setStyleSheet('color: orange; font-size: 11px;')
            yerlesim.addWidget(uyari)

    def _panodan_yapistir(self):
        """Panodan URL yapıştırır."""
        pano = QApplication.clipboard()
        metin = pano.text()

        if metin and (metin.startswith('http://') or metin.startswith('https://')):
            self.url_input.setText(metin)

    def _sayfayi_indir(self):
        """Web sayfasını indirir."""
        url = self.url_input.text().strip()

        if not url:
            return

        # URL'yi düzelt
        if not url.startswith('http'):
            url = 'https://' + url
            self.url_input.setText(url)

        # URL doğrulama
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Geçersiz URL")
        except:
            QMessageBox.warning(self, 'Hata', 'Geçersiz URL formatı!')
            return

        # İndiriciyi başlat
        self.ilerleme.setVisible(True)
        self.ilerleme.setValue(0)
        self.indir_btn.setEnabled(False)

        self.indirici = WebSayfaIndirici(url)
        self.indirici.tamamlandi.connect(self._indirme_tamamlandi)
        self.indirici.hata.connect(self._indirme_hatasi)
        self.indirici.ilerleme.connect(self.ilerleme.setValue)
        self.indirici.start()

    def _indirme_tamamlandi(self, html: str, url: str):
        """İndirme tamamlandığında."""
        self.html_icerik = html
        self.sayfa_url = url

        self.ilerleme.setVisible(False)
        self.indir_btn.setEnabled(True)
        self.kaydet_btn.setEnabled(True)

        # Başlığı çıkar
        baslik = IcerikCikarici.baslik_cikar(html)
        self.baslik_input.setText(baslik)

        # Meta bilgileri
        meta = IcerikCikarici.meta_bilgileri_cikar(html)
        meta_text = []
        if meta['site_name']:
            meta_text.append(f"Site: {meta['site_name']}")
        if meta['author']:
            meta_text.append(f"Yazar: {meta['author']}")
        if meta['description']:
            meta_text.append(f"Açıklama: {meta['description'][:100]}...")
        self.meta_label.setText(' | '.join(meta_text))

        # Önizleme
        self._onizleme_guncelle()

    def _indirme_hatasi(self, hata: str):
        """İndirme hatasında."""
        self.ilerleme.setVisible(False)
        self.indir_btn.setEnabled(True)

        QMessageBox.critical(self, 'Hata', f'Sayfa indirilemedi:\n{hata}')

    def _onizleme_guncelle(self):
        """Önizlemeyi günceller."""
        if not self.html_icerik:
            return

        mod_index = self.mod_combo.currentIndex()
        mod = ['tam', 'makale', 'basit'][mod_index]

        icerik = IcerikCikarici.icerik_cikar(self.html_icerik, mod, self.sayfa_url or '')

        if mod == 'basit':
            self.onizleme.setPlainText(icerik[:2000] + ('...' if len(icerik) > 2000 else ''))
        else:
            self.onizleme.setHtml(icerik[:10000])

    def _kaydet(self):
        """Notu kaydeder."""
        if not self.html_icerik:
            return

        baslik = self.baslik_input.text().strip() or 'Web Sayfası'

        mod_index = self.mod_combo.currentIndex()
        mod = ['tam', 'makale', 'basit'][mod_index]

        icerik = IcerikCikarici.icerik_cikar(self.html_icerik, mod, self.sayfa_url or '')

        # Ek bilgiler
        ek_bilgiler = []

        if self.kaynak_ekle.isChecked() and self.sayfa_url:
            ek_bilgiler.append(f'<p><strong>Kaynak:</strong> <a href="{self.sayfa_url}">{self.sayfa_url}</a></p>')

        if self.tarih_ekle.isChecked():
            from datetime import datetime
            tarih = datetime.now().strftime('%Y-%m-%d %H:%M')
            ek_bilgiler.append(f'<p><strong>Kaydedilme Tarihi:</strong> {tarih}</p>')

        if ek_bilgiler:
            ek_html = '<hr>' + ''.join(ek_bilgiler)
            if mod == 'basit':
                icerik = f'<p>{icerik}</p>' + ek_html
            else:
                icerik = icerik + ek_html

        self.notOlusturuldu.emit(baslik, icerik)
        self.accept()


class WebClipperYoneticisi:
    """Web clipper yöneticisi."""

    def __init__(self, veritabani=None):
        self.vt = veritabani

    def dialog_ac(self, parent=None) -> Optional[Tuple[str, str]]:
        """
        Web clipper dialogunu açar.

        Returns:
            (baslik, icerik) veya None
        """
        dialog = WebClipperDialog(parent)

        sonuc = None

        def not_olusturuldu(baslik, icerik):
            nonlocal sonuc
            sonuc = (baslik, icerik)

        dialog.notOlusturuldu.connect(not_olusturuldu)

        if dialog.exec_() == QDialog.Accepted:
            return sonuc

        return None

    def url_kaydet(self, url: str) -> Optional[int]:
        """
        URL'yi doğrudan kaydeder.

        Returns:
            Oluşturulan not ID veya None
        """
        if not self.vt:
            return None

        import urllib.request
        import ssl

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request, context=context, timeout=30) as response:
                html = response.read().decode('utf-8', errors='ignore')

            baslik = IcerikCikarici.baslik_cikar(html)
            icerik = IcerikCikarici.icerik_cikar(html, 'makale', url)

            # Kaynak ekle
            from datetime import datetime
            tarih = datetime.now().strftime('%Y-%m-%d %H:%M')
            icerik += f'<hr><p><strong>Kaynak:</strong> <a href="{url}">{url}</a></p>'
            icerik += f'<p><strong>Kaydedilme Tarihi:</strong> {tarih}</p>'

            # Veritabanına kaydet
            not_id = self.vt.not_ekle(
                baslik=f"🌐 {baslik}",
                icerik=IcerikCikarici.icerik_cikar(html, 'basit', url),
                zengin_icerik=icerik
            )

            return not_id

        except Exception as e:
            print(f"URL kaydetme hatası: {e}")
            return None


class HizliKlipWidget(QFrame):
    """Hızlı web klibi widget'ı."""

    notOlusturuldu = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Arayüzü oluşturur."""
        self.setStyleSheet('''
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        ''')

        yerlesim = QHBoxLayout(self)
        yerlesim.setContentsMargins(10, 5, 10, 5)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('URL yapıştır ve Enter tuşuna bas...')
        self.url_input.returnPressed.connect(self._hizli_kaydet)
        yerlesim.addWidget(self.url_input)

        kaydet_btn = QPushButton('📥')
        kaydet_btn.setToolTip('Hızlı kaydet')
        kaydet_btn.clicked.connect(self._hizli_kaydet)
        yerlesim.addWidget(kaydet_btn)

    def _hizli_kaydet(self):
        """URL'yi hızlıca kaydeder."""
        url = self.url_input.text().strip()

        if not url:
            return

        if not url.startswith('http'):
            url = 'https://' + url

        # Basit indirme
        try:
            import urllib.request
            import ssl

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request, context=context, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')

            baslik = IcerikCikarici.baslik_cikar(html)
            icerik = IcerikCikarici.icerik_cikar(html, 'makale', url)

            # Kaynak ekle
            from datetime import datetime
            tarih = datetime.now().strftime('%Y-%m-%d %H:%M')
            icerik += f'<hr><p><strong>Kaynak:</strong> <a href="{url}">{url}</a></p>'
            icerik += f'<p><strong>Kaydedilme Tarihi:</strong> {tarih}</p>'

            self.notOlusturuldu.emit(f"🌐 {baslik}", icerik)
            self.url_input.clear()

        except Exception as e:
            QMessageBox.warning(self, 'Hata', f'Sayfa kaydedilemedi:\n{str(e)}')
