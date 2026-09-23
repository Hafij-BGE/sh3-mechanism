"""Markdown -> .docx (raw OOXML, standard library only).

    python3 tools/md2docx.py docs/REPORT.md SH3_thesis_report.docx "Report title"

Supports: # ## ### headings, paragraphs, - bullets, 1. numbered lists, > quotes,
| pipe | tables |, --- rules, and inline **bold**, *italic*, `code`, [text](url).
Page: A4, 2 cm margins, Times New Roman, page number in the footer.
"""
import datetime
import html
import os
import re
import struct
import sys
import zipfile

SZ = 22          # body text: half-points (22 = 11 pt)
SZ_TABLE = 18
CONTENT_W = 9638  # A4 minus 2 cm margins, in twips

# ── inline markup ────────────────────────────────────────────────────────────
TOK = re.compile(r'(\*\*.+?\*\*|(?<!\*)\*[^*]+?\*(?!\*)|`[^`]+?`|\[[^\]]+?\]\([^)]+?\))')


def esc(t):
    return html.escape(t, quote=False)


def runs(text, sz=SZ, bold=False, italic=False, color=None):
    out = []
    for part in TOK.split(text):
        if not part:
            continue
        b, i, mono, s = bold, italic, False, part
        if s.startswith('**') and s.endswith('**') and len(s) > 4:
            s, b = s[2:-2], True
        elif s.startswith('*') and s.endswith('*') and len(s) > 2:
            s, i = s[1:-1], True
        elif s.startswith('`') and s.endswith('`') and len(s) > 2:
            s, mono = s[1:-1], True
        elif s.startswith('['):
            m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', s)
            if m:
                s = m.group(1) if m.group(1) != m.group(2) else m.group(2)
        rpr = f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
        if mono:
            rpr += '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
        if b:
            rpr += '<w:b/>'
        if i:
            rpr += '<w:i/>'
        if color:
            rpr += f'<w:color w:val="{color}"/>'
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(s)}</w:t></w:r>')
    return ''.join(out)


def para(text='', sz=SZ, align=None, before=0, after=120, ind=0, hang=0, color=None,
         bold=False, italic=False, keep=False, style=None):
    ppr = '<w:pPr>'
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if keep:
        ppr += '<w:keepNext/>'
    if ind:
        ppr += f'<w:ind w:left="{ind}"' + (f' w:hanging="{hang}"' if hang else '') + '/>'
    ppr += f'<w:spacing w:before="{before}" w:after="{after}" w:line="300" w:lineRule="auto"/>'
    if align:
        ppr += f'<w:jc w:val="{align}"/>'
    ppr += '</w:pPr>'
    return f'<w:p>{ppr}{runs(text, sz, bold, italic, color)}</w:p>'


def heading(text, lvl):
    sz = {1: 30, 2: 26, 3: 23}[lvl]
    col = {1: '1B2F4E', 2: '22436B', 3: '33506F'}[lvl]
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading{lvl}"/><w:keepNext/>'
            f'<w:spacing w:before="{320 if lvl == 1 else 260}" w:after="{120 if lvl == 1 else 90}"'
            f' w:line="300" w:lineRule="auto"/></w:pPr>'
            f'<w:r><w:rPr><w:b/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/><w:color w:val="{col}"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>')


def table(rows):
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    span = [max(len(r[c]) for r in rows) + 4 for c in range(ncol)]
    widths = [max(700, int(CONTENT_W * s / sum(span))) for s in span]
    widths[-1] += CONTENT_W - sum(widths)
    borders = ('<w:tblBorders>' + ''.join(
        f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="C9D3DE"/>'
        for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV')) + '</w:tblBorders>')
    xml = [f'<w:tbl><w:tblPr><w:tblW w:w="{CONTENT_W}" w:type="dxa"/>{borders}'
           '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
           '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar>'
           '</w:tblPr><w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>']
    for ri, row in enumerate(rows):
        hdr = ri == 0
        cells = []
        for ci, cell in enumerate(row):
            shade = '<w:shd w:val="clear" w:fill="EDF2F7"/>' if hdr else ''
            body = ('<w:p><w:pPr><w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/></w:pPr>'
                    + runs(cell, SZ_TABLE, hdr) + '</w:p>')
            cells.append(f'<w:tc><w:tcPr><w:tcW w:w="{widths[ci]}" w:type="dxa"/>{shade}'
                         f'<w:vAlign w:val="center"/></w:tcPr>{body}</w:tc>')
        trpr = '<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' if hdr else '<w:trPr><w:cantSplit/></w:trPr>'
        xml.append(f'<w:tr>{trpr}{"".join(cells)}</w:tr>')
    xml.append('</w:tbl>' + para('', sz=10, after=100))
    return ''.join(xml)


IMAGES = []          # (relationship id, absolute path) in document order


def png_size(path):
    d = open(path, 'rb').read(33)
    return struct.unpack('>II', d[16:24])


def image(path, caption_text, base):
    full = os.path.normpath(os.path.join(base, path))
    if not os.path.exists(full):
        return para(f'[missing figure: {path}]', italic=True, color='C0392B')
    rid = f'rId{100 + len(IMAGES)}'
    IMAGES.append((rid, full))
    w, h = png_size(full)
    cw = int(CONTENT_W / 1440 * 914400)
    ch = int(cw * h / w)
    idx = len(IMAGES)
    pic = (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="160" w:after="60"/><w:jc w:val="center"/></w:pPr>'
           f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
           f'<wp:extent cx="{cw}" cy="{ch}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
           f'<wp:docPr id="{idx}" name="Figure {idx}"/><wp:cNvGraphicFramePr>'
           f'<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
           f'</wp:cNvGraphicFramePr>'
           f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
           f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
           f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
           f'<pic:nvPicPr><pic:cNvPr id="{idx}" name="Figure {idx}"/><pic:cNvPicPr/></pic:nvPicPr>'
           f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
           f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cw}" cy="{ch}"/></a:xfrm>'
           f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
           f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
    cap = para(caption_text, sz=SZ - 3, italic=True, color='44546A', after=200, align='center') if caption_text else ''
    return pic + cap


def rule():
    return ('<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="C9D3DE"/></w:pBdr>'
            '<w:spacing w:before="60" w:after="160"/></w:pPr></w:p>')


# ── markdown parsing ─────────────────────────────────────────────────────────
def split_row(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def convert(md, base='.'):
    body, i, lines = [], 0, md.split('\n')
    while i < len(lines):
        ln = lines[i].rstrip()
        s = ln.strip()
        if not s:
            i += 1
            continue
        if re.fullmatch(r'-{3,}|_{3,}|\*{3,}', s):
            body.append(rule()); i += 1; continue
        m = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', s)
        if m:
            body.append(image(m.group(2), m.group(1), base)); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            body.append(heading(m.group(2).strip(), min(3, len(m.group(1))))); i += 1; continue
        if s.startswith('|') and i + 1 < len(lines) and re.fullmatch(r'\|[\s:|-]+\|', lines[i + 1].strip()):
            rows = [split_row(s)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(split_row(lines[i])); i += 1
            body.append(table(rows)); continue
        if s.startswith('```'):
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                block.append(lines[i]); i += 1
            i += 1
            for b in block:
                body.append(para('`' + b.strip() + '`', sz=SZ - 2, ind=300, after=40))
            continue
        m = re.match(r'^(\s*)[-*+]\s+(.*)$', ln)
        if m:
            ind = 360 + 260 * (len(m.group(1)) // 2)
            body.append(para('• ' + m.group(2), ind=ind, hang=240, after=70)); i += 1; continue
        m = re.match(r'^(\s*)(\d+)\.\s+(.*)$', ln)
        if m:
            ind = 400 + 260 * (len(m.group(1)) // 2)
            body.append(para(f'{m.group(2)}. ' + m.group(3), ind=ind, hang=280, after=70)); i += 1; continue
        if s.startswith('>'):
            body.append(para(s.lstrip('> ').strip(), ind=360, italic=True, color='44546A', after=90))
            i += 1; continue
        chunk = [s]                                   # a paragraph: join wrapped lines
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r'^\s*(#|\||[-*+]\s|\d+\.\s|>|```|-{3,}$)', lines[i].strip()):
            chunk.append(lines[i].strip()); i += 1
        body.append(para(' '.join(chunk), align='both', after=140))
    return ''.join(body)


# ── package ──────────────────────────────────────────────────────────────────
def write_docx(out, body_xml, title, author='Hafijur Rahman'):
    sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rId9"/>'
            '<w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" '
            'w:header="567" w:footer="567" w:gutter="0"/></w:sectPr>')
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
           'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
           'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
           'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
           f'<w:body>{body_xml}{sect}</w:body></w:document>')
    footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
              '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
              '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
              '<w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:t>1</w:t></w:r>'
              '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:docDefaults><w:rPrDefault><w:rPr>'
              '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
              f'<w:sz w:val="{SZ}"/><w:szCs w:val="{SZ}"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault>'
              '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr>'
              '</w:pPrDefault></w:docDefaults>'
              '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
              + ''.join(
                  f'<w:style w:type="paragraph" w:styleId="Heading{i}"><w:name w:val="heading {i}"/>'
                  f'<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>'
                  f'<w:pPr><w:outlineLvl w:val="{i - 1}"/><w:keepNext/></w:pPr>'
                  f'<w:rPr><w:b/><w:sz w:val="{[30, 26, 23][i - 1]}"/></w:rPr></w:style>' for i in (1, 2, 3))
              + '</w:styles>')
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Default Extension="png" ContentType="image/png"/>'
          '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
          '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
          '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
          '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '</Relationships>')
    drels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
             '<Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
             + ''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                       f'Target="media/image{k + 1}.png"/>' for k, (rid, _) in enumerate(IMAGES))
             + '</Relationships>')
    now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f'<dc:title>{esc(title)}</dc:title><dc:creator>{esc(author)}</dc:creator>'
            f'<cp:lastModifiedBy>{esc(author)}</cp:lastModifiedBy>'
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct)
        z.writestr('_rels/.rels', rels)
        z.writestr('word/document.xml', doc)
        z.writestr('word/_rels/document.xml.rels', drels)
        z.writestr('word/styles.xml', styles)
        z.writestr('word/footer1.xml', footer)
        z.writestr('docProps/core.xml', core)
        for k, (_, path) in enumerate(IMAGES):
            z.write(path, f'word/media/image{k + 1}.png')


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else src
    md = open(src, encoding='utf-8').read()
    body = convert(md, os.path.dirname(os.path.abspath(src)))
    write_docx(out, body, title)
    print(f'wrote {out}')
