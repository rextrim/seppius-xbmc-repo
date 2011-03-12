#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *   Copyright (с) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# *   Writer (C) 12/03/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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
# *  http://www.gnu.org/licenses/gpl.html
# */

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, cookielib, xml.dom.minidom, base64
import socket, hashlib

__settings__ = xbmcaddon.Addon(id='plugin.video.xbmc.rus')
__language__ = __settings__.getLocalizedString
h = int(sys.argv[1])
icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))


sizes = [10,25,50,100,150,200,250,300]
timeouts = [5,10,15,20,30,45,60,100]
username = __settings__.getSetting('username')
password = __settings__.getSetting('password')
vquality = int(__settings__.getSetting('quality'))
listsize = sizes[int(__settings__.getSetting('size'))]
stimeout = timeouts[int(__settings__.getSetting('timeout'))]
socket.setdefaulttimeout(stimeout)
token0 = __settings__.getSetting('token0')
token1 = __settings__.getSetting('token1')


def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))


def builtin(params):
	try: xbmc.executebuiltin(urllib.unquote_plus(params['target']))
	except: pass


def GET(href, post=None):
	try:
		sendpw = False
		based = base64.b64decode(__language__(30000))
		if href[:7] != 'http://':
			target = based + href
			sendpw = True
		CJ=cookielib.CookieJar()
		CP=urllib2.HTTPCookieProcessor(CJ)
		BO=urllib2.build_opener(CP)
		urllib2.install_opener(BO)
		req = urllib2.Request(target, post)
		req.add_header(     'User-Agent', 'XBMC/10-series (Python addon; XBMC-Russia; HD-lab Team; 2011; http://www.xbmc.org)')
		req.add_header( 'Accept-Charset', 'utf-8')
		cooks  = '; %s=%s'%('token0',urllib.quote_plus(token0))
		if sendpw:
			cooks += '; %s=%s'%('token1',urllib.quote_plus(token1))
			cooks += '; %s=%s'%('user',urllib.quote_plus(username))
			cooks += '; %s=%s'%('hash',urllib.quote_plus(hashlib.sha1(':%s:%s:%s:%s:'%(token0, token1, password, href)).hexdigest()))
			cooks += '; %s=%d'%('quality',vquality)
			cooks += '; %s=%d'%('length',listsize)
		req.add_header('Cookie', cooks[2:])
		o = urllib2.urlopen(req)
		for Cook in CJ:
			if   Cook.name == 'token0': __settings__.setSetting('token0', Cook.value)
			elif Cook.name == 'token1': __settings__.setSetting('token1', Cook.value)
		http = o.read()
		o.close()
		return http
	except:
		showMessage('HTTP ERROR', href, 5000)


def getitems(params):
	try:
		target = urllib.unquote_plus(params['target'])
	except:
		target = ''
	http = GET(target)
	if http == None:
		return False
	document = xml.dom.minidom.parseString(http)
	for item in document.getElementsByTagName('item'):
		info = {}
		try: info['count'] = int(item.getElementsByTagName('count')[0].firstChild.data)
		except: pass
		try: info['size'] = long(item.getElementsByTagName('size')[0].firstChild.data)
		except: pass
		try: info['date'] = item.getElementsByTagName('date')[0].firstChild.data
		except: pass
		try: info['genre'] = item.getElementsByTagName('genre')[0].firstChild.data
		except: pass
		try: info['year'] = int(item.getElementsByTagName('year')[0].firstChild.data)
		except: pass
		try: info['episode'] = int(item.getElementsByTagName('episode')[0].firstChild.data)
		except: pass
		try: info['season'] = int(item.getElementsByTagName('season')[0].firstChild.data)
		except: pass
		try: info['top250'] = int(item.getElementsByTagName('top250')[0].firstChild.data)
		except: pass
		try: info['tracknumber'] = int(item.getElementsByTagName('tracknumber')[0].firstChild.data)
		except: pass
		try: info['rating'] = float(item.getElementsByTagName('rating')[0].firstChild.data)
		except: pass
		try: playcount = int(item.getElementsByTagName('playcount')[0].firstChild.data)
		except: pass
		try: info['overlay'] = int(item.getElementsByTagName('overlay')[0].firstChild.data)
		except: pass
		try: info['cast'] = list(item.getElementsByTagName('cast')[0].firstChild.data)
		except: pass
		try: info['castandrole'] = list(item.getElementsByTagName('castandrole')[0].firstChild.data)
		except: pass
		try: info['director'] = item.getElementsByTagName('director')[0].firstChild.data
		except: pass
		try: info['mpaa'] = item.getElementsByTagName('mpaa')[0].firstChild.data
		except: pass
		try: info['plot'] = item.getElementsByTagName('plot')[0].firstChild.data
		except: pass
		try: info['plotoutline'] = item.getElementsByTagName('plotoutline')[0].firstChild.data
		except: pass
		try:    info['title'] = item.getElementsByTagName('title')[0].firstChild.data
		except: info['title'] = ''
		try: info['duration'] = item.getElementsByTagName('duration')[0].firstChild.data
		except: pass
		try: info['studio'] = item.getElementsByTagName('studio')[0].firstChild.data
		except: pass
		try: info['tagline'] = item.getElementsByTagName('tagline')[0].firstChild.data
		except: pass
		try: info['writer'] = item.getElementsByTagName('writer')[0].firstChild.data
		except: pass
		try: info['tvshowtitle'] = item.getElementsByTagName('tvshowtitle')[0].firstChild.data
		except: pass
		try: info['premiered'] = item.getElementsByTagName('premiered')[0].firstChild.data
		except: pass
		try: info['status'] = item.getElementsByTagName('status')[0].firstChild.data
		except: pass
		try: info['code'] = item.getElementsByTagName('code')[0].firstChild.data
		except: pass
		try: info['aired'] = item.getElementsByTagName('aired')[0].firstChild.data
		except: pass
		try: info['credits'] = item.getElementsByTagName('credits')[0].firstChild.data
		except: pass
		try: info['lastplayed'] = item.getElementsByTagName('lastplayed')[0].firstChild.data
		except: pass
		try: info['album'] = item.getElementsByTagName('album')[0].firstChild.data
		except: pass
		try: info['votes'] = item.getElementsByTagName('votes')[0].firstChild.data
		except: pass
		try: info['trailer'] = item.getElementsByTagName('trailer')[0].firstChild.data
		except: pass
		try:    fanartimage = item.getElementsByTagName('fanartimage')[0].firstChild.data
		except: fanartimage = ''
		try:    iconImage = item.getElementsByTagName('iconImage')[0].firstChild.data
		except: iconImage = ''
		try:    thumbnailImage = item.getElementsByTagName('thumbnailImage')[0].firstChild.data
		except: thumbnailImage = ''
		try:    IsPlayable = item.getElementsByTagName('IsPlayable')[0].firstChild.data
		except: IsPlayable = 'false'
		try:    IsFolder = (item.getElementsByTagName('IsFolder')[0].firstChild.data.lower() == 'true')
		except: IsFolder = False
		try:    itype = item.getElementsByTagName('type')[0].firstChild.data
		except: itype = 'video'
		try:    uri = '%s?%s'%(sys.argv[0], item.getElementsByTagName('next_uri')[0].firstChild.data)
		except: uri = ''
		li = xbmcgui.ListItem(info['title'], iconImage=iconImage, thumbnailImage=thumbnailImage)
		li.setInfo(type=itype, infoLabels=info)
		li.setProperty('fanart_image', fanartimage)
		li.setProperty('IsPlayable',   IsPlayable)
		xbmcplugin.addDirectoryItem(h, uri, li, IsFolder)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RATING)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(h)


def directplay(params):
	try:
		i = xbmcgui.ListItem(path=base64.b64decode(urllib.unquote_plus(params['target'])))
		xbmcplugin.setResolvedUrl(h, True, i)
	except:
		showMessage('DATA ERROR', 'I can not play this item')
		return False


def play(params):
	try:
		http = GET(urllib.unquote_plus(params['target']))
		i = xbmcgui.ListItem(path = base64.b64decode(http))
		xbmcplugin.setResolvedUrl(h, True, i)
	except:
		showMessage('DATA ERROR', 'I can not play this item')
		return False


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


params = get_params(sys.argv[2])
mode   = None
func   = None
try:    mode = urllib.unquote_plus(params['mode'])
except: getitems(params)

if mode != None:
	try:    func = globals()[mode]
	except: pass
	if func: func(params)
