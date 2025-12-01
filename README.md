# Not Defteri Pro

Gelişmiş özelliklerle donatılmış, Türkçe arayüzlü masaüstü not alma uygulaması.

## Özellikler

### Temel Özellikler
- Zengin metin düzenleme (kalın, italik, altı çizili, renkler, listeler)
- Kategori ve etiket sistemi ile not organizasyonu
- Favori notlar ve çöp kutusu
- Aydınlık/Karanlık tema desteği
- Gelişmiş arama ve filtreleme

### Gelişmiş Özellikler
- **Git Takip**: GitHub/GitLab repolarını takip edin, yeni commit bildirimleri alın
- **Sürüm Geçmişi**: Notlarınızın geçmiş versiyonlarını görüntüleyin
- **Şifreli Notlar**: AES-256 şifreleme ile notlarınızı koruyun
- **Hatırlatıcılar**: Notlara hatırlatıcı ekleyin
- **Takvim Görünümü**: Notlarınızı takvimde görüntüleyin
- **Markdown Desteği**: Markdown formatında yazın ve önizleyin
- **Kod Bloğu**: Sözdizimi vurgulama ile kod blokları ekleyin
- **Web Clipper**: Web sayfalarından içerik kaydedin
- **PDF Aktarımı**: Notları PDF olarak dışa aktarın
- **Çeviri**: Notları farklı dillere çevirin (sağ tık menüsü)
- **Bulut Senkronizasyon**: Google Drive ve Dropbox desteği
- **Şablonlar**: Hazır not şablonları kullanın
- **Notlar Arası Bağlantı**: [[Not Adı]] formatıyla notlar arası link

## Gereksinimler

- Python 3.11 veya üzeri
- Windows işletim sistemi

## Kurulum

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
pyinstaller --onefile --windowed --name "NotDefteriPro" ana_uygulama.py
```

**3. Klasör Yapısıyla EXE Oluşturma (Daha hızlı başlatma):**
```bash
pyinstaller --windowed --name "NotDefteriPro" ana_uygulama.py
```

**4. Modüller dahil detaylı komut:**
```bash
pyinstaller --onefile --windowed --name "NotDefteriPro" ^
  --add-data "moduller;moduller" ^
  --hidden-import "PyQt5.QtWidgets" ^
  --hidden-import "PyQt5.QtCore" ^
  --hidden-import "PyQt5.QtGui" ^
  --hidden-import "cryptography" ^
  --hidden-import "markdown" ^
  --hidden-import "Pygments" ^
  --hidden-import "bs4" ^
  --hidden-import "deep_translator" ^
  ana_uygulama.py
```

**Not:** Windows'ta `^` ile satır devam eder. Linux/Mac için `\` kullanın.

### Önemli Notlar

- EXE oluştururken tüm bağımlılıkların yüklü olduğundan emin olun
- `--onefile` tek dosya oluşturur ama başlatma süresi daha uzundur
- `--windowed` konsol penceresini gizler
- Oluşturulan EXE `dist` klasöründe bulunur
- Veritabanı (`notlar.db`) EXE ile aynı klasörde oluşturulur

## Kullanım

### Arayüz Bölümleri

#### Üst Çubuk (Sekmeler)
- **📝 Notlar**: Ana not görünümüne geç
- **🔄 Git Takip**: GitHub/GitLab repo takip paneli
- **📅 Takvim**: Takvim görünümünü aç
- **📊 İstatistikler**: Not istatistiklerini görüntüle
- **Not Seç Dropdown**: Hızlı not seçimi
- **Arama Kutusu**: Not içeriğinde arama
- **Gelişmiş Arama**: Detaylı arama seçenekleri

#### Sol Panel (Kenar Çubuğu)
- **Filtreler**: Tüm notlar, favoriler, şifreli notlar, çöp kutusu
- **Kategoriler**: Not kategorileri (+ ile yeni ekle)
- **Etiketler**: Tüm etiketler listesi (+ ile yeni ekle)

#### Orta Panel (Not Listesi)
- Not kartları tarihe göre sıralı
- Favori yıldızı ile hızlı işaretleme
- Görünüm menüsünden gizlenebilir (Ctrl+L)

#### Sağ Panel (Düzenleyici)
- Not başlığı girişi
- Kategori seçimi ve etiket ekleme
- Zengin metin düzenleyici (formatlama araç çubuğu)
- Kaydet, Sürüm Geçmişi, Sil butonları

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
| Ctrl+Z | Geri al |
| Ctrl+Y | Yinele |

### Git Takip Özelliği

1. Üst çubuktan "🔄 Git Takip" sekmesine geçin
2. "+ Repo Ekle" butonuna tıklayın
3. GitHub veya GitLab repo URL'sini girin
   - Örnek: `https://github.com/kullanici/repo`
   - Örnek: `https://gitlab.com/kullanici/repo`
4. "🔄 Kontrol Et" ile yeni commitleri kontrol edin
5. Yeşil nokta (🟢) güncelleme olduğunu gösterir
6. Repo'ya çift tıklayarak tarayıcıda açın

### Şifreli Not Oluşturma

1. Menüden veya araç çubuğundan şifreli not özelliğini kullanın
2. Şifre belirleyin
3. Notu açmak için şifreyi girmeniz gerekecek

### Sürüm Geçmişi

1. Bir not seçin
2. "Sürüm Geçmişi" butonuna tıklayın
3. Geçmiş sürümleri görüntüleyin
4. İstediğiniz sürümü geri yükleyin

### Metin Çevirisi

1. Düzenleyicide metin seçin (veya hiçbir şey seçmeyin - tüm içerik)
2. Sağ tıklayın
3. "Seçili Metni Çevir" veya "Hızlı Çeviri" alt menüsünü kullanın
4. Desteklenen diller: İngilizce ↔ Türkçe, Otomatik algılama

## Dosya Konumları

| Dosya | Konum |
|-------|-------|
| Veritabanı | `{uygulama_klasörü}/notlar.db` |

## Sorun Giderme

### Uygulama Açılmıyor
- Python 3.11+ yüklü olduğundan emin olun
- `pip install -r requirements.txt` ile bağımlılıkları yükleyin
- Hata mesajını görmek için komut satırından çalıştırın

### Türkçe Karakterler Bozuk Görünüyor
- Dosyaların UTF-8 kodlamasında olduğundan emin olun

### GitHub API Hatası (403 Rate Limit)
- Çok fazla istek gönderildiğinde oluşur
- Uygulama otomatik olarak istekler arası 1.5 saniye bekler
- Birkaç dakika bekleyip tekrar deneyin

### EXE Dosyası Çalışmıyor
- Antivirüs yazılımının engellemediğinden emin olun
- Windows Defender'da istisna ekleyin
- Visual C++ Redistributable 2015-2022 yüklü olduğundan emin olun

### Modül Bulunamadı Hatası
- İlgili opsiyonel bağımlılığı yükleyin
- Örnek: Çeviri için `pip install deep-translator`

## Lisans

Bu proje kişisel kullanım için geliştirilmiştir.
