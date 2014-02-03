function restoreValues(event) {
	if (localStorage.serviceAddress !== undefined) {
		$('#serviceAddress').val(localStorage.serviceAddress);
	}
	if (localStorage.servicePort !== undefined) {
		$('#servicePort').val(localStorage.servicePort);
	}
	if (localStorage.frameViewEnabled !== undefined) {
		if (localStorage.frameViewEnabled === "true") {
			$('#frameView').prop('checked', localStorage.frameViewEnabled);
		}
	} else {
		localStorage.frameViewEnabled = "true";
		$('#frameView').prop('checked', localStorage.frameViewEnabled);
		chrome.browserAction.setPopup({
			popup : "popup.html"
		});
	}
}

function defaultValues() {
	$('#serviceAddress').val("apple-tv.local");
	$('#servicePort').val("8181");
	$('#frameView').prop('checked', true);
	myAlert("Options set to default!",
		"Please press Save button to save default values.");
}

function saveValues() {
	localStorage.serviceAddress = $('#serviceAddress').val();
	localStorage.servicePort = $('#servicePort').val();
	localStorage.frameViewEnabled = $('#frameView').prop('checked');
	if (localStorage.frameViewEnabled === "true") {
		chrome.browserAction.setPopup({
			popup : "popup.html"
		});
	} else {
		chrome.browserAction.setPopup({
			popup : ""
		});
	}
	myAlert("Options saved!",
			"PlayIt extension will use saved values for further requests.");
	return false;
}

function myAlert(title, msg) {
	title = 'PlayIt: ' + title
	if (webkitNotifications.checkPermission() == 0) {
		var notification = window.webkitNotifications.createNotification(
				'Icon-128.png', title, msg);
		notification.show();
		setTimeout(function() {
			notification.cancel()
		}, 2000);
	} else {
		alert(title + ' -> ' + msg)
	}
}
$(document).ready(function() {
	restoreValues();
	$("#optionsForm").validate({
		rules : {
			serviceAddress : {
				required : true
			},
			servicePort : {
				required : true,
				maxlength : 4,
				pattern : /81[0-9]{2}/
			},
			frameViewOption : {
				required : true
			}
		},
		messages : {
			servicePort : {
				pattern : 'Invalid Input. Value Range 8100 - 8199.',
				maxlength : 'Invalid Input. Value Range 8100 - 8199.'
			}
		},
		highlight : function(element) {
			$(element).closest('.control-group').addClass('error');
		},
		success : function(element) {
			$(element).closest('.control-group').removeClass('error');
		},
		submitHandler : function(form) {
			// form.submit();
			saveValues();
		}
	});
	$('#save').click(function() {
		$("#optionsForm").submit();
	});
	$('#reset').click(defaultValues);
});
