# Programlama Dilleri İstatistik Dashboard

2010-2030 yılları arasında programlama dillerinin kullanım trendlerini, gelecek tahminlerini ve bölgesel analizlerini gösteren kapsamlı bir istatistik dashboard'u.

## Özellikler

- **Trend Analizi (2010-2024)**: TIOBE Index verilerine dayalı 15 yıllık trend grafikleri
- **Gelecek Tahminleri (2025-2030)**: Sektör analizlerine dayalı tahminler
- **Bölgesel Analiz**: Türkiye, ABD, Avrupa, İngiltere, Kanada, Latin Amerika, İskandinav ülkeleri
- **Adaptasyon Hızı**: Dillerin güncelleme sıklığı ve modern özellik adaptasyonu

## Desteklenen Diller

- Python, JavaScript, PHP, Go, Rust
- C#, C, C++
- Delphi/Pascal, ASP.NET

## Kurulum

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Veritabanı Oluşturma
```bash
python veritabani_olustur.py
```

## Kullanım

### HTML Dashboard
`dashboard.html` dosyasını herhangi bir web tarayıcısında açın. İnternet bağlantısı gereklidir (Chart.js CDN).

### Python Dashboard (PyQt5)
```bash
python dashboard_app.py
```

## Dosya Yapısı

```
Veri_Analizi/
├── dashboard.html              # HTML/JS dashboard (Chart.js)
├── dashboard_app.py            # PyQt5 masaüstü uygulaması
├── veritabani_olustur.py       # SQLite veritabanı oluşturucu
├── programlama_istatistikleri.db  # SQLite veritabanı
├── requirements.txt            # Python bağımlılıkları
└── README.md                   # Bu dosya
```

## Veri Kaynakları

- [TIOBE Index](https://www.tiobe.com/tiobe-index/) - Programlama dili popülerlik indeksi
- [Stack Overflow Developer Survey 2024](https://survey.stackoverflow.co/2024/) - Geliştirici anketi
- [GitHub Octoverse 2024](https://octoverse.github.com/) - GitHub kullanım istatistikleri
- [JetBrains Developer Ecosystem 2024](https://www.jetbrains.com/lp/devecosystem-2024/) - IDE geliştirici anketi

## Veritabanı Şeması

### Tablolar
- `diller`: Programlama dilleri bilgisi
- `tiobe_yillik`: 2010-2024 TIOBE Index verileri
- `gelecek_tahminleri`: 2025-2030 tahminleri
- `bolgesel_kullanim`: Bölgelere göre kullanım oranları
- `adaptasyon_metrikleri`: Güncelleme sıklığı, beğeni oranları
- `ozellik_karsilastirma`: Modern özellik skorları
- `veri_kaynaklari`: Kaynak meta bilgileri

## Ekran Görüntüleri

### HTML Dashboard
- 5 sekmeli interaktif arayüz
- Chart.js ile dinamik grafikler
- Dark tema, responsive tasarım

### Python Dashboard
- PyQt5 ile native masaüstü uygulaması
- Matplotlib grafikleri
- SQLite'dan canlı veri okuma

## Lisans

MIT License - Not Defteri Pro projesi kapsamında geliştirilmiştir.
