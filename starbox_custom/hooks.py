# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "starbox_custom"
app_title = "Starbox Custom"
app_publisher = "Starboxes India"
app_description = "Customisation for starbox"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hr@starboxes.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/starbox_custom/css/starbox_custom.css"
# app_include_js = "/assets/starbox_custom/js/starbox_custom.js"

# include js, css files in header of web template
# web_include_css = "/assets/starbox_custom/css/starbox_custom.css"
# web_include_js = "/assets/starbox_custom/js/starbox_custom.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "starbox_custom.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "starbox_custom.install.before_install"
# after_install = "starbox_custom.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "starbox_custom.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"starbox_custom.tasks.all"
# 	],
	"daily": [
		"starbox_custom.custom.emp_absent_today"
	],
# 	"hourly": [
# 		"starbox_custom.tasks.hourly"
# 	],
# 	"weekly": [
# 		"starbox_custom.tasks.weekly"
# 	]
# 	"monthly": [
# 		"starbox_custom.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "starbox_custom.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "starbox_custom.event.get_events"
# }

