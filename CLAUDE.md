# CLAUDE.md -- PinterestBulkPostBot

## 1. Project Identity

**Name:** PinterestBulkPostBot -- Pinterest Bulk Image Upload Bot
**Role:** Automate bulk uploading images to Pinterest boards with per-image metadata via CSV (title, description, link, board).
**Author:** SoClose Society (https://soclose.co)
**License:** MIT

### Stack

- **Language:** Python 3.9+
- **Browser:** Selenium 4.20+ with webdriver-manager
- **Parsing:** BeautifulSoup4
- **Config:** JSON (config.json) + CLI args
- **Architecture:** Monolithic (single main.py, 480 LOC)

### Critical Files

- `main.py` -- All logic (480 LOC)
- `config.json` -- Board name, delays, image folder, headless mode

## 2-5. Standard Workflow

- Enter plan mode for non-trivial tasks
- Test with a single image first
- Verify board selection works for your account
- Manual login required (60s wait by default)
- Track tasks in `tasks/todo.md`, lessons in `tasks/lessons.md`

## 6. Project-Specific Rules

### Dev Commands
```bash
pip install -r requirements.txt
# Edit config.json with your board name
# Place images in bulk_post_pinterest/ folder
python main.py
python main.py --csv metadata.csv --board "My Board"
python main.py --headless --delay 5
```

### Config (config.json)
```json
{
  "board_name": "",
  "login_wait_seconds": 60,
  "delay_between_pins": 2,
  "images_folder": "bulk_post_pinterest",
  "headless": false
}
```

### CLI Arguments
- --config FILE -- JSON config path
- --csv FILE -- Per-image metadata CSV
- --headless -- Headless Chrome
- --board NAME -- Board name override
- --delay N -- Delay between pins (seconds)
- --images FOLDER -- Images folder path

### Known Fragile Areas
- Pinterest DOM changes break board selection and pin upload
- Manual login wait (60s) -- no automated auth
- Board selection dropdown -- fragile selector

## 7. Core Principles

- Simplicity First, No Laziness, Minimal Impact
- Never use em dashes (use -- instead)

## Neo Connector (auto)
Ce projet expose `NEO_CONNECTOR.md` : le manifeste machine-lisible de TOUS ses
endpoints/auth/env, consommé par NeoBot pour se câbler automatiquement.
- RÈGLE : à chaque ajout/suppression/modif d'un endpoint, d'une auth ou d'une env var,
  régénère le manifeste via `/neo-connector` (ou le prompt dans .claude/skills/neo-connector).
- Ne jamais éditer NEO_CONNECTOR.md à la main : il est généré.
- Le hook pre-commit (.git/hooks/pre-commit) avertit si des routes ont changé sans MAJ du manifeste.
- NOTE: ce repo n'a AUCUNE API HTTP (CLI/Selenium pur) -- il ne doit PAS être câblé comme outils HTTP Neo.
