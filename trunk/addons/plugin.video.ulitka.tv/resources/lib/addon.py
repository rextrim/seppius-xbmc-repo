#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
#   Writer (c) 20/05/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
#
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon, re
import os, urllib, urllib2, cookielib

import html5lib
from html5lib import treebuilders

h = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id = 'plugin.video.ulitka.tv')

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')
addon_profile = __addon__.getAddonInfo('profile')

icon   = xbmc.translatePath(addon_icon)
fanart = xbmc.translatePath(addon_fanart)
profile = xbmc.translatePath(addon_profile)


def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))


def GET(tu, post=None):
	#print '[%s]: TARGET TU=[%s]' % (addon_id, tu)
	#print '[%s]: POST DATA=[%s]' % (addon_id, post)
	try:
		CJ = cookielib.CookieJar()
		urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor(CJ)))
		req = urllib2.Request(tu)
		req.add_header('User-Agent', '%s/%s %s/%s/%s' % (addon_type, addon_id, addon_author, addon_version, urllib.quote_plus(addon_name)))

		if post: req.add_header('Content-Type', 'application/x-www-form-urlencoded')

		cookie_path = os.path.join(profile, 'cookie')
		if not os.path.exists(cookie_path):
			os.makedirs(cookie_path)
			print '[%s]: os.makedirs(cookie_path=%s)' % (addon_id, cookie_path)

		cookie_send = {}
		for cookie_fname in os.listdir(cookie_path):
			cookie_file = os.path.join(cookie_path, cookie_fname)
			if os.path.isfile(cookie_file):
				cf = open(cookie_file, 'r')
				cookie_send[os.path.basename(cookie_file)] = cf.read()
				cf.close()
			else: print '[%s]: NOT os.path.isfile(cookie_file=%s)' % (addon_id, cookie_file)

		cookie_string = urllib.urlencode(cookie_send).replace('&','; ')
		req.add_header('Cookie', cookie_string)
		f = urllib2.urlopen(req, post)

		for Cook in CJ:
			cookie_file = os.path.join(cookie_path, Cook.name)
			cf = open(cookie_file, 'w')
			cf.write(Cook.value)
			cf.close()

		a = f.read()
		f.close()
		return a
	except Exception, e:
		print '[%s]: GET EXCEPTION: %s' % (addon_id, e)
		showMessage(tu, e, 5000)
		return None

def auth(params):
	username = __addon__.getSetting('username')
	password = __addon__.getSetting('password')

	if len(username) and len(password):
		http = GET('http://www.ulitka.tv/')
		if http != None:
			post_data = {'username':username, 'passwd':password}
			DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http)
			for div0 in DT.getElementsByTagName('span'):
				if div0.getAttribute('class') == 'login':
					for inputs in div0.getElementsByTagName('input'):
						if inputs.getAttribute('type') == 'hidden':
							post_data[inputs.getAttribute('name')] = inputs.getAttribute('value')
			GET('http://www.ulitka.tv/index.php', urllib.urlencode(post_data))
			#showMessage('Логин и пароль отправлен', 'Нет гарантии что она произошла', 5000)
	else:
		__addon__.openSettings()


def showlatest(params):
	import xml.dom.minidom, datetime
	http = GET('http://www.ulitka.tv/rss.xml')
	if http != None:
		document = xml.dom.minidom.parseString(http)
		items  = document.getElementsByTagName('item')
		for item in items:
			try: title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8','replace')
			except: title = None
			if (title != None):
				info = {'title':title}
				try:
					pda = item.getElementsByTagName('pubDate')[0].firstChild.data.encode('utf-8','replace')
					pdb = datetime.datetime.strptime(pda[:25],'%a, %d %b %Y %H:%M:%S')
					info['date'] = str(pdb.strftime('%d.%m.%Y'))
					info['year'] = int(pdb.strftime('%Y'))
				except: pass
				try:
					info['genre'] = item.getElementsByTagName('category')[0].firstChild.data
					info['tagline'] = info['genre']
				except: pass
				try:
					plot = item.getElementsByTagName('description')[0].firstChild.toxml().encode('utf-8','replace')
					info['plot'] = re.compile('/>(.*?)]]>', re.IGNORECASE + re.DOTALL + re.MULTILINE).findall(plot)[0]
				except: pass
				try:
					iimg = item.getElementsByTagName('media:thumbnail')[0].getAttribute('url').encode('utf-8','replace')
					imgSrc = iimg.split('/')
					poster = 'http://static.ulitka.tv/images/posters/%s'   % imgSrc[-1]
					fanart = 'http://static.ulitka.tv/images/S_posters/%s' % imgSrc[-1]
				except:
					poster = icon
					fanart = icom
				link = item.getElementsByTagName('link')[0].firstChild.data.replace('http://www.ulitka.tv','')
				li = xbmcgui.ListItem(info['title'], iconImage = poster, thumbnailImage = poster)
				li.setInfo(type = 'video', infoLabels = info)
				li.setProperty('IsPlayable', 'true')
				li.setProperty('fanart_image', fanart)
				xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'watch', 'href': link})), li, False)
		xbmcplugin.endOfDirectory(h)


def showroot():
	http = GET('http://www.ulitka.tv/')
	if http != None:
		#xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'auth'})), xbmcgui.ListItem('[ Авторизация ]'), False)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showlatest'})), xbmcgui.ListItem('[ Последние ]'), True)
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http)
		for div0 in DT.getElementsByTagName('div'):
			if div0.getAttribute('id') == 'menu':
				for div1 in div0.getElementsByTagName('a'):
					if div1.getAttribute('href'):
						for div2 in div1.getElementsByTagName('span'):
							if div2.getAttribute('class') == 'bg ':
								href  = div1.getAttribute('href')
								info = {'title':div2.firstChild.data.encode('utf8', 'ignore')}
								info['genre'] = info['title']
								li = xbmcgui.ListItem(info['title'], iconImage = icon, thumbnailImage = icon)
								li.setInfo(type = 'video', infoLabels = info)
								li.setProperty('fanart_image', icon)
								xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showserials', 'href':div1.getAttribute('href'), 'genre':info['genre']})), li, True)
		xbmcplugin.endOfDirectory(h)


def showserials(params):
	http = GET('http://www.ulitka.tv' + params['href'])
	if http != None:
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http)
		for div in DT.getElementsByTagName('td'):
			iName = ''
			iHref = None
			img = icon
			for div2 in div.getElementsByTagName('a'):
				if div2.firstChild.nodeType == div2.firstChild.TEXT_NODE:
					iName += ' / %s' % div2.firstChild.data.encode('utf8')
					iHref = div2.getAttribute('href')
				else:
					for div3 in div2.getElementsByTagName('img'):
						if div3.getAttribute('src'): fanart = div3.getAttribute('src') # 'http://www.ulitka.tv' +
			if (iHref != None) and (iName != ''):
				poster = fanart.replace('/S_posters/', '/posters/')
				info = {'title':iName[3:], 'genre':params['genre']}
				li = xbmcgui.ListItem(info['title'], iconImage = poster, thumbnailImage = poster)
				li.setInfo(type = 'video', infoLabels = info)
				li.setProperty('fanart_image', fanart)
				xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showserial', 'href':iHref, 'genre':info['genre'], 'tvshowtitle':info['title']})), li, True)
		xbmcplugin.endOfDirectory(h)


def showserial(params):
	http = GET('http://www.ulitka.tv' + params['href'])
	if http != None:
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http)
		for div in DT.getElementsByTagName('div'):
			if div.getAttribute('class') == 'description':
				iName = ''
				img = icon
				plot = ''
				for div2 in div.getElementsByTagName('img'):
					if div2.getAttribute('src'):
						img = div2.getAttribute('src') # 'http://www.ulitka.tv'
				for div2 in div.getElementsByTagName('p'):
					if div2.firstChild.nodeType == div2.firstChild.TEXT_NODE:
						plot = div2.firstChild.data.encode('utf8')
				for div2 in div.getElementsByTagName('a'):
					if div2.getAttribute('href'):
						if div2.firstChild.nodeType == div2.firstChild.TEXT_NODE:
							info = {'title':div2.firstChild.data.encode('utf8'), 'genre':params['genre'], 'plot':plot}
							try:
								season = int(info['title'].split(' ')[0])
							except: season = 0
							poster = img.replace('/S_posters/', '/posters/')
							fanart = img.replace('/posters/', '/S_posters/')
							li = xbmcgui.ListItem(info['title'], iconImage = poster, thumbnailImage = poster)
							li.setInfo(type = 'video', infoLabels = info)
							li.setProperty('fanart_image', fanart)
							xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showepisodes', 'href':div2.getAttribute('href'), 'genre':info['genre'], 'tvshowtitle':params['tvshowtitle'], 'icon':poster, 'season':season, 'plot': plot})), li, True)
		xbmcplugin.endOfDirectory(h)


def showepisodes(params):
	http = GET('http://www.ulitka.tv' + params['href'])
	if http != None:
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http)
		for div in DT.getElementsByTagName('div'):
			if div.getAttribute('class') == 'categorylist':
				for div2 in div.getElementsByTagName('td'):
					iName = ''
					iHref = None
					img = icon
					for div3 in div2.getElementsByTagName('a'):
						if div3.getAttribute('href'):
							if div3.firstChild.nodeType == div3.firstChild.TEXT_NODE:
								try:
									ssst = div3.firstChild.data.encode('utf8').split(' ')
									if ssst[0] == '0': ssst=ssst[1:]
									if ssst[0] == '0': ssst=ssst[1:]
									episode = int(ssst[0])
								except:
									episode = 0
								title = div3.firstChild.data.encode('utf8')
								try:
									title = re.compile('\((.*?)\)').findall(title)[0]
									if episode > 0: title = '%d. %s' % (episode, title)
								except:
									pass
								info = {'title':title, 'genre':params['genre'], 'season':int(params['season']), 'episode':episode, 'tvshowtitle':params['tvshowtitle'], 'plot':params['plot']}
								img = params['icon'].replace('/posters/', '/S_posters/')
								li = xbmcgui.ListItem(info['title'], iconImage=img, thumbnailImage=img)
								li.setInfo(type = 'video', infoLabels = info)
								li.setProperty('IsPlayable', 'true')
								li.setProperty('fanart_image', img)
								xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'watch', 'href':div3.getAttribute('href')})), li, False)
		xbmcplugin.endOfDirectory(h)


def watch(params):
	auth(None)
	import string
	digits39 = string.digits + string.lowercase
	digits62 = string.digits + string.lowercase + string.uppercase

	def int2base(x, base):
		digs = digits39
		if base == 62:
			digs = digits62
		if x < 0: sign = -1
		elif x==0: return '0'
		else: sign = 1
		x *= sign
		digits = []
		while x:
			digits.append(digs[x % base])
			x /= base
		if sign < 0:
			digits.append('-')
		digits.reverse()
		return ''.join(digits)

	def unpack(p, a, c, k, e=None, d=None):
		for i in xrange(c-1,-1,-1):
			if k[i]: p = re.sub('\\b'+int2base(i,a)+'\\b', k[i], p)
		return p

	http = GET('http://www.ulitka.tv' + params['href'])
	if http != None:
		jsDataRegexp = re.compile("function\(p,a,c,k,e,d\)\{([^\n]+)", re.IGNORECASE + re.DOTALL + re.MULTILINE)
		jsData = jsDataRegexp.findall(http)
		s = jsData[0]
		s = s[s.find('}(')+1:-1]
		initJs = eval('unpack' + s)
		fileRe = re.compile('so\.addVariable\("file",style\+"([^"]+)').findall(initJs)[0]
		swfRe_swf, swfRe_id = re.compile('SWFObject\("(.+?)","(.+?)".*?\);').findall(initJs)[0]
		url = 'http://ww.ulitka.tv:8080'+fileRe+'?start=0&id='+swfRe_id+'&client=FLASH%20LNX%2010,3,181,26&version=4.3.132&width=640'
		i = xbmcgui.ListItem(path = url)
		i.setProperty('mimetype', 'video/mp4')
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
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param




def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
	except:
		showroot()
		func = None

	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			print '[%s]: Function "%s" not found' % (addon_id, func)
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)

