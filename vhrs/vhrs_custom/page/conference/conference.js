
frappe.pages['conference'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'VHRS Video Conference',
		single_column: true
	});
	$('<div id="meet"></div>').appendTo(this.page.main);
	$(document).ready(function () {
		var domain = "meet.jit.si";
		var options = {
			roomName: "vhrs",
			width: 1500,
			height: 500,
			parentNode: document.querySelector('#meet')
		}
		var api = new JitsiMeetExternalAPI(domain, options);
	});

}


