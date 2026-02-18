<h1 align="center">Pinterest Bulk Post Bot</h1>

<p align="center">
  <strong>Automate bulk posting of images to Pinterest - Upload hundreds of pins in minutes instead of hours.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python 3.8+"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <a href="https://www.selenium.dev/"><img src="https://img.shields.io/badge/Selenium-4.20%2B-orange.svg" alt="Selenium"></a>
  <a href="https://github.com/SoCloseSociety/PinterestBulkPostBot/stargazers"><img src="https://img.shields.io/github/stars/SoCloseSociety/PinterestBulkPostBot?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/SoCloseSociety/PinterestBulkPostBot/issues"><img src="https://img.shields.io/github/issues/SoCloseSociety/PinterestBulkPostBot" alt="Issues"></a>
  <a href="https://github.com/SoCloseSociety/PinterestBulkPostBot/network/members"><img src="https://img.shields.io/github/forks/SoCloseSociety/PinterestBulkPostBot?style=social" alt="Forks"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#key-features">Features</a> &bull;
  <a href="#configuration">Configuration</a> &bull;
  <a href="#faq">FAQ</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

---

## What is Pinterest Bulk Post Bot?

**Pinterest Bulk Post Bot** is a free, open-source **Pinterest automation tool** built with Python and Selenium. It lets you **bulk upload images to Pinterest** directly from your computer. Instead of manually creating pins one by one, this bot automates the entire process: uploading images, filling in titles, descriptions, destination links, and selecting boards - all in one go.

Whether you need to post 10 pins or 1000, this **Pinterest pin scheduler** handles it automatically while you focus on what matters.

### Who is this for?

- **Pinterest Marketers** looking to scale their pinning strategy
- **Bloggers** who want to drive traffic from Pinterest to their blog posts
- **E-commerce Sellers** promoting products on Pinterest at scale
- **Social Media Managers** handling multiple Pinterest accounts
- **Affiliate Marketers** bulk-posting promotional pins
- **Content Creators** who want to save hours of manual work

### Key Features

- **Bulk Upload** - Post dozens or hundreds of pins in one session
- **Cross-Platform** - Works on Windows, macOS, and Linux
- **Per-Image Metadata** - Use a CSV file to set unique title, description, link, and board for each pin
- **Configurable** - JSON config file for persistent settings
- **Smart Waits** - Uses intelligent waits instead of fixed delays for reliability
- **Progress Tracking** - Real-time progress bar and logging
- **Error Recovery** - Continues posting even if individual pins fail
- **CLI Arguments** - Full command-line interface with options
- **Headless Mode** - Run without a visible browser window
- **Free & Open Source** - MIT license, no API key required

---

## Quick Start

### Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | Version 3.8 or higher ([Download](https://www.python.org/downloads/)) |
| **Google Chrome** | Latest version ([Download](https://www.google.com/chrome/)) |
| **Pinterest Account** | A valid Pinterest account |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/SoCloseSociety/PinterestBulkPostBot.git
cd PinterestBulkPostBot

# 2. (Recommended) Create a virtual environment
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Usage

#### Basic Usage (same metadata for all pins)

```bash
python main.py
```

The bot will:
1. Open Chrome and navigate to Pinterest login
2. Wait for you to log in manually
3. Ask you for a title, description, link, and board name
4. Upload all images from the `bulk_post_pinterest/` folder

#### Advanced Usage (per-image metadata with CSV)

```bash
python main.py --csv pins.csv
```

#### All CLI Options

```bash
python main.py --help
```

| Option | Description | Default |
|--------|-------------|---------|
| `--config FILE` | Path to JSON config file | `config.json` |
| `--csv FILE` | Path to CSV file with per-image metadata | None |
| `--headless` | Run Chrome without visible window | Off |
| `--board NAME` | Pinterest board name to post to | (interactive) |
| `--images FOLDER` | Path to folder containing images | `bulk_post_pinterest/` |

#### Examples

```bash
# Post all images to "My Recipes" board
python main.py --board "My Recipes"

# Use a CSV for unique metadata per pin
python main.py --csv my_pins.csv --board "Travel"

# Run in background (headless) with custom image folder
python main.py --headless --images ./my_photos --board "Photography"

# Use a custom config file
python main.py --config my_config.json
```

---

## Configuration

### Config File (`config.json`)

Create or edit `config.json` in the project root:

```json
{
    "board_name": "My Board",
    "login_wait_seconds": 60,
    "delay_between_pins": 2,
    "images_folder": "bulk_post_pinterest",
    "headless": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `board_name` | string | Default Pinterest board name |
| `login_wait_seconds` | number | Seconds to wait for manual login |
| `delay_between_pins` | number | Seconds to wait between each pin |
| `images_folder` | string | Folder containing images to upload |
| `headless` | boolean | Run Chrome without visible window |

### CSV File for Per-Image Metadata

Create a CSV file with unique title, description, link, and board for each pin:

```csv
filename,title,description,link,board
photo1.jpg,Beautiful Sunset,A stunning sunset over the ocean,https://myblog.com/sunset,Travel
photo2.png,Recipe Card,Easy pasta recipe in 30 minutes,https://myblog.com/pasta,Recipes
```

| Column | Required | Description |
|--------|----------|-------------|
| `filename` | Yes | Image filename (must match file in images folder) |
| `title` | Yes | Pin title |
| `description` | Yes | Pin description |
| `link` | No | Destination URL for the pin |
| `board` | No | Board name (overrides default) |

See [pins_example.csv](pins_example.csv) for a ready-to-use template.

---

## Supported Image Formats

| Format | Extension |
|--------|-----------|
| JPEG | `.jpg`, `.jpeg` |
| PNG | `.png` |
| GIF | `.gif` |
| WebP | `.webp` |
| BMP | `.bmp` |
| TIFF | `.tiff` |

---

## Project Structure

```
PinterestBulkPostBot/
├── main.py                 # Main bot script
├── config.json             # Configuration file
├── pins_example.csv        # Example CSV for per-image metadata
├── requirements.txt        # Python dependencies
├── bulk_post_pinterest/    # Default folder for images to upload
│   └── (your images here)
├── LICENSE                 # MIT License
├── README.md               # This file
├── CONTRIBUTING.md         # Contribution guidelines
└── .gitignore              # Git ignore rules
```

---

## Troubleshooting

### Chrome driver issues

The bot uses `webdriver-manager` to automatically download the correct ChromeDriver version. If you encounter issues:

```bash
pip install --upgrade webdriver-manager
```

### Login timeout

If 60 seconds isn't enough to log in, increase the timeout in `config.json`:

```json
{
    "login_wait_seconds": 120
}
```

### Pinterest UI changes

Pinterest occasionally updates its web interface. If the bot stops working:
1. Check the [Issues](https://github.com/SoCloseSociety/PinterestBulkPostBot/issues) page for known problems
2. Open a new issue with the error message

### Permission denied errors (macOS/Linux)

```bash
chmod +x main.py
```

---

## FAQ

**Q: Is this free?**
A: Yes. Pinterest Bulk Post Bot is 100% free and open source under the MIT license.

**Q: Do I need a Pinterest API key?**
A: No. This tool uses browser automation (Selenium), so no API key or developer account is needed.

**Q: How many pins can I post at once?**
A: There is no hard limit. The bot posts pins one by one, so you can upload as many images as you have in your folder. Just be mindful of Pinterest's usage policies.

**Q: Does it work with Pinterest business accounts?**
A: Yes. It works with both personal and business Pinterest accounts.

**Q: Can I set different titles and descriptions for each pin?**
A: Yes! Use the `--csv` option with a CSV file to provide unique metadata for each image. See [Configuration](#csv-file-for-per-image-metadata).

**Q: Does it work on Mac / Linux?**
A: Yes. The bot is fully cross-platform and works on Windows, macOS, and Linux.

**Q: Can I run it without opening a browser window?**
A: Yes. Use `--headless` mode: `python main.py --headless`

---

## Demo

A demo video (`watch_me.mp4`) is included in the repository. Clone the project and watch it locally to see the bot in action.

---

## Alternatives Comparison

| Feature | Pinterest Bulk Post Bot | Manual Posting | Tailwind | Buffer |
|---------|------------------------|----------------|----------|--------|
| Price | Free | Free | $14.99/mo | $15/mo |
| Bulk upload | Yes | No | Limited | Limited |
| Custom metadata per pin | Yes (CSV) | Yes | Yes | Yes |
| Open source | Yes | N/A | No | No |
| API key required | No | No | Yes | Yes |
| Cross-platform | Yes | Yes | Web only | Web only |
| Headless mode | Yes | N/A | N/A | N/A |

---

## Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) before submitting a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Disclaimer

This tool is provided for **educational and personal productivity purposes only**. Use it responsibly and in compliance with [Pinterest's Terms of Service](https://policy.pinterest.com/en/terms-of-service). The authors are not responsible for any misuse or consequences arising from the use of this software.

---

<p align="center">
  If this project helps you, please give it a <strong>star</strong>! It helps others discover this tool.<br><br>
  <a href="https://github.com/SoCloseSociety/PinterestBulkPostBot">
    <img src="https://img.shields.io/github/stars/SoCloseSociety/PinterestBulkPostBot?style=for-the-badge&logo=github" alt="Star this repo">
  </a>
</p>
