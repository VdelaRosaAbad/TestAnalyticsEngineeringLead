import os
import io
import zipfile
import requests
import pandas as pd
from google.cloud import bigquery

UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"
RAW_DATASET = os.getenv("RAW_DATASET", "bank_marketing_raw")
TABLE_NAME = os.getenv("RAW_TABLE", "bank_marketing")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("BQ_LOCATION", "US")


def download_and_extract_csv() -> pd.DataFrame:
    resp = requests.get(UCI_ZIP_URL, timeout=60)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        # Prefer bank-additional-full.csv if available; otherwise bank-full.csv
        target = None
        for name in zf.namelist():
            if name.endswith("bank-additional/bank-additional-full.csv"):
                target = name
                break
        if target is None:
            for name in zf.namelist():
                if name.endswith("bank-full.csv"):
                    target = name
                    break
        if target is None:
            raise RuntimeError("No CSV found in the UCI zip")
        with zf.open(target) as f:
            df = pd.read_csv(f, sep=";", low_memory=False)
    return df


def upload_to_bigquery(df: pd.DataFrame) -> None:
    client = bigquery.Client(project=PROJECT_ID, location=LOCATION)
    table_id = f"{PROJECT_ID}.{RAW_DATASET}.{TABLE_NAME}"

    # Standardize column names (lowercase, underscores)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
        source_format=bigquery.SourceFormat.CSV,
    )

    # Use pandas to_gbq alternative via load_table_from_dataframe for control
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows to {table_id}")


def main():
    if not PROJECT_ID:
        raise EnvironmentError("GOOGLE_CLOUD_PROJECT must be set")
    df = download_and_extract_csv()
    upload_to_bigquery(df)


if __name__ == "__main__":
    main()


