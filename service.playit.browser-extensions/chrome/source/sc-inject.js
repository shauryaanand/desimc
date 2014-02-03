//Following script code is picked from talented Technowise SoundCloud Downloader : http://userscripts.org/scripts/review/154933

var SC_CLIENT_ID = 'b45b1aa10f1ac2941910a7f0d10f8e28';

function addPlayItButton(sound) {
	if ($(sound).find(".playIt-on-xbmc").length == 0) {
		var playItButton = $('<button></button>');
		var anchor = $(sound).find(".soundTitle__title").eq(0);
		var resolveUrl = null, buttonClass = null;
		if ($(sound).is(".single")) {
			resolveUrl = document.location.href;
			buttonClass = 'sc-button sc-button-medium sc-button-icon sc-button-responsive playIt-on-xbmc';
		} else {
			resolveUrl = 'https://soundcloud.com' + anchor.attr("href");
			buttonClass = 'sc-button sc-button-small sc-button-icon sc-button-responsive playIt-on-xbmc';
		}

		var urlSplitArray = resolveUrl.split("/");
		var lastElement = urlSplitArray.pop();
		var secretToken = '';

		if (lastElement.substr(0, 2) == 's-')// Add secret token if present.
		{
			secretToken = lastElement;
		}

		playItButton.attr({
			'title' : 'PlayIt on XBMC',
			'target' : '_blank',
			'class' : buttonClass
		});
		playItButton
				.css({
					"background-image" : 'url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAADHmlDQ1BJQ0MgUHJvZmlsZQAAeAGFVN9r01AU/tplnbDhizpnEQk+aJFuZFN0Q5y2a1e6zVrqNrchSJumbVyaxiTtfrAH2YtvOsV38Qc++QcM2YNve5INxhRh+KyIIkz2IrOemzRNJ1MDufe73/nuOSfn5F6g+XFa0xQvDxRVU0/FwvzE5BTf8gFeHEMr/GhNi4YWSiZHQA/Tsnnvs/MOHsZsdO5v36v+Y9WalQwR8BwgvpQ1xCLhWaBpXNR0E+DWie+dMTXCzUxzWKcECR9nOG9jgeGMjSOWZjQ1QJoJwgfFQjpLuEA4mGng8w3YzoEU5CcmqZIuizyrRVIv5WRFsgz28B9zg/JfsKiU6Zut5xCNbZoZTtF8it4fOX1wjOYA1cE/Xxi9QbidcFg246M1fkLNJK4RJr3n7nRpmO1lmpdZKRIlHCS8YlSuM2xp5gsDiZrm0+30UJKwnzS/NDNZ8+PtUJUE6zHF9fZLRvS6vdfbkZMH4zU+pynWf0D+vff1corleZLw67QejdX0W5I6Vtvb5M2mI8PEd1E/A0hCgo4cZCjgkUIMYZpjxKr4TBYZIkqk0ml0VHmyONY7KJOW7RxHeMlfDrheFvVbsrj24Pue3SXXjrwVhcW3o9hR7bWB6bqyE5obf3VhpaNu4Te55ZsbbasLCFH+iuWxSF5lyk+CUdd1NuaQU5f8dQvPMpTuJXYSWAy6rPBe+CpsCk+FF8KXv9TIzt6tEcuAcSw+q55TzcbsJdJM0utkuL+K9ULGGPmQMUNanb4kTZyKOfLaUAsnBneC6+biXC/XB567zF3h+rkIrS5yI47CF/VFfCHwvjO+Pl+3b4hhp9u+02TrozFa67vTkbqisXqUj9sn9j2OqhMZsrG+sX5WCCu0omNqSrN0TwADJW1Ol/MFk+8RhAt8iK4tiY+rYleQTysKb5kMXpcMSa9I2S6wO4/tA7ZT1l3maV9zOfMqcOkb/cPrLjdVBl4ZwNFzLhegM3XkCbB8XizrFdsfPJ63gJE722OtPW1huos+VqvbdC5bHgG7D6vVn8+q1d3n5H8LeKP8BqkjCtbCoV8yAAAACXBIWXMAAAE7AAABOwEf329xAAACCElEQVQ4EYWUP0ucQRCH31NPMQqGiIUeHKSyEGwSSCAQkUBQrG1t/AC5IsWVWgn5AEkf0iQhkCK9HyJYRFBQ0lwUC//i6Xl5nnXnJaLEgYed2Z397czu3VspiqICvXDV7XavGG9ZBWPSHFK6HcKeHHdiTwWn3EhCH/FlOYGjCHNl0v/ih+S/gkc5v+qY/Tion/UX8CzP1/Bfw0Tk4RfzcAJfoJ4X+vAtvyfHT/CPYAMewwpY5Sr0mmPyGDyARfhG6TMs2J6JCmpWMJxRaBy0OgzpKOQGN3bgKXxFbBkxrU2sXVwPKUffXM31dH8KafEq5/hW+B6xNRh0EYvKfFVbNE9zPNNRSJEwL9UTHZvwETFbOgVN30ueNMCmYJYc84sliDvxREu1dAX1P8ACRBvOm2eO68cwF63h3zATop0/+G5KP0jGA7Al91pAC2z3VkX/nvyOdTfYjuK74Ot+yvFnxhqPUr5a3JMiVTiEBjRJso10B4y2tQ37oFntnk6UH/0OMLcFDQR+cIm2o7mueaC/mxB2dE9bIRetQluHN4j8RCQOcT7WHRWPtRBME5bmzX+Ht4i08nPaRrRsOzvwG37BJnjRG3BCfsobIXgJI4gwFHf9ab3waZjKOf5on8NojtMngvjaEPYPGPeRJj2NuXSCE4T+kX2AZLFuSWLf933YrMrPS3zYjMs9fwETzu1L2bAAQAAAAABJRU5ErkJggg==")',
					"background-position" : "center center",
					"background-repeat" : "no-repeat"
				});

		$.getJSON("https://api.soundcloud.com/resolve.json", {
			url : resolveUrl,
			client_id : SC_CLIENT_ID,
			secret_token : secretToken
		}, function(track) {
			playItButton.click({
				trackId : track.id.toString(),
				track_title : track.title == undefined ? track.id.toString()
						: track.title.toString(),
				track_artwork_url : track.artwork_url == undefined ? ""
						: track.artwork_url.toString(),
				secret_token : secretToken,
				client_id : SC_CLIENT_ID,
				type : "audio"
			}, function(event) {
				/*
				$.getJSON("https://api.soundcloud.com/i1/tracks/"
						+ event.data.trackId + "/streams", {
					client_id : SC_CLIENT_ID,
					secret_token : event.data.secretToken
				}, function(data) {
					var playItReq = {
						type : "audio",
						track_link : data.http_mp3_128_url,
						track_title : event.data.track_title,
						track_artwork_url : event.data.track_artwork_url
					};
					chrome.runtime.connect().postMessage(playItReq);
				});
				*/
				chrome.runtime.connect().postMessage(event.data);
			});
		});
		$(sound).find(".soundActions .sc-button-group:first").eq(0).append(
				playItButton);
	}
}

function scPlayItInjector() {
	$(".sound").not(".playlist").each(function() {
		addPlayItButton(this);
	});
	// We have a playlist, add download link to each item in the playlist.
	if ($(".trackList").length > 0) {
		$(".trackList .trackList__listItem").each(function() {
			addPlayItButton(this);
		});
		$(".trackList__item").each(function() {
			addPlayItButton(this);
		});
	}
	$(document).off("mousedown");
	$(window).off("mousedown", 'a[href*="-media.soundcloud."]');
}
$(document).ready(function() {
	scPlayItInjector();
	setInterval(scPlayItInjector, 3000);
});
