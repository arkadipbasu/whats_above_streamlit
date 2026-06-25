# ABOVE ME — Overhead Tracker (Streamlit)

Track aircraft, satellites, and flight routes overhead for any location on Earth —
plus a live ISS tracker embed from ESA.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the URL it prints (usually `http://localhost:8501`).

## Deploy publicly — free, in 3 minutes

**Streamlit Community Cloud** (easiest, free tier):

1. Push this folder to a public GitHub repo:
   ```bash
   git init
   git add .
   git commit -m "Above Me overhead tracker"
   git branch -M main
   git remote add origin https://github.com/<you>/above-me.git
   git push -u origin main
   ```
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → pick your repo → set main file to `app.py` → **Deploy**
4. You'll get a public URL like `https://above-me.streamlit.app`

No server, no Docker, no config needed — `requirements.txt` is auto-installed.

## What it shows

- **✈️ Aircraft** — live positions within 250 km, via OpenSky Network (falls back to adsb.lol → adsb.fi → demo data if rate-limited)
- **🗺️ Routes** — estimated origin/destination pairs derived from ICAO callsigns
- **🛰️ Satellites** — real orbital mechanics (simplified SGP4) computed from live Celestrak TLE data, with a hardcoded fallback if Celestrak is unreachable
- **🛰️ ISS Live** — embedded real-time 3D tracker from ESA

## Data sources

| Purpose | Source |
|---|---|
| Aircraft | OpenSky Network → adsb.lol → adsb.fi |
| Satellites | Celestrak (live TLE) → offline orbital fallback |
| Geocoding | Photon (Komoot) → Nominatim (OSM) |
| ISS 3D view | ESA Space Operations |

## Notes on rate limits

OpenSky's anonymous tier allows ~100 requests/hour per IP. If exceeded, the app
automatically shows clearly-labeled demo data instead of failing.

Celestrak TLE data is cached for 2 hours per session to avoid hammering their servers.
