document
		.write('<object type="application/x-growl-safari-bridge" width="0" height="0" id="growl-safari-bridge"></object>');
// Get the element
window.GrowlSafariBridge = document.getElementById('growl-safari-bridge');

// Set up the Listener
safari.application.addEventListener("command", performCommand, false);
// Function to perform when event is received
function performCommand(event) {
	// Make sure event comes from the button
	if (event.command == "execute-playIt") {
		active_url = safari.application.activeBrowserWindow.activeTab.url;
		playIt(active_url);
	} else if (event.command == "execute-playIt-cm") {
		myAlert('Video selected', event.userInfo[1]);
		playIt(event.userInfo[0]);
	} else if (event.command == "execute-playIt-view"
			|| event.command == "execute-playIt-view-btn") {
		myAlert('PlayIt Frame View',
				'Please click on PlayIt bar appears on top of video frame.');
		event.currentTarget.activeBrowserWindow.activeTab.page.dispatchMessage(
				"showFrameView",
				"Please click on PlayIt bar appears on top of video frame.");
	}
}

// Handling PlayIt messages from current window in Frame View
// Respond to message from PlayIt
function respondToMessage(theMessageEvent) {
	if (theMessageEvent.name === "playIt") {
		playIt(theMessageEvent.message);
	}
}
safari.application.addEventListener("message", respondToMessage, false);

// Adding context menu item programmatically, for hyperlink adds context menu
// item runtime.
function handleContextMenu(event) {
	if (event.userInfo != undefined) {
		event.contextMenu.appendContextMenuItem("execute-playIt-cm",
				"PlayIt on XBMC");
	}
}
safari.application.addEventListener("contextmenu", handleContextMenu, false);

function playIt(active_url) {
	service_url = "http://" + safari.extension.settings.serverip + ":"
			+ safari.extension.settings.serviceport + "/PlayIt"

	var playItService = new rpc.ServiceProxy(service_url, {
		asynchronous : true,
		protocol : "JSON-RPC",
		sanitize : false,
		methods : [ 'ping', 'playHostedVideo', 'playVideo' ]
	}, false);

	myAlert('Processing request',
			'Sending PlayIt request to XBMC, please wait...')
	try {
		playItService
				.playHostedVideo({
					params : {
						'videoLink' : active_url
					},
					onSuccess : function(responseObj) {
						title = responseObj.status
						if (responseObj.status === 'success')
							title = 'Playback started'
						else if (responseObj.status === 'error')
							title = 'Playback failed'
						else if (responseObj.status === 'exception')
							title = 'Unexpected error'
						myAlert(title, responseObj.message)
					},
					onException : function(err) {
						if (err != undefined && err.code != undefined
								&& err.code === 101)
							myAlert('Network error',
									'Unable to connect or request timed-out. Check PlayIt extension setting.')
						else
							myAlert('Unknown error',
									'Safari extension is unable to process request due to error.')
						return true
					},
					onComplete : function(responseObj) {
						// nothing
					}
				})

	} catch (err) {
		if (err != undefined && err.code != undefined && err.code === 101)
			myAlert('Network error',
					'Unable to connect or request timed-out. Check PlayIt extension setting.')
		else
			myAlert('Unknown error',
					'Safari extension is unable to process request due to error.')
	}

}

function myAlert(title, msg) {
	title = 'PlayIt: ' + title
	// Check if the plug-in is available
	if (GrowlSafariBridge.notify !== undefined) {
		// Notify
		GrowlSafariBridge.notify(title, msg, {
			isSticky : 0,
			priority : 0,
			imageUrl : 'http://s17.postimage.org/726c9l44f/playit.png'
		})
	} else {
		alert(title + ' -> ' + msg)
	}
}