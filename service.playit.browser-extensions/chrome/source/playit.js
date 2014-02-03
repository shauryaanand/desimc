//PlayIt core function to send data to XBMC PlayIt port
function playIt(streamReq) {
	serviceAddress = localStorage.serviceAddress
	servicePort = localStorage.servicePort
	if (!serviceAddress || !servicePort)
		myAlert('Options not set',
				'Using default values to connect. Check PlayIt extension options.')
	if (!serviceAddress) {
		serviceAddress = "apple-tv.local"
	}
	if (!servicePort) {
		servicePort = "8181"
	}

	service_url = "http://" + serviceAddress + ":" + servicePort + "/PlayIt"

	var playItService = new rpc.ServiceProxy(service_url, {
		asynchronous : true,
		protocol : "JSON-RPC",
		sanitize : false,
		methods : [ 'playHostedVideo', 'playHostedAudio' ]
	}, false);

	myAlert('Processing request',
			'Sending PlayIt request to XBMC, please wait...')

	try {

		if (streamReq.type === 'video') {
			playItService
					.playHostedVideo({
						params : {
							'videoLink' : streamReq.video_link
						},
						onSuccess : function(responseObj) {
							title = responseObj.status
							if (responseObj.title != undefined) {
								title = responseObj.title
							} else if (responseObj.status === 'success') {
								title = 'Playback started'
							} else if (responseObj.status === 'error') {
								title = 'Playback failed'
							} else if (responseObj.status === 'exception') {
								title = 'Unexpected error'
							}
							myAlert(title, responseObj.message)
						},
						onException : function(err) {
							if (err != undefined && err.code != undefined
									&& err.code === 101)
								myAlert('Network error',
										'Unable to connect or request time-out. Check PlayIt extension setting.')
							else
								myAlert('Unknown error',
										'Chrome extension is unable to process request due to error.')
							return true
						},
						onComplete : function(responseObj) {
							// nothing
						}
					});
		} else if (streamReq.type === 'audio') {
			playItService
					.playHostedAudio({
						params : streamReq,
						onSuccess : function(responseObj) {
							title = responseObj.status
							if (responseObj.title != undefined) {
								title = responseObj.title
							} else if (responseObj.status === 'success') {
								title = 'Playback started'
							} else if (responseObj.status === 'error') {
								title = 'Playback failed'
							} else if (responseObj.status === 'exception') {
								title = 'Unexpected error'
							}
							myAlert(title, responseObj.message)
						},
						onException : function(err) {
							if (err != undefined && err.code != undefined
									&& err.code === 101) {
								myAlert('Network error',
										'Unable to connect or request time-out. Check PlayIt extension setting.');
							} else if (err != undefined
									&& err.message != undefined
									&& err.message == "Method playAudio not supported.") {
								myAlert('OLD version of PlayIt Service',
										'Please check for updates of PlayIt Service add-on on XBMC.');
							} else {
								myAlert('Unknown error',
										'Chrome extension is unable to process request due to error.');
							}
							return true
						},
						onComplete : function(responseObj) {
							// nothing
						}
					});
		}

	} catch (err) {
		if (err != undefined && err.code != undefined && err.code === 101)
			myAlert('Network error',
					'Unable to connect or request time-out. Check PlayIt extension setting.')
		else
			myAlert('Unknown error',
					'Chrome extension is unable to process request due to error.')
	}

}

// Function to display HTML 5 notification to user.
function myAlert(title, msg) {
	title = 'PlayIt: ' + title;
	if (webkitNotifications.checkPermission() == 0) {
		var notification = window.webkitNotifications.createNotification(
				'Icon-48.png', title, msg);
		notification.show();
		setTimeout(function() {
			notification.cancel();
		}, 2000);
	} else {
		alert(title + ' -> ' + msg);
	}
}

// Handles context menu item on click event
function cmClickHandler(info) {
	if (info.menuItemId == "playIt") {
		if (info.linkUrl === undefined) {
			myAlert("Selection cannot be played!", info.selectionText);
		} else {
			if (info.selectionText !== undefined) {
				myAlert("Video selected", info.selectionText);
			}
			playIt({
				type : "video",
				video_link : info.linkUrl
			});
		}
	} else if (info.menuItemId == "playItFrameView") {
		playItFrameViewEnabler();
	}
}

// Handles playIt button click event
function playItRequestHandler() {
	chrome.tabs.getSelected(null, function(tab) {
		playIt({
			type : "video",
			video_link : tab.url
		});
	});
}

// Handles playIt button click event
function playItActionRequestHandler(tab) {
	if (localStorage.frameViewEnabled !== "true") {
		playIt({
			type : "video",
			video_link : tab.url
		});
	}
}

// Handles playIt Frame View button click event
function playItFrameViewEnabler() {
	myAlert("PlayIt Frame View",
			"Please click on PlayIt bar appears on top of video frame.");
	chrome.tabs.executeScript(null, {
		file : "js/jquery-2.0.0.min.js"
	}, function() {
		chrome.tabs.executeScript(null, {
			file : "view-inject.js"
		});
	});
}

// Handles playIt request from frame or embed videos
function playItRequestFromContentScript(port) {
	// This will get called by the view-inject script when frame is clicked for
	// play.
	port.onMessage.addListener(function(streamReq) {
		playIt(streamReq);
	});
}

// Add context menu item always
var playItOnXBMCContextMenuItem = {
	"type" : "normal",
	"title" : "PlayIt on XBMC",
	"id" : "playIt",
	"contexts" : [ "link", "image", "video", "audio" ],
	"onclick" : cmClickHandler
};

// Add context menu item always
var playItFrameViewContextMenuItem = {
	"type" : "normal",
	"title" : "PlayIt Frame View",
	"id" : "playItFrameView",
	"contexts" : [ "all" ],
	"onclick" : cmClickHandler
};

chrome.contextMenus.create(playItOnXBMCContextMenuItem);
chrome.contextMenus.create(playItFrameViewContextMenuItem);
chrome.runtime.onConnect.addListener(playItRequestFromContentScript);
chrome.browserAction.onClicked.addListener(playItActionRequestHandler);

if (localStorage.frameViewEnabled === undefined
		|| localStorage.frameViewEnabled === "true") {
	localStorage.frameViewEnabled = "true";
	chrome.browserAction.setPopup({
		popup : "popup.html"
	});
}
