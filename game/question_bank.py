import re


_LIST_MARKER_RE = re.compile(r"^(?:(?:\d+[\.)、]\s*)|(?:\d+\s+\S)|(?:[-*]\s+))")


def parse_text_bank_lines(lines):
    items = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if re.match(r"^\d+\s+\S", text):
            text = text.split(None, 1)[1].strip()
        else:
            text = re.sub(r"^(?:\d+[\.)、]\s*|[-*]\s+)", "", text, count=1).strip()
        if not text:
            continue
        items.append({"type": "text", "content": text, "hint": ""})
    return items


def read_text_bank_file(path):
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return parse_text_bank_lines(f.readlines())
        except UnicodeDecodeError:
            continue
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return parse_text_bank_lines(f.readlines())
