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
import xbmcplugin,xbmcgui,xbmcaddon,xbmc

try:
	import adanalytics, thread
	a_lock = thread.allocate_lock()
	a_lock.acquire()
	xbmc.output('adIO main: lock allocated, thread started')
	adanalytics.main(sys.argv[0], sys.argv[1], sys.argv[2], a_lock)
except Exception, e:
	print(e)
	xbmc.output('adIO main: thread exception')

__settings__ = xbmcaddon.Addon(id='plugin.video.moovie.ru')
h = int(sys.argv[1])
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
thumb  = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), "icon.png" ))
SWF = 'http://moovie.ru/i/flash/fms_moovie_player.swf'
RTS = 'rtmp://future.moovie.ru:1935/moovie/'


def Get(url, ref=None, post = None):
	cj = cookielib.CookieJar()
	h  = urllib2.HTTPCookieProcessor(cj)
	opener = urllib2.build_opener(h)
	urllib2.install_opener(opener)
	request = urllib2.Request(url, post)
	request.add_header(     'User-Agent','Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	request.add_header('Accept-Language','ru,en;q=0.9')
	if post != None:
		request.add_header('X-Requested-With','XMLHttpRequest')
		request.add_header(    'Content-Type','application/x-www-form-urlencoded')
		request.add_header(          'Accept', 'application/json, text/javascript, */*')
	else:
		request.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, */*')
	if ref != None:
		request.add_header('Referer', ref)
	POST_Cookie = ''
	phpsessid = __settings__.getSetting('cookie')
	if phpsessid != '':
		POST_Cookie = 'PHPSESSID=%s; '%phpsessid
	tokenssid = __settings__.getSetting('token')
	if tokenssid != '':
		POST_Cookie = 'token=%s; '%tokenssid
	if POST_Cookie != '':
		request.add_header('Cookie', POST_Cookie)
	o = urllib2.urlopen(request)
	for index, cookie in enumerate(cj):
		cookraw = re.compile('PHPSESSID=(.*?) ').findall(str(cookie))
		if len(cookraw) > 0: __settings__.setSetting('cookie', cookraw[0])
		tokraw = re.compile('token=(.*?) ').findall(str(cookie))
		if len(tokraw) > 0: __settings__.setSetting('token', tokraw[0])
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

def AUTH():
	UserMail = __settings__.getSetting('usermail')
	if UserMail == '':
		mk = xbmc.Keyboard()
		mk.setHeading('Ваш e-mail')
		mk.doModal()
		if (mk.isConfirmed()):
			UserMail = mk.getText()
			__settings__.setSetting('usermail', UserMail)
		else:
			return False
	UserPass = __settings__.getSetting('password')
	if UserPass == '':
		pk = xbmc.Keyboard()
		pk.setHeading('Ваш пароль')
		pk.setHiddenInput(True)
		pk.doModal()
		if (pk.isConfirmed()):
			UserPass = pk.getText()
			__settings__.setSetting('password', UserPass)
		else:
			return False
	http = Get('http://moovie.ru/user/login/', 'http://moovie.ru/', 'email=%s&remember=1&password=%s'%(UserMail, UserPass))
	dialog = xbmcgui.Dialog()
	if (http.find('"ok":') == -1):
		dialog.ok('moovie.ru', 'Ошибка. Пробуй еще!')
		#__settings__.setSetting('cookie', '')
		__settings__.setSetting('token', '')
		dialog.ok('Небольшой HELP', 'Если вы ошиблись с e-mail или паролем, то',
			'их можно изменить в настройках дополнения',
			'После чего войдите в moovie.ru снова.')
	else: dialog.ok('moovie.ru 18+', 'Спецраздел открыт!')
	return True

def openROOT(url):
	try:
		r2 = re.compile('<a href="(.*?)">(.*?)</a>').findall(re.compile('<div id="genres-list" >(.*?)</div>', re.DOTALL).findall(Get(url, 'http://moovie.ru/'))[0])
		for url, genre in r2:
			u = sys.argv[0] + '?mode=openGENRE'
			u += '&url=%s'%urllib.quote_plus('http://moovie.ru%s'%url)
			u += '&genre=%s'%urllib.quote_plus(genre)
			i=xbmcgui.ListItem(genre, iconImage=thumb, thumbnailImage=thumb)
			i.setInfo(type='video', infoLabels={'title': genre})
			xbmcplugin.addDirectoryItem(h,u,i,True)
	except:
		pass
	try:
		u = sys.argv[0] + '?mode=openSEARCH'
		i=xbmcgui.ListItem('Поиск', iconImage=fanart, thumbnailImage=fanart)
		xbmcplugin.addDirectoryItem(h,u,i,True)
	except:
		pass

	u = sys.argv[0] + '?mode=AUTH'
	i=xbmcgui.ListItem('Авторизация', iconImage=fanart, thumbnailImage=fanart)
	xbmcplugin.addDirectoryItem(h,u,i,True)

	xbmcplugin.endOfDirectory(h)

def openGENRE(url, name):
	http = Get(url, 'http://moovie.ru/')
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
		item.setInfo(type='video', infoLabels={'title': title, 'genre': name})
		item.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(h,uri,item)
	try:
		rp = re.compile('<div id="pages" class="pages"(.*?)</div>', re.DOTALL).findall(http)[0]
		rp2 = re.compile('<a href="(.*?)" id="(.*?)" >(.*?)</a>').findall(rp)
		for rURL, rID, rPN in rp2:
			uri = sys.argv[0] + '?mode=openGENRE'
			uri += '&url='+urllib.quote_plus('http://moovie.ru' + rURL)
			item=xbmcgui.ListItem('[ Страница %s ]'%rPN)
			xbmcplugin.addDirectoryItem(h,uri,item,True)
	except:
		pass
	xbmcplugin.endOfDirectory(h)

def openFILE(movid):
	web = Get('http://moovie.ru/film/check/?movieId=%s&cache=%s'%(movid,str(time.time())[:10]), SWF)
	mP = get_params(web)
	try:    PP = urllib.unquote_plus(mP['movie'])
	except: return False
	PU = 'http://moovie.ru/film/frame/?id=%s&auto_play=false'%movid
	u = '%s PlayPath=%s swfurl=%s tcUrl=%s pageUrl=%s swfVfy=True'%(RTS, PP, SWF, RTS[:-1], PU)
	i = xbmcgui.ListItem(path = u)
	xbmcplugin.setResolvedUrl(h, True, i)

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
genre=''
mode=None
ID=None

try: mode=params['mode']
except: pass
try: url=urllib.unquote_plus(params['url'])
except: pass
try: genre=urllib.unquote_plus(params['genre'])
except: pass
try: ID=urllib.unquote_plus(params['id'])
except: pass


if   mode=='openGENRE': openGENRE(url, genre)
elif mode=='AUTH': AUTH()
elif mode=='openFILE': openFILE(ID)
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

try:
	xbmc.output('adIO main: waiting for release lock')
	while a_lock.locked(): xbmc.sleep(100)
	xbmc.output('adIO main: finished')
except:
	xbmc.output('adIO main: release Exception!')
	pass
