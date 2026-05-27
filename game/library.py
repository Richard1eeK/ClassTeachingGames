"""Built-in material library.

Folder layout under data/library/:

    data/library/
      flashcards/{Series}/{Level}/{Unit}/*.png|jpg|...
      flashcards/Bright Spark/{Topic}/*.png|jpg|...
      words/{Series}/{Level}/{Unit}.txt

The folder/file names are used directly as display names — no manifest
file is required. Empty branches are pruned automatically so the UI only
shows materials that actually have content, except Bright Spark topic folders
which stay visible as ready-to-fill category shelves.
"""
import os
import re
from typing import Dict, List

from game.assets import resource_path
from game.question_bank import (
    IMAGE_EXTENSIONS,
    read_text_bank_file,
    scan_image_folder,
)


CATEGORY_FLASHCARDS = "flashcards"
CATEGORY_WORDS = "words"
CATEGORIES = (CATEGORY_FLASHCARDS, CATEGORY_WORDS)
BRIGHT_SPARK_SERIES = "Bright Spark"
BRIGHT_SPARK_TOPIC_UNIT = "__topic__"
BRIGHT_SPARK_TOPICS = [
    "Activities",
    "Adjectives",
    "Animal Parts",
    "Body Parts",
    "Characters",
    "Classroom Items",
    "Clothes",
    "Colours",
    "Days",
    "Directions",
    "Family",
    "Farm Animals",
    "Feelings",
    "Foods and Drinks",
    "Fruits",
    "Household Items",
    "Jobs and Responsibilities",
    "Jobs",
    "Months",
    "Natural World",
    "Numbers",
    "Pets",
    "Places",
    "Prepositions",
    "Pronouns",
    "Rooms",
    "Routines",
    "Seasons",
    "Shapes",
    "Short Answers",
    "Sports",
    "Time of Day",
    "Toys",
    "Vegetables",
    "Verbs",
    "Weather",
    "Wild Animals",
]


def _library_root() -> str:
    """Absolute path to data/library/, PyInstaller-compatible."""
    return resource_path("data", "library")


def natural_sort_key(s: str):
    """Split a string into chunks of digits and non-digits for natural sort.

    "Level 2"  -> ["level ", 2]
    "Level 10" -> ["level ", 10]
    "Level C"  -> ["level c"]
    """
    parts = re.split(r"(\d+)", str(s))
    key = []
    for part in parts:
        if not part:
            continue
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key


def _list_subdirs(path: str) -> List[str]:
    """List immediate subdirectory names (no recursion), sorted naturally."""
    if not os.path.isdir(path):
        return []
    try:
        names = os.listdir(path)
    except OSError:
        return []
    subdirs = [n for n in names
               if not n.startswith(".")
               and os.path.isdir(os.path.join(path, n))]
    subdirs.sort(key=natural_sort_key)
    return subdirs


def _is_phonics_name(name: str) -> bool:
    """True for folders/files that should stay out of Bright Spark topics."""
    return "phonics" in name.lower()


def _has_images(folder: str) -> bool:
    """True if folder contains at least one image file (first level only)."""
    if not os.path.isdir(folder):
        return False
    try:
        for name in os.listdir(folder):
            ext = os.path.splitext(name)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                full = os.path.join(folder, name)
                if os.path.isfile(full):
                    return True
    except OSError:
        return False
    return False


def _list_txt_units(level_dir: str) -> List[str]:
    """List `.txt` files under a level dir, returning Unit names without `.txt`.

    Naturally sorted. Hidden files and empty files (0 bytes) are skipped, so
    placeholder files don't show up in the UI until the teacher actually adds
    content to them.
    """
    if not os.path.isdir(level_dir):
        return []
    try:
        names = os.listdir(level_dir)
    except OSError:
        return []
    units = []
    for name in names:
        if name.startswith("."):
            continue
        if not name.lower().endswith(".txt"):
            continue
        full = os.path.join(level_dir, name)
        if not os.path.isfile(full):
            continue
        try:
            if os.path.getsize(full) == 0:
                continue
        except OSError:
            continue
        units.append(os.path.splitext(name)[0])
    units.sort(key=natural_sort_key)
    return units


def scan_library() -> Dict[str, Dict[str, Dict[str, List[str]]]]:
    """Scan data/library/ and build a 4-level index.

    Returns:
        {
            "flashcards": {
                "Bright Spark": {
                    "Level 1": ["Unit 1", "Unit 2"],
                    ...
                },
                ...
            },
            "words": {
                "High Flyer": {
                    "Level D": ["Unit 1", ...],
                    ...
                },
            },
        }

    Empty Series / Level branches are pruned so the UI never shows an empty
    folder. The library is rescanned every call (it's cheap — pure os.listdir
    over ~100 entries).
    """
    root = _library_root()
    index: Dict[str, Dict[str, Dict[str, List[str]]]] = {}

    for category in CATEGORIES:
        category_root = os.path.join(root, category)
        if not os.path.isdir(category_root):
            continue

        series_map: Dict[str, Dict[str, List[str]]] = {}
        for series in _list_subdirs(category_root):
            series_dir = os.path.join(category_root, series)
            level_map: Dict[str, List[str]] = {}

            if category == CATEGORY_FLASHCARDS and series == BRIGHT_SPARK_SERIES:
                existing_topics = set(_list_subdirs(series_dir))
                ordered_topics = [topic for topic in BRIGHT_SPARK_TOPICS if topic in existing_topics]
                extra_topics = [
                    topic for topic in sorted(existing_topics, key=natural_sort_key)
                    if topic not in BRIGHT_SPARK_TOPICS
                ]
                for topic in ordered_topics + extra_topics:
                    if _is_phonics_name(topic):
                        continue
                    level_map[topic] = [BRIGHT_SPARK_TOPIC_UNIT]

                if level_map:
                    series_map[series] = level_map
                continue

            for level in _list_subdirs(series_dir):
                level_dir = os.path.join(series_dir, level)
                if category == CATEGORY_FLASHCARDS:
                    # Flashcards: Unit is a sub-folder containing images
                    units = [
                        unit for unit in _list_subdirs(level_dir)
                        if _has_images(os.path.join(level_dir, unit))
                    ]
                else:
                    # Words: Unit is a .txt file
                    units = _list_txt_units(level_dir)

                if units:
                    level_map[level] = units

            if level_map:
                series_map[series] = level_map

        if series_map:
            index[category] = series_map

    return index


def list_categories(index: Dict) -> List[str]:
    """Return categories that actually have content."""
    return [c for c in CATEGORIES if c in index]


def list_series(index: Dict, category: str) -> List[str]:
    """Return series names for a given category."""
    return list(index.get(category, {}).keys())


def list_levels(index: Dict, category: str, series: str) -> List[str]:
    """Return level names for a given series."""
    return list(index.get(category, {}).get(series, {}).keys())


def list_units(index: Dict, category: str, series: str, level: str) -> List[str]:
    """Return unit names for a given level."""
    return list(index.get(category, {}).get(series, {}).get(level, []))


def load_unit(category: str, series: str, level: str, unit: str) -> List[Dict]:
    """Load actual items for a Unit.

    For flashcards: scans the unit folder for images.
    For words: parses the unit's .txt file.

    Returns a list of items in the standard format:
        [{"type": "text"|"image", "content": str, "hint": str}, ...]

    Returns an empty list on any error (missing folder/file, etc.).
    """
    root = _library_root()
    if category == CATEGORY_FLASHCARDS:
        if series == BRIGHT_SPARK_SERIES and unit == BRIGHT_SPARK_TOPIC_UNIT:
            folder = os.path.join(root, category, series, level)
        else:
            folder = os.path.join(root, category, series, level, unit)
        return scan_image_folder(folder)
    elif category == CATEGORY_WORDS:
        path = os.path.join(root, category, series, level, unit + ".txt")
        if os.path.isfile(path):
            return read_text_bank_file(path)
        return []
    return []
