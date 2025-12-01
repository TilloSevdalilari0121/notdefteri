# -*- coding: utf-8 -*-
"""
Not Defteri Uygulaması - Özel Bileşenler Modülü
Zengin metin editörü ve diğer özel widget'lar.

Yazar: Claude AI
Tarih: 2024
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QToolBar,
    QAction, QFontComboBox, QSpinBox, QColorDialog, QMenu,
    QLabel, QPushButton, QFrame, QSizePolicy, QListWidget,
    QListWidgetItem, QDialog, QLineEdit, QFormLayout,
    QDialogButtonBox, QDateTimeEdit, QComboBox, QMessageBox,
    QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QDateTime, QUrl, QByteArray
from PyQt5.QtGui import (
    QFont, QTextCharFormat, QColor, QTextCursor, QIcon,
    QPainter, QBrush, QPen, QPixmap, QTextListFormat,
    QTextBlockFormat, QKeySequence, QImage, QTextDocument
)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from datetime import datetime
from stiller import RENK_PALETI, KATEGORI_IKONLARI
import urllib.request
import urllib.parse
import ssl
import re
import os
import hashlib


class HariciResimYukleyiciTextEdit(QTextEdit):
    """Harici URL'lerden resim yükleyebilen QTextEdit."""

    # Çeviri istendi sinyali (ana uygulama bağlanacak)
    ceviriIstendi = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._resim_cache = {}  # URL -> QImage cache
        self._yuklenen_resimler = set()
        self._yukleme_devam = False
        self._resim_klasoru = None
        self._url_to_local = {}  # URL -> yerel dosya yolu mapping

        # Sağ tık menüsü için context menu policy
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._sag_tik_menusu_goster)

    def _sag_tik_menusu_goster(self, pos):
        """Sağ tık menüsünü gösterir."""
        menu = self.createStandardContextMenu()

        # Ayraç ekle
        menu.addSeparator()

        # Çeviri aksiyonu
        ceviri_action = QAction('Seçili Metni Çevir', self)
        ceviri_action.setShortcut('Ctrl+Shift+T')

        # Seçili metin varsa aktif, yoksa tüm metni çevir olarak değiştir
        cursor = self.textCursor()
        if cursor.hasSelection():
            ceviri_action.setText('Seçili Metni Çevir')
            ceviri_action.triggered.connect(lambda: self.ceviriIstendi.emit(cursor.selectedText()))
        else:
            ceviri_action.setText('Tüm İçeriği Çevir')
            ceviri_action.triggered.connect(lambda: self.ceviriIstendi.emit(self.toPlainText()))

        menu.addAction(ceviri_action)

        # Hızlı çeviri alt menüsü
        hizli_ceviri_menu = menu.addMenu('Hızlı Çeviri')

        # İngilizce -> Türkçe
        en_tr_action = QAction('İngilizce → Türkçe', self)
        en_tr_action.triggered.connect(lambda: self._hizli_cevir('en', 'tr'))
        hizli_ceviri_menu.addAction(en_tr_action)

        # Türkçe -> İngilizce
        tr_en_action = QAction('Türkçe → İngilizce', self)
        tr_en_action.triggered.connect(lambda: self._hizli_cevir('tr', 'en'))
        hizli_ceviri_menu.addAction(tr_en_action)

        # Otomatik -> Türkçe
        auto_tr_action = QAction('Otomatik → Türkçe', self)
        auto_tr_action.triggered.connect(lambda: self._hizli_cevir('auto', 'tr'))
        hizli_ceviri_menu.addAction(auto_tr_action)

        menu.exec_(self.mapToGlobal(pos))

    def _hizli_cevir(self, kaynak: str, hedef: str):
        """Seçili metni hızlıca çevirir (HTML formatını koruyarak)."""
        try:
            from moduller.ceviri import CeviriYoneticisi

            cursor = self.textCursor()
            if cursor.hasSelection():
                # Seçili metin - sadece seçili kısmı çevir
                metin = cursor.selectedText()
                if metin.strip():
                    ceviri = CeviriYoneticisi.hizli_cevir(metin, kaynak, hedef)
                    if ceviri and ceviri != metin:
                        cursor.insertText(ceviri)
            else:
                # Tüm içerik - HTML formatını koru
                metin = self.toPlainText()
                if metin.strip():
                    html_icerik = self.toHtml()
                    ceviri = CeviriYoneticisi.hizli_cevir(metin, kaynak, hedef)
                    if ceviri and ceviri != metin:
                        # HTML içindeki metinleri değiştir
                        cevrilmis_html = self._html_metin_degistir(html_icerik, metin, ceviri)
                        self.setHtml(cevrilmis_html)
        except ImportError:
            QMessageBox.warning(self, "Uyarı", "Çeviri modülü yüklenemedi.")
        except Exception as e:
            print(f"Hızlı çeviri hatası: {e}")

    def _html_metin_degistir(self, html_icerik: str, orijinal: str, ceviri: str) -> str:
        """HTML içindeki metinleri satır satır değiştirir."""
        orijinal_satirlar = orijinal.split('\n')
        ceviri_satirlar = ceviri.split('\n')

        sonuc = html_icerik
        for orig, cev in zip(orijinal_satirlar, ceviri_satirlar):
            orig = orig.strip()
            cev = cev.strip()
            if orig and cev and orig != cev:
                # HTML tag'leri arasındaki metni değiştir
                orijinal_escaped = re.escape(orig)
                # Replacement string'de backslash'ları escape et
                cev_escaped = cev.replace('\\', '\\\\')
                sonuc = re.sub(
                    r'(>)(' + orijinal_escaped + r')(<)',
                    r'\g<1>' + cev_escaped + r'\g<3>',
                    sonuc
                )
        return sonuc

    def set_resim_klasoru(self, klasor: str):
        """Resimlerin kaydedileceği klasörü ayarlar."""
        self._resim_klasoru = klasor
        if klasor:
            os.makedirs(klasor, exist_ok=True)

    def setHtml(self, html: str):
        """HTML içeriğini ayarlar ve resimleri yükler."""
        # Önce HTML'i ayarla
        super().setHtml(html)

        # Sonra resimleri yükle (recursive çağrıları engelle)
        if not self._yukleme_devam:
            self._resimleri_yukle()

    def _resimleri_yukle(self):
        """HTML içindeki harici resimleri yükler veya yerel dosyaları kontrol eder."""
        doc = self.document()
        html = doc.toHtml()

        # img src URL'lerini bul
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'

        for match in re.finditer(img_pattern, html, re.IGNORECASE):
            url = match.group(1)

            # Yerel dosya mı kontrol et (file:/// ile başlıyorsa)
            if url.startswith('file:///'):
                yerel_yol = QUrl(url).toLocalFile()
                if os.path.exists(yerel_yol):
                    # Yerel dosyayı yükle
                    image = QImage(yerel_yol)
                    if not image.isNull():
                        self._resim_cache[url] = image
                        doc.addResource(QTextDocument.ImageResource, QUrl(url), image)
                continue

            # Harici URL mi kontrol et
            if url.startswith(('http://', 'https://')) and url not in self._yuklenen_resimler:
                self._yuklenen_resimler.add(url)
                self._resim_indir(url)

    def _url_encode(self, url: str) -> str:
        """URL'deki özel karakterleri encode eder."""
        # URL'yi parçala
        parsed = urllib.parse.urlparse(url)

        # Path'i encode et (boşlukları %20'ye çevir vs.)
        encoded_path = urllib.parse.quote(parsed.path, safe='/:@')

        # Query string'i encode et
        encoded_query = urllib.parse.quote(parsed.query, safe='=&')

        # Yeniden birleştir
        encoded_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            encoded_path,
            parsed.params,
            encoded_query,
            parsed.fragment
        ))

        return encoded_url

    def _resim_indir(self, url: str):
        """Resmi indirir, yerel olarak kaydeder ve document'e ekler."""
        try:
            # Daha önce indirilip kaydedilmiş mi kontrol et
            if url in self._url_to_local:
                yerel_yol = self._url_to_local[url]
                if os.path.exists(yerel_yol):
                    image = QImage(yerel_yol)
                    if not image.isNull():
                        self._resim_cache[url] = image
                        doc = self.document()
                        doc.addResource(QTextDocument.ImageResource, QUrl(url), image)
                        return

            # URL'yi encode et
            encoded_url = self._url_encode(url)

            # SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            request = urllib.request.Request(encoded_url, headers=headers)

            with urllib.request.urlopen(request, context=context, timeout=10) as response:
                data = response.read()
                content_type = response.headers.get('Content-Type', '')

            image = None

            # SVG dosyaları için özel işlem
            if url.endswith('.svg') or 'svg' in content_type:
                try:
                    from PyQt5.QtSvg import QSvgRenderer

                    renderer = QSvgRenderer(QByteArray(data))
                    if renderer.isValid():
                        # SVG'yi QImage'a dönüştür
                        size = renderer.defaultSize()
                        # Maksimum boyut sınırla
                        max_width = 800
                        if size.width() > max_width:
                            ratio = max_width / size.width()
                            size.setWidth(int(size.width() * ratio))
                            size.setHeight(int(size.height() * ratio))

                        image = QImage(size, QImage.Format_ARGB32)
                        image.fill(Qt.transparent)
                        painter = QPainter(image)
                        renderer.render(painter)
                        painter.end()
                except ImportError:
                    pass  # QtSvg yüklü değil

            # Normal resim formatları (PNG, JPG, GIF, vb.)
            if image is None or image.isNull():
                image = QImage()
                image.loadFromData(data)

            if image and not image.isNull():
                # Yerel klasöre kaydet
                yerel_yol = self._resmi_yerel_kaydet(url, image)

                # Document'e resource olarak ekle
                doc = self.document()
                doc.addResource(QTextDocument.ImageResource, QUrl(url), image)

                # Cache'e ekle
                self._resim_cache[url] = image

                # HTML'i yeniden yükle (resimlerin görünmesi için)
                self._html_yenile()

        except Exception as e:
            print(f"Resim yükleme hatası ({url[:50]}...): {e}")

    def _resmi_yerel_kaydet(self, url: str, image: QImage) -> str:
        """Resmi yerel klasöre kaydeder ve yolu döndürür."""
        if not self._resim_klasoru:
            return None

        try:
            # URL'den benzersiz dosya adı oluştur
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            zaman = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Uzantıyı belirle
            if url.endswith('.svg'):
                uzanti = 'png'  # SVG'ler PNG olarak kaydedilir
            elif url.endswith('.gif'):
                uzanti = 'gif'
            elif url.endswith('.jpg') or url.endswith('.jpeg'):
                uzanti = 'jpg'
            else:
                uzanti = 'png'

            dosya_adi = f'web_{zaman}_{url_hash}.{uzanti}'
            yerel_yol = os.path.join(self._resim_klasoru, dosya_adi)

            # Resmi kaydet
            image.save(yerel_yol)

            # URL -> yerel yol mapping'i kaydet
            self._url_to_local[url] = yerel_yol

            # HTML içindeki URL'yi yerel yol ile değiştir
            self._html_url_degistir(url, yerel_yol)

            return yerel_yol

        except Exception as e:
            print(f"Resim yerel kaydetme hatası: {e}")
            return None

    def _html_url_degistir(self, eski_url: str, yerel_yol: str):
        """HTML içindeki resim URL'sini yerel yol ile değiştirir."""
        self._yukleme_devam = True
        try:
            doc = self.document()
            html = doc.toHtml()

            # URL'yi yerel yol ile değiştir (file:/// prefix ile)
            yerel_url = QUrl.fromLocalFile(yerel_yol).toString()
            yeni_html = html.replace(f'src="{eski_url}"', f'src="{yerel_url}"')
            yeni_html = yeni_html.replace(f"src='{eski_url}'", f"src='{yerel_url}'")

            if yeni_html != html:
                cursor_pos = self.textCursor().position()
                super().setHtml(yeni_html)

                # Yerel resmi document resource olarak ekle
                image = QImage(yerel_yol)
                if not image.isNull():
                    doc = self.document()
                    doc.addResource(QTextDocument.ImageResource, QUrl.fromLocalFile(yerel_yol), image)

                # Cursor pozisyonunu koru
                text_len = len(self.toPlainText())
                if text_len > 0 and cursor_pos >= 0:
                    cursor = self.textCursor()
                    new_pos = max(0, min(cursor_pos, text_len - 1))
                    cursor.setPosition(new_pos)
                    self.setTextCursor(cursor)
        finally:
            self._yukleme_devam = False

    def _html_yenile(self):
        """HTML'i yeniden yükler."""
        self._yukleme_devam = True
        try:
            cursor_pos = self.textCursor().position()
            doc = self.document()
            html = doc.toHtml()
            super().setHtml(html)

            # Cursor pozisyonunu koru
            text_len = len(self.toPlainText())
            if text_len > 0 and cursor_pos >= 0:
                cursor = self.textCursor()
                new_pos = max(0, min(cursor_pos, text_len - 1))
                cursor.setPosition(new_pos)
                self.setTextCursor(cursor)
        finally:
            self._yukleme_devam = False

    def loadResource(self, type_: int, url: QUrl) -> any:
        """Kaynak yükleme - cache'den veya harici URL'den."""
        url_str = url.toString()

        # Cache'de var mı?
        if url_str in self._resim_cache:
            return self._resim_cache[url_str]

        # Varsayılan davranış (recursive çağrıları engellemek için burada indirme yapmıyoruz)
        return super().loadResource(type_, url)


class ZenginMetinDuzenleyici(QWidget):
    """
    Zengin metin düzenleme özelliklerine sahip editör widget'ı.
    Kalın, italik, altı çizili, renkli metin, listeler ve daha fazlasını destekler.
    """

    icerikDegisti = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Editör arayüzünü oluşturur."""
        ana_yerlesim = QVBoxLayout(self)
        ana_yerlesim.setContentsMargins(0, 0, 0, 0)
        ana_yerlesim.setSpacing(0)

        # Önce metin editörünü oluştur (araç çubuğu buna bağlı)
        self.editor = HariciResimYukleyiciTextEdit()
        self.editor.setAcceptRichText(True)
        self.editor.textChanged.connect(self.icerikDegisti.emit)
        self.editor.cursorPositionChanged.connect(self._imlec_degisti)

        # Araç çubuğu
        self.arac_cubugu = QToolBar()
        self.arac_cubugu.setMovable(False)
        self.arac_cubugu.setIconSize(QSize(20, 20))
        self._arac_cubugu_olustur()

        # Widget'ları yerleşime ekle
        ana_yerlesim.addWidget(self.arac_cubugu)
        ana_yerlesim.addWidget(self.editor)

    def _arac_cubugu_olustur(self):
        """Araç çubuğunu ve aksiyonlarını oluşturur."""
        # Geri Al / Yinele
        self.geri_al_aksiyonu = QAction('↩', self)
        self.geri_al_aksiyonu.setToolTip('Geri Al (Ctrl+Z)')
        self.geri_al_aksiyonu.setShortcut(QKeySequence.Undo)
        self.geri_al_aksiyonu.triggered.connect(self.editor.undo)
        self.arac_cubugu.addAction(self.geri_al_aksiyonu)

        self.yinele_aksiyonu = QAction('↪', self)
        self.yinele_aksiyonu.setToolTip('Yinele (Ctrl+Y)')
        self.yinele_aksiyonu.setShortcut(QKeySequence.Redo)
        self.yinele_aksiyonu.triggered.connect(self.editor.redo)
        self.arac_cubugu.addAction(self.yinele_aksiyonu)

        self.arac_cubugu.addSeparator()

        # Yazı Tipi
        self.yazi_tipi_combo = QFontComboBox()
        self.yazi_tipi_combo.setMaximumWidth(150)
        self.yazi_tipi_combo.currentFontChanged.connect(self._yazi_tipi_degistir)
        self.arac_cubugu.addWidget(self.yazi_tipi_combo)

        # Yazı Boyutu
        self.yazi_boyutu = QSpinBox()
        self.yazi_boyutu.setRange(8, 72)
        self.yazi_boyutu.setValue(12)
        self.yazi_boyutu.setMaximumWidth(60)
        self.yazi_boyutu.valueChanged.connect(self._yazi_boyutu_degistir)
        self.arac_cubugu.addWidget(self.yazi_boyutu)

        self.arac_cubugu.addSeparator()

        # Kalın
        self.kalin_aksiyonu = QAction('K', self)
        self.kalin_aksiyonu.setToolTip('Kalın (Ctrl+B)')
        self.kalin_aksiyonu.setCheckable(True)
        self.kalin_aksiyonu.setShortcut(QKeySequence.Bold)
        self.kalin_aksiyonu.triggered.connect(self._kalin_yap)
        font = self.kalin_aksiyonu.font()
        font.setBold(True)
        self.kalin_aksiyonu.setFont(font)
        self.arac_cubugu.addAction(self.kalin_aksiyonu)

        # İtalik
        self.italik_aksiyonu = QAction('I', self)
        self.italik_aksiyonu.setToolTip('İtalik (Ctrl+I)')
        self.italik_aksiyonu.setCheckable(True)
        self.italik_aksiyonu.setShortcut(QKeySequence.Italic)
        self.italik_aksiyonu.triggered.connect(self._italik_yap)
        font = self.italik_aksiyonu.font()
        font.setItalic(True)
        self.italik_aksiyonu.setFont(font)
        self.arac_cubugu.addAction(self.italik_aksiyonu)

        # Altı Çizili
        self.alti_cizili_aksiyonu = QAction('A', self)
        self.alti_cizili_aksiyonu.setToolTip('Altı Çizili (Ctrl+U)')
        self.alti_cizili_aksiyonu.setCheckable(True)
        self.alti_cizili_aksiyonu.setShortcut(QKeySequence.Underline)
        self.alti_cizili_aksiyonu.triggered.connect(self._alti_cizili_yap)
        font = self.alti_cizili_aksiyonu.font()
        font.setUnderline(True)
        self.alti_cizili_aksiyonu.setFont(font)
        self.arac_cubugu.addAction(self.alti_cizili_aksiyonu)

        # Üstü Çizili
        self.ustu_cizili_aksiyonu = QAction('S', self)
        self.ustu_cizili_aksiyonu.setToolTip('Üstü Çizili')
        self.ustu_cizili_aksiyonu.setCheckable(True)
        self.ustu_cizili_aksiyonu.triggered.connect(self._ustu_cizili_yap)
        font = self.ustu_cizili_aksiyonu.font()
        font.setStrikeOut(True)
        self.ustu_cizili_aksiyonu.setFont(font)
        self.arac_cubugu.addAction(self.ustu_cizili_aksiyonu)

        self.arac_cubugu.addSeparator()

        # Metin Rengi
        self.metin_rengi_aksiyonu = QAction('🔤', self)
        self.metin_rengi_aksiyonu.setToolTip('Metin Rengi')
        self.metin_rengi_aksiyonu.triggered.connect(self._metin_rengi_sec)
        self.arac_cubugu.addAction(self.metin_rengi_aksiyonu)

        # Vurgulama Rengi
        self.vurgulama_aksiyonu = QAction('🖍', self)
        self.vurgulama_aksiyonu.setToolTip('Vurgulama Rengi')
        self.vurgulama_aksiyonu.triggered.connect(self._vurgulama_rengi_sec)
        self.arac_cubugu.addAction(self.vurgulama_aksiyonu)

        self.arac_cubugu.addSeparator()

        # Hizalama
        self.sol_hiza_aksiyonu = QAction('⬅', self)
        self.sol_hiza_aksiyonu.setToolTip('Sola Hizala')
        self.sol_hiza_aksiyonu.triggered.connect(lambda: self._hizala(Qt.AlignLeft))
        self.arac_cubugu.addAction(self.sol_hiza_aksiyonu)

        self.orta_hiza_aksiyonu = QAction('⬌', self)
        self.orta_hiza_aksiyonu.setToolTip('Ortala')
        self.orta_hiza_aksiyonu.triggered.connect(lambda: self._hizala(Qt.AlignCenter))
        self.arac_cubugu.addAction(self.orta_hiza_aksiyonu)

        self.sag_hiza_aksiyonu = QAction('➡', self)
        self.sag_hiza_aksiyonu.setToolTip('Sağa Hizala')
        self.sag_hiza_aksiyonu.triggered.connect(lambda: self._hizala(Qt.AlignRight))
        self.arac_cubugu.addAction(self.sag_hiza_aksiyonu)

        self.iki_yana_aksiyonu = QAction('⬔', self)
        self.iki_yana_aksiyonu.setToolTip('İki Yana Yasla')
        self.iki_yana_aksiyonu.triggered.connect(lambda: self._hizala(Qt.AlignJustify))
        self.arac_cubugu.addAction(self.iki_yana_aksiyonu)

        self.arac_cubugu.addSeparator()

        # Listeler
        self.madde_listesi_aksiyonu = QAction('• —', self)
        self.madde_listesi_aksiyonu.setToolTip('Madde İşaretli Liste')
        self.madde_listesi_aksiyonu.triggered.connect(self._madde_listesi_ekle)
        self.arac_cubugu.addAction(self.madde_listesi_aksiyonu)

        self.numarali_liste_aksiyonu = QAction('1. —', self)
        self.numarali_liste_aksiyonu.setToolTip('Numaralı Liste')
        self.numarali_liste_aksiyonu.triggered.connect(self._numarali_liste_ekle)
        self.arac_cubugu.addAction(self.numarali_liste_aksiyonu)

        self.arac_cubugu.addSeparator()

        # Biçimlendirmeyi Temizle
        self.temizle_aksiyonu = QAction('✕', self)
        self.temizle_aksiyonu.setToolTip('Biçimlendirmeyi Temizle')
        self.temizle_aksiyonu.triggered.connect(self._bicimlendirmeyi_temizle)
        self.arac_cubugu.addAction(self.temizle_aksiyonu)

    def _yazi_tipi_degistir(self, font: QFont):
        """Seçili metnin yazı tipini değiştirir."""
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self._format_uygula(fmt)

    def _yazi_boyutu_degistir(self, boyut: int):
        """Seçili metnin boyutunu değiştirir."""
        fmt = QTextCharFormat()
        fmt.setFontPointSize(boyut)
        self._format_uygula(fmt)

    def _kalin_yap(self):
        """Seçili metni kalın yapar."""
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.kalin_aksiyonu.isChecked() else QFont.Normal)
        self._format_uygula(fmt)

    def _italik_yap(self):
        """Seçili metni italik yapar."""
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italik_aksiyonu.isChecked())
        self._format_uygula(fmt)

    def _alti_cizili_yap(self):
        """Seçili metnin altını çizer."""
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.alti_cizili_aksiyonu.isChecked())
        self._format_uygula(fmt)

    def _ustu_cizili_yap(self):
        """Seçili metnin üstünü çizer."""
        fmt = QTextCharFormat()
        fmt.setFontStrikeOut(self.ustu_cizili_aksiyonu.isChecked())
        self._format_uygula(fmt)

    def _metin_rengi_sec(self):
        """Metin rengi seçim dialogunu açar."""
        renk = QColorDialog.getColor()
        if renk.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(renk)
            self._format_uygula(fmt)

    def _vurgulama_rengi_sec(self):
        """Vurgulama rengi seçim dialogunu açar."""
        renk = QColorDialog.getColor()
        if renk.isValid():
            fmt = QTextCharFormat()
            fmt.setBackground(renk)
            self._format_uygula(fmt)

    def _hizala(self, hizalama):
        """Paragrafı hizalar."""
        self.editor.setAlignment(hizalama)

    def _madde_listesi_ekle(self):
        """Madde işaretli liste ekler."""
        cursor = self.editor.textCursor()
        liste_formati = QTextListFormat()
        liste_formati.setStyle(QTextListFormat.ListDisc)
        cursor.createList(liste_formati)

    def _numarali_liste_ekle(self):
        """Numaralı liste ekler."""
        cursor = self.editor.textCursor()
        liste_formati = QTextListFormat()
        liste_formati.setStyle(QTextListFormat.ListDecimal)
        cursor.createList(liste_formati)

    def _bicimlendirmeyi_temizle(self):
        """Seçili metnin biçimlendirmesini temizler."""
        cursor = self.editor.textCursor()
        cursor.setCharFormat(QTextCharFormat())
        # Paragraf formatını da sıfırla
        blok_format = QTextBlockFormat()
        blok_format.setAlignment(Qt.AlignLeft)
        cursor.setBlockFormat(blok_format)

    def _format_uygula(self, format: QTextCharFormat):
        """Verilen formatı seçili metne uygular."""
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.editor.mergeCurrentCharFormat(format)

    def _imlec_degisti(self):
        """İmleç konumu değiştiğinde buton durumlarını günceller."""
        fmt = self.editor.currentCharFormat()
        font = fmt.font()

        # Buton durumlarını güncelle
        self.kalin_aksiyonu.setChecked(font.bold())
        self.italik_aksiyonu.setChecked(font.italic())
        self.alti_cizili_aksiyonu.setChecked(font.underline())
        self.ustu_cizili_aksiyonu.setChecked(font.strikeOut())

        # Yazı tipi ve boyutunu güncelle
        self.yazi_tipi_combo.blockSignals(True)
        self.yazi_tipi_combo.setCurrentFont(font)
        self.yazi_tipi_combo.blockSignals(False)

        self.yazi_boyutu.blockSignals(True)
        self.yazi_boyutu.setValue(int(font.pointSize()) if font.pointSize() > 0 else 12)
        self.yazi_boyutu.blockSignals(False)

    # Dış erişim metodları
    def html_icerik_getir(self) -> str:
        """HTML formatında içeriği döndürür."""
        return self.editor.toHtml()

    def html_icerik_ayarla(self, html: str):
        """HTML içeriği ayarlar."""
        self.editor.setHtml(html)

    def duz_metin_getir(self) -> str:
        """Düz metin içeriği döndürür."""
        return self.editor.toPlainText()

    def duz_metin_ayarla(self, metin: str):
        """Düz metin içeriği ayarlar."""
        self.editor.setPlainText(metin)

    def temizle(self):
        """Editörü temizler."""
        self.editor.clear()

    def odaklan(self):
        """Editöre odaklanır."""
        self.editor.setFocus()


class NotKarti(QFrame):
    """Not listesinde gösterilen not kartı widget'ı."""

    tiklandi = pyqtSignal(int)  # not_id
    favorDegisti = pyqtSignal(int)  # not_id

    def __init__(self, not_verisi: dict, parent=None):
        super().__init__(parent)
        self.not_id = not_verisi['id']
        self.not_verisi = not_verisi
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Kart arayüzünü oluşturur."""
        self.setObjectName('notKarti')
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameShape(QFrame.StyledPanel)

        ana_yerlesim = QVBoxLayout(self)
        ana_yerlesim.setContentsMargins(12, 10, 12, 10)
        ana_yerlesim.setSpacing(6)

        # Üst satır: Başlık ve Favori
        ust_yerlesim = QHBoxLayout()

        # Kategori rengi göstergesi
        kategori_renk = QFrame()
        kategori_renk.setObjectName('kategoriRenk')
        kategori_renk.setFixedSize(4, 40)
        renk = self.not_verisi.get('kategori_rengi', '#3498db')
        kategori_renk.setStyleSheet(f'background-color: {renk}; border-radius: 2px;')
        ust_yerlesim.addWidget(kategori_renk)

        # Başlık ve tarih
        baslik_yerlesim = QVBoxLayout()
        baslik_yerlesim.setSpacing(2)

        self.baslik_etiketi = QLabel(self.not_verisi['baslik'])
        self.baslik_etiketi.setStyleSheet('font-weight: bold; font-size: 14px;')
        baslik_yerlesim.addWidget(self.baslik_etiketi)

        # Tarih
        tarih = self.not_verisi.get('guncelleme_tarihi', '')
        if tarih:
            try:
                dt = datetime.strptime(tarih, '%Y-%m-%d %H:%M:%S')
                tarih_str = dt.strftime('%d.%m.%Y %H:%M')
            except:
                tarih_str = tarih
        else:
            tarih_str = ''
        self.tarih_etiketi = QLabel(tarih_str)
        self.tarih_etiketi.setStyleSheet('color: gray; font-size: 11px;')
        baslik_yerlesim.addWidget(self.tarih_etiketi)

        ust_yerlesim.addLayout(baslik_yerlesim, 1)

        # Favori butonu
        self.favori_btn = QPushButton('★' if self.not_verisi.get('favori') else '☆')
        self.favori_btn.setObjectName('favoriDugme')
        self.favori_btn.setFixedSize(30, 30)
        self.favori_btn.clicked.connect(lambda: self.favorDegisti.emit(self.not_id))
        if self.not_verisi.get('favori'):
            self.favori_btn.setStyleSheet('color: #f1c40f;')
        ust_yerlesim.addWidget(self.favori_btn)

        ana_yerlesim.addLayout(ust_yerlesim)

        # Önizleme metni
        icerik = self.not_verisi.get('icerik', '')
        onizleme = icerik[:100] + '...' if len(icerik) > 100 else icerik
        onizleme = onizleme.replace('\n', ' ')
        self.onizleme_etiketi = QLabel(onizleme)
        self.onizleme_etiketi.setStyleSheet('color: gray; font-size: 12px;')
        self.onizleme_etiketi.setWordWrap(True)
        ana_yerlesim.addWidget(self.onizleme_etiketi)

        # Etiketler
        etiketler = self.not_verisi.get('etiketler', [])
        if etiketler:
            etiket_yerlesim = QHBoxLayout()
            etiket_yerlesim.setSpacing(4)
            for etiket in etiketler[:3]:  # Max 3 etiket göster
                etiket_label = QLabel(etiket['ad'])
                etiket_label.setObjectName('etiketChip')
                etiket_label.setStyleSheet(f'''
                    background-color: {etiket.get('renk', '#9b59b6')}22;
                    color: {etiket.get('renk', '#9b59b6')};
                    border-radius: 10px;
                    padding: 2px 8px;
                    font-size: 10px;
                ''')
                etiket_yerlesim.addWidget(etiket_label)
            etiket_yerlesim.addStretch()
            ana_yerlesim.addLayout(etiket_yerlesim)

    def mousePressEvent(self, event):
        """Tıklama olayını yakalar."""
        if event.button() == Qt.LeftButton:
            self.tiklandi.emit(self.not_id)
        super().mousePressEvent(event)

    def favori_guncelle(self, durum: bool):
        """Favori durumunu günceller."""
        self.favori_btn.setText('★' if durum else '☆')
        self.favori_btn.setStyleSheet('color: #f1c40f;' if durum else '')


class KategoriDuzenleDialog(QDialog):
    """Kategori ekleme/düzenleme dialogu."""

    def __init__(self, parent=None, kategori: dict = None):
        super().__init__(parent)
        self.kategori = kategori
        self.secilen_renk = kategori.get('renk', '#3498db') if kategori else '#3498db'
        self.secilen_ikon = kategori.get('ikon', '📁') if kategori else '📁'
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Kategori Düzenle' if self.kategori else 'Yeni Kategori')
        self.setMinimumWidth(350)

        yerlesim = QVBoxLayout(self)

        # Form
        form = QFormLayout()

        self.ad_input = QLineEdit()
        if self.kategori:
            self.ad_input.setText(self.kategori['ad'])
        self.ad_input.setPlaceholderText('Kategori adı girin...')
        form.addRow('Ad:', self.ad_input)

        # Renk seçimi
        renk_yerlesim = QHBoxLayout()
        self.renk_onizleme = QFrame()
        self.renk_onizleme.setFixedSize(30, 30)
        self.renk_onizleme.setStyleSheet(f'''
            background-color: {self.secilen_renk};
            border-radius: 4px;
        ''')
        renk_yerlesim.addWidget(self.renk_onizleme)

        for renk in RENK_PALETI[:6]:
            renk_btn = QPushButton()
            renk_btn.setFixedSize(25, 25)
            renk_btn.setStyleSheet(f'''
                background-color: {renk};
                border: none;
                border-radius: 4px;
            ''')
            renk_btn.clicked.connect(lambda checked, r=renk: self._renk_sec(r))
            renk_yerlesim.addWidget(renk_btn)

        renk_secici_btn = QPushButton('...')
        renk_secici_btn.setFixedSize(25, 25)
        renk_secici_btn.clicked.connect(self._ozel_renk_sec)
        renk_yerlesim.addWidget(renk_secici_btn)
        renk_yerlesim.addStretch()

        form.addRow('Renk:', renk_yerlesim)

        # İkon seçimi
        ikon_yerlesim = QHBoxLayout()
        self.ikon_onizleme = QLabel(self.secilen_ikon)
        self.ikon_onizleme.setStyleSheet('font-size: 24px;')
        ikon_yerlesim.addWidget(self.ikon_onizleme)

        for ikon in KATEGORI_IKONLARI[:8]:
            ikon_btn = QPushButton(ikon)
            ikon_btn.setFixedSize(30, 30)
            ikon_btn.setStyleSheet('border: none; font-size: 16px;')
            ikon_btn.clicked.connect(lambda checked, i=ikon: self._ikon_sec(i))
            ikon_yerlesim.addWidget(ikon_btn)
        ikon_yerlesim.addStretch()

        form.addRow('İkon:', ikon_yerlesim)

        yerlesim.addLayout(form)

        # Butonlar
        butonlar = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        butonlar.accepted.connect(self.accept)
        butonlar.rejected.connect(self.reject)
        butonlar.button(QDialogButtonBox.Ok).setText('Kaydet')
        butonlar.button(QDialogButtonBox.Cancel).setText('İptal')
        yerlesim.addWidget(butonlar)

    def _renk_sec(self, renk: str):
        """Renk seçer."""
        self.secilen_renk = renk
        self.renk_onizleme.setStyleSheet(f'''
            background-color: {renk};
            border-radius: 4px;
        ''')

    def _ozel_renk_sec(self):
        """Özel renk seçim dialogunu açar."""
        renk = QColorDialog.getColor(QColor(self.secilen_renk), self)
        if renk.isValid():
            self._renk_sec(renk.name())

    def _ikon_sec(self, ikon: str):
        """İkon seçer."""
        self.secilen_ikon = ikon
        self.ikon_onizleme.setText(ikon)

    def verileri_getir(self) -> dict:
        """Dialog verilerini döndürür."""
        return {
            'ad': self.ad_input.text().strip(),
            'renk': self.secilen_renk,
            'ikon': self.secilen_ikon
        }


class EtiketDuzenleDialog(QDialog):
    """Etiket ekleme/düzenleme dialogu."""

    def __init__(self, parent=None, etiket: dict = None):
        super().__init__(parent)
        self.etiket = etiket
        self.secilen_renk = etiket.get('renk', '#9b59b6') if etiket else '#9b59b6'
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Etiket Düzenle' if self.etiket else 'Yeni Etiket')
        self.setMinimumWidth(300)

        yerlesim = QVBoxLayout(self)

        # Form
        form = QFormLayout()

        self.ad_input = QLineEdit()
        if self.etiket:
            self.ad_input.setText(self.etiket['ad'])
        self.ad_input.setPlaceholderText('Etiket adı girin...')
        form.addRow('Ad:', self.ad_input)

        # Renk seçimi
        renk_yerlesim = QHBoxLayout()
        self.renk_onizleme = QFrame()
        self.renk_onizleme.setFixedSize(30, 30)
        self.renk_onizleme.setStyleSheet(f'''
            background-color: {self.secilen_renk};
            border-radius: 15px;
        ''')
        renk_yerlesim.addWidget(self.renk_onizleme)

        for renk in RENK_PALETI[:6]:
            renk_btn = QPushButton()
            renk_btn.setFixedSize(25, 25)
            renk_btn.setStyleSheet(f'''
                background-color: {renk};
                border: none;
                border-radius: 12px;
            ''')
            renk_btn.clicked.connect(lambda checked, r=renk: self._renk_sec(r))
            renk_yerlesim.addWidget(renk_btn)

        renk_secici_btn = QPushButton('...')
        renk_secici_btn.setFixedSize(25, 25)
        renk_secici_btn.clicked.connect(self._ozel_renk_sec)
        renk_yerlesim.addWidget(renk_secici_btn)
        renk_yerlesim.addStretch()

        form.addRow('Renk:', renk_yerlesim)

        yerlesim.addLayout(form)

        # Butonlar
        butonlar = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        butonlar.accepted.connect(self.accept)
        butonlar.rejected.connect(self.reject)
        butonlar.button(QDialogButtonBox.Ok).setText('Kaydet')
        butonlar.button(QDialogButtonBox.Cancel).setText('İptal')
        yerlesim.addWidget(butonlar)

    def _renk_sec(self, renk: str):
        """Renk seçer."""
        self.secilen_renk = renk
        self.renk_onizleme.setStyleSheet(f'''
            background-color: {renk};
            border-radius: 15px;
        ''')

    def _ozel_renk_sec(self):
        """Özel renk seçim dialogunu açar."""
        renk = QColorDialog.getColor(QColor(self.secilen_renk), self)
        if renk.isValid():
            self._renk_sec(renk.name())

    def verileri_getir(self) -> dict:
        """Dialog verilerini döndürür."""
        return {
            'ad': self.ad_input.text().strip(),
            'renk': self.secilen_renk
        }


class HatirlaticiDialog(QDialog):
    """Hatırlatıcı ekleme dialogu."""

    def __init__(self, parent=None, not_baslik: str = ''):
        super().__init__(parent)
        self.not_baslik = not_baslik
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Hatırlatıcı Ekle')
        self.setMinimumWidth(350)

        yerlesim = QVBoxLayout(self)

        # Bilgi etiketi
        bilgi = QLabel(f'"{self.not_baslik}" için hatırlatıcı')
        bilgi.setStyleSheet('font-weight: bold;')
        yerlesim.addWidget(bilgi)

        # Form
        form = QFormLayout()

        # Tarih ve saat seçici
        self.tarih_saat = QDateTimeEdit()
        self.tarih_saat.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # 1 saat sonra
        self.tarih_saat.setCalendarPopup(True)
        self.tarih_saat.setDisplayFormat('dd.MM.yyyy HH:mm')
        form.addRow('Tarih/Saat:', self.tarih_saat)

        # Mesaj
        self.mesaj_input = QLineEdit()
        self.mesaj_input.setPlaceholderText('Hatırlatıcı mesajı (opsiyonel)...')
        form.addRow('Mesaj:', self.mesaj_input)

        yerlesim.addLayout(form)

        # Butonlar
        butonlar = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        butonlar.accepted.connect(self.accept)
        butonlar.rejected.connect(self.reject)
        butonlar.button(QDialogButtonBox.Ok).setText('Hatırlatıcı Ekle')
        butonlar.button(QDialogButtonBox.Cancel).setText('İptal')
        yerlesim.addWidget(butonlar)

    def verileri_getir(self) -> dict:
        """Dialog verilerini döndürür."""
        return {
            'hatirlatma_zamani': self.tarih_saat.dateTime().toPyDateTime(),
            'mesaj': self.mesaj_input.text().strip()
        }


class AyarlarDialog(QDialog):
    """Uygulama ayarları dialogu."""

    def __init__(self, parent=None, mevcut_tema: str = 'aydinlik'):
        super().__init__(parent)
        self.mevcut_tema = mevcut_tema
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Ayarlar')
        self.setMinimumWidth(400)

        yerlesim = QVBoxLayout(self)

        # Tema seçimi
        tema_grup = QHBoxLayout()
        tema_grup.addWidget(QLabel('Tema:'))

        self.tema_combo = QComboBox()
        self.tema_combo.addItem('Aydınlık', 'aydinlik')
        self.tema_combo.addItem('Karanlık', 'karanlik')

        index = self.tema_combo.findData(self.mevcut_tema)
        if index >= 0:
            self.tema_combo.setCurrentIndex(index)

        tema_grup.addWidget(self.tema_combo)
        tema_grup.addStretch()
        yerlesim.addLayout(tema_grup)

        yerlesim.addStretch()

        # Butonlar
        butonlar = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        butonlar.accepted.connect(self.accept)
        butonlar.rejected.connect(self.reject)
        butonlar.button(QDialogButtonBox.Ok).setText('Kaydet')
        butonlar.button(QDialogButtonBox.Cancel).setText('İptal')
        yerlesim.addWidget(butonlar)

    def tema_getir(self) -> str:
        """Seçilen temayı döndürür."""
        return self.tema_combo.currentData()


class IstatistiklerDialog(QDialog):
    """İstatistikler dialogu."""

    def __init__(self, parent=None, istatistikler: dict = None):
        super().__init__(parent)
        self.istatistikler = istatistikler or {}
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('İstatistikler')
        self.setMinimumWidth(350)

        yerlesim = QVBoxLayout(self)

        # Başlık
        baslik = QLabel('📊 Uygulama İstatistikleri')
        baslik.setStyleSheet('font-size: 18px; font-weight: bold; margin-bottom: 10px;')
        yerlesim.addWidget(baslik)

        # İstatistik satırları
        satirlar = [
            ('📝 Toplam Not', self.istatistikler.get('toplam_not', 0)),
            ('⭐ Favori Not', self.istatistikler.get('favori_not', 0)),
            ('🗑️ Çöp Kutusunda', self.istatistikler.get('silinen_not', 0)),
            ('📁 Kategori Sayısı', self.istatistikler.get('kategori_sayisi', 0)),
            ('🏷️ Etiket Sayısı', self.istatistikler.get('etiket_sayisi', 0)),
            ('🔔 Aktif Hatırlatıcı', self.istatistikler.get('aktif_hatirlatici', 0)),
            ('📅 Bu Hafta Oluşturulan', self.istatistikler.get('bu_hafta_not', 0)),
        ]

        for etiket, deger in satirlar:
            satir = QHBoxLayout()
            satir.addWidget(QLabel(etiket))
            satir.addStretch()
            deger_label = QLabel(str(deger))
            deger_label.setStyleSheet('font-weight: bold; font-size: 16px;')
            satir.addWidget(deger_label)
            yerlesim.addLayout(satir)

        yerlesim.addStretch()

        # Kapat butonu
        kapat_btn = QPushButton('Kapat')
        kapat_btn.clicked.connect(self.accept)
        yerlesim.addWidget(kapat_btn)


class EtiketSeciciDialog(QDialog):
    """Nota etiket ekleme dialogu."""

    def __init__(self, parent=None, tum_etiketler: list = None, secili_etiketler: list = None):
        super().__init__(parent)
        self.tum_etiketler = tum_etiketler or []
        self.secili_etiket_idleri = [e['id'] for e in (secili_etiketler or [])]
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Etiket Seç')
        self.setMinimumSize(300, 400)

        yerlesim = QVBoxLayout(self)

        # Etiket listesi
        self.liste = QListWidget()
        self.liste.setSelectionMode(QListWidget.MultiSelection)

        for etiket in self.tum_etiketler:
            item = QListWidgetItem(f"🏷️ {etiket['ad']}")
            item.setData(Qt.UserRole, etiket['id'])
            self.liste.addItem(item)
            if etiket['id'] in self.secili_etiket_idleri:
                item.setSelected(True)

        yerlesim.addWidget(self.liste)

        # Butonlar
        butonlar = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        butonlar.accepted.connect(self.accept)
        butonlar.rejected.connect(self.reject)
        butonlar.button(QDialogButtonBox.Ok).setText('Tamam')
        butonlar.button(QDialogButtonBox.Cancel).setText('İptal')
        yerlesim.addWidget(butonlar)

    def secili_etiket_idleri_getir(self) -> list:
        """Seçili etiket ID'lerini döndürür."""
        idler = []
        for item in self.liste.selectedItems():
            idler.append(item.data(Qt.UserRole))
        return idler