# IBVAP — Intelligent Border Video Analytics Platform

> **"Transforming Existing CCTV into Intelligent Border Security"**  
> *AI-powered real-time video analytics for smarter surveillance.*

IBVAP is a border surveillance and video analytics platform developed for the **Smart India Hackathon (SIH)**. The platform upgrades existing CCTV and border outpost (BOP) optical surveillance infrastructure into an automated threat monitoring command center without replacing expensive camera hardware.

---

## 📌 Phase 1 Scope & Status

This repository contains **Phase 1** of IBVAP:
- **Implemented**: Complete Django command-center architecture, database schema, authentication & role management, Dark SOC user interface, 2x2 live/simulation camera grid (with local webcam integration), live alert triage, searchable forensic event timeline with evidence dossier modal, ANPR monitoring & vehicle watchlist manager, tactical border sector map, 6 Chart.js intelligence graphs, customizable night detection and threat weights, demo data seeder, and automated Render deployment readiness.
- **Prototype**: Rule-based threat scoring engine (92/100 calculation breakdown), simulated border camera streams, simulated OCR confidence scores.
- **Planned (Phase 2)**: Integration of YOLOv8 object detection, OpenCV video streaming pipelines, PaddleOCR plate recognition models, and WebSocket live frame push via Django Channels.

---

## 🛠 Technology Stack

- **Backend**: Python 3.11, Django 5.x, Django REST Framework
- **Frontend**: Django Templates, Bootstrap 5, Custom SOC Dark Modern CSS (Glassmorphism), Chart.js
- **Database**: SQLite3 (default zero-config local run) with seamless PostgreSQL support via `DATABASE_URL` (for Render)
- **Deployment**: Render-ready with `Procfile`, `build.sh`, `runtime.txt`, WhiteNoise static compression
- **Version Control**: Git & GitHub friendly `.gitignore`

---

## 🗂 Project Structure

```
IBVAP/
├── manage.py
├── requirements.txt
├── Procfile
├── build.sh
├── runtime.txt
├── .env.example
├── .gitignore
├── README.md
├── ibvap_core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/          # Officer Authentication, User Profiles & Roles
│   ├── dashboard/         # Command Center Dashboard, 2x2 Feed Grid, Threat Gauge
│   ├── cameras/           # Optical Feed Management & AI Module Switches
│   ├── alerts/            # Real-time Alert Triage & Acknowledgment Queue
│   ├── events/            # Historical Event Logs & Evidence Dossier Modal
│   ├── anpr/              # ANPR Extraction & Watchlist Match Spotlight
│   ├── watchlist/         # Vehicle Watchlist Intelligence Registry
│   ├── map/               # Interactive Border Sector Tactical Radar Map
│   ├── analytics/         # SOC Metrics & 6 Chart.js Intelligence Graphs
│   ├── settings_app/      # Curfew Windows & Threat Algorithm Weight Settings
│   └── core/              # Management Commands (`seed_demo_data`) & Context Processors
├── static/
│   ├── css/
│   │   └── main.css       # Dark SOC Theme, Glassmorphism, Neon HUD Reticles
│   └── js/
│       ├── main.js        # Live Clock, Sidebar Collapse, Toast Banners
│       ├── dashboard.js   # Webcam Stream Engine + Tactical Canvas Stream Simulators
│       ├── charts.js      # 6 Chart.js Visualizations
│       ├── map.js         # Interactive Map Sector Inspector
│       └── alerts.js      # AJAX Alert Actions
└── templates/
    ├── base.html          # Persistent SOC Topbar & Sidebar Layout
    ├── components/        # Navbar, Sidebar, Evidence Modal, Empty State
    ├── accounts/login.html
    ├── dashboard/index.html
    ├── cameras/index.html
    ├── alerts/index.html
    ├── events/index.html
    ├── anpr/index.html
    ├── watchlist/index.html
    ├── map/index.html
    ├── analytics/index.html
    └── settings_app/index.html
```

---

## 🚀 Quick Start & Running Locally

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Realistic SIH Demo Data
Populates the database with default admin & officer accounts, 4 tactical cameras, alerts, historical events, ANPR records, and watchlist items:
```bash
python manage.py seed_demo_data
```

### 5. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔐 Demo Credentials

| Role | Username | Password | Access Scope |
|---|---|---|---|
| **Administrator** | `admin` | `ibvap@2026` | Full SOC + Settings + User Management |
| **Security Officer** | `officer_singh` | `ibvap@2026` | Tactical Feeds, Alert Triage & Event Logs |

---

## 🌐 Deploying to Render

IBVAP is pre-configured for **1-click deployment on Render**:

1. Push this repository to GitHub.
2. In Render, create a new **Web Service** and connect your GitHub repo.
3. Configure the following settings:
   - **Environment**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn ibvap_core.wsgi:application`
4. Set Environment Variables (optional):
   - `DEBUG`: `False`
   - `SECRET_KEY`: `<your-production-secret-key>`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com`
   - `DATABASE_URL`: `(Render PostgreSQL connection string, or leave empty for SQLite)`

`build.sh` automatically installs dependencies, collects static assets, applies database migrations, and seeds the demo data.

---

## 🛡 System Pages Overview

1. **Terminal Authentication (`/auth/login/`)**: Command-center styled authentication with animated radar sweep and credentials helper.
2. **Security Command Dashboard (`/`)**: 6 KPI metric cards, 2x2 camera grid (`BOP-01` webcam + `BOP-02/03/GATE-01` simulated streams), circular Threat Intelligence gauge (92/100), live alert stream, and recent events log.
3. **Camera Management (`/cameras/`)**: Node registry with AI module switches (Human, Vehicle, ANPR, Intrusion, Night) and Add Camera modal.
4. **Security Alerts (`/alerts/`)**: Alert triage with severity filters (Critical, High, Medium, Low, Resolved) and AJAX Acknowledge/Resolve actions.
5. **Historical Events (`/events/`)**: Filterable timeline with forensic evidence dossier modal.
6. **ANPR Hub (`/anpr/`)**: Vehicle license plate detection logs with highlighted Watchlist Match card.
7. **Watchlist Intelligence (`/watchlist/`)**: Flagged target vehicle database with Add Vehicle modal.
8. **Border Tactical Map (`/map/`)**: Simulated tactical radar sector map with camera node popups.
9. **Analytics (`/analytics/`)**: 6 Chart.js graphs (Hourly events, Threat distribution, Camera activity, Detection types, ANPR trends, Weekly alerts).
10. **System Settings (`/settings/`)**: Night detection curfew window (22:00–05:00), threat scoring algorithm weights, and RBAC matrix.
