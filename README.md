# Pickleball Playgroup 🏓

A Streamlit app for managing casual pickleball sessions. Check in who's here, generate fair doubles matchups with automatic rest rotation, and track scores — all backed by Google Sheets.

## Features

- **Player roster** — Add/remove players from the sidebar
- **Daily check-in** — Select who's present with a multiselect
- **Fair game generation** — Doubles matchups (2v2) with a guarantee that nobody plays more than 2 games in a row, and players who sat out are prioritized
- **Score tracking** — Record scores per game with fun reactions (blowouts, shutouts, nail-biters)
- **Game history** — Browse past days with the date picker
- **Password protection** — Simple password gate that persists for the day in the browser
- **Silly team names** — Every game gets random names like *The Dink Lords vs Dill With It*
- **Play count titles** — See who's the Court Monarch and who's a Professional Spectator

## Setup

### 1. Google Cloud service account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use an existing one)
3. Enable the **Google Sheets API**
4. Create a **Service Account** under IAM & Admin
5. Create a JSON key for the service account and download it

### 2. Google Sheet

1. Create a new Google Sheet
2. Import `pickleball_seed.xlsx` (File > Import > Upload) — this creates the 3 required tabs with correct headers:
   - **Players** — pre-filled with default names
   - **Attendance** — empty (Date, Name)
   - **Games** — empty (Date, Game, Team A P1, Team A P2, Team B P1, Team B P2, Score A, Score B)
3. Share the sheet with your service account email (Editor access)

### 3. Configure secrets

Fill in `.streamlit/secrets.toml` with your credentials:

```toml
app_password = "YourPassword"

[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID"
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### 4. Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub (**without** `secrets.toml` — it's in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) and deploy from the repo
3. Add your secrets in the Streamlit Cloud dashboard under **Settings > Secrets**
4. The app uses Pacific Time (`America/Los_Angeles`) for dates regardless of server timezone

## Default players

Harrison, Alex, Sean, Alanna, David, Ken, Adel, Jan

Players can be added or removed from the sidebar at any time.
