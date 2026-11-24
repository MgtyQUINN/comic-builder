#!/usr/bin/env python3
"""Gi et panelbilde et ensartet trykkpreg, så alle rutene i serien ser like ut.

Styles (internal names; build_comic.py also accepts the English names in brackets):
  sorthvitt        [bw-ink]          pure ink, black and white only
  sorthvitt-raster [bw-screentone]   ink + mechanical dot screen for the greys
  gratone          [greyscale]       ink and wash: smooth greys, lines strengthened
  firefarge        [four-color]      classic four-colour print on newsprint

Norwegian notes below:
Stiler:
  sorthvitt        rent blekk: bare svart og hvitt, konturer forsterket (avisstripe / eventyrserie)
  sorthvitt-raster som sorthvitt, men gråtoner blir svarte rasterprikker
  firefarge        klassisk amerikansk firefargetrykk: flate farger i trinn (0/25/50/100 %),
                   rasterprikker i cyan/magenta/gul med hver sin vinkel, svart konturblekk,
                   avispapir og litt forskjøvet fargetrykk

Bruk (vanligvis kalt fra bygg_serie.py):
  .venv/bin/python stilfilter.py <inn> <ut> --stil firefarge [--periode PX]
                   [--panel-mm B H --zoom Z --raster-mm R] [--maks-px N]
--periode er avstanden mellom prikkene i px. Gis panelstørrelsen i stedet, regnes perioden ut
slik at prikkene blir R mm store på siden uansett zoom.
"""
import argparse
import math

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

PAPIR_AVIS = np.array([0.955, 0.925, 0.835])
PAPIR_HVIT = np.array([1.0, 1.0, 1.0])
BLEKK = np.array([0.09, 0.08, 0.08])


def til_arr(img):
    return np.asarray(img, dtype=np.float32) / 255.0


def blur(a, s):
    if s <= 0.3:
        return a
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return til_arr(im.filter(ImageFilter.GaussianBlur(s)))


def strekk(a, lav=2, hoy=98):
    p1, p2 = np.percentile(a, [lav, hoy])
    return np.clip((a - p1) / max(p2 - p1, 1e-3), 0, 1)


def skjerm(h, w, p, vinkel):
    """Terskelskjerm for runde rasterprikker (verdier 0–1). Blekk der mengde > skjerm."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    v = math.radians(vinkel)
    u = x * math.cos(v) + y * math.sin(v)
    t = -x * math.sin(v) + y * math.cos(v)
    return 0.5 + 0.25 * (np.cos(2 * np.pi * u / p) + np.cos(2 * np.pi * t / p))


def normaliser(rgb):
    """Løft mørke bilder (nattscener) så midttonen havner rundt 0,5 – ellers blir alt svart blekk."""
    L = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    lo, med, hi = np.percentile(L, [1, 50, 99.5])
    rgb = np.clip((rgb - lo) / max(hi - lo, 1e-3), 0, 1)
    med = np.clip((med - lo) / max(hi - lo, 1e-3), 0.02, 0.98)
    g = float(np.clip(math.log(0.5) / math.log(med), 0.55, 1.3))
    return rgb ** g


def konturer(L, p, styrke=1.0):
    """Mørk side av kantene (difference of Gaussians) → blekkstreker."""
    s = max(0.8, p * 0.28)
    dog = blur(L, s) - blur(L, s * 2.2)
    return dog < -0.035 / styrke


def rens(maske, storrelse=3):
    im = Image.fromarray((maske * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(storrelse))
    return np.asarray(im) > 127


def sorthvitt(rgb, p, raster):
    rgb = normaliser(rgb)
    L = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    L = strekk(blur(L, max(0.6, p * 0.12)))
    L = L ** 0.9
    a = 1 - L  # blekkmengde
    svart = a > max(0.70 if raster else 0.6, float(np.percentile(a, 72)))
    if raster:
        mid = (a > 0.22) & ~svart
        mengde = np.clip((a - 0.22) / 0.48, 0, 1) * 0.85
        svart |= mid & (mengde > skjerm(*a.shape, p, 45))
    svart = rens(svart, 3 if p < 10 else 5)
    svart |= konturer(L, p)
    ut = np.where(svart[..., None], BLEKK, PAPIR_HVIT)
    return ut


def gratone(rgb, p):
    """Ink-and-wash greyscale: smooth grey tones, ink lines strengthened, white paper."""
    rgb = normaliser(rgb)
    L = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    L = strekk(L, 1, 99.5)
    linjer = rens(konturer(strekk(blur(L, max(0.6, p * 0.12))), p, 0.8), 3)
    L = np.where(linjer, 0.08, L)
    return np.repeat(L[..., None], 3, axis=2) * PAPIR_HVIT


def firefarge(rgb, p):
    rgb = normaliser(rgb)
    im = Image.fromarray((rgb * 255).astype(np.uint8))
    im = ImageEnhance.Color(im).enhance(1.45)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = im.filter(ImageFilter.MedianFilter(5 if p < 12 else 7))
    a = blur(til_arr(im), max(0.6, p * 0.15))
    L = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    cmy = 1 - a
    k = cmy.min(axis=2)
    # svart blekk: dype skygger + konturer
    svart = rens(k > max(0.6, float(np.percentile(k, 85))), 5) | konturer(strekk(L), p, 1.1)
    # fjern grå komponent og kvantiser hver farge til 0/25/50/100 %
    rest = np.clip((cmy - k[..., None] * 0.85) / np.maximum(1 - k[..., None] * 0.85, 1e-3), 0, 1)
    trinn = np.array([0, 0.25, 0.5, 1.0], dtype=np.float32)
    q = trinn[np.abs(rest[..., None] - trinn).argmin(axis=-1)]
    h, w = L.shape
    blekk = []
    forskyv = max(1, int(round(p * 0.12)))  # litt forskjøvet fargetrykk
    for i, vinkel in enumerate((15, 75, 0)):  # C, M, Y
        sk = skjerm(h, w, p, vinkel)
        lag = (q[..., i] >= 0.99) | ((q[..., i] > 0.01) & (q[..., i] * 0.95 > sk))
        if i == 0:
            lag = np.roll(lag, forskyv, axis=1)
        elif i == 1:
            lag = np.roll(lag, -forskyv, axis=0)
        blekk.append(lag.astype(np.float32))
    C, M, Y = blekk
    ut = np.empty((h, w, 3), dtype=np.float32)
    ut[..., 0] = PAPIR_AVIS[0] * (1 - 0.93 * C)
    ut[..., 1] = PAPIR_AVIS[1] * (1 - 0.90 * M) * (1 - 0.18 * C) * (1 - 0.05 * Y)
    ut[..., 2] = PAPIR_AVIS[2] * (1 - 0.92 * Y) * (1 - 0.30 * M) * (1 - 0.05 * C)
    ut = np.where(svart[..., None], BLEKK, ut)
    return ut


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inn")
    ap.add_argument("ut")
    ap.add_argument("--stil", required=True, choices=["sorthvitt", "sorthvitt-raster", "firefarge", "gratone"])
    ap.add_argument("--periode", type=float)
    ap.add_argument("--panel-mm", nargs=2, type=float)
    ap.add_argument("--zoom", type=float, default=1.0)
    ap.add_argument("--raster-mm", type=float, default=0.55)
    ap.add_argument("--maks-px", type=int, default=0)
    a = ap.parse_args()

    im = Image.open(a.inn).convert("RGB")
    maks = int(a.maks_px * max(a.zoom, 1.0)) if a.maks_px else 0  # zoomet panel trenger flere px
    if maks and max(im.size) > maks:
        im.thumbnail((maks, maks), Image.LANCZOS)
    iw, ih = im.size
    if a.periode:
        p = a.periode
    elif a.panel_mm:
        bw, bh = a.panel_mm
        mm_per_px = max(bw / iw, bh / ih) * max(a.zoom, 0.01)  # object-fit: cover, og zoom gjør hver px større på siden
        p = a.raster_mm / mm_per_px
    else:
        p = iw / 180
    p = max(3.0, p)
    rgb = til_arr(im)
    if a.stil == "firefarge":
        ut = firefarge(rgb, p)
    elif a.stil == "gratone":
        ut = gratone(rgb, p)
    else:
        ut = sorthvitt(rgb, p, raster=a.stil == "sorthvitt-raster")
    bilde = Image.fromarray(np.clip(ut * 255, 0, 255).astype(np.uint8))
    if a.ut.lower().endswith(".png") and a.stil != "gratone":
        # Trykkstilene har bare et titall faste farger: palett-PNG blir skarp og liten (ingen JPEG-støy i prikkene)
        bilde = bilde.quantize(colors=2 if a.stil == "sorthvitt" else 24, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        bilde.save(a.ut, optimize=True)
    else:
        bilde.save(a.ut, quality=86)
    print(f"{a.ut}  periode {p:.1f} px")


if __name__ == "__main__":
    main()
