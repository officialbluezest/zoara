# Zoara — Content Creation Engine

A real, working full-stack app: FastAPI + SQLite backend, vanilla JS/HTML/CSS
frontend, no mocked features. Persistent Brand Brain, real document parsing
(.docx/.pdf), real link reading, real live web research (Reddit/Quora/general
search via DuckDuckGo), and real content generation/critique via the
Anthropic API.

## What's real vs. what has honest limits

- **Persistence**: real. SQLite file (`backend/zoara.db`), survives restarts.
- **Strategy doc parsing**: real. `.docx`, `.pdf`, `.txt` are actually opened and read.
- **Competitor / inspiration link reading**: real, via oEmbed (YouTube, X,
  TikTok) and generic scraping (BeautifulSoup) for regular websites. Content
  behind a login wall (private posts, some Instagram content) can't be
  scraped anonymously — Zoara will tell you when that happens so you can
  paste the caption/transcript in manually instead.
- **Research**: real live search via DuckDuckGo (`ddgs` package, no API key
  needed), targeted at Reddit, Quora, and general query expansion, then
  synthesized into 30 ideas by Claude. Facebook Group content is mostly
  walled off from anonymous access, so that source is best-effort.
- **Generation & critique**: real calls to the Anthropic API. Requires your
  own `ANTHROPIC_API_KEY`.

## 1. Requirements

- Python 3.10+
- An Anthropic API key: https://console.anthropic.com/settings/keys

## 2. Setup

```bash
cd zoara/backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# open .env and paste in your ANTHROPIC_API_KEY
```

## 3. Run it

```bash
# still inside zoara/backend, with the venv active
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** — that's the whole app, frontend and backend
on one port. Create a brand and go through the tabs; nothing else to start.

## 4. Get a link you can share with others (no deployment needed)

The simplest way to hand someone a real URL that hits your local server is
a tunnel. [ngrok](https://ngrok.com) is the standard tool for this:

```bash
# one-time setup
brew install ngrok        # or download from ngrok.com/download
ngrok config add-authtoken YOUR_TOKEN   # free account, from ngrok.com

# with Zoara already running on port 8000 in another terminal:
ngrok http 8000
```

ngrok will print a URL like `https://a1b2c3d4.ngrok-free.app` — send that to
anyone and they'll hit your local Zoara instance directly. Keep both the
`uvicorn` terminal and the `ngrok` terminal running while they're testing.

Two things worth knowing about this approach:
- Your machine has to stay on and connected — this is a tunnel to your
  laptop, not a hosted server. Fine for testing with a handful of people,
  not for a permanent public product.
- Everyone who uses the link shares the same SQLite database and the same
  brands. That's fine for a demo; for real multi-tenant use later you'd
  move to a hosted Postgres instance and add per-user auth (see the "Next
  steps to productionize" section below).

Alternative tunnels if you don't want ngrok: `cloudflared tunnel --url
http://localhost:8000` (Cloudflare, no account needed for quick tunnels) or
`lt --port 8000` (localtunnel, via `npm install -g localtunnel`).

## 5. Project structure

```
zoara/
  backend/
    main.py                 # FastAPI app entrypoint, mounts frontend + routers
    database.py              # SQLite schema + connection
    repo.py                  # all DB CRUD
    format_modules.py        # the 11 format blueprints (structure, length, dropdowns)
    platform_modules.py      # the 5+ platform playbooks
    strategy_questions.py    # the strategist-level discovery questionnaire
    knowledge_panel.py       # curated copywriting resources + writing standards
    services/
      doc_parser.py           # real .docx/.pdf extraction
      scraper.py               # real oEmbed + generic link reading
      research.py              # real live search + idea synthesis
      generator.py             # content generation / revision / repurposing prompts
      critique.py              # dual-perspective critique + scoring
      ai_client.py             # Anthropic API wrapper
    routers/                  # brand.py, inspo.py, research.py, content.py, meta.py
  frontend/
    index.html
    style.css                # yellow (#FFC72C) + dark navy (#0B1F3A) brand theme
    app.js                    # full SPA logic, no build step required
```

## 6. How the "conditioning" architecture works

Nothing is generated generically. Every generation/critique call merges:
`Format Module + Platform Module + Brand Brain (strategy, competitors,
inspiration patterns) + the approved research idea + build spec (length/
structure) + creative angle`. Change any one of those and the prompt Zoara
actually sends to Claude changes with it — that's what "reconditions the
output" means in practice; see `services/generator.py:build_generation_prompt`.

## 7. Next steps to productionize (when you're ready to actually sell this)

1. **Auth + multi-tenancy**: add user accounts, scope brands to a user/org,
   move from SQLite to Postgres.
2. **Real hosting**: deploy the backend (Render, Railway, Fly.io, or a VPS)
   instead of tunneling from your laptop; serve the frontend from the same
   host or a CDN.
3. **Background jobs**: move the research job off FastAPI's in-process
   `BackgroundTasks` and onto a real queue (e.g. Celery + Redis) once you
   have concurrent users.
4. **Rate limiting & cost control** on the Anthropic API calls per brand/user.
5. **Editable knowledge modules**: expose `format_modules.py` /
   `platform_modules.py` content through an admin UI instead of code edits,
   since platform norms drift and you'll want to update them without a
   deploy.
