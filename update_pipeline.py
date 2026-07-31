import pandas as pd
from sqlalchemy import create_engine
from scraper_etl import scrape_all_athletes, transform_data
import os
from datetime import datetime

DB_URL = os.environ["DB_URL"]
username = os.environ["TILASTOPAJA_USERNAME"]
password = os.environ["TILASTOPAJA_PASSWORD"]

CURRENT_YEAR = datetime.now().year

engine = create_engine(DB_URL)

events = pd.read_csv(
    "config/tilastopaja_event_codes.csv"
)

for _, row in events.iterrows():

    event_code = row["Code"]
    event_name = row["Event"]

    for sex in ["1", "2"]:

        print(
            f"UPDATE {event_name} sex={sex}"
        )

        raw_df = scrape_all_athletes(
            username,
            password,
            str(event_code),
            sex,
            leaderboard_years=[
                str(y) for y in range(2022, CURRENT_YEAR + 1)
            ],
            data_years=[
                str(CURRENT_YEAR)
            ]
        )

        df = transform_data(
            raw_df,
            str(event_code),
            sex
        )

        # Read existing competitions for this event/sex/year
        existing = pd.read_sql(
            """
            SELECT DISTINCT
                athlete,
                event_code,
                sex_code,
                year,
                location,
                date
            FROM athlete_trials
            WHERE event_code = %(event_code)s
            AND sex_code = %(sex)s
            AND year = %(year)s
            """,
            engine,
            params={
                "event_code": str(event_code),
                "sex": sex,
                "year": str(CURRENT_YEAR)
            }
        )

        key_cols = [
            "athlete",
            "event_code",
            "sex_code",
            "year",
            "location",
            "date"
        ]

        # Find competitions not already in the database
        new_df = (
            df.merge(
                existing,
                on=key_cols,
                how="left",
                indicator=True
            )
            .query("_merge == 'left_only'")
            .drop(columns="_merge")
        )

        if new_df.empty:
            print("No new competitions found.")
        else:
            new_df.to_sql(
                "athlete_trials",
                engine,
                if_exists="append",
                index=False
            )

            print(f"Inserted {len(new_df)} new trial rows.")