# -*- coding: utf-8 -*-
"""
Not Defteri - Not Şablonları Modülü
Hazır not şablonları ve özelleştirme.
"""

from datetime import datetime
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QGroupBox, QFormLayout, QMessageBox, QFrame, QScrollArea,
    QWidget, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor


# Varsayılan şablonlar
VARSAYILAN_SABLONLAR = [
    {
        'ad': 'Boş Not',
        'ikon': '📝',
        'aciklama': 'Boş bir not',
        'baslik': 'Yeni Not',
        'icerik': ''
    },
    {
        'ad': 'Günlük',
        'ikon': '📅',
        'aciklama': 'Günlük giriş şablonu',
        'baslik': '{tarih} - Günlük',
        'icerik': '''## {tarih_uzun}

### Bugün nasıl hissediyorum?


### Bugün neler yaptım?


### Yarın için hedefler:
- [ ]
- [ ]
- [ ]

### Notlar:

'''
    },
    {
        'ad': 'Toplantı Notu',
        'ikon': '👥',
        'aciklama': 'Toplantı kayıt şablonu',
        'baslik': 'Toplantı: ',
        'icerik': '''## Toplantı Bilgileri
- **Tarih:** {tarih}
- **Saat:**
- **Yer:**
- **Katılımcılar:**

---

## Gündem
1.
2.
3.

---

## Notlar


---

## Alınan Kararlar
-

---

## Aksiyon Maddeleri
- [ ]
- [ ]

---

## Sonraki Toplantı
- **Tarih:**
- **Gündem:**
'''
    },
    {
        'ad': 'Proje Planı',
        'ikon': '🎯',
        'aciklama': 'Proje planlama şablonu',
        'baslik': 'Proje: ',
        'icerik': '''## Proje Özeti
**Proje Adı:**
**Başlangıç Tarihi:** {tarih}
**Bitiş Tarihi:**
**Sorumlu:**

---

## Hedefler
1.
2.
3.

---

## Kapsam
### Dahil:
-

### Hariç:
-

---

## Zaman Çizelgesi
| Aşama | Başlangıç | Bitiş | Durum |
|-------|-----------|-------|-------|
| Planlama | | | ⏳ |
| Geliştirme | | | |
| Test | | | |
| Yayın | | | |

---

## Riskler ve Sorunlar
| Risk | Olasılık | Etki | Azaltma |
|------|----------|------|---------|
| | | | |

---

## Kaynaklar
-

---

## Notlar

'''
    },
    {
        'ad': 'Haftalık Planlama',
        'ikon': '📆',
        'aciklama': 'Haftalık plan şablonu',
        'baslik': 'Hafta {hafta_no} Planı',
        'icerik': '''## Hafta {hafta_no} ({hafta_baslangic} - {hafta_bitis})

### Bu Haftanın Hedefleri
1.
2.
3.

---

### Pazartesi
- [ ]

### Salı
- [ ]

### Çarşamba
- [ ]

### Perşembe
- [ ]

### Cuma
- [ ]

### Hafta Sonu
- [ ]

---

### Haftalık Değerlendirme
**Tamamlanan:**

**Ertelenen:**

**Öğrenilen:**

'''
    },
    {
        'ad': 'Fikir Notu',
        'ikon': '💡',
        'aciklama': 'Fikir ve beyin fırtınası',
        'baslik': 'Fikir: ',
        'icerik': '''## Fikir Özeti


---

## Problem / Fırsat
Ne sorunu çözüyor veya hangi fırsatı değerlendiriyor?


---

## Çözüm Önerisi


---

## Faydalar
-

---

## Zorluklar
-

---

## Sonraki Adımlar
- [ ] Araştır
- [ ] Prototip yap
- [ ] Geri bildirim al

---

## Kaynaklar / Referanslar
-
'''
    },
    {
        'ad': 'Kitap Notu',
        'ikon': '📚',
        'aciklama': 'Kitap okuma notları',
        'baslik': 'Kitap: ',
        'icerik': '''## Kitap Bilgileri
- **Kitap Adı:**
- **Yazar:**
- **Başlama Tarihi:** {tarih}
- **Bitiş Tarihi:**
- **Puan:** ⭐⭐⭐⭐⭐

---

## Özet


---

## Önemli Alıntılar
>

---

## Öğrendiklerim
1.
2.
3.

---

## Uygulayacaklarım
- [ ]

---

## Benzer Kitaplar
-
'''
    },
    {
        'ad': 'Yapılacaklar',
        'ikon': '✅',
        'aciklama': 'Basit yapılacaklar listesi',
        'baslik': 'Yapılacaklar - {tarih}',
        'icerik': '''## Öncelikli
- [ ]
- [ ]
- [ ]

## Normal
- [ ]
- [ ]

## Düşük Öncelik
- [ ]

---

## Notlar

'''
    },
    {
        'ad': 'Problem Çözme',
        'ikon': '🔧',
        'aciklama': 'Problem analizi şablonu',
        'baslik': 'Problem: ',
        'icerik': '''## Problem Tanımı


---

## Etkilenen Alan


---

## Kök Neden Analizi
### 5 Neden:
1. Neden? →
2. Neden? →
3. Neden? →
4. Neden? →
5. Neden? →

---

## Olası Çözümler
| Çözüm | Artıları | Eksileri | Maliyet |
|-------|----------|----------|---------|
| | | | |

---

## Seçilen Çözüm


---

## Uygulama Adımları
- [ ]
- [ ]

---

## Sonuç ve Öğrenilen

'''
    }
]


class SablonYoneticisi:
    """Not şablonlarını yöneten sınıf."""

    def __init__(self, veritabani=None):
        self.vt = veritabani
        self.sablonlar = VARSAYILAN_SABLONLAR.copy()
        self._ozel_sablonlari_yukle()

    def _ozel_sablonlari_yukle(self):
        """Kullanıcı tanımlı şablonları yükler."""
        if self.vt:
            try:
                import json
                ozel = self.vt.ayar_getir('ozel_sablonlar')
                if ozel:
                    self.sablonlar.extend(json.loads(ozel))
            except:
                pass

    def _ozel_sablonlari_kaydet(self):
        """Kullanıcı tanımlı şablonları kaydeder."""
        if self.vt:
            import json
            # Sadece özel şablonları kaydet
            ozel = [s for s in self.sablonlar if s not in VARSAYILAN_SABLONLAR]
            self.vt.ayar_kaydet('ozel_sablonlar', json.dumps(ozel, ensure_ascii=False))

    def sablon_listesi(self) -> List[Dict]:
        """Tüm şablonları döndürür."""
        return self.sablonlar

    def sablon_getir(self, ad: str) -> Optional[Dict]:
        """İsme göre şablon döndürür."""
        for sablon in self.sablonlar:
            if sablon['ad'] == ad:
                return sablon
        return None

    def sablon_uygula(self, sablon: Dict) -> tuple:
        """
        Şablonu uygular ve değişkenleri doldurur.

        Returns:
            (baslik, icerik)
        """
        baslik = sablon.get('baslik', 'Yeni Not')
        icerik = sablon.get('icerik', '')

        # Tarih değişkenlerini doldur
        simdi = datetime.now()
        degiskenler = {
            '{tarih}': simdi.strftime('%d.%m.%Y'),
            '{tarih_uzun}': simdi.strftime('%d %B %Y, %A'),
            '{saat}': simdi.strftime('%H:%M'),
            '{yil}': str(simdi.year),
            '{ay}': simdi.strftime('%B'),
            '{gun}': simdi.strftime('%A'),
            '{hafta_no}': str(simdi.isocalendar()[1]),
            '{hafta_baslangic}': (simdi - __import__('datetime').timedelta(days=simdi.weekday())).strftime('%d.%m'),
            '{hafta_bitis}': (simdi + __import__('datetime').timedelta(days=6-simdi.weekday())).strftime('%d.%m'),
        }

        for anahtar, deger in degiskenler.items():
            baslik = baslik.replace(anahtar, deger)
            icerik = icerik.replace(anahtar, deger)

        return baslik, icerik

    def sablon_ekle(self, ad: str, ikon: str, aciklama: str, baslik: str, icerik: str) -> bool:
        """Yeni şablon ekler."""
        if any(s['ad'] == ad for s in self.sablonlar):
            return False

        yeni_sablon = {
            'ad': ad,
            'ikon': ikon,
            'aciklama': aciklama,
            'baslik': baslik,
            'icerik': icerik,
            'ozel': True
        }
        self.sablonlar.append(yeni_sablon)
        self._ozel_sablonlari_kaydet()
        return True

    def sablon_sil(self, ad: str) -> bool:
        """Şablonu siler (sadece özel şablonlar)."""
        for i, sablon in enumerate(self.sablonlar):
            if sablon['ad'] == ad and sablon.get('ozel'):
                del self.sablonlar[i]
                self._ozel_sablonlari_kaydet()
                return True
        return False


class SablonKarti(QFrame):
    """Şablon seçim kartı."""

    secildi = pyqtSignal(dict)  # şablon verisi

    def __init__(self, sablon: Dict, parent=None):
        super().__init__(parent)
        self.sablon = sablon
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Kart arayüzünü oluşturur."""
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(150, 120)
        self.setStyleSheet('''
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        ''')

        yerlesim = QVBoxLayout(self)
        yerlesim.setAlignment(Qt.AlignCenter)

        # İkon
        ikon = QLabel(self.sablon.get('ikon', '📝'))
        ikon.setStyleSheet('font-size: 32px;')
        ikon.setAlignment(Qt.AlignCenter)
        yerlesim.addWidget(ikon)

        # Ad
        ad = QLabel(self.sablon.get('ad', 'Şablon'))
        ad.setFont(QFont('Segoe UI', 10, QFont.Bold))
        ad.setAlignment(Qt.AlignCenter)
        ad.setWordWrap(True)
        yerlesim.addWidget(ad)

    def mousePressEvent(self, event):
        """Tıklama olayı."""
        if event.button() == Qt.LeftButton:
            self.secildi.emit(self.sablon)
        super().mousePressEvent(event)


class SablonSeciciDialog(QDialog):
    """Şablon seçme dialogu."""

    sablonSecildi = pyqtSignal(str, str)  # baslik, icerik

    def __init__(self, parent=None, sablon_yoneticisi=None):
        super().__init__(parent)
        self.yonetici = sablon_yoneticisi or SablonYoneticisi()
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Şablon Seç')
        self.setMinimumSize(600, 450)

        yerlesim = QVBoxLayout(self)

        # Başlık
        baslik = QLabel('📋 Şablon ile Başla')
        baslik.setFont(QFont('Segoe UI', 14, QFont.Bold))
        yerlesim.addWidget(baslik)

        aciklama = QLabel('Hızlıca başlamak için bir şablon seçin')
        aciklama.setStyleSheet('color: gray;')
        yerlesim.addWidget(aciklama)

        # Şablon grid'i
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        grid_widget = QWidget()
        self.grid = QGridLayout(grid_widget)
        self.grid.setSpacing(15)

        sablonlar = self.yonetici.sablon_listesi()
        row, col = 0, 0
        max_col = 4

        for sablon in sablonlar:
            kart = SablonKarti(sablon)
            kart.secildi.connect(self._sablon_sec)
            self.grid.addWidget(kart, row, col)

            col += 1
            if col >= max_col:
                col = 0
                row += 1

        scroll.setWidget(grid_widget)
        yerlesim.addWidget(scroll)

        # Alt butonlar
        buton_yerlesim = QHBoxLayout()

        self.ozel_btn = QPushButton('➕ Özel Şablon Oluştur')
        self.ozel_btn.clicked.connect(self._ozel_sablon_olustur)
        buton_yerlesim.addWidget(self.ozel_btn)

        buton_yerlesim.addStretch()

        kapat_btn = QPushButton('Kapat')
        kapat_btn.clicked.connect(self.reject)
        buton_yerlesim.addWidget(kapat_btn)

        yerlesim.addLayout(buton_yerlesim)

    def _sablon_sec(self, sablon: Dict):
        """Şablon seçildiğinde."""
        baslik, icerik = self.yonetici.sablon_uygula(sablon)
        self.sablonSecildi.emit(baslik, icerik)
        self.accept()

    def _ozel_sablon_olustur(self):
        """Özel şablon oluşturma dialogu."""
        dialog = OzelSablonDialog(self, self.yonetici)
        if dialog.exec_():
            # Grid'i yenile
            # Basit yenileme için dialogu kapat ve yeniden aç
            pass


class OzelSablonDialog(QDialog):
    """Özel şablon oluşturma dialogu."""

    def __init__(self, parent=None, sablon_yoneticisi=None):
        super().__init__(parent)
        self.yonetici = sablon_yoneticisi
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        self.setWindowTitle('Özel Şablon Oluştur')
        self.setMinimumSize(500, 500)

        yerlesim = QVBoxLayout(self)

        # Form
        form = QFormLayout()

        self.ad_input = QLineEdit()
        self.ad_input.setPlaceholderText('Şablon adı')
        form.addRow('Ad:', self.ad_input)

        self.ikon_input = QLineEdit()
        self.ikon_input.setPlaceholderText('Emoji ikon (örn: 📝)')
        self.ikon_input.setMaxLength(2)
        form.addRow('İkon:', self.ikon_input)

        self.aciklama_input = QLineEdit()
        self.aciklama_input.setPlaceholderText('Kısa açıklama')
        form.addRow('Açıklama:', self.aciklama_input)

        self.baslik_input = QLineEdit()
        self.baslik_input.setPlaceholderText('Varsayılan başlık ({tarih} kullanılabilir)')
        form.addRow('Başlık:', self.baslik_input)

        yerlesim.addLayout(form)

        # İçerik
        yerlesim.addWidget(QLabel('İçerik:'))
        self.icerik_edit = QTextEdit()
        self.icerik_edit.setPlaceholderText(
            'Şablon içeriği...\n\n'
            'Değişkenler:\n'
            '{tarih} - 01.01.2024\n'
            '{tarih_uzun} - 01 Ocak 2024, Pazartesi\n'
            '{hafta_no} - Hafta numarası'
        )
        yerlesim.addWidget(self.icerik_edit)

        # Butonlar
        buton_yerlesim = QHBoxLayout()

        iptal_btn = QPushButton('İptal')
        iptal_btn.clicked.connect(self.reject)
        buton_yerlesim.addWidget(iptal_btn)

        buton_yerlesim.addStretch()

        kaydet_btn = QPushButton('Kaydet')
        kaydet_btn.clicked.connect(self._kaydet)
        buton_yerlesim.addWidget(kaydet_btn)

        yerlesim.addLayout(buton_yerlesim)

    def _kaydet(self):
        """Şablonu kaydeder."""
        ad = self.ad_input.text().strip()
        if not ad:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir ad girin.')
            return

        basari = self.yonetici.sablon_ekle(
            ad=ad,
            ikon=self.ikon_input.text() or '📝',
            aciklama=self.aciklama_input.text(),
            baslik=self.baslik_input.text() or 'Yeni Not',
            icerik=self.icerik_edit.toPlainText()
        )

        if basari:
            self.accept()
        else:
            QMessageBox.warning(self, 'Hata', 'Bu isimde bir şablon zaten var.')
