import frappe
from frappe.utils import nowdate

def _default_customer():
    return frappe.db.get_single_value("Selling Settings","default_customer")

def _get_price(item_code):
    price=frappe.db.get_value("Item Price",{"item_code":item_code,"selling":1},"price_list_rate")
    return price or 0

def _ensure_amounts(pos_order):
    for row in pos_order.items:
        if not row.item_name:
            row.item_name=frappe.db.get_value("Item",row.item_code,"item_name") or row.item_code
        if row.rate is None:
            row.rate=0
        if not row.rate:
            row.rate=_get_price(row.item_code)
        row.amount=(row.qty or 0)*(row.rate or 0)

@frappe.whitelist()
def create_sales_invoice_from_pos_order(doc, method=None):
    if isinstance(doc,str):
        doc=frappe.get_doc("POS Order",doc)
    if getattr(doc,"sales_invoice",None):
        return doc.sales_invoice

    _ensure_amounts(doc)

    si=frappe.new_doc("Sales Invoice")
    si.customer=doc.customer or _default_customer()
    si.set_posting_time=1
    si.posting_date=nowdate()
    si.update_stock=1
    si.is_pos=1
    for it in doc.items:
        si.append("items",{"item_code":it.item_code,"qty":it.qty,"uom":it.uom,"rate":it.rate,"warehouse":doc.outlet})
    if doc.payments:
        for p in doc.payments:
            si.append("payments",{"mode_of_payment":p.mode_of_payment,"amount":p.amount})
    si.flags.ignore_permissions=True
    si.insert()
    si.submit()
    frappe.db.set_value("POS Order",doc.name,"sales_invoice",si.name)
    return si.name
