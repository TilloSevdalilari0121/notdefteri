# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Not Defteri Pro is a Turkish-language desktop note-taking application built with PyQt5. It provides rich text editing, categories, tags, reminders, Git repository tracking, version history, dark/light theme support, and settings persistence.

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

- **ana_uygulama.py** - Main application entry point and `NotDefteri` QMainWindow class. Handles the three-panel UI layout (sidebar, note list, editor), menu creation, and coordinates all user interactions.

- **bilesenler.py** - Custom Qt widgets:
  - `ZenginMetinDuzenleyici` - Rich text editor with formatting toolbar (bold, italic, colors, lists, alignment)
  - `NotKarti` - Note card widget for the list view with signals for click and favorite toggle
  - Dialog classes: `KategoriDuzenleDialog`, `EtiketDuzenleDialog`, `HatirlaticiDialog`, `AyarlarDialog`, `IstatistiklerDialog`, `EtiketSeciciDialog`

- **veritabani.py** - `VeritabaniYoneticisi` class managing SQLite database operations. Tables: `notlar`, `kategoriler`, `etiketler`, `not_etiketleri` (many-to-many), `hatirlaticilar`, `ayarlar`, `surumler` (version history). Database stored at `~/Documents/NotDefteri/notlar.db`. Includes `_temizle_unicode()` for handling invalid Unicode characters.

- **moduller/git_takip.py** - `GitTakipWidget` for monitoring GitHub repositories. Features:
  - Add/remove GitHub repos to track
  - Background thread (`RepoKontrolThread`) checks for new commits
  - Rate limit handling with 1.5 second delay between API requests
  - Desktop notifications for new commits
  - Stores tracked repos in `git_repolar.json`

- **stiller.py** - `TemaYoneticisi` class generating QSS stylesheets for light (`aydinlik`) and dark (`karanlik`) themes. Also exports `RENK_PALETI` and `KATEGORI_IKONLARI` constants.

### Key Patterns

- Signal-slot connections established in `_baglantilari_kur()` method
- Database access uses context manager pattern (`_baglanti_al()`)
- Theme changes applied via `setStyleSheet()` with generated QSS
- Notes use soft delete (moved to trash via `silindi` flag)
- Reminder checking runs on 60-second QTimer interval

### UI Layout

**Top Bar** (left to right):
- Tab buttons: Notlar (notes), Git Takip, Takvim (calendar), İstatistikler (statistics)
- Note dropdown selector (`not_secici_combo`) - always visible, auto-updates on note changes
- Search input (`ust_arama_input`)
- Advanced search button (`ust_gelismis_arama_btn`)

**Three-panel design** using QSplitter:
1. Left sidebar (180-250px): Filters list (stretch 2), categories tree (stretch 3), tags list (stretch 2)
2. Middle panel (250px min): Note cards in scrollable list - can be hidden via Görünüm menu (Ctrl+L)
3. Right panel (400px min): Title input, metadata, rich text editor, save/delete/version history buttons

### Settings Persistence

User preferences saved to `ayarlar` table in database:
- `ayar_kaydet(anahtar, deger)` - Save setting
- `ayar_getir(anahtar, varsayilan)` - Get setting with default
- Settings loaded on startup via `_ayarlari_yukle()`
- Persists: theme choice, panel visibility, etc.

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

## Known Issues & Solutions

- **GitHub API Rate Limit**: Handled with 1.5s delay between requests in `git_takip.py`
- **Unicode Surrogate Errors**: `_temizle_unicode()` in `veritabani.py` cleans invalid characters
- **Search Input**: Use `self.ust_arama_input` (not `self.arama_input`)

## File Locations

- Database: `~/Documents/NotDefteri/notlar.db`
- Git repos config: `~/Documents/NotDefteri/git_repolar.json`
- Attachments: `~/Documents/NotDefteri/ekler/`
