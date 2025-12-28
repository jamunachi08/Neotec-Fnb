import frappe
def create_kds_ticket_from_pos_order(doc, method=None):
    if isinstance(doc,str):
        doc=frappe.get_doc("POS Order",doc)
    ticket=frappe.new_doc("KDS Ticket")
    ticket.pos_order=doc.name
    ticket.outlet=doc.outlet
    for it in doc.items:
        ticket.append("items",{"item_code":it.item_code,"qty":it.qty,"station":it.kitchen_station or "General","prep_status":"Queued"})
    ticket.insert(ignore_permissions=True)
    return ticket.name
