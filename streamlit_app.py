import hashlib
import random
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Pickleball playgroup",
    page_icon=":material/sports_tennis:",
)

# --- Password gate (token persists in URL for the day) ---
_TODAY_STR = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
_DAILY_TOKEN = hashlib.sha256(
    f"{st.secrets['app_password']}:{_TODAY_STR}".encode()
).hexdigest()[:16]

if st.query_params.get("token") == _DAILY_TOKEN:
    st.session_state.authenticated = True

if not st.session_state.get("authenticated"):
    st.title(":material/sports_tennis: Pickleball playgroup")
    pwd = st.text_input("Enter password", type="password")
    if pwd:
        if pwd == st.secrets["app_password"]:
            st.session_state.authenticated = True
            st.query_params["token"] = _DAILY_TOKEN
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# --- Constants ---
PLAYERS_PER_GAME = 4
TODAY = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
DEFAULT_PLAYERS = ["Harrison", "Alex", "Sean", "Alanna", "David", "Ken", "Adel", "Jan"]
GAME_COLS = ["Date", "Game", "Team A P1", "Team A P2", "Team B P1", "Team B P2", "Score A", "Score B"]

# --- Google Sheets helpers ---
conn = st.connection("gsheets", type=GSheetsConnection)


def read_sheet(worksheet, columns):
    """Read a worksheet. Returns empty DF with given columns on any failure."""
    try:
        df = conn.read(worksheet=worksheet, ttl=300)
        if df is None or df.empty:
            return pd.DataFrame(columns=columns)
        df = df.dropna(how="all")
        return df
    except Exception:
        return pd.DataFrame(columns=columns)


def write_sheet(worksheet, df):
    """Write a DF to a worksheet, creating it if it doesn't exist yet."""
    try:
        conn.update(worksheet=worksheet, data=df)
    except Exception:
        conn.create(worksheet=worksheet, data=df)
    st.cache_data.clear()


# --- Sidebar: date picker (rendered early so VIEW_DATE is available) ---
with st.sidebar:
    st.header("View games", divider=True)
    view_date = st.date_input("Date", value=datetime.now(ZoneInfo("America/Los_Angeles")).date())
    VIEW_DATE = view_date.isoformat()
    viewing_today = VIEW_DATE == TODAY

# --- Load data from sheets ---
players_df = read_sheet("Players", ["Name"])
st.session_state.setdefault("players", [])
st.session_state.players = players_df["Name"].dropna().astype(str).tolist()

# Seed defaults on first run
if not st.session_state.players:
    st.session_state.players = list(DEFAULT_PLAYERS)
    write_sheet("Players", pd.DataFrame({"Name": st.session_state.players}))

attendance_df = read_sheet("Attendance", ["Date", "Name"])
if not attendance_df.empty:
    dates = attendance_df["Date"].astype(str)
    today_attendance = attendance_df[dates == TODAY]["Name"].tolist()
    viewed_attendance = attendance_df[dates == VIEW_DATE]["Name"].tolist()
else:
    today_attendance = []
    viewed_attendance = []

games_df = read_sheet("Games", GAME_COLS)
# Ensure score columns exist for older sheets
for col in ("Score A", "Score B"):
    if col not in games_df.columns:
        games_df[col] = pd.NA


def _parse_schedule(df, target_date):
    """Build schedule list and max game number for a given date string."""
    if df.empty or "Date" not in df.columns:
        return [], 0
    day_df = df[df["Date"].astype(str) == str(target_date)].sort_values("Game")
    sched = []
    for _, row in day_df.iterrows():
        sched.append({
            "number": int(row["Game"]),
            "team_a": [str(row["Team A P1"]), str(row["Team A P2"])],
            "team_b": [str(row["Team B P1"]), str(row["Team B P2"])],
            "players": [
                str(row["Team A P1"]),
                str(row["Team A P2"]),
                str(row["Team B P1"]),
                str(row["Team B P2"]),
            ],
            "score_a": row.get("Score A"),
            "score_b": row.get("Score B"),
        })
    g_num = int(day_df["Game"].max()) if not day_df.empty else 0
    return sched, g_num


schedule, game_number = _parse_schedule(games_df, VIEW_DATE)
if not viewing_today:
    today_schedule, today_game_number = _parse_schedule(games_df, TODAY)
else:
    today_schedule, today_game_number = schedule, game_number


# --- Callbacks ---
def _on_add_player():
    name = st.session_state.get("new_player_input", "").strip()
    if not name or name in st.session_state.players:
        return
    st.session_state.players.append(name)
    write_sheet("Players", pd.DataFrame({"Name": st.session_state.players}))


def _on_remove_player():
    name = st.session_state.get("remove_player_select")
    if name and name in st.session_state.players:
        st.session_state.players.remove(name)
        write_sheet("Players", pd.DataFrame({"Name": st.session_state.players}))


# --- Sidebar: roster management ---
with st.sidebar:
    st.header("Roster", divider=True)

    st.text_input("Add a player", placeholder="Name", key="new_player_input")
    st.button("Add", icon=":material/person_add:", use_container_width=True, on_click=_on_add_player)

    if st.session_state.players:
        st.caption(f"{len(st.session_state.players)} players in roster")
        st.selectbox(
            "Remove a player",
            options=st.session_state.players,
            index=None,
            placeholder="Select to remove…",
            key="remove_player_select",
        )
        st.button("Remove", icon=":material/person_remove:", use_container_width=True, on_click=_on_remove_player)

# --- Main area ---
st.title(":material/sports_tennis: Pickleball playgroup")

# --- Check-in ---
present = []

if viewing_today:
    st.subheader("Who's here today?")

    default = today_attendance if today_attendance else list(st.session_state.players)
    present = st.multiselect(
        "Select players",
        options=st.session_state.players,
        default=default,
        label_visibility="collapsed",
    )
else:
    st.subheader(f"Attendance — {view_date:%B %-d, %Y}")
    if viewed_attendance:
        st.write(", ".join(viewed_attendance))
    else:
        st.caption("No attendance recorded for this date.")

    if len(present) < PLAYERS_PER_GAME:
        st.info(
            f"Need at least {PLAYERS_PER_GAME} players checked in to generate games.",
            icon=":material/group:",
        )


def _save_attendance():
    """Persist today's check-in to the Attendance sheet."""
    other_days = (
        attendance_df[attendance_df["Date"].astype(str) != TODAY]
        if not attendance_df.empty
        else pd.DataFrame(columns=["Date", "Name"])
    )
    today_rows = pd.DataFrame({"Date": [TODAY] * len(present), "Name": present})
    write_sheet("Attendance", pd.concat([other_days, today_rows], ignore_index=True))


# --- Algorithm ---
def generate_next_game(present_players: list[str], history: list[dict]) -> dict | None:
    """Pick 4 players for the next game ensuring nobody plays more than 2 in a row."""
    if len(present_players) < PLAYERS_PER_GAME:
        return None

    # Determine who MUST sit (played last 2 consecutive games)
    must_sit: set[str] = set()
    if len(history) >= 2:
        last_two = [set(g["players"]) for g in history[-2:]]
        must_sit = last_two[0] & last_two[1]

    eligible = [p for p in present_players if p not in must_sit]
    if len(eligible) < PLAYERS_PER_GAME:
        eligible = list(present_players)

    # Prioritise players who sat out last game
    if history:
        last_played = set(history[-1]["players"])
        sat_last = [p for p in eligible if p not in last_played]
        still_eligible = [p for p in eligible if p in last_played]
    else:
        sat_last = []
        still_eligible = eligible

    selected: list[str] = []
    random.shuffle(sat_last)
    random.shuffle(still_eligible)

    for p in sat_last:
        if len(selected) < PLAYERS_PER_GAME:
            selected.append(p)
    for p in still_eligible:
        if len(selected) < PLAYERS_PER_GAME:
            selected.append(p)

    random.shuffle(selected)
    return {"players": selected, "team_a": selected[:2], "team_b": selected[2:4]}


# --- Generate games ---
if viewing_today:
    st.subheader("Games")
else:
    st.subheader(f"Games — {view_date:%B %-d, %Y}")

if viewing_today and st.button(
    "Generate next game",
    icon=":material/casino:",
    type="primary",
    disabled=len(present) < PLAYERS_PER_GAME,
):
    _save_attendance()
    game = generate_next_game(present, today_schedule)
    if game:
        today_game_number += 1
        game["number"] = today_game_number

        new_row = pd.DataFrame(
            {
                "Date": [TODAY],
                "Game": [game["number"]],
                "Team A P1": [game["team_a"][0]],
                "Team A P2": [game["team_a"][1]],
                "Team B P1": [game["team_b"][0]],
                "Team B P2": [game["team_b"][1]],
                "Score A": [pd.NA],
                "Score B": [pd.NA],
            }
        )
        games_df_updated = pd.concat([games_df, new_row], ignore_index=True)
        write_sheet("Games", games_df_updated)
        # Update in-memory state so the rest of the script renders the new game
        # today_schedule and schedule are the same list when viewing_today
        today_schedule.append(game)
        if not viewing_today:
            schedule.append(game)


def _save_games_df(updated):
    """Persist an updated games DataFrame."""
    write_sheet("Games", updated)


def _delete_game(game_num):
    """Remove a single game from the sheet by game number + viewed date."""
    mask = (games_df["Date"].astype(str) == VIEW_DATE) & (games_df["Game"] == game_num)
    _save_games_df(games_df[~mask].reset_index(drop=True))


def _update_score(game_num, score_a, score_b):
    """Write scores for a specific game."""
    mask = (games_df["Date"].astype(str) == VIEW_DATE) & (games_df["Game"] == game_num)
    games_df.loc[mask, "Score A"] = score_a
    games_df.loc[mask, "Score B"] = score_b
    _save_games_df(games_df)


# --- Confirmation dialogs (st.rerun is the only way to close a dialog) ---
@st.dialog("Delete game")
def confirm_delete_game(game_num):
    st.write(f"Are you sure you want to delete **Game {game_num}**?")
    st.caption("This cannot be undone.")
    col_cancel, col_confirm = st.columns(2)
    if col_cancel.button("Cancel", use_container_width=True):
        st.rerun()
    if col_confirm.button("Yes, delete", type="primary", use_container_width=True):
        _delete_game(game_num)
        st.rerun()


@st.dialog("Reset all games")
def confirm_reset_all():
    st.write(f"Are you sure you want to delete **all {len(schedule)} games** for **{VIEW_DATE}**?")
    st.caption("This cannot be undone.")
    col_cancel, col_confirm = st.columns(2)
    if col_cancel.button("Cancel", use_container_width=True, key="reset_cancel"):
        st.rerun()
    if col_confirm.button("Yes, reset all", type="primary", use_container_width=True, key="reset_confirm"):
        remaining = (
            games_df[games_df["Date"].astype(str) != VIEW_DATE]
            if not games_df.empty
            else pd.DataFrame(columns=GAME_COLS)
        )
        _save_games_df(remaining)
        st.rerun()


if schedule and st.button("Reset games for this day", icon=":material/restart_alt:"):
    confirm_reset_all()

# --- Display schedule ---
if schedule:
    for game in reversed(schedule):
        with st.container(border=True):
            header_col, delete_col = st.columns([5, 1], vertical_alignment="center")
            header_col.markdown(f"**Game {game['number']}**")
            if delete_col.button(
                ":material/delete:",
                key=f"del_{game['number']}",
                help="Delete this game",
            ):
                confirm_delete_game(game["number"])

            col1, col2 = st.columns(2)
            col1.metric("Team A", " & ".join(game["team_a"]))
            col2.metric("Team B", " & ".join(game["team_b"]))

            # --- Score inputs ---
            score_a_val = game["score_a"] if pd.notna(game.get("score_a")) else None
            score_b_val = game["score_b"] if pd.notna(game.get("score_b")) else None

            s1, s2, s_btn = st.columns([2, 2, 1], vertical_alignment="bottom")
            new_score_a = s1.number_input(
                "Team A score",
                min_value=0,
                max_value=99,
                value=int(score_a_val) if score_a_val is not None else 0,
                key=f"score_a_{game['number']}",
            )
            new_score_b = s2.number_input(
                "Team B score",
                min_value=0,
                max_value=99,
                value=int(score_b_val) if score_b_val is not None else 0,
                key=f"score_b_{game['number']}",
            )
            if s_btn.button("Save", key=f"save_score_{game['number']}", use_container_width=True):
                _update_score(game["number"], new_score_a, new_score_b)
                st.toast(f"Score saved for Game {game['number']}!")

        if viewing_today and present:
            sitting = [p for p in present if p not in game["players"]]
            if sitting:
                st.caption(f":material/weekend: Sitting out: {', '.join(sitting)}")

    # --- Play tracker ---
    st.subheader("Play count")
    all_day_players = present if viewing_today else sorted({p for g in schedule for p in g["players"]})
    play_counts = {p: 0 for p in all_day_players}
    for game in schedule:
        for p in game["players"]:
            if p in play_counts:
                play_counts[p] += 1

    if play_counts:
        count_cols = st.columns(min(len(play_counts), 4))
        for i, (player, count) in enumerate(sorted(play_counts.items(), key=lambda x: -x[1])):
            count_cols[i % len(count_cols)].metric(player, f"{count} games")
else:
    st.caption("No games for today.")
