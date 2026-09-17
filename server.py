import json
import re
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_IDS = [
    "964324085",
    "865951583",
    "794262893",
    "894071529",
    "808201366",
    "795320078",
    "798648038",
    "628733977",
]
UNICODE_LETTER_MAP = {
    'ᴀ': 'a', 'ʙ': 'b', 'ᴄ': 'c', 'ᴅ': 'd', 'ᴇ': 'e', 'ꜰ': 'f', 'ɢ': 'g', 'ʜ': 'h', 'ɪ': 'i',
    'ᴋ': 'k', 'ʟ': 'l', 'ᴍ': 'm', 'ɴ': 'n', 'ᴏ': 'o', 'ᴘ': 'p', 'ʀ': 'r', 'ꜛ': 's', 'ꜜ': 's',
    'ꜝ': 's', 'ꜞ': 's', 'ꜟ': 'f', 'ꜱ': 's', 'ᴛ': 't', 'ᴜ': 'u', 'ᴠ': 'v', 'ᴡ': 'w', 'ʏ': 'y', 'ᴢ': 'z',
    'ᵃ': 'a', 'ᵇ': 'b', 'ᶜ': 'c', 'ᵈ': 'd', 'ᵉ': 'e', 'ᶠ': 'f', 'ᵍ': 'g', 'ʰ': 'h', 'ⁱ': 'i',
    'ʲ': 'j', 'ˡ': 'l', 'ᵐ': 'm', 'ⁿ': 'n', 'ᵒ': 'o', 'ᵖ': 'p', 'ʳ': 'r', 'ˢ': 's', 'ᵗ': 't',
    'ᵘ': 'u', 'ᵛ': 'v', 'ʷ': 'w', 'ˣ': 'x', 'ʸ': 'y', 'ᶻ': 'z'
}


def normalize_unicode_text(text):
    if not text:
        return ""
    text = ''.join(UNICODE_LETTER_MAP.get(ch, ch) for ch in text)
    return text.replace("\u202f", " ").replace("\xa0", " ").lower()


def clean_number(raw_value):
    if raw_value is None:
        return None
    value = str(raw_value).replace(",", "").replace(" ", "")
    value = value.split("/")[0].split("k")[0]
    try:
        return int(value)
    except ValueError:
        return None


class SiteHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/user"):
            user_data = self.get_user_profile()
            payload = json.dumps(user_data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path.startswith("/project_views.json"):
            data = self.get_project_views()
            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        return super().do_GET()

    def get_user_profile(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        username = params.get("username", ["yoshihome"])[0].strip() or "yoshihome"

        try:
            url = f"https://api.scratch.mit.edu/users/{urllib.parse.quote(username)}"
            with urllib.request.urlopen(url, timeout=20) as response:
                user = json.load(response)
        except Exception:
            user = {}

        profile = user.get("profile") or {}
        bio = profile.get("bio") or "No bio available."

        followers = self.extract_profile_count(bio, "followers")
        loves = self.extract_profile_count(bio, "loves")
        faves = self.extract_profile_count(bio, "faves")

        return {
            "username": user.get("username", username),
            "profile": profile,
            "followers": followers,
            "loves": loves,
            "faves": faves,
            "bio": bio,
        }

    @staticmethod
    def extract_profile_count(bio_text, label):
        if not bio_text:
            return 0

        normalized = normalize_unicode_text(bio_text)
        aliases = {
            "followers": ["followers", "follower"],
            "loves": ["loves", "love"],
            "faves": ["faves", "favorites", "favorite", "favourites", "favourite"],
        }

        candidates = aliases.get(label, [label])
        for candidate in candidates:
            label_index = normalized.find(candidate)
            if label_index == -1:
                continue

            tail = normalized[label_index + len(candidate):]
            match = re.search(r"[0-9][0-9\s,]*", tail)
            if match:
                return clean_number(match.group(0)) or 0

        return 0

    def get_project_views(self):
        views_by_id = {}
        for project_id in PROJECT_IDS:
            try:
                url = f"https://api.scratch.mit.edu/projects/{project_id}"
                with urllib.request.urlopen(url, timeout=20) as response:
                    project = json.load(response)
                views_by_id[project_id] = int(project.get("stats", {}).get("views", 0) or 0)
            except Exception:
                views_by_id[project_id] = 0
        return views_by_id

    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if path in ("", "/"):
            path = "/index.html"
        return str(ROOT / path.lstrip("/"))


if __name__ == "__main__":
    port = 8000
    server = ThreadingHTTPServer(("0.0.0.0", port), SiteHandler)
    print(f"Serving http://localhost:{port}")
    server.serve_forever()
