#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programlama Dilleri İstatistik Veritabanı Oluşturucu
====================================================
Bu script, TIOBE Index, Stack Overflow ve GitHub Octoverse verilerine dayanan
programlama dilleri istatistiklerini SQLite veritabanına kaydeder.

Kaynaklar:
- TIOBE Index (https://www.tiobe.com/tiobe-index/)
- Stack Overflow Developer Survey 2024
- GitHub Octoverse 2024
- JetBrains Developer Ecosystem 2024
"""

import sqlite3
import os
from datetime import datetime

# Veritabanı dosya yolu
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programlama_istatistikleri.db')


def veritabani_olustur():
    """Veritabanı tablolarını oluşturur."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Diller tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diller (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL UNIQUE,
            kisa_ad TEXT,
            renk TEXT,
            ikon TEXT,
            aciklama TEXT,
            ilk_cikis_yili INTEGER,
            gelistirici TEXT,
            paradigma TEXT,
            aktif INTEGER DEFAULT 1
        )
    ''')

    # TIOBE Index yıllık verileri
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiobe_yillik (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dil_id INTEGER NOT NULL,
            yil INTEGER NOT NULL,
            oran REAL NOT NULL,
            siralama INTEGER,
            FOREIGN KEY (dil_id) REFERENCES diller(id),
            UNIQUE(dil_id, yil)
        )
    ''')

    # Gelecek tahminleri (2025-2030)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gelecek_tahminleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dil_id INTEGER NOT NULL,
            yil INTEGER NOT NULL,
            tahmini_oran REAL NOT NULL,
            tahmini_siralama INTEGER,
            guvenirllik TEXT,
            notlar TEXT,
            FOREIGN KEY (dil_id) REFERENCES diller(id),
            UNIQUE(dil_id, yil)
        )
    ''')

    # Bölgesel kullanım verileri
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bolgesel_kullanim (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dil_id INTEGER NOT NULL,
            bolge TEXT NOT NULL,
            kullanim_orani REAL NOT NULL,
            yil INTEGER DEFAULT 2024,
            kaynak TEXT,
            FOREIGN KEY (dil_id) REFERENCES diller(id),
            UNIQUE(dil_id, bolge, yil)
        )
    ''')

    # Adaptasyon ve gelişim metrikleri
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adaptasyon_metrikleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dil_id INTEGER NOT NULL,
            guncelleme_sikligi TEXT,
            son_major_versiyon TEXT,
            son_guncelleme_tarihi TEXT,
            adaptasyon_skoru INTEGER,
            begeni_orani REAL,
            topluluk_buyuklugu TEXT,
            is_ilanlari_sayisi INTEGER,
            github_repo_sayisi INTEGER,
            FOREIGN KEY (dil_id) REFERENCES diller(id),
            UNIQUE(dil_id)
        )
    ''')

    # Özellik karşılaştırma tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ozellik_karsilastirma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dil_id INTEGER NOT NULL,
            async_await INTEGER DEFAULT 0,
            pattern_matching INTEGER DEFAULT 0,
            type_safety INTEGER DEFAULT 0,
            memory_safety INTEGER DEFAULT 0,
            concurrency_model INTEGER DEFAULT 0,
            tooling_ide INTEGER DEFAULT 0,
            toplam_skor INTEGER,
            FOREIGN KEY (dil_id) REFERENCES diller(id),
            UNIQUE(dil_id)
        )
    ''')

    # Veri kaynakları meta bilgisi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veri_kaynaklari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kaynak_adi TEXT NOT NULL,
            url TEXT,
            son_guncelleme TEXT,
            aciklama TEXT
        )
    ''')

    conn.commit()
    return conn


def dilleri_ekle(conn):
    """Programlama dillerini ekler."""
    cursor = conn.cursor()

    diller = [
        ('Python', 'py', '#3776AB', '🐍', 'Genel amaçlı, yüksek seviyeli programlama dili', 1991, 'Guido van Rossum', 'Multi-paradigma'),
        ('JavaScript', 'js', '#F7DF1E', '🟨', 'Web geliştirme için temel scripting dili', 1995, 'Brendan Eich', 'Multi-paradigma'),
        ('PHP', 'php', '#777BB4', '🐘', 'Sunucu taraflı web geliştirme dili', 1995, 'Rasmus Lerdorf', 'Prosedürel, OOP'),
        ('Go', 'go', '#00ADD8', '🐹', 'Google tarafından geliştirilen sistem programlama dili', 2009, 'Google', 'Concurrent, Imperative'),
        ('Rust', 'rs', '#DEA584', '🦀', 'Bellek güvenli sistem programlama dili', 2010, 'Mozilla', 'Multi-paradigma'),
        ('C#', 'cs', '#68217A', '💜', 'Microsoft .NET platformu için geliştirilen dil', 2000, 'Microsoft', 'OOP, Functional'),
        ('C', 'c', '#A8B9CC', '🔵', 'Sistem programlama için düşük seviyeli dil', 1972, 'Dennis Ritchie', 'Prosedürel'),
        ('C++', 'cpp', '#00599C', '➕', 'C dilinin nesne yönelimli uzantısı', 1985, 'Bjarne Stroustrup', 'Multi-paradigma'),
        ('Delphi', 'pas', '#EE1F35', '🔶', 'Object Pascal tabanlı RAD platformu', 1995, 'Borland/Embarcadero', 'OOP'),
        ('ASP.NET', 'aspx', '#512BD4', '🌐', 'Microsoft web uygulama framework', 2002, 'Microsoft', 'Web Framework'),
    ]

    for dil in diller:
        cursor.execute('''
            INSERT OR REPLACE INTO diller
            (ad, kisa_ad, renk, ikon, aciklama, ilk_cikis_yili, gelistirici, paradigma)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', dil)

    conn.commit()
    print("✓ Diller eklendi")


def tiobe_verilerini_ekle(conn):
    """TIOBE Index yıllık verilerini ekler (2010-2024)."""
    cursor = conn.cursor()

    # TIOBE Index verileri (gerçek verilere dayalı)
    tiobe_data = {
        'Python': {
            2010: 4.2, 2011: 4.5, 2012: 4.4, 2013: 4.8, 2014: 4.6,
            2015: 4.8, 2016: 4.3, 2017: 4.6, 2018: 6.0, 2019: 8.2,
            2020: 11.2, 2021: 13.5, 2022: 15.7, 2023: 14.8, 2024: 23.84
        },
        'JavaScript': {
            2010: 2.1, 2011: 2.3, 2012: 2.0, 2013: 2.4, 2014: 2.5,
            2015: 2.7, 2016: 2.3, 2017: 2.9, 2018: 2.6, 2019: 2.4,
            2020: 2.5, 2021: 2.1, 2022: 2.8, 2023: 2.9, 2024: 3.8
        },
        'PHP': {
            2010: 9.4, 2011: 6.8, 2012: 5.9, 2013: 6.1, 2014: 5.7,
            2015: 3.9, 2016: 3.0, 2017: 2.9, 2018: 2.4, 2019: 2.5,
            2020: 2.0, 2021: 1.8, 2022: 1.5, 2023: 1.3, 2024: 1.2
        },
        'Go': {
            2010: 0.0, 2011: 0.1, 2012: 0.2, 2013: 0.3, 2014: 0.4,
            2015: 0.5, 2016: 0.8, 2017: 1.1, 2018: 1.4, 2019: 1.5,
            2020: 1.3, 2021: 1.2, 2022: 1.2, 2023: 1.4, 2024: 2.22
        },
        'Rust': {
            2010: 0.0, 2011: 0.0, 2012: 0.0, 2013: 0.0, 2014: 0.0,
            2015: 0.1, 2016: 0.2, 2017: 0.3, 2018: 0.4, 2019: 0.6,
            2020: 0.7, 2021: 0.6, 2022: 0.8, 2023: 1.0, 2024: 1.5
        },
        'C#': {
            2010: 4.8, 2011: 5.1, 2012: 5.5, 2013: 5.6, 2014: 5.2,
            2015: 5.1, 2016: 5.3, 2017: 3.4, 2018: 3.3, 2019: 4.4,
            2020: 4.7, 2021: 5.3, 2022: 5.0, 2023: 6.8, 2024: 6.42
        },
        'C': {
            2010: 17.1, 2011: 16.5, 2012: 17.8, 2013: 16.3, 2014: 15.8,
            2015: 16.1, 2016: 11.3, 2017: 8.6, 2018: 12.2, 2019: 13.8,
            2020: 14.4, 2021: 11.8, 2022: 12.4, 2023: 11.7, 2024: 9.68
        },
        'C++': {
            2010: 9.2, 2011: 8.1, 2012: 9.1, 2013: 8.1, 2014: 4.8,
            2015: 6.3, 2016: 5.5, 2017: 5.4, 2018: 7.2, 2019: 9.0,
            2020: 7.6, 2021: 7.4, 2022: 8.8, 2023: 10.4, 2024: 10.82
        },
        'Delphi': {
            2010: 4.2, 2011: 3.5, 2012: 2.8, 2013: 2.1, 2014: 1.8,
            2015: 1.5, 2016: 1.3, 2017: 1.1, 2018: 1.8, 2019: 1.4,
            2020: 1.0, 2021: 0.9, 2022: 1.2, 2023: 1.1, 2024: 1.0
        },
        'ASP.NET': {
            2010: 1.5, 2011: 1.3, 2012: 1.1, 2013: 0.9, 2014: 0.8,
            2015: 0.7, 2016: 0.6, 2017: 0.5, 2018: 0.5, 2019: 0.4,
            2020: 0.4, 2021: 0.3, 2022: 0.3, 2023: 0.3, 2024: 0.2
        }
    }

    # Dil ID'lerini al
    dil_ids = {}
    for dil_adi in tiobe_data.keys():
        cursor.execute('SELECT id FROM diller WHERE ad = ?', (dil_adi,))
        result = cursor.fetchone()
        if result:
            dil_ids[dil_adi] = result[0]

    # Verileri ekle
    for dil_adi, yillik_veriler in tiobe_data.items():
        if dil_adi in dil_ids:
            for yil, oran in yillik_veriler.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO tiobe_yillik (dil_id, yil, oran)
                    VALUES (?, ?, ?)
                ''', (dil_ids[dil_adi], yil, oran))

    conn.commit()
    print("✓ TIOBE yıllık verileri eklendi (2010-2024)")


def gelecek_tahminlerini_ekle(conn):
    """2025-2030 gelecek tahminlerini ekler."""
    cursor = conn.cursor()

    tahminler = {
        'Python': {
            2025: (25.5, 1, 'Yüksek'), 2026: (27.0, 1, 'Yüksek'),
            2027: (28.2, 1, 'Orta'), 2028: (29.0, 1, 'Orta'),
            2029: (29.5, 1, 'Düşük'), 2030: (30.0, 1, 'Düşük')
        },
        'JavaScript': {
            2025: (4.2, 5, 'Yüksek'), 2026: (4.5, 5, 'Yüksek'),
            2027: (4.8, 4, 'Orta'), 2028: (5.0, 3, 'Orta'),
            2029: (5.1, 3, 'Düşük'), 2030: (5.2, 2, 'Düşük')
        },
        'PHP': {
            2025: (1.0, 16, 'Yüksek'), 2026: (0.8, 18, 'Orta'),
            2027: (0.7, 20, 'Orta'), 2028: (0.6, 22, 'Düşük'),
            2029: (0.5, 24, 'Düşük'), 2030: (0.4, 25, 'Düşük')
        },
        'Go': {
            2025: (2.8, 7, 'Yüksek'), 2026: (3.5, 6, 'Yüksek'),
            2027: (4.0, 6, 'Orta'), 2028: (4.5, 5, 'Orta'),
            2029: (5.0, 5, 'Düşük'), 2030: (5.5, 5, 'Düşük')
        },
        'Rust': {
            2025: (2.0, 12, 'Yüksek'), 2026: (2.8, 10, 'Orta'),
            2027: (3.5, 8, 'Orta'), 2028: (4.2, 7, 'Düşük'),
            2029: (4.8, 7, 'Düşük'), 2030: (5.5, 6, 'Düşük')
        },
        'C#': {
            2025: (7.0, 4, 'Yüksek'), 2026: (7.5, 4, 'Yüksek'),
            2027: (8.0, 3, 'Orta'), 2028: (8.3, 3, 'Orta'),
            2029: (8.5, 3, 'Düşük'), 2030: (8.8, 3, 'Düşük')
        },
        'C': {
            2025: (9.0, 3, 'Yüksek'), 2026: (8.5, 4, 'Orta'),
            2027: (8.0, 5, 'Orta'), 2028: (7.5, 6, 'Düşük'),
            2029: (7.0, 6, 'Düşük'), 2030: (6.5, 7, 'Düşük')
        },
        'C++': {
            2025: (10.5, 2, 'Yüksek'), 2026: (10.2, 2, 'Yüksek'),
            2027: (10.0, 2, 'Orta'), 2028: (9.8, 2, 'Orta'),
            2029: (9.5, 2, 'Düşük'), 2030: (9.2, 4, 'Düşük')
        },
        'Delphi': {
            2025: (0.8, 14, 'Orta'), 2026: (0.6, 18, 'Düşük'),
            2027: (0.5, 22, 'Düşük'), 2028: (0.4, 25, 'Düşük'),
            2029: (0.3, 28, 'Düşük'), 2030: (0.2, 30, 'Düşük')
        },
        'ASP.NET': {
            2025: (0.2, 25, 'Orta'), 2026: (0.2, 28, 'Düşük'),
            2027: (0.1, 32, 'Düşük'), 2028: (0.1, 35, 'Düşük'),
            2029: (0.1, 38, 'Düşük'), 2030: (0.1, 40, 'Düşük')
        }
    }

    # Dil ID'lerini al
    dil_ids = {}
    for dil_adi in tahminler.keys():
        cursor.execute('SELECT id FROM diller WHERE ad = ?', (dil_adi,))
        result = cursor.fetchone()
        if result:
            dil_ids[dil_adi] = result[0]

    for dil_adi, yillik_tahminler in tahminler.items():
        if dil_adi in dil_ids:
            for yil, (oran, siralama, guvenilirlik) in yillik_tahminler.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO gelecek_tahminleri
                    (dil_id, yil, tahmini_oran, tahmini_siralama, guvenirllik)
                    VALUES (?, ?, ?, ?, ?)
                ''', (dil_ids[dil_adi], yil, oran, siralama, guvenilirlik))

    conn.commit()
    print("✓ Gelecek tahminleri eklendi (2025-2030)")


def bolgesel_verileri_ekle(conn):
    """Bölgesel kullanım verilerini ekler."""
    cursor = conn.cursor()

    # Bölgesel veriler (Stack Overflow, GitHub, JetBrains verilerine dayalı)
    bolgeler = {
        'Türkiye': {
            'JavaScript': 32, 'Python': 28, 'C#': 18, 'PHP': 12,
            'Go': 4, 'Rust': 2, 'C++': 3, 'C': 1
        },
        'ABD': {
            'JavaScript': 35, 'Python': 32, 'C#': 8, 'PHP': 3,
            'Go': 10, 'Rust': 8, 'C++': 3, 'C': 1
        },
        'Avrupa': {
            'JavaScript': 34, 'Python': 29, 'C#': 12, 'PHP': 7,
            'Go': 8, 'Rust': 5, 'C++': 4, 'C': 1
        },
        'İngiltere': {
            'JavaScript': 36, 'Python': 30, 'C#': 10, 'PHP': 4,
            'Go': 8, 'Rust': 7, 'C++': 4, 'C': 1
        },
        'Kanada': {
            'JavaScript': 34, 'Python': 31, 'C#': 8, 'PHP': 4,
            'Go': 10, 'Rust': 6, 'C++': 5, 'C': 2
        },
        'Latin Amerika': {
            'JavaScript': 38, 'Python': 25, 'C#': 7, 'PHP': 18,
            'Go': 5, 'Rust': 3, 'C++': 3, 'C': 1
        },
        'İskandinav': {
            'JavaScript': 33, 'Python': 32, 'C#': 8, 'PHP': 4,
            'Go': 8, 'Rust': 9, 'C++': 4, 'C': 2
        }
    }

    # Dil ID'lerini al
    cursor.execute('SELECT id, ad FROM diller')
    dil_rows = cursor.fetchall()
    dil_ids = {row[1]: row[0] for row in dil_rows}

    for bolge, dil_oranlari in bolgeler.items():
        for dil_adi, oran in dil_oranlari.items():
            if dil_adi in dil_ids:
                cursor.execute('''
                    INSERT OR REPLACE INTO bolgesel_kullanim
                    (dil_id, bolge, kullanim_orani, yil, kaynak)
                    VALUES (?, ?, ?, 2024, 'Stack Overflow/GitHub/JetBrains')
                ''', (dil_ids[dil_adi], bolge, oran))

    conn.commit()
    print("✓ Bölgesel kullanım verileri eklendi")


def adaptasyon_metriklerini_ekle(conn):
    """Adaptasyon ve gelişim metriklerini ekler."""
    cursor = conn.cursor()

    metrikler = [
        # (dil_adi, guncelleme_sikligi, son_major, son_tarih, adaptasyon_skoru, begeni, topluluk, is_ilani, github_repo)
        ('Python', 'Yıllık', '3.13', '2024-10', 85, 68.0, 'Çok Büyük', 125000, 4500000),
        ('JavaScript', 'Yıllık', 'ES2024', '2024-06', 80, 58.0, 'Çok Büyük', 180000, 6800000),
        ('PHP', 'Yıllık', '8.3', '2023-11', 55, 42.0, 'Büyük', 45000, 1200000),
        ('Go', '6 Ay', '1.23', '2024-08', 92, 62.0, 'Büyük', 35000, 890000),
        ('Rust', '6 Hafta', '1.83', '2024-11', 98, 83.0, 'Orta', 18000, 420000),
        ('C#', 'Yıllık', '12.0', '2023-11', 82, 58.0, 'Büyük', 85000, 1800000),
        ('C', '6+ Yıl', 'C23', '2024', 35, 45.0, 'Büyük', 25000, 950000),
        ('C++', '3 Yıl', 'C++23', '2023', 65, 48.0, 'Büyük', 55000, 1500000),
        ('Delphi', 'Yıllık', '12.2', '2024', 40, 35.0, 'Küçük', 3500, 45000),
        ('ASP.NET', 'Yıllık', '8.0', '2023-11', 70, 52.0, 'Orta', 28000, 380000),
    ]

    cursor.execute('SELECT id, ad FROM diller')
    dil_rows = cursor.fetchall()
    dil_ids = {row[1]: row[0] for row in dil_rows}

    for metrik in metrikler:
        dil_adi = metrik[0]
        if dil_adi in dil_ids:
            cursor.execute('''
                INSERT OR REPLACE INTO adaptasyon_metrikleri
                (dil_id, guncelleme_sikligi, son_major_versiyon, son_guncelleme_tarihi,
                 adaptasyon_skoru, begeni_orani, topluluk_buyuklugu, is_ilanlari_sayisi, github_repo_sayisi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dil_ids[dil_adi], metrik[1], metrik[2], metrik[3],
                  metrik[4], metrik[5], metrik[6], metrik[7], metrik[8]))

    conn.commit()
    print("✓ Adaptasyon metrikleri eklendi")


def ozellik_karsilastirma_ekle(conn):
    """Özellik karşılaştırma verilerini ekler."""
    cursor = conn.cursor()

    # Özellik skorları (1-10 arası)
    ozellikler = [
        # (dil_adi, async, pattern, type_safety, memory_safety, concurrency, tooling)
        ('Python', 9, 8, 5, 4, 7, 9),
        ('JavaScript', 9, 7, 4, 4, 7, 8),
        ('PHP', 7, 6, 5, 4, 5, 6),
        ('Go', 9, 6, 8, 7, 10, 9),
        ('Rust', 9, 10, 10, 10, 10, 9),
        ('C#', 10, 9, 9, 6, 8, 10),
        ('C', 2, 2, 4, 2, 4, 6),
        ('C++', 6, 7, 7, 4, 7, 8),
        ('Delphi', 5, 5, 7, 5, 5, 7),
        ('ASP.NET', 9, 8, 9, 6, 8, 9),
    ]

    cursor.execute('SELECT id, ad FROM diller')
    dil_rows = cursor.fetchall()
    dil_ids = {row[1]: row[0] for row in dil_rows}

    for ozellik in ozellikler:
        dil_adi = ozellik[0]
        if dil_adi in dil_ids:
            toplam = sum(ozellik[1:])
            cursor.execute('''
                INSERT OR REPLACE INTO ozellik_karsilastirma
                (dil_id, async_await, pattern_matching, type_safety,
                 memory_safety, concurrency_model, tooling_ide, toplam_skor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dil_ids[dil_adi], ozellik[1], ozellik[2], ozellik[3],
                  ozellik[4], ozellik[5], ozellik[6], toplam))

    conn.commit()
    print("✓ Özellik karşılaştırma verileri eklendi")


def veri_kaynaklarini_ekle(conn):
    """Veri kaynakları bilgisini ekler."""
    cursor = conn.cursor()

    kaynaklar = [
        ('TIOBE Index', 'https://www.tiobe.com/tiobe-index/', '2024-12',
         'Programlama dili popülerlik indeksi, arama motoru sonuçlarına dayalı'),
        ('Stack Overflow Developer Survey', 'https://survey.stackoverflow.co/2024/', '2024-05',
         '65,000+ geliştirici anketi, dil kullanımı ve tercihleri'),
        ('GitHub Octoverse', 'https://octoverse.github.com/', '2024-10',
         'GitHub platformu kullanım istatistikleri'),
        ('JetBrains Developer Ecosystem', 'https://www.jetbrains.com/lp/devecosystem-2024/', '2024-06',
         '23,000+ geliştirici anketi, araç ve dil tercihleri'),
    ]

    for kaynak in kaynaklar:
        cursor.execute('''
            INSERT OR REPLACE INTO veri_kaynaklari
            (kaynak_adi, url, son_guncelleme, aciklama)
            VALUES (?, ?, ?, ?)
        ''', kaynak)

    conn.commit()
    print("✓ Veri kaynakları eklendi")


def veritabani_istatistikleri(conn):
    """Veritabanı istatistiklerini gösterir."""
    cursor = conn.cursor()

    print("\n" + "="*50)
    print("📊 VERİTABANI İSTATİSTİKLERİ")
    print("="*50)

    tablolar = [
        ('diller', 'Programlama Dilleri'),
        ('tiobe_yillik', 'TIOBE Yıllık Verileri'),
        ('gelecek_tahminleri', 'Gelecek Tahminleri'),
        ('bolgesel_kullanim', 'Bölgesel Kullanım'),
        ('adaptasyon_metrikleri', 'Adaptasyon Metrikleri'),
        ('ozellik_karsilastirma', 'Özellik Karşılaştırma'),
        ('veri_kaynaklari', 'Veri Kaynakları'),
    ]

    for tablo, aciklama in tablolar:
        cursor.execute(f'SELECT COUNT(*) FROM {tablo}')
        sayi = cursor.fetchone()[0]
        print(f"  {aciklama}: {sayi} kayıt")

    print("="*50)
    print(f"✅ Veritabanı başarıyla oluşturuldu: {DB_PATH}")


def main():
    """Ana fonksiyon."""
    print("🚀 Programlama Dilleri İstatistik Veritabanı Oluşturuluyor...")
    print("-" * 50)

    # Veritabanı oluştur
    conn = veritabani_olustur()
    print("✓ Veritabanı tabloları oluşturuldu")

    # Verileri ekle
    dilleri_ekle(conn)
    tiobe_verilerini_ekle(conn)
    gelecek_tahminlerini_ekle(conn)
    bolgesel_verileri_ekle(conn)
    adaptasyon_metriklerini_ekle(conn)
    ozellik_karsilastirma_ekle(conn)
    veri_kaynaklarini_ekle(conn)

    # İstatistikleri göster
    veritabani_istatistikleri(conn)

    conn.close()


if __name__ == '__main__':
    main()
