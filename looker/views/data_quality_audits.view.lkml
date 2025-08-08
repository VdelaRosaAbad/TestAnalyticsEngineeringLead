view: data_quality_audits {
  sql_table_name: `${_user_attributes.google_cloud_project}.bank_marketing_dm.data_quality_audits` ;;

  dimension: audit_timestamp { type: time sql: ${TABLE}.audit_timestamp ;; }
  dimension: check_name { type: string sql: ${TABLE}.check_name ;; }
  dimension: status { type: string sql: ${TABLE}.status ;; }
  dimension: details { type: string sql: ${TABLE}.details ;; }
}

