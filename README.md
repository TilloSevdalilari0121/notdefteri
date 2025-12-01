# Not Defteri Pro

Gelişmiş özelliklerle donatılmış, Türkçe arayüzlü masaüstü not alma uygulaması.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## Özellikler

### Temel Özellikler
- Zengin metin düzenleme (kalın, italik, altı çizili, renkler, listeler)
- Kategori ve etiket sistemi ile not organizasyonu
- Favori notlar ve çöp kutusu
- Aydınlık/Karanlık tema desteği
- Gelişmiş arama ve filtreleme

### Gelişmiş Özellikler
- **Git Takip**: GitHub repolarını takip edin, yeni commit bildirimleri alın
- **Sürüm Geçmişi**: Notlarınızın geçmiş versiyonlarını görüntüleyin
- **Şifreli Notlar**: AES şifreleme ile notlarınızı koruyun
- **Hatırlatıcılar**: Notlara hatırlatıcı ekleyin
- **Takvim Görünümü**: Notlarınızı takvimde görüntüleyin
- **Markdown Desteği**: Markdown formatında yazın
- **Kod Bloğu**: Sözdizimi vurgulama ile kod blokları
- **Web Clipper**: Web sayfalarından içerik kaydedin
- **PDF Aktarımı**: Notları PDF olarak dışa aktarın
- **Çeviri**: Notları farklı dillere çevirin
- **Bulut Senkronizasyon**: Google Drive ve Dropbox desteği
- **Şablonlar**: Hazır not şablonları kullanın

## Kurulum

### Gereksinimler
- Python 3.11 veya üzeri
- Windows işletim sistemi

### Bağımlılıkları Yükleme

**Tüm özellikler için:**
```bash
pip install -r requirements.txt
```

**Sadece temel özellikler için:**
```bash
pip install PyQt5>=5.15.9
```

**Seçmeli kurulum:**
```bash
# Şifreleme ile
pip install PyQt5 cryptography

# Markdown ile
pip install PyQt5 markdown Pygments

# Web clipper ile
pip install PyQt5 beautifulsoup4 readability-lxml lxml

# Çeviri ile
pip install PyQt5 deep-translator

# Bulut senkronizasyon ile
pip install PyQt5 google-api-python-client google-auth-httplib2 google-auth-oauthlib dropbox
```

### Uygulamayı Çalıştırma

```bash
python ana_uygulama.py
```

## EXE Haline Getirme

### PyInstaller ile

**1. PyInstaller Kurulumu:**
```bash
pip install pyinstaller
```

**2. Tek Dosya EXE Oluşturma:**
```bash
pyinstaller --onefile --windowed --name "NotDefteriPro" --icon=icon.ico ana_uygulama.py
```

**3. Klasör Yapısıyla EXE Oluşturma (Daha hızlı başlatma):**
```bash
pyinstaller --windowed --name "NotDefteriPro" --icon=icon.ico ana_uygulama.py
```

**4. Spec Dosyası ile Detaylı Yapılandırma:**

`NotDefteriPro.spec` dosyası oluşturun:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ana_uygulama.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('moduller', 'moduller'),
    ],
    hiddenimports=[
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'cryptography',
        'markdown',
        'Pygments',
        'bs4',
        'deep_translator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NotDefteriPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
```

Ardından çalıştırın:
```bash
pyinstaller NotDefteriPro.spec
```

### Cx_Freeze ile (Alternatif)

**1. Cx_Freeze Kurulumu:**
```bash
pip install cx_Freeze
```

**2. setup.py Dosyası Oluşturun:**
```python
from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": [
        "PyQt5",
        "sqlite3",
        "json",
        "os",
        "sys",
        "datetime",
    ],
    "includes": [
        "moduller",
        "bilesenler",
        "veritabani",
        "stiller",
    ],
    "excludes": ["tkinter"],
    "include_files": [
        ("moduller", "moduller"),
    ],
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="NotDefteriPro",
    version="1.0.0",
    description="Gelişmiş Not Defteri Uygulaması",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "ana_uygulama.py",
            base=base,
            target_name="NotDefteriPro.exe",
            icon="icon.ico",
        )
    ],
)
```

**3. EXE Oluşturma:**
```bash
python setup.py build
```

### Önemli Notlar

- EXE oluştururken tüm bağımlılıkların yüklü olduğundan emin olun
- `--onefile` seçeneği daha yavaş başlatma süresi verir ama tek dosya oluşturur
- `--windowed` seçeneği konsol penceresini gizler
- İkon dosyası (icon.ico) yoksa `--icon` parametresini kaldırın
- Oluşturulan EXE `dist` klasöründe bulunur

## Kullanım Kılavuzu

### Temel Kullanım

1. **Yeni Not Oluşturma**: Araç çubuğundan "Yeni Not" butonuna tıklayın
2. **Not Kaydetme**: "Kaydet" butonuna tıklayın veya Ctrl+S kullanın
3. **Kategori Ekleme**: Sol paneldeki "+" butonuyla yeni kategori ekleyin
4. **Etiket Ekleme**: Not düzenleyicisinde "Etiket ekle..." alanını kullanın

### Klavye Kısayolları

| Kısayol | İşlev |
|---------|-------|
| Ctrl+N | Yeni not |
| Ctrl+S | Kaydet |
| Ctrl+F | Arama |
| Ctrl+L | Not listesini gizle/göster |
| Ctrl+B | Kalın |
| Ctrl+I | İtalik |
| Ctrl+U | Altı çizili |
| Delete | Notu çöpe taşı |

### Arayüz Bölümleri

#### Üst Çubuk
- **Notlar**: Ana not görünümüne geç
- **Git Takip**: GitHub repo takip paneli
- **Takvim**: Takvim görünümü
- **İstatistikler**: Not istatistikleri
- **Not Seç**: Hızlı not seçimi dropdown menüsü
- **Arama**: Not içeriğinde arama
- **Gelişmiş Arama**: Detaylı arama seçenekleri

#### Sol Panel
- **Filtreler**: Tüm notlar, favoriler, şifreli notlar, çöp kutusu
- **Kategoriler**: Not kategorileri ağaç yapısında
- **Etiketler**: Tüm etiketler listesi

#### Orta Panel
- Not kartları listesi
- Tarihe göre sıralama
- Görünüm menüsünden gizlenebilir (Ctrl+L)

#### Sağ Panel
- Not başlığı
- Kategori ve etiket seçimi
- Zengin metin düzenleyici
- Kaydet, Sürüm Geçmişi, Sil butonları

### Git Takip Özelliği

1. "Git Takip" sekmesine geçin
2. "Repo Ekle" butonuna tıklayın
3. GitHub repo URL'sini girin (örn: `https://github.com/kullanici/repo`)
4. Uygulama yeni commitleri otomatik kontrol eder ve bildirim gönderir

### Şifreli Not Oluşturma

1. Yeni not oluşturun
2. Araç çubuğundan kilit ikonuna tıklayın
3. Şifre belirleyin
4. Notu açmak için şifreyi girmeniz gerekecek

### Sürüm Geçmişi

1. Bir not seçin
2. "Sürüm Geçmişi" butonuna tıklayın
3. Geçmiş sürümleri görüntüleyin ve geri yükleyin

## Dosya Konumları

| Dosya | Konum |
|-------|-------|
| Veritabanı | `%USERPROFILE%\Documents\NotDefteri\notlar.db` |
| Ekler | `%USERPROFILE%\Documents\NotDefteri\ekler\` |
| Git Repo Listesi | `%USERPROFILE%\Documents\NotDefteri\git_repolar.json` |

## Sorun Giderme

### Uygulama Açılmıyor
- Python 3.11+ yüklü olduğundan emin olun
- `pip install -r requirements.txt` ile bağımlılıkları yükleyin

### Türkçe Karakterler Bozuk Görünüyor
- Sistem dil ayarlarınızı kontrol edin
- UTF-8 kodlaması kullanıldığından emin olun

### GitHub API Hatası (Rate Limit)
- Çok fazla istek gönderildiğinde oluşur
- Uygulama otomatik olarak istekler arası bekleme yapar

### EXE Dosyası Çalışmıyor
- Antivirüs yazılımının engellemediğinden emin olun
- Windows Defender'da istisna ekleyin
- Visual C++ Redistributable yüklü olduğundan emin olun

## Lisans

Bu proje kişisel kullanım için geliştirilmiştir.

## Katkıda Bulunma

Hata bildirimleri ve öneriler için issue açabilirsiniz.
