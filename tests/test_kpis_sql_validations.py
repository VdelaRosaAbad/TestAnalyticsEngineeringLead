import os
from google.cloud import bigquery


def test_customer_kpis_basic_constraints():
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    client = bigquery.Client(project=project)
    table = f"{project}.bank_marketing_dm.customer_kpis"

    q = f"""
    SELECT
      SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_ids,
      SUM(CASE WHEN conversion_rate < 0 OR conversion_rate > 1 OR conversion_rate IS NULL THEN 1 ELSE 0 END) AS bad_conversion,
      SUM(CASE WHEN successful_contacts_count < 0 OR successful_contacts_count IS NULL THEN 1 ELSE 0 END) AS bad_success
    FROM `{table}`
    """
    row = list(client.query(q).result())[0]
    assert row[0] == 0, "customer_id must be NOT NULL"
    assert row[1] == 0, "conversion_rate must be in [0,1] and NOT NULL"
    assert row[2] == 0, "successful_contacts_count must be >= 0 and NOT NULL"

