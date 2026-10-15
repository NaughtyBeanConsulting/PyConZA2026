# Now Ship It: PyCon ZA 2026

Slides for *"It works on my machine. Now ship it."*, a 30-minute talk on deploying a Python
web app to any Ubuntu server. Built with [reveal.js](https://revealjs.com) 5.2.1.

Everything is in this folder, including reveal.js and the fonts, so the deck works with no
internet connection.

## Presenting

The speaker-notes window needs the deck served over HTTP rather than opened as a file:

```bash
cd slide_show
python3 -m http.server 8000
```

Then open http://localhost:8000. For a quick look, double-clicking `index.html` also works.

| Key | Action |
| --- | --- |
| `S` | Speaker view: notes, timer, next slide |
| `F` | Fullscreen |
| `Esc` / `O` | Overview of all slides |
| `B` or `.` | Black out the screen |
| `Alt`+click (`Ctrl`+click on Linux) | Zoom into a screenshot |
| `→` / `Space` | Next step (many slides reveal in steps) |

Each slide's notes start with a time cue such as `[12:50 → 13:50]`, so you can see in the
speaker view whether you're ahead or behind.

## Running order (30 min)

| Time | Section |
| --- | --- |
| 0:00 – 7:00 | The problem, the big idea, the ten building blocks, one request's journey |
| 7:00 – 10:35 | Part 1: the demo app, dev vs prod settings, secrets in the environment |
| 10:35 – 22:30 | Part 2: ten stops from a fresh VM to a live site (route bar at the top) |
| 22:30 – 25:00 | The museum of real errors from building the talk |
| 25:00 – 28:30 | CI/CD, background workers, the checklist |
| 28:30 – 30:00 | Thanks and questions |

## Files

```
index.html        the slides and speaker notes
css/theme.css     the visual theme (original design)
js/deck.js        draws the route bar on slides marked data-stop, starts reveal.js
img/              screenshots (WebP) and the repo QR code
vendor/           reveal.js 5.2.1 (MIT) and fonts via Fontsource (SIL OFL 1.1)
```

## About the screenshots

They come from the talk notes in Obsidian. Before they were added here, private details were
covered with solid boxes: the server's public IP, the aaPanel login and URL, the database
password and an email address. The originals were not modified. If you add new
screenshots, check them for the same things, because this folder is part of a public repository.

aaPanel screenshots show aaPanel's own website and interface.
