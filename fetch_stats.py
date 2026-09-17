import json
import re
from pathlib import Path

import scratchattach as sa

USER_NAME = "yoshihome"
DEFAULT_STATS = {
    "followers": 18370,
    "loves": 178442,
    "faves": 163214,
}
UNICODE_LETTER_MAP = {
    'ᴀ': 'a', 'ʙ': 'b', 'ᴄ': 'c', 'ᴅ': 'd', 'ᴇ': 'e', 'ꜰ': 'f', 'ɢ': 'g', 'ʜ': 'h', 'ɪ': 'i',
    'ᴋ': 'k', 'ʟ': 'l', 'ᴍ': 'm', 'ɴ': 'n', 'ᴏ': 'o', 'ᴘ': 'p', 'ʀ': 'r', 'ꜛ': 's', 'ꜜ': 's',
    'ꜝ': 's', 'ꜞ': 's', 'ꜟ': 'f', 'ꜱ': 's', 'ᴛ': 't', 'ᴜ': 'u', 'ᴠ': 'v', 'ᴡ': 'w', 'ʏ': 'y', 'ᴢ': 'z',
    'ᵃ': 'a', 'ᵇ': 'b', 'ᶜ': 'c', 'ᵈ': 'd', 'ᵉ': 'e', 'ᶠ': 'f', 'ᵍ': 'g', 'ʰ': 'h', 'ⁱ': 'i',
    'ʲ': 'j', 'ˡ': 'l', 'ᵐ': 'm', 'ⁿ': 'n', 'ᵒ': 'o', 'ᵖ': 'p', 'ʳ': 'r', 'ˢ': 's', 'ᵗ': 't',
    'ᵘ': 'u', 'ᵛ': 'v', 'ʷ': 'w', 'ˣ': 'x', 'ʸ': 'y', 'ᶻ': 'z'
}


def normalize_text(text):
    if not text:
        return ""
    text = ''.join(UNICODE_LETTER_MAP.get(ch, ch) for ch in text)
    return text.replace("\u202f", " ").replace("\xa0", " ").lower()


def extract_count_from_text(text, label_patterns):
    if not text:
        return None

    normalized = normalize_text(text)

    for label in label_patterns:
        label_index = normalized.find(label)
        if label_index == -1:
            continue
        tail = normalized[label_index + len(label):]
        match = re.search(r"[0-9][0-9\s,]*", tail)
        if match:
            number = match.group(0).replace(",", "").replace(" ", "")
            try:
                return int(number)
            except ValueError:
                continue
    return None


def fetch_stats():
    user = sa.User(username=USER_NAME)
    user.update()

    profile_text = getattr(user, "about_me", "") or ""
    followers = extract_count_from_text(
        profile_text,
        [r"followers\s*[:\-]?\s*([0-9][0-9\s,]*)"],
    )
    love_count = extract_count_from_text(
        profile_text,
        [
            r"loves\s*[:\-]?\s*([0-9][0-9\s,]*)",
            r"love\s*[:\-]?\s*([0-9][0-9\s,]*)",
        ],
    )
    fave_count = extract_count_from_text(
        profile_text,
        [
            r"faves\s*[:\-]?\s*([0-9][0-9\s,]*)",
            r"fave\s*[:\-]?\s*([0-9][0-9\s,]*)",
            r"favorites\s*[:\-]?\s*([0-9][0-9\s,]*)",
        ],
    )

    return {
        "followers": int(followers) if followers is not None else DEFAULT_STATS["followers"],
        "loves": int(love_count) if love_count is not None else DEFAULT_STATS["loves"],
        "faves": int(fave_count) if fave_count is not None else DEFAULT_STATS["faves"],
    }


def main():
    stats = fetch_stats()
    output_path = Path(__file__).resolve().parent / "stats.json"
    output_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
