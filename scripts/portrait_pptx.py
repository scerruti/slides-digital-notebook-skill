#!/usr/bin/env python3
"""Write a one-slide, blank .pptx with a custom page size (default 7.5 x 10 in portrait),
using only the standard library. Upload it with Drive create_file (contentMimeType
application/vnd.openxmlformats-officedocument.presentationml.presentation, base64Content =
the --b64 file's contents) and Drive converts it to a Google Slides deck of that size.

  python portrait_pptx.py OUT.pptx [--width 7.5] [--height 10] [--b64 OUT.b64]
"""
import argparse, base64, zipfile
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("out"); ap.add_argument("--width", type=float, default=7.5); ap.add_argument("--height", type=float, default=10.0)
ap.add_argument("--b64", help="also write the file base64-encoded here, ready for base64Content")
a = ap.parse_args()
PW, PH = int(round(a.width * 914400)), int(round(a.height * 914400))
A='xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
R='xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
P='xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
H='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
RT='http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
def rels(*rs): return H+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{i}" Type="{t}" Target="{g}"/>' for i,t,g in rs)+'</Relationships>'
CT='application/vnd.openxmlformats-officedocument.'
tree='<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>'
sf='<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
ln='<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
cs=''.join(f'<a:{n}><a:srgbClr val="{v}"/></a:{n}>' for n,v in [('dk1','000000'),('lt1','FFFFFF'),('dk2','1F2937'),('lt2','EEEEEE'),('accent1','1565C0'),('accent2','EF6C00'),('accent3','2E7D32'),('accent4','6A1B9A'),('accent5','00838F'),('accent6','C62828'),('hlink','1565C0'),('folHlink','6A1B9A')])
theme=H+f'<a:theme {A} name="T"><a:themeElements><a:clrScheme name="T">{cs}</a:clrScheme><a:fontScheme name="T"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="T"><a:fillStyleLst>{sf*3}</a:fillStyleLst><a:lnStyleLst>{ln*3}</a:lnStyleLst><a:effectStyleLst>{"<a:effectStyle><a:effectLst/></a:effectStyle>"*3}</a:effectStyleLst><a:bgFillStyleLst>{sf*3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
files={
'[Content_Types].xml':H+'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'+''.join(f'<Override PartName="{p}" ContentType="{CT}{t}"/>' for p,t in [('/ppt/presentation.xml','presentationml.presentation.main+xml'),('/ppt/slideMasters/slideMaster1.xml','presentationml.slideMaster+xml'),('/ppt/slideLayouts/slideLayout1.xml','presentationml.slideLayout+xml'),('/ppt/slides/slide1.xml','presentationml.slide+xml'),('/ppt/theme/theme1.xml','theme+xml')])+'</Types>',
'_rels/.rels':rels(('rId1',RT+'officeDocument','ppt/presentation.xml')),
'ppt/presentation.xml':H+f'<p:presentation {A} {R} {P}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst><p:sldId id="256" r:id="rId3"/></p:sldIdLst><p:sldSz cx="{PW}" cy="{PH}"/><p:notesSz cx="{PW}" cy="{PH}"/></p:presentation>',
'ppt/_rels/presentation.xml.rels':rels(('rId1',RT+'slideMaster','slideMasters/slideMaster1.xml'),('rId2',RT+'theme','theme/theme1.xml'),('rId3',RT+'slide','slides/slide1.xml')),
'ppt/slideMasters/slideMaster1.xml':H+f'<p:sldMaster {A} {R} {P}>{tree}<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>',
'ppt/slideMasters/_rels/slideMaster1.xml.rels':rels(('rId1',RT+'slideLayout','../slideLayouts/slideLayout1.xml'),('rId2',RT+'theme','../theme/theme1.xml')),
'ppt/slideLayouts/slideLayout1.xml':H+f'<p:sldLayout {A} {R} {P} type="blank">{tree.replace("<p:cSld>","<p:cSld name=\"Blank\">")}<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>',
'ppt/slideLayouts/_rels/slideLayout1.xml.rels':rels(('rId1',RT+'slideMaster','../slideMasters/slideMaster1.xml')),
'ppt/slides/slide1.xml':H+f'<p:sld {A} {R} {P}>{tree}<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>',
'ppt/slides/_rels/slide1.xml.rels':rels(('rId1',RT+'slideLayout','../slideLayouts/slideLayout1.xml')),
'ppt/theme/theme1.xml':theme}
with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for k, v in files.items(): z.writestr(k, v)
if a.b64:
    open(a.b64, "w").write(base64.b64encode(open(a.out, "rb").read()).decode())
print(f"{a.out}: {a.width} x {a.height} in, {len(open(a.out,'rb').read())} bytes")
