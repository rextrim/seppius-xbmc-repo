#!/usr/bin/python
#/*
# *      Copyright (C) 2010 FreeForAll
# *      This Program is free software
# */

import urllib2, re, string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib #, xbmcaddon

#__settings__ = xbmcaddon.Addon(id='plugin.video.zoomby.ru')
#__language__ = __settings__.getLocalizedString

handle = int(sys.argv[1])

PLUGIN_NAME   = 'ZOOMBY.RU'
SITE_HOSTNAME = 'www.zoomby.ru'
SITEPREF      = 'http://%s' % SITE_HOSTNAME
SITE_URL      = SITEPREF + '/'

phpsessid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_zoomby.sess')
thumb = os.path.join( os.getcwd(), "icon.png" )

def clean(name):
	remove=[('&nbsp;', ''), ('&mdash;', '-'), ('&hellip;', '.'), ('&ndash;', '-'), ('&laquo;', '"'), ('&ldquo;', '"'), ('&ldquo;', '"'), ('&raquo;', '"'), ('&quot;', '"')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def Get(url, ref=None):
	url = SITEPREF + url
	cj = cookielib.CookieJar()
	h  = urllib2.HTTPCookieProcessor(cj)
	opener = urllib2.build_opener(h)
	urllib2.install_opener(opener)
	post = None
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
		request.add_header('Cookie', 'CGISESSID=' + phpsessid)
	o = urllib2.urlopen(request)
	for index, cookie in enumerate(cj):
		cookraw = re.compile('<Cookie CGISESSID=(.*?) for.*/>').findall(str(cookie))
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

def GetAlphabetList(http):
	raw1 = re.compile('<ul class="afltr">(.*?)</ul>', re.DOTALL).findall(http)
	if len(raw1) != 0:
		raw2 = re.compile('<a href="(.*?)">(.*?)</a>').findall(raw1[0])
		if len(raw2) != 0:
		  	for grp_url, grp_name in raw2:
				Title = '%s : %s' % ('Alphabet', grp_name)
				listitem = xbmcgui.ListItem(Title)
				listitem.setInfo(type = "Video", infoLabels = {"Title":	Title} )
				url = sys.argv[0] + '?mode=OpenAlphabet&url=' + urllib.quote_plus(grp_url) + '&title=' + urllib.quote_plus(grp_name)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)

def ShowRoot(url):
	http = Get(url)
	if http == None:
		return
	raw1 = re.compile('<ul class="mainmenu">(.*?)</ul>', re.DOTALL).findall(http)
	if len(raw1) != 0:
		raw2 = re.compile('<a href="(.*?)">(.*?)</a>\s*<div class="msubmenu">(.*?)</div>', re.DOTALL).findall(raw1[0])
		if len(raw2) != 0:
			x = 1
		  	for grp_url, grp_name, grp_block in raw2:
				Title = '%s. %s (All)' % (str(x), grp_name)
				listitem = xbmcgui.ListItem(Title) # , iconImage = Thumb, thumbnailImage = Thumb
				listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
				url = sys.argv[0] + '?mode=OpenList&url=' + urllib.quote_plus(grp_url) + '&title=' + urllib.quote_plus(grp_name)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)
				raw3 = re.compile('<a href="(.*?)">(.*?)</a>').findall(grp_block)
				if len(raw3) != 0:
					y = 1
					for row_url, row_name in raw3:
						Title = '%s. %s. %s : %s' % (str(x), str(y), grp_name, row_name)
						listitem = xbmcgui.ListItem(Title) # , iconImage = Thumb, thumbnailImage = Thumb
						listitem.setInfo(type = "Video", infoLabels = {"Title":	Title} )
						url = sys.argv[0] + '?mode=OpenList&url=' + urllib.quote_plus(row_url) + '&title=' + urllib.quote_plus(row_name)
						xbmcplugin.addDirectoryItem(handle, url, listitem, True)
						y = y + 1
				x = x + 1

	raw1 = re.compile('<div id="tags" style=".*" align="center">(.*?)</div>', re.DOTALL).findall(http)
	if len(raw1) != 0:
		raw2 = re.compile('<a href="(.*?)".*><span.*>(.*?)</span></a>').findall(raw1[0])
		if len(raw2) != 0:
		  	for grp_url, grp_name in raw2:
				grp_name = clean(grp_name)
				Title = '%s :%s' % ('Tag', grp_name)
				listitem = xbmcgui.ListItem(Title) # , iconImage = Thumb, thumbnailImage = Thumb
				listitem.setInfo(type = "Video", infoLabels = {"Title":	Title} )
				url = sys.argv[0] + '?mode=OpenList&url=' + urllib.quote_plus(row_url) + '&title=' + urllib.quote_plus(grp_name)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)
	GetAlphabetList(http)


def OpenAlphabetList(url, title):
	http = OpenList(url, title)
	if http != None:
		GetAlphabetList(http)

def OpenList(work_url, title):
	print '||||||||def OpenList(work_url, title) URL=' + work_url
	http = Get(work_url)
	if http == None:
		return None
	raw1 = re.compile('<div class="preview01cont">(.*?)<div', re.DOTALL).findall(http)
	if len(raw1) != 0:
		x = 1
		for raw_block in raw1:
			#xbmc.output(str(x))
			#xbmc.output(raw_block)
			raw2 = re.compile('<a href="(.*?)" class="nav2">(.*?)</a>').findall(raw_block)
			if len(raw2) != 0:
				pg_url, pg_name = raw2[0]
				raw3 = re.compile('<img src="(.*?)" alt=".*" width=".*" height=".*" />').findall(raw_block)
				Thumb = thumb
				if len(raw3) != 0:
					Thumb = raw3[0]
				tname = clean(pg_name)
				Title = tname
				listitem = xbmcgui.ListItem(Title, iconImage = Thumb, thumbnailImage = Thumb)
				listitem.setInfo(type = "Video", infoLabels = {"Title":	Title} )
				url = sys.argv[0] + '?mode=PlayPage&url=' + urllib.quote_plus(pg_url) + '&title=' + urllib.quote_plus(tname) + '&img=' + urllib.quote_plus(Thumb)
				xbmcplugin.addDirectoryItem(handle, url, listitem, False)
				x = x + 1

	ht2 = http.replace('</td><td valign="top">', '</td>\n<td valign="top">')

	raw1 = re.compile('<td valign="top"><div onClick="window.location.href=\'(.*?)\'" style=".*">(.*?)</div></td>').findall(ht2)
	if len(raw1) != 0:
		targ_url = re.compile('(.*?)\\?page=.*').findall(work_url)
		ptarget = work_url
		if len(targ_url) != 0:
			ptarget = targ_url[0]
		for raw_url, raw_page in raw1:
			Title = 'To page ' + raw_page
			target = ptarget + raw_url
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title":	Title} )
			url = sys.argv[0] + '?mode=OpenList&url=' + urllib.quote_plus(target) + '&title=' + urllib.quote_plus(title)
			xbmcplugin.addDirectoryItem(handle, url, listitem, True)
	return http


def PlayPage(url, Title, Image):
	xbmc.output('[%s] PlayPage(%s, %s, %s)' % (PLUGIN_NAME, url, Title, Image))

	dialog = xbmcgui.Dialog()

	http = Get(url)
	if http == None:
		xbmc.output('[%s] PlayPage() Error: http == None URL=%s' % (PLUGIN_NAME, url))
		return

	raw_embed = re.compile('<embed(.*?)</embed>', re.DOTALL).findall(http)
	if len(raw_embed) == 0:
		xbmc.output('[%s] PlayPage() Error: len(raw_embed) == 0 URL=%s' % (PLUGIN_NAME, url))
		return
	embed = raw_embed[0]

	raw_swf = re.compile('src="(.*?)"').findall(embed)
	if len(raw_swf) == 0:
		xbmc.output('[%s] PlayPage() Error: len(raw_swf) == 0 URL=%s' % (PLUGIN_NAME, url))
		return
	swf = raw_swf[0]

	raw_fV = re.compile('flashVars="video=(.*?)&.*"').findall(raw_embed[0])
	if len(raw_fV) == 0:
		xbmc.output('[%s] PlayPage() Error: len(raw_fV) == 0 URL=%s' % (PLUGIN_NAME, url))
		return
	getplaylist = raw_fV[0]

	b = Get(getplaylist, swf)
	if b == None:
		xbmc.output('[%s] PlayPage() Error: Get(getplaylist, swf) == None URL=%s SWF=%s' % (PLUGIN_NAME, getplaylist, swf))
		return

	raw_srvbase = re.compile('<meta base="(.*?)"').findall(b)
	#srvbase = raw_srvbase[0].replace('rtmpe', 'rtmp')
	srvbase = raw_srvbase[0]

	raw_filesdata = re.compile('<video src="(.*?)" system-bitrate="(.*?)"/>').findall(b)
	if len(raw_filesdata) == 0:
		xbmc.output('[%s] PlayPage() Error: len(raw_filesdata) == 0 URL=%s' % (PLUGIN_NAME, url))
		return

	list = []
	spcn = len(raw_filesdata)
	if spcn == 1:
		selected = 0
	else:
		for x in range(spcn):
			list.append(raw_filesdata[x][1])
		selected = dialog.select('Quality?', list)
	if selected < 0:
		return
	video_path  = raw_filesdata[selected][0]
	video_quality = raw_filesdata[selected][1]

	xbmc.output('Title       = %s' % Title)
	xbmc.output('Image       = %s' % Image)
	xbmc.output('swf         = %s' % swf)
	xbmc.output('srvbase     = %s' % srvbase)
	xbmc.output('video_path  = %s' % video_path)
	xbmc.output('getplaylist = %s' % getplaylist)

	item = xbmcgui.ListItem(Title, iconImage = Image, thumbnailImage = Image)
	item.setInfo(type="Video", infoLabels={"Title": Title, "Director": 'ZOOMBY'})
	item.setProperty("swfUrl", swf)
	item.setProperty("tcUrl",  srvbase)
	item.setProperty("PlayPath", video_path)
	item.setProperty('video', getplaylist + '&time=0')
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(srvbase, item)


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
	ShowRoot('/')
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenList':
	OpenList(url, title)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenAlphabet':
	OpenAlphabetList(url, title)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'PlayPage':
	PlayPage(url, title, img)

