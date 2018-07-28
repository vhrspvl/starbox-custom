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
page_js = {"employee-attendance-tool": "public/js/employee_attendance_tool.js"}


# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "p
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/starbox_custom/css/starbox_custom.css"
# app_include_js = "/assets/starbox_custom/js/starbox_custom.js"

# include js, css files in headerublic/js/doctype_tree.js"}
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

doc_events = {
    # "*": {
    # 	"on_update": "method",
    # 	"on_cancel": "method",
    # 	"on_trash": "method"
    # },
    "Job Applicant": {
        "before_save": "starbox_custom.custom.calculate_total"
    },
    "Attendance": {
        "on_submit": "starbox_custom.starbox_custom.validations.attendance.onsubmit",
        # "on_update_after_submit": "starbox_custom.calculations.total_working_hours"
        "on_update_after_submit": "starbox_custom.starbox_custom.validations.attendance.updateaftersubmit"
    },
    "Leave Application": {
        "on_submit": "starbox_custom.custom.mark_on_leave",
        "on_cancel":"starbox_custom.custom.cancel_on_leave"
    }
    # "Salary Slip": {
    #     "onload": "starbox_custom.calculations.calculate_present_days"
    # }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # 	"all": [
    # 		"starbox_custom.tasks.all"
    # 	],
    "daily_long": [
        "starbox_custom.custom.emp_absent_today",
        "starbox_custom.custom.send_daily_report",
        "starbox_custom.custom.send_ctc_report",
        "starbox_custom.custom.removeduplicateatt",
        "starbox_custom.custom.mark_comp_off"
    ],
    "cron": {
        "00 10 * * *": [
            "starbox_custom.calculations.create_ts"
        ]
    },
    # "hourly": [
    #     "starbox_custom.calculations.create_ts"
    # ],
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
