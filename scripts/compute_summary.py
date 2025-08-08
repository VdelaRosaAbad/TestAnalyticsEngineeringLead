import os
from google.cloud import bigquery


def main() -> None:
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    client = bigquery.Client(project=project)
    table = f"{project}.bank_marketing_dm.customer_kpis"

    q = f"""
    WITH overall AS (
      SELECT
        SAFE_DIVIDE(SUM(successful_contacts_count), SUM(total_contacts)) AS conversion_rate,
        SUM(successful_contacts_count) AS successful_contacts_count,
        SUM(total_contacts) AS total_contacts
      FROM `{table}`
    ), by_segment AS (
      SELECT customer_segment,
             SAFE_DIVIDE(SUM(successful_contacts_count), SUM(total_contacts)) AS conversion_rate,
             SUM(successful_contacts_count) AS successful_contacts_count
      FROM `{table}`
      GROUP BY customer_segment
    )
    SELECT * FROM overall, by_segment
    ORDER BY by_segment.customer_segment
    """

    rows = list(client.query(q).result())

    # Build simple HTML summary
    html_lines = [
        "<h3>Bank Marketing - Resumen Diario</h3>",
        "<p>Métricas clave calculadas por dbt:</p>",
        "<ul>",
    ]
    # overall metrics are same across rows; take from first
    if rows:
        overall_conv = rows[0][0] or 0
        overall_succ = rows[0][1] or 0
        total_contacts = rows[0][2] or 0
        html_lines.append(f"<li><b>conversion_rate</b>: {overall_conv:.4f}</li>")
        html_lines.append(f"<li><b>successful_contacts_count</b>: {int(overall_succ)}</li>")
        html_lines.append(f"<li><b>total_contacts</b>: {int(total_contacts)}</li>")
    html_lines.append("</ul>")
    html_lines.append("<h4>Por segmento</h4>")
    html_lines.append("<table border='1' cellpadding='4' cellspacing='0'>")
    html_lines.append("<tr><th>customer_segment</th><th>conversion_rate</th><th>successful_contacts_count</th></tr>")
    for r in rows:
        seg = r[3]
        seg_conv = (r[4] or 0)
        seg_succ = int(r[5] or 0)
        html_lines.append(
            f"<tr><td>{seg}</td><td>{seg_conv:.4f}</td><td>{seg_succ}</td></tr>"
        )
    html_lines.append("</table>")

    print("\n".join(html_lines))


if __name__ == "__main__":
    main()


