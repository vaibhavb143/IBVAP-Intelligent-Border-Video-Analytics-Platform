# 🛡️ IBVAP — Intelligent Border Video Analytics Platform

> **"Transforming Existing CCTV Infrastructure into an Autonomous AI-Driven Border Defense Network"**  
> *Real-time Computer Vision • Edge Analytics • Facial Recognition (FRS) • ANPR • Virtual Fence Intrusion • Behavioral Threat Intelligence*

---

## 📌 Problem Statement & Solution Overview

### The Challenge
Border security forces deploy standard CCTV cameras across Border Out Posts (BOPs), checkposts, and strategic perimeter lines. However, conventional CCTV systems only offer passive video recording, requiring continuous human observation. Advanced capabilities like **Facial Recognition Systems (FRS)**, **Automatic Number Plate Recognition (ANPR)**, **Intrusion Detection**, and **Behavioral Tracking** typically require expensive proprietary hardware and specialized smart cameras, making large-scale deployment unfeasible in remote border terrain.

### The IBVAP Solution
**IBVAP** is a software-defined, AI-driven surveillance command platform that transforms **existing legacy CCTV cameras and IP/RTSP streams** into an intelligent, automated perimeter defense system without requiring hardware replacements.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      IBVAP EDGE SURVEILLANCE PIPELINE                            │
│                                                                                  │
│  [ Existing CCTV / RTSP / USB Feeds ]                                            │
│                 │                                                                │
│                 ▼                                                                │
│  [ AI Edge Analytics & Computer Vision Layer ]                                   │
│  ├── 👤 Human Detection & Tracking                                              │
│  ├── 🚗 Vehicle Classification (Car, SUV, Truck, Bus, Van, Bike)                 │
│  ├── 🎯 Facial Recognition System (FRS Biometric Watchlist Matching)             │
│  ├── 🔍 ANPR / OCR License Plate Scanning & Watchlist Intercepts                 │
│  ├── ⚡ Virtual Fence & Tripwire Intrusion Detection                             │
│  ├── 🚷 Behavioral Analytics (Low-Crawl, Loitering, Contraband Drops, Surges)    │
│  └── 🌙 Thermal / Night-Time Movement Detection (Curfew Hours)                   │
│                 │                                                                │
│                 ▼                                                                │
│  [ Tactical Threat Scoring Engine (0-100) & Automated Alert Dispatch ]           │
│                 │                                                                │
│        ┌────────┴─────────────────────────┐                                      │
│        ▼                                  ▼                                      │
│  [ Live Tactical Command HUD ]      [ Django Unfold Super Admin ]                │
│  (For Field Duty Officers)          (For Base Commanders & Admins)               │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Core Features & Capabilities

### 1. 🛡️ Real-Time Perimeter Intrusion & Virtual Tripwire
- Configurable virtual tripwire zones across boundary sectors.
- Instant threat alerts when unauthorized personnel cross restricted lines.

### 2. 🎯 Biometric Facial Recognition System (FRS) & Suspect Watchlist
- Real-time facial detection and biometric feature vector matching.
- Dedicated **Persons of Interest / Suspect Watchlist** (`WatchlistPerson`) categorizing *Cross-Border Infiltrators*, *Smugglers*, *Fugitives*, and *POW / Detainees*.
- Priority threat tags (*Critical Immediate Intercept*, *High Risk*, *Under Investigation*).

### 3. 🚗 Automated Number Plate Recognition (ANPR) & Vehicle Radar
- Real-time optical character recognition (OCR) of vehicle registration plates.
- Vehicle classification (*Sedan, SUV, Truck, Motorcycle, Cargo Van*).
- Instant cross-referencing against the **Border Vehicle Watchlist** (`WatchlistVehicle`) with speed and vector estimates.

### 4. 🚷 Behavioral & Suspicious Activity Analytics
- Autonomous detection of tactical and suspicious movement patterns:
  - 🚷 `CRAWLING_CONCEALMENT`: Low-crawl / prone movement across vegetation.
  - 📦 `SUSPICIOUS_PACKAGE_DROP`: Unattended contraband or blast hazard quarantine.
  - 🚶 `PERIMETER_LOITERING`: Reconnaissance loitering near zero-line (>180s).
  - 👥 `CROWD_SURGE`: Abnormal clustering at gate checkpoints.

### 5. 🌙 Night-Time & Thermal Vision Monitoring
- Scheduled curfew windows (e.g. 22:00 – 05:00) with heightened threat multipliers for nocturnal movement detection.

### 6. 🗺️ Tactical Sector Radar & Geospatial BOP Map
- Interactive map plotting Border Observation Posts (BOPs) with live operational status (*Normal, Elevated, High, Critical*).

### 7. 📈 Threat Intelligence & Analytics Dashboard
- 6 Chart.js interactive visualizations covering hourly breach frequencies, sector threat heatmaps, camera uptime readiness, and alert triage timelines.

### 8. ⚙️ Django Unfold Command Super Admin Console
- Modern, high-tech admin backend powered by **`django-unfold`**:
  - Live Border Telemetry HUD (Feeds Online %, Active Critical Threats, Radar Hits).
  - Bulk actions (*Activate AI Modules*, *Set Status Online/Standby*, *Acknowledge Incidents*).
  - Tabbed fieldsets, audit history, and role-based access control.

---

## 🛠 Technology Stack

- **Frontend**: HTML5, Vanilla CSS (Custom Dark Glassmorphism), JavaScript (ES6+), Bootstrap 5, Chart.js, Bootstrap Icons, Material Symbols
- **Backend**: Python 3.11, Django 5.x, Django REST Framework (DRF)
- **Super Admin**: Django Unfold (v0.91+) with Tailwind-styled Command Telemetry HUD & Bulk Actions
- **Database**: SQLite3 (Local / Edge Deployments) & PostgreSQL (Production Cloud via `dj-database-url`)
- **Hosting & Deployment**: Render Cloud Platform, Gunicorn 21.x WSGI Server, WhiteNoise Asset Compression
- **AI & Video Analytics**: Facial Recognition System (FRS), ANPR / OCR, Virtual Tripwire Intrusion, Behavioral Analytics (Low-Crawl, Package Drops, Loitering), Night Thermal Vision
- **Data Visualization & Mapping**: Chart.js 6-Graph Intelligence Suite, Interactive Geospatial Sector Map

---

## 🗂 Project Directory Structure

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
├── ibvap_core/                # Project Settings, URLs, ASGI & WSGI
│   ├── settings.py           # Unfold Theme, INSTALLED_APPS, Database Config
│   ├── urls.py               # Root URL Dispatcher
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/             # Officer Auth, User Profiles, Roles (Admin/Officer)
│   ├── dashboard/            # Tactical Command HUD & Live Camera Stream Grid
│   ├── cameras/              # Camera Node Registry & Edge AI Toggles (FRS, ANPR, Behavior)
│   ├── alerts/               # Real-Time Alert Triage & Officer Dispatch Queue
│   ├── events/               # Forensic Security Event Logs & Evidence Dossier
│   ├── anpr/                 # License Plate Scans & OCR Match Pipeline
│   ├── watchlist/            # Dual-Tab Intelligence Watchlist (FRS Suspects + ANPR Vehicles)
│   ├── map/                  # Interactive Geospatial BOP Sector Map
│   ├── analytics/            # Threat Intelligence Charts & Analytics
│   ├── settings_app/         # Curfew Windows & Threat Scoring Weight Calibration
│   └── core/                 # Admin Dashboard Callbacks, Context Processors & Seed Commands
│       └── management/commands/
│           ├── seed_demo_data.py       # Baseline Demo Data Seeder
│           └── seed_hackathon_demo.py  # FRS, Behavioral & Infiltrator Data Seeder
├── static/
│   ├── css/main.css          # Dark SOC Theme, Cyber Accents, Glassmorphic Panels
│   └── js/                   # Live Tickers, Chart.js Visuals, Map & Alert Controllers
└── templates/
    ├── base.html             # Main Tactical Frame (Topbar & Sidebar)
    ├── admin/index.html      # Custom Unfold Command Telemetry HUD
    ├── accounts/login.html   # Dedicated Radar HUD Login with 1-Click Demo Chips
    ├── dashboard/index.html  # Live Command Center HUD
    ├── cameras/index.html    # Multi-Cam Grid & Module Switches
    ├── watchlist/index.html  # Dual-Tab Biometric FRS & Vehicle Registry
    ├── alerts/index.html     # Incident Triage Board
    ├── events/index.html     # Forensic Incident Audit Logs
    ├── anpr/index.html       # ANPR Live Scans Hub
    ├── map/index.html        # Tactical BOP Sector Map
    ├── analytics/index.html  # Threat Analytics Suite
    └── settings_app/index.html
```

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone Repository & Setup Environment
```bash
# Clone the repository
git clone https://github.com/vaibhavb143/IBVAP-Intelligent-Border-Video-Analytics-Platform.git
cd IBVAP-Intelligent-Border-Video-Analytics-Platform

# Create and activate virtual environment (Optional but Recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Realistic Hackathon Demonstration Data
Populates the database with default officer accounts, tactical border camera feeds, FRS suspects, behavioral breach events, ANPR scans, and priority alerts:
```bash
python manage.py seed_demo_data
python manage.py seed_hackathon_demo
```

### 6. Start the Server
```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🔐 Demonstration Credentials

| Account Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `ibvap@2026` | Full Platform + Django Unfold Super Admin (`/admin/`) |
| **Border Security Officer** | `officer_singh` | `ibvap@2026` | Tactical Command HUD, Camera Feeds, Alert Triage, Watchlists |

*Note: The login page at `/auth/login/` features **1-Click Quick Demo Autofill Chips** (`[🛡️ Admin]` and `[👮 Officer]`) for effortless presentation.*

---

## 🌐 Site Route Map

| Page / Module | URL Route | Description |
| :--- | :--- | :--- |
| **Officer Terminal Login** | `/auth/login/` | Encrypted authentication with isolated radar scanner & 1-click demo chips. |
| **Live Command HUD** | `/` | Real-time threat gauge, active camera streams, and incident telemetry. |
| **Multi-Cam Grid** | `/cameras/` | Live feed management with individual AI module toggles (Human, ANPR, FRS, Behavior, Night). |
| **Biometric & ANPR Watchlists** | `/watchlist/` | Dual-tab target registry for **FRS Suspects** and **Vehicle Targets**. |
| **Security Alerts Triage** | `/alerts/` | Incident response inbox with *Acknowledge* and *Resolve* workflows. |
| **Forensic Event Audit Log** | `/events/` | Immutable log of all detected incursions, coordinates, and confidence ratings. |
| **ANPR Radar Scans** | `/anpr/` | Real-time OCR license plate detection logs with vehicle classification. |
| **Tactical Sector Map** | `/map/` | Geospatial map plotting Border Observation Posts (BOPs) with status markers. |
| **Threat Analytics** | `/analytics/` | 6 Chart.js graphs tracking intrusion trends and sector risk metrics. |
| **System Preferences** | `/settings/` | Night detection window and threat scoring algorithm weights. |
| **Django Unfold Super Admin** | `/admin/` | High-tech command console with live surveillance telemetry HUD. |

---

## ☁️ Production Deployment (Render-Ready)

IBVAP is fully configured for automated cloud deployment on **Render**:

1. Push your code to GitHub.
2. In the Render Dashboard, create a **New Web Service** and connect this repository.
3. Configure the build parameters:
   - **Environment**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn ibvap_core.wsgi:application`
4. Environment Variables (optional):
   - `DEBUG`: `False`
   - `SECRET_KEY`: `<your-production-secret-key>`
   - `DATABASE_URL`: `(PostgreSQL Connection String or leave blank for SQLite)`

`build.sh` automatically installs dependencies, runs migrations, collects static assets, and seeds the demonstration dataset.

---

## 📄 License & Intellectual Property

Developed for the **Smart India Hackathon (SIH)**.  
Project: **IBVAP — Intelligent Border Video Analytics Platform**  
*All rights reserved.*
