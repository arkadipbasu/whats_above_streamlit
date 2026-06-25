"""
ABOVE ME — Overhead Tracker
Streamlit app: aircraft, satellites & routes for any location on Earth.

Contact - arkadipbasu.github.io
"""

import streamlit as st
import requests
import math
import time
import random
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ABOVE ME — Overhead Tracker",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────
# THEME — space / mission-control CSS
# ──────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root{
  --bg:#060B18; --bg2:#0A1628; --bg3:#0F1F3A;
  --panel:#0D1A30; --border:rgba(0,212,255,.13); --border2:rgba(0,212,255,.06);
  --cyan:#00D4FF; --cyan-dim:rgba(0,212,255,.13); --cyan-glow:rgba(0,212,255,.3);
  --amber:#FFB347; --amber-dim:rgba(255,179,71,.13);
  --green:#39FF7E; --green-dim:rgba(57,255,126,.12);
  --red:#FF4B6E; --red-dim:rgba(255,75,110,.12);
  --purple:#C084FC;
  --text:#E8F4FF; --text2:#7FA3C4; --text3:#3D6080;
}

/* App background */
.stApp{
  background:var(--bg);
  background-image:
    radial-gradient(ellipse at 20% 15%, rgba(0,80,160,.18) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 85%, rgba(0,50,120,.13) 0%, transparent 55%);
}
.stApp, .stApp * { font-family:'Inter',sans-serif; color:var(--text); }
.block-container{padding-top:1.2rem; max-width:1280px;}

/* Hide default streamlit chrome */
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}

/* Starfield canvas (fixed, behind everything) */
#star-canvas{
  position:fixed; inset:0; z-index:0; pointer-events:none;
}

/* Brand header */
.brand-row{display:flex; align-items:center; justify-content:space-between;
  padding:6px 0 14px; border-bottom:1px solid var(--border2); margin-bottom:18px;}
.brand{font-family:'Orbitron',monospace; font-size:17px; font-weight:700;
  letter-spacing:.12em; color:var(--cyan); display:flex; align-items:center; gap:10px;}
.brand-orb{width:30px;height:30px;border-radius:50%;flex-shrink:0;
  background:conic-gradient(var(--cyan) 0 120deg,var(--amber) 120deg 240deg,var(--purple) 240deg 360deg);
  animation:spin 14s linear infinite;}
@keyframes spin{to{transform:rotate(360deg)}}
.brand-sub{font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--text3);
  letter-spacing:.05em; display:block; margin-top:1px; font-weight:400;}
.portfolio-link{font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:.06em;
  color:var(--text3); border:1px solid var(--border2); padding:4px 11px; border-radius:99px;
  background:rgba(255,255,255,.03); text-decoration:none;}
.portfolio-link:hover{color:var(--cyan); border-color:var(--cyan);}
.live-pill{font-family:'JetBrains Mono',monospace; font-size:10px; padding:4px 11px;
  border-radius:99px; display:inline-flex; align-items:center; gap:5px;
  border:1px solid var(--green); color:var(--green); background:var(--green-dim);}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);
  animation:pdot 1.4s infinite ease-in-out; display:inline-block;}
@keyframes pdot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.65)}}

/* Status pills */
.status-row{display:flex; gap:7px; flex-wrap:wrap; margin:8px 0 18px;}
.pill{font-family:'JetBrains Mono',monospace; font-size:11px; padding:3px 10px;
  border-radius:99px; display:inline-flex; align-items:center; gap:5px;}
.p-dim{background:rgba(255,255,255,.04); color:var(--text3); border:1px solid var(--border2);}
.p-green{background:var(--green-dim); color:var(--green); border:1px solid rgba(57,255,126,.2);}
.p-amber{background:var(--amber-dim); color:var(--amber); border:1px solid rgba(255,179,71,.2);}
.p-blue{background:var(--cyan-dim); color:var(--cyan); border:1px solid var(--border);}
.p-red{background:var(--red-dim); color:var(--red); border:1px solid rgba(255,75,110,.2);}

/* Metric cards */
.met{background:var(--panel); border:1px solid var(--border2); border-radius:12px;
  padding:16px 18px; position:relative; overflow:hidden; height:100%;}
.met::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:var(--ac,var(--cyan)); opacity:.45;}
.met-val{font-family:'Orbitron',monospace; font-size:26px; font-weight:700;
  color:var(--text); line-height:1; margin-bottom:4px;}
.met-lbl{font-size:11px; color:var(--text3); letter-spacing:.06em; text-transform:uppercase;}
.met-sub{font-size:11px; color:var(--text3); margin-top:5px; font-family:'JetBrains Mono',monospace;}

/* Section headers */
.section-hd{font-family:'Orbitron',monospace; font-size:11px; font-weight:600;
  letter-spacing:.1em; color:var(--text2); text-transform:uppercase;
  display:flex; align-items:center; gap:8px; margin:22px 0 10px;
  padding-bottom:8px; border-bottom:1px solid var(--border2);}

/* Tables */
.styled-table{width:100%; border-collapse:collapse; font-size:13px;}
.styled-table th{padding:8px 12px; font-size:10px; font-weight:600; letter-spacing:.07em;
  text-transform:uppercase; color:var(--text3); border-bottom:1px solid var(--border2);
  text-align:left; background:var(--bg2);}
.styled-table td{padding:9px 12px; border-bottom:1px solid var(--border2); color:var(--text);}
.styled-table tr:hover td{background:rgba(0,212,255,.035);}
.cs{font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:500; color:var(--cyan);}
.cc{font-size:10px; color:var(--text3);}
.mono{font-family:'JetBrains Mono',monospace; font-size:12px; color:var(--text2);}
.badge{font-size:9px; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
  padding:2px 7px; border-radius:4px; display:inline-block; white-space:nowrap;}
.b-c{background:var(--cyan-dim); color:var(--cyan); border:1px solid rgba(0,212,255,.2);}
.b-a{background:var(--amber-dim); color:var(--amber); border:1px solid rgba(255,179,71,.2);}
.b-g{background:var(--green-dim); color:var(--green); border:1px solid rgba(57,255,126,.2);}
.b-p{background:rgba(192,132,252,.12); color:var(--purple); border:1px solid rgba(192,132,252,.2);}
.b-d{background:rgba(255,255,255,.05); color:var(--text2); border:1px solid var(--border2);}

/* ISS card */
.iss-card{border-radius:12px; padding:16px; margin-bottom:10px;
  background:linear-gradient(135deg,rgba(192,132,252,.08),rgba(0,212,255,.05));
  border:1px solid rgba(192,132,252,.2);}
.iss-ttl{font-family:'Orbitron',monospace; font-size:11px; font-weight:700; color:var(--purple);
  letter-spacing:.07em; margin-bottom:8px; display:flex; align-items:center; gap:6px;}
.iss-grid{display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:9px;}
.iss-datum label{font-size:9px; color:var(--text3); text-transform:uppercase;
  letter-spacing:.06em; display:block; margin-bottom:1px;}
.iss-datum span{font-family:'JetBrains Mono',monospace; font-size:13px;}

/* Satellite list items */
.sat-item{padding:11px 14px; border-bottom:1px solid var(--border2);}
.sat-item:last-child{border-bottom:none;}
.sat-list-scroll{max-height:560px; overflow-y:auto; background:var(--panel);
  border:1px solid var(--border2); border-radius:12px;}
.sat-list-scroll::-webkit-scrollbar{width:5px;}
.sat-list-scroll::-webkit-scrollbar-track{background:transparent;}
.sat-list-scroll::-webkit-scrollbar-thumb{background:var(--border); border-radius:3px;}
.sat-name{font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:500;
  display:flex; align-items:center; justify-content:space-between; gap:6px; margin-bottom:5px;}
.sat-meta{font-size:10px; color:var(--text3); display:flex; flex-wrap:wrap; gap:8px; margin-bottom:6px;}
.prog{height:3px; background:rgba(255,255,255,.07); border-radius:2px; overflow:hidden;}
.prog-fill{height:100%; border-radius:2px;}

/* Notice boxes */
.notice{font-size:12px; padding:9px 13px; border-radius:6px;
  display:flex; align-items:flex-start; gap:7px; line-height:1.55; margin-bottom:10px;}
.ni{background:var(--cyan-dim); color:var(--cyan); border:1px solid rgba(0,212,255,.2);}
.nw{background:var(--amber-dim); color:var(--amber); border:1px solid rgba(255,179,71,.2);}

/* ESA iframe frame */
.frame-wrapper{border:1px solid var(--border2); border-radius:12px; overflow:hidden;
  background:var(--panel);}

/* Footer links */
.footer-row{display:flex; justify-content:space-between; align-items:center;
  margin-top:28px; padding-top:16px; border-top:1px solid var(--border2); flex-wrap:wrap; gap:10px;}
.src-lbl{font-size:10px; color:var(--text3); text-transform:uppercase; letter-spacing:.06em;}
.src{font-size:10px; font-family:'JetBrains Mono',monospace; padding:4px 10px; border-radius:4px;
  border:1px solid var(--border2); color:var(--text3); background:rgba(255,255,255,.02);
  text-decoration:none; margin-right:6px;}
.src:hover{border-color:var(--cyan); color:var(--cyan);}
.isro-link{display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:10px;
  border:1px solid rgba(57,255,126,.2); background:rgba(57,255,126,.05);
  color:var(--green); font-size:11px; font-family:'JetBrains Mono',monospace;
  letter-spacing:.06em; text-decoration:none;}
.isro-link:hover{background:rgba(57,255,126,.12); border-color:rgba(57,255,126,.5);}

/* Streamlit widget overrides */
div[data-testid="stTextInput"] input{
  background:var(--bg2); border:1px solid var(--border); color:var(--text);
  border-radius:10px; font-family:'Inter',sans-serif;
}
div[data-testid="stTextInput"] input:focus{border-color:var(--cyan); box-shadow:0 0 0 2px var(--cyan-dim);}
.stButton button{
  background:var(--cyan); color:var(--bg); border:none; border-radius:10px;
  font-weight:600; letter-spacing:.04em; box-shadow:0 0 16px var(--cyan-glow);
}
.stButton button:hover{background:#33DDFF;}
div[data-testid="stTabs"] button[role="tab"]{font-family:'Inter',sans-serif; color:var(--text3);}
div[data-testid="stTabs"] button[aria-selected="true"]{color:var(--cyan); border-color:var(--cyan);}
</style>
"""

STARFIELD_HTML = """
<canvas id="star-canvas"></canvas>
<script>
(function(){
  const c = document.getElementById('star-canvas');
  if(!c || c.dataset.init) return;
  c.dataset.init='1';
  const ctx = c.getContext('2d');
  function resize(){ c.width=window.innerWidth; c.height=window.innerHeight; }
  resize(); window.addEventListener('resize', resize);

  const stars = [];
  for(let i=0;i<250;i++){
    stars.push({
      x:Math.random()*c.width, y:Math.random()*c.height,
      r:Math.random()*1.6+0.3, speed:Math.random()*0.015+0.003,
      phase:Math.random()*Math.PI*2, bright:Math.random()<0.12
    });
  }
  function draw(t){
    ctx.clearRect(0,0,c.width,c.height);
    stars.forEach(s=>{
      const tw = 0.3 + 0.7*Math.abs(Math.sin(t*s.speed + s.phase));
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.bright ? s.r*1.8 : s.r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(255,255,255,${tw})`;
      ctx.fill();
      if(s.bright && tw>0.85){
        ctx.strokeStyle = `rgba(200,230,255,${(tw-0.85)*4})`;
        ctx.lineWidth=1;
        ctx.beginPath(); ctx.moveTo(s.x-6,s.y); ctx.lineTo(s.x+6,s.y); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(s.x,s.y-6); ctx.lineTo(s.x,s.y+6); ctx.stroke();
      }
    });
    requestAnimationFrame(draw);
  }
  draw(0);
})();
</script>
"""

st.markdown(CSS, unsafe_allow_html=True)
st.components.v1.html(STARFIELD_HTML, height=0)

# ──────────────────────────────────────────────────────────────
# DATA: airline lookup
# ──────────────────────────────────────────────────────────────
AIRLINES = {
    'AI': 'Air India', 'AIC': 'Air India',
    'EK': 'Emirates', 'UAE': 'Emirates',
    '6E': 'IndiGo', 'IGO': 'IndiGo',
    'SG': 'SpiceJet', 'SEJ': 'SpiceJet',
    'UK': 'Vistara', 'VTI': 'Vistara',
    'QR': 'Qatar Airways', 'QTR': 'Qatar Airways',
    'SQ': 'Singapore Airlines', 'SIA': 'Singapore Airlines',
    'EY': 'Etihad', 'ETD': 'Etihad',
    'BA': 'British Airways', 'BAW': 'British Airways',
    'LH': 'Lufthansa', 'DLH': 'Lufthansa',
    'TG': 'Thai Airways', 'THA': 'Thai Airways',
    'I5': 'Air Asia India', 'QP': 'Akasa Air',
    'G8': 'GoAir', '9W': 'Jet Airways',
}
POOLS = {
    'AI': ['DEL', 'BOM', 'MAA', 'HYD', 'CCU', 'BLR', 'DXB', 'LHR', 'JFK', 'SIN'],
    'EK': ['DXB', 'BOM', 'DEL', 'BLR', 'MAA', 'HYD', 'LHR', 'JFK', 'SYD', 'NRT'],
    '6E': ['DEL', 'BOM', 'BLR', 'MAA', 'HYD', 'CCU', 'GOI', 'AMD', 'PNQ', 'JAI'],
    'SG': ['DEL', 'BOM', 'BLR', 'MAA', 'HYD', 'CCU', 'GAU'],
    'UK': ['DEL', 'BOM', 'BLR', 'MAA', 'HYD', 'DXB', 'SIN', 'LHR'],
    'QR': ['DOH', 'BOM', 'DEL', 'BLR', 'MAA', 'HYD', 'LHR', 'JFK'],
    'SQ': ['SIN', 'BOM', 'DEL', 'BLR', 'MAA', 'LHR', 'JFK', 'NRT'],
}
DEFAULT_POOL = ['DEL', 'BOM', 'DXB', 'SIN', 'LHR', 'JFK', 'BKK', 'CDG', 'FRA', 'DOH']


def guess_route(callsign, country):
    if not callsign:
        return {'airline': country or 'Unknown', 'from': '???', 'to': '???'}
    cs = callsign.strip().upper()
    i2, i3 = cs[:2], cs[:3]
    airline = AIRLINES.get(i3) or AIRLINES.get(i2) or country or 'Unknown'
    pool = POOLS.get(i2) or POOLS.get(i3) or DEFAULT_POOL
    seed = sum(ord(c) for c in cs)
    rnd = random.Random(seed)
    frm = rnd.choice(pool)
    to = rnd.choice([p for p in pool if p != frm]) if len(pool) > 1 else frm
    return {'airline': airline, 'from': frm, 'to': to}


# ──────────────────────────────────────────────────────────────
# GEOCODING
# ──────────────────────────────────────────────────────────────
import re

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"


@st.cache_data(ttl=3600, show_spinner=False)
def geocode(q: str):
    q = q.strip()
    m = re.match(r'^\s*(-?\d{1,3}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)\s*$', q)
    if m:
        return {'lat': float(m.group(1)), 'lon': float(m.group(2)), 'display': q}

    try:
        r = requests.get(
            "https://photon.komoot.io/api/",
            params={'q': q, 'limit': 1, 'lang': 'en'},
            headers={'User-Agent': UA}, timeout=8,
        )
        if r.ok:
            d = r.json()
            feats = d.get('features', [])
            if feats:
                f = feats[0]
                lon, lat = f['geometry']['coordinates']
                p = f.get('properties', {})
                display = ', '.join(filter(None, [p.get('name'), p.get('city') or p.get('county'), p.get('country')]))
                return {'lat': lat, 'lon': lon, 'display': display or q}
    except Exception:
        pass

    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={'format': 'json', 'limit': 1, 'q': q, 'accept-language': 'en'},
            headers={'User-Agent': UA, 'Referer': 'https://streamlit.io/'}, timeout=8,
        )
        if r.ok:
            d = r.json()
            if d:
                display = ','.join(d[0]['display_name'].split(',')[:2]).strip()
                return {'lat': float(d[0]['lat']), 'lon': float(d[0]['lon']), 'display': display}
    except Exception:
        pass

    raise ValueError(f'Could not geocode "{q}"')


# ──────────────────────────────────────────────────────────────
# AIRCRAFT — OpenSky → adsb.lol → adsb.fi fallback chain
# ──────────────────────────────────────────────────────────────
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def demo_aircraft(lat, lon):
    fleet = [
        ('AI102', 'India'), ('EK528', 'UAE'), ('6E441', 'India'),
        ('SG804', 'India'), ('UK948', 'India'), ('QR597', 'Qatar'),
        ('SQ514', 'Singapore'), ('I5701', 'India'), ('G8432', 'India'),
        ('QP102', 'India'), ('AI870', 'India'), ('6E710', 'India'),
    ]
    out = []
    rnd = random.Random(int(lat * 1000) + int(lon * 1000))
    for i, (cs, cc) in enumerate(fleet):
        out.append({
            'icao24': f'demo{i}', 'callsign': cs, 'country': cc,
            'lon': lon + (rnd.random() - 0.5) * 2.4,
            'lat': lat + (rnd.random() - 0.5) * 2.4,
            'alt_m': round(4000 + rnd.random() * 8000),
            'speed_kph': round(380 + rnd.random() * 520),
            'heading': round(rnd.random() * 360),
            '_demo': True,
        })
    return out


def fetch_opensky(lat, lon, radius_km=250):
    d_lat = radius_km / 111.0
    d_lon = d_lat / math.cos(math.radians(lat))
    bbox = dict(
        lamin=lat - d_lat, lamax=lat + d_lat,
        lomin=lon - d_lon, lomax=lon + d_lon,
    )
    url = "https://opensky-network.org/api/states/all"
    r = requests.get(url, params=bbox, headers={'User-Agent': UA}, timeout=10)
    if r.status_code == 429:
        raise TimeoutError('rate_limit')
    r.raise_for_status()
    states = r.json().get('states') or []
    out = []
    for s in states:
        if s[5] is None or s[6] is None or s[8]:
            continue
        ac = {
            'icao24': s[0] or '', 'callsign': (s[1] or '').strip(),
            'country': s[2] or '', 'lon': s[5], 'lat': s[6],
            'alt_m': round(s[7]) if s[7] is not None else None,
            'speed_kph': round(s[9] * 3.6) if s[9] is not None else None,
            'heading': round(s[10]) if s[10] is not None else None,
            'squawk': s[14] or '',
        }
        if haversine_km(lat, lon, ac['lat'], ac['lon']) <= radius_km:
            out.append(ac)
    return out


def fetch_adsb_lol(lat, lon, radius_km=250):
    url = f"https://api.adsb.lol/v2/point/{lat}/{lon}/{radius_km}"
    r = requests.get(url, headers={'User-Agent': UA}, timeout=10)
    r.raise_for_status()
    ac_list = r.json().get('ac') or []
    out = []
    for a in ac_list:
        if a.get('gnd') or not a.get('lat') or not a.get('lon'):
            continue
        out.append({
            'icao24': a.get('hex', ''), 'callsign': (a.get('flight') or a.get('r') or '').strip(),
            'country': a.get('cou', ''), 'lon': a['lon'], 'lat': a['lat'],
            'alt_m': round(a['alt_baro'] * 0.3048) if a.get('alt_baro') else None,
            'speed_kph': round(a['gs'] * 1.852) if a.get('gs') else None,
            'heading': round(a['track']) if a.get('track') else None,
            'squawk': a.get('squawk', ''),
        })
    return out


def fetch_adsb_fi(lat, lon, radius_km=250):
    url = "https://api.adsb.fi/v1/point"
    r = requests.get(url, params={'lat': lat, 'lon': lon, 'radius': radius_km},
                      headers={'User-Agent': UA}, timeout=10)
    r.raise_for_status()
    ac_list = r.json().get('ac') or []
    out = []
    for a in ac_list:
        if a.get('gnd') or not a.get('lat') or not a.get('lon'):
            continue
        out.append({
            'icao24': a.get('hex', ''), 'callsign': (a.get('flight') or '').strip(),
            'country': '', 'lon': a['lon'], 'lat': a['lat'],
            'alt_m': round(a['alt_baro'] * 0.3048) if a.get('alt_baro') else None,
            'speed_kph': round(a['gs'] * 1.852) if a.get('gs') else None,
            'heading': round(a['track']) if a.get('track') else None,
            'squawk': a.get('squawk', ''),
        })
    return out


def get_aircraft(lat, lon):
    """Returns (aircraft_list, source, is_demo, demo_reason)"""
    try:
        ac = fetch_opensky(lat, lon)
        if ac:
            return ac, 'OpenSky Network', False, None
    except TimeoutError:
        return demo_aircraft(lat, lon), 'demo', True, 'rate_limit'
    except Exception:
        pass

    try:
        ac = fetch_adsb_lol(lat, lon)
        if ac:
            return ac, 'adsb.lol', False, None
    except Exception:
        pass

    try:
        ac = fetch_adsb_fi(lat, lon)
        if ac:
            return ac, 'adsb.fi', False, None
    except Exception:
        pass

    return demo_aircraft(lat, lon), 'demo', True, 'fetch_failed'


# ──────────────────────────────────────────────────────────────
# SATELLITES — Celestrak TLE + simplified SGP4 propagation
# ──────────────────────────────────────────────────────────────
def get_gmst(unix_sec):
    JD = unix_sec / 86400.0 + 2440587.5
    d = JD - 2451545.0
    gmst = (280.46061837 + 360.98564736629 * d) % 360
    return gmst + 360 if gmst < 0 else gmst


def compute_pass(sat, obs_lat, obs_lon, now_unix):
    try:
        mu = 398600.4418
        Re = 6371.0
        j2 = 1.08262668e-3

        n = sat['mm'] * 2 * math.pi / 86400.0
        a = (mu / (n * n)) ** (1 / 3)
        alt_km = a - Re
        if alt_km < 160 or alt_km > 42000:
            return None

        dt = now_unix - sat['epoch']
        M = (math.radians(sat['ma']) + n * dt) % (2 * math.pi)
        if M < 0:
            M += 2 * math.pi

        E = M
        for _ in range(3):
            E = M + sat['ecc'] * math.sin(E)

        nu = 2 * math.atan2(
            math.sqrt(1 + sat['ecc']) * math.sin(E / 2),
            math.sqrt(1 - sat['ecc']) * math.cos(E / 2),
        )
        u = math.radians(sat['argp']) + nu
        inc = math.radians(sat['inc'])

        d_om = -1.5 * n * j2 * (Re / a) ** 2 * math.cos(inc)
        Om = math.radians(sat['raan']) + d_om * dt

        x = a * (math.cos(Om) * math.cos(u) - math.sin(Om) * math.sin(u) * math.cos(inc))
        y = a * (math.sin(Om) * math.cos(u) + math.cos(Om) * math.sin(u) * math.cos(inc))
        z = a * math.sin(u) * math.sin(inc)

        gmst = math.radians(get_gmst(now_unix))
        xe = x * math.cos(gmst) + y * math.sin(gmst)
        ye = -x * math.sin(gmst) + y * math.cos(gmst)

        sat_lat = math.degrees(math.asin(z / a))
        sat_lon = math.degrees(math.atan2(ye, xe))

        o_lat = math.radians(obs_lat)
        s_lat_r = math.radians(sat_lat)
        d_lon = math.radians(sat_lon - obs_lon)
        hav = (math.sin(math.radians(sat_lat - obs_lat) / 2) ** 2
               + math.cos(o_lat) * math.cos(s_lat_r) * math.sin(d_lon / 2) ** 2)
        ca = 2 * math.atan2(math.sqrt(hav), math.sqrt(max(0, 1 - hav)))
        sin_el = (math.cos(ca) - Re / a) / math.sqrt(max(1e-9, 1 - 2 * (Re / a) * math.cos(ca) + (Re / a) ** 2))
        elevation = math.degrees(math.asin(max(-1, min(1, sin_el))))

        yb = math.sin(d_lon) * math.cos(s_lat_r)
        xb = math.cos(o_lat) * math.sin(s_lat_r) - math.sin(o_lat) * math.cos(s_lat_r) * math.cos(d_lon)
        azimuth = (math.degrees(math.atan2(yb, xb)) + 360) % 360

        return {
            'name': sat['name'],
            'elevation': round(elevation),
            'azimuth': round(azimuth),
            'alt_km': round(alt_km),
            'sat_lat': round(sat_lat, 1),
            'sat_lon': round(sat_lon, 1),
            'type': classify_orbit(alt_km),
        }
    except Exception:
        return None


def classify_orbit(alt_km):
    if alt_km < 600:
        return 'LEO'
    if alt_km < 2000:
        return 'LEO+'
    if alt_km < 20000:
        return 'MEO'
    return 'GEO'


def parse_tle_text(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    sats = []
    for i in range(len(lines) - 2):
        l1, l2 = lines[i + 1], lines[i + 2]
        if not l1.startswith('1 ') or not l2.startswith('2 '):
            continue
        try:
            epoch_str = l1[18:32].strip()
            yr2 = int(epoch_str[:2])
            yr = 2000 + yr2 if yr2 < 57 else 1900 + yr2
            day = float(epoch_str[2:])
            epoch_unix = datetime(yr, 1, 1, tzinfo=timezone.utc).timestamp() + (day - 1) * 86400
            sats.append({
                'name': lines[i].strip(),
                'mm': float(l2[52:63]),
                'inc': float(l2[8:16]),
                'raan': float(l2[17:25]),
                'ecc': float('0.' + l2[26:33].strip()),
                'argp': float(l2[34:42]),
                'ma': float(l2[43:51]),
                'epoch': epoch_unix,
            })
        except Exception:
            continue
    return sats


@st.cache_data(ttl=7200, show_spinner=False)
def fetch_tles():
    """Fetch live TLEs from Celestrak, cached 2 hours. Pulls from multiple
    constellations so there's always a healthy number of satellites to
    propagate, regardless of which ones happen to be overhead."""
    sources = [
        ('https://celestrak.org/TLE/query.php?GROUP=stations&FORMAT=tle', 'stations'),
        ('https://celestrak.org/TLE/query.php?GROUP=visual&FORMAT=tle', 'visual'),
        ('https://celestrak.org/TLE/query.php?GROUP=weather&FORMAT=tle', 'weather'),
        ('https://celestrak.org/TLE/query.php?GROUP=noaa&FORMAT=tle', 'noaa'),
        ('https://celestrak.org/TLE/query.php?GROUP=starlink&FORMAT=tle', 'starlink'),
        ('https://celestrak.org/TLE/query.php?GROUP=gps-ops&FORMAT=tle', 'gps'),
        ('https://celestrak.org/TLE/query.php?GROUP=resource&FORMAT=tle', 'resource'),
        ('https://celestrak.org/TLE/query.php?GROUP=science&FORMAT=tle', 'science'),
    ]
    all_sats = []
    sources_used = []
    for url, label in sources:
        try:
            r = requests.get(url, headers={'User-Agent': UA, 'Accept': 'text/plain'}, timeout=6)
            if r.status_code == 200 and len(r.text) > 100:
                parsed = parse_tle_text(r.text)
                if parsed:
                    # Cap starlink/gps contributions so they don't drown out everything else
                    if label in ('starlink', 'gps'):
                        parsed = parsed[:60]
                    all_sats.extend(parsed)
                    sources_used.append(label)
        except Exception:
            continue
    if all_sats:
        return all_sats, f"Celestrak (live: {', '.join(sources_used)})"
    return [], None


def get_known_fallback_sats(now_unix):
    return [
        {'name': 'ISS (ZARYA)', 'mm': 15.49564958, 'inc': 51.6416, 'raan': 15.2, 'ecc': 0.0001234, 'argp': 84.1, 'ma': 276.1, 'epoch': now_unix - 600},
        {'name': 'Tiangong (CSS)', 'mm': 15.61622767, 'inc': 41.4700, 'raan': 200.1, 'ecc': 0.0005500, 'argp': 180.0, 'ma': 180.0, 'epoch': now_unix - 600},
        {'name': 'Hubble (HST)', 'mm': 15.09297620, 'inc': 28.4700, 'raan': 187.4, 'ecc': 0.0002719, 'argp': 45.3, 'ma': 315.2, 'epoch': now_unix - 1200},
        {'name': 'Starlink-1007', 'mm': 15.06391602, 'inc': 53.0536, 'raan': 42.1, 'ecc': 0.0001420, 'argp': 90.0, 'ma': 270.1, 'epoch': now_unix - 300},
        {'name': 'Starlink-2341', 'mm': 15.06398211, 'inc': 53.0541, 'raan': 162.3, 'ecc': 0.0001180, 'argp': 90.0, 'ma': 90.2, 'epoch': now_unix - 900},
        {'name': 'Starlink-3056', 'mm': 15.06412033, 'inc': 53.0539, 'raan': 282.5, 'ecc': 0.0001350, 'argp': 90.0, 'ma': 180.1, 'epoch': now_unix - 450},
        {'name': 'Starlink-4112', 'mm': 15.06405000, 'inc': 53.0540, 'raan': 2.5, 'ecc': 0.0001200, 'argp': 90.0, 'ma': 45.0, 'epoch': now_unix - 700},
        {'name': 'Starlink-5023', 'mm': 15.06400000, 'inc': 53.0538, 'raan': 122.5, 'ecc': 0.0001300, 'argp': 90.0, 'ma': 225.0, 'epoch': now_unix - 1100},
        {'name': 'Sentinel-2A', 'mm': 14.30824610, 'inc': 98.5702, 'raan': 311.2, 'ecc': 0.0001041, 'argp': 87.3, 'ma': 272.9, 'epoch': now_unix - 1800},
        {'name': 'Sentinel-1A', 'mm': 14.59197756, 'inc': 98.1813, 'raan': 130.6, 'ecc': 0.0001180, 'argp': 88.0, 'ma': 60.0, 'epoch': now_unix - 2100},
        {'name': 'NOAA-20', 'mm': 14.19551574, 'inc': 98.7450, 'raan': 22.6, 'ecc': 0.0009126, 'argp': 92.1, 'ma': 268.1, 'epoch': now_unix - 2400},
        {'name': 'NOAA-19', 'mm': 14.12345678, 'inc': 99.1900, 'raan': 142.6, 'ecc': 0.0013500, 'argp': 95.0, 'ma': 120.0, 'epoch': now_unix - 2800},
        {'name': 'Landsat-9', 'mm': 14.57116667, 'inc': 98.2069, 'raan': 176.3, 'ecc': 0.0001090, 'argp': 90.0, 'ma': 270.0, 'epoch': now_unix - 3600},
        {'name': 'Landsat-8', 'mm': 14.57135000, 'inc': 98.2042, 'raan': 56.3, 'ecc': 0.0001110, 'argp': 90.0, 'ma': 90.0, 'epoch': now_unix - 3300},
        {'name': 'Terra (EOS AM-1)', 'mm': 14.57100000, 'inc': 98.2080, 'raan': 296.3, 'ecc': 0.0001200, 'argp': 90.0, 'ma': 0.0, 'epoch': now_unix - 4000},
        {'name': 'Aqua (EOS PM-1)', 'mm': 14.57100000, 'inc': 98.2030, 'raan': 116.3, 'ecc': 0.0001150, 'argp': 90.0, 'ma': 180.0, 'epoch': now_unix - 4200},
        {'name': 'GPS BIIR-2', 'mm': 2.00561200, 'inc': 55.0000, 'raan': 30.0, 'ecc': 0.0080000, 'argp': 90.0, 'ma': 0.0, 'epoch': now_unix - 7200},
        {'name': 'GPS BIIR-5', 'mm': 2.00561200, 'inc': 55.0000, 'raan': 150.0, 'ecc': 0.0080000, 'argp': 90.0, 'ma': 120.0, 'epoch': now_unix - 7200},
        {'name': 'GPS BIIR-8', 'mm': 2.00561200, 'inc': 55.0000, 'raan': 270.0, 'ecc': 0.0080000, 'argp': 90.0, 'ma': 240.0, 'epoch': now_unix - 7200},
        {'name': 'GSAT-30', 'mm': 1.00271614, 'inc': 0.0500, 'raan': 83.0, 'ecc': 0.0002000, 'argp': 90.0, 'ma': 0.0, 'epoch': now_unix - 43200},
        {'name': 'IRNSS-1I (NavIC)', 'mm': 1.00342958, 'inc': 29.0000, 'raan': 55.0, 'ecc': 0.0010000, 'argp': 270.0, 'ma': 0.0, 'epoch': now_unix - 43200},
        {'name': 'INSAT-3D', 'mm': 1.00270000, 'inc': 0.0400, 'raan': 175.0, 'ecc': 0.0002000, 'argp': 90.0, 'ma': 0.0, 'epoch': now_unix - 43200},
        {'name': 'OneWeb-0012', 'mm': 12.84512000, 'inc': 87.9000, 'raan': 100.0, 'ecc': 0.0010000, 'argp': 90.0, 'ma': 180.0, 'epoch': now_unix - 1800},
        {'name': 'OneWeb-0089', 'mm': 12.84510000, 'inc': 87.9100, 'raan': 220.0, 'ecc': 0.0010000, 'argp': 90.0, 'ma': 60.0, 'epoch': now_unix - 2200},
    ]


def get_satellites(lat, lon):
    now_unix = time.time()
    raw, source_label = fetch_tles()

    if raw:
        for s in raw:
            s['epoch'] = s.get('epoch', now_unix - 3600)
        passes = [compute_pass(s, lat, lon, now_unix) for s in raw]
        passes = [p for p in passes if p]
        passes.sort(key=lambda p: -p['elevation'])
        if passes:
            return passes[:60], source_label

    fallback = get_known_fallback_sats(now_unix)
    passes = [compute_pass(s, lat, lon, now_unix) for s in fallback]
    passes = [p for p in passes if p]
    passes.sort(key=lambda p: -p['elevation'])
    return passes, 'estimated (Celestrak unavailable)'


def sat_style(orbit_type, name):
    name = name or ''
    if 'ISS' in name:
        return '#C084FC', 'b-p'
    if 'starlink' in name.lower():
        return '#00D4FF', 'b-c'
    if 'NOAA' in name or 'Weather' in name:
        return '#FFB347', 'b-a'
    if orbit_type == 'GEO':
        return '#39FF7E', 'b-g'
    if orbit_type == 'MEO':
        return '#FFB347', 'b-a'
    if orbit_type in ('LEO', 'LEO+'):
        return '#C084FC', 'b-p'
    return '#7FA3C4', 'b-d'


# ──────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────
if 'tracked' not in st.session_state:
    st.session_state.tracked = False
    st.session_state.lat = None
    st.session_state.lon = None
    st.session_state.location_name = ''
    st.session_state.aircraft = []
    st.session_state.satellites = []
    st.session_state.ac_source = ''
    st.session_state.sat_source = ''
    st.session_state.is_demo = False
    st.session_state.demo_reason = ''
    st.session_state.last_scan = None

# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────
live_text = "STANDBY"
if st.session_state.tracked:
    live_text = "DEMO" if st.session_state.is_demo else "LIVE"

st.markdown(f"""
<div class="brand-row">
  <div class="brand">
    <div class="brand-orb"></div>
    <div>ABOVE ME<span class="brand-sub">OVERHEAD TRACKER — AIRCRAFT · SATELLITES · ROUTES</span></div>
  </div>
  <div style="display:flex; align-items:center; gap:12px;">
    <a class="portfolio-link" href="https://arkadipbasu.github.io/" target="_blank">arkadipbasu.github.io</a>
    <span class="live-pill"><span class="live-dot"></span>{live_text}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SEARCH BAR
# ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([5, 1, 1])
with col1:
    location_input = st.text_input(
        "Location", value="Bengaluru, India",
        placeholder="City, address, or lat, lon…",
        label_visibility="collapsed",
    )
with col2:
    scan_clicked = st.button("🛰️ SCAN", use_container_width=True)
with col3:
    auto_refresh = st.checkbox("Auto 60s", value=False)


def run_scan(query):
    with st.spinner("Geocoding location…"):
        try:
            geo = geocode(query)
        except Exception as e:
            st.error(f"✖ Geocoding failed: {e}")
            return

    st.session_state.lat = geo['lat']
    st.session_state.lon = geo['lon']
    st.session_state.location_name = geo['display']

    with st.spinner("Fetching aircraft…"):
        ac, ac_source, is_demo, demo_reason = get_aircraft(geo['lat'], geo['lon'])
    st.session_state.aircraft = ac
    st.session_state.ac_source = ac_source
    st.session_state.is_demo = is_demo
    st.session_state.demo_reason = demo_reason

    with st.spinner("Computing satellite passes…"):
        sats, sat_source = get_satellites(geo['lat'], geo['lon'])
    st.session_state.satellites = sats
    st.session_state.sat_source = sat_source

    st.session_state.tracked = True
    st.session_state.last_scan = datetime.now(IST)


if scan_clicked and location_input.strip():
    run_scan(location_input)

if auto_refresh and st.session_state.tracked:
    if st.session_state.last_scan and (datetime.now(IST) - st.session_state.last_scan).seconds > 60:
        run_scan(location_input)
        st.rerun()

# ──────────────────────────────────────────────────────────────
# STATUS ROW
# ──────────────────────────────────────────────────────────────
if st.session_state.tracked:
    pills = []
    if st.session_state.is_demo:
        pills.append('<span class="pill p-amber">⬤ Demo data</span>')
    else:
        pills.append(f'<span class="pill p-green">⬤ Live · {st.session_state.ac_source}</span>')
    pills.append(f'<span class="pill p-blue">{st.session_state.location_name}</span>')
    pills.append(f'<span class="pill p-dim">{st.session_state.lat:.3f}°N {st.session_state.lon:.3f}°E</span>')
    n_above = sum(1 for s in st.session_state.satellites if s['elevation'] > 0)
    pills.append(f'<span class="pill p-dim">{len(st.session_state.aircraft)} aircraft · {n_above} sats above horizon</span>')
    st.markdown(f'<div class="status-row">{"".join(pills)}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-row"><span class="pill p-dim">AWAITING LOCATION</span></div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# METRICS
# ──────────────────────────────────────────────────────────────
ac_count = len(st.session_state.aircraft) if st.session_state.tracked else 0
sat_above = sum(1 for s in st.session_state.satellites if s['elevation'] > 0) if st.session_state.tracked else 0
route_keys = set()
if st.session_state.tracked:
    for a in st.session_state.aircraft:
        r = guess_route(a.get('callsign'), a.get('country'))
        route_keys.add(f"{r['from']}-{r['to']}")
route_count = len(route_keys)
last_scan_str = f"{st.session_state.last_scan.strftime('%H:%M')} IST (GMT+5:30)" if st.session_state.last_scan else '—:—'

m1, m2, m3, m4 = st.columns(4)
metric_defs = [
    (m1, '#00D4FF', ac_count if st.session_state.tracked else '—', 'Aircraft overhead', 'within 250 km'),
    (m2, '#C084FC', sat_above if st.session_state.tracked else '—', 'Satellites tracked', 'above horizon now'),
    (m3, '#FFB347', route_count if st.session_state.tracked else '—', 'Active routes', 'unique O/D pairs'),
    (m4, '#39FF7E', last_scan_str, 'Last scanned', 'auto-refresh 60s'),
]
for col, color, val, label, sub in metric_defs:
    with col:
        val_size = '15px' if isinstance(val, str) and 'IST' in val else '26px'
        met_html = (
            f'<div class="met" style="--ac:{color}">'
            f'<div class="met-val" style="font-size:{val_size};">{val}</div>'
            f'<div class="met-lbl">{label}</div>'
            f'<div class="met-sub">{sub}</div>'
            f'</div>'
        )
        st.markdown(met_html, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# MAIN CONTENT — TABS
# ──────────────────────────────────────────────────────────────
left_col, right_col = st.columns([2.2, 1])

with left_col:
    tab_ac, tab_routes, tab_iss = st.tabs(["✈️ Aircraft", "🗺️ Routes", "🛰️ ISS Live"])

    with tab_ac:
        if not st.session_state.tracked:
            st.info("Enter a location and click **SCAN** to fetch live aircraft from OpenSky Network.")
        else:
            ac = st.session_state.aircraft
            if st.session_state.is_demo:
                if st.session_state.demo_reason == 'rate_limit':
                    st.markdown('<div class="notice nw">⚠ OpenSky rate limit hit — showing demo data. Resets hourly. Create a free account at opensky-network.org for higher limits.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="notice ni">ℹ Could not reach aircraft APIs — showing illustrative demo data.</div>', unsafe_allow_html=True)

            if not ac:
                st.markdown("No aircraft detected within 250 km right now.")
            else:
                rows = []
                for a in ac[:30]:
                    r = guess_route(a.get('callsign'), a.get('country'))
                    alt_m = a.get('alt_m')
                    alt_ft = round(alt_m * 3.281) if alt_m else None
                    tp = 'Commercial' if (alt_m or 0) > 8000 else 'Regional' if (alt_m or 0) > 3000 else 'GA'
                    rows.append({
                        'Callsign': a.get('callsign') or 'N/A',
                        'Country': a.get('country') or '—',
                        'Type': tp,
                        'Route (est.)': f"{r['from']} → {r['to']}",
                        'Airline': r['airline'],
                        'Altitude (ft)': f"{alt_ft:,}" if alt_ft else '—',
                        'Speed (km/h)': a.get('speed_kph') or '—',
                        'Heading (°)': a.get('heading') if a.get('heading') is not None else '—',
                    })
                st.dataframe(rows, use_container_width=True, height=440, hide_index=True)

    with tab_routes:
        if not st.session_state.tracked:
            st.info("Scan a location to see active flight routes.")
        else:
            ac = st.session_state.aircraft
            route_map = {}
            for a in ac:
                r = guess_route(a.get('callsign'), a.get('country'))
                key = f"{r['from']}-{r['to']}"
                if key not in route_map:
                    route_map[key] = {**r, 'count': 0, 'callsigns': []}
                route_map[key]['count'] += 1
                if len(route_map[key]['callsigns']) < 4:
                    route_map[key]['callsigns'].append(a.get('callsign') or '?')

            route_list = sorted(route_map.values(), key=lambda r: -r['count'])
            if not route_list:
                st.markdown("No routes derived from current traffic.")
            else:
                rows = [{
                    'Route': f"{r['from']} → {r['to']}",
                    'Airline': r['airline'],
                    'Active flights': r['count'],
                    'Callsigns': ' · '.join(r['callsigns']),
                } for r in route_list]
                st.dataframe(rows, use_container_width=True, height=440, hide_index=True)

    with tab_iss:
        st.markdown("#### Position of International Space Station")
        st.markdown('<div class="frame-wrapper">', unsafe_allow_html=True)
        st.components.v1.iframe(
            "https://isstracker.spaceflight.esa.int/index_portal.php",
            height=600,
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Live ISS tracker provided by the European Space Agency (ESA)")

with right_col:
    st.markdown('<div class="section-hd">🛰️ Satellites above</div>', unsafe_allow_html=True)

    if not st.session_state.tracked:
        st.info("Awaiting scan…")
    else:
        sats = st.session_state.satellites
        n_above_horizon = sum(1 for s in sats if s['elevation'] > 0)
        st.caption(f"Source: {st.session_state.sat_source} · {len(sats)} satellites computed · {n_above_horizon} above horizon")

        iss = next((s for s in sats if 'ISS' in (s.get('name') or '')), None)
        if iss:
            el_pct = max(0, round((iss['elevation'] + 90) / 180 * 100))
            above = iss['elevation'] > 10
            badge_cls = 'b-g' if above else 'b-d'
            badge_txt = 'ABOVE HORIZON' if above else 'Below horizon'
            iss_html = (
                f'<div class="iss-card">'
                f'<div class="iss-ttl">🛰️ International Space Station</div>'
                f'<span class="badge {badge_cls}">{badge_txt}</span>'
                f'<div class="iss-grid">'
                f'<div class="iss-datum"><label>Elevation</label><span>{iss["elevation"]}°</span></div>'
                f'<div class="iss-datum"><label>Azimuth</label><span>{iss["azimuth"]}°</span></div>'
                f'<div class="iss-datum"><label>Altitude</label><span>{iss["alt_km"]} km</span></div>'
                f'<div class="iss-datum"><label>Subpoint</label><span>{iss["sat_lat"]}°N</span></div>'
                f'</div>'
                f'<div class="prog" style="margin-top:10px;"><div class="prog-fill" style="width:{el_pct}%;background:#C084FC;"></div></div>'
                f'</div>'
            )
            st.markdown(iss_html, unsafe_allow_html=True)

        # Show ALL other satellites, sorted highest-elevation first, in a scrollable list
        others = [s for s in sats if 'ISS' not in (s.get('name') or '')]
        others = sorted(others, key=lambda s: -s['elevation'])
        sat_items = []
        for s in others[:50]:
            color, badge = sat_style(s['type'], s['name'])
            el_pct = max(0, round((s['elevation'] + 90) / 180 * 100))
            above = s['elevation'] > 0
            status_txt = "⬤ High overhead" if s['elevation'] > 30 else ("⬤ Above horizon" if above else "Below horizon")
            status_color = "var(--green)" if above else "var(--text3)"
            # Build each item as a single unindented line — Streamlit's markdown
            # parser treats heavily-indented HTML as a code block and escapes it,
            # so no leading whitespace or embedded newlines are allowed here.
            item = (
                f'<div class="sat-item">'
                f'<div class="sat-name"><span>{s["name"]}</span><span class="badge {badge}">{s["type"]}</span></div>'
                f'<div class="sat-meta">'
                f'<span>{s["alt_km"]} km alt</span>'
                f'<span>El {s["elevation"]}° Az {s["azimuth"]}°</span>'
                f'<span style="color:{status_color}">{status_txt}</span>'
                f'</div>'
                f'<div class="prog"><div class="prog-fill" style="width:{el_pct}%;background:{color};"></div></div>'
                f'</div>'
            )
            sat_items.append(item)
        sat_html = ''.join(sat_items)
        if sat_html:
            st.markdown(f'<div class="sat-list-scroll">{sat_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("No additional satellite data available.")

    st.markdown('<div class="section-hd" style="margin-top:24px;">📡 Data sources</div>', unsafe_allow_html=True)
    src_links = [
        ('https://opensky-network.org', 'OpenSky Network (ADS-B)'),
        ('https://api.adsb.lol', 'adsb.lol (fallback)'),
        ('https://celestrak.org', 'Celestrak (TLE data)'),
        ('https://photon.komoot.io', 'Photon (geocoding)'),
        ('https://in-the-sky.org/satmap_worldmap.php', 'In-The-Sky.org'),
        ('https://www.n2yo.com', 'N2YO satellite passes'),
    ]
    src_html = '<div style="display:flex; flex-direction:column; gap:6px;">' + ''.join(
        f'<a class="src" href="{url}" target="_blank" style="display:block;">↗ {label}</a>'
        for url, label in src_links
    ) + '</div>'
    st.markdown(src_html, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer-row">
  <div>
    <span class="src-lbl">Quick links:</span>
    <a class="src" href="https://www.flightradar24.com" target="_blank">FlightRadar24</a>
    <a class="src" href="https://flightaware.com" target="_blank">FlightAware</a>
    <a class="src" href="https://satellitetracker3d.com" target="_blank">SatelliteTracker3D</a>
    <a class="src" href="https://in-the-sky.org/satmap_worldmap.php" target="_blank">In-The-Sky.org</a>
  </div>
  <a class="isro-link" href="https://www.isro.gov.in/" target="_blank">🛰️ ISRO — isro.gov.in</a>
</div>
""", unsafe_allow_html=True)
