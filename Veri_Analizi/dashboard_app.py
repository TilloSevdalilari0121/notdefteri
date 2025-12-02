#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programlama Dilleri İstatistik Dashboard - PyQt5 Uygulaması
============================================================
SQLite veritabanından veri okuyarak görselleştiren profesyonel dashboard.

Gereksinimler:
    pip install PyQt5 matplotlib numpy

Kullanım:
    python dashboard_app.py
"""

import sys
import os
import sqlite3
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QFrame, QScrollArea, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout, QGroupBox,
    QComboBox, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPainter

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Veritabanı yolu
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programlama_istatistikleri.db')

# Renk paleti
COLORS = {
    'Python': '#3776AB',
    'JavaScript': '#F7DF1E',
    'PHP': '#777BB4',
    'Go': '#00ADD8',
    'Rust': '#DEA584',
    'C#': '#68217A',
    'C': '#A8B9CC',
    'C++': '#00599C',
    'Delphi': '#EE1F35',
    'ASP.NET': '#512BD4'
}

# Tema renkleri
THEME = {
    'bg_primary': '#0f172a',
    'bg_secondary': '#1e293b',
    'bg_card': '#334155',
    'text_primary': '#f8fafc',
    'text_secondary': '#94a3b8',
    'accent': '#6366f1',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444'
}


class VeritabaniYoneticisi:
    """SQLite veritabanı işlemlerini yönetir."""

    def __init__(self, db_path):
        self.db_path = db_path

    def baglanti_al(self):
        return sqlite3.connect(self.db_path)

    def dilleri_getir(self):
        """Tüm dilleri getirir."""
        conn = self.baglanti_al()
        cursor = conn.cursor()
        cursor.execute('SELECT id, ad, renk, ikon FROM diller ORDER BY ad')
        sonuc = cursor.fetchall()
        conn.close()
        return sonuc

    def tiobe_verilerini_getir(self, dil_id=None):
        """TIOBE yıllık verilerini getirir."""
        conn = self.baglanti_al()
        cursor = conn.cursor()

        if dil_id:
            cursor.execute('''
                SELECT d.ad, t.yil, t.oran
                FROM tiobe_yillik t
                JOIN diller d ON t.dil_id = d.id
                WHERE t.dil_id = ?
                ORDER BY t.yil
            ''', (dil_id,))
        else:
            cursor.execute('''
                SELECT d.ad, t.yil, t.oran
                FROM tiobe_yillik t
                JOIN diller d ON t.dil_id = d.id
                ORDER BY d.ad, t.yil
            ''')

        sonuc = cursor.fetchall()
        conn.close()
        return sonuc

    def gelecek_tahminlerini_getir(self):
        """Gelecek tahminlerini getirir."""
        conn = self.baglanti_al()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.ad, g.yil, g.tahmini_oran, g.tahmini_siralama, g.guvenirllik
            FROM gelecek_tahminleri g
            JOIN diller d ON g.dil_id = d.id
            ORDER BY d.ad, g.yil
        ''')
        sonuc = cursor.fetchall()
        conn.close()
        return sonuc

    def bolgesel_verileri_getir(self):
        """Bölgesel kullanım verilerini getirir."""
        conn = self.baglanti_al()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.ad, b.bolge, b.kullanim_orani
            FROM bolgesel_kullanim b
            JOIN diller d ON b.dil_id = d.id
            ORDER BY b.bolge, b.kullanim_orani DESC
        ''')
        sonuc = cursor.fetchall()
        conn.close()
        return sonuc

    def adaptasyon_metriklerini_getir(self):
        """Adaptasyon metriklerini getirir."""
        conn = self.baglanti_al()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.ad, a.guncelleme_sikligi, a.son_major_versiyon,
                   a.adaptasyon_skoru, a.begeni_orani, a.topluluk_buyuklugu
            FROM adaptasyon_metrikleri a
            JOIN diller d ON a.dil_id = d.id
            ORDER BY a.adaptasyon_skoru DESC
        ''')
        sonuc = cursor.fetchall()
        conn.close()
        return sonuc

    def ozellik_karsilastirma_getir(self):
        """Özellik karşılaştırma verilerini getirir."""
        conn = self.baglanti_al()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.ad, o.async_await, o.pattern_matching, o.type_safety,
                   o.memory_safety, o.concurrency_model, o.tooling_ide, o.toplam_skor
            FROM ozellik_karsilastirma o
            JOIN diller d ON o.dil_id = d.id
            ORDER BY o.toplam_skor DESC
        ''')
        sonuc = cursor.fetchall()
        conn.close()
        return sonuc

    def guncel_siralamayi_getir(self):
        """2024 yılı sıralamasını getirir."""
        conn = self.baglanti_al()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.ad, t.oran
            FROM tiobe_yillik t
            JOIN diller d ON t.dil_id = d.id
            WHERE t.yil = 2024
            ORDER BY t.oran DESC
        ''')
        sonuc = cursor.fetchall()
        conn.close()
        return sonuc


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib grafikleri için canvas widget."""

    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=THEME['bg_card'])
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor(THEME['bg_card'])

        # Eksen renklerini ayarla
        self.axes.tick_params(colors=THEME['text_secondary'])
        self.axes.spines['bottom'].set_color(THEME['text_secondary'])
        self.axes.spines['top'].set_color(THEME['text_secondary'])
        self.axes.spines['left'].set_color(THEME['text_secondary'])
        self.axes.spines['right'].set_color(THEME['text_secondary'])

        super().__init__(self.fig)
        self.setMinimumHeight(300)


class StatKarti(QFrame):
    """İstatistik kartı widget."""

    def __init__(self, baslik, deger, icon="", degisim="", pozitif=True):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_card']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(self)

        # İkon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; color: {THEME['text_primary']};")
        icon_label.setAlignment(Qt.AlignCenter)

        # Değer
        deger_label = QLabel(str(deger))
        deger_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {THEME['accent']};
        """)
        deger_label.setAlignment(Qt.AlignCenter)

        # Başlık
        baslik_label = QLabel(baslik)
        baslik_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 12px;")
        baslik_label.setAlignment(Qt.AlignCenter)

        # Değişim
        if degisim:
            renk = THEME['success'] if pozitif else THEME['danger']
            degisim_label = QLabel(degisim)
            degisim_label.setStyleSheet(f"""
                color: {renk};
                font-size: 11px;
                padding: 3px 8px;
                background-color: {renk}33;
                border-radius: 10px;
            """)
            degisim_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(deger_label)
        layout.addWidget(baslik_label)
        if degisim:
            layout.addWidget(degisim_label)


class GenelBakisWidget(QWidget):
    """Genel bakış sekmesi."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.arayuz_olustur()

    def arayuz_olustur(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Üst istatistik kartları
        kartlar_layout = QHBoxLayout()

        kart1 = StatKarti("Python (2024)", "23.84%", "🐍", "↑ 9.3% yıllık", True)
        kart2 = StatKarti("C++ (2024)", "10.82%", "➕", "↑ Yükselişte", True)
        kart3 = StatKarti("JavaScript Kullanımı", "62%", "🟨", "↑ 1.4%", True)
        kart4 = StatKarti("Rust Beğeni", "83%", "🦀", "En sevilen", True)

        kartlar_layout.addWidget(kart1)
        kartlar_layout.addWidget(kart2)
        kartlar_layout.addWidget(kart3)
        kartlar_layout.addWidget(kart4)

        layout.addLayout(kartlar_layout)

        # Grafikler
        grafik_layout = QHBoxLayout()

        # Sol: Bar chart
        sol_frame = QFrame()
        sol_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        sol_layout = QVBoxLayout(sol_frame)

        baslik1 = QLabel("🏆 2024 Dil Sıralaması (TIOBE Index)")
        baslik1.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: bold; padding: 10px;")
        sol_layout.addWidget(baslik1)

        self.siralama_canvas = MatplotlibCanvas(width=6, height=4)
        sol_layout.addWidget(self.siralama_canvas)

        # Sağ: Pie chart
        sag_frame = QFrame()
        sag_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        sag_layout = QVBoxLayout(sag_frame)

        baslik2 = QLabel("📊 Pazar Payı Dağılımı")
        baslik2.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: bold; padding: 10px;")
        sag_layout.addWidget(baslik2)

        self.pazar_canvas = MatplotlibCanvas(width=5, height=4)
        sag_layout.addWidget(self.pazar_canvas)

        grafik_layout.addWidget(sol_frame, 6)
        grafik_layout.addWidget(sag_frame, 4)

        layout.addLayout(grafik_layout)

        # Grafikleri çiz
        self.siralama_grafigi_ciz()
        self.pazar_grafigi_ciz()

    def siralama_grafigi_ciz(self):
        """Sıralama bar grafiğini çizer."""
        veriler = self.db.guncel_siralamayi_getir()

        diller = [v[0] for v in veriler]
        oranlar = [v[1] for v in veriler]
        renkler = [COLORS.get(d, '#64748b') for d in diller]

        ax = self.siralama_canvas.axes
        ax.clear()
        ax.set_facecolor(THEME['bg_card'])

        bars = ax.barh(diller, oranlar, color=renkler, height=0.6)

        # Değerleri bar üzerine yaz
        for bar, oran in zip(bars, oranlar):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                   f'{oran:.1f}%', va='center', color=THEME['text_secondary'], fontsize=9)

        ax.set_xlabel('TIOBE Index (%)', color=THEME['text_secondary'])
        ax.tick_params(colors=THEME['text_secondary'])
        ax.invert_yaxis()

        for spine in ax.spines.values():
            spine.set_color(THEME['text_secondary'])

        self.siralama_canvas.fig.tight_layout()
        self.siralama_canvas.draw()

    def pazar_grafigi_ciz(self):
        """Pazar payı pie grafiğini çizer."""
        veriler = self.db.guncel_siralamayi_getir()[:6]  # İlk 6

        diller = [v[0] for v in veriler]
        oranlar = [v[1] for v in veriler]

        # Diğer
        diger = 100 - sum(oranlar)
        if diger > 0:
            diller.append('Diğer')
            oranlar.append(diger)

        renkler = [COLORS.get(d, '#64748b') for d in diller]

        ax = self.pazar_canvas.axes
        ax.clear()
        ax.set_facecolor(THEME['bg_card'])

        wedges, texts, autotexts = ax.pie(
            oranlar, labels=diller, colors=renkler,
            autopct='%1.1f%%', startangle=90,
            textprops={'color': THEME['text_primary'], 'fontsize': 8},
            wedgeprops={'linewidth': 2, 'edgecolor': THEME['bg_card']}
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(7)

        self.pazar_canvas.fig.tight_layout()
        self.pazar_canvas.draw()


class TrendAnaliziWidget(QWidget):
    """Trend analizi sekmesi."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.arayuz_olustur()

    def arayuz_olustur(self):
        layout = QVBoxLayout(self)

        # Ana trend grafiği
        ana_frame = QFrame()
        ana_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        ana_layout = QVBoxLayout(ana_frame)

        baslik = QLabel("📈 TIOBE Index Trendi (2010-2024)")
        baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 16px; font-weight: bold; padding: 10px;")
        ana_layout.addWidget(baslik)

        self.trend_canvas = MatplotlibCanvas(width=12, height=5)
        ana_layout.addWidget(self.trend_canvas)

        layout.addWidget(ana_frame)

        # Alt grafikler
        alt_layout = QHBoxLayout()

        # Python büyümesi
        python_frame = QFrame()
        python_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        python_layout = QVBoxLayout(python_frame)

        python_baslik = QLabel("🐍 Python Yükselişi")
        python_baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: bold; padding: 10px;")
        python_layout.addWidget(python_baslik)

        self.python_canvas = MatplotlibCanvas(width=5, height=3)
        python_layout.addWidget(self.python_canvas)

        # PHP düşüşü
        php_frame = QFrame()
        php_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        php_layout = QVBoxLayout(php_frame)

        php_baslik = QLabel("🐘 PHP Düşüşü")
        php_baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: bold; padding: 10px;")
        php_layout.addWidget(php_baslik)

        self.php_canvas = MatplotlibCanvas(width=5, height=3)
        php_layout.addWidget(self.php_canvas)

        alt_layout.addWidget(python_frame)
        alt_layout.addWidget(php_frame)

        layout.addLayout(alt_layout)

        # Grafikleri çiz
        self.trend_grafigi_ciz()
        self.python_grafigi_ciz()
        self.php_grafigi_ciz()

    def trend_grafigi_ciz(self):
        """Ana trend grafiğini çizer."""
        veriler = self.db.tiobe_verilerini_getir()

        # Verileri düzenle
        dil_verileri = {}
        for dil, yil, oran in veriler:
            if dil not in dil_verileri:
                dil_verileri[dil] = {'yillar': [], 'oranlar': []}
            dil_verileri[dil]['yillar'].append(yil)
            dil_verileri[dil]['oranlar'].append(oran)

        ax = self.trend_canvas.axes
        ax.clear()
        ax.set_facecolor(THEME['bg_card'])

        for dil, veri in dil_verileri.items():
            renk = COLORS.get(dil, '#64748b')
            ax.plot(veri['yillar'], veri['oranlar'], label=dil, color=renk, linewidth=2, marker='o', markersize=3)

        ax.set_xlabel('Yıl', color=THEME['text_secondary'])
        ax.set_ylabel('TIOBE Index (%)', color=THEME['text_secondary'])
        ax.legend(loc='upper left', facecolor=THEME['bg_secondary'], labelcolor=THEME['text_primary'], fontsize=8)
        ax.tick_params(colors=THEME['text_secondary'])
        ax.grid(True, alpha=0.2, color=THEME['text_secondary'])

        for spine in ax.spines.values():
            spine.set_color(THEME['text_secondary'])

        self.trend_canvas.fig.tight_layout()
        self.trend_canvas.draw()

    def python_grafigi_ciz(self):
        """Python büyüme grafiğini çizer."""
        veriler = self.db.tiobe_verilerini_getir()

        python_veriler = [(yil, oran) for dil, yil, oran in veriler if dil == 'Python']
        yillar = [v[0] for v in python_veriler]
        oranlar = [v[1] for v in python_veriler]

        ax = self.python_canvas.axes
        ax.clear()
        ax.set_facecolor(THEME['bg_card'])

        ax.fill_between(yillar, oranlar, alpha=0.3, color=COLORS['Python'])
        ax.plot(yillar, oranlar, color=COLORS['Python'], linewidth=2, marker='o', markersize=4)

        ax.set_ylabel('TIOBE (%)', color=THEME['text_secondary'], fontsize=9)
        ax.tick_params(colors=THEME['text_secondary'], labelsize=8)
        ax.grid(True, alpha=0.2, color=THEME['text_secondary'])

        for spine in ax.spines.values():
            spine.set_color(THEME['text_secondary'])

        self.python_canvas.fig.tight_layout()
        self.python_canvas.draw()

    def php_grafigi_ciz(self):
        """PHP düşüş grafiğini çizer."""
        veriler = self.db.tiobe_verilerini_getir()

        php_veriler = [(yil, oran) for dil, yil, oran in veriler if dil == 'PHP']
        yillar = [v[0] for v in php_veriler]
        oranlar = [v[1] for v in php_veriler]

        ax = self.php_canvas.axes
        ax.clear()
        ax.set_facecolor(THEME['bg_card'])

        ax.fill_between(yillar, oranlar, alpha=0.3, color=COLORS['PHP'])
        ax.plot(yillar, oranlar, color=COLORS['PHP'], linewidth=2, marker='o', markersize=4)

        ax.set_ylabel('TIOBE (%)', color=THEME['text_secondary'], fontsize=9)
        ax.tick_params(colors=THEME['text_secondary'], labelsize=8)
        ax.grid(True, alpha=0.2, color=THEME['text_secondary'])

        for spine in ax.spines.values():
            spine.set_color(THEME['text_secondary'])

        self.php_canvas.fig.tight_layout()
        self.php_canvas.draw()


class GelecekTahminWidget(QWidget):
    """Gelecek tahminleri sekmesi."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.arayuz_olustur()

    def arayuz_olustur(self):
        layout = QVBoxLayout(self)

        # Ana grafik
        ana_frame = QFrame()
        ana_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        ana_layout = QVBoxLayout(ana_frame)

        baslik = QLabel("🔮 Gelecek Tahminleri (2025-2030)")
        baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 16px; font-weight: bold; padding: 10px;")
        ana_layout.addWidget(baslik)

        self.tahmin_canvas = MatplotlibCanvas(width=12, height=5)
        ana_layout.addWidget(self.tahmin_canvas)

        layout.addWidget(ana_frame)

        # Tahmin tablosu
        tablo_frame = QFrame()
        tablo_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        tablo_layout = QVBoxLayout(tablo_frame)

        tablo_baslik = QLabel("📋 2030 Tahmin Senaryoları")
        tablo_baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: bold; padding: 10px;")
        tablo_layout.addWidget(tablo_baslik)

        self.tablo = QTableWidget()
        self.tablo.setStyleSheet(f"""
            QTableWidget {{
                background-color: {THEME['bg_secondary']};
                color: {THEME['text_primary']};
                border: none;
                gridline-color: {THEME['bg_card']};
            }}
            QHeaderView::section {{
                background-color: {THEME['bg_card']};
                color: {THEME['text_primary']};
                padding: 8px;
                border: none;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
        """)
        tablo_layout.addWidget(self.tablo)

        layout.addWidget(tablo_frame)

        # Verileri yükle
        self.tahmin_grafigi_ciz()
        self.tablo_doldur()

    def tahmin_grafigi_ciz(self):
        """Gelecek tahmin grafiğini çizer."""
        tiobe_veriler = self.db.tiobe_verilerini_getir()
        tahmin_veriler = self.db.gelecek_tahminlerini_getir()

        # Verileri düzenle
        dil_verileri = {}

        # Tarihsel veriler
        for dil, yil, oran in tiobe_veriler:
            if dil not in dil_verileri:
                dil_verileri[dil] = {'yillar': [], 'oranlar': [], 'tahmin_yillar': [], 'tahmin_oranlar': []}
            dil_verileri[dil]['yillar'].append(yil)
            dil_verileri[dil]['oranlar'].append(oran)

        # Tahmin verileri
        for dil, yil, oran, _, _ in tahmin_veriler:
            if dil in dil_verileri:
                dil_verileri[dil]['tahmin_yillar'].append(yil)
                dil_verileri[dil]['tahmin_oranlar'].append(oran)

        ax = self.tahmin_canvas.axes
        ax.clear()
        ax.set_facecolor(THEME['bg_card'])

        # Seçili diller
        secili_diller = ['Python', 'Go', 'Rust', 'C#', 'PHP', 'JavaScript']

        for dil in secili_diller:
            if dil in dil_verileri:
                veri = dil_verileri[dil]
                renk = COLORS.get(dil, '#64748b')

                # Tarihsel çizgi
                ax.plot(veri['yillar'], veri['oranlar'], color=renk, linewidth=2, label=dil)

                # Tahmin çizgisi (kesikli)
                if veri['tahmin_yillar']:
                    # Bağlantı noktası
                    baglanti_yil = [veri['yillar'][-1]] + veri['tahmin_yillar']
                    baglanti_oran = [veri['oranlar'][-1]] + veri['tahmin_oranlar']
                    ax.plot(baglanti_yil, baglanti_oran, color=renk, linewidth=2, linestyle='--', alpha=0.7)

        # Dikey çizgi (2024)
        ax.axvline(x=2024, color=THEME['text_secondary'], linestyle=':', alpha=0.5)
        ax.text(2024.2, ax.get_ylim()[1] * 0.95, 'Tahmin', color=THEME['text_secondary'], fontsize=9)

        ax.set_xlabel('Yıl', color=THEME['text_secondary'])
        ax.set_ylabel('TIOBE Index (%)', color=THEME['text_secondary'])
        ax.legend(loc='upper left', facecolor=THEME['bg_secondary'], labelcolor=THEME['text_primary'], fontsize=8)
        ax.tick_params(colors=THEME['text_secondary'])
        ax.grid(True, alpha=0.2, color=THEME['text_secondary'])

        for spine in ax.spines.values():
            spine.set_color(THEME['text_secondary'])

        self.tahmin_canvas.fig.tight_layout()
        self.tahmin_canvas.draw()

    def tablo_doldur(self):
        """Tahmin tablosunu doldurur."""
        veriler = self.db.gelecek_tahminlerini_getir()

        # 2030 verilerini filtrele
        veriler_2030 = [(dil, oran, siralama, guven) for dil, yil, oran, siralama, guven in veriler if yil == 2030]

        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(['Dil', '2030 Tahmini', 'Sıralama', 'Güvenilirlik'])
        self.tablo.setRowCount(len(veriler_2030))

        for i, (dil, oran, siralama, guven) in enumerate(veriler_2030):
            self.tablo.setItem(i, 0, QTableWidgetItem(f"{COLORS.get(dil, '')} {dil}"))
            self.tablo.setItem(i, 1, QTableWidgetItem(f"{oran:.1f}%"))
            self.tablo.setItem(i, 2, QTableWidgetItem(str(siralama)))
            self.tablo.setItem(i, 3, QTableWidgetItem(guven or '-'))

        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class BolgeselAnalizWidget(QWidget):
    """Bölgesel analiz sekmesi."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.arayuz_olustur()

    def arayuz_olustur(self):
        layout = QVBoxLayout(self)

        # Ana grafik
        ana_frame = QFrame()
        ana_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        ana_layout = QVBoxLayout(ana_frame)

        baslik = QLabel("🌍 Bölgelere Göre Dil Kullanımı")
        baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 16px; font-weight: bold; padding: 10px;")
        ana_layout.addWidget(baslik)

        self.bolgesel_canvas = MatplotlibCanvas(width=12, height=5)
        ana_layout.addWidget(self.bolgesel_canvas)

        layout.addWidget(ana_frame)

        # Bölge kartları
        kartlar_frame = QFrame()
        kartlar_layout = QHBoxLayout(kartlar_frame)

        bolgeler = ['Türkiye', 'ABD', 'Avrupa', 'İskandinav']
        for bolge in bolgeler:
            kart = self.bolge_karti_olustur(bolge)
            kartlar_layout.addWidget(kart)

        layout.addWidget(kartlar_frame)

        # Grafik çiz
        self.bolgesel_grafik_ciz()

    def bolge_karti_olustur(self, bolge):
        """Bölge kartı oluşturur."""
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px; padding: 10px;")
        layout = QVBoxLayout(frame)

        bayraklar = {
            'Türkiye': '🇹🇷', 'ABD': '🇺🇸', 'Avrupa': '🇪🇺',
            'İskandinav': '🇸🇪', 'İngiltere': '🇬🇧', 'Kanada': '🇨🇦',
            'Latin Amerika': '🌎'
        }

        baslik = QLabel(f"{bayraklar.get(bolge, '🌍')} {bolge}")
        baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: bold;")
        layout.addWidget(baslik)

        # Verileri al
        veriler = self.db.bolgesel_verileri_getir()
        bolge_verileri = [(dil, oran) for dil, b, oran in veriler if b == bolge][:5]

        for dil, oran in bolge_verileri:
            satir = QLabel(f"{dil}: {oran:.0f}%")
            satir.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
            layout.addWidget(satir)

        return frame

    def bolgesel_grafik_ciz(self):
        """Bölgesel karşılaştırma grafiğini çizer."""
        veriler = self.db.bolgesel_verileri_getir()

        # Verileri düzenle
        bolgeler = {}
        for dil, bolge, oran in veriler:
            if bolge not in bolgeler:
                bolgeler[bolge] = {}
            bolgeler[bolge][dil] = oran

        ax = self.bolgesel_canvas.axes
        ax.clear()
        ax.set_facecolor(THEME['bg_card'])

        bolge_isimleri = list(bolgeler.keys())
        x = np.arange(len(bolge_isimleri))
        width = 0.1

        diller = ['JavaScript', 'Python', 'C#', 'PHP', 'Go', 'Rust']

        for i, dil in enumerate(diller):
            degerler = [bolgeler.get(b, {}).get(dil, 0) for b in bolge_isimleri]
            ax.bar(x + i * width, degerler, width, label=dil, color=COLORS.get(dil, '#64748b'))

        ax.set_xlabel('Bölge', color=THEME['text_secondary'])
        ax.set_ylabel('Kullanım (%)', color=THEME['text_secondary'])
        ax.set_xticks(x + width * 2.5)
        ax.set_xticklabels(bolge_isimleri, rotation=45, ha='right', fontsize=8)
        ax.legend(loc='upper right', facecolor=THEME['bg_secondary'], labelcolor=THEME['text_primary'], fontsize=8)
        ax.tick_params(colors=THEME['text_secondary'])

        for spine in ax.spines.values():
            spine.set_color(THEME['text_secondary'])

        self.bolgesel_canvas.fig.tight_layout()
        self.bolgesel_canvas.draw()


class AdaptasyonWidget(QWidget):
    """Adaptasyon hızı sekmesi."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.arayuz_olustur()

    def arayuz_olustur(self):
        layout = QVBoxLayout(self)

        # Ana grafik
        ana_frame = QFrame()
        ana_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        ana_layout = QVBoxLayout(ana_frame)

        baslik = QLabel("⚡ Dillerin Adaptasyon ve Gelişim Hızı")
        baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 16px; font-weight: bold; padding: 10px;")
        ana_layout.addWidget(baslik)

        self.adaptasyon_canvas = MatplotlibCanvas(width=12, height=4)
        ana_layout.addWidget(self.adaptasyon_canvas)

        layout.addWidget(ana_frame)

        # Metrik tablosu
        tablo_frame = QFrame()
        tablo_frame.setStyleSheet(f"background-color: {THEME['bg_card']}; border-radius: 12px;")
        tablo_layout = QVBoxLayout(tablo_frame)

        tablo_baslik = QLabel("🔄 Güncelleme ve Metrik Detayları")
        tablo_baslik.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: bold; padding: 10px;")
        tablo_layout.addWidget(tablo_baslik)

        self.tablo = QTableWidget()
        self.tablo.setStyleSheet(f"""
            QTableWidget {{
                background-color: {THEME['bg_secondary']};
                color: {THEME['text_primary']};
                border: none;
                gridline-color: {THEME['bg_card']};
            }}
            QHeaderView::section {{
                background-color: {THEME['bg_card']};
                color: {THEME['text_primary']};
                padding: 8px;
                border: none;
            }}
        """)
        tablo_layout.addWidget(self.tablo)

        layout.addWidget(tablo_frame)

        # Verileri yükle
        self.adaptasyon_grafigi_ciz()
        self.tablo_doldur()

    def adaptasyon_grafigi_ciz(self):
        """Adaptasyon bar grafiğini çizer."""
        veriler = self.db.adaptasyon_metriklerini_getir()

        diller = [v[0] for v in veriler]
        skorlar = [v[3] for v in veriler]
        renkler = [COLORS.get(d, '#64748b') for d in diller]

        ax = self.adaptasyon_canvas.axes
        ax.clear()
        ax.set_facecolor(THEME['bg_card'])

        bars = ax.bar(diller, skorlar, color=renkler)

        # Değerleri bar üzerine yaz
        for bar, skor in zip(bars, skorlar):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   str(skor), ha='center', color=THEME['text_secondary'], fontsize=9)

        ax.set_ylabel('Adaptasyon Skoru', color=THEME['text_secondary'])
        ax.set_ylim(0, 110)
        ax.tick_params(colors=THEME['text_secondary'])
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        for spine in ax.spines.values():
            spine.set_color(THEME['text_secondary'])

        self.adaptasyon_canvas.fig.tight_layout()
        self.adaptasyon_canvas.draw()

    def tablo_doldur(self):
        """Adaptasyon tablosunu doldurur."""
        veriler = self.db.adaptasyon_metriklerini_getir()

        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels([
            'Dil', 'Güncelleme Sıklığı', 'Son Versiyon',
            'Adaptasyon', 'Beğeni', 'Topluluk'
        ])
        self.tablo.setRowCount(len(veriler))

        for i, (dil, siklik, versiyon, skor, begeni, topluluk) in enumerate(veriler):
            self.tablo.setItem(i, 0, QTableWidgetItem(dil))
            self.tablo.setItem(i, 1, QTableWidgetItem(siklik or '-'))
            self.tablo.setItem(i, 2, QTableWidgetItem(versiyon or '-'))
            self.tablo.setItem(i, 3, QTableWidgetItem(f"{skor}/100"))
            self.tablo.setItem(i, 4, QTableWidgetItem(f"{begeni:.0f}%"))
            self.tablo.setItem(i, 5, QTableWidgetItem(topluluk or '-'))

        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class AnaPencere(QMainWindow):
    """Ana uygulama penceresi."""

    def __init__(self):
        super().__init__()
        self.db = VeritabaniYoneticisi(DB_PATH)
        self.arayuz_olustur()

    def arayuz_olustur(self):
        self.setWindowTitle("📊 Programlama Dilleri İstatistik Dashboard")
        self.setMinimumSize(1400, 900)

        # Tema uygula
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {THEME['bg_primary']};
            }}
            QTabWidget::pane {{
                border: none;
                background-color: {THEME['bg_primary']};
            }}
            QTabBar::tab {{
                background-color: {THEME['bg_card']};
                color: {THEME['text_secondary']};
                padding: 12px 24px;
                margin-right: 4px;
                border-radius: 8px 8px 0 0;
            }}
            QTabBar::tab:selected {{
                background-color: {THEME['accent']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: {THEME['bg_secondary']};
                color: {THEME['text_primary']};
            }}
            QScrollArea {{
                border: none;
                background-color: {THEME['bg_primary']};
            }}
        """)

        # Ana widget
        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)
        ana_layout = QVBoxLayout(ana_widget)

        # Başlık
        baslik_frame = QFrame()
        baslik_frame.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {THEME['accent']}, stop:1 #8b5cf6);
            border-radius: 16px;
            padding: 20px;
        """)
        baslik_layout = QVBoxLayout(baslik_frame)

        baslik = QLabel("🖥️ Programlama Dilleri İstatistik Dashboard")
        baslik.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        baslik.setAlignment(Qt.AlignCenter)

        alt_baslik = QLabel("2010 - 2030 Kullanım Trendleri, Gelecek Tahminleri ve Bölgesel Analiz")
        alt_baslik.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 12px;")
        alt_baslik.setAlignment(Qt.AlignCenter)

        kaynak = QLabel("📊 Kaynaklar: TIOBE Index, Stack Overflow, GitHub Octoverse, JetBrains")
        kaynak.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 10px;")
        kaynak.setAlignment(Qt.AlignCenter)

        baslik_layout.addWidget(baslik)
        baslik_layout.addWidget(alt_baslik)
        baslik_layout.addWidget(kaynak)

        ana_layout.addWidget(baslik_frame)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(GenelBakisWidget(self.db), "📊 Genel Bakış")
        self.tabs.addTab(TrendAnaliziWidget(self.db), "📈 Trend Analizi")
        self.tabs.addTab(GelecekTahminWidget(self.db), "🔮 Gelecek Tahminleri")
        self.tabs.addTab(BolgeselAnalizWidget(self.db), "🌍 Bölgesel Analiz")
        self.tabs.addTab(AdaptasyonWidget(self.db), "⚡ Adaptasyon Hızı")

        ana_layout.addWidget(self.tabs)

        # Footer
        footer = QLabel(f"© 2024 Programlama Dilleri İstatistik Dashboard | Son güncelleme: {datetime.now().strftime('%Y-%m-%d')}")
        footer.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 10px; padding: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        ana_layout.addWidget(footer)


def main():
    """Ana fonksiyon."""
    # Veritabanı kontrolü
    if not os.path.exists(DB_PATH):
        print(f"❌ Veritabanı bulunamadı: {DB_PATH}")
        print("Önce 'python veritabani_olustur.py' komutunu çalıştırın.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(THEME['bg_primary']))
    palette.setColor(QPalette.WindowText, QColor(THEME['text_primary']))
    palette.setColor(QPalette.Base, QColor(THEME['bg_secondary']))
    palette.setColor(QPalette.AlternateBase, QColor(THEME['bg_card']))
    palette.setColor(QPalette.Text, QColor(THEME['text_primary']))
    palette.setColor(QPalette.Button, QColor(THEME['bg_card']))
    palette.setColor(QPalette.ButtonText, QColor(THEME['text_primary']))
    palette.setColor(QPalette.Highlight, QColor(THEME['accent']))
    palette.setColor(QPalette.HighlightedText, QColor('white'))
    app.setPalette(palette)

    pencere = AnaPencere()
    pencere.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
