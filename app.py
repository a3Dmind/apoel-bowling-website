#!/usr/bin/env python3
import cgi
import hashlib
import hmac
import html
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import time
from http import cookies
from pathlib import Path
from urllib.parse import parse_qs, quote_plus
from wsgiref.simple_server import make_server


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
ASSETS_DIR = BASE_DIR / "assets"
ASSET_IMAGE_UPLOADS_DIR = ASSETS_DIR / "images" / "uploads"
ASSET_FILES_DIR = ASSETS_DIR / "files"
DB_PATH = DATA_DIR / "site.db"
SECRET_PATH = DATA_DIR / "secret.key"
INITIAL_PASSWORD_PATH = DATA_DIR / "initial_admin_password.txt"
CONTENT_SEED_PATH = BASE_DIR / "content_seed.json"
SESSION_COOKIE = "apoel_admin_session"


DEFAULT_CONTENT = {
    "config": {
        "clubName": "APOEL Bowling",
        "clubTagline": "Team spirit. Strong lanes. Modern home base.",
        "phone": "+357 99 541254",
        "email": "apoelbowlingteam@gmail.com",
        "facebook": "https://www.facebook.com/",
        "venue": "The Bowling Boutique Bar & Grill",
        "venueAddress": "Nicosia, Cyprus",
        "season": "2025-2026",
    },
    "index": {
        "title": "APOEL Bowling",
        "hero": {
            "eyebrow": "APOEL Bowling Team",
            "heading": "Sporty. Fast. Ready for the next frame.",
            "text": "A modern mobile-friendly home for the team with a private admin area for quick updates.",
            "primaryLabel": "Δες Βαθμολογία",
            "primaryHref": "/totalstandings",
            "secondaryLabel": "Τελευταία Νέα",
            "secondaryHref": "/news",
            "image": "assets/images/bbc-apoel-2024-25.webp",
            "panelLabel": "Current season spotlight",
            "panelTitle": "BBC League 2025-2026",
            "panelText": "Fixtures, standings, team stories, sponsors, and gallery content in one clean place.",
        },
        "quickLinks": [
            {
                "title": "Εγγραφή Ομάδας",
                "text": "Άνοιξε άμεσα το αρχείο εγγραφής για τη νέα περίοδο.",
                "href": "https://drive.google.com/file/d/11p8frgXHRn9J2NuzLhlDhzevXpkrzNhQ/view?usp=drive_link",
            },
            {
                "title": "Εγγραφή Μέλους",
                "text": "Μπες στην ομάδα και στήριξε την προσπάθεια της χρονιάς.",
                "href": "https://drive.google.com/file/d/1Gpnb14Fo5K868RZPDOS6Mg_Eu5tffkFd/view?usp=sharing",
            },
            {
                "title": "Αγωνιστικοί Κανονισμοί",
                "text": "Όλοι οι βασικοί κανονισμοί σε ένα σημείο.",
                "href": "https://drive.google.com/file/d/1Mzt58uv6Q6Elzb6GrbWj_WB4CY53kgzB/view?usp=drive_link",
            },
        ],
        "venue": {
            "title": "Η Έδρα Μας",
            "subtitle": "The Bowling Boutique Bar & Grill",
            "text": "Εκεί που η προπόνηση, ο ανταγωνισμός και η ομάδα συναντιούνται κάθε εβδομάδα.",
            "image": "assets/images/bowling-ball-with-bowling-sml.jpg",
            "bullets": [
                "Αγωνιστική βάση για προπονήσεις και επίσημους αγώνες",
                "Φιλικό περιβάλλον για νέα μέλη και αθλητές",
                "Σημείο συνάντησης για events, βραβεύσεις και social nights",
            ],
        },
        "leaders": [
            {"label": "Ψηλότερος Μέσος Όρος", "value": "Ανδρέας Οικονομίδης", "score": "Μ.Ο. —"},
            {"label": "Ψηλότερη Σειρά", "value": "Θέος Αναστασίου", "score": "Σειρά —"},
            {"label": "Ψηλότερο Παιχνίδι", "value": "Θέος Αναστασίου", "score": "Παιχνίδι —"},
        ],
        "faq": [
            {
                "q": "Πώς μπορώ να γίνω μέλος;",
                "a": "Συμπλήρωσε την αίτηση εγγραφής μέλους και στείλε τη στο apoelbowlingteam@gmail.com.",
            },
            {
                "q": "Υπάρχουν ηλικιακοί περιορισμοί;",
                "a": "Το bowling είναι προσβάσιμο σε πολλές ηλικίες. Για αγωνιστική συμμετοχή ισχύουν οι κανονισμοί της διοργάνωσης.",
            },
            {
                "q": "Μπορώ να φέρω δικό μου εξοπλισμό;",
                "a": "Ναι. Αν ήδη έχεις μπάλα, παπούτσια ή άλλο προσωπικό εξοπλισμό, μπορείς να τα χρησιμοποιήσεις.",
            },
        ],
    },
    "news": {
        "title": "Νέα",
        "hero": {
            "eyebrow": "Team updates",
            "heading": "Νέα από τη σεζόν και την ομάδα.",
            "text": "Ανακοινώσεις, εκδηλώσεις, βραβεύσεις και ιστορίες από το APOEL Bowling.",
        },
        "items": [
            {
                "title": "ABCD Singles Open Tour 2025-2026",
                "date": "05 Σεπτεμβρίου 2025",
                "category": "Tournament",
                "image": "assets/images/bbc-apoel-2024-27.jpg",
                "text": "Η νέα σεζόν ξεκινά με ένταση, ρυθμό και υψηλές προσδοκίες για την ομάδα.",
            },
            {
                "title": "Κύπελλα 24-25",
                "date": "Ιούλιος 2025",
                "category": "Awards",
                "image": "assets/images/bbc-apoel-2024-25.webp",
                "text": "Ανασκόπηση των διακρίσεων της περασμένης χρονιάς και των σημαντικότερων στιγμών.",
            },
        ],
    },
    "i_omada": {
        "title": "Η Ομάδα",
        "hero": {
            "eyebrow": "Meet the squad",
            "heading": "Γνώρισε την ομάδα.",
            "text": "Παίκτες, επιτυχίες και η φιλοσοφία που κρατά το APOEL Bowling ενωμένο σε κάθε αγωνιστική.",
        },
        "roster": [
            {
                "name": "Ανδρέας Οικονομίδης",
                "role": "Captain",
                "bio": "Σταθερότητα, εμπειρία και έντονη αγωνιστική παρουσία.",
                "image": "assets/images/bbc-apoel-2024-25.webp",
            },
            {
                "name": "Θέος Αναστασίου",
                "role": "Power scorer",
                "bio": "Γνωστός για τα δυνατά παιχνίδια και τις μεγάλες σειρές.",
                "image": "assets/images/bbc-apoel-2024-27.jpg",
            },
        ],
        "achievements": [
            "Συνεχής παρουσία σε διοργανώσεις του BBC League",
            "Βραβεύσεις αθλητών και ομαδικές διακρίσεις",
            "Ενεργή κοινότητα παικτών, φίλων και υποστηρικτών",
        ],
    },
    "agonistiko_programma": {
        "title": "Αγωνιστικό Πρόγραμμα",
        "hero": {
            "eyebrow": "Season calendar",
            "heading": "Το ημερολόγιο μας.",
            "text": "Οι αγωνιστικές ημερομηνίες ενημερώνονται αυτόματα από το Google Calendar της ομάδας.",
        },
        "calendarUrl": "https://calendar.google.com/calendar/embed?height=600&wkst=1&ctz=Asia%2FNicosia&showPrint=0&mode=AGENDA&src=YXBvZWxib3dsaW5ndGVhbUBnbWFpbC5jb20&color=%23039be5",
        "schedule": [
            {
                "day": "10",
                "month": "Oct",
                "title": "Week 1",
                "details": "Έναρξη πρωταθλήματος BBC League",
                "link": "https://drive.google.com/file/d/1SdNYAsd5wogMboFTxbv1rx7w-mIPcHlH/view?usp=drive_link",
            },
            {
                "day": "17",
                "month": "Oct",
                "title": "Week 2",
                "details": "Δεύτερη αγωνιστική και ανανέωση standings",
                "link": "https://drive.google.com/file/d/12P5k3kF6l2KfctUR8UrV-BK3idwhD-yx/view?usp=drive_link",
            },
        ],
    },
    "totalstandings": {
        "title": "Συνολική Βαθμολογία",
        "hero": {
            "eyebrow": "Live table",
            "heading": "Βαθμολογία με ιδιωτικό admin.",
            "text": "Μόνο εσύ και όποιοι έχουν admin access μπορούν να ενημερώνουν τη βαθμολογία.",
        },
        "season": "2025-2026",
        "updatedAt": "2026-04-17",
        "rows": [
            {"team": "APOEL", "played": "12", "wins": "9", "losses": "3", "pins": "11234", "points": "27"},
            {"team": "Hawks", "played": "12", "wins": "8", "losses": "4", "pins": "11088", "points": "24"},
            {"team": "Kingpins", "played": "12", "wins": "7", "losses": "5", "pins": "10815", "points": "21"},
        ],
    },
    "league_archives": {
        "items": [],
    },
    "gallery": {
        "title": "Γκαλερί",
        "hero": {
            "eyebrow": "Gallery",
            "heading": "Στιγμές από τη σεζόν.",
            "text": "Επιλεγμένα στιγμιότυπα από αγώνες, events και βραβεύσεις.",
        },
        "items": [
            {
                "title": "Match Night",
                "image": "assets/images/bbc-apoel-2024-25.webp",
                "text": "Ομαδικό στιγμιότυπο από τη γραμμή εκκίνησης.",
            },
            {
                "title": "Awards Evening",
                "image": "assets/images/bbc-apoel-2024-27.jpg",
                "text": "Βραβεύσεις και γιορτή για τη δουλειά της χρονιάς.",
            },
        ],
    },
    "bbc_teams": {
        "title": "BBC Teams",
        "hero": {
            "eyebrow": "League overview",
            "heading": "Η οικογένεια του BBC League.",
            "text": "Ομάδες, events και σημεία αναφοράς από το περιβάλλον της διοργάνωσης.",
        },
        "groups": [
            {"title": "Ομάδες 2024-2025", "text": "Συνοπτική ενότητα για τις ομάδες της προηγούμενης σεζόν."},
            {"title": "Χριστουγεννιάτικο Τουρνουά 2024", "text": "Μια ξεχωριστή διοργάνωση με εορταστικό χαρακτήρα και έντονο ανταγωνισμό."},
        ],
    },
    "xorigi": {
        "title": "Χορηγοί",
        "hero": {
            "eyebrow": "Supporters",
            "heading": "Οι χορηγοί μας 2025-2026.",
            "text": "Οι συνεργάτες που στηρίζουν την προσπάθεια της ομάδας σε κάθε frame.",
        },
        "sponsors": [
            {"name": "Romanos", "image": "assets/images/romanos-logo-full-1.jpg", "type": "Hospitality partner"},
            {"name": "ARGUS", "image": "assets/images/argus-logo-white.jpg", "type": "Support partner"},
        ],
    },
    "coming_soon": {
        "title": "Σύντομα Κοντά Σας",
        "hero": {
            "eyebrow": "New section",
            "heading": "Περισσότερο περιεχόμενο έρχεται.",
            "text": "Χρησιμοποίησε αυτή τη σελίδα για νέες υποενότητες, αρχεία ή μελλοντικά αποτελέσματα.",
        },
    },
    "tools": {
        "title": "Tools",
        "hero": {
            "eyebrow": "Team toolkit",
            "heading": "Bowling tools for line building.",
            "text": "Use the lane play calculator directly in the site to project stance, slide, laydown, focal point, launch angle, and simple move progressions.",
        },
    },
}

BBC_LEAGUE_LINKS = [
    {"href": "https://drive.google.com/file/d/11p8frgXHRn9J2NuzLhlDhzevXpkrzNhQ/view?usp=drive_link", "label": "Εγγραφή Ομάδας", "text": "Άνοιξε τη φόρμα εγγραφής ομάδας για τη σεζόν."},
    {"href": "https://drive.google.com/file/d/1Gpnb14Fo5K868RZPDOS6Mg_Eu5tffkFd/view?usp=sharing", "label": "Εγγραφή Μέλους", "text": "Η αίτηση για νέα μέλη και αθλητές."},
    {"href": "https://drive.google.com/file/d/1Mzt58uv6Q6Elzb6GrbWj_WB4CY53kgzB/view?usp=drive_link", "label": "Αγωνιστικοί Κανονισμοί", "text": "Οι βασικοί κανονισμοί της διοργάνωσης."},
    {"href": "https://drive.google.com/file/d/1Mzt58uv6Q6Elzb6GrbWj_WB4CY53kgzB/view?usp=drive_link", "label": "Προκήρυξη Πρωταθλήματος", "text": "Πληροφορίες και όροι για το πρωτάθλημα."},
    {"href": "https://drive.google.com/file/d/19EG_TI776d3LavB3qLh81e9ZBdtwXyLN/view?usp=sharing", "label": "Προκήρυξη Κυπέλλου", "text": "Πληροφορίες και όροι για το κύπελλο."},
    {"href": "https://drive.google.com/file/d/1drG_b4aXb68wkl11WXhDH71WC7NIm_cN/view?usp=drive_link", "label": "Αγωνιστικό Πρόγραμμα", "text": "Το επίσημο αγωνιστικό πρόγραμμα του BBC League."},
    {"href": "https://drive.google.com/file/d/1CyTKxNueNT5Q0CvqctZV18Gh_qCnIf54/view?usp=drive_link", "label": "Συνολική Βαθμολογία 2024-2025", "text": "Αρχείο βαθμολογίας της προηγούμενης σεζόν."},
    {"href": "/coming_soon", "label": "Αποτελέσματα Αγωνιστικών", "text": "Χώρος για αποτελέσματα ανά αγωνιστική."},
    {"href": "/coming_soon", "label": "Ατομικές Επιδόσεις", "text": "Χώρος για ατομικά στατιστικά και επιδόσεις."},
    {"href": "https://docs.google.com/spreadsheets/d/1eYr8eKcF0DwDGEQAtr0ElCtv3mccPujI/edit?usp=drive_link&ouid=114440334960870831379&rtpof=true&sd=true", "label": "Oil Pattern Πρωταθλήματος", "text": "Το oil pattern για το πρωτάθλημα."},
    {"href": "https://docs.google.com/spreadsheets/d/1nppjemvfsVvy7pHrNj3QJp7QstrV1mNN/edit?usp=sharing&ouid=114440334960870831379&rtpof=true&sd=true", "label": "Oil Pattern Κυπέλλου", "text": "Το oil pattern για το κύπελλο."},
    {"href": "/bbc_teams", "label": "Οι Ομάδες", "text": "Οι ομάδες και η κοινότητα του BBC League."},
    {"href": "/bbc_teams", "label": "Χριστουγεννιάτικος Διαγωνισμός", "text": "Πληροφορίες για τον εορταστικό διαγωνισμό."},
    {"href": "/bbc_teams", "label": "Τελετή Βραβεύσεων", "text": "Στιγμές και πληροφορίες από τις βραβεύσεις."},
    {"href": "https://drive.google.com/file/d/1l2bFxPoZ_LPVa_VLZ-2KOeTSuu6UaMns/view?usp=drive_link", "label": "Βραβευθέντες 2024-2025", "text": "Το αρχείο των βραβευθέντων της σεζόν 2024-2025."},
]

NAV_ITEMS = [
    {"href": "/", "label": "Αρχική"},
    {"href": "/news", "label": "Νέα"},
    {"href": "/i_omada", "label": "Η Ομάδα"},
    {"href": "/bbc_teams", "label": "BBC League"},
    {"href": "https://cyprusbowlingfederation.com/el/%CE%B3%CE%B9%CE%B1/", "label": "Κ.Ο.ΜΠΟ"},
    {"href": "/gallery", "label": "Γκαλερί"},
    {"href": "/xorigi", "label": "Χορηγοί"},
    {"href": "/tools", "label": "Εργαλεία"},
]


def ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)
    ASSET_IMAGE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_FILES_DIR.mkdir(parents=True, exist_ok=True)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_secret():
    if not SECRET_PATH.exists():
        SECRET_PATH.write_text(secrets.token_hex(32))
    return SECRET_PATH.read_text().strip()


def load_seed_content():
    if CONTENT_SEED_PATH.exists():
        return json.loads(CONTENT_SEED_PATH.read_text())
    return DEFAULT_CONTENT


SECRET = None


def password_hash(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200000).hex()
    return f"{salt}${digest}"


def password_matches(password, stored):
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200000).hex()
    return hmac.compare_digest(check, digest)


def init_db():
    ensure_dirs()
    global SECRET
    SECRET = load_secret()
    with db() as conn:
        conn.execute("create table if not exists content (key text primary key, value text not null)")
        conn.execute(
            """
            create table if not exists admin_users (
              id integer primary key autoincrement,
              username text unique not null,
              password_hash text not null,
              created_at text not null
            )
            """
        )
        for key, value in load_seed_content().items():
            conn.execute(
                "insert or ignore into content (key, value) values (?, ?)",
                (key, json.dumps(value, ensure_ascii=False)),
            )
        count = conn.execute("select count(*) from admin_users").fetchone()[0]
        if count == 0:
            username = os.environ.get("ADMIN_USERNAME", "admin")
            env_password = os.environ.get("ADMIN_PASSWORD")
            temp_password = env_password or secrets.token_urlsafe(10)
            conn.execute(
                "insert into admin_users (username, password_hash, created_at) values (?, ?, ?)",
                (username, password_hash(temp_password), time.strftime("%Y-%m-%d %H:%M:%S")),
            )
            password_line = "password: from ADMIN_PASSWORD environment variable\n" if env_password else f"password: {temp_password}\n"
            INITIAL_PASSWORD_PATH.write_text(
                "APOEL Bowling Admin Login\n"
                f"username: {username}\n"
                f"{password_line}\n"
                "Change this password immediately from /admin/account after logging in.\n"
            )


def get_content(key):
    with db() as conn:
        row = conn.execute("select value from content where key = ?", (key,)).fetchone()
    return json.loads(row["value"]) if row else {}


def set_content(key, payload):
    with db() as conn:
        conn.execute(
            "insert into content (key, value) values (?, ?) on conflict(key) do update set value = excluded.value",
            (key, json.dumps(payload, ensure_ascii=False)),
        )


def e(value):
    return html.escape(str(value or ""))


def as_url(value):
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://", "//")):
        return value
    return "/" + value.lstrip("/")


def image_html(src, alt, cls=""):
    url = as_url(src)
    if not url:
        return ""
    return f'<img src="{e(url)}" alt="{e(alt)}" class="{e(cls)}">'


def parse_cookies(environ):
    raw = environ.get("HTTP_COOKIE", "")
    jar = cookies.SimpleCookie()
    jar.load(raw)
    return {key: morsel.value for key, morsel in jar.items()}


def make_signed_value(username, expiry):
    payload = f"{username}|{expiry}"
    sig = hmac.new(SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}|{sig}"


def read_session(environ):
    token = parse_cookies(environ).get(SESSION_COOKIE, "")
    try:
        username, expiry, sig = token.split("|", 2)
    except ValueError:
        return None
    payload = f"{username}|{expiry}"
    expected = hmac.new(SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    if int(expiry) < int(time.time()):
        return None
    return username


def redirect(location, headers=None):
    headers = headers or []
    headers.append(("Location", location))
    return "302 Found", headers, b""


def response_html(body, status="200 OK", headers=None):
    headers = headers or []
    headers.append(("Content-Type", "text/html; charset=utf-8"))
    return status, headers, body.encode("utf-8")


def response_bytes(body, content_type="application/octet-stream", status="200 OK", headers=None):
    headers = headers or []
    headers.append(("Content-Type", content_type))
    return status, headers, body


def serve_file(path):
    if not path.exists() or not path.is_file():
        return response_html("<h1>Not found</h1>", "404 Not Found")
    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return response_bytes(path.read_bytes(), content_type)


def parse_request(environ):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    if method == "GET":
        query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
        return {k: v[-1] for k, v in query.items()}, {}

    content_type = environ.get("CONTENT_TYPE", "")
    if content_type.startswith("multipart/form-data"):
        fs = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ, keep_blank_values=True)
        form, files = {}, {}
        if fs.list:
            for item in fs.list:
                if item.filename:
                    files[item.name] = item
                else:
                    form[item.name] = item.value
        return form, files

    length = int(environ.get("CONTENT_LENGTH") or 0)
    raw = environ["wsgi.input"].read(length).decode("utf-8")
    form = parse_qs(raw, keep_blank_values=True)
    return {k: v[-1] for k, v in form.items()}, {}


def sanitize_filename(name):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name)
    return cleaned.strip("-") or "upload"


def save_upload(item):
    filename = sanitize_filename(item.filename or "upload")
    target = ASSET_IMAGE_UPLOADS_DIR / filename
    if target.exists():
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        target = ASSET_IMAGE_UPLOADS_DIR / f"{stem}-{secrets.token_hex(3)}{suffix}"
    data = item.file.read()
    target.write_bytes(data)
    return f"assets/images/uploads/{target.name}"


def save_file_upload(item):
    filename = sanitize_filename(item.filename or "upload")
    target = ASSET_FILES_DIR / filename
    if target.exists():
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        target = ASSET_FILES_DIR / f"{stem}-{secrets.token_hex(3)}{suffix}"
    target.write_bytes(item.file.read())
    return target


def parse_repeater(form, prefix, fields):
    rows = {}
    pattern = re.compile(rf"^{re.escape(prefix)}__(\d+)__([A-Za-z0-9_]+)$")
    for key, value in form.items():
        match = pattern.match(key)
        if not match:
            continue
        idx, field = int(match.group(1)), match.group(2)
        if field not in fields:
            continue
        rows.setdefault(idx, {})[field] = value.strip()
    results = []
    for idx in sorted(rows):
        row = rows[idx]
        if any(row.get(field, "").strip() for field in fields):
            results.append({field: row.get(field, "").strip() for field in fields})
    return results


def apply_repeater_uploads(items, files, prefix, image_fields):
    pattern = re.compile(rf"^{re.escape(prefix)}__(\d+)__([A-Za-z0-9_]+)_upload$")
    for key, item in files.items():
        match = pattern.match(key)
        if not match:
            continue
        idx, field = int(match.group(1)), match.group(2)
        if field not in image_fields or idx >= len(items):
            continue
        if item.filename:
            items[idx][field] = save_upload(item)
    return items


def apply_single_upload(current, files, field_name):
    upload_key = f"{field_name}_upload"
    if upload_key in files and files[upload_key].filename:
        return save_upload(files[upload_key])
    return current


def hero_section(hero, page_key):
    eyebrow = e(hero.get("eyebrow"))
    heading = e(hero.get("heading"))
    text = e(hero.get("text"))
    image = hero.get("image", "")
    primary = ""
    if hero.get("primaryLabel"):
        primary = (
            f'<div class="hero-actions">'
            f'<a class="button button-primary" href="{e(hero.get("primaryHref") or "#")}">{e(hero.get("primaryLabel"))}</a>'
            f'<a class="button button-secondary" href="{e(hero.get("secondaryHref") or "#")}">{e(hero.get("secondaryLabel"))}</a>'
            f"</div>"
        )
    aside = ""
    if image:
        aside = (
            '<aside class="hero-panel">'
            f'<span class="panel-badge">{e(hero.get("panelLabel") or "APOEL Bowling")}</span>'
            f'{image_html(image, hero.get("panelTitle") or hero.get("heading"))}'
            "<div>"
            f'<strong>{e(hero.get("panelTitle") or hero.get("heading"))}</strong>'
            f'<p class="muted">{e(hero.get("panelText") or "")}</p>'
            "</div></aside>"
        )
    section_class = "hero" if page_key == "index" else "page-hero"
    grid_class = "hero-grid" if page_key == "index" else "page-hero-grid"
    return (
        f'<section class="{section_class}"><div class="{grid_class}"><div class="hero-copy">'
        f'<span class="eyebrow">{eyebrow}</span><h1>{heading}</h1><p>{text}</p>{primary}</div>{aside}</div></section>'
    )


def section_head(title, subtitle="", copy=""):
    extra = f'<p class="section-copy">{e(copy)}</p>' if copy else ""
    return (
        '<div class="section-head"><div>'
        f'<p class="section-subtitle">{e(subtitle)}</p>'
        f'<h2 class="section-title">{e(title)}</h2>'
        f"</div>{extra}</div>"
    )


def render_site_layout(title, page_key, inner, extra_head="", extra_scripts=""):
    config = get_content("config")
    css_version = int((ASSETS_DIR / "css" / "styles.css").stat().st_mtime)
    nav_parts = []
    for item in NAV_ITEMS:
        href = item["href"]
        label = item["label"]
        children = item.get("children", [])
        is_current = href == page_key or any(child.get("href") == page_key for child in children)
        current_attr = ' aria-current="page"' if is_current else ""
        if children:
            child_links = "".join(
                f'<a class="dropdown-link" href="{e(child["href"])}">{e(child["label"])}</a>'
                for child in children
            )
            nav_parts.append(
                f'<div class="nav-item has-dropdown">'
                f'<button class="nav-link nav-parent" type="button"{current_attr}>{e(label)} <span class="dropdown-caret">▾</span></button>'
                f'<div class="nav-dropdown">{child_links}</div>'
                f'</div>'
            )
        else:
            nav_parts.append(f'<a class="nav-link" href="{e(href)}"{current_attr}>{e(label)}</a>')
    nav = "".join(nav_parts)
    return f"""<!doctype html>
<html lang="el">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{e(title)} | {e(config.get("clubName"))}</title>
    <meta name="description" content="{e(config.get("clubTagline"))}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=JetBrains+Mono:wght@500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/styles.css?v={css_version}">
    {extra_head}
  </head>
  <body>
    <div class="site-shell">
      <header class="site-header">
        <div class="container header-inner">
          <a class="brand" href="/">
            <img class="brand-logo" src="/assets/images/apoel-bowling-logo.svg" alt="APOEL Bowling logo">
            <span class="brand-copy">
              <strong>{e(config.get("clubName"))}</strong>
              <span>{e(config.get("season"))}</span>
            </span>
          </a>
          <button class="nav-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false">Menu</button>
          <nav class="main-nav" aria-label="Primary navigation">{nav}</nav>
        </div>
      </header>
      <main class="page-main">{inner}</main>
      <footer class="site-footer">
        <div class="container">
          <div class="footer-card">
            <div class="footer-grid">
              <div>
                <p class="footer-brand">{e(config.get("clubName"))}</p>
                <p class="footer-note">{e(config.get("clubTagline"))}</p>
              </div>
              <div>
                <strong>Contact</strong>
                <div class="footer-list">
                  <a href="tel:{e(config.get("phone", "").replace(" ", ""))}">{e(config.get("phone"))}</a>
                  <a href="mailto:{e(config.get("email"))}">{e(config.get("email"))}</a>
                  <span>{e(config.get("venue"))}</span>
                </div>
              </div>
              <div>
                <strong>Admin</strong>
                <div class="footer-list">
                  <a href="/admin">Dashboard</a>
                  <a href="/admin/account">Account</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
    <script>
      document.addEventListener("click", function (event) {{
        if (!event.target.matches(".nav-toggle")) return;
        var header = event.target.closest(".site-header");
        var isOpen = header.classList.toggle("is-open");
        event.target.setAttribute("aria-expanded", isOpen ? "true" : "false");
      }});
      document.addEventListener("click", function (event) {{
        var parent = event.target.closest(".nav-parent");
        if (!parent) return;
        var item = parent.closest(".has-dropdown");
        if (!item) return;
        item.classList.toggle("is-expanded");
      }});
    </script>
    {extra_scripts}
  </body>
</html>"""


def render_home():
    data = get_content("index")
    quick_links = "".join(
        f'<a class="tile" href="{e(item.get("href") or "#")}"><h3>{e(item.get("title"))}</h3><p>{e(item.get("text"))}</p></a>'
        for item in data.get("quickLinks", [])
    )
    venue = data.get("venue", {})
    venue_bullets = "".join(f"<li><strong>{e(item)}</strong></li>" for item in venue.get("bullets", []))
    leader_cards = []
    for item in data.get("leaders", []):
        score = f'<em>{e(item.get("score"))}</em>' if item.get("score") else ""
        leader_cards.append(
            f'<div class="metric-card"><span>{e(item.get("label"))}</span><strong>{e(item.get("value"))}</strong>{score}</div>'
        )
    leaders = "".join(leader_cards)
    faq = "".join(
        f'<article class="faq-item"><strong>{e(item.get("q"))}</strong><p class="muted">{e(item.get("a"))}</p></article>'
        for item in data.get("faq", [])
    )
    body = (
        f'<div class="container">{home_hero_section(data.get("hero", {}))}</div>'
        '<section class="section"><div class="container">'
        f'{section_head("Quick Access", "BBC League", "Keep your most important team links one tap away.")}'
        f'<div class="grid grid-3">{quick_links}</div></div></section>'
        '<section class="section"><div class="container split">'
        '<article class="split-panel">'
        f'{image_html(venue.get("image"), venue.get("title"))}'
        f'<p class="section-subtitle">Home lane</p><h2 class="section-title">{e(venue.get("title"))}</h2>'
        f'<p>{e(venue.get("text"))}</p><ul class="list">{venue_bullets}</ul></article>'
        '<div class="grid">'
        f'<div class="metric-card"><span>Venue</span><strong>{e(venue.get("subtitle"))}</strong></div>{leaders}'
        '</div></div></section>'
        '<section class="section"><div class="container">'
        f'{section_head("Συχνές Ερωτήσεις", "FAQ", "Keep the answers visible for players and new members.")}'
        f'<div class="faq-list">{faq}</div></div></section>'
    )
    return render_site_layout(data.get("title", "Home"), "/", body)


def home_hero_section(hero):
    return (
        '<section class="hero home-identity-hero">'
        '<div class="home-identity-inner">'
        '<img class="home-identity-logo" src="/assets/images/apoel-bowling-logo.svg" alt="APOEL Bowling logo">'
        f'<h1>{e(hero.get("heading") or "ΑΠΟΕΛ ΜΠΟΟΥΛΙΝΓΚ")}</h1>'
        f'<p class="home-identity-text">{e(hero.get("text") or "")}</p>'
        '<div class="hero-actions">'
        f'<a class="button button-primary" href="{e(hero.get("primaryHref") or "/totalstandings")}">{e(hero.get("primaryLabel") or "Δες Βαθμολογία")}</a>'
        f'<a class="button button-secondary" href="{e(hero.get("secondaryHref") or "/news")}">{e(hero.get("secondaryLabel") or "Τελευταία Νέα")}</a>'
        '</div>'
        '</div>'
        '</section>'
    )


def render_news():
    data = get_content("news")
    cards = "".join(
        '<article class="news-card">'
        f'{image_html(item.get("image"), item.get("title"))}'
        f'<div class="news-meta"><span class="meta-pill">{e(item.get("date"))}</span><span class="meta-pill">{e(item.get("category"))}</span></div>'
        f'<h3>{e(item.get("title"))}</h3><p class="muted">{e(item.get("text"))}</p></article>'
        for item in data.get("items", [])
    )
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "news")}</div>'
        '<section class="section"><div class="container">'
        f'{section_head("Latest Updates", "Newsroom", "Everything here is editable from the private admin area.")}'
        f'<div class="news-list">{cards}</div></div></section>'
    )
    return render_site_layout(data.get("title", "News"), "/news", body)


def render_team():
    data = get_content("i_omada")
    schedule_data = get_content("agonistiko_programma")
    calendar_url = schedule_data.get("calendarUrl") or DEFAULT_CONTENT["agonistiko_programma"]["calendarUrl"]
    roster = "".join(
        '<article class="roster-card">'
        f'{image_html(item.get("image"), item.get("name"))}'
        f'<span class="roster-role">{e(item.get("role"))}</span><h3>{e(item.get("name"))}</h3><p class="muted">{e(item.get("bio"))}</p></article>'
        for item in data.get("roster", [])
    )
    achievements = "".join(f"<li><strong>{e(item)}</strong></li>" for item in data.get("achievements", []))
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "i_omada")}</div>'
        '<section class="section"><div class="container">'
        f'{section_head("Roster", "Team core", "Player names, roles, bios and photos are editable.")}'
        f'<div class="roster-grid">{roster}</div></div></section>'
        '<section class="section"><div class="container">'
        f'{section_head("Ημερολόγιο Επιτυχιών", "Highlights")}'
        f'<ul class="list">{achievements}</ul></div></section>'
        '<section class="section"><div class="container">'
        f'<div id="team-calendar"></div>{section_head("Το Ημερολόγιο Μας", "Team calendar", "Το ημερολόγιο της ομάδας εμφανίζεται εδώ όπως και στο αρχικό website.")}'
        '<div class="calendar-shell">'
        f'<iframe class="calendar-frame" src="{e(calendar_url)}" title="APOEL Bowling Google Calendar" frameborder="0" scrolling="no"></iframe>'
        '</div></div></section>'
    )
    return render_site_layout(data.get("title", "Η Ομάδα"), "/i_omada", body)


def render_schedule():
    data = get_content("agonistiko_programma")
    calendar_url = data.get("calendarUrl") or DEFAULT_CONTENT["agonistiko_programma"]["calendarUrl"]
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "agonistiko_programma")}</div>'
        '<section class="section"><div class="container">'
        f'{section_head("Το Ημερολόγιο Μας", "Google Calendar", "Events are pulled automatically from the team calendar, just like the original site.")}'
        '<div class="calendar-shell">'
        f'<iframe class="calendar-frame" src="{e(calendar_url)}" title="APOEL Bowling Google Calendar" frameborder="0" scrolling="no"></iframe>'
        '</div>'
        '<p class="editor-note">If the calendar does not appear, make sure the Google Calendar is public or shared correctly.</p>'
        '</div></section>'
    )
    return render_site_layout(data.get("title", "Αγωνιστικό Πρόγραμμα"), "/agonistiko_programma", body)


STANDINGS_FIELDS = [
    ("place", "#"),
    ("teamNumber", "Team #"),
    ("team", "Team"),
    ("percentWon", "% Won"),
    ("pointsWon", "Points Won"),
    ("pointsLost", "Points Lost"),
    ("unearnedPoints", "UnEarned"),
    ("ytdPercentWon", "YTD %"),
    ("ytdWon", "YTD Won"),
    ("ytdLost", "YTD Lost"),
    ("gamesWon", "Games Won"),
    ("scratchPins", "Scratch Pins"),
    ("totalPins", "Total Pins"),
]

STANDINGS_DISPLAY_FIELDS = [
    ("place", "#"),
    ("team", "Team"),
    ("pointsWon", "Points"),
    ("totalPins", "Total Pins"),
]


PLAYER_DISPLAY_NAMES = {
    "ANDREAS ECONOMIDES": "Ανδρέας Οικονομίδης",
    "THEOS ANASTASIOU": "Θέος Αναστασίου",
    "MICHALIS ZAMBARTAS": "Μιχάλης Ζαμπάρτας",
    "YIOLA PASTOU": "Γιώλα Παστού",
    "ANDREAS HADJIEVANGELOU": "Ανδρέας Χατζηευαγγέλου",
    "GEORGE ANASTASIOU": "Γιώργος Αναστασίου",
}


def numberish(value, default=0):
    text = str(value or "").replace("½", ".5").strip()
    try:
        return float(text)
    except ValueError:
        return default


def team_initials(name):
    words = [word for word in re.split(r"\s+", str(name or "").strip()) if word]
    if not words:
        return "?"
    return "".join(word[0] for word in words[:2]).upper()


def name_key(name):
    return re.sub(r"[^A-Z]+", " ", str(name or "").upper()).strip()


def slugify(value):
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or f"season-{int(time.time())}"


def pdf_text(path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF import needs the pypdf package installed.") from exc
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_team_roster_names(text, team_name="APOEL"):
    players = []
    current_team = ""
    team_header_re = re.compile(r"^\d+\s+-\s+(.+)$")
    player_re = re.compile(r"^\d+\s+([A-Z][A-Z ]+?)\s+\d+\s+\d+\s+\d+\s+")
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        team_match = team_header_re.match(line)
        if team_match:
            current_team = team_match.group(1).strip()
            continue
        if current_team != team_name:
            continue
        player_match = player_re.match(line)
        if player_match:
            players.append(player_match.group(1).strip())
    return players


def parse_total_standings_pdf(path):
    text = pdf_text(path)
    week_match = re.search(r"Week\s+(\d+)\s+of\s+(\d+)", text)
    date_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+\d{1,2}:\d{2}\s*[ap]m", text, re.I)
    week = week_match.group(1) if week_match else ""
    total_weeks = week_match.group(2) if week_match else ""
    updated_at = ""
    if date_match:
        month, day, year = date_match.groups()
        updated_at = f"{year}-{int(month):02d}-{int(day):02d}"

    rows = []
    in_standings = False
    row_re = re.compile(
        r"^(\d+)\s+(\d+)\s+(.+?)\s+([0-9.]+)\s+([0-9½]+)\s+([0-9½]+)\s+(?:(\d+)\s+)?([0-9.]+)\s+([0-9½]+)\s+([0-9½]+)\s+([0-9½]+)\s+(\d+)\s+(\d+)$"
    )
    bye_re = re.compile(r"^(\d+)\s+(\d+)\s+(BYE)\s+0\s+0\s+0\s+0\s+0\s+0$")
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if line == "Team Standings":
            in_standings = True
            continue
        if in_standings and line.startswith("Review of Last Week"):
            break
        if not in_standings:
            continue
        match = row_re.match(line)
        if match:
            (
                place,
                team_number,
                team,
                percent_won,
                points_won,
                points_lost,
                unearned_points,
                ytd_percent,
                ytd_won,
                ytd_lost,
                games_won,
                scratch_pins,
                total_pins,
            ) = match.groups()
            rows.append(
                {
                    "place": place,
                    "teamNumber": team_number,
                    "team": team,
                    "percentWon": percent_won,
                    "pointsWon": points_won,
                    "pointsLost": points_lost,
                    "unearnedPoints": unearned_points or "",
                    "ytdPercentWon": ytd_percent,
                    "ytdWon": ytd_won,
                    "ytdLost": ytd_lost,
                    "gamesWon": games_won,
                    "scratchPins": scratch_pins,
                    "totalPins": total_pins,
                }
            )
            continue
        match = bye_re.match(line)
        if match:
            place, team_number, team = match.groups()
            rows.append(
                {
                    "place": place,
                    "teamNumber": team_number,
                    "team": team,
                    "percentWon": "0",
                    "pointsWon": "0",
                    "pointsLost": "0",
                    "unearnedPoints": "",
                    "ytdPercentWon": "0",
                    "ytdWon": "0",
                    "ytdLost": "0",
                    "gamesWon": "0",
                    "scratchPins": "0",
                    "totalPins": "0",
                }
            )
    if not rows:
        raise ValueError("No team standings rows were found in the PDF.")
    apoel_players = extract_team_roster_names(text, "APOEL")
    season = "2025-2026"
    if week and total_weeks:
        season = f"{season} · Week {week} of {total_weeks}"
    return {
        "title": "Συνολική Βαθμολογία",
        "hero": {
            "eyebrow": "BBC 25-26",
            "heading": f"Βαθμολογία Week {week}" if week else "Βαθμολογία",
            "text": f"Στοιχεία από το {Path(path).name}.",
        },
        "season": season,
        "updatedAt": updated_at or time.strftime("%Y-%m-%d"),
        "source": Path(path).name,
        "apoelPlayers": apoel_players,
        "rows": rows,
    }


def parse_high_average_pdf(path):
    text = pdf_text(path)
    bowlers = []
    row_re = re.compile(
        r"^([A-Z][A-Z ]+?)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+%\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\b"
    )
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        match = row_re.match(line)
        if not match:
            continue
        name, won, lost, percent, pins, games, avg, high_game, high_series = match.groups()
        bowlers.append(
            {
                "name": name.strip(),
                "won": won,
                "lost": lost,
                "percent": percent,
                "pins": pins,
                "games": games,
                "avg": int(avg),
                "highGame": int(high_game),
                "highSeries": int(high_series),
            }
        )
    if not bowlers:
        raise ValueError("No high-average rows were found in the PDF.")
    best_avg = max(bowlers, key=lambda row: row["avg"])
    best_game = max(bowlers, key=lambda row: row["highGame"])
    best_series = max(bowlers, key=lambda row: row["highSeries"])
    return {
        "bestAverage": best_avg,
        "bestGame": best_game,
        "bestSeries": best_series,
        "bowlers": bowlers,
        "topAverages": sorted(bowlers, key=lambda row: row["avg"], reverse=True)[:3],
        "topGames": sorted(bowlers, key=lambda row: row["highGame"], reverse=True)[:3],
        "topSeries": sorted(bowlers, key=lambda row: row["highSeries"], reverse=True)[:3],
        "source": Path(path).name,
    }


def player_label(name):
    return PLAYER_DISPLAY_NAMES.get(name, name.title())


def league_leader_entry(row, score_key):
    return {
        "name": player_label(row["name"]),
        "score": str(row[score_key]),
    }


def build_league_leaders(summary):
    return {
        "averages": [league_leader_entry(row, "avg") for row in summary.get("topAverages", [])],
        "games": [league_leader_entry(row, "highGame") for row in summary.get("topGames", [])],
        "series": [league_leader_entry(row, "highSeries") for row in summary.get("topSeries", [])],
        "source": summary.get("source", ""),
    }


def update_home_leaders_from_high_avg(summary, apoel_players=None):
    apoel_keys = {name_key(name) for name in (apoel_players or [])}
    bowlers = summary.get("bowlers", [])
    apoel_bowlers = [row for row in bowlers if name_key(row.get("name")) in apoel_keys]
    if apoel_bowlers:
        summary = {
            **summary,
            "bestAverage": max(apoel_bowlers, key=lambda row: row["avg"]),
            "bestGame": max(apoel_bowlers, key=lambda row: row["highGame"]),
            "bestSeries": max(apoel_bowlers, key=lambda row: row["highSeries"]),
        }
    data = get_content("index")
    data["leaders"] = [
        {
            "label": "Ψηλότερος Μέσος Όρος",
            "value": player_label(summary["bestAverage"]["name"]),
            "score": f'Μ.Ο. {summary["bestAverage"]["avg"]}',
        },
        {
            "label": "Ψηλότερη Σειρά",
            "value": player_label(summary["bestSeries"]["name"]),
            "score": f'Σειρά {summary["bestSeries"]["highSeries"]}',
        },
        {
            "label": "Ψηλότερο Παιχνίδι",
            "value": player_label(summary["bestGame"]["name"]),
            "score": f'Παιχνίδι {summary["bestGame"]["highGame"]}',
        },
    ]
    set_content("index", data)


def import_score_pdfs(files):
    messages = []
    standings_payload = None
    if "standings_pdf" in files and files["standings_pdf"].filename:
        pdf_path = save_file_upload(files["standings_pdf"])
        standings_payload = parse_total_standings_pdf(pdf_path)
        set_content("totalstandings", standings_payload)
        messages.append(f"Imported standings: {standings_payload.get('season')} ({len(standings_payload.get('rows', []))} teams)")
    if "high_avg_pdf" in files and files["high_avg_pdf"].filename:
        pdf_path = save_file_upload(files["high_avg_pdf"])
        summary = parse_high_average_pdf(pdf_path)
        current_standings = standings_payload or get_content("totalstandings")
        update_home_leaders_from_high_avg(summary, current_standings.get("apoelPlayers", []))
        current_standings["leagueLeaders"] = build_league_leaders(summary)
        set_content("totalstandings", current_standings)
        messages.append(f"Imported high scores: {Path(pdf_path).name}")
    if not messages:
        raise ValueError("Choose at least one PDF to import.")
    return " · ".join(messages)


def league_leaders_html(leaders):
    groups = [
        ("Top Average", "Average", leaders.get("averages", [])),
        ("Top High Game", "High Game", leaders.get("games", [])),
        ("Top High Series", "High Series", leaders.get("series", [])),
    ]
    cards = []
    for title, score_label, rows in groups:
        if not rows:
            continue
        items = "".join(
            f'<li><span class="leader-rank">{index + 1}</span><strong>{e(row.get("name"))}</strong><em>{e(score_label)} {e(row.get("score"))}</em></li>'
            for index, row in enumerate(rows[:3])
        )
        cards.append(f'<article class="league-leader-card"><h3>{e(title)}</h3><ol>{items}</ol></article>')
    if not cards:
        return ""
    return (
        '<div class="league-leaders">'
        '<div class="section-head compact"><div><p class="section-subtitle">League leaders</p><h2 class="section-title">Top Performers</h2></div></div>'
        f'<div class="league-leader-grid">{"".join(cards)}</div></div>'
    )


def get_league_archives():
    data = get_content("league_archives")
    return data.get("items", []) if isinstance(data, dict) else []


def set_league_archives(items):
    set_content("league_archives", {"items": items})


def fresh_standings_payload(new_season):
    return {
        "title": "Συνολική Βαθμολογία",
        "hero": {
            "eyebrow": "BBC League",
            "heading": f"Βαθμολογία {new_season}",
            "text": "Ανέβασε τα PDF της νέας σεζόν από το admin για να ξεκινήσει ο νέος πίνακας.",
        },
        "season": new_season,
        "updatedAt": "",
        "source": "",
        "apoelPlayers": [],
        "leagueLeaders": {},
        "rows": [],
    }


def archive_current_season(new_season):
    new_season = (new_season or "").strip()
    if not new_season:
        raise ValueError("Enter the new season label first, for example 2026-2027.")
    current = get_content("totalstandings")
    if not current.get("rows"):
        raise ValueError("There are no standings rows to archive yet.")

    archives = get_league_archives()
    base_id = slugify(current.get("season") or current.get("title") or "season")
    archive_id = base_id
    existing_ids = {item.get("id") for item in archives}
    if archive_id in existing_ids:
        archive_id = f"{base_id}-{time.strftime('%Y%m%d%H%M%S')}"

    archived = dict(current)
    archived["id"] = archive_id
    archived["archivedAt"] = time.strftime("%Y-%m-%d")
    set_league_archives([archived] + archives)
    set_content("totalstandings", fresh_standings_payload(new_season))
    return f"Archived {current.get('season', 'previous season')} and started {new_season}"


def league_archives_html():
    archives = get_league_archives()
    if not archives:
        return ""
    cards = "".join(
        '<a class="tile link-tile archive-tile" href="/league_archive?id={id}">'
        '<span class="roster-role">Previous season</span>'
        '<h3>{season}</h3>'
        '<p>Archived {archived}. View the saved table and top performers.</p>'
        '</a>'.format(
            id=e(item.get("id")),
            season=e(item.get("season") or item.get("title") or "League archive"),
            archived=e(item.get("archivedAt") or "season record"),
        )
        for item in archives
    )
    return (
        '<section class="section"><div class="container">'
        f'{section_head("Previous Seasons", "League archive", "Old league tables stay here while the live table starts fresh.")}'
        f'<div class="grid grid-3">{cards}</div></div></section>'
    )


def standings_section(copy="Only logged-in admins can update this live table.", data=None):
    data = data or get_content("totalstandings")
    rows = sorted(
        [row for row in data.get("rows", []) if row.get("team") != "BYE"],
        key=lambda row: numberish(row.get("place"), 999),
    )
    table_rows = "".join(
        f'<tr class="{"is-leader" if index == 0 else ""} {"is-podium" if index < 3 else ""}">'
        f'<td class="standings-rank" data-label="#"><span class="rank-badge">{e(item.get("place"))}</span></td>'
        f'<td class="standings-team" data-label="Team"><span class="team-mark">{e(team_initials(item.get("team")))}</span><strong>{e(item.get("team"))}</strong></td>'
        f'<td class="standings-points" data-label="Points"><span>{e(item.get("pointsWon"))}</span></td>'
        f'<td class="standings-pins" data-label="Total Pins"><span>{e(item.get("totalPins"))}</span></td>'
        "</tr>"
        for index, item in enumerate(rows)
    )
    table_head = "".join(f"<th>{e(label)}</th>" for _, label in STANDINGS_DISPLAY_FIELDS)
    league_leaders = league_leaders_html(data.get("leagueLeaders", {}))
    empty_state = ""
    if not rows:
        empty_state = '<div class="callout">No standings have been uploaded for this season yet.</div>'
    return (
        '<section class="section"><div class="container">'
        f'{section_head("League Table", "Standings", copy)}'
        '<div class="stats-strip">'
        f'<div class="metric-card"><span>Season</span><strong>{e(data.get("season"))}</strong></div>'
        f'<div class="metric-card"><span>Teams</span><strong>{len(rows)}</strong></div>'
        f'<div class="metric-card"><span>Updated</span><strong>{e(data.get("updatedAt"))}</strong></div>'
        '</div>'
        '<div class="table-shell"><table class="standings-table"><thead><tr>'
        f'{table_head}'
        f'</tr></thead><tbody>{table_rows}</tbody></table></div>{empty_state}{league_leaders}</div></section>'
    )


def render_standings():
    data = get_content("totalstandings")
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "totalstandings")}</div>'
        f'{standings_section()}'
    )
    return render_site_layout(data.get("title", "Βαθμολογία"), "/totalstandings", body)


def render_gallery():
    data = get_content("gallery")
    cards = "".join(
        f'<article class="gallery-card">{image_html(item.get("image"), item.get("title"))}<h3>{e(item.get("title"))}</h3><p class="muted">{e(item.get("text"))}</p></article>'
        for item in data.get("items", [])
    )
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "gallery")}</div>'
        '<section class="section"><div class="container">'
        f'{section_head("Gallery", "Season moments", "Add and update gallery photos in the admin panel.")}'
        f'<div class="gallery-grid">{cards}</div></div></section>'
    )
    return render_site_layout(data.get("title", "Γκαλερί"), "/gallery", body)


def render_bbc_teams():
    data = get_content("bbc_teams")
    league_links = "".join(
        f'<a class="tile link-tile" href="{e(item.get("href"))}"><span class="roster-role">BBC League</span><h3>{e(item.get("label"))}</h3><p>{e(item.get("text"))}</p></a>'
        for item in BBC_LEAGUE_LINKS
    )
    groups = "".join(
        f'<article class="tile"><h3>{e(item.get("title"))}</h3><p>{e(item.get("text"))}</p></article>'
        for item in data.get("groups", [])
    )
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "bbc_teams")}</div>'
        f'{standings_section("Η τρέχουσα βαθμολογία εμφανίζεται απευθείας εδώ και ενημερώνεται από το admin.")}'
        f'{league_archives_html()}'
        '<section class="section"><div class="container">'
        f'{section_head("BBC League Links", "League hub", "All the old dropdown links are now here as large mobile-friendly cards.")}'
        f'<div class="grid grid-3">{league_links}</div></div></section>'
        '<section class="section"><div class="container">'
        f'{section_head("BBC League", "Community", "Teams, events and league context in one editable page.")}'
        f'<div class="grid grid-3">{groups}</div></div></section>'
    )
    return render_site_layout(data.get("title", "BBC Teams"), "/bbc_teams", body)


def render_league_archive(query):
    archive_id = query.get("id", "")
    archive = next((item for item in get_league_archives() if item.get("id") == archive_id), None)
    if not archive:
        body = '<section class="section"><div class="container"><div class="callout">League archive not found.</div></div></section>'
        return render_site_layout("League Archive", "/bbc_teams", body)
    hero = {
        "eyebrow": "BBC Archive",
        "heading": archive.get("season") or archive.get("title") or "Previous Season",
        "text": f'Archived on {archive.get("archivedAt", "")}. This page keeps the old league record while the current table can start fresh.',
    }
    body = (
        f'<div class="container">{hero_section(hero, "bbc_teams")}</div>'
        f'{standings_section("Saved archive table. This record is read-only from the public site.", data=archive)}'
    )
    return render_site_layout(archive.get("season") or "League Archive", "/bbc_teams", body)


def render_sponsors():
    data = get_content("xorigi")
    sponsors = "".join(
        f'<article class="sponsor-card">{image_html(item.get("image"), item.get("name"))}<h3>{e(item.get("name"))}</h3><p class="muted">{e(item.get("type"))}</p></article>'
        for item in data.get("sponsors", [])
    )
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "xorigi")}</div>'
        '<section class="section"><div class="container">'
        f'{section_head("Partners", "Support network", "Names and logos are editable from the admin panel.")}'
        f'<div class="sponsor-grid">{sponsors}</div></div></section>'
    )
    return render_site_layout(data.get("title", "Χορηγοί"), "/xorigi", body)


def render_coming_soon():
    data = get_content("coming_soon")
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "coming_soon")}</div>'
        '<section class="section"><div class="container"><div class="callout">Use this page as a placeholder for future content.</div></div></section>'
    )
    return render_site_layout(data.get("title", "Σύντομα Κοντά Σας"), "/coming_soon", body)


def render_tools():
    data = get_content("tools")
    body = (
        f'<div class="container">{hero_section(data.get("hero", {}), "tools")}</div>'
        '<section class="section"><div class="container">'
        f'{section_head("Lane Play Calculator", "Bowling calculator", "Ported from your other Codex project and adapted for the website.")}'
        '<div class="tools-grid">'
        '<article class="tool-panel">'
        '<div class="tool-panel-head"><strong>Calculator Inputs</strong><span class="meta-pill">Live results</span></div>'
        '<div class="tool-form">'
        '<label class="tool-label">Preset<select class="tool-select" id="patternPreset"><option value="">Custom line</option></select></label>'
        '<div class="tool-toggle-row">'
        '<label class="tool-radio"><input type="radio" name="handedness" value="right" checked> Right handed</label>'
        '<label class="tool-radio"><input type="radio" name="handedness" value="left"> Left handed</label>'
        '</div>'
        '<div class="tool-fields-grid">'
        '<label class="tool-label">Arrow board<input class="tool-input" id="arrowBoard" type="number" min="1" max="39" step="0.1" value="12"></label>'
        '<label class="tool-label">Breakpoint board<input class="tool-input" id="breakpointBoard" type="number" min="1" max="39" step="0.1" value="8"></label>'
        '<label class="tool-label">Breakpoint distance (ft)<input class="tool-input" id="breakpointDistance" type="number" min="16" max="60" step="0.1" value="40"></label>'
        '<label class="tool-label">Laydown distance<input class="tool-input" id="laydownDistance" type="number" min="0" max="20" step="0.1" value="6"></label>'
        '<label class="tool-label">Drift distance<input class="tool-input" id="driftDistance" type="number" min="0" max="20" step="0.1" value="5"></label>'
        '<label class="tool-label">Drift direction<select class="tool-select" id="driftDirection"><option value="left">Left</option><option value="right">Right</option></select></label>'
        '</div>'
        '</div></article>'
        '<article class="tool-panel">'
        '<div class="tool-panel-head"><strong>Projected Line</strong><span class="meta-pill">Based on arrows + breakpoint</span></div>'
        '<div class="tool-stats-grid" id="lanePlayResults"></div>'
        '<div class="tool-moves-grid" id="lanePlayMoves"></div>'
        '<div class="tool-notes" id="lanePlayNotes"></div>'
        '</article>'
        '</div></div></section>'
    )
    scripts = '<script src="/assets/js/tools.js"></script>'
    return render_site_layout(data.get("title", "Tools"), "/tools", body, extra_scripts=scripts)


def admin_layout(title, inner, current="/admin", message=""):
    nav_items = [
        ("/admin", "Dashboard"),
        ("/admin/site", "Site"),
        ("/admin/home", "Home"),
        ("/admin/news", "News"),
        ("/admin/team", "Team"),
        ("/admin/schedule", "Schedule"),
        ("/admin/standings", "Standings"),
        ("/admin/gallery", "Gallery"),
        ("/admin/bbc-teams", "BBC Teams"),
        ("/admin/sponsors", "Sponsors"),
        ("/admin/coming-soon", "Coming Soon"),
        ("/admin/account", "Account"),
    ]
    nav = "".join(
        f'<a class="admin-nav-link {"is-active" if href == current else ""}" href="{href}">{label}</a>'
        for href, label in nav_items
    )
    flash = f'<div class="admin-flash">{e(message)}</div>' if message else ""
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{e(title)} | APOEL Admin</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=JetBrains+Mono:wght@500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/styles.css">
    <style>
      .admin-shell {{ width:min(100% - 2rem, 1240px); margin: 1.5rem auto 3rem; }}
      .admin-bar, .admin-card, .admin-grid-card {{ background: rgba(10,21,39,.9); border:1px solid rgba(255,255,255,.1); border-radius:24px; box-shadow: var(--shadow); }}
      .admin-bar {{ padding: 1rem 1.2rem; display:flex; justify-content:space-between; gap:1rem; align-items:center; }}
      .admin-nav {{ display:flex; flex-wrap:wrap; gap:.6rem; margin:1rem 0; }}
      .admin-nav-link {{ padding:.75rem .95rem; border-radius:999px; background:rgba(255,255,255,.05); color:var(--muted); }}
      .admin-nav-link.is-active {{ background:rgba(246,195,36,.16); color:var(--text); }}
      .admin-flash {{ padding: .9rem 1rem; border-radius:18px; border:1px solid rgba(105,212,153,.3); background:rgba(105,212,153,.12); color:#c8ffe0; margin-bottom:1rem; }}
      .admin-card {{ padding:1.2rem; }}
      .admin-grid {{ display:grid; gap:1rem; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
      .admin-grid-card {{ padding:1rem; }}
      .admin-form {{ display:grid; gap:1.25rem; }}
      .admin-fieldset {{ border:1px solid rgba(255,255,255,.08); border-radius:20px; padding:1rem; }}
      .admin-fieldset legend {{ padding:0 .4rem; color:var(--yellow); font-weight:700; }}
      .admin-row {{ display:grid; gap:.85rem; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .admin-input, .admin-textarea, .admin-select {{ width:100%; min-height:44px; padding:.75rem .85rem; color:var(--text); background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.08); border-radius:14px; }}
      .admin-textarea {{ min-height:120px; resize:vertical; }}
      .admin-label {{ display:grid; gap:.35rem; font-weight:600; }}
      .admin-repeater {{ display:grid; gap:.9rem; }}
      .admin-repeater-item {{ border:1px solid rgba(255,255,255,.08); border-radius:18px; padding:1rem; background:rgba(255,255,255,.03); }}
      .admin-actions {{ display:flex; gap:.75rem; flex-wrap:wrap; }}
      .admin-mini {{ font-size:.9rem; color:var(--muted); }}
      @media (max-width: 820px) {{ .admin-row {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <div class="admin-shell">
      <div class="admin-bar">
        <div>
          <strong>APOEL Bowling Admin</strong>
          <div class="admin-mini">Private editor for the live site</div>
        </div>
        <div class="admin-actions">
          <a class="button button-secondary" href="/">View site</a>
          <a class="button button-secondary" href="/admin/logout">Log out</a>
        </div>
      </div>
      <nav class="admin-nav">{nav}</nav>
      {flash}
      {inner}
    </div>
    <script>
      function addRepeaterRow(id) {{
        const container = document.getElementById(id);
        const template = document.getElementById(id + '-template');
        const index = container.querySelectorAll('.admin-repeater-item').length;
        container.insertAdjacentHTML('beforeend', template.innerHTML.replace(/__INDEX__/g, index));
      }}
      document.addEventListener('click', function (event) {{
        if (event.target.matches('[data-remove-row]')) {{
          event.target.closest('.admin-repeater-item').remove();
        }}
      }});
      document.addEventListener('change', function (event) {{
        if (!event.target.matches('input[type="file"][name$="_upload"]')) return;
        const fileInput = event.target;
        const pathInputName = fileInput.name.replace(/_upload$/, '');
        const row = fileInput.closest('.admin-repeater-item') || fileInput.closest('.admin-fieldset') || document;
        const pathInput = row.querySelector('input[name="' + CSS.escape(pathInputName) + '"]') || document.querySelector('input[name="' + CSS.escape(pathInputName) + '"]');
        if (!pathInput || !fileInput.files || !fileInput.files[0]) return;
        const safeName = fileInput.files[0].name.replace(/[^A-Za-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '') || 'upload';
        pathInput.value = 'assets/images/uploads/' + safeName;
      }});
    </script>
  </body>
</html>"""


def admin_input(name, label, value="", input_type="text", placeholder=""):
    return (
        f'<label class="admin-label">{e(label)}'
        f'<input class="admin-input" type="{e(input_type)}" name="{e(name)}" value="{e(value)}" placeholder="{e(placeholder)}"></label>'
    )


def admin_textarea(name, label, value="", placeholder=""):
    return (
        f'<label class="admin-label">{e(label)}'
        f'<textarea class="admin-textarea" name="{e(name)}" placeholder="{e(placeholder)}">{e(value)}</textarea></label>'
    )


def repeater_item_html(prefix, index, columns, item):
    fields = []
    for key, label, field_type in columns:
        value = item.get(key, "")
        if field_type == "textarea":
            fields.append(admin_textarea(f"{prefix}__{index}__{key}", label, value))
        elif field_type == "image":
            fields.append(admin_input(f"{prefix}__{index}__{key}", label, value))
            fields.append(admin_input(f"{prefix}__{index}__{key}_upload", f"{label} upload", "", "file"))
        else:
            fields.append(admin_input(f"{prefix}__{index}__{key}", label, value))
    joined = "".join(fields)
    return f'<div class="admin-repeater-item"><div class="admin-row">{joined}</div><div class="admin-actions" style="margin-top:.8rem;"><button class="button button-secondary" type="button" data-remove-row>Remove</button></div></div>'


def render_repeater(prefix, title, columns, items):
    current = "".join(repeater_item_html(prefix, index, columns, item) for index, item in enumerate(items))
    template = repeater_item_html(prefix, "__INDEX__", columns, {})
    return (
        f'<fieldset class="admin-fieldset"><legend>{e(title)}</legend>'
        f'<div id="{e(prefix)}" class="admin-repeater">{current}</div>'
        f'<template id="{e(prefix)}-template">{template}</template>'
        f'<div class="admin-actions" style="margin-top:.85rem;"><button class="button button-secondary" type="button" onclick="addRepeaterRow(\'{e(prefix)}\')">Add item</button></div>'
        '</fieldset>'
    )


def admin_dashboard(query):
    password_note = ""
    if INITIAL_PASSWORD_PATH.exists():
        password_note = f'<div class="callout">Initial admin credentials were written to <span class="inline-code">{e(str(INITIAL_PASSWORD_PATH))}</span>. Change the password after first login.</div>'
    cards = [
        ("/admin/home", "Homepage", "Hero, quick links, venue, leaders, FAQ"),
        ("/admin/news", "News", "Headlines, categories, photos and article cards"),
        ("/admin/team", "Team", "Roster, player photos and achievements"),
        ("/admin/schedule", "Schedule", "Events, dates and links"),
        ("/admin/standings", "Standings", "PDF import, season archive and live table"),
        ("/admin/gallery", "Gallery", "Photo cards and captions"),
        ("/admin/sponsors", "Sponsors", "Partner names and logos"),
    ]
    grid = "".join(
        f'<a class="admin-grid-card" href="{href}"><strong>{title}</strong><p class="muted">{desc}</p></a>'
        for href, title, desc in cards
    )
    body = f'<div class="admin-card">{password_note}<div class="admin-grid">{grid}</div></div>'
    return admin_layout("Dashboard", body, "/admin", query.get("message", ""))


def render_login(error=""):
    error_html = f'<div class="callout" style="margin-bottom:1rem;">{e(error)}</div>' if error else ""
    body = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin Login</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/styles.css">
  </head>
  <body>
    <div class="container" style="padding:4rem 0;">
      <div class="admin-card" style="max-width:520px; margin:0 auto;">
        <h1 class="section-title">Admin Login</h1>
        <p class="muted">Only approved admins can edit the live website.</p>
        {error_html}
        <form method="post" class="admin-form">
          {admin_input("username", "Username")}
          {admin_input("password", "Password", "", "password")}
          <div class="admin-actions">
            <button class="button button-primary" type="submit">Log in</button>
            <a class="button button-secondary" href="/">Back to site</a>
          </div>
        </form>
      </div>
    </div>
  </body>
</html>"""
    return body


def save_site_settings(form):
    payload = {
        "clubName": form.get("clubName", "").strip(),
        "clubTagline": form.get("clubTagline", "").strip(),
        "phone": form.get("phone", "").strip(),
        "email": form.get("email", "").strip(),
        "facebook": form.get("facebook", "").strip(),
        "venue": form.get("venue", "").strip(),
        "venueAddress": form.get("venueAddress", "").strip(),
        "season": form.get("season", "").strip(),
    }
    set_content("config", payload)


def page_form_site(query):
    data = get_content("config")
    fields = (
        '<div class="admin-card"><form method="post" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Site settings</legend><div class="admin-row">'
        f'{admin_input("clubName", "Club name", data.get("clubName"))}'
        f'{admin_input("season", "Season", data.get("season"))}'
        f'{admin_input("clubTagline", "Tagline", data.get("clubTagline"))}'
        f'{admin_input("venue", "Venue", data.get("venue"))}'
        f'{admin_input("phone", "Phone", data.get("phone"))}'
        f'{admin_input("email", "Email", data.get("email"))}'
        f'{admin_input("facebook", "Facebook URL", data.get("facebook"))}'
        f'{admin_input("venueAddress", "Venue address", data.get("venueAddress"))}'
        '</div></fieldset><div class="admin-actions"><button class="button button-primary" type="submit">Save settings</button></div></form></div>'
    )
    return admin_layout("Site", fields, "/admin/site", query.get("message", ""))


def save_home(form, files):
    data = get_content("index")
    hero_image = apply_single_upload(form.get("hero_image", "").strip(), files, "hero_image")
    venue_image = apply_single_upload(form.get("venue_image", "").strip(), files, "venue_image")
    quick_links = parse_repeater(form, "quickLinks", ["title", "text", "href"])
    leaders = parse_repeater(form, "leaders", ["label", "value", "score"])
    faq = parse_repeater(form, "faq", ["q", "a"])
    bullets = [item["text"] for item in parse_repeater(form, "venueBullets", ["text"])]
    payload = {
        "title": data.get("title", "APOEL Bowling"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
            "primaryLabel": form.get("hero_primaryLabel", "").strip(),
            "primaryHref": form.get("hero_primaryHref", "").strip(),
            "secondaryLabel": form.get("hero_secondaryLabel", "").strip(),
            "secondaryHref": form.get("hero_secondaryHref", "").strip(),
            "image": hero_image,
            "panelLabel": form.get("hero_panelLabel", "").strip(),
            "panelTitle": form.get("hero_panelTitle", "").strip(),
            "panelText": form.get("hero_panelText", "").strip(),
        },
        "quickLinks": quick_links,
        "venue": {
            "title": form.get("venue_title", "").strip(),
            "subtitle": form.get("venue_subtitle", "").strip(),
            "text": form.get("venue_text", "").strip(),
            "image": venue_image,
            "bullets": bullets,
        },
        "leaders": leaders,
        "faq": faq,
    }
    set_content("index", payload)


def page_form_home(query):
    data = get_content("index")
    hero = data.get("hero", {})
    venue = data.get("venue", {})
    form_html = (
        '<div class="admin-card"><form method="post" enctype="multipart/form-data" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Hero text", hero.get("text"))}'
        f'{admin_input("hero_image", "Hero image URL/path", hero.get("image"))}'
        f'{admin_input("hero_image_upload", "Hero image upload", "", "file")}'
        f'{admin_input("hero_primaryLabel", "Primary button label", hero.get("primaryLabel"))}'
        f'{admin_input("hero_primaryHref", "Primary button link", hero.get("primaryHref"))}'
        f'{admin_input("hero_secondaryLabel", "Secondary button label", hero.get("secondaryLabel"))}'
        f'{admin_input("hero_secondaryHref", "Secondary button link", hero.get("secondaryHref"))}'
        f'{admin_input("hero_panelLabel", "Panel label", hero.get("panelLabel"))}'
        f'{admin_input("hero_panelTitle", "Panel title", hero.get("panelTitle"))}'
        f'{admin_textarea("hero_panelText", "Panel text", hero.get("panelText"))}'
        '</div></fieldset>'
        '<fieldset class="admin-fieldset"><legend>Venue</legend><div class="admin-row">'
        f'{admin_input("venue_title", "Venue title", venue.get("title"))}'
        f'{admin_input("venue_subtitle", "Venue subtitle", venue.get("subtitle"))}'
        f'{admin_textarea("venue_text", "Venue text", venue.get("text"))}'
        f'{admin_input("venue_image", "Venue image URL/path", venue.get("image"))}'
        f'{admin_input("venue_image_upload", "Venue image upload", "", "file")}'
        '</div></fieldset>'
        f'{render_repeater("venueBullets", "Venue bullets", [("text", "Bullet", "text")], [{"text": item} for item in venue.get("bullets", [])])}'
        f'{render_repeater("quickLinks", "Quick links", [("title", "Title", "text"), ("text", "Text", "textarea"), ("href", "Link", "text")], data.get("quickLinks", []))}'
        f'{render_repeater("leaders", "Leaders", [("label", "Label", "text"), ("value", "Player name", "text"), ("score", "Score", "text")], data.get("leaders", []))}'
        f'{render_repeater("faq", "FAQ", [("q", "Question", "text"), ("a", "Answer", "textarea")], data.get("faq", []))}'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Save homepage</button></div></form></div>'
    )
    return admin_layout("Home", form_html, "/admin/home", query.get("message", ""))


def save_news(form, files):
    data = get_content("news")
    items = parse_repeater(form, "items", ["title", "date", "category", "image", "text"])
    apply_repeater_uploads(items, files, "items", ["image"])
    payload = {
        "title": data.get("title", "Νέα"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
        },
        "items": items,
    }
    set_content("news", payload)


def page_form_news(query):
    data = get_content("news")
    hero = data.get("hero", {})
    form_html = (
        '<div class="admin-card"><form method="post" enctype="multipart/form-data" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Text", hero.get("text"))}'
        '</div></fieldset>'
        f'{render_repeater("items", "News items", [("title", "Title", "text"), ("date", "Date", "text"), ("category", "Category", "text"), ("image", "Image URL/path", "image"), ("text", "Text", "textarea")], data.get("items", []))}'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Save news</button></div></form></div>'
    )
    return admin_layout("News", form_html, "/admin/news", query.get("message", ""))


def save_team(form, files):
    data = get_content("i_omada")
    roster = parse_repeater(form, "roster", ["name", "role", "bio", "image"])
    apply_repeater_uploads(roster, files, "roster", ["image"])
    achievements = [item["text"] for item in parse_repeater(form, "achievements", ["text"])]
    payload = {
        "title": data.get("title", "Η Ομάδα"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
        },
        "roster": roster,
        "achievements": achievements,
    }
    set_content("i_omada", payload)


def page_form_team(query):
    data = get_content("i_omada")
    hero = data.get("hero", {})
    form_html = (
        '<div class="admin-card"><form method="post" enctype="multipart/form-data" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Text", hero.get("text"))}'
        '</div></fieldset>'
        f'{render_repeater("roster", "Roster", [("name", "Name", "text"), ("role", "Role", "text"), ("bio", "Bio", "textarea"), ("image", "Photo URL/path", "image")], data.get("roster", []))}'
        f'{render_repeater("achievements", "Achievements", [("text", "Achievement", "text")], [{"text": item} for item in data.get("achievements", [])])}'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Save team page</button></div></form></div>'
    )
    return admin_layout("Team", form_html, "/admin/team", query.get("message", ""))


def save_schedule(form):
    data = get_content("agonistiko_programma")
    schedule = parse_repeater(form, "schedule", ["day", "month", "title", "details", "link"])
    payload = {
        "title": data.get("title", "Αγωνιστικό Πρόγραμμα"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
        },
        "calendarUrl": form.get("calendarUrl", "").strip(),
        "schedule": schedule,
    }
    set_content("agonistiko_programma", payload)


def page_form_schedule(query):
    data = get_content("agonistiko_programma")
    hero = data.get("hero", {})
    form_html = (
        '<div class="admin-card"><form method="post" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Text", hero.get("text"))}'
        f'{admin_input("calendarUrl", "Google Calendar embed URL", data.get("calendarUrl") or DEFAULT_CONTENT["agonistiko_programma"]["calendarUrl"])}'
        '</div></fieldset>'
        '<div class="callout">The public calendar page now uses the Google Calendar embed above. The manual schedule items below are kept only as backup/reference content.</div>'
        f'{render_repeater("schedule", "Backup schedule items", [("day", "Day", "text"), ("month", "Month", "text"), ("title", "Title", "text"), ("details", "Details", "textarea"), ("link", "Link", "text")], data.get("schedule", []))}'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Save schedule</button></div></form></div>'
    )
    return admin_layout("Schedule", form_html, "/admin/schedule", query.get("message", ""))


def save_standings(form):
    data = get_content("totalstandings")
    rows = parse_repeater(form, "rows", [field for field, _ in STANDINGS_FIELDS])
    payload = {
        "title": data.get("title", "Συνολική Βαθμολογία"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
        },
        "season": form.get("season", "").strip(),
        "updatedAt": form.get("updatedAt", "").strip(),
        "source": data.get("source", ""),
        "apoelPlayers": data.get("apoelPlayers", []),
        "leagueLeaders": data.get("leagueLeaders", {}),
        "rows": rows,
    }
    set_content("totalstandings", payload)


def page_form_standings(query):
    data = get_content("totalstandings")
    hero = data.get("hero", {})
    next_year = str(time.localtime().tm_year + 1)
    current_year = str(time.localtime().tm_year)
    archive_html = (
        '<div class="admin-card"><form method="post" class="admin-form">'
        '<input type="hidden" name="league_action" value="archive_start">'
        '<fieldset class="admin-fieldset"><legend>Season archive</legend>'
        '<p class="editor-note">Use this after the final league week. It saves the current standings as a previous season, then clears the live table for the new season.</p>'
        '<div class="admin-row">'
        f'{admin_input("new_season", "New season label", f"{current_year}-{next_year}", "text", "2026-2027")}'
        '</div></fieldset>'
        '<div class="admin-actions"><button class="button button-secondary" type="submit">Archive current season and start new season</button></div>'
        '</form></div>'
    )
    import_html = (
        '<div class="admin-card"><form method="post" enctype="multipart/form-data" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Import PDFs</legend>'
        '<p class="editor-note">Upload reports with the same BLS format. The standings PDF updates the BBC League table; the high-average PDF updates the homepage leader cards.</p>'
        '<div class="admin-row">'
        f'{admin_input("standings_pdf", "TOTAL STANDINGS PDF", "", "file")}'
        f'{admin_input("high_avg_pdf", "HIGH AVG PDF", "", "file")}'
        '</div></fieldset>'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Import PDFs</button></div>'
        '</form></div>'
    )
    form_html = archive_html + import_html + (
        '<div class="admin-card"><form method="post" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Text", hero.get("text"))}'
        f'{admin_input("season", "Season", data.get("season"))}'
        f'{admin_input("updatedAt", "Updated at", data.get("updatedAt"))}'
        '</div></fieldset>'
        f'{render_repeater("rows", "Standings rows", [(field, label, "text") for field, label in STANDINGS_FIELDS], data.get("rows", []))}'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Save standings</button></div></form></div>'
    )
    return admin_layout("Standings", form_html, "/admin/standings", query.get("message", ""))


def save_gallery(form, files):
    data = get_content("gallery")
    items = parse_repeater(form, "items", ["title", "image", "text"])
    apply_repeater_uploads(items, files, "items", ["image"])
    payload = {
        "title": data.get("title", "Γκαλερί"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
        },
        "items": items,
    }
    set_content("gallery", payload)


def page_form_gallery(query):
    data = get_content("gallery")
    hero = data.get("hero", {})
    form_html = (
        '<div class="admin-card"><form method="post" enctype="multipart/form-data" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Text", hero.get("text"))}'
        '</div></fieldset>'
        f'{render_repeater("items", "Gallery items", [("title", "Title", "text"), ("image", "Image URL/path", "image"), ("text", "Caption", "textarea")], data.get("items", []))}'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Save gallery</button></div></form></div>'
    )
    return admin_layout("Gallery", form_html, "/admin/gallery", query.get("message", ""))


def save_bbc_teams(form):
    data = get_content("bbc_teams")
    groups = parse_repeater(form, "groups", ["title", "text"])
    payload = {
        "title": data.get("title", "BBC Teams"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
        },
        "groups": groups,
    }
    set_content("bbc_teams", payload)


def page_form_bbc_teams(query):
    data = get_content("bbc_teams")
    hero = data.get("hero", {})
    form_html = (
        '<div class="admin-card"><form method="post" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Text", hero.get("text"))}'
        '</div></fieldset>'
        f'{render_repeater("groups", "BBC team groups", [("title", "Title", "text"), ("text", "Text", "textarea")], data.get("groups", []))}'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Save BBC teams page</button></div></form></div>'
    )
    return admin_layout("BBC Teams", form_html, "/admin/bbc-teams", query.get("message", ""))


def save_sponsors(form, files):
    data = get_content("xorigi")
    sponsors = parse_repeater(form, "sponsors", ["name", "image", "type"])
    apply_repeater_uploads(sponsors, files, "sponsors", ["image"])
    payload = {
        "title": data.get("title", "Χορηγοί"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
        },
        "sponsors": sponsors,
    }
    set_content("xorigi", payload)


def page_form_sponsors(query):
    data = get_content("xorigi")
    hero = data.get("hero", {})
    form_html = (
        '<div class="admin-card"><form method="post" enctype="multipart/form-data" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Text", hero.get("text"))}'
        '</div></fieldset>'
        f'{render_repeater("sponsors", "Sponsors", [("name", "Name", "text"), ("image", "Logo URL/path", "image"), ("type", "Type", "text")], data.get("sponsors", []))}'
        '<div class="admin-actions"><button class="button button-primary" type="submit">Save sponsors</button></div></form></div>'
    )
    return admin_layout("Sponsors", form_html, "/admin/sponsors", query.get("message", ""))


def save_coming_soon(form):
    data = get_content("coming_soon")
    payload = {
        "title": data.get("title", "Σύντομα Κοντά Σας"),
        "hero": {
            "eyebrow": form.get("hero_eyebrow", "").strip(),
            "heading": form.get("hero_heading", "").strip(),
            "text": form.get("hero_text", "").strip(),
        },
    }
    set_content("coming_soon", payload)


def page_form_coming_soon(query):
    data = get_content("coming_soon")
    hero = data.get("hero", {})
    form_html = (
        '<div class="admin-card"><form method="post" class="admin-form"><fieldset class="admin-fieldset"><legend>Hero</legend><div class="admin-row">'
        f'{admin_input("hero_eyebrow", "Eyebrow", hero.get("eyebrow"))}'
        f'{admin_input("hero_heading", "Heading", hero.get("heading"))}'
        f'{admin_textarea("hero_text", "Text", hero.get("text"))}'
        '</div></fieldset><div class="admin-actions"><button class="button button-primary" type="submit">Save page</button></div></form></div>'
    )
    return admin_layout("Coming Soon", form_html, "/admin/coming-soon", query.get("message", ""))


def page_form_account(query):
    form_html = (
        '<div class="admin-card"><form method="post" class="admin-form">'
        '<fieldset class="admin-fieldset"><legend>Change password</legend><div class="admin-row">'
        f'{admin_input("current_password", "Current password", "", "password")}'
        f'{admin_input("new_password", "New password", "", "password")}'
        '</div></fieldset><div class="admin-actions"><button class="button button-primary" type="submit">Update password</button></div></form></div>'
    )
    return admin_layout("Account", form_html, "/admin/account", query.get("message", ""))


def update_password(username, form):
    current = form.get("current_password", "")
    new_password = form.get("new_password", "")
    with db() as conn:
        row = conn.execute("select password_hash from admin_users where username = ?", (username,)).fetchone()
        if not row or not password_matches(current, row["password_hash"]):
            return False, "Current password is incorrect."
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters."
        conn.execute("update admin_users set password_hash = ? where username = ?", (password_hash(new_password), username))
    return True, "Password updated."


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()

    if path.startswith("/assets/"):
        status, headers, body = serve_file(ASSETS_DIR / path.removeprefix("/assets/"))
        start_response(status, headers)
        return [body]
    if path.startswith("/uploads/"):
        status, headers, body = serve_file(UPLOADS_DIR / path.removeprefix("/uploads/"))
        start_response(status, headers)
        return [body]

    if path == "/admin/login":
        if method == "POST":
            form, _ = parse_request(environ)
            username = form.get("username", "").strip()
            password = form.get("password", "")
            with db() as conn:
                row = conn.execute("select * from admin_users where username = ?", (username,)).fetchone()
            if row and password_matches(password, row["password_hash"]):
                expiry = int(time.time()) + 60 * 60 * 24 * 14
                token = make_signed_value(username, expiry)
                status, headers, body = redirect("/admin")
                headers.append(("Set-Cookie", f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax"))
                start_response(status, headers)
                return [body]
            status, headers, body = response_html(render_login("Invalid username or password."))
            start_response(status, headers)
            return [body]
        status, headers, body = response_html(render_login())
        start_response(status, headers)
        return [body]

    username = read_session(environ)
    if path.startswith("/admin"):
        if not username:
            status, headers, body = redirect("/admin/login")
            start_response(status, headers)
            return [body]

        query, files = parse_request(environ)
        if path == "/admin/logout":
            status, headers, body = redirect("/admin/login")
            headers.append(("Set-Cookie", f"{SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"))
            start_response(status, headers)
            return [body]

        if path == "/admin" and method == "GET":
            status, headers, body = response_html(admin_dashboard(query))
        elif path == "/admin/site":
            if method == "POST":
                save_site_settings(query)
                status, headers, body = redirect("/admin/site?message=Saved")
            else:
                status, headers, body = response_html(page_form_site(query))
        elif path == "/admin/home":
            if method == "POST":
                save_home(query, files)
                status, headers, body = redirect("/admin/home?message=Saved")
            else:
                status, headers, body = response_html(page_form_home(query))
        elif path == "/admin/news":
            if method == "POST":
                save_news(query, files)
                status, headers, body = redirect("/admin/news?message=Saved")
            else:
                status, headers, body = response_html(page_form_news(query))
        elif path == "/admin/team":
            if method == "POST":
                save_team(query, files)
                status, headers, body = redirect("/admin/team?message=Saved")
            else:
                status, headers, body = response_html(page_form_team(query))
        elif path == "/admin/schedule":
            if method == "POST":
                save_schedule(query)
                status, headers, body = redirect("/admin/schedule?message=Saved")
            else:
                status, headers, body = response_html(page_form_schedule(query))
        elif path == "/admin/standings":
            if method == "POST":
                if query.get("league_action") == "archive_start":
                    try:
                        message = archive_current_season(query.get("new_season", ""))
                    except Exception as exc:
                        message = f"Archive failed: {exc}"
                    status, headers, body = redirect(f"/admin/standings?message={quote_plus(message)}")
                elif any(key in files and files[key].filename for key in ("standings_pdf", "high_avg_pdf")):
                    try:
                        message = import_score_pdfs(files)
                    except Exception as exc:
                        message = f"Import failed: {exc}"
                    status, headers, body = redirect(f"/admin/standings?message={quote_plus(message)}")
                else:
                    save_standings(query)
                    status, headers, body = redirect("/admin/standings?message=Saved")
            else:
                status, headers, body = response_html(page_form_standings(query))
        elif path == "/admin/gallery":
            if method == "POST":
                save_gallery(query, files)
                status, headers, body = redirect("/admin/gallery?message=Saved")
            else:
                status, headers, body = response_html(page_form_gallery(query))
        elif path == "/admin/bbc-teams":
            if method == "POST":
                save_bbc_teams(query)
                status, headers, body = redirect("/admin/bbc-teams?message=Saved")
            else:
                status, headers, body = response_html(page_form_bbc_teams(query))
        elif path == "/admin/sponsors":
            if method == "POST":
                save_sponsors(query, files)
                status, headers, body = redirect("/admin/sponsors?message=Saved")
            else:
                status, headers, body = response_html(page_form_sponsors(query))
        elif path == "/admin/coming-soon":
            if method == "POST":
                save_coming_soon(query)
                status, headers, body = redirect("/admin/coming-soon?message=Saved")
            else:
                status, headers, body = response_html(page_form_coming_soon(query))
        elif path == "/admin/account":
            if method == "POST":
                ok, message = update_password(username, query)
                status, headers, body = redirect(f"/admin/account?message={message.replace(' ', '+')}")
            else:
                status, headers, body = response_html(page_form_account(query))
        else:
            status, headers, body = response_html("<h1>Not found</h1>", "404 Not Found")

        start_response(status, headers)
        return [body]

    public_routes = {
        "/": render_home,
        "/index.html": render_home,
        "/news": render_news,
        "/news.html": render_news,
        "/i_omada": render_team,
        "/i_omada.html": render_team,
        "/agonistiko_programma": render_schedule,
        "/agonistiko_programma.html": render_schedule,
        "/totalstandings": render_standings,
        "/totalstandings.html": render_standings,
        "/gallery": render_gallery,
        "/gallery.html": render_gallery,
        "/bbc_teams": render_bbc_teams,
        "/bbc_teams.html": render_bbc_teams,
        "/xorigi": render_sponsors,
        "/xorigi.html": render_sponsors,
        "/tools": render_tools,
        "/tools.html": render_tools,
        "/coming_soon": render_coming_soon,
        "/coming_soon.html": render_coming_soon,
    }
    if path == "/league_archive":
        query, _ = parse_request(environ)
        status, headers, body = response_html(render_league_archive(query))
    elif path in public_routes:
        status, headers, body = response_html(public_routes[path]())
    else:
        status, headers, body = response_html("<h1>Not found</h1>", "404 Not Found")
    start_response(status, headers)
    return [body]


def main():
    init_db()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    with make_server(host, port, application) as server:
        print(f"APOEL Bowling admin site running on http://{host}:{port}")
        print(f"Admin: http://{host}:{port}/admin")
        if INITIAL_PASSWORD_PATH.exists():
            print(f"Initial credentials: {INITIAL_PASSWORD_PATH}")
        server.serve_forever()


if __name__ == "__main__":
    main()
