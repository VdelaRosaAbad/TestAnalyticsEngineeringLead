
import os
import re
import gspread
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.cloud import bigquery

# Configuracion de Google Sheets y BigQuery
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
QUERIES_FILE = os.path.join(os.path.dirname(__file__), "queries.sql")
SPREADSHEET_NAME = "Bank Marketing KPIs"


def authenticate_gspread():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.expanduser("~/.config/gcloud/application_default_credentials.json"), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return gspread.authorize(creds)

def get_queries():
    with open(QUERIES_FILE, "r") as f:
        content = f.read()
    queries = re.split(r"^-- ", content, flags=re.MULTILINE)[1:]
    return [q.strip() for q in queries]

def run_bigquery_query(query):
    client = bigquery.Client()
    return client.query(query).to_dataframe()

def main():
    gc = authenticate_gspread()

    try:
        spreadsheet = gc.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        spreadsheet = gc.create(SPREADSHEET_NAME)
        spreadsheet.share(None, perm_type="anyone", role="writer")

    queries = get_queries()

    for query in queries:
        title_match = re.match(r"(\d+.\s*[^\n]+)", query)
        if title_match:
            title = title_match.group(1).strip()
            sql_query = query[len(title_match.group(0)):].strip()

            print(f"Running query: {title}")
            df = run_bigquery_query(sql_query)

            try:
                worksheet = spreadsheet.worksheet(title)
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=title, rows=100, cols=20)

            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            print(f"Successfully updated worksheet: {title}")

if __name__ == "__main__":
    main()
