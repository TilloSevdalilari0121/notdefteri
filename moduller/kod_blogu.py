# -*- coding: utf-8 -*-
"""
Not Defteri - Kod Bloğu Modülü
Sözdizimi vurgulu kod blokları.
"""

import re
from typing import Dict, List, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QComboBox, QFrame, QApplication, QPlainTextEdit,
    QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QSize
from PyQt5.QtGui import (
    QFont, QColor, QTextCharFormat, QSyntaxHighlighter,
    QPainter, QTextFormat, QFontMetrics
)


# Sözdizimi vurgulama renkleri
class SozdizimiRenkleri:
    """Sözdizimi vurgulama renk şeması."""

    # Monokai benzeri tema
    MONOKAI = {
        'background': '#272822',
        'foreground': '#f8f8f2',
        'comment': '#75715e',
        'keyword': '#f92672',
        'string': '#e6db74',
        'number': '#ae81ff',
        'function': '#a6e22e',
        'class': '#66d9ef',
        'operator': '#f92672',
        'variable': '#fd971f',
    }

    # Aydınlık tema
    LIGHT = {
        'background': '#fafafa',
        'foreground': '#383a42',
        'comment': '#a0a1a7',
        'keyword': '#a626a4',
        'string': '#50a14f',
        'number': '#986801',
        'function': '#4078f2',
        'class': '#c18401',
        'operator': '#e45649',
        'variable': '#986801',
    }


# Dil tanımları
DIL_KURALLARI = {
    'python': {
        'keywords': [
            'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
            'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
            'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not',
            'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
            'True', 'False', 'None'
        ],
        'builtins': [
            'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict',
            'set', 'tuple', 'bool', 'open', 'input', 'type', 'isinstance',
            'hasattr', 'getattr', 'setattr', 'enumerate', 'zip', 'map', 'filter'
        ],
        'comment': r'#.*$',
        'string': r'(?:\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\'|\"[^\"]*\"|\'[^\']*\')',
        'number': r'\b\d+\.?\d*\b',
        'function': r'\bdef\s+(\w+)',
        'class': r'\bclass\s+(\w+)',
    },
    'javascript': {
        'keywords': [
            'break', 'case', 'catch', 'const', 'continue', 'debugger', 'default',
            'delete', 'do', 'else', 'export', 'extends', 'finally', 'for',
            'function', 'if', 'import', 'in', 'instanceof', 'let', 'new',
            'return', 'switch', 'this', 'throw', 'try', 'typeof', 'var',
            'void', 'while', 'with', 'yield', 'async', 'await', 'class',
            'true', 'false', 'null', 'undefined'
        ],
        'comment': r'(?://.*$|/\*[\s\S]*?\*/)',
        'string': r'(?:\"[^\"]*\"|\'[^\']*\'|`[^`]*`)',
        'number': r'\b\d+\.?\d*\b',
        'function': r'\bfunction\s+(\w+)',
        'class': r'\bclass\s+(\w+)',
    },
    'html': {
        'keywords': [],
        'comment': r'<!--[\s\S]*?-->',
        'string': r'(?:\"[^\"]*\"|\'[^\']*\')',
        'tag': r'</?[\w-]+',
        'attribute': r'\b[\w-]+(?==)',
    },
    'css': {
        'keywords': [],
        'comment': r'/\*[\s\S]*?\*/',
        'string': r'(?:\"[^\"]*\"|\'[^\']*\')',
        'property': r'[\w-]+(?=\s*:)',
        'value': r':\s*([^;{}]+)',
        'selector': r'^[^{}]+(?=\s*\{)',
    },
    'sql': {
        'keywords': [
            'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'INSERT', 'INTO',
            'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE', 'DROP',
            'ALTER', 'INDEX', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
            'ON', 'AS', 'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET',
            'UNION', 'ALL', 'DISTINCT', 'NULL', 'IS', 'LIKE', 'IN', 'BETWEEN'
        ],
        'comment': r'(?:--.*$|/\*[\s\S]*?\*/)',
        'string': r'(?:\"[^\"]*\"|\'[^\']*\')',
        'number': r'\b\d+\.?\d*\b',
    },
    'json': {
        'keywords': ['true', 'false', 'null'],
        'string': r'\"[^\"]*\"',
        'number': r'-?\b\d+\.?\d*\b',
    },
}


class KodVurgulayici(QSyntaxHighlighter):
    """Kod sözdizimi vurgulayıcı."""

    def __init__(self, parent=None, dil: str = 'python', tema: str = 'monokai'):
        super().__init__(parent)
        self.dil = dil
        self.tema = SozdizimiRenkleri.MONOKAI if tema == 'monokai' else SozdizimiRenkleri.LIGHT
        self._formatlari_olustur()

    def _formatlari_olustur(self):
        """Vurgulama formatlarını oluşturur."""
        self.formatlar = {}

        # Yorum
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.tema['comment']))
        fmt.setFontItalic(True)
        self.formatlar['comment'] = fmt

        # Anahtar kelime
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.tema['keyword']))
        fmt.setFontWeight(QFont.Bold)
        self.formatlar['keyword'] = fmt

        # String
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.tema['string']))
        self.formatlar['string'] = fmt

        # Sayı
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.tema['number']))
        self.formatlar['number'] = fmt

        # Fonksiyon
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.tema['function']))
        self.formatlar['function'] = fmt

        # Sınıf
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.tema['class']))
        fmt.setFontWeight(QFont.Bold)
        self.formatlar['class'] = fmt

    def highlightBlock(self, text):
        """Metin bloğunu vurgular."""
        if self.dil not in DIL_KURALLARI:
            return

        kurallar = DIL_KURALLARI[self.dil]

        # Anahtar kelimeler
        for keyword in kurallar.get('keywords', []):
            pattern = rf'\b{keyword}\b'
            for match in re.finditer(pattern, text, re.IGNORECASE if self.dil == 'sql' else 0):
                self.setFormat(match.start(), match.end() - match.start(), self.formatlar['keyword'])

        # String'ler
        if 'string' in kurallar:
            for match in re.finditer(kurallar['string'], text, re.MULTILINE):
                self.setFormat(match.start(), match.end() - match.start(), self.formatlar['string'])

        # Sayılar
        if 'number' in kurallar:
            for match in re.finditer(kurallar['number'], text):
                self.setFormat(match.start(), match.end() - match.start(), self.formatlar['number'])

        # Fonksiyonlar
        if 'function' in kurallar:
            for match in re.finditer(kurallar['function'], text):
                if match.group(1):
                    start = match.start(1)
                    length = len(match.group(1))
                    self.setFormat(start, length, self.formatlar['function'])

        # Sınıflar
        if 'class' in kurallar:
            for match in re.finditer(kurallar['class'], text):
                if match.group(1):
                    start = match.start(1)
                    length = len(match.group(1))
                    self.setFormat(start, length, self.formatlar['class'])

        # Yorumlar (en son, üzerine yazmasın)
        if 'comment' in kurallar:
            for match in re.finditer(kurallar['comment'], text, re.MULTILINE):
                self.setFormat(match.start(), match.end() - match.start(), self.formatlar['comment'])


class SatirNumarasiAlani(QWidget):
    """Satır numarası gösterme alanı."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.satir_numarasi_genislik(), 0)

    def paintEvent(self, event):
        self.editor.satir_numarasi_ciz(event)


class KodBloguWidget(QPlainTextEdit):
    """Sözdizimi vurgulu kod editörü widget'ı."""

    def __init__(self, parent=None, dil: str = 'python'):
        super().__init__(parent)
        self.dil = dil

        # Font
        font = QFont('Consolas', 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        # Tab genişliği
        fm = QFontMetrics(font)
        self.setTabStopDistance(fm.horizontalAdvance(' ') * 4)

        # Vurgulayıcı
        self.vurgulayici = KodVurgulayici(self.document(), dil)

        # Satır numarası alanı
        self.satir_numarasi = SatirNumarasiAlani(self)
        self.blockCountChanged.connect(self._satir_sayisi_degisti)
        self.updateRequest.connect(self._alan_guncelle)
        self._satir_sayisi_degisti(0)

        # Stil
        self._stil_uygula()

    def _stil_uygula(self):
        """Stil uygular."""
        tema = SozdizimiRenkleri.MONOKAI
        self.setStyleSheet(f'''
            QPlainTextEdit {{
                background-color: {tema['background']};
                color: {tema['foreground']};
                border: 1px solid #444;
                border-radius: 6px;
                padding: 5px;
                padding-left: {self.satir_numarasi_genislik()}px;
            }}
        ''')

    def satir_numarasi_genislik(self) -> int:
        """Satır numarası alanı genişliğini hesaplar."""
        basamak = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            basamak += 1
        return 10 + self.fontMetrics().horizontalAdvance('9') * basamak

    def _satir_sayisi_degisti(self, _):
        """Satır sayısı değiştiğinde."""
        self.setViewportMargins(self.satir_numarasi_genislik(), 0, 0, 0)

    def _alan_guncelle(self, rect, dy):
        """Görünüm güncellemesi."""
        if dy:
            self.satir_numarasi.scroll(0, dy)
        else:
            self.satir_numarasi.update(0, rect.y(), self.satir_numarasi.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._satir_sayisi_degisti(0)

    def resizeEvent(self, event):
        """Yeniden boyutlandırma."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.satir_numarasi.setGeometry(QRect(cr.left(), cr.top(),
                                              self.satir_numarasi_genislik(), cr.height()))

    def satir_numarasi_ciz(self, event):
        """Satır numaralarını çizer."""
        painter = QPainter(self.satir_numarasi)
        painter.fillRect(event.rect(), QColor('#2d2d2d'))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor('#636d83'))
                painter.drawText(0, top, self.satir_numarasi.width() - 5,
                               self.fontMetrics().height(),
                               Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def dil_degistir(self, dil: str):
        """Dili değiştirir."""
        self.dil = dil
        self.vurgulayici = KodVurgulayici(self.document(), dil)


class KodDilSecici(QFrame):
    """Kod bloğu için dil seçici ve araç çubuğu."""

    dilDegisti = pyqtSignal(str)
    kopyalandi = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Arayüzü oluşturur."""
        self.setStyleSheet('''
            QFrame {
                background-color: #1e1e1e;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 5px;
            }
        ''')

        yerlesim = QHBoxLayout(self)
        yerlesim.setContentsMargins(10, 5, 10, 5)

        # Dil seçici
        self.dil_combo = QComboBox()
        self.dil_combo.addItems(['Python', 'JavaScript', 'HTML', 'CSS', 'SQL', 'JSON', 'Düz Metin'])
        self.dil_combo.setStyleSheet('''
            QComboBox {
                background-color: #2d2d2d;
                color: #f8f8f2;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 100px;
            }
        ''')
        self.dil_combo.currentTextChanged.connect(self._dil_degisti)
        yerlesim.addWidget(self.dil_combo)

        yerlesim.addStretch()

        # Kopyala butonu
        self.kopyala_btn = QPushButton('📋 Kopyala')
        self.kopyala_btn.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                color: #888;
                border: none;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #f8f8f2;
            }
        ''')
        self.kopyala_btn.clicked.connect(self.kopyalandi.emit)
        yerlesim.addWidget(self.kopyala_btn)

    def _dil_degisti(self, dil_adi: str):
        """Dil değiştiğinde."""
        dil_map = {
            'Python': 'python',
            'JavaScript': 'javascript',
            'HTML': 'html',
            'CSS': 'css',
            'SQL': 'sql',
            'JSON': 'json',
            'Düz Metin': 'text'
        }
        self.dilDegisti.emit(dil_map.get(dil_adi, 'text'))


class KodBloguFrame(QFrame):
    """Tam kod bloğu (başlık + editör)."""

    def __init__(self, parent=None, dil: str = 'python', kod: str = ''):
        super().__init__(parent)
        self._arayuz_olustur(dil, kod)

    def _arayuz_olustur(self, dil: str, kod: str):
        """Arayüzü oluşturur."""
        self.setStyleSheet('''
            QFrame {
                border: 1px solid #444;
                border-radius: 6px;
                margin: 5px 0;
            }
        ''')

        yerlesim = QVBoxLayout(self)
        yerlesim.setContentsMargins(0, 0, 0, 0)
        yerlesim.setSpacing(0)

        # Dil seçici
        self.dil_secici = KodDilSecici()
        self.dil_secici.dilDegisti.connect(self._dil_degisti)
        self.dil_secici.kopyalandi.connect(self._kopyala)
        yerlesim.addWidget(self.dil_secici)

        # Kod editörü
        self.editor = KodBloguWidget(dil=dil)
        self.editor.setPlainText(kod)
        self.editor.setMinimumHeight(100)
        yerlesim.addWidget(self.editor)

    def _dil_degisti(self, dil: str):
        """Dil değişikliği."""
        self.editor.dil_degistir(dil)

    def _kopyala(self):
        """Kodu panoya kopyalar."""
        QApplication.clipboard().setText(self.editor.toPlainText())

    def kod_getir(self) -> str:
        """Kodu döndürür."""
        return self.editor.toPlainText()

    def kod_ayarla(self, kod: str):
        """Kodu ayarlar."""
        self.editor.setPlainText(kod)


class KodBloguDialog(QDialog):
    """Kod bloğu ekleme dialogu."""

    kodEklendi = pyqtSignal(str)  # HTML formatında kod

    def __init__(self, parent=None):
        super().__init__(parent)
        self._html_sonuc = None
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Kod Bloğu Ekle')
        self.setMinimumSize(600, 450)

        from PyQt5.QtWidgets import QDialog, QDialogButtonBox

        yerlesim = QVBoxLayout(self)

        # Kod bloğu frame
        self.kod_frame = KodBloguFrame()
        yerlesim.addWidget(self.kod_frame)

        # Butonlar
        butonlar = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        butonlar.accepted.connect(self._onayla)
        butonlar.rejected.connect(self.reject)
        butonlar.button(QDialogButtonBox.Ok).setText('Ekle')
        butonlar.button(QDialogButtonBox.Cancel).setText('İptal')
        yerlesim.addWidget(butonlar)

    def _onayla(self):
        """Kodu HTML olarak hazırlar."""
        kod = self.kod_frame.kod_getir()
        if kod.strip():
            # HTML formatında kod bloğu oluştur
            escaped_kod = kod.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            self._html_sonuc = f'''<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 6px; font-family: Consolas, monospace; font-size: 11pt; overflow-x: auto;"><code>{escaped_kod}</code></pre>'''
            self.kodEklendi.emit(self._html_sonuc)
            self.accept()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir kod girin.')

    def html_getir(self) -> str:
        """HTML formatında kodu döndürür."""
        return self._html_sonuc or ''
