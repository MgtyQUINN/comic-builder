"""English names for comic.json.

build_comic.py works internally with the original (Norwegian) field names. This module lets
people write comic.json in English; normalize() translates keys and the values of a few
fields before building. Norwegian files still work unchanged.
"""

KEYS = {
    # book
    "title": "tittel", "subtitle": "undertittel", "author": "forfatter", "language": "språk",
    "style": "stil", "font_pt": "skrift_pt", "uppercase": "store_bokstaver", "box_color": "boks_farge",
    "page_numbers": "sidetall", "characters": "figurer", "cover": "omslag", "pages": "sider",
    "print_style": "stilfilter", "screen_mm": "raster_mm", "paper": "papir",
    # characters
    "name": "navn", "reference": "referanse", "traits": "kjennetegn",
    # cover
    "title_position": "tittel_plass", "title_color": "tittel_farge",
    # pages, rows, panels
    "rows": "rader", "panels": "paneler", "layout": "oppsett", "image": "bilde", "width": "bredde",
    "focus": "fokus", "border": "kant", "darken": "mork", "lock_focus": "fokus_fast",
    "overlay": "overlegg", "soft": "myk", "text": "tekst",
    # text items
    "w": "b", "tail": "hale", "size": "str", "color": "farge", "max_w": "maxb",
}

TYPES = {
    # page types
    "panels": "paneler", "title": "tittel", "chapter": "kapittel", "text": "tekst",
    # text types
    "speech": "tale", "speech-box": "tale-firkant", "thought": "tanke", "shout": "rop",
    "whisper": "hvisk", "caption": "boks", "sfx": "lyd", "free": "fri",
}

PRINT_STYLES = {
    "none": "ingen", "colour": "ingen", "color": "ingen",
    "bw-ink": "sorthvitt", "bw-screentone": "sorthvitt-raster",
    "greyscale": "gratone", "grayscale": "gratone", "four-color": "firefarge", "four-colour": "firefarge",
}

LAYOUTS = {
    "six-grid": "seksrute", "strips": "striper", "splash": "splash", "half-page-three": "halvside-tre",
    "column-three": "soyle-tre", "diagonal": "diagonal", "inset": "innfelt", "break-the-frame": "bryter-rammen",
    "zoom-steps": "zoom-trapp", "bleed-frameless": "utfallende-rammelos", "round": "rund",
    "nine-grid": "ni-rute", "three-columns": "tre-soyler", "montage": "montasje", "pause-panel": "pause-rute",
    "tilted": "skjevt",
    "spread-panorama": "oppslag-panorama", "spread-mirrored": "oppslag-speilet", "spread-splash": "oppslag-splash",
    "spread-diagonal": "oppslag-diagonal", "spread-release": "oppslag-utlosning", "spread-midfield": "oppslag-midtfelt",
    "spread-full": "oppslag-helt", "spread-monologue": "oppslag-stakitt", "spread-contrast": "oppslag-kontrast",
    "spread-two-worlds": "oppslag-to-verdener", "spread-strips-bang": "oppslag-strimler-smell",
}

TITLE_POSITIONS = {"top": "topp", "bottom": "bunn"}


def _value(key, v):
    if not isinstance(v, str):
        return v
    if key == "type":
        return TYPES.get(v, v)
    if key == "stilfilter":
        return PRINT_STYLES.get(v, v)
    if key == "oppsett":
        return LAYOUTS.get(v, v)
    if key == "tittel_plass":
        return TITLE_POSITIONS.get(v, v)
    if key == "hale" and v == "none":
        return "ingen"
    return v


def normalize(x):
    """Translate English keys/values to the internal names, recursively. Unknown keys are kept."""
    if isinstance(x, list):
        return [normalize(v) for v in x]
    if not isinstance(x, dict):
        return x
    out = {}
    for k, v in x.items():
        k2 = KEYS.get(k, k)
        out[k2] = _value(k2, normalize(v))
    return out


def print_style_name(v):
    return PRINT_STYLES.get(v, v) if v else v


def layout_name(v):
    return LAYOUTS.get(v, v)
