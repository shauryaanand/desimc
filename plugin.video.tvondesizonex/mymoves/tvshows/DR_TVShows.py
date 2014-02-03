'''
Created on Dec 4, 2011

@author: ajju
'''
from TurtleContainer import Container
from common import AddonUtils, XBMCInterfaceUtils, HttpUtils, ExceptionHandler, \
    Logger
from common.DataObjects import ListItem
from common.HttpUtils import HttpClient
from moves import SnapVideo
from snapvideo import Dailymotion, GoogleDocs, Playwire, Putlocker
import BeautifulSoup
import base64
import re
import sys
import time
import urllib
import xbmcgui  # @UnresolvedImport
import xbmcplugin  # @UnresolvedImport


'''
Creating a JSON object in following format:
{
    channelName:
    {
        iconimage: imgURL,
        channelType: IND|PAK,
        running_tvshows_url: running_tvshowUrl,
        finished_tvshows_url: finished_tvshowUrl,
        running_tvshows: [ {name: tvshowName, url: tvshowUrl}, {name: tvshowName2, url: tvshowUrl2} ]
        finished_tvshows: [ {name: tvshowName, url: tvshowUrl}, {name: tvshowName2, url: tvshowUrl2} ]
    }
}
'''

PREFERRED_DIRECT_PLAY_ORDER = [Dailymotion.VIDEO_HOSTING_NAME, Playwire.VIDEO_HOSTING_NAME, Putlocker.VIDEO_HOSTING_NAME]
CHANNELS_JSON_FILE = 'DR_Channels_v4.json'
OLD_CHANNELS_JSON_FILE = 'DR_Channels_v3.json'
CHANNEL_TYPE_IND = 'IND'
CHANNEL_TYPE_PAK = 'PAK'
BASE_WSITE_URL = base64.b64decode('aHR0cDovL3d3dy5kZXNpcnVsZXoubmV0')

def __retrieveTVShows__(tvShowsUrl):
    tvShows = []
    if tvShowsUrl is None:
        return tvShows
    tvShowsUrl = BASE_WSITE_URL + tvShowsUrl
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'forumbits', 'class':'forumbits'})
    soup = HttpClient().getBeautifulSoup(url=tvShowsUrl, parseOnlyThese=contentDiv)
    for tvShowTitleTag in soup.findAll('h2', {'class':'forumtitle'}):
        aTag = tvShowTitleTag.find('a')
        tvshowUrl = str(aTag['href'])
        if tvshowUrl[0:4] != "http":
            tvshowUrl = BASE_WSITE_URL + '/' + tvshowUrl
        tvshowName = aTag.getText()
        if not re.search('Past Shows', tvshowName, re.IGNORECASE):
            tvShows.append({"name":HttpUtils.unescape(tvshowName), "url":tvshowUrl})
    return tvShows
    
    
def __retrieveChannelTVShows__(tvChannelObj):
    running_tvshows = []
    finished_tvshows = []
    try:
        running_tvshows = __retrieveTVShows__(tvChannelObj["running_tvshows_url"])
        if(len(running_tvshows) == 0):
            running_tvshows.append({"name":"ENTER TO VIEW :: This is the only easy way to view!", "url":BASE_WSITE_URL + tvChannelObj["running_tvshows_url"]})
    except Exception, e:
        Logger.logFatal(e)
        Logger.logDebug('Failed to load a channel... Continue retrieval of next tv show')
    try:
        finished_tvshows = __retrieveTVShows__(tvChannelObj["finished_tvshows_url"])
    except Exception, e:
        Logger.logFatal(e)
        Logger.logDebug('Failed to load a channel... Continue retrieval of next tv show')
    tvChannelObj["running_tvshows"] = running_tvshows
    tvChannelObj["finished_tvshows"] = finished_tvshows
        

def retrieveTVShowsAndSave(request_obj, response_obj):
    oldfilepath = AddonUtils.getCompleteFilePath(baseDirPath=Container().getAddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=OLD_CHANNELS_JSON_FILE, makeDirs=True)
    AddonUtils.deleteFile(oldfilepath)
    
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=Container().getAddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE, makeDirs=True)
    refresh = Container().getAddonContext().addon.getSetting('drForceRefresh')
    if refresh == None or refresh != 'true':
        lastModifiedTime = AddonUtils.getFileLastModifiedTime(filepath)
        if lastModifiedTime is not None:
            diff = long((time.time() - lastModifiedTime) / 3600)
            if diff < 720:
                return
            else:
                Logger.logNotice(CHANNELS_JSON_FILE + ' was last created 30 days ago, refreshing data.')
    else:
        Logger.logNotice(CHANNELS_JSON_FILE + ' request to force refresh data. ')
    tvChannels = {"UTV Stars":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/uu/utv_stars.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=1274",
                   "finished_tvshows_url": "/forumdisplay.php?f=1435"},
                  "Star Plus":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_plus.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=42",
                   "finished_tvshows_url": "/forumdisplay.php?f=209"},
                  "Zee TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/zz/zee_tv.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=73",
                   "finished_tvshows_url": "/forumdisplay.php?f=211"},
                  "Sony TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/set_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=63",
                   "finished_tvshows_url": "/forumdisplay.php?f=210"},
                  "Life OK":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ll/life_ok_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=1375",
                   "finished_tvshows_url": "/forumdisplay.php?f=1581"},
                  "Star Jalsha":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_jalsha.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=667",
                   "finished_tvshows_url": "/forumdisplay.php?f=1057"},
                  "Sahara One":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/sahara_one.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=134",
                   "finished_tvshows_url": "/forumdisplay.php?f=213"},
                  "Colors":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/cc/colors_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=176",
                   "finished_tvshows_url": "/forumdisplay.php?f=374"},
                  "Sab TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/sony_sab_tv.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=254",
                   "finished_tvshows_url": "/forumdisplay.php?f=454"},
                  "MTV (India/Pakistan)":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/mm/mtv_india.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=339",
                   "finished_tvshows_url": "/forumdisplay.php?f=532"},
                  "Bindass TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/uu/utv_bindass.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=504",
                   "finished_tvshows_url": "/forumdisplay.php?f=960"},
                  "Channel [V]":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/cc/channel_v_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=633",
                   "finished_tvshows_url": "/forumdisplay.php?f=961"},
                  "DD National":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/dd/dd_national.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=535",
                   "finished_tvshows_url": "/forumdisplay.php?f=801"},
                  "Ary Digital":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/aa/atn_ary_digital.jpg",
                   "channelType": "PAK",
                   "running_tvshows_url": "/forumdisplay.php?f=384",
                   "finished_tvshows_url": "/forumdisplay.php?f=950"},
                  "GEO TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/gg/geo_tv.jpg",
                   "channelType": "PAK",
                   "running_tvshows_url": "/forumdisplay.php?f=413",
                   "finished_tvshows_url": "/forumdisplay.php?f=894"},
                  "HUM TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/hh/hum_tv.jpg",
                   "channelType": "PAK",
                   "running_tvshows_url": "/forumdisplay.php?f=448",
                   "finished_tvshows_url": "/forumdisplay.php?f=794"},
                  "A PLUS":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/aa/a_plus.jpg",
                   "channelType": "PAK",
                   "running_tvshows_url": "/forumdisplay.php?f=1327",
                   "finished_tvshows_url": "/forumdisplay.php?f=1334"},
                  "POGO":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/pp/pogo.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=500",
                   "finished_tvshows_url": None},
                  "Disney Channel":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/dd/disney_channel_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=479",
                   "finished_tvshows_url": None},
                  "Hungama TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/hh/hungama.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=472",
                   "finished_tvshows_url": "/forumdisplay.php?f=2102"},
                  "Cartoon Network":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/cc/cartoon_network_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=509",
                   "finished_tvshows_url": None},
                  "Star Pravah":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_pravah.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=1138",
                   "finished_tvshows_url": "/forumdisplay.php?f=1466"},
                  "Zee Marathi":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/zz/zee_marathi.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=1299",
                   "finished_tvshows_url": "/forumdisplay.php?f=1467"},
                  "Star Vijay":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_vijay_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=1609",
                   "finished_tvshows_url": "/forumdisplay.php?f=1747"},
                  "ZEE Bangla":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/zz/zee_bangla.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=676",
                   "finished_tvshows_url": "/forumdisplay.php?f=802"},
                  "Mahuaa TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/mm/mahuaa_bangla.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=772",
                   "finished_tvshows_url": "/forumdisplay.php?f=803"},
                  "Movies":
                  {"iconimage":"http://2.bp.blogspot.com/-8IURT2pXsb4/T5BqxR2OhfI/AAAAAAAACd0/cc5fwuEQIx8/s1600/the_movies.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=260",
                   "finished_tvshows_url": None},
                  "Latest & HQ Movies":
                  {"iconimage":"http://2.bp.blogspot.com/-8IURT2pXsb4/T5BqxR2OhfI/AAAAAAAACd0/cc5fwuEQIx8/s1600/the_movies.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=20",
                   "finished_tvshows_url": None},
                  "Awards & Concerts":
                  {"iconimage":"https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQGOu4sxdHNUQC8BUic5rcuMB3VbHf864dKIF7g65aNc2ozDxQQ",
                   "channelType": "IND",
                   "running_tvshows_url": "/forumdisplay.php?f=36",
                   "finished_tvshows_url": None},
                }
    
    XBMCInterfaceUtils.callBackDialogProgressBar(getattr(sys.modules[__name__], '__retrieveChannelTVShows__'), tvChannels.values(), 'Retrieving channel TV Shows', 'Failed to retrieve video information, please try again later', line1='Takes about 5 minutes first time', line3='Refreshes data every month or on force refresh or on new add-on version')
    # save tvChannels in moving data
    request_obj.get_data()['tvChannels'] = tvChannels
    status = AddonUtils.saveObjToJsonFile(filepath, tvChannels)
    if status is not None:
        Logger.logNotice('Saved status = ' + str(status))
    Container().getAddonContext().addon.setSetting('drForceRefresh', 'false')


def displayTVChannels(request_obj, response_obj):
    channelsList = None
    if request_obj.get_data().has_key('tvChannels'):
        channelsList = request_obj.get_data()['tvChannels']
    else:
        channelsList = getTVChannelsList()
    if channelsList is None:
        raise Exception(ExceptionHandler.TV_CHANNELS_NOT_LOADED, 'Please delete data folder from add-on user data folder.')
    displayChannelType = int(Container().getAddonContext().addon.getSetting('drChannelType'))
    for channelName in channelsList:
        channelObj = channelsList[channelName]
        if ((displayChannelType == 1 and channelObj['channelType'] == CHANNEL_TYPE_IND) 
            or (displayChannelType == 2 and channelObj['channelType'] == CHANNEL_TYPE_PAK) 
            or (displayChannelType == 0)):
            item = ListItem()
            item.add_request_data('channelName', channelName)
            item.add_request_data('channelType', channelObj['channelType'])
            item.set_next_action_name('TV_Shows')
            xbmcListItem = xbmcgui.ListItem(label=channelName, iconImage=channelObj['iconimage'], thumbnailImage=channelObj['iconimage'])
            item.set_xbmc_list_item_obj(xbmcListItem)
            response_obj.addListItem(item)
            
    response_obj.set_xbmc_sort_method(xbmcplugin.SORT_METHOD_LABEL)
        

def displayTVShows(request_obj, response_obj):
    channelsList = getTVChannelsList()
    channelObj = channelsList[request_obj.get_data()['channelName']]
    channelType = request_obj.get_data()['channelType']
    if channelObj.has_key('running_tvshows'):
        items = __displayTVShows__(channelObj['running_tvshows'], channelType)
        response_obj.extendItemList(items)
    if channelObj.has_key('finished_tvshows'):
        items = __displayTVShows__(channelObj['finished_tvshows'], channelType, True)
        response_obj.extendItemList(items)
        
        
def getTVChannelsList():
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=Container().getAddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE)
    Logger.logDebug(filepath)
    return AddonUtils.getJsonFileObj(filepath)

            
def __displayTVShows__(tvShowsList, channelType, finished=False):
    items = []
    for tvShow in tvShowsList:
        tvShowName = tvShow['name']
        if finished:
            tvShowName = tvShowName + ' [' + AddonUtils.getBoldString('finished') + '] '
        item = ListItem()
        item.add_request_data('channelType', channelType)
        item.add_request_data('tvShowName', tvShowName)
        item.add_request_data('tvShowUrl', tvShow['url'])
        item.set_next_action_name('Show_Episodes')
        xbmcListItem = xbmcgui.ListItem(label=tvShowName)
        contextMenuItems = []
        data = '?actionId=' + urllib.quote_plus("add_Fav_TVShow") + '&data=' + urllib.quote_plus(AddonUtils.encodeData({"channelType":channelType, "tvShowName":tvShowName, "tvShowUrl":tvShow['url']}))
        contextMenuItems.append(('Add to favourite shows', 'XBMC.RunPlugin(%s?%s)' % (sys.argv[0], data)))
        xbmcListItem.addContextMenuItems(contextMenuItems, replaceItems=True)
        item.set_xbmc_list_item_obj(xbmcListItem)
        items.append(item)
    return items


def __retrieveTVShowEpisodes__(threads, response_obj):
    if threads is None:
        return
    aTags = threads.findAll('a', {'class':re.compile(r'\btitle\b')})
    videoEpisodes = []
    for aTag in aTags:
        episodeName = aTag.getText()
        if not re.search(r'\b(Watch|Episode|Video|Promo)\b', episodeName, re.IGNORECASE):
            pass
        else:
            videoEpisodes.append(aTag)
            
    if len(videoEpisodes) == 0:
        videoEpisodes = aTags
        
    for aTag in videoEpisodes:
        episodeName = aTag.getText()
        item = ListItem()
        titleInfo = HttpUtils.unescape(episodeName)
        movieInfo = re.compile("(.+?)\((\d+)\)").findall(titleInfo)
        if(len(movieInfo) >= 1 and len(movieInfo[0]) >= 2):
            title = unicode(movieInfo[0][0].rstrip()).encode('utf-8')
            year = unicode(movieInfo[0][1]).encode('utf-8')
            item.add_moving_data('movieTitle', title)
            item.add_moving_data('movieYear', year)
        
        item.add_request_data('episodeName', titleInfo)
        episodeUrl = str(aTag['href'])
        if not episodeUrl.lower().startswith(BASE_WSITE_URL):
            if episodeUrl[0] != '/':
                episodeUrl = '/' + episodeUrl
            episodeUrl = BASE_WSITE_URL + episodeUrl
        item.add_request_data('episodeUrl', episodeUrl)
        item.set_next_action_name('Episode_VLinks')
        xbmcListItem = xbmcgui.ListItem(label=episodeName)
        item.set_xbmc_list_item_obj(xbmcListItem)
        response_obj.addListItem(item)

def retrieveTVShowEpisodes(request_obj, response_obj):
    Container().ga_client.reportContentUsage('dr_tvshow', request_obj.get_data()['tvShowName'])
    url = request_obj.get_data()['tvShowUrl']
    if request_obj.get_data().has_key('page'):
        url = url + '&page=' + request_obj.get_data()['page']
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'contentBody'})
    soup = HttpClient().getBeautifulSoup(url=url, parseOnlyThese=contentDiv)
    
    if not request_obj.get_data().has_key('page'):
        threads = soup.find('ol', {'class':'stickies', 'id':'stickies'})
        __retrieveTVShowEpisodes__(threads, response_obj)
    
    threads = soup.find('ol', {'class':'threads', 'id':'threads'})
    __retrieveTVShowEpisodes__(threads, response_obj)
            
    pagesDiv = soup.find('div', {'class':'threadpagenav'})
    if pagesDiv is not None:
        pagesInfoTag = pagesDiv.find('a', {'class':re.compile(r'\bpopupctrl\b')})
        if pagesInfoTag is not None:
            pageInfo = re.compile('Page (.+?) of (.+?) ').findall(pagesInfoTag.getText() + ' ')
            currentPage = int(pageInfo[0][0])
            totalPages = int(pageInfo[0][1])
            for page in range(1, totalPages + 1):
                if page != currentPage:
                    item = ListItem()
                    item.add_request_data('tvShowName', request_obj.get_data()['tvShowName'])
                    item.add_request_data('tvShowUrl', request_obj.get_data()['tvShowUrl'])
                    if page != 1:
                        item.add_request_data('page', str(page))
                    pageName = ''
                    if page < currentPage:
                        pageName = AddonUtils.getBoldString('              <-              Page #' + str(page))
                    else:
                        pageName = AddonUtils.getBoldString('              ->              Page #' + str(page))
                        
                    item.set_next_action_name('Show_Episodes_Next_Page')
                    xbmcListItem = xbmcgui.ListItem(label=pageName)
                    item.set_xbmc_list_item_obj(xbmcListItem)
                    response_obj.addListItem(item)


def retrieveVideoLinks(request_obj, response_obj):
    video_source_id = 1
    video_source_img = None
    video_source_name = None
    video_part_index = 0
    video_playlist_items = []
    ignoreAllLinks = False
    
    content = BeautifulSoup.SoupStrainer('blockquote', {'class':re.compile(r'\bpostcontent\b')})
    soup = HttpClient().getBeautifulSoup(url=request_obj.get_data()['episodeUrl'], parseOnlyThese=content)
    for e in soup.findAll('br'):
        e.extract()
    Logger.logDebug(soup)
    if soup.has_key('div'):
        soup = soup.findChild('div', recursive=False)
    prevChild = ''
    prevAFont = None
    for child in soup.findChildren():
        if (child.name == 'img' or child.name == 'b' or (child.name == 'font' and not child.findChild('a'))):
            if (child.name == 'b' and prevChild == 'a') or (child.name == 'font' and child == prevAFont):
                continue
            else:
                if len(video_playlist_items) > 0:
                    response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_source_name, video_playlist_items))
                if video_source_img is not None:
                    video_source_id = video_source_id + 1
                    video_source_img = None
                    video_source_name = None
                    video_part_index = 0
                    video_playlist_items = []
                ignoreAllLinks = False
        elif not ignoreAllLinks and child.name == 'a' and not re.search('multi', str(child['href']), re.IGNORECASE):
            video_part_index = video_part_index + 1
            video_link = {}
            video_link['videoTitle'] = 'Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) + ' | ' + child.getText()
            video_link['videoLink'] = str(child['href'])
            try:
                try:
                    __prepareVideoLink__(video_link)
                except Exception, e:
                    Logger.logFatal(e)
                    video_hosting_info = SnapVideo.findVideoHostingInfo(video_link['videoLink'])
                    if video_hosting_info is None or video_hosting_info.get_video_hosting_name() == 'UrlResolver by t0mm0':
                        raise
                    video_link['videoSourceImg'] = video_hosting_info.get_video_hosting_image()
                    video_link['videoSourceName'] = video_hosting_info.get_video_hosting_name()
                video_playlist_items.append(video_link)
                video_source_img = video_link['videoSourceImg']
                video_source_name = video_link['videoSourceName']
                
                item = ListItem()
                item.add_request_data('videoLink', video_link['videoLink'])
                item.add_request_data('videoTitle', video_link['videoTitle'])
                item.set_next_action_name('SnapAndPlayVideo')
                xbmcListItem = xbmcgui.ListItem(label='Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) , iconImage=video_source_img, thumbnailImage=video_source_img)
                item.set_xbmc_list_item_obj(xbmcListItem)
                response_obj.addListItem(item)
                prevAFont = child.findChild('font')
            except:
                Logger.logWarning('Unable to recognize a source = ' + str(video_link['videoLink']))
                video_source_img = None
                video_source_name = None
                video_part_index = 0
                video_playlist_items = []
                ignoreAllLinks = True
                prevAFont = None
        prevChild = child.name
    if len(video_playlist_items) > 0:
        response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_source_name, video_playlist_items))
        
    
    ''' Following new cool stuff is to get Smart Direct Play Feature'''
    playNowItem = __findPlayNowStream__(response_obj.get_item_list())
    if playNowItem is not None:
        request_obj.set_data({'videoPlayListItems': playNowItem.get_request_data()['videoPlayListItems']})


def __preparePlayListItem__(video_source_id, video_source_img, video_source_name, video_playlist_items):
    item = ListItem()
    item.add_request_data('videoPlayListItems', video_playlist_items)
    item.set_next_action_name('SnapAndDirectPlayList')
    item.add_moving_data('isContinuousPlayItem', True)
    item.add_moving_data('videoSourceName', video_source_name)
    xbmcListItem = xbmcgui.ListItem(label='[COLOR blue]' + AddonUtils.getBoldString('Continuous Play') + '[/COLOR]' + ' | ' + 'Source #' + str(video_source_id) + ' | ' + 'Parts = ' + str(len(video_playlist_items)) , iconImage=video_source_img, thumbnailImage=video_source_img)
    item.set_xbmc_list_item_obj(xbmcListItem)
    return item


def __prepareVideoLink__(video_link):
    video_url = video_link['videoLink']
    new_video_url = None
    video_id = re.compile('(id|url|v)=(.+?)/').findall(video_url + '/')[0][1]
    if re.search('dm(\d*).php', video_url, flags=re.I):
        new_video_url = 'http://www.dailymotion.com/video/' + video_id + '_'
    elif re.search('(flash.php|fp.php|wire.php)', video_url, flags=re.I):
        new_video_url = 'http://cdn.playwire.com/12376/embed/' + video_id + '.xml'
    elif re.search('(youtube|u|yt)(\d*).php', video_url, flags=re.I):
        new_video_url = 'http://www.youtube.com/watch?v=' + video_id + '&'
    elif re.search('megavideo', video_url, flags=re.I):
        new_video_url = 'http://www.megavideo.com/v/' + video_id + '&'
    elif re.search('put.php', video_url, flags=re.I):
        new_video_url = 'http://www.putlocker.com/file/' + video_id
    elif re.search('(weed.php|vw.php)', video_url, flags=re.I):
        new_video_url = 'http://www.videoweed.es/file/' + video_id
    elif re.search('(sockshare.com|sock.com)', video_url, flags=re.I):
        new_video_url = video_url
    elif re.search('divxstage.php', video_url, flags=re.I):
        new_video_url = 'divxstage.eu/video/' + video_id + '&'
    elif re.search('(hostingbulk|hb).php', video_url, flags=re.I):
        new_video_url = 'hostingbulk.com/' + video_id + '&'
    elif re.search('movshare.php', video_url, flags=re.I):
        new_video_url = 'movshare.net/video/' + video_id + '&'
    elif re.search('nm.php', video_url, flags=re.I):
        new_video_url = 'novamov.com/video/' + video_id + '&'
    elif re.search('tune.php', video_url, flags=re.I):
        new_video_url = 'tune.pk/play/' + video_id + '&'
        
    video_hosting_info = SnapVideo.findVideoHostingInfo(new_video_url)
    video_link['videoLink'] = new_video_url
    video_link['videoSourceImg'] = video_hosting_info.get_video_hosting_image()
    video_link['videoSourceName'] = video_hosting_info.get_video_hosting_name()

def __findPlayNowStream__(new_items):
    if Container().getAddonContext().addon.getSetting('autoplayback') == 'false':
        return None
    selectedIndex = None
    selectedSource = None
    for item in new_items:
        if item.get_moving_data().has_key('isContinuousPlayItem') and item.get_moving_data()['isContinuousPlayItem']:
            try:
                Logger.logDebug(item.get_moving_data()['videoSourceName'])
                preference = PREFERRED_DIRECT_PLAY_ORDER.index(item.get_moving_data()['videoSourceName'])
                if preference == 0:
                    selectedSource = item
                    selectedIndex = 0
                    break
                elif selectedIndex is None or selectedIndex > preference:
                    selectedSource = item
                    selectedIndex = preference
            except ValueError:
                continue
    return selectedSource
