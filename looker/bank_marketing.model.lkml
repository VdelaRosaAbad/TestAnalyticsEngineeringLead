connection: "bigquery"

includes: ["views/*.view.lkml", "explores/*.explore.lkml"]

label: "Bank Marketing"

explore: customer_kpis {
  from: customer_kpis
}

explore: data_quality_audits {
  from: data_quality_audits
}

