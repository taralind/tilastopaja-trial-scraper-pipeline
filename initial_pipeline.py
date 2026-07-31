import pandas as pd
from sqlalchemy import create_engine
from scraper_etl import scrape_all_athletes, transform_data
import os
from datetime import datetime

DB_URL = os.environ["DB_URL"]
username = os.environ["TILASTOPAJA_USERNAME"]
password = os.environ["TILASTOPAJA_PASSWORD"]

engine = create_engine(DB_URL)

events = pd.read_csv(
    "config/tilastopaja_event_codes.csv"
)


for _, row in events.iterrows():

    event_name = row["Event"]
    event_code = row["Code"]

    for sex in ["1", "2"]:

        print(
            f"INITIAL LOAD: {event_name} sex={sex}"
        )

        # extract
        raw_df = scrape_all_athletes(
            username,
            password,
            str(event_code),
            sex,
            leaderboard_years=[
                str(y) for y in range(2022, datetime.now().year + 1)
            ],
            data_years=[
                str(y) for y in range(2022, datetime.now().year + 1)
            ]
        )

        # transform
        df = transform_data(
            raw_df,
            str(event_code),
            sex
        )

        # load
        df.to_sql(
            "athlete_trials",
            engine,
            if_exists="append",
            index=False
        )

        print(
            f"Inserted {len(df)} rows"
        )