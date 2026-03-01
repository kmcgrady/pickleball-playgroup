# Pickleball Playgroup - Development Guide

## Project overview

A Streamlit app for managing casual pickleball playgroup sessions. Players check in, and the app generates fair doubles matchups (2v2) with automatic rest rotation. All data is persisted to Google Sheets.

**Single-file app:** Everything lives in `streamlit_app.py`. Do not split into multiple files or pages unless explicitly asked.

## Tech stack

- **Framework:** Streamlit
- **Data backend:** Google Sheets via `st-gsheets-connection` (service account auth)
- **Language:** Python 3.11+
- **Timezone:** All dates use `America/Los_Angeles` (Pacific Time) — never use `date.today()` directly

## Project structure

```
streamlit_app.py          # The entire app
requirements.txt          # Python dependencies (streamlit, st-gsheets-connection)
pickleball_seed.xlsx      # Seed spreadsheet for initial Google Sheet setup
.streamlit/
  config.toml             # Theme config (court-green + pickleball-yellow, light/dark)
  secrets.toml            # Password + Google service account credentials (NEVER commit)
.gitignore                # Excludes secrets.toml, __pycache__, .venv
```

## Google Sheets schema

Three worksheets in a single spreadsheet:

| Sheet | Columns | Purpose |
|-------|---------|---------|
| **Players** | `Name` | Player roster. Seeded with defaults on first run. |
| **Attendance** | `Date`, `Name` | One row per player per day. Written when "Generate next game" is clicked. |
| **Games** | `Date`, `Game`, `Team A P1`, `Team A P2`, `Team B P1`, `Team B P2`, `Score A`, `Score B` | One row per game. Scores are nullable (added after the game). |

**Date format:** ISO 8601 (`YYYY-MM-DD`), always stringified. All date comparisons use `.astype(str)` because Google Sheets may return dates as datetime objects.

## Key architecture decisions

### Authentication
- Simple password gate stored in `st.secrets["app_password"]`
- Daily auth token hashed from password + date, persisted in `st.query_params` so browser refreshes don't re-prompt for the day

### State management
- Google Sheets is the source of truth for all persistent data
- `st.session_state` is used for the player roster (to support `on_click` callbacks without `st.rerun()`)
- Reads are cached with `ttl=300` (5 minutes) to avoid Google Sheets API rate limits (60 reads/min)
- `st.cache_data.clear()` is called after every write to bust the cache
- Avoid `st.rerun()` — only used for password gate and closing `@st.dialog` modals (the only way to dismiss them)

### Game generation algorithm
- Picks 4 players for doubles
- **Hard rule:** Nobody plays more than 2 games in a row (players in both of the last 2 games must sit)
- **Soft preference:** Players who sat out last game are prioritized
- Attendance is auto-saved when generating a game

### Date handling
- `VIEW_DATE` (from sidebar date picker) controls which day's games/attendance are displayed
- `TODAY` is always Pacific Time, used for check-in, game generation, and auth tokens
- When viewing today: full UI (check-in, generate, scores, delete)
- When viewing past dates: read-only attendance + games with score editing

## Conventions

### Streamlit patterns
- Use `on_click` callbacks instead of `st.rerun()` for button actions where possible
- Use `@st.dialog` for confirmation flows (delete game, reset all games)
- Date picker renders in a separate `with st.sidebar:` block before data loading so `VIEW_DATE` is available
- Roster management uses a second `with st.sidebar:` block after data loading

### Fun / personality
- The app has a playful tone — silly team names, puns, reactions
- Team names are seeded by `date + game_number` via `random.Random()` so they're stable across refreshes
- Daily greeting is seeded by `TODAY` so it stays consistent all day
- Score reactions are context-aware (blowout, close game, shutout, tie)
- Player titles in the play count section (Court Monarch, Iron Pickler, Professional Spectator, etc.)
- Keep the fun — don't strip it out during refactors

### Theme
- Custom pickleball theme in `.streamlit/config.toml` with both light and dark modes
- Court green primary, pickleball yellow accents
- Inter body font, Outfit heading font, pill-shaped buttons
- Do not use `st.markdown` with `unsafe_allow_html=True` for styling — use config.toml

## Common tasks

### Adding a new Google Sheet column
1. Add the column name to `GAME_COLS` (or the relevant column list)
2. Add a fallback in the data loading section (like the `Score A`/`Score B` pattern)
3. Update `pickleball_seed.xlsx` generation
4. Update writes to include the new column

### Modifying the game algorithm
- The algorithm is in `generate_next_game()` — it takes present players and game history
- `must_sit` enforces the 2-game-in-a-row max
- `sat_last` / `still_eligible` handles fair rotation
- Always shuffle before selecting to keep things random

### Running locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
