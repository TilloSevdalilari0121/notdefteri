# -*- coding: utf-8 -*-
"""
Not Defteri Uygulaması - Stil ve Tema Modülü
Uygulama için karanlık ve aydınlık tema stilleri.

Yazar: Claude AI
Tarih: 2024
"""


class TemaYoneticisi:
    """Uygulama temalarını yöneten sınıf."""

    AYDINLIK_TEMA = {
        'ad': 'aydinlik',
        'baslik': 'Aydınlık Tema',
        'arkaplan': '#f5f5f5',
        'arkaplan_alternatif': '#ffffff',
        'kenar_cubugu': '#e8e8e8',
        'metin': '#333333',
        'metin_soluk': '#666666',
        'vurgu': '#2196F3',
        'vurgu_hover': '#1976D2',
        'tehlike': '#f44336',
        'basari': '#4CAF50',
        'uyari': '#FF9800',
        'kenarlık': '#dddddd',
        'secili': '#e3f2fd',
        'hover': '#eeeeee',
    }

    KARANLIK_TEMA = {
        'ad': 'karanlik',
        'baslik': 'Karanlık Tema',
        'arkaplan': '#1e1e1e',
        'arkaplan_alternatif': '#252526',
        'kenar_cubugu': '#333333',
        'metin': '#e0e0e0',
        'metin_soluk': '#888888',
        'vurgu': '#4fc3f7',
        'vurgu_hover': '#29b6f6',
        'tehlike': '#ef5350',
        'basari': '#66bb6a',
        'uyari': '#ffa726',
        'kenarlık': '#404040',
        'secili': '#37474f',
        'hover': '#3a3a3a',
    }

    @classmethod
    def tema_getir(cls, tema_adi: str) -> dict:
        """Tema renklerini getirir."""
        if tema_adi == 'karanlik':
            return cls.KARANLIK_TEMA
        return cls.AYDINLIK_TEMA

    @classmethod
    def stil_olustur(cls, tema_adi: str) -> str:
        """Tema için QSS stil dizesi oluşturur."""
        tema = cls.tema_getir(tema_adi)

        return f'''
        /* Ana Pencere */
        QMainWindow {{
            background-color: {tema['arkaplan']};
        }}

        /* Genel Widget */
        QWidget {{
            background-color: {tema['arkaplan']};
            color: {tema['metin']};
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 13px;
        }}

        /* Etiketler */
        QLabel {{
            color: {tema['metin']};
            background-color: transparent;
        }}

        /* Düğmeler */
        QPushButton {{
            background-color: {tema['vurgu']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {tema['vurgu_hover']};
        }}

        QPushButton:pressed {{
            background-color: {tema['vurgu_hover']};
            padding-top: 9px;
        }}

        QPushButton:disabled {{
            background-color: {tema['kenar_cubugu']};
            color: {tema['metin_soluk']};
        }}

        QPushButton#tehlikeDugme {{
            background-color: {tema['tehlike']};
        }}

        QPushButton#tehlikeDugme:hover {{
            background-color: #d32f2f;
        }}

        QPushButton#ikinciDugme {{
            background-color: transparent;
            color: {tema['vurgu']};
            border: 2px solid {tema['vurgu']};
        }}

        QPushButton#ikinciDugme:hover {{
            background-color: {tema['secili']};
        }}

        /* Metin Girişleri */
        QLineEdit {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['metin']};
            border: 2px solid {tema['kenarlık']};
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: {tema['vurgu']};
        }}

        QLineEdit:focus {{
            border-color: {tema['vurgu']};
        }}

        QLineEdit::placeholder {{
            color: {tema['metin_soluk']};
        }}

        /* Metin Alanı */
        QTextEdit, QPlainTextEdit {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['metin']};
            border: 2px solid {tema['kenarlık']};
            border-radius: 6px;
            padding: 8px;
            selection-background-color: {tema['vurgu']};
        }}

        QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {tema['vurgu']};
        }}

        /* Liste Widget */
        QListWidget {{
            background-color: {tema['arkaplan_alternatif']};
            border: 1px solid {tema['kenarlık']};
            border-radius: 8px;
            padding: 4px;
            outline: none;
        }}

        QListWidget::item {{
            background-color: transparent;
            color: {tema['metin']};
            border-radius: 6px;
            padding: 10px 12px;
            margin: 2px 0px;
        }}

        QListWidget::item:hover {{
            background-color: {tema['hover']};
        }}

        QListWidget::item:selected {{
            background-color: {tema['secili']};
            color: {tema['vurgu']};
        }}

        /* Ağaç Widget */
        QTreeWidget {{
            background-color: {tema['arkaplan_alternatif']};
            border: 1px solid {tema['kenarlık']};
            border-radius: 8px;
            padding: 4px;
            outline: none;
        }}

        QTreeWidget::item {{
            padding: 8px;
            border-radius: 4px;
        }}

        QTreeWidget::item:hover {{
            background-color: {tema['hover']};
        }}

        QTreeWidget::item:selected {{
            background-color: {tema['secili']};
            color: {tema['vurgu']};
        }}

        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(icons/branch-closed.png);
        }}

        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(icons/branch-open.png);
        }}

        /* Açılır Kutu */
        QComboBox {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['metin']};
            border: 2px solid {tema['kenarlık']};
            border-radius: 6px;
            padding: 8px 12px;
            min-height: 20px;
        }}

        QComboBox:hover {{
            border-color: {tema['vurgu']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {tema['metin']};
            margin-right: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['metin']};
            border: 1px solid {tema['kenarlık']};
            border-radius: 6px;
            selection-background-color: {tema['secili']};
            outline: none;
        }}

        /* Kaydırma Çubuğu */
        QScrollBar:vertical {{
            background-color: {tema['arkaplan']};
            width: 12px;
            margin: 0;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {tema['kenar_cubugu']};
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {tema['metin_soluk']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QScrollBar:horizontal {{
            background-color: {tema['arkaplan']};
            height: 12px;
            margin: 0;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {tema['kenar_cubugu']};
            min-width: 30px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {tema['metin_soluk']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}

        /* Sekmeler */
        QTabWidget::pane {{
            border: 1px solid {tema['kenarlık']};
            border-radius: 8px;
            background-color: {tema['arkaplan_alternatif']};
        }}

        QTabBar::tab {{
            background-color: {tema['kenar_cubugu']};
            color: {tema['metin']};
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['vurgu']};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {tema['hover']};
        }}

        /* Ayırıcı */
        QSplitter::handle {{
            background-color: {tema['kenarlık']};
        }}

        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        QSplitter::handle:vertical {{
            height: 2px;
        }}

        /* Menü */
        QMenuBar {{
            background-color: {tema['kenar_cubugu']};
            color: {tema['metin']};
            padding: 4px;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QMenuBar::item:selected {{
            background-color: {tema['hover']};
        }}

        QMenu {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['metin']};
            border: 1px solid {tema['kenarlık']};
            border-radius: 8px;
            padding: 8px;
        }}

        QMenu::item {{
            padding: 8px 24px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background-color: {tema['secili']};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {tema['kenarlık']};
            margin: 4px 8px;
        }}

        /* Araç Çubuğu */
        QToolBar {{
            background-color: {tema['kenar_cubugu']};
            border: none;
            padding: 4px;
            spacing: 4px;
        }}

        QToolButton {{
            background-color: transparent;
            color: {tema['metin']};
            border: none;
            border-radius: 6px;
            padding: 8px;
        }}

        QToolButton:hover {{
            background-color: {tema['hover']};
        }}

        QToolButton:pressed, QToolButton:checked {{
            background-color: {tema['secili']};
            color: {tema['vurgu']};
        }}

        /* Durum Çubuğu */
        QStatusBar {{
            background-color: {tema['kenar_cubugu']};
            color: {tema['metin_soluk']};
        }}

        /* Grup Kutusu */
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {tema['kenarlık']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 6px;
            background-color: {tema['arkaplan']};
        }}

        /* Onay Kutusu */
        QCheckBox {{
            color: {tema['metin']};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {tema['kenarlık']};
            border-radius: 4px;
            background-color: {tema['arkaplan_alternatif']};
        }}

        QCheckBox::indicator:hover {{
            border-color: {tema['vurgu']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {tema['vurgu']};
            border-color: {tema['vurgu']};
        }}

        /* Radyo Düğmesi */
        QRadioButton {{
            color: {tema['metin']};
            spacing: 8px;
        }}

        QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {tema['kenarlık']};
            border-radius: 10px;
            background-color: {tema['arkaplan_alternatif']};
        }}

        QRadioButton::indicator:hover {{
            border-color: {tema['vurgu']};
        }}

        QRadioButton::indicator:checked {{
            background-color: {tema['vurgu']};
            border-color: {tema['vurgu']};
        }}

        /* Kaydırıcı */
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background-color: {tema['kenar_cubugu']};
            border-radius: 3px;
        }}

        QSlider::handle:horizontal {{
            background-color: {tema['vurgu']};
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}

        QSlider::handle:horizontal:hover {{
            background-color: {tema['vurgu_hover']};
        }}

        /* İlerleme Çubuğu */
        QProgressBar {{
            border: none;
            border-radius: 6px;
            background-color: {tema['kenar_cubugu']};
            text-align: center;
            color: {tema['metin']};
        }}

        QProgressBar::chunk {{
            background-color: {tema['vurgu']};
            border-radius: 6px;
        }}

        /* Tarih/Saat Düzenleyici */
        QDateTimeEdit, QDateEdit, QTimeEdit {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['metin']};
            border: 2px solid {tema['kenarlık']};
            border-radius: 6px;
            padding: 8px;
        }}

        QDateTimeEdit:focus, QDateEdit:focus, QTimeEdit:focus {{
            border-color: {tema['vurgu']};
        }}

        /* Takvim Widget */
        QCalendarWidget {{
            background-color: {tema['arkaplan_alternatif']};
        }}

        QCalendarWidget QToolButton {{
            color: {tema['metin']};
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }}

        QCalendarWidget QToolButton:hover {{
            background-color: {tema['hover']};
        }}

        QCalendarWidget QSpinBox {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['metin']};
            border: 1px solid {tema['kenarlık']};
            border-radius: 4px;
        }}

        QCalendarWidget QTableView {{
            background-color: {tema['arkaplan_alternatif']};
            selection-background-color: {tema['vurgu']};
            selection-color: white;
        }}

        /* Araç İpucu */
        QToolTip {{
            background-color: {tema['arkaplan_alternatif']};
            color: {tema['metin']};
            border: 1px solid {tema['kenarlık']};
            border-radius: 4px;
            padding: 6px;
        }}

        /* Özel Sınıflar */
        .baslikEtiket {{
            font-size: 24px;
            font-weight: bold;
            color: {tema['metin']};
        }}

        .altBaslikEtiket {{
            font-size: 14px;
            color: {tema['metin_soluk']};
        }}

        .kartWidget {{
            background-color: {tema['arkaplan_alternatif']};
            border: 1px solid {tema['kenarlık']};
            border-radius: 12px;
            padding: 16px;
        }}

        .kenarCubugu {{
            background-color: {tema['kenar_cubugu']};
            border-right: 1px solid {tema['kenarlık']};
        }}

        #aramaCubugu {{
            background-color: {tema['arkaplan_alternatif']};
            border: 2px solid {tema['kenarlık']};
            border-radius: 20px;
            padding: 8px 16px;
            padding-left: 36px;
        }}

        #aramaCubugu:focus {{
            border-color: {tema['vurgu']};
        }}

        #favoriDugme {{
            background-color: transparent;
            border: none;
            font-size: 18px;
        }}

        #favoriDugme:hover {{
            background-color: {tema['hover']};
        }}

        #kategoriRenk {{
            border-radius: 3px;
            min-width: 6px;
            max-width: 6px;
        }}

        #notKarti {{
            background-color: {tema['arkaplan_alternatif']};
            border: 1px solid {tema['kenarlık']};
            border-radius: 8px;
            padding: 12px;
        }}

        #notKarti:hover {{
            border-color: {tema['vurgu']};
            background-color: {tema['hover']};
        }}

        #etiketChip {{
            background-color: {tema['secili']};
            color: {tema['vurgu']};
            border-radius: 12px;
            padding: 4px 10px;
            font-size: 11px;
        }}
        '''


# Renk paleti - Kategoriler ve etiketler için
RENK_PALETI = [
    '#e74c3c',  # Kırmızı
    '#e67e22',  # Turuncu
    '#f1c40f',  # Sarı
    '#2ecc71',  # Yeşil
    '#1abc9c',  # Turkuaz
    '#3498db',  # Mavi
    '#9b59b6',  # Mor
    '#e91e63',  # Pembe
    '#795548',  # Kahverengi
    '#607d8b',  # Mavi Gri
    '#00bcd4',  # Camgöbeği
    '#8bc34a',  # Açık Yeşil
]

# Emoji ikonları - Kategoriler için
KATEGORI_IKONLARI = [
    '📝', '📁', '📌', '⭐', '💡', '🎯', '📚', '💼',
    '🏠', '💰', '🎮', '🎵', '🍕', '✈️', '🏃', '❤️',
    '🔧', '📊', '🎨', '📷', '🌟', '🔔', '📅', '🎁'
]
