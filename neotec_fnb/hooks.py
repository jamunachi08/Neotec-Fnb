app_name="neotec_fnb"
app_title="Neotec F&B Suite"
app_publisher="Neotec"
app_description="Restaurant POS + Tables + Split Bills + KDS (MVP)"
app_email="support@neotec.example"
app_license="MIT"

fixtures=[
  {"dt":"Module Def","filters":[["name","in",["Neotec F&B"]]]},
  {"dt":"Website Route","filters":[["route","like","neotec-docs%"]]},
]

doc_events={
  "POS Order":{
    "on_submit":[
      "neotec_fnb.api.pos.create_sales_invoice_from_pos_order",
      "neotec_fnb.kds.router.create_kds_ticket_from_pos_order",
      "neotec_fnb.tables.logic.on_pos_order_submit_update_table_session",
    ],
    "on_cancel":[
      "neotec_fnb.tables.logic.on_pos_order_cancel_reopen_or_adjust",
    ],
  }
}
