import os
import datetime as dt
from google.cloud import bigquery

import os

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("BQ_LOCATION", "US")
AUDIT_DATASET = os.getenv("AUDIT_DATASET", "bank_marketing_dm")
AUDIT_TABLE = os.getenv("AUDIT_TABLE", "data_quality_audits")


CREATE_TABLE_SQL = f"""
CREATE SCHEMA IF NOT EXISTS `{PROJECT_ID}.{AUDIT_DATASET}`;
CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{AUDIT_DATASET}.{AUDIT_TABLE}` (
  audit_timestamp TIMESTAMP,
  check_name STRING,
  status STRING,
  details STRING
);
"""


INSERT_AUDIT_SQL = f"""
INSERT INTO `{PROJECT_ID}.{AUDIT_DATASET}.{AUDIT_TABLE}`
  (audit_timestamp, check_name, status, details)
VALUES
  (@ts, @check_name, @status, @details)
"""


def ensure_table(client: bigquery.Client) -> None:
    for statement in CREATE_TABLE_SQL.split(";"):
        stmt = statement.strip()
        if not stmt:
            continue
        client.query(stmt).result()


def record_check(client: bigquery.Client, check_name: str, status: str, details: str) -> None:
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ts", "TIMESTAMP", dt.datetime.now(dt.UTC)),
            bigquery.ScalarQueryParameter("check_name", "STRING", check_name),
            bigquery.ScalarQueryParameter("status", "STRING", status),
            bigquery.ScalarQueryParameter("details", "STRING", details),
        ]
    )
    client.query(INSERT_AUDIT_SQL, job_config=job_config).result()


def run_basic_audits() -> None:
    if not PROJECT_ID:
        raise EnvironmentError("GOOGLE_CLOUD_PROJECT must be set")
    client = bigquery.Client(project=PROJECT_ID, location=LOCATION)

    # Example audits against the DM model (created by dbt) bank_marketing_dm.customer_kpis
    # 1) No nulls in customer_id
    q1 = f"""
    SELECT COUNT(1) AS null_count
    FROM `{PROJECT_ID}.bank_marketing_dm.customer_kpis`
    WHERE customer_id IS NULL
    """
    null_count = list(client.query(q1).result())[0][0]
    record_check(client, "customer_id_not_null", "PASS" if null_count == 0 else "FAIL", f"nulls={null_count}")

    # 2) conversion_rate between 0 and 1
    q2 = f"""
    SELECT COUNT(1) AS out_of_range
    FROM `{PROJECT_ID}.bank_marketing_dm.customer_kpis`
    WHERE conversion_rate < 0 OR conversion_rate > 1 OR conversion_rate IS NULL
    """
    oor = list(client.query(q2).result())[0][0]
    record_check(client, "conversion_rate_range", "PASS" if oor == 0 else "FAIL", f"out_of_range={oor}")

    # 3) successful_contacts_count non-negative
    q3 = f"""
    SELECT COUNT(1) AS negatives
    FROM `{PROJECT_ID}.bank_marketing_dm.customer_kpis`
    WHERE successful_contacts_count < 0 OR successful_contacts_count IS NULL
    """
    neg = list(client.query(q3).result())[0][0]
    record_check(client, "successful_contacts_count_non_negative", "PASS" if neg == 0 else "FAIL", f"negatives={neg}")


if __name__ == "__main__":
    run_basic_audits()


