import re

META = (r"(?:transcript|garbled|Garbled|see flags|See flags|not traced|not checked|unchecked|not verified|my reading|my guess|"
        r"my inference|transcribed|I have (?:kept|given|used|not (?:checked|traced|verified|tried)|identified|corrected|only)|"
        r"I did not (?:trace|check|reconstruct|try|verify|locate|examine)|I could not (?:confirm|trace|verify|locate)|"
        r"I take (?:it|this)|I took (?:it|this)|I read (?:it|this)|I matched|I identified|I corrected|I kept|I rendered|I treat|I give (?:it|them|the)|"
        r"claims in it are the speaker)")


def drop_meta_sentences(line):
    # split a bullet/paragraph into sentences; drop those that are pure working notes
    m = re.match(r'^(\s*(?:- )?)(.*)$', line)
    head, body = m.group(1), m.group(2)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"“(])', body)
    keep = [p for p in parts if not re.search(META, p)]
    if not keep:
        return None
    return head + ' '.join(keep)


def clean(md):
    out = []
    skip = False
    for ln in md.split('\n'):
        if ln.startswith('## Flags on the transcript text'):
            skip = True
        if skip:
            continue
        if ln.startswith('Source: https://aminikhaah.ir'):
            m = re.search(r'https://aminikhaah\.ir/song/\d+', ln)
            ln = ('Source: ' + (m.group(0) if m else 'aminikhaah.ir') +
                  ". This is a summary of the lecture, not a translation; claims in it are the speaker's own.")
            out.append(ln)
            continue
        out.append(ln)
    t = '\n'.join(out)
    t = re.sub(r'\s*\[\?\]', '', t)

    # editorial brackets: end with a period/question mark, or contain working-note words
    def rm(m):
        inner = m.group(0)[1:-1].strip()
        if inner.endswith('.') or inner.endswith('?') or re.search(META + r'|As he|As told|As given|Not traced|not explained', inner):
            return ''
        return m.group(0)

    t = re.sub(r'\s*\[[^\[\]]*\]', rm, t)
    # clause substitutions
    subs = [
        (r',? as the transcript (?:gives|has|renders|calls|spells|states|says) (?:it|them)?', ''),
        (r'\s*\((?:the )?transcript[^()]*\)', ''),
        (r',? in the transcript', ''),
        (r',? according to the transcript', ''),
        (r'\s+\(not his real name\)', ''),
    ]
    for a, b in subs:
        t = re.sub(a, b, t)
    lines = []
    for ln in t.split('\n'):
        if re.search(META, ln):
            r = drop_meta_sentences(ln) if ln.strip() and not ln.startswith('#') else ln
            if r is None:
                continue
            ln = r
        lines.append(ln)
    t = '\n'.join(lines)
    t = re.sub(r'[ \t]+\n', '\n', t)
    t = re.sub(r'  +', ' ', t)
    t = re.sub(r' ([,.;:])', r'\1', t)
    return t
