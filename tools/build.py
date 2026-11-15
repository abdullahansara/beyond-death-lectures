import os, re, glob, html, shutil, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sanitize import clean, translit_html, translit_text
from docx import Document
from docx.shared import Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# folder holding the raw transcripts and summaries; override with the BEYOND_DEATH_SRC environment variable
SRC = os.environ.get('BEYOND_DEATH_SRC', os.path.join(os.path.dirname(ROOT), 'AminikhahDurus'))
E = html.escape


def read(p):
    return open(p, encoding='utf8').read()


def write(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf8', newline='\n').write(t)


def inline(t):
    t = E(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
    return t


def md2html(md):
    out = []
    stack = 0

    def close(to=0):
        nonlocal stack
        while stack > to:
            out.append('</ul>')
            stack -= 1

    for line in md.split('\n'):
        if not line.strip() or line.startswith('# ') or line.startswith('Source: '):
            continue
        if line.startswith('## '):
            close()
            out.append('<h3>%s</h3>' % inline(line[3:]))
            continue
        m = re.match(r'^(\s*)- (.*)', line)
        if m:
            lvl = len(m.group(1)) // 2 + 1
            while stack < lvl:
                out.append('<ul>')
                stack += 1
            close(lvl)
            out.append('<li>%s</li>' % inline(m.group(2)))
            continue
        close()
        out.append('<p>%s</p>' % inline(line))
    close()
    return '\n'.join(out)


def page(title, body, depth=0):
    p = '../' * depth
    return translit_html(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} | Beyond Death (Ān sūy-e marg)</title>
<link rel="stylesheet" href="{p}assets/style.css"></head>
<body><header><div class="wrap"><a class="brand" href="{p}index.html">Beyond Death <span>Ān sūy-e marg: the lectures of Hujjat al-Islam Aminikhah, with English summaries</span></a>
<nav><a href="{p}about.html">The speaker</a><a href="{p}nde-iran.html">NDEs in Iran</a><a href="{p}position.html">His reading of NDEs</a><a href="{p}sessions/index.html">Sessions</a><a href="{p}notes.html">About this site</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Lectures and Persian transcripts belong to their source (aminikhaah.ir) and are shown here for study, with credit. English summaries were prepared with AI assistance and reviewed against the Persian transcripts. <a href="{p}notes.html">About this site</a></div></footer></body></html>''')


def make_docx(md, dst):
    md = translit_text(md)
    d = Document()
    st = d.styles['Normal']
    st.font.name = 'Times New Roman'
    st.font.size = Pt(11)

    def runs(p, t):
        for part in re.split(r'(\*\*[^*]+\*\*)', t):
            if part.startswith('**') and part.endswith('**'):
                p.add_run(part[2:-2]).bold = True
            else:
                p.add_run(part.replace('*', ''))

    for line in md.split(chr(10)):
        if not line.strip():
            continue
        if line.startswith('# '):
            d.add_heading(line[2:], 0)
        elif line.startswith('## '):
            d.add_heading(line[3:], 1)
        else:
            m = re.match(r'^(\s*)- (.*)', line)
            if m:
                p = d.add_paragraph(style='List Bullet' if len(m.group(1)) < 2 else 'List Bullet 2')
                runs(p, m.group(2))
            else:
                runs(d.add_paragraph(), line)
    d.save(dst)


ses = []
for n in range(1, 42):
    raw = read(os.path.join(SRC, 'raw', '1_BeyondDeath', f'{n}.txt')).split('\n')
    pt = raw[0].replace('TITLE:', '').strip()
    pt = re.sub(r'\s*-\s*شرح و بررسی کتاب آن سوی مرگ\s*$', '', pt)
    body = [l for l in raw[5:] if l.strip()]
    md = clean(read(os.path.join(SRC, 'summaries', f'1_BeyondDeath_s{n:02d}_song{n}.md')))
    h1 = md.split('\n')[0]
    m = re.search(r'session \d+: (.*)$', h1)
    en = (m.group(1) if m else re.sub(r'^# ', '', h1)).strip().strip('"')
    if n == 40:
        en = 'Questions and answers, part 1'
    if n == 41:
        en = 'Questions and answers, part 2'
    docx = os.path.join(SRC, 'summaries', f'1_BeyondDeath_s{n:02d}_final.docx')
    assert os.path.exists(docx)
    ses.append(dict(n=n, pt=pt, en=en, body=body, md=md, docx=docx,
                    words=sum(len(l.split()) for l in body)))

write(os.path.join(ROOT, 'assets', 'style.css'), read(os.path.join(ROOT, 'tools', 'fonts.css')) + read(os.path.join(ROOT, 'tools', 'style.css')))
adir = os.path.join(ROOT, 'audio')
for s in ses:
    n = s['n']
    af = [f for f in ('opus', 'm4a', 'mp3', 'ogg') if os.path.exists(os.path.join(adir, f'{n:02d}.{f}'))]
    s['audio'] = f'{n:02d}.{af[0]}' if af else None
    os.makedirs(os.path.join(ROOT, 'downloads'), exist_ok=True)
    make_docx(s['md'], os.path.join(ROOT, 'downloads', f'session-{n:02d}-summary.docx'))
    write(os.path.join(ROOT, 'transcripts', f'{n:02d}.txt'),
          f"{s['pt']}\nhttps://aminikhaah.ir/song/{n}\n\n" + '\n\n'.join(s['body']))
    paras = ''.join('<p>%s</p>' % E(l) for l in s['body'])
    prev = f'<a href="{n-1:02d}.html">&larr; Session {n-1}</a>' if n > 1 else '<span></span>'
    nxt = f'<a href="{n+1:02d}.html">Session {n+1} &rarr;</a>' if n < 41 else '<span></span>'
    if s['audio']:
        au = (f'<audio controls preload="none" src="../audio/{s["audio"]}"></audio>'
              f'<p class="small">Original audio, re-encoded to a small file for the web. '
              f'<a href="https://aminikhaah.ir/song/{n}">Original page</a>.</p>')
    else:
        au = (f'<p class="small">Listen to this session at its <a href="https://aminikhaah.ir/song/{n}">source page</a>.</p>')
    body = f'''<div class="pn">{prev}{nxt}</div>
<h1>Session {n}: {E(s['en'])}</h1>
<p class="fa" dir="rtl" lang="fa">{E(s['pt'])}</p>
<h2>Audio</h2>{au}
<h2>Summary (English)</h2>
<div class="summary">{md2html(s['md'])}</div>
<p class="small"><a href="../downloads/session-{n:02d}-summary.docx">Download summary (.docx)</a></p>
<h2>Persian transcript</h2>
<p class="small">Automatic transcription from the source site; it may contain errors. <a href="../transcripts/{n:02d}.txt">Plain text</a>.</p>
<details><summary>Show the transcript ({s['words']:,} words)</summary><div class="fa" dir="rtl" lang="fa">{paras}</div></details>
<div class="pn">{prev}{nxt}</div>'''
    write(os.path.join(ROOT, 'sessions', f'{n:02d}.html'), page(f'Session {n}: {s["en"]}', body, 1))

groups = [('Story 1: the first narrator (Saḥar)', 1, 5), ('Story 2: the engineer', 6, 15),
          ('Story 3: the doctor', 16, 39), ('Questions and answers', 40, 41)]
rows = ''
for g, a, b in groups:
    rows += f'<h2>{g}</h2><table><tr><th>#</th><th>Session</th><th>Persian title</th><th>Audio</th></tr>'
    for s in ses[a - 1:b]:
        rows += (f'<tr><td>{s["n"]}</td><td><a href="{s["n"]:02d}.html">{E(s["en"])}</a></td>'
                 f'<td class="fa" dir="rtl" lang="fa">{E(s["pt"])}</td><td><a href="https://aminikhaah.ir/song/{s["n"]}">Listen</a></td></tr>')
    rows += '</table>'
write(os.path.join(ROOT, 'sessions', 'index.html'), page('Sessions',
      '<h1>The sessions</h1><p>Forty-one sessions on the book <em>Ān sūy-e marg</em> ("Beyond Death"), '
      'given to university students in Iran. Each page has an English summary and the Persian transcript, with a link to the audio on the speaker\'s site.</p>' + rows, 1))

for name, title in (('index', 'Home'), ('about', 'The speaker'), ('nde-iran', 'Near-death experiences in Iran'), ('position', 'A Sadrian reading of NDEs'), ('notes', 'About this site')):
    body = read(os.path.join(ROOT, 'tools', 'pages', name + '.html'))
    write(os.path.join(ROOT, name + '.html'), page(title, body))
write(os.path.join(ROOT, '.nojekyll'), '')
print('built', len(ses), 'sessions;', sum(1 for s in ses if s['audio']), 'with audio')
