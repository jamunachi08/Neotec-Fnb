import frappe
from frappe.utils import now

def _get_open_session(table_name):
    return frappe.db.get_value("Neotec Table Session",{"table":table_name,"status":"Open"},"name")

def _create_session(pos_order):
    s=frappe.new_doc("Neotec Table Session")
    s.outlet=pos_order.outlet
    s.floor=pos_order.floor
    s.table=pos_order.table
    s.opened_on=now()
    s.status="Open"
    s.insert(ignore_permissions=True)
    return s.name

def _ensure_check(session_name, check_no):
    existing=frappe.db.get_value("Neotec Check",{"session":session_name,"check_no":check_no,"status":"Open"},"name")
    if existing: return existing
    c=frappe.new_doc("Neotec Check")
    c.session=session_name
    c.check_no=check_no
    c.status="Open"
    c.insert(ignore_permissions=True)
    return c.name

def on_pos_order_submit_update_table_session(pos_order, method=None):
    if isinstance(pos_order,str):
        pos_order=frappe.get_doc("POS Order",pos_order)
    if not pos_order.table: return
    session=_get_open_session(pos_order.table) or _create_session(pos_order)
    frappe.db.set_value("POS Order",pos_order.name,"table_session",session)
    check_no=pos_order.check_no or 1
    check=_ensure_check(session,check_no)
    frappe.db.set_value("POS Order",pos_order.name,"check",check)
    for it in pos_order.items:
        ci=frappe.new_doc("Neotec Check Item")
        ci.parent=check; ci.parenttype="Neotec Check"; ci.parentfield="items"
        ci.item_code=it.item_code; ci.qty=it.qty; ci.rate=it.rate
        ci.amount=(it.qty or 0)*(it.rate or 0)
        ci.allocation_type="Normal"
        ci.insert(ignore_permissions=True)

def on_pos_order_cancel_reopen_or_adjust(pos_order, method=None):
    return

@frappe.whitelist()
def add_shared_item(session, item_code, qty, rate, allocations):
    qty=float(qty); rate=float(rate)
    total_amount=qty*rate
    sa=frappe.new_doc("Neotec Shared Allocation")
    sa.session=session; sa.item_code=item_code; sa.qty=qty; sa.rate=rate; sa.total_amount=total_amount
    for a in allocations:
        sa.append("allocations",{"check":a.get("check"),"percent":a.get("percent"),"amount":a.get("amount")})
    sa.insert(ignore_permissions=True)
    for a in sa.allocations:
        part_amount=0
        if a.amount: part_amount=float(a.amount)
        elif a.percent: part_amount=(float(a.percent)/100.0)*total_amount
        ci=frappe.new_doc("Neotec Check Item")
        ci.parent=a.check; ci.parenttype="Neotec Check"; ci.parentfield="items"
        ci.item_code=item_code; ci.qty=qty; ci.rate=rate; ci.amount=part_amount
        ci.allocation_type="Shared"; ci.source_allocation=sa.name
        ci.insert(ignore_permissions=True)
    return sa.name
