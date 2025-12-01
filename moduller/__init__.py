# -*- coding: utf-8 -*-
"""
Not Defteri - Modüller Paketi
Tüm ek özelliklerin modülleri burada bulunur.
"""

from .markdown_editor import MarkdownOnizleyici, MarkdownDuzenleyici
from .sifreleme import SifreYoneticisi, SifreliNotDialog
from .otomatik_kayit import OtomatikKayitYoneticisi
from .surum_gecmisi import SurumGecmisiYoneticisi, SurumGecmisiDialog
from .baglantilar import NotBaglantisiYoneticisi, BaglantiOnizleyici
from .yapilacaklar import YapilacaklarYoneticisi, YapilacaklarWidget
from .resim_yoneticisi import ResimYoneticisi, ResimDialog
from .kod_blogu import KodBloguWidget, KodDilSecici, KodBloguDialog
from .pdf_aktarici import PDFAktarici
from .arama_motoru import AramaMotoru, GelismisAramaDialog
from .kisayollar import KisayolYoneticisi, KisayollarDialog
from .bulut_sync import BulutSenkronizasyon, BulutAyarlariDialog
from .sablonlar import SablonYoneticisi, SablonSeciciDialog
from .takvim import TakvimGorunumu, TakvimWidget
from .ice_aktarici import IceAktarici, IceAktarmaDialog
from .coklu_pencere import CokluPencereYoneticisi, AyrikNotPenceresi
from .web_clipper import WebClipperYoneticisi, WebClipperDialog, HizliKlipWidget
from .ceviri import CeviriDialog, CeviriYoneticisi
from .git_takip import GitTakipWidget, GitKontrolThread

__all__ = [
    'MarkdownOnizleyici', 'MarkdownDuzenleyici',
    'SifreYoneticisi', 'SifreliNotDialog',
    'OtomatikKayitYoneticisi',
    'SurumGecmisiYoneticisi', 'SurumGecmisiDialog',
    'NotBaglantisiYoneticisi', 'BaglantiOnizleyici',
    'YapilacaklarYoneticisi', 'YapilacaklarWidget',
    'ResimYoneticisi', 'ResimDialog',
    'KodBloguWidget', 'KodDilSecici', 'KodBloguDialog',
    'PDFAktarici',
    'AramaMotoru', 'GelismisAramaDialog',
    'KisayolYoneticisi', 'KisayollarDialog',
    'BulutSenkronizasyon', 'BulutAyarlariDialog',
    'SablonYoneticisi', 'SablonSeciciDialog',
    'TakvimGorunumu', 'TakvimWidget',
    'IceAktarici', 'IceAktarmaDialog',
    'CokluPencereYoneticisi', 'AyrikNotPenceresi',
    'WebClipperYoneticisi', 'WebClipperDialog', 'HizliKlipWidget',
    'CeviriDialog', 'CeviriYoneticisi',
    'GitTakipWidget', 'GitKontrolThread',
]
