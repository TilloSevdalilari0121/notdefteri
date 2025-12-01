# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Not Defteri Pro is a Turkish-language desktop note-taking application built with PyQt5. Features include rich text editing, categories, tags, reminders, Git repository tracking, version history, encrypted notes, PDF export, cloud sync, and dark/light theme support.

## Commands

### Running the Application
```bash
python ana_uygulama.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Module Structure

- **ana_uygulama.py** - Main application entry point and `NotDefteri` QMainWindow class. Handles the three-panel UI layout (sidebar, note list, editor), menu creation, tab switching (Notlar/Git Takip), and coordinates all user interactions.

- **bilesenler.py** - Custom Qt widgets:
  - `HariciResimYukleyiciTextEdit` - QTextEdit with external image loading and translation support
  - `ZenginMetinDuzenleyici` - Rich text editor with formatting toolbar (bold, italic, colors, lists, alignment)
  - `NotKarti` - Note card widget for the list view with signals for click and favorite toggle
  - Dialog classes: `KategoriDuzenleDialog`, `EtiketDuzenleDialog`, `HatirlaticiDialog`, `AyarlarDialog`, `IstatistiklerDialog`, `EtiketSeciciDialog`

- **veritabani.py** - `VeritabaniYoneticisi` class managing SQLite database operations. Tables: `notlar`, `kategoriler`, `etiketler`, `not_etiketleri` (many-to-many), `hatirlaticilar`, `ayarlar`, `surum_gecmisi`, `git_repolar`. Database stored in application folder as `notlar.db`. Includes `_temizle_unicode()` for handling invalid Unicode characters.

- **stiller.py** - `TemaYoneticisi` class generating QSS stylesheets for light (`aydinlik`) and dark (`karanlik`) themes. Exports `RENK_PALETI` and `KATEGORI_IKONLARI` constants.

### moduller/ Directory

- **git_takip.py** - `GitTakipWidget` and `GitKontrolThread` for monitoring GitHub/GitLab repositories. Checks for new commits via API with 1.5s delay between requests to avoid rate limiting.

- **sifreleme.py** - `SifreYoneticisi` for AES-256 encrypted notes

- **surum_gecmisi.py** - `SurumGecmisiYoneticisi` for version history management

- **markdown_editor.py** - `MarkdownDuzenleyici` for Markdown editing and preview

- **kod_blogu.py** - `KodBloguDialog` for syntax-highlighted code blocks

- **pdf_aktarici.py** - `PDFAktarici` for PDF export

- **arama_motoru.py** - `AramaMotoru` and `GelismisAramaDialog` for full-text search

- **bulut_sync.py** - `BulutSenkronizasyon` for Google Drive and Dropbox sync

- **sablonlar.py** - `SablonYoneticisi` for note templates

- **takvim.py** - `TakvimGorunumu` for calendar view

- **web_clipper.py** - `WebClipperYoneticisi` for saving web content

- **ceviri.py** - `CeviriYoneticisi` for translation (uses deep-translator)

- **resim_yoneticisi.py** - `ResimYoneticisi` for image handling

- **ice_aktarici.py** - `IceAktarici` for import functionality

- **coklu_pencere.py** - `CokluPencereYoneticisi` for multi-window support

- **kisayollar.py** - `KisayolYoneticisi` for keyboard shortcuts

- **yapilacaklar.py** - `YapilacaklarYoneticisi` for todo lists

- **baglantilar.py** - `NotBaglantisiYoneticisi` for inter-note links ([[Note]])

- **otomatik_kayit.py** - `OtomatikKayitYoneticisi` for auto-save

### Key Patterns

- Signal-slot connections established in `_baglantilari_kur()` method
- Database access uses context manager pattern (`_baglanti_al()`)
- Theme changes applied via `setStyleSheet()` with generated QSS
- Notes use soft delete (moved to trash via `silindi` flag)
- Reminder checking runs on 60-second QTimer interval
- Git repo checking uses background QThread with rate limiting

### UI Layout

**Top Bar** (left to right):
- Tab buttons: Notlar (📝), Git Takip (🔄), Takvim (📅), İstatistikler (📊)
- Note dropdown selector (`not_secici_combo`) - always visible, auto-updates
- Search input (`ust_arama_input`)
- Advanced search button (`ust_gelismis_arama_btn`)

**Three-panel design** using QSplitter (when Notlar tab active):
1. Left sidebar (160-220px): Filters list (stretch 2), categories tree (stretch 3), tags list (stretch 2)
2. Middle panel (250px min): Note cards in scrollable list - can be hidden via Görünüm menu (Ctrl+L)
3. Right panel: Title input, category/tag selection, rich text editor, save/version history/delete buttons

**Git Takip view** (when Git Takip tab active):
- Repo list with status indicators (🟢 updated, ⚪ no changes)
- Add repo, check for updates buttons
- Progress bar during checks

### Settings Persistence

User preferences saved to `ayarlar` table in database:
- `ayar_kaydet(anahtar, deger)` - Save setting
- `ayar_getir(anahtar, varsayilan)` - Get setting with default
- Settings loaded on startup via `_ayarlari_yukle()`
- Persists: theme choice (`tema`), panel visibility (`not_listesi_gorunur`)

## Language

All code comments, variable names, database columns, and UI text are in Turkish. Key terms:
- not/notlar = note/notes
- kategori = category
- etiket = tag
- hatirlatici = reminder
- favori = favorite
- silindi = deleted (trash)
- tema = theme
- aydinlik/karanlik = light/dark
- surum = version
- gorunur = visible
- gizle/goster = hide/show
- repo/repolar = repository/repositories
- takip = tracking/follow
- icerik = content
- baslik = title
- zengin_icerik = rich content (HTML)

## Known Issues & Solutions

- **GitHub API Rate Limit**: Handled with 1.5s delay between requests in `git_takip.py`
- **Unicode Surrogate Errors**: `_temizle_unicode()` in `veritabani.py` cleans invalid characters
- **Search Input**: Use `self.ust_arama_input` (not `self.arama_input`)

## File Locations

- Database: `{app_folder}/notlar.db`
- Images saved by web clipper stored locally with MD5-based filenames
