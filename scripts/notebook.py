#!/usr/bin/env python3
"""Build and check tabbed "digital notebook" decks in Google Slides.

Commands (each prints a compact JSON body for update_presentation, or a report):
  skeleton SPEC --revision REV [--deck READ.json]   template page + one divider per tab, all tabs linked
  pages    SPEC --section ID --count N --revision REV [--index N] [--start N] [--deck READ.json]
                                                     new content pages for a section (copies of the template);
                                                     --deck checks the template, divider and new IDs first
  check    SPEC READ.json                            report missing, broken or misdirected tabs, covered tabs,
                                                     hidden pages, contrast
  image    SPEC --page ID --url URL --id ID [--y IN] [--h IN] [--deck READ.json]
                                                     an image boxed inside the safe area (aspect ratio kept)

SPEC (JSON):
  {"prefix": "nb",                       # object-ID prefix, letters/digits/_ only
   "tabs": [{"id": "start", "label": "Getting started", "color": "#1565C0"}, ...],
   "font_size": 10, "strip": 0.45, "dividers": true}
Geometry comes from the deck's pageSize (pass --deck with a read that includes pageSize),
otherwise 7.5 x 10 in portrait is assumed.
"""
import argparse, json, re, sys

E = 914400

def emu(x): return int(round(x * E))
def hex6(h):
    h = h.strip().lstrip('#')
    if re.fullmatch(r'[0-9A-Fa-f]{3}', h): h = ''.join(c * 2 for c in h)
    if not re.fullmatch(r'[0-9A-Fa-f]{6}', h): sys.exit(f"color {h!r}: use #RRGGBB or #RGB")
    return '#' + h.upper()
def rgb(h):
    h = hex6(h).lstrip('#'); return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}
def lum(h):
    def ch(v): return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    c = rgb(h); return 0.2126 * ch(c['red']) + 0.7152 * ch(c['green']) + 0.0722 * ch(c['blue'])
def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
DARK, WHITE = '#1F2937', '#FFFFFF'
def text_on(fill): return WHITE if contrast(fill, WHITE) >= contrast(fill, DARK) else DARK

def load_spec(p):
    s = json.load(open(p))
    s.setdefault('prefix', 'nb'); s.setdefault('font_size', 10); s.setdefault('strip', 0.45); s.setdefault('dividers', True)
    # Slides object IDs: 5-50 chars, first a letter or _, then letters, digits, _ - :
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{1,19}', s['prefix']): sys.exit('prefix: 2-20 letters, digits or _, not starting with a digit')
    ids = [t['id'] for t in s['tabs']]
    if len(ids) != len(set(ids)): sys.exit('tab ids must be unique')
    for t in s['tabs']:
        if not re.fullmatch(r'[A-Za-z0-9_]{1,20}', t['id']): sys.exit(f"tab id {t['id']!r}: 1-20 letters, digits or _")
        # longest IDs made: <prefix>_div_<id>_title and <prefix>_<id>_<page>_t<k> (pages up to 999)
        if len(s['prefix']) + len(t['id']) + 11 > 50: sys.exit(f"prefix + tab id {t['id']!r} too long: keep them under 39 characters together (Slides IDs max 50)")
        t['color'] = hex6(t['color'])
    if len(s['tabs']) > 8: print(f"warning: {len(s['tabs'])} tabs; more than 8 get cramped", file=sys.stderr)
    return s

def page_size(deck):
    if deck:
        d = json.load(open(deck)); d = d.get('content', d); ps = d.get('pageSize')
        if ps: return ps['width']['magnitude'] / E, ps['height']['magnitude'] / E
    return 7.5, 10.0

def ids(s):
    P = s['prefix']
    return {"tpl": f"{P}_tpl", "div": lambda t: f"{P}_div_{t}", "tab": lambda page, k: f"{page}_t{k}"}

def tab_geom(s, W, H):
    n = len(s['tabs']); gap, margin = 0.04, 0.1
    L = (H - 2 * margin - (n - 1) * gap) / n
    return [(L, margin + k * (L + gap)) for k in range(n)]

def shape(oid, page, w, h, tf, kind="RECTANGLE"):
    return {"createShape": {"objectId": oid, "shapeType": kind, "elementProperties": {"pageObjectId": page,
            "size": {"width": {"magnitude": emu(w), "unit": "EMU"}, "height": {"magnitude": emu(h), "unit": "EMU"}},
            "transform": dict(tf, unit="EMU")}}}
def fill(oid, color, extra=None):
    sp = {"outline": {"propertyState": "NOT_RENDERED"}}; f = "outline.propertyState"
    if color: sp["shapeBackgroundFill"] = {"solidFill": {"color": {"rgbColor": rgb(color)}}}; f += ",shapeBackgroundFill.solidFill.color"
    if extra: sp.update(extra); f += "," + ",".join(extra)
    return {"updateShapeProperties": {"objectId": oid, "shapeProperties": sp, "fields": f}}
def text(oid, t, size, color, bold=True, align="CENTER"):
    return [{"insertText": {"objectId": oid, "text": t}},
            {"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "style": {"fontSize": {"magnitude": size, "unit": "PT"}, "bold": bold,
             "foregroundColor": {"opaqueColor": {"rgbColor": rgb(color)}}}, "fields": "fontSize,bold,foregroundColor"}},
            {"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "style": {"alignment": align}, "fields": "alignment"}}]
def link(oid, page): return {"updateShapeProperties": {"objectId": oid, "shapeProperties": {"link": {"pageObjectId": page}}, "fields": "link"}}
def nudge(oid): return {"updatePageElementTransform": {"objectId": oid, "applyMode": "RELATIVE",
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": -emu(0.1), "translateY": 0, "unit": "EMU"}}}

def body(reqs, rev):
    out = {"requests": reqs}
    if rev: out["writeControl"] = {"requiredRevisionId": rev}
    return json.dumps(out, separators=(',', ':'))

def cmd_skeleton(a):
    s = load_spec(a.spec); W, H = page_size(a.deck); I = ids(s); tpl = I['tpl']; T = s['strip']
    r = [{"createSlide": {"objectId": tpl, "slideLayoutReference": {"predefinedLayout": "BLANK"}}}]
    # 1. draw the strip on the template, unlinked (copies made while links point at missing pages get broken links)
    for k, ((L, y), t) in enumerate(zip(tab_geom(s, W, H), s['tabs'])):
        oid = I['tab'](tpl, k)
        # rotated 90 deg clockwise: base box is L long x (T+0.1) thick, pivot at its top-left -> occupies x in [W-T, W+0.1]
        r.append(shape(oid, tpl, L, T + 0.1, {"scaleX": 0, "scaleY": 0, "shearX": -1, "shearY": 1, "translateX": emu(W + 0.1), "translateY": emu(y)}, "ROUND_RECTANGLE"))
        r.append(fill(oid, t['color'], {"contentAlignment": "MIDDLE"}))
        r += text(oid, t['label'], s['font_size'], text_on(t['color']))
    # 2. dividers = copies of the template, so they carry the strip
    pages = [tpl]
    for t in reversed(s['tabs']):  # duplicates land right after the original; reverse keeps tab order
        d = I['div'](t['id'])
        m = {tpl: d}; m.update({I['tab'](tpl, k): I['tab'](d, k) for k in range(len(s['tabs']))})
        r.append({"duplicateObject": {"objectId": tpl, "objectIds": m}})
    divs = [I['div'](t['id']) for t in s['tabs']]; pages += divs
    # 3. link every tab on every page now that all dividers exist
    for p in pages:
        for k, t in enumerate(s['tabs']):
            r.append(link(I['tab'](p, k), I['div'](t['id'])))
    # 4. divider look: colored band + section name, and the active tab sticks out
    for k, t in enumerate(s['tabs']):
        d = divs[k]; r.append(nudge(I['tab'](d, k)))
        if s['dividers']:
            r.append(shape(f"{d}_band", d, W - T, 1.8, {"scaleX": 1, "scaleY": 1, "translateX": 0, "translateY": 0}))
            r.append(fill(f"{d}_band", t['color']))
            # behind the tabs, or it hides the active tab's protruding edge
            r.append({"updatePageElementsZOrder": {"pageElementObjectIds": [f"{d}_band"], "operation": "SEND_TO_BACK"}})
            r.append(shape(f"{d}_title", d, W - T - 1.0, 1.0, {"scaleX": 1, "scaleY": 1, "translateX": emu(0.5), "translateY": emu(0.4)}, "TEXT_BOX"))
            r += text(f"{d}_title", t['label'], 32, text_on(t['color']), align="START")
    # 5. dividers go after the cover; the template stays last and is skipped, so readers never see it
    r.append({"updateSlidesPosition": {"slideObjectIds": divs, "insertionIndex": a.index}})
    r.append({"updateSlideProperties": {"objectId": tpl, "slideProperties": {"isSkipped": True}, "fields": "isSkipped"}})
    print(body(r, a.revision))
    print(f"{len(r)} requests; template {tpl}; dividers {', '.join(divs)}; safe content area x 0.5..{W - T - 0.3:.2f} in", file=sys.stderr)

def cmd_pages(a):
    s = load_spec(a.spec); I = ids(s); tpl = I['tpl']
    tab_ids = [t['id'] for t in s['tabs']]
    if a.section not in tab_ids: sys.exit(f"section {a.section!r} is not a tab in the spec ({', '.join(tab_ids)})")
    k = tab_ids.index(a.section)
    if a.deck:
        # catch the usual failures here, with a clear message, instead of as a rejected batch
        d = json.load(open(a.deck)); d = d.get('content', d)
        have = {x['objectId'] for x in d.get('slides', [])}
        if not have: sys.exit("--deck: the read has no slides.objectId; read with revisionId,pageSize,slides.objectId")
        if tpl not in have: sys.exit(f"template {tpl} is not in the deck; run skeleton first (or check the spec's prefix)")
        if I['div'](a.section) not in have: print(f"warning: divider {I['div'](a.section)} is not in the deck", file=sys.stderr)
        taken = [f"{s['prefix']}_{a.section}_{a.start + i}" for i in range(a.count) if f"{s['prefix']}_{a.section}_{a.start + i}" in have]
        if taken:
            n = max(int(m.group(1)) for x in have if (m := re.fullmatch(rf"{re.escape(s['prefix'])}_{re.escape(a.section)}_(\d+)", x)))
            sys.exit(f"page IDs already in the deck: {', '.join(taken)}; use --start {n + 1}")
    r = []; new = []
    for i in reversed(range(a.count)):
        p = f"{s['prefix']}_{a.section}_{a.start + i}"; new.insert(0, p)
        m = {tpl: p}; m.update({I['tab'](tpl, j): I['tab'](p, j) for j in range(len(s['tabs']))})
        r.append({"duplicateObject": {"objectId": tpl, "objectIds": m}})
    r += [nudge(I['tab'](p, k)) for p in new]
    # copies of a skipped template are skipped too; un-skip them so readers see them
    r += [{"updateSlideProperties": {"objectId": p, "slideProperties": {"isSkipped": False}, "fields": "isSkipped"}} for p in new]
    if a.index is not None: r.append({"updateSlidesPosition": {"slideObjectIds": new, "insertionIndex": a.index}})
    print(body(r, a.revision)); print(f"new pages: {', '.join(new)}", file=sys.stderr)

def cmd_image(a):
    """createImage boxed inside the safe area; Slides scales the image to fit the box and keeps its aspect ratio."""
    s = load_spec(a.spec); W, H = page_size(a.deck); T = s['strip']
    x0, x1 = 0.5, W - T - 0.3                      # safe area, same as skeleton prints
    x = a.x if a.x is not None else x0
    w = min(a.w if a.w is not None else x1 - x, x1 - x)
    h = min(a.h if a.h is not None else H - a.y - 0.4, H - a.y - 0.4)
    if w <= 0 or h <= 0: sys.exit(f"no room: box would be {w:.2f} x {h:.2f} in at x {x}, y {a.y}")
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_\-:]{4,49}', a.id): sys.exit("--id: 5-50 characters, starting with a letter or _")
    r = [{"createImage": {"objectId": a.id, "url": a.url, "elementProperties": {"pageObjectId": a.page,
          "size": {"width": {"magnitude": emu(w), "unit": "EMU"}, "height": {"magnitude": emu(h), "unit": "EMU"}},
          "transform": {"scaleX": 1, "scaleY": 1, "translateX": emu(x), "translateY": emu(a.y), "unit": "EMU"}}}}]
    print(body(r, a.revision)); print(f"image {a.id} fits within x {x:.2f}..{x + w:.2f}, y {a.y:.2f}..{a.y + h:.2f} in", file=sys.stderr)

def affine(t):
    t = t or {}
    return (t.get('scaleX', 1), t.get('shearX', 0), t.get('translateX', 0), t.get('shearY', 0), t.get('scaleY', 1), t.get('translateY', 0))
def compose(g, c):  # g after c
    a, b, tx, d, e, ty = g; A, B, TX, D, E, TY = c
    return (a*A + b*D, a*B + b*E, a*TX + b*TY + tx, d*A + e*D, d*B + e*E, d*TX + e*TY + ty)
def bbox(el, parent=(1, 0, 0, 0, 1, 0)):
    """Page-space box (x0, y0, x1, y1) in inches. Handles rotation/shear, and groups (children are relative to the group)."""
    m = compose(parent, affine(el.get('transform')))
    kids = (el.get('elementGroup') or {}).get('children')
    if kids:
        bs = [bbox(k, m) for k in kids]; bs = [x for x in bs if x]
        return (min(x[0] for x in bs), min(x[1] for x in bs), max(x[2] for x in bs), max(x[3] for x in bs)) if bs else None
    sz = el.get('size') or {}
    w = (sz.get('width') or {}).get('magnitude', 0); h = (sz.get('height') or {}).get('magnitude', 0)
    if not w and not h: return None
    a, b, tx, d, e, ty = m
    xs = [a*x + b*y + tx for x, y in ((0, 0), (w, 0), (0, h), (w, h))]
    ys = [d*x + e*y + ty for x, y in ((0, 0), (w, 0), (0, h), (w, h))]
    return (min(xs) / E, min(ys) / E, max(xs) / E, max(ys) / E)
def overlap(p, q, tol=0.01):
    return p and q and p[0] < q[2] - tol and q[0] < p[2] - tol and p[1] < q[3] - tol and q[1] < p[3] - tol

def cmd_check(a):
    s = load_spec(a.spec); I = ids(s); d = json.load(open(a.read)); d = d.get('content', d)
    W = d['pageSize']['width']['magnitude'] / E; H = d['pageSize']['height']['magnitude'] / E
    divs = [I['div'](t['id']) for t in s['tabs']]; want = set(divs); slide_ids = [x['objectId'] for x in d['slides']]
    label = {I['div'](t['id']): t['label'] for t in s['tabs']}
    has_skip = any('slideProperties' in x for x in d['slides'])
    issues = []
    if W > H: issues.append(f"page is landscape ({W:.2f} x {H:.2f} in); notebooks read best portrait (File > Page setup)")
    for t in s['tabs']:
        c = contrast(t['color'], text_on(t['color']))
        if c < 4.5: issues.append(f"tab {t['label']!r}: label contrast {c:.1f}:1 is below 4.5:1")
        if I['div'](t['id']) not in slide_ids: issues.append(f"divider for {t['label']!r} is missing")
    for n, sl in enumerate(d['slides'], 1):
        sid = sl['objectId']; els = sl.get('pageElements', [])
        skipped = (sl.get('slideProperties') or {}).get('isSkipped', False)
        if sid == I['tpl']: continue  # the hidden template
        if skipped:  # hidden from readers: worth knowing, and its tabs don't matter
            issues.append(f"slide {n} ({sid}) is skipped, so readers won't see it"); continue
        # a tab: named <page>_t<k>, or (copied by hand, new IDs) a shape in the right-hand strip linking to a divider
        tabs = []
        for z, e in enumerate(els):
            lk = ((e.get('shape') or {}).get('shapeProperties') or {}).get('link', {}).get('pageObjectId')
            m = re.fullmatch(re.escape(sid) + r'_t(\d+)', e['objectId']); bb = bbox(e)
            if m or (lk in want and bb and bb[0] >= W - s['strip'] - 0.25):
                tabs.append({'z': z, 'id': e['objectId'], 'k': int(m.group(1)) if m else None, 'link': lk, 'bb': bb})
        if not tabs:
            if n > 1: issues.append(f"slide {n} ({sid}): no tab strip (made with New slide instead of Duplicate?)")
            continue
        by_y = sorted(tabs, key=lambda t: t['bb'][1] if t['bb'] else 0)
        for rank, t in enumerate(by_y):
            k = t['k'] if t['k'] is not None else rank
            exp = divs[k] if k < len(divs) else None
            if not t['link']: issues.append(f"slide {n}: tab {t['id']} has no link")
            elif t['link'] not in slide_ids: issues.append(f"slide {n}: tab {t['id']} links to missing page {t['link']}")
            elif exp and t['link'] != exp: issues.append(f"slide {n}: tab {t['id']} goes to {label.get(t['link'], t['link'])!r}, should go to {label[exp]!r}")
        missing = want - {t['link'] for t in tabs}
        if missing: issues.append(f"slide {n} ({sid}): missing tabs for {sorted(label[m] for m in missing)}")
        # only something drawn ON TOP of a tab blocks clicks; a background sent behind the strip is fine
        tab_ids = {t['id'] for t in tabs}; blockers = []
        for z, e in enumerate(els):
            if e['objectId'] in tab_ids: continue
            bb = bbox(e)
            if any(t['z'] < z and overlap(bb, t['bb']) for t in tabs): blockers.append(e['objectId'])
        if blockers: issues.append(f"slide {n}: {', '.join(blockers)} covers a tab (keep content left of x = {W - s['strip'] - 0.15:.2f} in, or send it to back)")
    if not has_skip: issues.append("note: the read had no slides.slideProperties.isSkipped, so hidden pages couldn't be told apart; add it to the mask")
    print("\n".join(issues) if issues else "OK: every page has a full, correctly linked tab strip and nothing covers it")

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = ap.add_subparsers(dest='cmd', required=True)
p = sub.add_parser('skeleton'); p.add_argument('spec'); p.add_argument('--revision'); p.add_argument('--deck'); p.add_argument('--index', type=int, default=1, help='where the first divider goes (default 1, after the cover)')
p = sub.add_parser('pages'); p.add_argument('spec'); p.add_argument('--section', required=True); p.add_argument('--count', type=int, default=1); p.add_argument('--start', type=int, default=1, help='first page number for IDs'); p.add_argument('--index', type=int, help='slide index for the new pages'); p.add_argument('--revision'); p.add_argument('--deck', help='a read with slides.objectId; checks the template, divider and new IDs before writing')
p = sub.add_parser('check'); p.add_argument('spec'); p.add_argument('read')
p = sub.add_parser('image'); p.add_argument('spec'); p.add_argument('--page', required=True, help='slide objectId'); p.add_argument('--url', required=True, help='public URL that returns the image itself')
p.add_argument('--id', required=True, help='objectId for the image'); p.add_argument('--y', type=float, default=1.4, help='top, in inches (default 1.4)')
p.add_argument('--x', type=float); p.add_argument('--w', type=float); p.add_argument('--h', type=float, help='max height, in inches (default: down to 0.4 in above the bottom)')
p.add_argument('--revision'); p.add_argument('--deck')
a = ap.parse_args(); {"skeleton": cmd_skeleton, "pages": cmd_pages, "check": cmd_check, "image": cmd_image}[a.cmd](a)
