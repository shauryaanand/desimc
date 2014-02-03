//Context menu listener
document.addEventListener("contextmenu", handleContextMenu, false);
// This function adds information about the hyperlink on which context menu
// opened.
function handleContextMenu(event) {
	var linkElement = undefined;
	var currentElement = event.target;
	while (currentElement != null) {
		if (currentElement.nodeName == 'A') {
			linkElement = currentElement;
			break;
		}
		currentElement = currentElement.parentNode;
	}
	if (linkElement != undefined) {
		safari.self.tab.setContextMenuEventUserInfo(event, [ linkElement.href,
				linkElement.textContent.trim() ]);
	}
}
