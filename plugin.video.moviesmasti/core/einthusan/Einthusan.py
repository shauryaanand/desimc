'''
Created on May 20, 2012

@author: ajju,Kamal
'''
from TurtleContainer import Container
from common.DataObjects import ListItem
import xbmcgui  # @UnresolvedImport
from common import AddonUtils, Logger, EnkDekoder
import base64
import re
import sys
from urllib import urlopen
import BeautifulSoup
from moves import SnapVideo
from snapvideo import Dailymotion, YouTube, GoogleDocs
from common import XBMCInterfaceUtils
try:
    import json
except ImportError:
    import simplejson as json
from common import HttpUtils


BASE_WSITE_URL = base64.b64decode('aHR0cDovL3d3dy5laW50aHVzYW4uY29tLw==')
pageDict = {0:25, 1:50, 2:100}
TITLES_PER_PAGE = pageDict[int(Container().getAddonContext().addon.getSetting('moviesPerPage'))]



def listMovies(request_obj, response_obj):
    categoryUrlSuffix = request_obj.get_data()['categoryUrlSuffix']
   
    page = None
    if request_obj.get_data().has_key('page'):
        page = int(request_obj.get_data()['page'])
    
    titles = Container().getAddonContext().cache.cacheFunction(retrieveMovies, categoryUrlSuffix)
    
    count = -1
    start = 0
    current_page = -1
    total_pages = -1
    if len(titles) > TITLES_PER_PAGE:
        count = 0
        current_page = 1
        total_pages = int(len(titles) / TITLES_PER_PAGE)
        if len(titles) % TITLES_PER_PAGE:
            total_pages = total_pages + 1
        if page is not None:
            current_page = int(page)
            start = (current_page - 1) * TITLES_PER_PAGE
    end = start + TITLES_PER_PAGE
    items = []
    for entry in titles:
        if count > -1:
            if count < start:
                count = count + 1
                continue
            elif count >= end:
                break
            else:
                count = count + 1
        titleInfo = entry['info']
        year = ''
                
        movieInfoUrl = entry['link']
        movieLabel = '[B]' + titleInfo + '[/B]' + ('(' + year + ')' + quality if (year != '') else '')
      
        item = ListItem()
        item.add_moving_data('movieTitle', titleInfo)
        item.add_moving_data('movieYear', year)
        item.add_request_data('movieTitle', titleInfo)
        item.add_request_data('movieInfoUrl', movieInfoUrl)
        item.set_next_action_name('Movie_Streams')
        xbmcListItem = xbmcgui.ListItem(label=movieLabel, label2='(' + year + ')')
        item.set_xbmc_list_item_obj(xbmcListItem)
        items.append(item)
        response_obj.addListItem(item)
    
    if current_page > 0 and current_page < total_pages:
        next_page = current_page + 1
        item = ListItem()
        item.add_request_data('page', next_page)
        item.add_request_data('categoryUrlSuffix', request_obj.get_data()['categoryUrlSuffix'])
        item.set_next_action_name('Next_Page')
        xbmcListItem = xbmcgui.ListItem(label='  ---- next page ----  #' + str(next_page) + ' ->')
        item.set_xbmc_list_item_obj(xbmcListItem)
        response_obj.addListItem(item)
    
    response_obj.set_xbmc_content_type('movies')
    
'''
Cached function to retrieve HD movies
'''
def retrieveMovies(categoryUrlSuffix):
    loopCount = 10
    titles = []
    
    if categoryUrlSuffix == 'BluRay' :
        XBMCInterfaceUtils.displayDialogMessage('HD Movies', 'Bluray movies not supported at the moment!', msgType='[B]INFO & REQUEST: [/B]')
        return titles

    queryParms = '&organize=Activity&filtered=RecentlyPosted&org_type=Activity'
    print categoryUrlSuffix
    if categoryUrlSuffix.find('_') > 0 :
        options_url = re.compile("(.+?)_(.*)").findall(categoryUrlSuffix)
        categoryUrlSuffix = options_url[0][1]
        if options_url[0][0].isdigit():
            queryParms = '&organize=Year&filtered=' + options_url[0][0] + '&org_type=Year'
        else:
            queryParms = '&organize=Alphabetical&filtered=' + options_url[0][0] + '&org_type=Alphabetical'    
    
    webpage = urlopen(BASE_WSITE_URL + 'movies/index.php?lang=' + categoryUrlSuffix + queryParms)
    soup2 = BeautifulSoup.BeautifulSoup(webpage)
    numDiv = soup2.find('div', {'class': 'numerical-nav'})
    
    if numDiv :
        links = numDiv.findChildren('a') [-1]
        loopCount = int(links.text)
    for i in range(1, loopCount) :
        webpage = urlopen(BASE_WSITE_URL + 'movies/index.php?lang=' + categoryUrlSuffix + queryParms + '&page=' + str(i)).read()
        if re.match('page not found', webpage):
            break
        soup2 = BeautifulSoup.BeautifulSoup(webpage)
        for row in soup2('a', {'class' : 'movie-title'}) :  
            print row.contents
            titleInfo = ''.join(row.contents)
            movieInfoUrl = row['href']
            title = {}
            title['info'] = titleInfo
            title['link'] = movieInfoUrl
            titles.append(title)
    return titles


def retieveTrailerStream(request_obj, response_obj):
    soup = None
    title = None
    if request_obj.get_data().has_key('movieInfoUrl'):
        html = HttpUtils.HttpClient().getHtmlContent(url=(request_obj.get_data()['movieInfoUrl'] + '?alt=json'))
        jObj = json.loads(html)
        html = jObj['entry']['content']['$t']
        title = jObj['entry']['title']['$t']
        soup = BeautifulSoup.BeautifulSoup(html)
    elif request_obj.get_data().has_key('moviePageUrl'):
        contentDiv = BeautifulSoup.SoupStrainer('div', {'dir':'ltr'})
        soup = HttpUtils.HttpClient().getBeautifulSoup(url=request_obj.get_data()['moviePageUrl'], parseOnlyThese=contentDiv)
    if soup == None:
        return
    paramTag = soup.findChild('param', attrs={'name':'movie'}, recursive=True)
    videoLink = None
    if paramTag is not None:
        videoLink = paramTag['value']
    else:
        videoLink = soup.findChild('embed', recursive=True)['src']
    request_obj.set_data({'videoLink': videoLink, 'videoTitle':title})


def retieveMovieStreams(request_obj, response_obj):
    soup = None
    if request_obj.get_data().has_key('movieInfoUrl'):
        html = HttpUtils.HttpClient().getHtmlContent(url=(BASE_WSITE_URL + request_obj.get_data()['movieInfoUrl'][3:]))
        soup = BeautifulSoup.BeautifulSoup(html)
    elif request_obj.get_data().has_key('moviePageUrl'):
        contentDiv = BeautifulSoup.SoupStrainer('div', {'dir':'ltr'})
        soup = HttpUtils.HttpClient().getBeautifulSoup(url=request_obj.get_data()['moviePageUrl'], parseOnlyThese=contentDiv)
    if soup == None:
        return
    videoSourceLink = None
    scriptTags = []
    
    for row in soup('script', {'type':'text/javascript'}):
        if re.search('jwplayer', ''.join(row.contents)):
             jwplayer = ''.join(row.contents)
             m_obj = re.search(r'({.*})', jwplayer)
             if m_obj:
                jwplayerStr = m_obj.group(1).replace("'", "\"")
                matches = re.search('"file": "(.+?)"', jwplayerStr, re.IGNORECASE)
                if matches:
                    videoSourceLink = matches.group(1)
                    break
    
    
    XBMCInterfaceUtils.displayDialogMessage('Do you know?', 'The content of this add-on is from www.einthusan.com.', 'Please help Einthusan by visiting his website regularly.', 'The developer has no relation with www.einthusan.com. OK to proceed!', msgType='[B]INFO & REQUEST: [/B]')
    
    item = ListItem()
    item.set_next_action_name('Play')
    item.get_moving_data()['videoStreamUrl'] = videoSourceLink
    xbmcListItem = xbmcgui.ListItem(label=request_obj.get_data()['movieTitle'])
    if(request_obj.get_data().has_key('videoInfo')):
        meta = request_obj.get_data()['videoInfo']
        xbmcListItem.setIconImage(meta['thumb_url'])
        xbmcListItem.setThumbnailImage(meta['cover_url'])
        xbmcListItem.setInfo('video', meta)
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)
    