import os
import time
import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 120))


def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?regions=eu&markets=h2h&apiKey={ODDS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return data
    except:
        return None


def check_arbitrage(events):
    if not events:
        return []

    alerts = []

    for ev in events:
        try:
            home = ev["home_team"]
            away = ev["away_team"]

            bookmakers = ev["bookmakers"]
            best_home = 0
            best_draw = 0
            best_away = 0

            for bm in bookmakers:
                for market in bm["markets"]:
                    if market["key"] == "h2h":
                        odds = market["outcomes"]
                        for o in odds:
                            if o["name"] == home:
                                best_home = max(best_home, o["price"])
                            elif o["name"] == away:
                                best_away = max(best_away, o["price"])
                            elif o["name"] == "Draw":
                                best_draw = max(best_draw, o["price"])

            if best_home > 0 and best_draw > 0 and best_away > 0:
                arb = (1/best_home)+(1/best_draw)+(1/best_away)
                if arb < 1:
                    alerts.append(
                        f"🔥 ARBITRAGE FOUND 🔥\n{home} vs {away}\nHome: {best_home}\nDraw: {best_draw}\nAway: {best_away}\nArb Value: {arb}"
                    )
        except:
            continue

    return alerts


def main():
    bot = Bot(BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text="🔄 Bot Started — Scanning EPL 1X2 Markets...")

    while True:
        events = fetch_odds()
        alerts = check_arbitrage(events)

        if alerts:
            for a in alerts:
                bot.send_message(chat_id=CHAT_ID, text=a)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
