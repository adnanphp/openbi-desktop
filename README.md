# OpenBI Desktop

> Native Linux desktop client for [OpenBI](https://github.com/adnanphp/openbi) — an end-to-end Business Intelligence platform.

[![Release](https://img.shields.io/github/v/release/adnanphp/openbi-desktop)](https://github.com/adnanphp/openbi-desktop/releases)
[![CI](https://github.com/adnanphp/openbi-desktop/actions/workflows/release.yml/badge.svg)](https://github.com/adnanphp/openbi-desktop/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Download:** [OpenBI-Desktop-0.1.0-x86_64.AppImage](https://github.com/adnanphp/openbi-desktop/releases/latest) — one file, no installation.

---

## What is this?

OpenBI Desktop is a native PySide6 application that connects to an OpenBI
API backend and provides an interactive interface for:

- **Executive KPIs** — revenue, profit, margin, orders
- **Customer intelligence** — RFM segments with revenue breakdown
- **Sales forecasting** — multi-model comparison (ETS, XGBoost, baseline)
- **Monthly trends** — 48-month revenue visualization

It is a *thin client*: all data processing, ML, and analytics happen on the
OpenBI backend (PostgreSQL, Spark, Kafka, dbt, Airflow, Superset). The
desktop app is the face.

---

## Screenshots

![1](docs/images/image1.png)
![2](docs/images/image2.png)
![3](docs/images/image3.png)
![4](docs/images/image4.png)
![5](docs/images/image5.png)
![6](docs/images/image6.png)
![7](docs/images/image7.png)
![8](docs/images/image8.png)
![9](docs/images/image9.png)
![10](docs/images/image10.png)
![11](docs/images/image11.png)
![12](docs/images/image12.png)
![13](docs/images/image13.png)



## Install

### AppImage (recommended)

```bash
wget https://github.com/adnanphp/openbi-desktop/releases/latest/download/OpenBI-Desktop-0.1.0-x86_64.AppImage
chmod +x OpenBI-Desktop-0.1.0-x86_64.AppImage
./OpenBI-Desktop-0.1.0-x86_64.AppImage
Requires FUSE 2 (libfuse2 on Ubuntu/Debian, fuse2 on Fedora).

Runs on Ubuntu 22.04+, Fedora 38+, Debian 12+, and other modern Linux distributions.

Verify
bash
wget https://github.com/adnanphp/openbi-desktop/releases/latest/download/OpenBI-Desktop-0.1.0-x86_64.AppImage.sha256
sha256sum -c OpenBI-Desktop-0.1.0-x86_64.AppImage.sha256
Requirements
The desktop app needs a running OpenBI backend. On first launch, enter the API URL:

text
http://localhost:8000
See the main OpenBI repository for backend setup.

Development
bash
git clone https://github.com/adnanphp/openbi-desktop.git
cd openbi-desktop

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python -m openbi_desktop
Tests
bash
pytest -q
Build the AppImage locally
bash
# Download appimagetool once
mkdir -p packaging/tools
wget -O packaging/tools/appimagetool-x86_64.AppImage \
  https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x packaging/tools/appimagetool-x86_64.AppImage

# Build
VERSION=0.1.0 ./packaging/build-appimage.sh
Produces OpenBI-Desktop-0.1.0-x86_64.AppImage in the repo root.

Architecture
text
┌────────────────────────────────────────────────────────┐
│  OpenBI Desktop (PySide6)                              │
│  ┌──────────┬──────────┬──────────┬──────────┐         │
│  │ Connect  │Dashboard │Customers │Forecasts │         │
│  └──────────┴──────────┴──────────┴──────────┘         │
└─────────────────────┬──────────────────────────────────┘
                      │ HTTP (httpx)
                      ▼
┌────────────────────────────────────────────────────────┐
│  OpenBI FastAPI backend                                │
│  ┌──────────────┬───────────────┬─────────────────┐    │
│  │ /kpis/*      │ /customers/*  │ /forecasts/*    │    │
│  └──────────────┴───────────────┴─────────────────┘    │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
         PostgreSQL · Spark · Kafka · dbt
Tech stack
Layer	Technology
GUI	PySide6 (Qt 6)
HTTP	httpx
Charts	QtCharts
Config	TOML (~/.config/openbi-desktop/config.toml)
Packaging	PyInstaller + appimagetool
CI/CD	GitHub Actions
Project structure
text
openbi-desktop/
├── src/openbi_desktop/
│   ├── api/              # OpenBIClient + models
│   ├── views/            # Connect, Dashboard, Customers, Forecasts
│   ├── widgets/          # KPI card
│   └── resources/        # Icons
├── packaging/
│   ├── openbi-desktop.spec      # PyInstaller recipe
│   ├── openbi-desktop.desktop   # Desktop entry
│   └── build-appimage.sh        # AppImage builder
├── tests/                # pytest suite
└── .github/workflows/
    └── release.yml       # CI: build + release AppImage
Related
OpenBI — the backend data platform

Dev.to writeup: How I Built a Two-Tier Data Platform in 9 Phases

License
MIT
