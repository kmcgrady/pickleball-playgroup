import hashlib
import random
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Pickleball playgroup",
    page_icon="🥒",
)

# --- Password gate (token persists in URL for the day) ---
_TODAY_STR = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
_DAILY_TOKEN = hashlib.sha256(
    f"{st.secrets['app_password']}:{_TODAY_STR}".encode()
).hexdigest()[:16]

if st.query_params.get("token") == _DAILY_TOKEN:
    st.session_state.authenticated = True

if not st.session_state.get("authenticated"):
    st.markdown("# 🥒🏓")
    st.title("Pickleball playgroup")
    st.caption("*The court is calling. Enter the secret brine to proceed.*")
    pwd = st.text_input("Enter password", type="password", placeholder="Shhh...")
    if pwd:
        if pwd == st.secrets["app_password"]:
            st.session_state.authenticated = True
            st.query_params["token"] = _DAILY_TOKEN
            st.rerun()
        else:
            st.error("Wrong password! That's a kitchen violation. 🚫")
    st.stop()

# --- Constants ---
PLAYERS_PER_GAME = 4
TODAY = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
DEFAULT_PLAYERS = ["Harrison", "Alex", "Sean", "Alanna", "David", "Ken", "Adel", "Jan"]
GAME_COLS = ["Date", "Game", "Team A P1", "Team A P2", "Team B P1", "Team B P2", "Score A", "Score B"]

# --- Fun stuff ---
TEAM_NAMES_A = [
    "The Dink Lords", "Pickle Rockets", "Net Ninjas", "Kitchen Crashers",
    "Smash Pandas", "Lob Stars", "The Volley Llamas", "Brine Time",
    "Drop Shot Divas", "The Third Shots", "Paddle Patrol", "Brine & Punishment",
    "The Jar Starters", "Net Worth", "Dill or No Dill", "Pickle Palooza",
    "Court Destroyers", "The Vinegar Strokes", "Smash Mouth", "Lob City",
    "The Zesty Ones", "Full Send Picklers", "Dink Dynasty", "Pickle Militia",
    "The Cucumber Crushers", "Brine Force", "Net Positive", "The Spin Cycle",
    "Slam Dunk Dills", "The Overhead Smashers", "Gherkin Warriors", "Relish This",
    "The Pickle Pimps", "Ace Ventura", "Brined & Dangerous", "Dink Floyd",
    "The Volley Dollies", "Spicy Brine", "The Kitchen Sink", "Paddle Royale",
    "Dill Picklers United", "Court of Appeals", "Net Gain", "The Backhand Bandits",
    "Pickle My Fancy", "Drop It Like It's Hot", "Rally Royale", "The Brinestormers",
    "Sour Patch Kids", "Paddle Surfers", "The Erne Eagles", "Third Shot Thrillers",
    "Dink Tank", "Court Chaos", "Pickle Party", "The Net Setters",
    "Smash Bros", "The Topspin Tornados", "Brine Squad", "Side Out Syndicate",
    "The Lob Fathers", "Baseline Blazers", "Dill Seekers", "Paddle Phoenix",
    "The Score Settlers", "Kitchen Confidential", "Net Profits", "The Dinkasaurus",
    "Pickle Punchline", "Court Crushers", "Brine Before Swine", "Drop Zone",
    "The Overhead Ogres", "Lob Monsters", "Smash Academy", "The Pickle Press",
    "Dink Detectives", "Rally Rascals", "Court Voltage", "The Brine Bunch",
    "Pickle Storm", "Net Result", "The Spin Wizards", "Paddle Troopers",
    "Dill Thrill", "Baseline Bosses", "The Volley Vipers", "Smash Palace",
    "Brine Wave", "The Kitchen Crew", "Drop Shot Demons", "Court Supremacy",
    "Pickle Proof", "Net Gain Gang", "The Dink Mob", "Rally Runners",
    "Salty Smashers", "The Paddle Prophets", "Lob Legends", "Court Mavericks",
    "Brine Believers", "The Spin Sisters", "Pickle Perfection", "Net Crusaders",
    "Dink Masters", "Smash Potatoes", "The Overhead Express", "Drop & Roll",
    "Baseline Beasts", "The Volley Vandals", "Court Commanders", "Brine Bombers",
    "Pickle Protocol", "Rally Rebels", "The Dink Tanks", "Net Warriors",
    "Paddle Power", "Smash Collective", "The Kitchen Kings", "Drop Dead Gorgeous",
    "Lob Life", "Court Catalysts", "Brine Brothers", "The Spin Twins",
    "Pickle Pirates", "Net Navigators", "Dink Doctors", "Rally Rangers",
    "Smash Magnets", "The Paddle Pandas", "Baseline Breakers", "Court Coyotes",
    "Brine Bandits", "The Volley Veterans", "Pickle Platoon", "Drop Shot Dynasty",
    "Net Nomads", "The Dink Dragons", "Smash Society", "Rally Republic",
    "Paddle Patriots", "The Kitchen Wolves", "Court Cougars", "Brine Battalion",
    "Pickle Phalanx", "Lob Launchers", "Net Neutralizers", "The Spin Serpents",
    "Dink Disciples", "Smash Stampede", "Rally Renegades", "The Overhead Outlaws",
    "Baseline Bulldogs", "Court Corsairs", "Brine Blasters", "Paddle Pioneers",
    "Pickle Posse", "Drop Shot Dojo", "Net Nincompoops", "The Dink Demons",
    "Smash Syndicate", "The Volley Vortex", "Rally Rockets", "Court Cobras",
    "Brine Blitz", "The Kitchen Ninjas", "Pickle Phantoms", "Lob Lobsters",
    "Net Nerds", "Dink Daredevils", "Paddle Predators", "Smash Savages",
    "The Spin Storm", "Baseline Barracudas", "Court Cyclones", "Brine Bears",
    "Rally Raptors", "Pickle Pranksters", "Drop Shot Daredevils", "Net Nuggets",
    "The Overhead Orchestra", "Dink Dominators", "Smash Surge", "Paddle Punks",
    "Court Cannons", "Brine Bruisers", "The Volley Vikings", "Pickle Prowlers",
    "Rally Rampage", "Net Nighthawks", "The Kitchen Krakens", "Lob Lynx",
    "Dink Dynamos", "Baseline Brawlers", "Smash Spectrum", "Court Centurions",
    "Brine Blazers", "Paddle Phantoms", "Pickle Paragons", "The Spin Sharks",
]
TEAM_NAMES_B = [
    "Dill With It", "Sweet Gherkins", "The Spin Doctors", "Court Jesters",
    "Pickle Poppers", "Baseline Bandits", "Rally Cats", "No Man's Land",
    "The Big Dills", "Ace Holes", "Half Sour Heroes", "The Cornichons",
    "Bread & Butter", "Vlasic Attack", "Dill-ightful", "Jarred & Loaded",
    "The Briny Deep", "Crunch Time", "The Pickleback", "Fermentation Station",
    "Deli Style", "The Spear Chuckers", "Garlic Dill Gang", "Pickle Backs",
    "Kosher Chaos", "The Salt Lickers", "Clutch Picklers", "Chip & Dip",
    "Snack Attack", "The Brine Rats", "Dill-icious", "The Gerkin Jerks",
    "Full Cornichon", "Zero Pickle Given", "The Dill Dozers", "Brine & Cheese",
    "The Jar Heads", "Sour Power", "The Tiny Gherks", "Claussen Clashers",
    "The Cucumber Cult", "Pickle Backs Forever", "Deli Counter Strike", "Brine & Grind",
    "The Relish Tray", "Half Sour Hour", "Dill Pill", "The Brine Tycoons",
    "Crunchy Bunch", "Jar Wars", "The Sour Scouts", "Ferment & Conquer",
    "Garlic Press Gang", "The Dill Dashers", "Kosher Knockout", "Brine & Shine",
    "The Salt Circle", "Pickle Pledge", "Cucumber Collective", "The Vinegar Vibe",
    "Spear Squad", "Dill Dilemma", "The Brine Line", "Chip Shot Champs",
    "Sour Surge", "The Jar Droppers", "Kosher Krew", "Gherkin Gangsters",
    "Claussen Crowd", "The Dill Reapers", "Brine or Bust", "Full Sour Force",
    "The Pickle Barrel", "Crunch Crew", "Cucumber Commandos", "Jar Juice",
    "Sour Kraut Cousins", "The Relish Rebels", "Dill Brigade", "Brine Runners",
    "The Salt Shakers", "Ferment Frenzy", "Garlic Guardians", "Pickle Pledge Crew",
    "Spear Spirits", "The Vinegar Vigilantes", "Kosher Kings", "Gherkin Gremlins",
    "Claussen Conspiracy", "Dill Dominion", "Brine Academy", "The Jar Jedis",
    "Sour Seekers", "Cucumber Cavalry", "Crunch Coalition", "The Pickle Path",
    "Full Sour Fury", "Deli Destroyers", "Brine Republic", "The Salt Saints",
    "Ferment Force", "Garlic Gladiators", "The Relish Regiment", "Dill Defiance",
    "Spear Strikers", "Pickle Precedent", "The Vinegar Vanguard", "Kosher Kabal",
    "Gherkin Guild", "Claussen Cartel", "Brine Regime", "The Jar Jackals",
    "Sour Syndicate", "Cucumber Corps", "Crunch Crusade", "The Dill Decree",
    "Full Sour Squadron", "Deli Division", "Pickle Parliament", "The Salt Sages",
    "Ferment Federation", "Garlic Gorillas", "Brine Bureau", "The Relish Realm",
    "Dill Directive", "Spear Sentinels", "The Vinegar Vault", "Kosher Knights",
    "Gherkin Ghosts", "Claussen Command", "Pickle Province", "The Jar Giants",
    "Sour Savants", "Cucumber Clan", "Crunch Council", "Brine Barracks",
    "The Dill Domain", "Full Sour Fleet", "Deli Dispatch", "The Salt Soldiers",
    "Ferment Faction", "Garlic Griffins", "Pickle Plaza", "The Relish Rovers",
    "Dill Dozen", "Brine Bastion", "Spear Specters", "The Vinegar Venture",
    "Kosher Komrades", "Gherkin Garrison", "Claussen Cohort", "Pickle Pinnacle",
    "The Jar Juggernauts", "Sour Society", "Cucumber Citadel", "Crunch Compact",
    "Brine Bunker", "The Dill Depot", "Full Sour Front", "Deli Defenders",
    "The Salt Sentries", "Ferment Frontier", "Garlic Gatekeepers", "Pickle Precinct",
    "The Relish Ring", "Dill Detachment", "Brine Bivouac", "Spear Spartans",
    "The Vinegar Victory", "Kosher Klan", "Gherkin Gurus", "Claussen Chapter",
    "Pickle Pavilion", "The Jar Jockeys", "Sour Stronghold", "Cucumber Compound",
    "Crunch Chamber", "Brine Blockade", "The Dill Den", "Full Sour Forum",
    "Deli Dragoons", "The Salt Siblings", "Ferment Fortress", "Garlic Generals",
    "Pickle Plateau", "The Relish Roundtable", "Dill Dynasty", "Brine Bulwark",
    "Spear Seraphs", "The Vinegar Vessel", "Kosher Keepers", "Gherkin Guardsmen",
    "Claussen Collective", "Pickle Pantheon", "The Jar Jesters", "Sour Summit",
    "Cucumber Conclave", "Crunch Citadel", "Brine Battleground", "The Dill Dojo",
]
GAME_ANNOUNCEMENTS = [
    "Let the dinking begin!",
    "May the best picklers win!",
    "Time to get briny!",
    "This one's gonna be a real pickle...",
    "Kitchen's open, let's cook!",
    "No lobs, no glory!",
    "Dink responsibly.",
    "Rally on, brave picklers!",
    "Third shot drop incoming!",
    "Let's get this bread... and butter pickle.",
]
SIT_OUT_MESSAGES = [
    "Hydrate and judge from the sidelines",
    "Time to heckle from the bench",
    "Enjoy the view, couch pickles",
    "Rest those pickle legs",
    "Scouting the competition (aka napping)",
    "Bench warmers assemble",
    "Strategic resting in progress",
    "Recharging dink energy",
]
SCORE_REACTIONS = {
    "blowout": ["Absolutely demolished!", "That wasn't even close!", "Call the pickle police!"],
    "close": ["What a nail-biter!", "Down to the wire!", "Heart rate: elevated."],
    "shutout": ["A SHUTOUT?! Ruthless.", "Bageled! Zero! Zip! Nada!", "Flawless victory."],
    "tie": ["A tie?! That's not how pickleball works!", "Everyone's a winner? Sure, Jan."],
}

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
    st.header("📅 View games", divider=True)
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
        g_num = int(row["Game"])
        # Stable random team names seeded by date + game number
        rng = random.Random(f"{target_date}-{g_num}")
        sched.append({
            "number": g_num,
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
            "team_a_name": rng.choice(TEAM_NAMES_A),
            "team_b_name": rng.choice(TEAM_NAMES_B),
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
    st.header("🧑‍🤝‍🧑 Roster", divider=True)

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
GREETINGS = [
    "It's dink o'clock!",
    "Ready to get pickled?",
    "No kitchen violations today!",
    "Paddles up, let's go!",
    "Time to relish the moment.",
    "Drop it like it's hot (shot).",
    "In a pickle? Good.",
    "Let's brine and grind!",
]
st.markdown("# 🥒🏓 Pickleball playgroup")
# Stable greeting per day
st.caption(f"*{random.Random(TODAY).choice(GREETINGS)}*")

# --- Check-in ---
present = []

if viewing_today:
    st.subheader("🙋 Who's here today?")

    default = today_attendance if today_attendance else list(st.session_state.players)
    present = st.multiselect(
        "Select players",
        options=st.session_state.players,
        default=default,
        label_visibility="collapsed",
    )
else:
    st.subheader(f"📋 Attendance — {view_date:%B %-d, %Y}")
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

    # Build weighted pool: weight based on total games sat today
    weighted_pool: list[str] = []
    if history:
        for p in eligible:
            games_sat = sum(1 for g in history if p not in g["players"])
            entries = 1 + games_sat  # 1 base + 1 per game sat
            for _ in range(entries):
                weighted_pool.append(p)
    else:
        weighted_pool = list(eligible)

    # Collect past partnerships and opponent matchups to diversify teams
    past_partners: set[frozenset[str]] = set()
    past_opponents: set[frozenset[str]] = set()
    for g in history:
        past_partners.add(frozenset(g["team_a"]))
        past_partners.add(frozenset(g["team_b"]))
        for a in g["team_a"]:
            for b in g["team_b"]:
                past_opponents.add(frozenset([a, b]))

    last_players = set(history[-1]["players"]) if history else set()

    # Try to pick players that aren't an exact repeat of last game
    best_selected: list[str] | None = None
    best_split: tuple[list[str], list[str]] | None = None
    best_repeat_score = float("inf")
    max_attempts = 1 if len(eligible) <= PLAYERS_PER_GAME else 20

    for _ in range(max_attempts):
        selected: list[str] = []
        random.shuffle(weighted_pool)
        for p in weighted_pool:
            if p not in selected and len(selected) < PLAYERS_PER_GAME:
                selected.append(p)

        # Skip exact repeat of last game's players (retry if possible)
        if set(selected) == last_players and best_selected is None:
            best_selected = selected
            best_split = (selected[:2], selected[2:4])
            continue

        # Find the team split with fewest repeat partnerships and opponents
        # 4 players have 3 possible splits into pairs
        splits = [
            (selected[:2], selected[2:4]),
            ([selected[0], selected[2]], [selected[1], selected[3]]),
            ([selected[0], selected[3]], [selected[1], selected[2]]),
        ]
        random.shuffle(splits)

        for team_a, team_b in splits:
            partner_repeats = sum(
                1 for pair in (frozenset(team_a), frozenset(team_b))
                if pair in past_partners
            )
            opponent_repeats = sum(
                1 for a in team_a for b in team_b
                if frozenset([a, b]) in past_opponents
            )
            # Partners weighted higher — playing with someone matters more than against
            repeat_score = partner_repeats * 2 + opponent_repeats
            if repeat_score < best_repeat_score:
                best_repeat_score = repeat_score
                best_selected = selected
                best_split = (team_a, team_b)

        if best_repeat_score == 0 and set(best_selected) != last_players:
            break  # found an ideal pick — no repeats, different players

    selected = best_selected
    team_a, team_b = best_split
    return {
        "players": selected,
        "team_a": team_a,
        "team_b": team_b,
        "team_a_name": random.choice(TEAM_NAMES_A),
        "team_b_name": random.choice(TEAM_NAMES_B),
        "announcement": random.choice(GAME_ANNOUNCEMENTS),
    }


# --- Generate games ---
if viewing_today:
    st.subheader("⚔️ Games")
else:
    st.subheader(f"⚔️ Games — {view_date:%B %-d, %Y}")

if viewing_today:
    with st.expander("How does matchmaking work?"):
        st.markdown(
            """
**Fair rotation** — Players who've sat out more games today are more likely to
be picked next. The more you sit, the higher your chances.

**No back-to-back-to-back** — If you've played the last 2 games in a row,
you're guaranteed a break (with 6+ players).

**Fresh teams** — The app tries to mix up partners *and* opponents so you're
not stuck with the same matchup all day.

**No exact repeats** — It avoids running the same 4 players twice in a row.

*With only 4–5 players, everyone plays nearly every game — there just
aren't enough people to rotate!*
"""
        )

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
        st.toast(f"🏓 {game['announcement']}")
        st.balloons()


def _save_games_df(updated):
    """Persist an updated games DataFrame."""
    write_sheet("Games", updated)


def _delete_game(game_num):
    """Remove a single game from the sheet by game number + viewed date."""
    mask = (games_df["Date"].astype(str) == VIEW_DATE) & (games_df["Game"] == game_num)
    _save_games_df(games_df[~mask].reset_index(drop=True))


def _update_game(game_num, ta_p1, ta_p2, tb_p1, tb_p2, score_a, score_b):
    """Write player names and scores for a specific game."""
    mask = (games_df["Date"].astype(str) == VIEW_DATE) & (games_df["Game"] == game_num)
    games_df.loc[mask, "Team A P1"] = ta_p1
    games_df.loc[mask, "Team A P2"] = ta_p2
    games_df.loc[mask, "Team B P1"] = tb_p1
    games_df.loc[mask, "Team B P2"] = tb_p2
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
        team_a_name = game.get("team_a_name", "Team A")
        team_b_name = game.get("team_b_name", "Team B")

        with st.container(border=True):
            header_col, delete_col = st.columns([5, 1], vertical_alignment="center")
            header_col.markdown(f"**🏓 Game {game['number']}** — *{team_a_name}* ⚡ *{team_b_name}*")
            if delete_col.button(
                ":material/delete:",
                key=f"del_{game['number']}",
                help="Delete this game",
            ):
                confirm_delete_game(game["number"])

            score_a_val = game["score_a"] if pd.notna(game.get("score_a")) else None
            score_b_val = game["score_b"] if pd.notna(game.get("score_b")) else None

            # Build player options, including any players in this game who may have left the roster
            player_options = list(st.session_state.players)
            for p in game["team_a"] + game["team_b"]:
                if p not in player_options:
                    player_options.append(p)

            def _pidx(name):
                try:
                    return player_options.index(name)
                except ValueError:
                    return 0

            with st.form(f"game_{game['number']}", border=False):
                a_col, b_col = st.columns(2)
                with a_col:
                    st.caption(f"**{team_a_name}**")
                    a1c, a2c = st.columns(2)
                    ta_p1 = a1c.selectbox(
                        "Team A P1",
                        options=player_options,
                        index=_pidx(game["team_a"][0]),
                        key=f"ta_p1_{game['number']}",
                        label_visibility="collapsed",
                    )
                    ta_p2 = a2c.selectbox(
                        "Team A P2",
                        options=player_options,
                        index=_pidx(game["team_a"][1]),
                        key=f"ta_p2_{game['number']}",
                        label_visibility="collapsed",
                    )
                with b_col:
                    st.caption(f"**{team_b_name}**")
                    b1c, b2c = st.columns(2)
                    tb_p1 = b1c.selectbox(
                        "Team B P1",
                        options=player_options,
                        index=_pidx(game["team_b"][0]),
                        key=f"tb_p1_{game['number']}",
                        label_visibility="collapsed",
                    )
                    tb_p2 = b2c.selectbox(
                        "Team B P2",
                        options=player_options,
                        index=_pidx(game["team_b"][1]),
                        key=f"tb_p2_{game['number']}",
                        label_visibility="collapsed",
                    )

                s1, s2 = st.columns(2)
                new_score_a = s1.number_input(
                    f"{team_a_name} score",
                    min_value=0,
                    max_value=99,
                    value=int(score_a_val) if score_a_val is not None else 0,
                    key=f"score_a_{game['number']}",
                )
                new_score_b = s2.number_input(
                    f"{team_b_name} score",
                    min_value=0,
                    max_value=99,
                    value=int(score_b_val) if score_b_val is not None else 0,
                    key=f"score_b_{game['number']}",
                )
                submitted = st.form_submit_button("Save", use_container_width=True)

            if submitted:
                _update_game(game["number"], ta_p1, ta_p2, tb_p1, tb_p2, new_score_a, new_score_b)
                a, b = new_score_a, new_score_b
                if a == b:
                    reaction = random.choice(SCORE_REACTIONS["tie"])
                elif a == 0 or b == 0:
                    reaction = random.choice(SCORE_REACTIONS["shutout"])
                elif abs(a - b) >= 6:
                    reaction = random.choice(SCORE_REACTIONS["blowout"])
                elif abs(a - b) <= 2:
                    reaction = random.choice(SCORE_REACTIONS["close"])
                else:
                    reaction = f"Game {game['number']} saved!"
                st.toast(f"🏓 {reaction}")

            # Show score verdict inline if both scores are recorded
            if score_a_val is not None and score_b_val is not None:
                sa, sb = int(score_a_val), int(score_b_val)
                if sa > sb:
                    st.caption(f"🏆 **{team_a_name}** win {sa}–{sb}")
                elif sb > sa:
                    st.caption(f"🏆 **{team_b_name}** win {sb}–{sa}")
                elif sa == sb and sa > 0:
                    st.caption(f"🤝 Tied {sa}–{sb} — *did someone forget to finish?*")

        if viewing_today and present:
            sitting = [p for p in present if p not in game["players"]]
            if sitting:
                sit_msg = random.Random(game["number"]).choice(SIT_OUT_MESSAGES)
                st.caption(f":material/weekend: {', '.join(sitting)} — *{sit_msg}*")

    # --- Play tracker ---
    st.subheader("📊 Play count")
    all_day_players = present if viewing_today else sorted({p for g in schedule for p in g["players"]})
    play_counts = {p: 0 for p in all_day_players}
    for game in schedule:
        for p in game["players"]:
            if p in play_counts:
                play_counts[p] += 1

    if play_counts:
        def _title(count, rank, total):
            if rank == 0:
                return "👑 Court Monarch"
            if count == 0:
                return "🪑 Professional Spectator"
            if rank == total - 1 and count > 0:
                return "🌱 Fresh Legs"
            if count >= 5:
                return "🔥 Iron Pickler"
            if count >= 3:
                return "💪 Warmed Up"
            return "🏓 Getting Started"

        sorted_players = sorted(play_counts.items(), key=lambda x: -x[1])
        count_cols = st.columns(min(len(sorted_players), 4))
        for i, (player, count) in enumerate(sorted_players):
            title = _title(count, i, len(sorted_players))
            count_cols[i % len(count_cols)].metric(
                player,
                f"{count} games",
                help=title,
            )
            count_cols[i % len(count_cols)].caption(title)
else:
    st.markdown("*🦗 No games yet... the court is lonely.*")
