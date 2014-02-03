
from metahandler import metahandlers, metacontainers  # @UnresolvedImport
import xbmcgui, xbmcplugin  # @UnresolvedImport
from common import XBMCInterfaceUtils
import sys


    
def retieveMovieInfoAndAddItem(request_obj, response_obj):
    items = response_obj.get_item_list()
    XBMCInterfaceUtils.callBackDialogProgressBar(getattr(sys.modules[__name__], '__addMovieInfo_in_item'), items, 'Retrieving info', 'Failed to retrieve information, please try again later')

global metaget
metaget = metahandlers.MetaData()

def __addMovieInfo_in_item(item):
    if item.get_moving_data().has_key('movieTitle'):
        title = unicode(item.get_moving_data()['movieTitle']).encode('utf-8')
        year = unicode(item.get_moving_data()['movieYear']).encode('utf-8')
        meta = metaget.get_meta('movie', title, year=year)
        xbmc_item = item.get_xbmc_list_item_obj()
        
        if(meta is not None):
            xbmc_item.setIconImage(meta['thumb_url'])
            xbmc_item.setThumbnailImage(meta['cover_url'])
            videoInfo = {'trailer_url':meta['trailer_url']}
            for key, value in meta.items():
                if key in ['genre', 'title', 'year', 'rating', 'tagline', 'writer', 'director', 'rating', 'votes', 'plot', 'duration', 'cast', 'mpaa', 'studio', 'premiered']:
                    if type(value) is str:
                        value = unicode(value).encode('utf-8')
                    videoInfo['key'] = value
            xbmc_item.setInfo('video', videoInfo)
            xbmc_item.setProperty('fanart_image', meta['backdrop_url'])
        else:
            xbmc_item.setInfo('video', {'title':title, 'year':year})

