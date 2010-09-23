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
import urllib,urllib2,cookielib,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon

__settings__ = xbmcaddon.Addon(id='plugin.video.moovie.ru')
__language__ = __settings__.getLocalizedString
pluginhandle = int(sys.argv[1])
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )
xbmcplugin.setPluginFanart(pluginhandle, fanart)
swfobject = 'http://moovie.ru/i/flash/fms_moovie_player.swf'

def Get(url, ref=None, post = None):
	#xbmc.output('Get URL=%s'%url)
	cj = cookielib.CookieJar()
	h  = urllib2.HTTPCookieProcessor(cj)
	opener = urllib2.build_opener(h)
	urllib2.install_opener(opener)
	request = urllib2.Request(url, post)
	request.add_header(     'User-Agent','Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	request.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, */*')
	request.add_header('Accept-Language','ru,en;q=0.9')
	if ref != None:
		request.add_header('Referer', ref)
	phpsessid = __settings__.getSetting('cookie')
	if len(phpsessid) > 0:
		request.add_header('Cookie', 'PHPSESSID=' + phpsessid)
	o = urllib2.urlopen(request)
	for index, cookie in enumerate(cj):
		cookraw = re.compile('<Cookie PHPSESSID=(.*?) for.*/>').findall(str(cookie))
		if len(cookraw) > 0:
			__settings__.setSetting('cookie', cookraw[0])
	http = o.read()
	o.close()
	return http

def clean(name):
	pname = re.sub('(?is)<.*?>', '', name, re.DOTALL|re.IGNORECASE)
	remove = [('\n\n',''),('\t',''),('<br/>','\n'),('<br />','\n'),('mdash;',''),('&ndash;',''),('hellip;','\n'),('&amp;',''),('&quot;','"'),
		  ('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;','"'),('&#151;','-')]
	for trash, crap in remove:
		pname=pname.replace(trash, crap)
	return pname

def openROOT(url):
	http = Get(url)
	r1 = re.compile('<div id="genres-list" >(.*?)</div>', re.DOTALL).findall(http)
	if len(r1) == 0:
		return False
	r2 = re.compile('<a href="(.*?)">(.*?)</a>').findall(r1[0])
	for rURL, rNAME in r2:
		uri = sys.argv[0] + '?mode=openGENRE'
		uri += '&url='+urllib.quote_plus('http://moovie.ru' + rURL)
		uri += '&name='+urllib.quote_plus(rNAME)
		item=xbmcgui.ListItem(rNAME, iconImage=thumb, thumbnailImage=thumb)
		item.setInfo(type='video', infoLabels={'title': rNAME})
		xbmcplugin.addDirectoryItem(pluginhandle,uri,item,True)

	uri = sys.argv[0] + '?mode=openSEARCH'
	item=xbmcgui.ListItem('Поиск', iconImage=fanart, thumbnailImage=fanart)
	xbmcplugin.addDirectoryItem(pluginhandle,uri,item,True)
	xbmcplugin.endOfDirectory(pluginhandle)


def openGENRE(url, name):
	http = Get(url)
	r1 = re.compile('<div class="(.*?)" id="movie_(.*?)">\s*<a href="(.*?)" class="block"><img src="(.*?)"></a>\s*<a href="(.*?)" class="block title">(.*?)</a>').findall(http)
	if len(r1) == 0:
		return False
	for rCLS, movID, rURL, rIMG, rURL2, rNAME in r1:
		title = clean(rNAME)
		img = 'http://moovie.ru'+rIMG
		uri = sys.argv[0] + '?mode=openFILE'
		uri += '&url='+urllib.quote_plus('http://moovie.ru'+rURL)
		uri += '&name='+urllib.quote_plus(title)
		uri += '&id='+urllib.quote_plus(movID)
		uri += '&thumbnail='+urllib.quote_plus(img)
		item=xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
		item.setInfo(type='video', infoLabels={'title': title})
		xbmcplugin.addDirectoryItem(pluginhandle,uri,item)
	try:
		rp = re.compile('<div id="pages" class="pages"(.*?)</div>', re.DOTALL).findall(http)[0]
		rp2 = re.compile('<a href="(.*?)" id="(.*?)" >(.*?)</a>').findall(rp)
		for rURL, rID, rPN in rp2:
			uri = sys.argv[0] + '?mode=openGENRE'
			uri += '&url='+urllib.quote_plus('http://moovie.ru' + rURL)
			item=xbmcgui.ListItem('[ Страница %s ]'%rPN)
			xbmcplugin.addDirectoryItem(pluginhandle,uri,item,True)
	except:
		pass

	xbmcplugin.endOfDirectory(pluginhandle)

def openFILE(url, name, movid, thumbnail):
	http = Get(url)
	try:
		r1 = re.compile('<div class="stars">(.*?)</div>', re.DOTALL).findall(http)
		(rname, stars) = re.compile('title="(.*?)" value="(.*?)" checked="checked"/>').findall(r1[0])[0]
		rate = int(stars)
	except: rate = 0
	try:
		r1 = re.compile('<div class="col-l p20">(.*?)<div class="col-r p20">', re.DOTALL).findall(http)[0]
		plot = clean(r1)
	except: plot = ''
	http2=Get('http://moovie.ru/film/check/?movieId=%s&cache=%s'%(movid,str(time.time())[:10]), swfobject)
	mov_params = get_params(http2)
	try:    movie = urllib.unquote_plus(mov_params['movie'])
	except: return False
	try:    genre = urllib.unquote_plus(mov_params['genre'])
	except: genre = 'No genre'
	try:    title = urllib.unquote_plus(mov_params['title'])
	except: title = 'No title'
	furl  = 'rtmp://future.moovie.ru:1935/moovie/' + movie
	furl += ' swfurl='  + 'http://moovie.ru/i/flash/fms_moovie_player.swf'
	furl += ' pageUrl=' + 'http://moovie.ru/film/frame/?id=1771&auto_play=false'
	furl += ' tcUrl='   + 'rtmp://future.moovie.ru:1935/moovie'
	furl += ' swfVfy=True'
	item=xbmcgui.ListItem(title, iconImage=thumbnail, thumbnailImage=thumbnail)
	item.setInfo(type='video', infoLabels={'title': title, 'genre': genre, 'plot': plot})
	xbmc.Player().play(furl, item)


def get_params(paramstring):
    param=[]
    if len(paramstring)>=2:
        params=paramstring
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

params=get_params(sys.argv[2])
url='http://moovie.ru/'
name=''
plot=''
mode=None
thumbnail=fanart
movid=None

try: mode=params['mode']
except: pass
try: url=urllib.unquote_plus(params['url'])
except: pass
try: name=urllib.unquote_plus(params['name'])
except: pass
try: thumbnail=urllib.unquote_plus(params['thumbnail'])
except: pass
try: plot=urllib.unquote_plus(params['plot'])
except: pass
try: movid=urllib.unquote_plus(params['id'])
except: pass

if mode=='openGENRE':
	openGENRE(url, name)
elif mode=='openFILE':
	openFILE(url, name, movid, thumbnail)
elif mode=='openSEARCH':
	pass_keyboard = xbmc.Keyboard()
	pass_keyboard.setHeading('Что ищем?')
	pass_keyboard.doModal()
	if (pass_keyboard.isConfirmed()):
		SearchStr = pass_keyboard.getText()
		dialog = xbmcgui.Dialog()
		openGENRE('http://moovie.ru/search/?q='+urllib.quote_plus(SearchStr), 'Поиск')
	else:
		exit

else:
	openROOT(url)
