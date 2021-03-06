'''
Created on Jun 11, 2013

@author: PK
'''
from common.DataObjects import VideoHostingInfo, VideoInfo, VIDEO_QUAL_SD
from common import HttpUtils
import re

def getVideoHostingInfo():
    video_hosting_info = VideoHostingInfo()
    video_hosting_info.set_video_hosting_image('http://www.comedyportal.net/themes/berylizer/gfx/logo.png')
    video_hosting_info.set_video_hosting_name('ComedyPortal')
    return video_hosting_info

def retrieveVideoInfo(video_id):
    video_info = VideoInfo()
    video_info.set_video_hosting_info(getVideoHostingInfo())
    video_info.set_video_id(video_id)
    try:
        video_link = 'http://www.comedyportal.net/' + str(video_id)
        html = HttpUtils.HttpClient().getHtmlContent(url=video_link)
        match = re.compile("id='pl'.+?data='(.+?)'").findall(html)
        html = HttpUtils.HttpClient().getHtmlContent(url=match[0].replace(' ', '%20'))
        video_link = re.compile("file : '(.+?)'").findall(html)[0].replace(' ', '%20')
        video_info.set_video_stopped(False)
        video_info.add_video_link(VIDEO_QUAL_SD, video_link)
    except:
        video_info.set_video_stopped(True)
    return video_info