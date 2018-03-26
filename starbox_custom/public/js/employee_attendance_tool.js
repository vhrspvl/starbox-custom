frappe.EmployeeAttendanceTool = frappe.EmployeeAttendanceTool.extend({
    init: function (parent) {
        console.log("Hello this file is called.")
    },
})

frappe.pages['employee-attendance-tool'].on_page_load = function (wrapper) {
    frappe.employee_attendance_tool = new frappe.EmployeeAttendanceTool(wrapper);
}