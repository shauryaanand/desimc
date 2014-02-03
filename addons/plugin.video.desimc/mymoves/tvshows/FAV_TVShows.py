from TurtleContainer import Container
from common import AddonUtils, Logger
from common.DataObjects import ListItem
import sys
import urllib
import xbmc  # @UnresolvedImport
import xbmcgui  # @UnresolvedImport

FAV_TV_SHOWS_JSON_FILE = "FAV_TV_Shows.json"

def addFavouriteTVShow(request_obj, response_obj):
    addonContext = Container().getAddonContext()
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=addonContext.addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=FAV_TV_SHOWS_JSON_FILE, makeDirs=True)
    favTVShowsJsonObj = {}
    if AddonUtils.doesFileExist(filepath):
        try:
            favTVShowsJsonObj = AddonUtils.getJsonFileObj(filepath)
        except ValueError:
            AddonUtils.deleteFile(filepath)
            Logger.logError('CORRUPT FILE DELETED = ' + filepath)
    favTVShowsJsonObj[request_obj.get_data()['tvShowName']] = {"tvShowName":request_obj.get_data()['tvShowName'] , "tvShowUrl": request_obj.get_data()['tvShowUrl']}
    AddonUtils.saveObjToJsonFile(filepath, favTVShowsJsonObj)
    d = xbmcgui.Dialog()
    d.ok('TV Show favourite added successfully.', 'ENJOY!')
    
    
def removeFavouriteTVShow(request_obj, response_obj):
    addonContext = Container().getAddonContext()
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=addonContext.addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=FAV_TV_SHOWS_JSON_FILE, makeDirs=True)
    favTVShowsJsonObj = {}
    if AddonUtils.doesFileExist(filepath):
        try:
            favTVShowsJsonObj = AddonUtils.getJsonFileObj(filepath)
            del favTVShowsJsonObj[request_obj.get_data()['tvShowName']]
            AddonUtils.saveObjToJsonFile(filepath, favTVShowsJsonObj)
            d = xbmcgui.Dialog()
            d.ok('TV Show removed favourite successfully.', 'You can add this TV Show again using same way.', 'ENJOY!')
            xbmc.executebuiltin("Container.Refresh()")
        except ValueError:
            AddonUtils.deleteFile(filepath)
            Logger.logError('CORRUPT FILE DELETED = ' + filepath)
            d = xbmcgui.Dialog()
            d.ok('Failed to remove TV Show favourite.', 'Please try again.')
    
    
def displayFavouriteTVShows(request_obj, response_obj):
    addonContext = Container().getAddonContext()
    
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=addonContext.addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=FAV_TV_SHOWS_JSON_FILE, makeDirs=True)

    try:
        if AddonUtils.doesFileExist(filepath):
            favTVShowsJsonObj = AddonUtils.getJsonFileObj(filepath)
            if len(favTVShowsJsonObj) == 0:
                d = xbmcgui.Dialog()
                d.ok('No Favourites added yet!', 'Please use context menu on TV Show to add new favourite.', '')
    
            for tvShowName in favTVShowsJsonObj:
                tvShowInfo = favTVShowsJsonObj[tvShowName]
                item = ListItem()
                item.add_request_data('tvShowName', tvShowInfo['tvShowName'])
                item.add_request_data('tvShowUrl', tvShowInfo['tvShowUrl'])
                item.set_next_action_name('Show_Episodes')
                xbmcListItem = xbmcgui.ListItem(label=unicode(tvShowInfo['tvShowName']).encode("utf-8"))
                
                contextMenuItems = []
                data = '?actionId=' + urllib.quote_plus("remove_Fav_TVShow") + '&data=' + urllib.quote_plus(AddonUtils.encodeData({"tvShowName":tvShowInfo['tvShowName'], "tvShowUrl":tvShowInfo['tvShowUrl']}))
                contextMenuItems.append(('Remove favourite', 'XBMC.RunPlugin(%s?%s)' % (sys.argv[0], data)))
                xbmcListItem.addContextMenuItems(contextMenuItems, replaceItems=True)
                item.set_xbmc_list_item_obj(xbmcListItem)
                response_obj.addListItem(item)
        else:
            d = xbmcgui.Dialog()
            d.ok('No favourites added yet!', 'Please use context menu on TV Show to add new favourite.', '')
        
    except:
        AddonUtils.deleteFile(filepath)
        d = xbmcgui.Dialog()
        d.ok('FAILED to display TV Shows', 'Please add favorite again.')
