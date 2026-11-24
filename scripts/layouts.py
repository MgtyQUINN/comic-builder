"""Ferdige sideoppsett (rutegeometri i mm) for bygg_serie.py.

Bruk i serie.json:  {"oppsett": "diagonal", "paneler": [ {...}, {...}, ... ]}
Panelene fylles inn i rutene i leserekkefølge. Oppslag (navn som starter med «oppslag-»)
dekker to sider (venstre + høyre) og teller som to sidetall.

Hver rute er en dict:
  form  "poly" (p = punktliste) eller "sirkel" (cx, cy, r)
  kant  False = ingen ramme (utfallende / rammeløst bilde)
  hvit  hvit kant rundt (mm) – for innfelte ruter
  rot   rotasjon i grader rundt rc (mm)
  zoom, fokus, myk, mork  standardverdier panelet kan overstyre (mork 0–1 = mørkere bilde, for uttoning)
Koordinatene er mm fra øvre venstre hjørne av den skårne siden (oppslag: av venstre side).
Ruter som går ut til sidekanten forlenges med u (utfall).
"""

OPPSETT_INFO = {
    "seksrute": "Klassisk 2 × 3. Grunnrytmen: samtaler, ro.",
    "striper": "4 brede striper. Filmatisk, landskap, reise.",
    "splash": "Én rute over hele siden, utfallende. Åpning, vendepunkt, klimaks.",
    "halvside-tre": "Stor rute øverst + tre under. Etablering, så detaljer.",
    "soyle-tre": "Høy søyle til venstre + tre til høyre. Hel figur, fall, høyde.",
    "diagonal": "Skrå skiller (4 ruter). Fart, slåsskamp, kaos.",
    "innfelt": "Stort bilde + to innfelte nærbilder (3 ruter).",
    "bryter-rammen": "Bred + stor + to små. Bruk «overlegg» for figuren som bryter ut (4 ruter).",
    "zoom-trapp": "Bred + fire som zoomer inn (zoom 1→3,6) + bred (6 ruter).",
    "utfallende-rammelos": "Utfallende topp + to ruter + rammeløs, myk bunn (4 ruter).",
    "rund": "To store + rund innfelling (minne, sikte, klokke) (3 ruter).",
    "ni-rute": "3 × 3. Tett takt, nedtelling, avhør.",
    "tre-soyler": "Tre høye søyler + bred bunn. Samtidighet (4 ruter).",
    "montasje": "Utfallende bakgrunn + fire skjeve småbilder (5 ruter).",
    "pause-rute": "Bred + stor + liten taus rute + bred (4 ruter).",
    "skjevt": "Hele rutenettet heller −4°. Uro, panikk (4 ruter).",
    "oppslag-panorama": "Panorama over begge sider + fire ruter under (5 ruter).",
    "oppslag-speilet": "Samme rutenett på begge sider: hun/han, før/etter (8 ruter).",
    "oppslag-splash": "Ett bilde over hele oppslaget + to innfellinger (3 ruter).",
    "oppslag-diagonal": "En diagonal gjennom begge sider (6 ruter).",
    "oppslag-utlosning": "Ni små til venstre, ett utfallende til høyre (10 ruter).",
    "oppslag-midtfelt": "Seks smale øverst, bredt midtfelt, fire nederst (11 ruter).",
    "oppslag-helt": "Ett eneste bilde over begge sider, ingen innfellinger. Stor scene, samme figur gjerne flere ganger (1 rute).",
    "oppslag-stakitt": "Monolog: bred topp, fire høye smale ansiktsruter, ekstremt nærbilde nederst – likt på begge sider (12 ruter).",
    "oppslag-kontrast": "Helsides splash til venstre mot tett side til høyre (7 ruter).",
    "oppslag-to-verdener": "To høye søyler (kropp / sinn) + to innfelte striper; høyre side ender i tre ruter som toner ut i svart (11 ruter).",
    "oppslag-strimler-smell": "Fem brede strimler til venstre (oppbygging), stort utfallende smell nederst til høyre (8 ruter).",
}


def _R(x, y, w, h, **o):
    return dict(form="poly", p=[(x, y), (x + w, y), (x + w, y + h), (x, y + h)], **o)


def _P(p, **o):
    return dict(form="poly", p=p, **o)


def _kol(x0, bredde, n, G):
    w = (bredde - (n - 1) * G) / n
    return [(x0 + i * (w + G), w) for i in range(n)]


def _lin(x, a, b):
    (x0, y0), (x1, y1) = a, b
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def er_oppslag(navn):
    return navn.startswith("oppslag-")


def hent(navn, W, H, M, G, u=0.0):
    """Returnerer liste med ruter for oppsettet. W, H = skåret side; M = marg; G = mellomrom; u = utfall."""
    X0, Y0, IW, IH = M, M, W - 2 * M, H - 2 * M
    X1, Y1 = X0 + IW, Y0 + IH
    c2, c3 = _kol(X0, IW, 2, G), _kol(X0, IW, 3, G)
    r3, r4 = _kol(Y0, IH, 3, G), _kol(Y0, IH, 4, G)
    g2 = G / 2

    if navn == "seksrute":
        return [_R(x, y, w, h) for (y, h) in r3 for (x, w) in c2]
    if navn == "striper":
        return [_R(X0, y, IW, h) for (y, h) in r4]
    if navn == "splash":
        return [_R(-u, -u, W + 2 * u, H + 2 * u, kant=False)]
    if navn == "halvside-tre":
        th = IH * .58
        return [_R(X0, Y0, IW, th)] + [_R(x, Y0 + th + G, w, IH - th - G) for (x, w) in c3]
    if navn == "soyle-tre":
        sw = IW * .48
        return [_R(X0, Y0, sw, IH)] + [_R(X0 + sw + G, y, IW - sw - G, h) for (y, h) in r3]
    if navn == "diagonal":
        a = ((X0, Y0 + .354 * IH), (X1, Y0 + .229 * IH))
        b = ((X0, Y0 + .679 * IH), (X1, Y0 + .554 * IH))
        st, sb = X0 + .533 * IW, X0 + .4 * IW
        return [
            _P([(X0, Y0), (X1, Y0), (X1, _lin(X1, *a) - g2), (X0, _lin(X0, *a) - g2)]),
            _P([(X0, _lin(X0, *a) + g2), (st - g2, _lin(st - g2, *a) + g2), (sb - g2, _lin(sb - g2, *b) - g2), (X0, _lin(X0, *b) - g2)]),
            _P([(st + g2, _lin(st + g2, *a) + g2), (X1, _lin(X1, *a) + g2), (X1, _lin(X1, *b) - g2), (sb + g2, _lin(sb + g2, *b) - g2)]),
            _P([(X0, _lin(X0, *b) + g2), (X1, _lin(X1, *b) + g2), (X1, Y1), (X0, Y1)])]
    if navn == "innfelt":
        return [_R(X0, Y0, IW, IH),
                _R(X0 + .053 * IW, Y0 + .033 * IH, .33 * IW, .19 * IH, hvit=1.6),
                _R(X0 + .56 * IW, Y0 + .658 * IH, .387 * IW, .308 * IH, hvit=1.6)]
    if navn == "bryter-rammen":
        h1, h2 = .258 * IH, .458 * IH
        y3 = Y0 + h1 + G + h2 + G
        return [_R(X0, Y0, IW, h1), _R(X0, Y0 + h1 + G, IW, h2)] + [_R(x, y3, w, Y1 - y3) for (x, w) in c2]
    if navn == "zoom-trapp":
        zt, zm = .29 * IH, .333 * IH
        zy = Y0 + zt + G
        return ([_R(X0, Y0, IW, zt)] +
                [_R(x, zy, w, zm, zoom=z) for (x, w), z in zip(_kol(X0, IW, 4, G), [1.0, 1.6, 2.4, 3.6])] +
                [_R(X0, zy + zm + G, IW, Y1 - zy - zm - G)])
    if navn == "utfallende-rammelos":
        ty = .415 * H
        ry, rh = ty + G, .275 * IH
        return ([_R(-u, -u, W + 2 * u, ty + u, kant=False)] + [_R(x, ry, w, rh) for (x, w) in c2] +
                [_R(X0, ry + rh + G, IW, Y1 - ry - rh - G, kant=False, myk=True)])
    if navn == "rund":
        rt = .483 * IH
        return [_R(X0, Y0, IW, rt), _R(X0, Y0 + rt + G, IW, IH - rt - G),
                dict(form="sirkel", cx=X0 + .733 * IW, cy=Y0 + .5 * IH, r=.22 * IW, hvit=2.0)]
    if navn == "ni-rute":
        return [_R(x, y, w, h) for (y, h) in r3 for (x, w) in c3]
    if navn == "tre-soyler":
        sh = .75 * IH
        return [_R(x, Y0, w, sh) for (x, w) in c3] + [_R(X0, Y0 + sh + G, IW, IH - sh - G)]
    if navn == "montasje":
        ut = [_R(-u, -u, W + 2 * u, H + 2 * u, kant=False)]
        for (x, y, w, h, r) in [(16, 18, 62, 48, -6), (92, 54, 62, 50, 5), (18, 150, 58, 52, 4), (90, 188, 64, 54, -5)]:
            x, w, y, h = x / 170 * W, w / 170 * W, y / 260 * H, h / 260 * H
            ut.append(_R(x, y, w, h, rot=r, rc=(x + w / 2, y + h / 2), hvit=2.0))
        return ut
    if navn == "pause-rute":
        p1, pb, ph = .3 * IH, .747 * IW, .367 * IH
        py = Y0 + p1 + G
        return [_R(X0, Y0, IW, p1), _R(X0, py, pb, ph),
                _R(X0 + pb + G, py + .108 * IH, IW - pb - G, .15 * IH),
                _R(X0, py + ph + G, IW, Y1 - py - ph - G)]
    if navn == "skjevt":
        t1, t2 = .292 * IH, .342 * IH
        ty2, ty3 = Y0 + t1 + G, Y0 + t1 + G + t2 + G
        ut = [_R(X0, Y0, IW, t1)] + [_R(x, ty2, w, t2) for (x, w) in c2] + [_R(X0, ty3, IW, Y1 - ty3)]
        for r in ut:
            r.update(rot=-4, rc=(W / 2, H / 2))
        return ut

    # ---- oppslag (to sider, 2W bredt; falsen ved x = W)
    VX0, HX0 = M, W + M
    SX0, SX1 = VX0, 2 * W - M
    SW = SX1 - SX0
    c2v, c2h = _kol(VX0, IW, 2, G), _kol(HX0, IW, 2, G)
    if navn == "oppslag-panorama":
        pt = .615 * H
        return [_R(-u, -u, 2 * W + 2 * u, pt + u, kant=False)] + [_R(x, pt + G, w, Y1 - pt - G) for (x, w) in c2v + c2h]
    if navn == "oppslag-speilet":
        t1, t2 = .292 * IH, .342 * IH
        ty2, ty3 = Y0 + t1 + G, Y0 + t1 + G + t2 + G
        ut = []
        for x0, c in [(VX0, c2v), (HX0, c2h)]:
            ut += [_R(x0, Y0, IW, t1)] + [_R(x, ty2, w, t2) for (x, w) in c] + [_R(x0, ty3, IW, Y1 - ty3)]
        return ut
    if navn == "oppslag-splash":
        return [_R(-u, -u, 2 * W + 2 * u, H + 2 * u, kant=False),
                _R(20 / 340 * 2 * W, 176 / 260 * H, 60 / 340 * 2 * W, 62 / 260 * H, hvit=1.6),
                _R(262 / 340 * 2 * W, 18 / 260 * H, 58 / 340 * 2 * W, 58 / 260 * H, hvit=1.6)]
    if navn == "oppslag-diagonal":
        d = ((SX0, Y0 + .208 * IH), (SX1, Y0 + .792 * IH))
        ov = [SX0, SX0 + .344 * SW, SX0 + .6875 * SW, SX1]
        ne = [SX0, SX0 + .3125 * SW, SX0 + .656 * SW, SX1]
        ut = []
        for i in range(3):
            a0, a1 = ov[i] + (g2 if i else 0), ov[i + 1] - (g2 if i < 2 else 0)
            ut.append(_P([(a0, Y0), (a1, Y0), (a1, _lin(a1, *d) - g2), (a0, _lin(a0, *d) - g2)]))
        for i in range(3):
            a0, a1 = ne[i] + (g2 if i else 0), ne[i + 1] - (g2 if i < 2 else 0)
            ut.append(_P([(a0, _lin(a0, *d) + g2), (a1, _lin(a1, *d) + g2), (a1, Y1), (a0, Y1)]))
        return ut
    if navn == "oppslag-utlosning":
        c3v = _kol(VX0, IW, 3, G)
        return [_R(x, y, w, h) for (y, h) in r3 for (x, w) in c3v] + [_R(W, -u, W + u, H + 2 * u, kant=False)]
    if navn == "oppslag-midtfelt":
        ft, fm = .208 * IH, .55 * IH
        my = Y0 + ft + G
        by = my + fm + G
        return ([_R(x, Y0, w, ft) for (x, w) in _kol(SX0, SW, 6, G)] + [_R(-u, my, 2 * W + 2 * u, fm, kant=False)] +
                [_R(x, by, w, Y1 - by) for (x, w) in _kol(SX0, SW, 4, G)])
    if navn == "oppslag-helt":
        return [_R(-u, -u, 2 * W + 2 * u, H + 2 * u, kant=False)]
    if navn == "oppslag-stakitt":
        t1, t2 = .24 * IH, .47 * IH
        ty2, ty3 = Y0 + t1 + G, Y0 + t1 + G + t2 + G
        ut = []
        for x0 in (VX0, HX0):
            ut += ([_R(x0, Y0, IW, t1)] + [_R(x, ty2, w, t2) for (x, w) in _kol(x0, IW, 4, G)] +
                   [_R(x0, ty3, IW, Y1 - ty3, zoom=2.2)])
        return ut
    if navn == "oppslag-kontrast":
        a, b = .25 * IH, .2 * IH
        ry = [Y0, Y0 + a + G, Y0 + a + b + 2 * G, Y0 + 2 * a + b + 3 * G]
        return ([_R(-u, -u, W + u, H + 2 * u, kant=False)] +
                [_R(x, ry[0], w, a) for (x, w) in c2h] + [_R(HX0, ry[1], IW, b)] +
                [_R(x, ry[2], w, a) for (x, w) in c2h] + [_R(HX0, ry[3], IW, Y1 - ry[3])])
    if navn == "oppslag-to-verdener":
        sx, sw, sh = VX0 + .05 * IW, .9 * IW, .1 * IH
        t1, t2 = .3 * IH, .25 * IH
        c3h = _kol(HX0, IW, 3, G)
        by = Y0 + t1 + t2 + 2 * G
        return ([_R(x, Y0, w, IH) for (x, w) in c2v] +
                [_R(sx, Y0 + .7 * IH, sw, sh, hvit=1.6), _R(sx, Y0 + .7 * IH + sh + 2.5 * G, sw, sh, hvit=1.6)] +
                [_R(x, Y0, w, t1) for (x, w) in c3h] + [_R(HX0, Y0 + t1 + G, IW, t2)] +
                [_R(x, by, w, Y1 - by, mork=m) for (x, w), m in zip(c3h, [0, .45, .85])])
    if navn == "oppslag-strimler-smell":
        r5 = _kol(Y0, IH, 5, G)
        th = .38 * IH
        bw = .64 * IW
        sy = Y0 + th + G
        return ([_R(VX0, y, IW, h) for (y, h) in r5] +
                [_R(HX0, Y0, bw, th), _R(HX0 + bw + G, Y0, IW - bw - G, th),
                 _R(W + G, sy, W - G + u, H - sy + u, kant=False)])
    raise KeyError(f"ukjent oppsett «{navn}». Finnes: {', '.join(OPPSETT_INFO)}")


def bbox(r):
    if r["form"] == "sirkel":
        return (r["cx"] - r["r"], r["cy"] - r["r"], 2 * r["r"], 2 * r["r"])
    xs, ys = [p[0] for p in r["p"]], [p[1] for p in r["p"]]
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
