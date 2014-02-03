from common import XBMCInterfaceUtils,HttpUtils,AddonUtils
import xbmcgui  # @UnresolvedImport


def displayLinks(request_obj, response_obj):
    if not request_obj.get_data()['isLoginSuccess']:
        return
    matchLinks = request_obj.get_data()['matchLinks']
    if len(matchLinks) == 0:
        XBMCInterfaceUtils.displayDialogMessage('Match not started yet', 'Error: This match is not started.', 'Please verify match schedule.')
        return
    
    d = xbmcgui.Dialog()
    index = d.select('What do you wanna watch:', matchLinks.keys())
    key = matchLinks.keys()[index]
    print 'SELECTED : ' + key
    url = matchLinks[key]
    soup = HttpUtils.HttpClient().getBeautifulSoup(url)
    print soup
    
