from common import HttpUtils, AddonUtils, XBMCInterfaceUtils
from TurtleContainer import Container
from common.DataObjects import ListItem
import calendar
import re
import time
import xbmcgui  # @UnresolvedImport
import logging

FIXTURE_URL = 'http://www.willow.tv/EventMgmt/UserMgmt/FixtureArchiveHelper.asp?eid=&'

def displayFixtures(request_obj, response_obj):
    if not request_obj.get_data()['isLoginSuccess']:
        return
    items = __retrieveEventMatches__(request_obj.get_data()['target'])
    response_obj.set_item_list(items)
    

def __retrieveEventMatches__(eventTarget):
    url = FIXTURE_URL + 'target=' + eventTarget
    print url
    soup = HttpUtils.HttpClient().getBeautifulSoup(url)
    items = []
    for row in soup.findChildren(name='tr'):
        rowClass = row['class']
        if re.search('tableHeading', rowClass):
            continue
        title = ''
        matchLinks = {}
        next_action_name = ''
        if((not row.has_key('toggler')) or (row['toggler'] != 'yes')):
            matchCols = row.findChildren('td')
            localMatchDate = 'Date Not Fixed!!'
            try:
                matchDate = re.compile('CXGetLocalDateTime(.+?);').findall(matchCols[0].getText())[0]
                datetime_obj = None
                try:
                    datetime_obj = time.strptime(matchDate, "('%m/%d/%Y %H:%M:%S %Z')")
                except ValueError:
                    datetime_obj = time.strptime(matchDate, "('%d %b %Y %H:%M %Z')")
                localMatchDate = time.strftime('(%a, %b %d %Y %I:%M %p)', time.localtime(calendar.timegm(datetime_obj)))
            except Exception, e:
                logging.exception(e)
            
            title = '  ' + localMatchDate + '  ' + unicode(matchCols[1].getText()).encode('utf-8')
            
            next_action_name = 'Match_Links'
            
            for matchLink in  matchCols[2].findChildren('a'):
                iconSrc = unicode(matchLink.img['src']).encode('utf-8')
                if re.search('live.png', iconSrc):
                    matchLinks['LIVE'] = unicode(matchLink['href']).encode('utf-8')
                elif  re.search('replay.png', iconSrc):
                    matchLinks['Replay'] = unicode(matchLink['href']).encode('utf-8')
                elif  re.search('Scorebaord.png', iconSrc):
                    matchLinks['Scoreboard'] = unicode(matchLink['href']).encode('utf-8')
                elif  re.search('highlights.png', iconSrc):
                    matchLinks['Highlights'] = unicode(matchLink['href']).encode('utf-8')
        else:
            title = '[COLOR blue][B]' + row.findChild('td').getText() + '[/B][/COLOR]'
            next_action_name = 'Series'
        cricket_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=Container().getAddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='cricket-icon.png')
        item = ListItem()
        item.add_request_data('matchLinks', matchLinks)
        item.set_next_action_name(next_action_name)
        xbmcListItem = xbmcgui.ListItem(label=title, iconImage=cricket_icon_filepath, thumbnailImage=cricket_icon_filepath)
        item.set_xbmc_list_item_obj(xbmcListItem)
        items.append(item)
    return items
        

    
