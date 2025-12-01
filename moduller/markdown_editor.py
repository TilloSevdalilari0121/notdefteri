# -*- coding: utf-8 -*-
"""
Not Defteri - Markdown Editör Modülü
Markdown yazma ve önizleme özellikleri.
"""

import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QSplitter,
    QToolBar, QAction, QLabel, QComboBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import (
    QFont, QTextCharFormat, QColor, QSyntaxHighlighter,
    QTextDocument, QFontDatabase
)

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class MarkdownSozdizimiVurgulayici(QSyntaxHighlighter):
    """Markdown sözdizimi vurgulayıcı."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._kurallar_olustur()

    def _kurallar_olustur(self):
        """Vurgulama kurallarını oluşturur."""
        self.kurallar = []

        # Başlıklar
        baslik_format = QTextCharFormat()
        baslik_format.setForeground(QColor('#e74c3c'))
        baslik_format.setFontWeight(QFont.Bold)
        self.kurallar.append((r'^#{1,6}\s.*$', baslik_format))

        # Kalın
        kalin_format = QTextCharFormat()
        kalin_format.setFontWeight(QFont.Bold)
        kalin_format.setForeground(QColor('#2ecc71'))
        self.kurallar.append((r'\*\*.*?\*\*', kalin_format))
        self.kurallar.append((r'__.*?__', kalin_format))

        # İtalik
        italik_format = QTextCharFormat()
        italik_format.setFontItalic(True)
        italik_format.setForeground(QColor('#3498db'))
        self.kurallar.append((r'\*[^*]+\*', italik_format))
        self.kurallar.append((r'_[^_]+_', italik_format))

        # Kod (inline)
        kod_format = QTextCharFormat()
        kod_format.setFontFamily('Consolas')
        kod_format.setBackground(QColor('#f0f0f0'))
        kod_format.setForeground(QColor('#c0392b'))
        self.kurallar.append((r'`[^`]+`', kod_format))

        # Kod bloğu
        kod_blok_format = QTextCharFormat()
        kod_blok_format.setFontFamily('Consolas')
        kod_blok_format.setBackground(QColor('#2d2d2d'))
        kod_blok_format.setForeground(QColor('#f8f8f2'))
        self.kurallar.append((r'```[\s\S]*?```', kod_blok_format))

        # Linkler
        link_format = QTextCharFormat()
        link_format.setForeground(QColor('#9b59b6'))
        link_format.setFontUnderline(True)
        self.kurallar.append((r'\[.*?\]\(.*?\)', link_format))

        # Listeler
        liste_format = QTextCharFormat()
        liste_format.setForeground(QColor('#e67e22'))
        self.kurallar.append((r'^\s*[-*+]\s', liste_format))
        self.kurallar.append((r'^\s*\d+\.\s', liste_format))

        # Alıntı
        alinti_format = QTextCharFormat()
        alinti_format.setForeground(QColor('#7f8c8d'))
        alinti_format.setFontItalic(True)
        self.kurallar.append((r'^>\s.*$', alinti_format))

        # Yatay çizgi
        cizgi_format = QTextCharFormat()
        cizgi_format.setForeground(QColor('#bdc3c7'))
        self.kurallar.append((r'^(-{3,}|\*{3,}|_{3,})$', cizgi_format))

        # Checkbox
        checkbox_format = QTextCharFormat()
        checkbox_format.setForeground(QColor('#1abc9c'))
        self.kurallar.append((r'\[[ x]\]', checkbox_format))

    def highlightBlock(self, text):
        """Metin bloğunu vurgular."""
        for pattern, format in self.kurallar:
            for match in re.finditer(pattern, text, re.MULTILINE):
                self.setFormat(match.start(), match.end() - match.start(), format)


class MarkdownOnizleyici(QTextEdit):
    """Markdown içeriği HTML olarak önizleyen widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet('''
            QTextEdit {
                background-color: #ffffff;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        ''')

        # Varsayılan CSS
        self.css = '''
            body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; }
            h1, h2, h3, h4, h5, h6 { color: #2c3e50; margin-top: 20px; }
            h1 { border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
            code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-family: Consolas, monospace; }
            pre { background-color: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 8px; overflow-x: auto; }
            pre code { background-color: transparent; padding: 0; }
            blockquote { border-left: 4px solid #3498db; margin: 10px 0; padding: 10px 20px; background-color: #f9f9f9; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
            ul, ol { padding-left: 30px; }
            li { margin: 5px 0; }
            hr { border: none; border-top: 1px solid #bdc3c7; margin: 20px 0; }
            table { border-collapse: collapse; width: 100%; margin: 15px 0; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #f4f4f4; }
            img { max-width: 100%; height: auto; border-radius: 8px; }
            .task-list-item { list-style-type: none; }
            .task-list-item input { margin-right: 10px; }
        '''

    def markdown_goster(self, markdown_metni: str):
        """Markdown metnini HTML olarak gösterir."""
        if MARKDOWN_AVAILABLE:
            html = markdown.markdown(
                markdown_metni,
                extensions=[
                    'extra',
                    'codehilite',
                    'toc',
                    'tables',
                    'nl2br',
                    'sane_lists'
                ]
            )
        else:
            # Basit Markdown dönüştürme
            html = self._basit_markdown_donustur(markdown_metni)

        tam_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>{self.css}</style>
        </head>
        <body>
            {html}
        </body>
        </html>
        '''
        self.setHtml(tam_html)

    def _basit_markdown_donustur(self, metin: str) -> str:
        """Basit Markdown dönüştürme (markdown kütüphanesi yoksa)."""
        import html
        metin = html.escape(metin)

        # Başlıklar
        metin = re.sub(r'^###### (.*)$', r'<h6>\1</h6>', metin, flags=re.MULTILINE)
        metin = re.sub(r'^##### (.*)$', r'<h5>\1</h5>', metin, flags=re.MULTILINE)
        metin = re.sub(r'^#### (.*)$', r'<h4>\1</h4>', metin, flags=re.MULTILINE)
        metin = re.sub(r'^### (.*)$', r'<h3>\1</h3>', metin, flags=re.MULTILINE)
        metin = re.sub(r'^## (.*)$', r'<h2>\1</h2>', metin, flags=re.MULTILINE)
        metin = re.sub(r'^# (.*)$', r'<h1>\1</h1>', metin, flags=re.MULTILINE)

        # Kalın ve italik
        metin = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', metin)
        metin = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', metin)
        metin = re.sub(r'\*(.*?)\*', r'<em>\1</em>', metin)

        # Kod
        metin = re.sub(r'`([^`]+)`', r'<code>\1</code>', metin)

        # Linkler
        metin = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', metin)

        # Yatay çizgi
        metin = re.sub(r'^(-{3,}|\*{3,}|_{3,})$', r'<hr>', metin, flags=re.MULTILINE)

        # Paragraflar
        metin = re.sub(r'\n\n', '</p><p>', metin)
        metin = f'<p>{metin}</p>'

        return metin


class MarkdownDuzenleyici(QWidget):
    """Markdown düzenleyici widget - yazma ve önizleme."""

    icerikDegisti = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.onizleme_gecikme = 500  # ms
        self._arayuz_olustur()
        self._timer_olustur()

    def _arayuz_olustur(self):
        """Arayüzü oluşturur."""
        ana_yerlesim = QVBoxLayout(self)
        ana_yerlesim.setContentsMargins(0, 0, 0, 0)

        # Araç çubuğu
        self.arac_cubugu = QToolBar()
        self._arac_cubugu_olustur()
        ana_yerlesim.addWidget(self.arac_cubugu)

        # Splitter - Editör ve Önizleme
        self.splitter = QSplitter(Qt.Horizontal)

        # Editör
        self.editor = QTextEdit()
        self.editor.setFont(QFont('Consolas', 11))
        self.editor.setPlaceholderText('Markdown formatında yazın...')
        self.editor.textChanged.connect(self._icerik_degisti)

        # Sözdizimi vurgulayıcı
        self.vurgulayici = MarkdownSozdizimiVurgulayici(self.editor.document())

        self.splitter.addWidget(self.editor)

        # Önizleme
        self.onizleme = MarkdownOnizleyici()
        self.splitter.addWidget(self.onizleme)

        self.splitter.setSizes([400, 400])
        ana_yerlesim.addWidget(self.splitter)

        # Görünüm modu
        self.gorunum_modu = 'bolunmus'  # 'editor', 'onizleme', 'bolunmus'

    def _arac_cubugu_olustur(self):
        """Araç çubuğunu oluşturur."""
        # Başlık ekleme
        baslik_menu = QComboBox()
        baslik_menu.addItems(['Başlık', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6'])
        baslik_menu.currentIndexChanged.connect(self._baslik_ekle)
        self.arac_cubugu.addWidget(baslik_menu)

        self.arac_cubugu.addSeparator()

        # Biçimlendirme butonları
        kalin_btn = QAction('B', self)
        kalin_btn.setToolTip('Kalın (Ctrl+B)')
        kalin_btn.triggered.connect(lambda: self._format_ekle('**', '**'))
        font = kalin_btn.font()
        font.setBold(True)
        kalin_btn.setFont(font)
        self.arac_cubugu.addAction(kalin_btn)

        italik_btn = QAction('I', self)
        italik_btn.setToolTip('İtalik (Ctrl+I)')
        italik_btn.triggered.connect(lambda: self._format_ekle('*', '*'))
        font = italik_btn.font()
        font.setItalic(True)
        italik_btn.setFont(font)
        self.arac_cubugu.addAction(italik_btn)

        ustu_cizili_btn = QAction('S', self)
        ustu_cizili_btn.setToolTip('Üstü Çizili')
        ustu_cizili_btn.triggered.connect(lambda: self._format_ekle('~~', '~~'))
        self.arac_cubugu.addAction(ustu_cizili_btn)

        self.arac_cubugu.addSeparator()

        # Kod
        kod_btn = QAction('< >', self)
        kod_btn.setToolTip('Satır İçi Kod')
        kod_btn.triggered.connect(lambda: self._format_ekle('`', '`'))
        self.arac_cubugu.addAction(kod_btn)

        kod_blok_btn = QAction('{ }', self)
        kod_blok_btn.setToolTip('Kod Bloğu')
        kod_blok_btn.triggered.connect(self._kod_blogu_ekle)
        self.arac_cubugu.addAction(kod_blok_btn)

        self.arac_cubugu.addSeparator()

        # Liste
        liste_btn = QAction('• —', self)
        liste_btn.setToolTip('Madde Listesi')
        liste_btn.triggered.connect(self._madde_listesi_ekle)
        self.arac_cubugu.addAction(liste_btn)

        numarali_btn = QAction('1. —', self)
        numarali_btn.setToolTip('Numaralı Liste')
        numarali_btn.triggered.connect(self._numarali_liste_ekle)
        self.arac_cubugu.addAction(numarali_btn)

        checkbox_btn = QAction('☑', self)
        checkbox_btn.setToolTip('Yapılacak Maddesi')
        checkbox_btn.triggered.connect(self._checkbox_ekle)
        self.arac_cubugu.addAction(checkbox_btn)

        self.arac_cubugu.addSeparator()

        # Link ve resim
        link_btn = QAction('🔗', self)
        link_btn.setToolTip('Link Ekle')
        link_btn.triggered.connect(self._link_ekle)
        self.arac_cubugu.addAction(link_btn)

        resim_btn = QAction('🖼', self)
        resim_btn.setToolTip('Resim Ekle')
        resim_btn.triggered.connect(self._resim_ekle)
        self.arac_cubugu.addAction(resim_btn)

        self.arac_cubugu.addSeparator()

        # Alıntı ve çizgi
        alinti_btn = QAction('❝', self)
        alinti_btn.setToolTip('Alıntı')
        alinti_btn.triggered.connect(self._alinti_ekle)
        self.arac_cubugu.addAction(alinti_btn)

        cizgi_btn = QAction('—', self)
        cizgi_btn.setToolTip('Yatay Çizgi')
        cizgi_btn.triggered.connect(lambda: self._metin_ekle('\n---\n'))
        self.arac_cubugu.addAction(cizgi_btn)

        self.arac_cubugu.addSeparator()

        # Tablo
        tablo_btn = QAction('⊞', self)
        tablo_btn.setToolTip('Tablo Ekle')
        tablo_btn.triggered.connect(self._tablo_ekle)
        self.arac_cubugu.addAction(tablo_btn)

        # Boşluk
        spacer = QWidget()
        spacer.setFixedWidth(50)
        self.arac_cubugu.addWidget(spacer)

        # Görünüm değiştirme
        self.editor_btn = QPushButton('Editör')
        self.editor_btn.setCheckable(True)
        self.editor_btn.clicked.connect(lambda: self._gorunum_degistir('editor'))
        self.arac_cubugu.addWidget(self.editor_btn)

        self.bolunmus_btn = QPushButton('Bölünmüş')
        self.bolunmus_btn.setCheckable(True)
        self.bolunmus_btn.setChecked(True)
        self.bolunmus_btn.clicked.connect(lambda: self._gorunum_degistir('bolunmus'))
        self.arac_cubugu.addWidget(self.bolunmus_btn)

        self.onizleme_btn = QPushButton('Önizleme')
        self.onizleme_btn.setCheckable(True)
        self.onizleme_btn.clicked.connect(lambda: self._gorunum_degistir('onizleme'))
        self.arac_cubugu.addWidget(self.onizleme_btn)

    def _timer_olustur(self):
        """Önizleme güncelleme timer'ı oluşturur."""
        self.guncelleme_timer = QTimer()
        self.guncelleme_timer.setSingleShot(True)
        self.guncelleme_timer.timeout.connect(self._onizleme_guncelle)

    def _icerik_degisti(self):
        """İçerik değiştiğinde çağrılır."""
        self.guncelleme_timer.start(self.onizleme_gecikme)
        self.icerikDegisti.emit(self.editor.toPlainText())

    def _onizleme_guncelle(self):
        """Önizlemeyi günceller."""
        self.onizleme.markdown_goster(self.editor.toPlainText())

    def _gorunum_degistir(self, mod: str):
        """Görünüm modunu değiştirir."""
        self.gorunum_modu = mod

        self.editor_btn.setChecked(mod == 'editor')
        self.bolunmus_btn.setChecked(mod == 'bolunmus')
        self.onizleme_btn.setChecked(mod == 'onizleme')

        if mod == 'editor':
            self.editor.show()
            self.onizleme.hide()
        elif mod == 'onizleme':
            self.editor.hide()
            self.onizleme.show()
            self._onizleme_guncelle()
        else:  # bolunmus
            self.editor.show()
            self.onizleme.show()
            self._onizleme_guncelle()

    def _format_ekle(self, prefix: str, suffix: str):
        """Seçili metne format ekler."""
        cursor = self.editor.textCursor()
        secili = cursor.selectedText()
        cursor.insertText(f'{prefix}{secili}{suffix}')

    def _metin_ekle(self, metin: str):
        """İmleç konumuna metin ekler."""
        cursor = self.editor.textCursor()
        cursor.insertText(metin)

    def _baslik_ekle(self, index: int):
        """Başlık ekler."""
        if index > 0:
            prefix = '#' * index + ' '
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.StartOfLine)
            cursor.insertText(prefix)

    def _kod_blogu_ekle(self):
        """Kod bloğu ekler."""
        cursor = self.editor.textCursor()
        secili = cursor.selectedText()
        cursor.insertText(f'```\n{secili}\n```')

    def _madde_listesi_ekle(self):
        """Madde listesi ekler."""
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.StartOfLine)
        cursor.insertText('- ')

    def _numarali_liste_ekle(self):
        """Numaralı liste ekler."""
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.StartOfLine)
        cursor.insertText('1. ')

    def _checkbox_ekle(self):
        """Checkbox ekler."""
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.StartOfLine)
        cursor.insertText('- [ ] ')

    def _link_ekle(self):
        """Link ekler."""
        cursor = self.editor.textCursor()
        secili = cursor.selectedText()
        if secili:
            cursor.insertText(f'[{secili}](url)')
        else:
            cursor.insertText('[metin](url)')

    def _resim_ekle(self):
        """Resim ekler."""
        cursor = self.editor.textCursor()
        cursor.insertText('![alt metin](resim_url)')

    def _alinti_ekle(self):
        """Alıntı ekler."""
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.StartOfLine)
        cursor.insertText('> ')

    def _tablo_ekle(self):
        """Tablo şablonu ekler."""
        tablo = '''
| Başlık 1 | Başlık 2 | Başlık 3 |
|----------|----------|----------|
| Hücre 1  | Hücre 2  | Hücre 3  |
| Hücre 4  | Hücre 5  | Hücre 6  |
'''
        self._metin_ekle(tablo)

    # Dış erişim metodları
    def icerik_getir(self) -> str:
        """Markdown içeriğini döndürür."""
        return self.editor.toPlainText()

    def icerik_ayarla(self, metin: str):
        """Markdown içeriğini ayarlar."""
        self.editor.setPlainText(metin)
        self._onizleme_guncelle()

    def html_getir(self) -> str:
        """HTML çıktısını döndürür."""
        if MARKDOWN_AVAILABLE:
            return markdown.markdown(self.editor.toPlainText(), extensions=['extra', 'codehilite', 'tables'])
        return self.onizleme.toHtml()

    def temizle(self):
        """Editörü temizler."""
        self.editor.clear()
        self.onizleme.clear()
