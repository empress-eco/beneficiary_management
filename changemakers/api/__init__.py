from mimetypes import guess_type

import frappe

from changemakers.utils.form import get_doctype_title_field

MOBILE_SUPPORTED_FIELD_TYPES = [
	"Select",
	"Link",
	"Data",
	"Int",
	"Datetime",
	"Check",
	"Geolocation",
]


@frappe.whitelist()
def get_current_user_info():
	current_user = frappe.session.user
	return frappe.db.get_value(
		"User", current_user, ["first_name", "full_name"], as_dict=True
	)


@frappe.whitelist()
def get_form_fields(doctype):
	return frappe.db.get_all(
		"DocField",
		filters={
			"parenttype": "DocType",
			"parent": doctype,
			"fieldtype": ("in", MOBILE_SUPPORTED_FIELD_TYPES),
			"fieldname": ("!=", "amended_from"),
			"fetch_from": ("is", "not set"),  # TODO: handle later
		},
		fields=["label", "fieldname", "idx", "fieldtype", "reqd", "default", "options"],
		order_by="idx",
		ignore_permissions=True,
	)


@frappe.whitelist()
def get_doctype_options(doctype):
	title_field = get_doctype_title_field(doctype)

	fields = [title_field]
	if title_field != "name":
		fields.append("name")

	# maybe paginate later
	return {"docs": frappe.get_all(doctype, fields=fields), "title_field": title_field}


@frappe.whitelist()
def upload_base64_file(content, filename, dt=None, dn=None, fieldname=None):
	import base64

	from frappe.handler import ALLOWED_MIMETYPES

	decoded_content = base64.b64decode(content)
	content_type = guess_type(filename)[0]
	if content_type not in ALLOWED_MIMETYPES:
		frappe.throw("You can only upload JPG, PNG, PDF, TXT or Microsoft documents.")

	return frappe.get_doc(
		{
			"doctype": "File",
			"attached_to_doctype": dt,
			"attached_to_name": dn,
			"attached_to_field": fieldname,
			"folder": "Home",
			"file_name": filename,
			"content": decoded_content,
			"is_private": 1,
		}
	).save(ignore_permissions=True)
