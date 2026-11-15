# Beyond Death: the lectures of Ḥujjat al-Islām Muṣṭafā Amīnīkhāh

**Site: https://beyond-death.pages.dev/**

In early 2019 Muṣṭafā Amīnīkhāh began a series of lectures for university students on *Ān sūy-e marg* ("Beyond Death"), a Persian book of three near-death accounts. Over thirty-nine sessions he read the accounts and set them against the Qurʾān, the sayings of the Imams and the philosophy of Mullā Ṣadrā. Two question-and-answer sessions followed in 2020.

This repository is the source of the site that gathers the whole series: 41 sessions, each with the audio, an English summary and the Persian transcript. The speaker's own website is [aminikhaah.ir](https://aminikhaah.ir/). Three short pages give the context: the speaker, a review of the research on near-death experiences in Iran, and a synthesis of his reading of them.

## What is here

| Path | Contents |
| --- | --- |
| `index.html`, `about.html`, `nde-iran.html`, `position.html`, `notes.html` | The home page, the speaker, NDEs in Iran, his reading of NDEs, and sources |
| `sessions/` | One page per session (`01.html` to `41.html`) and the session list |
| `transcripts/` | The Persian transcript of each session as plain text |
| `audio/` | The audio of each session, compressed (mono Opus, 24 kbps; about 196 MB in total) |
| `downloads/` | Each English summary as a Word file |
| `assets/` | Stylesheet, fonts (EB Garamond, Amiri, Noto Naskh Arabic) and the portrait |
| `tools/` | The build script, page templates and style sources |

The published files at the top level are generated. Edit the templates in `tools/pages/` and `tools/style.css`, not the generated HTML.

## Deployment

Cloudflare Pages serves the repository root and redeploys on every push to `main`. There is no build step on the server.

## Rebuilding the pages

```
pip install python-docx
python tools/build.py
```

The script reads the raw transcripts and the session summaries from a folder named `AminikhahDurus` next to this repository. Set `BEYOND_DEATH_SRC` to use another location. That source folder is not part of this repository, so a full rebuild needs it. Template and style changes can be tested by opening the generated pages in a browser.

## Credits and copyright

The lectures, their audio and the Persian transcripts are © Ḥujjat al-Islām Muṣṭafā Amīnīkhāh and [aminikhaah.ir](https://aminikhaah.ir/), and are shown here with credit to make the series easier to study. The English summaries, the essays on the speaker and on near-death experiences in Iran, the arrangement of the material and the site design are © 2026 Abdullah Ansar.

The transcripts are the source site's automatic transcriptions and contain mishearings and gaps. The English summaries are not translations: they follow each lecture, were prepared with AI assistance and were checked against the Persian text. Qurʾān verses are given in the Sahih International translation. Arabic and Persian names and terms are transliterated.

If the speaker or his site would like anything changed or removed, please open an issue on this repository.
