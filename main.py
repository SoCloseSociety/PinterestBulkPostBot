#!/usr/bin/env python3
"""
Pinterest Bulk Post Bot - Automate bulk posting of images to Pinterest.

Supports Windows, macOS, and Linux.
Usage: python main.py [--config config.json] [--csv pins.csv] [--headless]
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PINTEREST_LOGIN_URL = "https://www.pinterest.com/login/"
PINTEREST_PIN_BUILDER_URL = "https://www.pinterest.com/pin-builder/"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}
DEFAULT_IMAGES_FOLDER = "bulk_post_pinterest"
DEFAULT_CONFIG_FILE = "config.json"
DEFAULT_TIMEOUT = 30  # seconds for WebDriverWait

BANNER = r"""
  ____  _       _                    _     ____        _ _      ____           _
 |  _ \(_)_ __ | |_ ___ _ __ ___  _| |_  | __ ) _   _| | | __ |  _ \ ___  __| |_
 | |_) | | '_ \| __/ _ \ '__/ _ \/ __| __||  _ \| | | | | |/ / | |_) / _ \/ __| __|
 |  __/| | | | | ||  __/ | |  __/\__ \ |_ | |_) | |_| | |   <  |  __/ (_) \__ \ |_
 |_|   |_|_| |_|\__\___|_|  \___||___/\__||____/ \__,_|_|_|\_\ |_|   \___/|___/\__|
                                                              Bot v2.0
"""

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("PinterestBot")

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def xpath_soup(element):
    """Build an XPath string from a BeautifulSoup element."""
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if siblings == [child]
            else "%s[%d]" % (child.name, 1 + siblings.index(child))
        )
        child = parent
    components.reverse()
    return "/%s" % "/".join(components)


def load_config(config_path):
    """Load configuration from a JSON file. Returns defaults if file not found."""
    defaults = {
        "board_name": "",
        "login_wait_seconds": 60,
        "delay_between_pins": 2,
        "images_folder": DEFAULT_IMAGES_FOLDER,
        "headless": False,
    }
    if config_path and os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            defaults.update(user_config)
            logger.info("Configuration loaded from %s", config_path)
        except (ValueError, IOError) as exc:
            logger.warning("Could not read config file (%s). Using defaults.", exc)
    return defaults


def load_csv_metadata(csv_path):
    """
    Load per-image metadata from a CSV file.

    Expected columns: filename, title, description, link, board (optional)
    Returns a dict keyed by filename (basename).
    """
    metadata = {}
    if not csv_path or not os.path.isfile(csv_path):
        return metadata
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = os.path.basename(row.get("filename", "").strip())
                if key:
                    metadata[key] = {
                        "title": row.get("title", "").strip(),
                        "description": row.get("description", "").strip(),
                        "link": row.get("link", "").strip(),
                        "board": row.get("board", "").strip(),
                    }
        logger.info("Loaded metadata for %d images from %s", len(metadata), csv_path)
    except (csv.Error, ValueError, IOError) as exc:
        logger.warning("Could not read CSV file (%s). Skipping.", exc)
    return metadata


def discover_images(folder_path):
    """Return a sorted list of image file paths in *folder_path*."""
    folder = Path(folder_path)
    if not folder.is_dir():
        logger.error("Images folder not found: %s", folder)
        sys.exit(1)

    images = sorted(
        str(p) for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not images:
        logger.error("No images found in %s", folder)
        sys.exit(1)

    logger.info("Found %d image(s) in %s", len(images), folder)
    return images


def create_driver(headless=False):
    """Create and return a configured Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as exc:
        logger.error("Failed to start Chrome: %s", exc)
        logger.info("Make sure Google Chrome is installed on your system.")
        sys.exit(1)

    return driver


def progress_bar(current, total, width=40):
    """Return a text progress bar string."""
    pct = current / total
    filled = int(width * pct)
    bar = "\u2588" * filled + "\u2591" * (width - filled)
    return f"|{bar}| {current}/{total} ({pct:.0%})"


# ---------------------------------------------------------------------------
# Core bot logic
# ---------------------------------------------------------------------------


def wait_for_login(driver, timeout_seconds):
    """Open Pinterest login page and wait for the user to log in."""
    driver.get(PINTEREST_LOGIN_URL)
    logger.info("Pinterest login page opened.")
    print()
    print("  Please log in to your Pinterest account in the browser window.")
    print(f"  You have {timeout_seconds} seconds to complete login.")
    print()

    # Wait until the user navigates away from the login page
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        current_url = driver.current_url
        if "/login" not in current_url:
            logger.info("Login detected! Continuing...")
            return True
        time.sleep(1)

    # If still on login page, ask for manual confirmation
    choice = input("\n  Are you logged in? (y/n): ").strip().lower()
    if choice == "y":
        return True
    logger.error("Login not confirmed. Exiting.")
    return False


def wait_for_element(driver, by, value, timeout=DEFAULT_TIMEOUT):
    """Wait for an element and return it."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_for_clickable(driver, by, value, timeout=DEFAULT_TIMEOUT):
    """Wait for an element to be clickable and return it."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )


def upload_image(driver, image_path):
    """Upload an image file to the pin builder."""
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
    file_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(os.path.abspath(image_path))
    time.sleep(2)


def fill_pin_details(driver, title, description, link):
    """Fill in the title, description, and link fields for a pin."""
    # Title
    try:
        title_field = wait_for_clickable(
            driver, By.XPATH, "//textarea[contains(@id,'pin-draft-title')]"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", title_field)
        time.sleep(0.5)
        title_field.click()
        title_field.send_keys(title)
    except Exception as exc:
        logger.warning("Could not fill title: %s", exc)

    # Description
    try:
        desc_field = wait_for_clickable(
            driver, By.XPATH, "//div[contains(@id,'pin-draft-description')]"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", desc_field)
        time.sleep(0.5)
        desc_field.click()
        time.sleep(1)
        ActionChains(driver).move_to_element(desc_field).send_keys(description).perform()
    except Exception as exc:
        logger.warning("Could not fill description: %s", exc)

    # Link
    try:
        link_field = wait_for_clickable(
            driver, By.XPATH, "//textarea[contains(@id,'pin-draft-link')]"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", link_field)
        time.sleep(0.5)
        link_field.click()
        link_field.send_keys(link)
    except Exception as exc:
        logger.warning("Could not fill link: %s", exc)


def select_board(driver, board_name):
    """Select a Pinterest board by name."""
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        select_btn = soup.find("button", attrs={"data-test-id": "board-dropdown-select-button"})
        if not select_btn:
            logger.warning("Board dropdown button not found.")
            return

        element = driver.find_element(By.XPATH, xpath_soup(select_btn))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        element.click()
        time.sleep(1)

        search_field = wait_for_clickable(driver, By.ID, "pickerSearchField")
        search_field.send_keys(board_name)
        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        first_board = soup.find("div", attrs={"data-test-id": "boardWithoutSection"})
        if first_board:
            driver.find_element(By.XPATH, xpath_soup(first_board)).click()
            time.sleep(1)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        save_btn = soup.find("button", attrs={"data-test-id": "board-dropdown-save-button"})
        if save_btn:
            driver.find_element(By.XPATH, xpath_soup(save_btn)).click()
            time.sleep(1)

    except Exception as exc:
        logger.warning("Could not select board '%s': %s", board_name, exc)


def wait_for_publish(driver, timeout=60):
    """Wait until the pin finishes publishing."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        loading = soup.find("svg", attrs={"role": "img", "aria-label": "Saving Pin..."})
        if loading is None:
            return True
        time.sleep(2)
    logger.warning("Publish timeout - pin may not have saved properly.")
    return False


def post_single_pin(driver, image_path, title, description, link, board_name):
    """Post a single pin to Pinterest."""
    upload_image(driver, image_path)
    fill_pin_details(driver, title, description, link)
    if board_name:
        select_board(driver, board_name)
    time.sleep(2)
    wait_for_publish(driver)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main():
    print(BANNER)

    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Pinterest Bulk Post Bot - Automate posting images to Pinterest.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG_FILE,
        help="Path to JSON config file (default: config.json)",
    )
    parser.add_argument(
        "--csv", default=None,
        help="Path to CSV file with per-image metadata",
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Run Chrome in headless mode (no visible browser window)",
    )
    parser.add_argument(
        "--board", default=None,
        help="Pinterest board name to post to",
    )
    parser.add_argument(
        "--images", default=None,
        help="Path to folder containing images to post",
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # CLI args override config file
    headless = args.headless or config.get("headless", False)
    images_folder = args.images or config.get("images_folder", DEFAULT_IMAGES_FOLDER)
    board_name = args.board or config.get("board_name", "")
    csv_path = args.csv

    # Resolve images folder (relative to script location)
    if not os.path.isabs(images_folder):
        images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), images_folder)

    # Discover images
    images = discover_images(images_folder)

    # Load CSV metadata if provided
    csv_metadata = load_csv_metadata(csv_path)

    # Collect default metadata from user if no CSV provided
    default_title = ""
    default_description = ""
    default_link = ""

    if not csv_metadata:
        print("  Enter the default metadata for your pins:")
        print("  (Leave blank to skip a field)\n")
        default_title = input("  Title: ").strip()
        default_description = input("  Description: ").strip()
        default_link = input("  Link: ").strip()
        print()

    if not board_name:
        board_name = input("  Board name: ").strip()
        print()

    # Start browser
    logger.info("Starting Chrome browser...")
    driver = create_driver(headless=headless)

    try:
        # Login
        if not wait_for_login(driver, config.get("login_wait_seconds", 60)):
            driver.quit()
            sys.exit(1)

        total = len(images)
        successful = 0
        failed = 0

        print(f"\n  Starting to post {total} pin(s)...\n")

        for i, image_path in enumerate(images, start=1):
            filename = os.path.basename(image_path)
            meta = csv_metadata.get(filename, {})

            title = meta.get("title") or default_title
            description = meta.get("description") or default_description
            link = meta.get("link") or default_link
            pin_board = meta.get("board") or board_name

            logger.info(
                "Posting %s  %s",
                progress_bar(i, total),
                filename,
            )

            try:
                # Navigate to pin builder
                driver.get(PINTEREST_PIN_BUILDER_URL)
                time.sleep(config.get("delay_between_pins", 2))

                # Wait for pin builder to load
                wait_for_element(
                    driver, By.CSS_SELECTOR, "input[type='file']", timeout=DEFAULT_TIMEOUT
                )

                post_single_pin(driver, image_path, title, description, link, pin_board)
                successful += 1
                logger.info("Pin %d/%d posted successfully.", i, total)

            except Exception as exc:
                failed += 1
                logger.error("Failed to post pin %d/%d (%s): %s", i, total, filename, exc)
                continue

        # Summary
        print("\n" + "=" * 60)
        print(f"  COMPLETED: {successful} posted | {failed} failed | {total} total")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        logger.info("Interrupted by user. Stopping...")

    finally:
        driver.quit()
        logger.info("Browser closed. Goodbye!")


if __name__ == "__main__":
    main()
