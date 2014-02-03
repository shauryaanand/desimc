from TurtleContainer import Container
from common import AddonUtils, HttpUtils, XBMCInterfaceUtils
import time
import re
import xbmcgui  # @UnresolvedImport
import sys


LOGIN_URL = 'https://www.willow.tv/EventMgmt/UserMgmt/Login.asp'
COOKIES_FILENAME = 'CookieStore'

def login(request_obj, response_obj):
    HttpUtils.HttpClient().enableCookies()
    cookieStore = AddonUtils.getCompleteFilePath(baseDirPath=Container().getAddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=COOKIES_FILENAME, makeDirs=True)
    
    success = True
    relogin = Container().getAddonContext().addon.getSetting('relogin') == 'true'
    if not relogin:
        relogin = __checkAndLoadCookieStore__(cookieStore)
    if relogin:
        success = __loginAndSaveCookieStore__(cookieStore)

    if ((not request_obj.get_params().has_key('data')) or request_obj.get_params()['data'] == ''):
        request_obj.set_data({})
    if success:
        request_obj.get_data()['isLoginSuccess'] = True
    else:
        request_obj.get_data()['isLoginSuccess'] = False
    Container().getAddonContext().addon.setSetting('relogin', 'false')
    
    
def __checkAndLoadCookieStore__(cookieStore):
    relogin = False
    if AddonUtils.doesFileExist(cookieStore):
        HttpUtils.HttpClient().loadCookiesToFile(cookieStore)
        now = time.time()
        for cookie in HttpUtils.HttpClient().get_cookiejar():
            if ((cookie.name == 'CXUserId' or cookie.name == 'CXUserName') and cookie.is_expired(now)):
                relogin = True
    else:
        relogin = True
    return relogin
        
    
def __loginAndSaveCookieStore__(cookieStore):
    AddonUtils.deleteFile(cookieStore)
    email = Container().getAddonContext().addon.getSetting('email')
    password = Container().getAddonContext().addon.getSetting('password')
    if email == None or email == '' or password == None or password == '':
        d = xbmcgui.Dialog()
        d.ok('Welcome to Willow TV', 'Watch LIVE CRICKET on your favorite Willow TV.', 'Please provide your login details for both', 'Willow TV and YouTube.')
        Container().getAddonContext().addon.openSettings(sys.argv[ 0 ])
        return False
    params = {'Email': email, 'Password': password, 'KeepSigned': 'true', 'LoginFormSubmit': 'true'}
    html = HttpUtils.HttpClient().getHtmlContent(LOGIN_URL, params)
    HttpUtils.HttpClient().saveCookiesToFile(cookieStore)
    match = re.compile('Error: Your email or password is incorrect').findall(html)
    if(len(match) > 0):
        XBMCInterfaceUtils.displayDialogMessage('Login Failure', 'Error: Your email or password is incorrect.', 'Please verify your login details.')
        return False
    else:
        return True
