# Tilastopaja Trial Data Scraper (pipeline)

Automated pipeline for collecting, transforming, and storing athletics trial-level performance data from Tilastopaja into a PostgreSQL database.

The project is designed to build a continuously updated database of athlete attempts across field events (e.g., long jump, high jump, throws). 

## Overview

Traditional athletics datasets often store only the best performance from each competition. This project collects **attempt-level data**, including:

* Attempt results (e.g. 5.5m)
* Fouls (`X`)
* Competition location
* Competition date
* Athlete name
* Event name (e.g. long jump)

The resulting database can be used for performance modelling, athlete profiling, and statistical analysis of competitive consistency and ability. It has been built along side my PhD project, which contains a study analysing this data.  

## Data Source

Data is scraped from:

Tilastopaja
https://www.tilastopaja.info/

The scraper requires a Tilastopaja account.

## Project Structure

```
tilastopaja-trial-scraper-pipeline/
│
├── scraper_etl.py
│   ├── Logs into Tilastopaja
│   ├── Finds athletes from event leaderboards
│   ├── Scrapes athlete competition histories
│   ├── Extracts trial-level results
│   └── Returns transformed DataFrames
│
├── initial_pipeline.py
│   └── Performs the initial historical database build
│
├── update_pipeline.py
│   └── Adds new competition results to the database
│
├── config/
│   └── tilastopaja_event_codes.csv
│
├── .github/
│   └── workflows/
│       └── update_database.yml
│
├── requirements.txt
└── README.md
```

## Pipeline Workflow

### 1. Initial Database Build

The initial pipeline performs a larger scrape covering historical seasons. This is currently set to 2022-current year. 

This creates the initial PostgreSQL database.

Run locally:

```bash
python initial_pipeline.py
```

The pipeline:

1. Reads available events from:

```
config/tilastopaja_event_codes.csv
```

2. Scrapes each event and sex category.
3. Transforms raw HTML tables into tidy trial-level data.
4. Appends results into PostgreSQL.

---

### 2. Regular Updates

The update pipeline is designed to run periodically (e.g., weekly).

Instead of re-building the database, it:

1. Scrapes the current season only.
2. Extracts new athlete competition results.
3. Appends new rows to the database.

Run locally:

```bash
python update_pipeline.py
```

The update process is intended to run automatically through GitHub Actions.

---

## Database Schema

The PostgreSQL table:

```
athlete_trials
```

contains:

| Column       | Description                       |
| ------------ | --------------------------------- |
| year         | Competition year                  |
| athlete      | Athlete name                      |
| location     | Competition location              |
| date         | Competition date                  |
| DOB          | Athlete date of birth             |
| event_name   | Athletics event                   |
| result       | Individual attempt result         |
| trial_number | Attempt number within competition |
| event_code   | Tilastopaja event code            |
| sex_code     | Athlete sex category              |

---

## Events

Events are controlled through:

```
config/tilastopaja_event_codes.csv
```

This is currently:

```csv
Event,Code
High Jump,310
Pole Vault,320
Long Jump,330
Triple Jump,340
Shot Put,350
Discus Throw,360
Hammer Throw,380
Javelin Throw,390
```

Adding a new event only requires updating this file.

---

## Environment Variables

Sensitive, required credential variables include:

```bash
TILASTOPAJA_USERNAME
TILASTOPAJA_PASSWORD
DB_URL
```

Example:

```bash
export TILASTOPAJA_USERNAME="username"
export TILASTOPAJA_PASSWORD="password"
export DB_URL="postgresql://user:password@host:port/database"
```

---

## Local Installation

Clone the repository:

```bash
git clone https://github.com/taralind/tilastopaja-trial-scraper.git

cd tilastopaja-trial-scraper
```

Create environment:

```bash
python -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## GitHub Actions

The automated update workflow:

```
.github/workflows/update_database.yml
```

runs the update pipeline on a schedule.

This is currently set to:

```yaml
schedule:
  - cron: "0 0 * * 1"
```

which runs weekly.

The workflow:

1. Creates a Python environment.
2. Installs dependencies.
3. Loads repository secrets.
4. Runs `update_pipeline.py`.
5. Updates the PostgreSQL database.

---

## Database Hosting

The PostgreSQL database is hosted using Supabase.

The database URL is stored securely as:

```
DB_URL
```

and accessed through environment variables.

---

