#!/usr/bin/python
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

import urllib2, re, xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib

__settings__ = xbmcaddon.Addon(id='plugin.video.ruhd.tv')
__language__ = __settings__.getLocalizedString
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
handle = int(sys.argv[1])

PLUGIN_NAME = 'RuHD.TV'
SITE_HOSTNAME = 'www.ruhd.tv'
SITEPREF      = 'http://%s' % SITE_HOSTNAME
SITE_URL      = SITEPREF + '/'

phpsessid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_ruhd_tv.sess')
plotdescr_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_ruhd_tv.plot')
thumb = os.path.join( os.getcwd(), "icon.png" )

def run_once():
	global USERNAME, USERPASS
	while (Get(__language__(30008)) == None):
		user_keyboard = xbmc.Keyboard()
		user_keyboard.setHeading(__language__(30001))
		user_keyboard.doModal()
		if (user_keyboard.isConfirmed()):
			USERNAME = user_keyboard.getText()
			pass_keyboard = xbmc.Keyboard()
			pass_keyboard.setHeading(__language__(30002))
			pass_keyboard.setHiddenInput(True)
			pass_keyboard.doModal()
			if (pass_keyboard.isConfirmed()):
				USERPASS = pass_keyboard.getText()
				__settings__.setSetting('username', USERNAME)
				__settings__.setSetting('password', USERPASS)
			else:
				return False
		else:
			return False
	return True

def Get(url, ref=None):
	url = SITEPREF + url
	use_auth = False
	inter = 2
	while inter:
		cj = cookielib.CookieJar()
		h  = urllib2.HTTPCookieProcessor(cj)
		opener = urllib2.build_opener(h)
		urllib2.install_opener(opener)
		post = None
		if use_auth:
			post = urllib.urlencode({'login': USERNAME, 'password': USERPASS})
			url = SITE_URL
		request = urllib2.Request(url, post)
		request.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
		request.add_header('Host', SITE_HOSTNAME)
		request.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
		request.add_header('Accept-Language', 'ru,en;q=0.9')
		if ref != None:
			request.add_header('Referer', ref)
		if os.path.isfile(phpsessid_file):
			fh = open(phpsessid_file, 'r')
			phpsessid = fh.read()
			fh.close()
			request.add_header('Cookie', 'PHPSESSID=' + phpsessid)
		o = urllib2.urlopen(request)
		for index, cookie in enumerate(cj):
			cookraw = re.compile('<Cookie PHPSESSID=(.*?) for.*/>').findall(str(cookie))
			if len(cookraw) > 0:
				fh = open(phpsessid_file, 'w')
				fh.write(cookraw[0])
				fh.close()
		http = o.read()
		o.close()
		if (http.find('<form id="loginform" method="POST" action="/">') == -1):
			return http
		else:
			use_auth = True
		inter = inter - 1
	return None

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

def ShowSeries(url):
	http = Get(url)
	if http == None:
		xbmc.output('[%s] ShowSeries() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
		return
	http2 = re.compile('<td class="sit">(.*?)</td>', re.DOTALL).findall(http)
	if len(http2) == 0:
		xbmc.output('[%s] ShowSeries() Error 2: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
		return
	for dat2 in http2:
		(row_img, row_title ) = re.compile('<img src="(.*?)" alt="(.*?)"').findall(dat2)[0]
		row_url = re.compile('<a href="(.*?)"').findall(dat2)[0]
		Title = row_title
		rawru = re.compile(';">(.*?)</a><br>').findall(dat2)
		if len(rawru) > 0:
			Title = rawru[0]
		Thumb  = SITEPREF + row_img

		listitem = xbmcgui.ListItem(Title, iconImage = Thumb, thumbnailImage = Thumb)
		listitem.setInfo(type = "Video", infoLabels = {
			"Title":	Title
			} )
		url = sys.argv[0] + '?mode=ShowEpisodes&url=' + urllib.quote_plus(row_url) \
			+ '&title=' + urllib.quote_plus(Title)
		xbmcplugin.addDirectoryItem(handle, url, listitem, True)

def ShowEpisodes(url, title):
	http = Get(url, SITE_URL)
	if http == None:
		xbmc.output('[%s] ShowEpisodes() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
		return
	Thumbnail = thumb
	picdat = re.compile('<div id="series" style="background:.*url\(\'(.*?)\'\) no-repeat top center;">').findall(http)
	if len(picdat) > 0:
		Thumbnail = SITEPREF + picdat[0]
	else:
		xbmc.output('[%s] ShowEpisodes() Warn 1: background not found (style=background) URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
	Plot = __language__(30007)
	pldata  = re.compile('<div class="desc">(.*?)</div>', re.DOTALL).findall(http)
	if len(pldata) > 0:
		Plot = pldata[0]
		Plot = Plot.replace('&mdash;', '-')
		Plot = Plot.replace('&hellip;', '.')
		Plot = Plot.replace('&ndash;', '-')
		Plot = Plot.replace('&laquo;', '"')
		Plot = Plot.replace('&ldquo;', '"')
		Plot = Plot.replace('&ldquo;', '"')
		Plot = Plot.replace('&raquo;', '"')
		Plot = Plot.replace('<br />', '')
		Plot = Plot.replace('<br>', '')
		Plot = Plot.replace('<br/>', '')
	else:
		xbmc.output('[%s] ShowEpisodes() Warn 2: Plot not found (div class=desc) URL=%s' % (PLUGIN_NAME, url))
	if os.path.isfile(plotdescr_file):
		os.remove(plotdescr_file)
	fh = open(plotdescr_file, 'w')
	fh.write(Plot)
	fh.close()
	seasons = re.compile('<h2><span class="head">(.*?)</span></h2>\s(.*?)\s</div>', re.DOTALL).findall(http)
	if len(seasons) > 0:
		for seanum, seacont in seasons:
			srows = re.compile('<div><span class=".*">(.*?)<a href="(.*?)">(.*?)</a></span></div>').findall(seacont)
			if len(srows) > 0:
				x = 1
				for row_sernum, row_url, row_title in srows:
					ssn = __language__(30003)
					ser = __language__(30004)
					Title = ('%s %s %s %s "%s"' % (ssn.encode('utf8'), seanum, ser.encode('utf8'), str(x), row_title))
					listitem = xbmcgui.ListItem(Title, iconImage = Thumbnail, thumbnailImage = Thumbnail)
					listitem.setInfo(type="Video", infoLabels = {
						"Title": 	Title,
						"Plot": 	Plot
						} )
					url = sys.argv[0] + '?mode=ShowEpisode&url=' + urllib.quote_plus(row_url) \
						+ '&title=' + urllib.quote_plus(title + ' : ' + Title) \
						+ '&img=' + urllib.quote_plus(Thumbnail)
					xbmcplugin.addDirectoryItem(handle, url, listitem, False)
					x = x+1
			else:
				xbmc.output('[%s] ShowEpisodes() Error 2: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
				xbmc.output(seacont)
	else:
		xbmc.output('[%s] ShowEpisodes() Error 3: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)

def ShowEpisode(url, title, img):
	strid = re.compile('.*/([0-9]*)/').findall(url)
	if len(strid) > 0:
		http = Get('/GetEpisodeLink/%s/' % strid[0], SITEPREF + url)
		if http == None:
			xbmc.output('[%s] ShowEpisode() Error 1: GetEpisodeLink == None URL=%s' % (PLUGIN_NAME, url))
			return
		throw = re.compile('f="(.*?)"').findall(http)
		if len(throw) > 0:
			Plot = __language__(30007)
			if os.path.isfile(plotdescr_file):
				fh = open(plotdescr_file, 'r')
				Plot = fh.read()
				fh.close()
			playfile = throw[0]
			item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
			item.setInfo(type="Video", infoLabels = {
				"Title":	title,
				"Plot":		Plot
				} )
			xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(playfile, item)
		else:
			xbmc.output('[%s] ShowEpisode() Error 2: r.e. unable to find a link to a video! URL=%s' % (PLUGIN_NAME, url))
			xbmc.output(http)
	else:
		xbmc.output('[%s] ShowEpisode() Error 3: Episode ID - not found! URL=%s' % (PLUGIN_NAME, url))
		xbmc.output('ShowEpisode(%s, %s, %s)' % (url, title, img))


def AddGetBalance(wwwurl):
	listitem = xbmcgui.ListItem(__language__(30006), iconImage = thumb, thumbnailImage = thumb)
	url = sys.argv[0] + '?mode=ShowProfile&url=' + urllib.quote_plus(wwwurl)
	xbmcplugin.addDirectoryItem(handle, url, listitem, False)

def ShowProfile(url):
	dialog = xbmcgui.Dialog()
	www_dir = '/ShowProfile/'
	http = Get(www_dir, url)
	if http == None:
		xbmc.output('[%s] ShowProfile() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
		return
	http = http.replace('\t','')
	http = http.replace('\n','')
	raw_data = re.compile('<div class="pdays">(.*?)<br><span class="spdays" style=" background-color:.*>(.*?)</span>').findall(http)
	if len(raw_data) > 0:
		for msg, days in raw_data:
			dialog.ok(__language__(30006), msg + '\n' + days)
	else:
		xbmc.output('[%s] ShowEpisodes() Error 3: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)

def GetNews(url):
	http = Get(url)
	if http == None:
		xbmc.output('[%s] GetNews() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
		return
	raw1 = re.compile('<item>(.*?)</item>', re.DOTALL).findall(http)
	if len(raw1) == 0:
		xbmc.output('[%s] GetNews() Error 2: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		return
	x = 1
	for itemblock in raw1:
		raw_link    = re.compile('<link>(.*?)</link>').findall(itemblock)
		if len(raw_link) == 0:
			xbmc.output('[%s] GetNews() Error 3: len(raw_link) == 0 URL=%s' % (PLUGIN_NAME, url))
			return
		raw_title   = re.compile('<title>(.*?)</title>').findall(itemblock)
		if len(raw_title) == 0:
			xbmc.output('[%s] GetNews() Error 4: len(raw_title) == 0 URL=%s' % (PLUGIN_NAME, url))
			return
		raw_pubdate = re.compile('<pubDate>(.*?)</pubDate>').findall(itemblock)
		if len(raw_pubdate) == 0:
			xbmc.output('[%s] GetNews() Error 5: len(raw_pubdate) == 0 URL=%s' % (PLUGIN_NAME, url))
			return
		Title = ('%s. %s' % (str(x), raw_title[0]))
		Plot = raw_pubdate[0]
		listitem = xbmcgui.ListItem(Title, iconImage = thumb, thumbnailImage = thumb)
		listitem.setInfo(type="Video", infoLabels = {
			"Title": 	Title,
			"Plot": 	Plot
			} )
		url = sys.argv[0] + '?mode=ShowEpisode&url=' + urllib.quote_plus(raw_link[0]) \
			+ '&title=' + urllib.quote_plus(raw_title[0])
		xbmcplugin.addDirectoryItem(handle, url, listitem, False)
		x = x+1
	if os.path.isfile(plotdescr_file):
		os.remove(plotdescr_file)

def addGetNews():
	listitem = xbmcgui.ListItem(__language__(30005), iconImage = thumb, thumbnailImage = thumb)
	url = sys.argv[0] + '?mode=GetNews&url=' + urllib.quote_plus('/ShowRSS/')
	xbmcplugin.addDirectoryItem(handle, url, listitem, True)

if run_once():
	params = get_params()
	mode  = None
	url   = ''
	title = ''
	ref   = ''
	img   = ''

	try:
		mode  = urllib.unquote_plus(params["mode"])
	except:
		pass

	try:
		url  = urllib.unquote_plus(params["url"])
	except:
		pass

	try:
		title  = urllib.unquote_plus(params["title"])
	except:
		pass
	try:
		img  = urllib.unquote_plus(params["img"])
	except:
		pass

	if mode == None:
		ShowSeries(__language__(30008))
		AddGetBalance(SITE_URL)
		addGetNews()
		xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		xbmcplugin.endOfDirectory(handle)

	elif mode == 'ShowEpisodes':
		ShowEpisodes(url, title)
		xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		xbmcplugin.endOfDirectory(handle)

	elif mode == 'ShowEpisode':
		ShowEpisode(url, title, img)

	elif mode == 'ShowProfile':
		ShowProfile(url)

	elif mode == 'GetNews':
		GetNews(url)
		xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		xbmcplugin.endOfDirectory(handle)
