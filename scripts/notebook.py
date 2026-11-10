#!/usr/bin/env python3
"""Build and check tabbed "digital notebook" decks in Google Slides.

Commands (each prints a compact JSON body for update_presentation, or a report):
  skeleton SPEC --revision REV [--deck READ.json]   template page + one divider per tab, all tabs linked
  pages    SPEC --section ID --count N --revision REV [--deck READ.json] [--after SLIDE_ID]
                                                     new content pages for a section (copies of the template)
  check    SPEC READ.json                            report missing/broken tabs, blocked strips, contrast

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
def rgb(h):
    h = h.lstrip('#'); return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}
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
    if not re.fullmatch(r'[A-Za-z0-9_]{2,20}', s['prefix']): sys.exit('prefix: 2-20 letters, digits or _')
    ids = [t['id'] for t in s['tabs']]
    if len(ids) != len(set(ids)): sys.exit('tab ids must be unique')
    for t in s['tabs']:
        if not re.fullmatch(r'[A-Za-z0-9_]{1,20}', t['id']): sys.exit(f"tab id {t['id']!r}: 1-20 letters, digits or _")
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
            r.append(shape(f"{d}_title", d, W - T - 1.0, 1.0, {"scaleX": 1, "scaleY": 1, "translateX": emu(0.5), "translateY": emu(0.4)}, "TEXT_BOX"))
            r += text(f"{d}_title", t['label'], 32, text_on(t['color']), align="START")
    # 5. dividers go after the cover; the template stays last and is skipped, so readers never see it
    r.append({"updateSlidesPosition": {"slideObjectIds": divs, "insertionIndex": a.index}})
    r.append({"updateSlideProperties": {"objectId": tpl, "slideProperties": {"isSkipped": True}, "fields": "isSkipped"}})
    print(body(r, a.revision))
    print(f"{len(r)} requests; template {tpl}; dividers {', '.join(divs)}; safe content area x 0.5..{W - T - 0.3:.2f} in", file=sys.stderr)

def cmd_pages(a):
    s = load_spec(a.spec); I = ids(s); tpl = I['tpl']
    k = [t['id'] for t in s['tabs']].index(a.section)
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

def cmd_check(a):
    s = load_spec(a.spec); I = ids(s); d = json.load(open(a.read)); d = d.get('content', d)
    W = d['pageSize']['width']['magnitude'] / E; H = d['pageSize']['height']['magnitude'] / E
    want = {I['div'](t['id']) for t in s['tabs']}; slide_ids = [x['objectId'] for x in d['slides']]
    issues = []
    if W > H: issues.append(f"page is landscape ({W:.2f} x {H:.2f} in); notebooks read best portrait (File > Page setup)")
    for t in s['tabs']:
        c = contrast(t['color'], text_on(t['color']))
        if c < 4.5: issues.append(f"tab {t['label']!r}: label contrast {c:.1f}:1 is below 4.5:1")
        if I['div'](t['id']) not in slide_ids: issues.append(f"divider for {t['label']!r} is missing")
    for n, sl in enumerate(d['slides'], 1):
        links, blockers = set(), []
        for e in sl.get('pageElements', []):
            lk = ((e.get('shape') or {}).get('shapeProperties') or {}).get('link', {}).get('pageObjectId')
            if lk in want or e['objectId'].startswith(sl['objectId'] + '_t'):
                if lk: links.add(lk)
                if lk and lk not in slide_ids: issues.append(f"slide {n}: tab {e['objectId']} links to missing page {lk}")
                continue
            tf = e.get('transform', {}); sz = e.get('size', {})
            w = sz.get('width', {}).get('magnitude', 0) * tf.get('scaleX', 1) / E
            x0 = tf.get('translateX', 0) / E
            if x0 + w > W - s['strip'] + 0.02 and x0 < W - 0.05:
                blockers.append(e['objectId'])
        missing = want - links
        if links and missing: issues.append(f"slide {n} ({sl['objectId']}): missing tabs for {sorted(missing)}")
        if sl['objectId'] == I['tpl']: continue
        if not links and n > 1: issues.append(f"slide {n} ({sl['objectId']}): no tab strip (made with New slide instead of Duplicate?)")
        if blockers and links: issues.append(f"slide {n}: {', '.join(blockers)} reaches into the tab strip (keep the right {s['strip']} in clear)")
    print("\n".join(issues) if issues else "OK: every page has a full, linked tab strip and nothing covers it")

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = ap.add_subparsers(dest='cmd', required=True)
p = sub.add_parser('skeleton'); p.add_argument('spec'); p.add_argument('--revision'); p.add_argument('--deck'); p.add_argument('--index', type=int, default=1, help='where the first divider goes (default 1, after the cover)')
p = sub.add_parser('pages'); p.add_argument('spec'); p.add_argument('--section', required=True); p.add_argument('--count', type=int, default=1); p.add_argument('--start', type=int, default=1, help='first page number for IDs'); p.add_argument('--index', type=int, help='slide index for the new pages'); p.add_argument('--revision'); p.add_argument('--deck')
p = sub.add_parser('check'); p.add_argument('spec'); p.add_argument('read')
a = ap.parse_args(); {"skeleton": cmd_skeleton, "pages": cmd_pages, "check": cmd_check}[a.cmd](a)
