view: customer_kpis {
  sql_table_name: `${_user_attributes.google_cloud_project}.bank_marketing_dm.customer_kpis` ;;

  dimension: customer_id { primary_key: yes type: number sql: ${TABLE}.customer_id ;; }
  dimension: customer_segment { type: string sql: ${TABLE}.customer_segment ;; }
  measure: total_contacts { type: sum sql: ${TABLE}.total_contacts ;; }
  measure: successful_contacts_count { type: sum sql: ${TABLE}.successful_contacts_count ;; }
  measure: conversion_rate { type: average sql: ${TABLE}.conversion_rate ;; value_format: "0.0%" }
}

