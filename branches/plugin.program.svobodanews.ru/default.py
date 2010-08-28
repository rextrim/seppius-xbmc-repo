#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2010 Kostynoy S. aka Seppius
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
import urllib, urllib2, re, sys, os
import xbmcplugin, xbmcgui, xbmcaddon

fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
icon   = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
pluginhandle = int(sys.argv[1])
xbmcplugin.setPluginFanart(pluginhandle, fanart)

def clean(name):
	remove=[('&ndash;',''),('<ul>',''),('</ul>',''),('" target="_blank">',' '),('<a href="',''),('</a>',''),('<br>',''),('<br />',''),('<div>',''),('</div>',''),('<strong>',' '),('</strong>',' '),('<span>',' '),('</span>',' '),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-'),('<nobr>',''),('</nobr>',''),('<p>',''),('</p>','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def getURL(url):
	xbmc.output('def getURL(%s)'%url)
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent','Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
		req.add_header('Accept','text/html, application/xml, application/xhtml+xml, */*')
		req.add_header('Accept-Language', 'ru,en;q=0.9')
		response = urllib2.urlopen(req)
		link = response.read()
		response.close()
	except urllib2.URLError, e:
		xbmcgui.Dialog().ok('HTTP ERROR', str(e))
		return None
	else:
		return link


def RssParser(http):

	item_count = 0
	titles = []
	descriptions = []
	links = []
	guids = []
	pubDates = []
	categorys = []
	comments = []
	if http != None:
		region_1 = re.compile('<item>(.*?)</item>', re.DOTALL).findall(http)
		if len(region_1) > 0:
			for region in region_1:
				current_title       = ''
				current_description = 'No description'
				current_link        = ''
				current_guid        = ''
				current_pubDate     = 'No pub Date'
				current_category    = 'No category'
				current_comments    = 'No comments'
				current_title_raw       = re.compile('<title>(.*?)</title>').findall(region)
				current_description_raw = re.compile('<description>(.*?)</description>', re.DOTALL).findall(region)
				current_link_raw        = re.compile('<link>(.*?)</link>').findall(region)
				current_guid_raw        = re.compile('<guid>(.*?)</guid>').findall(region)
				current_pubDate_raw     = re.compile('<pubDate>(.*?)</pubDate>').findall(region)
				current_category_raw    = re.compile('<category>(.*?)</category>').findall(region)
				current_comments_raw    = re.compile('<comments>(.*?)</comments>', re.DOTALL).findall(region)
				if (len(current_title_raw) > 0) and (current_guid_raw > 0):
					item_count += 1
					current_title       = current_title_raw[0]
					if len(current_description_raw) > 0:
						current_description = current_description_raw[0]
					if len(current_link_raw) > 0:
						current_link = current_link_raw[0]
					current_guid        = current_guid_raw[0]
					if len(current_pubDate_raw) > 0:
						current_pubDate = current_pubDate_raw[0]
					if len(current_category_raw) > 0:
						current_category = current_category_raw[0]
					if len(current_comments_raw) > 0:
						current_comments = current_comments_raw[0]
					titles.append(current_title)
					descriptions.append(clean(current_description))
					links.append(current_link)
					guids.append(current_guid)
					pubDates.append(current_pubDate)
					categorys.append(current_category)
					comments.append(current_comments)
	return item_count, titles, descriptions, links, guids, pubDates, categorys, comments


def RSSRoot(url):
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_TITLE)
	r1 = re.compile('</h5>(.*?)</div><div class=\'rsspage_links\'><a class=\'addico linksmall\' href=\'(.*?)\'>').findall(getURL(url))
	x=1
	for rssTitle, rssUrl in r1:
		rssUrl = rssUrl.replace('count=50','count=100')
		#xbmc.output('rssTitle=%s' % rssTitle)
		#xbmc.output('  rssUrl=%s' % rssUrl)

		uri = sys.argv[0] + '?mode=RSSShow'
		uri += "&url="       + urllib.quote_plus(rssUrl)
		uri += "&name="      + urllib.quote_plus(rssTitle)
#		uri += "&season="    + urllib.quote_plus(str(seasonnumber))
#		uri += "&episode="   + urllib.quote_plus(str(episodenumber))
#		uri += "&premiered=" + urllib.quote_plus(date)
		uri += "&plot="      + urllib.quote_plus(rssTitle)
		#uri += "&thumbnail=" + urllib.quote_plus(thumbnail)
		item=xbmcgui.ListItem(('%s. %s'%(x,rssTitle)), iconImage = icon)#, thumbnailImage = thumbnail)
		item.setInfo( type="Video", infoLabels={"Title": rssTitle,
							#"Season":season,
							#"Episode":episode,
							#"premiered":date,
							"Plot":rssTitle
							#"TVShowTitle": 'Debilizator.TV : '+ rssTitle
							})
		#item.setProperty('IsPlayable', 'true')
		item.setProperty('fanart_image', fanart)
		xbmcplugin.addDirectoryItem(handle = pluginhandle, url = uri, isFolder = True, listitem = item)
		x += 1
	xbmcplugin.endOfDirectory(pluginhandle)




def RSSShow(url, name):
	#xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_TITLE)
	(item_count, titles, descriptions, links, guids, pubDates, categorys, comments) = RssParser(getURL(url))
	if item_count > 0:
		for x in range(item_count):
			Title       = titles[x]
			Description = descriptions[x]
			Link        = links[x]
			Guid        = guids[x]
			PubDate     = pubDates[x]
			Category    = categorys[x]
			Comment     = comments[x]
			#xbmc.output('      Title = %s' % Title)
			#xbmc.output('Description = %s' % Description)
			#xbmc.output('       Link = %s' % Link)
			#xbmc.output('       Guid = %s' % Guid)
			#xbmc.output('    PubDate = %s' % PubDate)
			#xbmc.output('   Category = %s' % Category)
			#xbmc.output('    Comment = %s' % Comment)

			uri = sys.argv[0] + '?mode=ShowPage'
			uri += "&url="       + urllib.quote_plus(Guid)
			uri += "&name="      + urllib.quote_plus(Title)
	#		uri += "&season="    + urllib.quote_plus(str(seasonnumber))
	#		uri += "&episode="   + urllib.quote_plus(str(episodenumber))
	#		uri += "&premiered=" + urllib.quote_plus(date)
			uri += "&plot="      + urllib.quote_plus(Description)
			#uri += "&thumbnail=" + urllib.quote_plus(thumbnail)
			item=xbmcgui.ListItem('%s. %s' % ((x+1),Title), iconImage = icon)#, thumbnailImage = thumbnail)
			item.setInfo( type="Video", infoLabels={"Title": Title,
								#"Season":season,
								#"Episode":episode,
								#"premiered":date,
								"Plot":Description
								#"TVShowTitle": 'Debilizator.TV : '+ rssTitle
								})
			item.setProperty('IsPlayable', 'true')
			item.setProperty('fanart_image', fanart)
			xbmcplugin.addDirectoryItem(handle = pluginhandle, url = uri, isFolder = True, listitem = item)
	xbmcplugin.endOfDirectory(pluginhandle)
########################



def ShowPage(url, name, plot):
	print 'def ShowPage(url, name, plot): %s' % url
	r1 = re.compile('<a class=\'downloadico linksmall showdownload\' href=\'(.*?)\' >').findall(getURL(url))
	#
	stacked_url = 'stack://'
	for cur_url in r1:
		xbmc.output('PLAY URL= %s'%scur_url)
		stacked_url += cur_url + ' , '
	stacked_url = stacked_url[:-3]
	print stacked_url
	item=xbmcgui.ListItem(name, thumbnailImage=thumbnail, path=stacked_url)
	item.setInfo( type="Video", infoLabels={"Title": name,
					  #      "Season":season,
					    #   "Episode":episode,
					    #    "premiered":premiered,
						"Plot":plot,
						"TVShowTitle":name
						})
	xbmcplugin.setResolvedUrl(pluginhandle, True, item)


'''
var flashvars = {
	configFilePath : "/GetFlashXml.aspx?param=9547|user|video", defvolume: getVolume()	};


GET /GetFlashXml.aspx?param=9545|user|video HTTP/1.1\r\n
<?xml version="1.0" encoding="utf-8"?>
<playlist title="Video" hideDelay="5"  topImageLeftUrl="http://www.svobodanews.ru/video/9545.html"><media type="video" id="9545" watermark="0"> <title><![CDATA[   -  1]]></title><description><![CDATA[        .       .]]></description><mediaSource value="http://flashvideo.rferl.org/Flashvideo/c/c4/c4950360-e51f-45e3-a00e-7aec94ca8810.flv" ></mediaSource><videoPreviewImage value="http://flashvideo.rferl.org/Flashvideo/thumbnail/c/c4/c4950360-e51f-45e3-a00e-7aec94ca8810.flv.jpg" ></videoPreviewImage><playMode value="user"/><fullscreen value="on"/><protocol value="http"/><videoUrl value="http://www.svobodanews.ru/video/9545.html"></videoUrl><videoUrlLabel value="  :"></videoUrlLabel><embedCode><![CDATA[<object><embed src="http://www.svobodanews.ru/flash/MediaPlayer.swf?cache=" type="application/x-shockwave-flash" wmode="transparent" width="512" height="357" allowfullscreen="true" flashvars="configFilePath=http://www.svobodanews.ru/GetFlashXml.aspx?param=9545|user|video%26skin=embeded" /></object>]]></embedCode><embedCodeLabel value="  :"></embedCodeLabel></media></playlist>
'''






'''

def playVideo(url, name, thumbnail, plot):
    response = getURL(url)
    print 'response=' + response
    SWFObject = 'http://debilizator.tv/' + re.compile('new SWFObject\(\'(.*?)\'').findall(response)[0]
    print 'SWFObject = ' + SWFObject
    stacked_url = 'stack://'

    flashvars = re.compile('so.addParam\(\'flashvars\',\'(.*?)\'\);').findall(response)[0] + '&'
    print 'flashvars = ' + flashvars
    flashparams = flashvars.split('&')
    print flashparams

    param={}
    for i in range(len(flashparams)):
	splitparams={}
	splitparams=flashparams[i].split('=')
	if (len(splitparams))==2:
	    param[splitparams[0]]=splitparams[1]

    print param
    rtmp_file     = param['file']
    rtmp_streamer = param['streamer']
    rtmp_plugins  = param['plugins']

    print '        rtmp_file =' + rtmp_file
    print '    rtmp_streamer =' + rtmp_streamer
    print '     rtmp_plugins =' + rtmp_plugins

    furl = rtmp_streamer + '/' + rtmp_file  + " swfurl=" + SWFObject + " swfvfy=true"# + " pageUrl=" + url + "  playPath=" + rtmp_file
    stacked_url += furl + ' , '
    stacked_url = stacked_url[:-3]
    print stacked_url
    item=xbmcgui.ListItem(name, thumbnailImage=thumbnail, path=stacked_url)
    item.setInfo( type="Video", infoLabels={"Title": name,
                                      #      "Season":season,
                                         #   "Episode":episode,
                                        #    "premiered":premiered,
                                            "Plot":plot,
                                            "TVShowTitle":name
                                            })
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
'''

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass

try:
    name=urllib.unquote_plus(params["name"])
except:
    name=''

try:
    mode=params["mode"]
except:
    pass

try:
    thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
    thumbnail=''

try:
    season=int(params["season"])
except:
    season=0

try:
    episode=int(params["episode"])
except:
    episode=0

try:
    premiered=urllib.unquote_plus(params["premiered"])
except:
    premiered=''

try:
    plot=urllib.unquote_plus(params["plot"])
except:
    plot=''

print "====== Mode: "+str(mode)
print "====== URL: "+str(url)
print "====== Name: "+str(name)

#if mode=='BIG':
#	ShowPage(url, name, plot)

if mode=='RSSShow':
	RSSShow(url, name)

elif mode=='ShowPage':
	ShowPage(url, name, plot)
#    print "Episodes"
#    episodes(url)
#elif mode==2:
#    print "Get Rtmp"
#elif mode==3:
#    print "Random Episode"
#    randomEpisode(url)
else:
	RSSRoot('http://www.svobodanews.ru/rsspage.aspx')
	#Root('http://debilizator.tv/')





