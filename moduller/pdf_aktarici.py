# -*- coding: utf-8 -*-
"""
Not Defteri - PDF Dışa Aktarma Modülü
Notları PDF formatında dışa aktarma.
"""

import os
from datetime import datetime
from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QComboBox, QCheckBox, QSpinBox, QGroupBox,
    QFormLayout, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QMarginsF
from PyQt5.QtGui import QFont, QPageSize, QPageLayout
from PyQt5.QtPrintSupport import QPrinter

try:
    from PyQt5.QtPdf import QPdfWriter
    PDF_WRITER_AVAILABLE = True
except ImportError:
    PDF_WRITER_AVAILABLE = False


class PDFAktarici:
    """Notları PDF olarak dışa aktaran sınıf."""

    def __init__(self):
        self.sayfa_boyutu = QPageSize.A4
        self.kenar_boslugu = 20  # mm
        self.font_boyutu = 11
        self.baslik_ekle = True
        self.tarih_ekle = True

    def html_sablonu_olustur(self, baslik: str, icerik: str, tarih: str = None) -> str:
        """PDF için HTML şablonu oluşturur."""
        tarih_html = ''
        if self.tarih_ekle and tarih:
            tarih_html = f'<p style="color: #666; font-size: 10px; margin-bottom: 20px;">{tarih}</p>'

        baslik_html = ''
        if self.baslik_ekle:
            baslik_html = f'<h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">{baslik}</h1>'

        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: {self.font_boyutu}pt;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }}
        h1 {{ font-size: 18pt; margin-top: 0; }}
        h2 {{ font-size: 14pt; color: #2c3e50; }}
        h3 {{ font-size: 12pt; color: #34495e; }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: Consolas, monospace;
            font-size: 10pt;
        }}
        pre {{
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: Consolas, monospace;
            font-size: 10pt;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 10px 0;
            padding: 10px 20px;
            background-color: #f9f9f9;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f4f4f4;
        }}
        ul, ol {{
            padding-left: 25px;
        }}
        li {{
            margin: 5px 0;
        }}
        .checkbox {{
            font-family: 'Segoe UI Symbol', sans-serif;
        }}
        .checkbox-checked {{
            color: #27ae60;
        }}
        .checkbox-unchecked {{
            color: #bdc3c7;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    {baslik_html}
    {tarih_html}
    <div class="content">
        {icerik}
    </div>
</body>
</html>
'''

    def pdf_olustur(self, hedef_yol: str, baslik: str, html_icerik: str,
                    tarih: str = None) -> bool:
        """
        PDF dosyası oluşturur.

        Args:
            hedef_yol: Kaydedilecek PDF dosya yolu
            baslik: Not başlığı
            html_icerik: HTML formatında içerik
            tarih: Tarih metni

        Returns:
            Başarılı ise True
        """
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
            from PyQt5.QtCore import QUrl, QEventLoop

            # HTML şablonu oluştur
            html = self.html_sablonu_olustur(baslik, html_icerik, tarih)

            # Web view oluştur (görünmez)
            app = QApplication.instance()

            class PdfPage(QWebEnginePage):
                def __init__(self):
                    super().__init__()
                    self.pdf_saved = False

                def save_pdf(self, path):
                    layout = QPageLayout(
                        QPageSize(QPageSize.A4),
                        QPageLayout.Portrait,
                        QMarginsF(20, 20, 20, 20)
                    )
                    self.printToPdf(path, layout)

            page = PdfPage()
            page.setHtml(html)

            loop = QEventLoop()
            page.loadFinished.connect(lambda ok: self._on_load_finished(page, hedef_yol, loop))
            loop.exec_()

            return True

        except ImportError:
            # QtWebEngine yoksa basit yöntem dene
            return self._basit_pdf_olustur(hedef_yol, baslik, html_icerik, tarih)
        except Exception as e:
            print(f"PDF oluşturma hatası: {e}")
            return False

    def _on_load_finished(self, page, path, loop):
        """Sayfa yüklendiğinde PDF oluştur."""
        page.save_pdf(path)
        # Biraz bekle
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, loop.quit)

    def _basit_pdf_olustur(self, hedef_yol: str, baslik: str,
                           html_icerik: str, tarih: str = None) -> bool:
        """
        Basit PDF oluşturma (QtWebEngine olmadan).
        QPrinter kullanarak oluşturur.
        """
        try:
            from PyQt5.QtWidgets import QTextDocument
            from PyQt5.QtPrintSupport import QPrinter

            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(hedef_yol)
            printer.setPageSize(QPageSize(QPageSize.A4))

            # Kenar boşlukları
            printer.setPageMargins(
                QMarginsF(self.kenar_boslugu, self.kenar_boslugu,
                         self.kenar_boslugu, self.kenar_boslugu),
                QPageLayout.Millimeter
            )

            # HTML dökümanı oluştur
            html = self.html_sablonu_olustur(baslik, html_icerik, tarih)

            doc = QTextDocument()
            doc.setHtml(html)
            doc.setPageSize(printer.pageRect().size())
            doc.print_(printer)

            return True

        except Exception as e:
            print(f"Basit PDF oluşturma hatası: {e}")
            return False

    def coklu_pdf_olustur(self, hedef_klasor: str, notlar: list) -> dict:
        """
        Birden fazla notu PDF olarak dışa aktarır.

        Args:
            hedef_klasor: Hedef klasör yolu
            notlar: Not listesi [{'baslik': str, 'icerik': str, 'tarih': str}, ...]

        Returns:
            {'basarili': int, 'basarisiz': int, 'hatalar': []}
        """
        sonuc = {'basarili': 0, 'basarisiz': 0, 'hatalar': []}

        for not_verisi in notlar:
            baslik = not_verisi.get('baslik', 'Başlıksız')
            # Dosya adı için uygun karakter
            guvenli_ad = "".join(c for c in baslik if c.isalnum() or c in ' -_').strip()
            dosya_adi = f"{guvenli_ad}.pdf"
            hedef_yol = os.path.join(hedef_klasor, dosya_adi)

            basari = self.pdf_olustur(
                hedef_yol,
                baslik,
                not_verisi.get('zengin_icerik', not_verisi.get('icerik', '')),
                not_verisi.get('tarih')
            )

            if basari:
                sonuc['basarili'] += 1
            else:
                sonuc['basarisiz'] += 1
                sonuc['hatalar'].append(baslik)

        return sonuc


class PDFAktarmaDialog(QDialog):
    """PDF dışa aktarma ayarları dialogu."""

    aktarildi = pyqtSignal(str)  # Dosya yolu

    def __init__(self, parent=None, baslik: str = '', icerik: str = ''):
        super().__init__(parent)
        self.baslik = baslik
        self.icerik = icerik
        self.aktarici = PDFAktarici()
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('PDF Olarak Dışa Aktar')
        self.setMinimumWidth(400)

        yerlesim = QVBoxLayout(self)

        # Bilgi
        bilgi = QLabel(f'📄 "{self.baslik}" notunu PDF olarak kaydet')
        bilgi.setFont(QFont('Segoe UI', 11, QFont.Bold))
        yerlesim.addWidget(bilgi)

        # Ayarlar grubu
        ayarlar_grup = QGroupBox('Ayarlar')
        ayarlar_yerlesim = QFormLayout(ayarlar_grup)

        # Sayfa boyutu
        self.sayfa_combo = QComboBox()
        self.sayfa_combo.addItems(['A4', 'A5', 'Letter', 'Legal'])
        ayarlar_yerlesim.addRow('Sayfa Boyutu:', self.sayfa_combo)

        # Kenar boşluğu
        self.kenar_spin = QSpinBox()
        self.kenar_spin.setRange(5, 50)
        self.kenar_spin.setValue(20)
        self.kenar_spin.setSuffix(' mm')
        ayarlar_yerlesim.addRow('Kenar Boşluğu:', self.kenar_spin)

        # Font boyutu
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 16)
        self.font_spin.setValue(11)
        self.font_spin.setSuffix(' pt')
        ayarlar_yerlesim.addRow('Font Boyutu:', self.font_spin)

        yerlesim.addWidget(ayarlar_grup)

        # Seçenekler
        secenek_grup = QGroupBox('Seçenekler')
        secenek_yerlesim = QVBoxLayout(secenek_grup)

        self.baslik_check = QCheckBox('Başlık ekle')
        self.baslik_check.setChecked(True)
        secenek_yerlesim.addWidget(self.baslik_check)

        self.tarih_check = QCheckBox('Tarih ekle')
        self.tarih_check.setChecked(True)
        secenek_yerlesim.addWidget(self.tarih_check)

        yerlesim.addWidget(secenek_grup)

        # Butonlar
        buton_yerlesim = QHBoxLayout()

        iptal_btn = QPushButton('İptal')
        iptal_btn.clicked.connect(self.reject)
        buton_yerlesim.addWidget(iptal_btn)

        buton_yerlesim.addStretch()

        self.aktar_btn = QPushButton('📥 PDF Olarak Kaydet')
        self.aktar_btn.clicked.connect(self._aktar)
        buton_yerlesim.addWidget(self.aktar_btn)

        yerlesim.addLayout(buton_yerlesim)

    def _aktar(self):
        """PDF olarak dışa aktarır."""
        # Dosya yolu seç
        guvenli_ad = "".join(c for c in self.baslik if c.isalnum() or c in ' -_').strip()
        dosya, _ = QFileDialog.getSaveFileName(
            self, 'PDF Olarak Kaydet',
            f'{guvenli_ad}.pdf',
            'PDF Dosyaları (*.pdf)'
        )

        if not dosya:
            return

        # Ayarları uygula
        sayfa_map = {
            'A4': QPageSize.A4,
            'A5': QPageSize.A5,
            'Letter': QPageSize.Letter,
            'Legal': QPageSize.Legal
        }
        self.aktarici.sayfa_boyutu = sayfa_map.get(self.sayfa_combo.currentText(), QPageSize.A4)
        self.aktarici.kenar_boslugu = self.kenar_spin.value()
        self.aktarici.font_boyutu = self.font_spin.value()
        self.aktarici.baslik_ekle = self.baslik_check.isChecked()
        self.aktarici.tarih_ekle = self.tarih_check.isChecked()

        # PDF oluştur
        tarih = datetime.now().strftime('%d.%m.%Y %H:%M')
        basari = self.aktarici.pdf_olustur(dosya, self.baslik, self.icerik, tarih)

        if basari:
            self.aktarildi.emit(dosya)
            QMessageBox.information(self, 'Başarılı', f'PDF başarıyla kaydedildi:\n{dosya}')
            self.accept()
        else:
            QMessageBox.warning(self, 'Hata', 'PDF oluşturulurken bir hata oluştu.')
