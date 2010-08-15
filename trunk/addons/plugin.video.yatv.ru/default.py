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

__settings__ = xbmcaddon.Addon(id='plugin.video.yatv.ru')
__language__ = __settings__.getLocalizedString

handle = int(sys.argv[1])

PLUGIN_NAME = 'YaTV.RU'
SITE_HOSTNAME = 'yatv.ru'
SITEPREF      = 'http://%s' % SITE_HOSTNAME
SITE_URL      = SITEPREF + '/'

phpsessid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_yatv_ru.sess')
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

def Get(url, ref=None, post=None):
	url = url
	cj = cookielib.CookieJar()
	h  = urllib2.HTTPCookieProcessor(cj)
	opener = urllib2.build_opener(h)
	urllib2.install_opener(opener)
	request = urllib2.Request(url, post)
	request.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	#request.add_header('Host', SITE_HOSTNAME)
	request.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	request.add_header('Accept-Language', 'ru,en;q=0.9')
	if ref != None:
		request.add_header('Referer', ref)
	if os.path.isfile(phpsessid_file):
		fh = open(phpsessid_file, 'r')
		phpsessid = fh.read()
		fh.close()
		request.add_header('Cookie', 'xEsid=' + phpsessid)
	o = urllib2.urlopen(request)
	for index, cookie in enumerate(cj):
		cookraw = re.compile('<Cookie xEsid=(.*?) for.*/>').findall(str(cookie))
		if len(cookraw) > 0:
			fh = open(phpsessid_file, 'w')
			fh.write(cookraw[0])
			fh.close()
	http = o.read()
	o.close()
	return http

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

def CheckHttp(data):
	if (data.find('http://') == -1):
		data = SITEPREF + data
	return data

def GetChannels():
	completed = True
	page = 0

	while completed:
		url = 'http://yatv.ru/ru/tv,channels?page=' + str(page)
		http = Get(url)
		if http == None:
			xbmc.output('[%s] GetChannels() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
			return
		raw1 = re.compile('<a href="(.*?)" class="logo"><img.*src="(.*?)" alt="(.*?)" /></a>').findall(http)
		if len(raw1) == 0:
			xbmc.output('[%s] GetChannels() Error 2: len(raw1) == 0 URL=%s' % (PLUGIN_NAME, url))
			return
		for rURL, rIMG, Name in raw1:
			rIMG = CheckHttp(rIMG)
#			xbmc.output('******************************************')
#			xbmc.output('rURL = %s' % rURL)
#			xbmc.output('rIMG = %s' % rIMG)
#			xbmc.output('Name = %s' % Name)

			listitem = xbmcgui.ListItem(Name, iconImage = rIMG, thumbnailImage = rIMG)
			listitem.setInfo(type = "Video", infoLabels = {
				"Title":	Name
				} )
			purl = sys.argv[0] + '?mode=OpenChannel&url=' + urllib.quote_plus(rURL) \
				+ '&title=' + urllib.quote_plus(Name) + '&img=' + urllib.quote_plus(rIMG)
			xbmcplugin.addDirectoryItem(handle, purl, listitem, False)
		page = page + 1
		xbmc.sleep(100)


def OpenChannel(url, title, image):
	http = Get(url, SITE_URL)
	if http == None:
		xbmc.output('[%s] OpenChannel() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
		return
	cidraw = re.compile('cid=(.[0-9]*)').findall(http)
	if len(cidraw) == 0:
		xbmc.output('[%s] OpenChannel() Error 2: cid = ? URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
		return
	cid = cidraw[0]
	xbmc.output('CID = %s' % str(cid))

	pic = image
	bkgraw = re.compile('background:.*url\(\'(.*?)\'\) repeat center top;').findall(http)
	if len(bkgraw) != 0:
		pic = CheckHttp(bkgraw[0])
	else:
		xbmc.output('[%s] OpenChannel() Warn 2: background not found URL=%s' % (PLUGIN_NAME, url))
	xbmc.output('PIC = %s' % pic)

	swf_val = None
	swfraw = re.compile('<div id="container_swf">(.*?)</div>', re.DOTALL).findall(http)
	if len(swfraw) == 0:
		xbmc.output('[%s] OpenChannel() Warn 3: len(swfraw) == 0 URL=%s' % (PLUGIN_NAME, url))
	else:
		dat_raw = re.compile('data="(.*?)"').findall(swfraw[0])
		if len(dat_raw) == 0:
			xbmc.output('[%s] OpenChannel() Warn 4: len(dat_raw) == 0 URL=%s' % (PLUGIN_NAME, url))
		else:
			swf_val = dat_raw[0]
	xbmc.output('swf_val = %s' % swf_val)

	post = urllib.urlencode({'cid': cid})

	http2 = Get('http://api.yatv.ru/user,sessions,get', swf_val, post)
	#xbmc.output('http2 = %s' % http2)

	http3 = Get('http://api.yatv.ru/channels', swf_val, post)
	if len(http3) == 0:
		xbmc.output('[%s] OpenChannel() Error 5: len(http3) == 0 URL=%s' % (PLUGIN_NAME, url))
		return
	#xbmc.output('http3 = %s' % http3)

	ssraw = re.compile('"streamserver":"(.*?)"').findall(http3)
	if len(ssraw) == 0:
		xbmc.output('[%s] OpenChannel() Error 6: len(ssraw) == 0 URL=%s' % (PLUGIN_NAME, url))
		return
	ssr = ssraw[0].replace('\\','')

	xbmc.output('title   = %s' % title)
	xbmc.output('pic     = %s' % pic)
	xbmc.output('swf_val = %s' % swf_val)
	xbmc.output('ssr     = %s' % ssr)
#	xbmc.output('video_path  = %s' % video_path)
#	xbmc.output('getplaylist = %s' % getplaylist)

	item = xbmcgui.ListItem(title, iconImage = pic, thumbnailImage = pic)
	item.setInfo(type="Video", infoLabels={"Title": title, "Director": PLUGIN_NAME})
	item.setProperty("swfUrl", swf_val)
	item.setProperty("tcUrl",  ssr)
	#item.setProperty("PlayPath", video_path)
	#item.setProperty('video', getplaylist + '&time=0')
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(ssr, item)


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
	GetChannels()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenChannel':
	OpenChannel(url, title, img)
