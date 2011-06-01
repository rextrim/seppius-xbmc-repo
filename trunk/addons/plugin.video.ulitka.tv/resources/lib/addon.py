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
import os, urllib, urllib2, httplib, xml.dom.minidom, cookielib

import html5lib
from html5lib import treebuilders

from jsdecoder import unpack

icon   = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
h = int(sys.argv[1])


addon_id       = 'unknown addon id'
addon_name     = 'unknown addon'
addon_version  = '0.0.0'
addon_provider = 'unknown'

addon_xml = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'addon.xml'))
if os.path.isfile(addon_xml):
	af = open(addon_xml, 'r')
	adom = xml.dom.minidom.parseString(af.read())
	af.close()
	areg = adom.getElementsByTagName('addon')
	addon_id       = areg[0].getAttribute('id')
	addon_name     = areg[0].getAttribute('name')
	addon_version  = areg[0].getAttribute('version')
	addon_provider = areg[0].getAttribute('provider-name')

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

__settings__ = xbmcaddon.Addon(id=addon_id)
__language__ = __settings__.getLocalizedString


def GET(tu):
	#print 'GET [%s]' % tu
	try:
		req = urllib2.Request(tu)
		req.add_header(     'User-Agent','Opera/9.80 (X11; Linux i686; U; ru) Presto/2.8.131 Version/11.10')
		req.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*')
		req.add_header('Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
		req.add_header( 'Accept-Charset','utf-8, utf-16, *;q=0.1')
		req.add_header('Accept-Encoding','identity, *;q=0')
		req.add_header(     'Connection','Keep-Alive')
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		#print a
		return a
	except Exception, e:
		showMessage(tu, e, 5000)
		return None



def showroot():
	http = GET('http://www.ulitka.tv/')
	if http != None:
		li = xbmcgui.ListItem("[Последние]")
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showlatest'})), li, True)

		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http)
		for div0 in DT.getElementsByTagName('div'):
			if div0.getAttribute('id') == 'menu':
				for div1 in div0.getElementsByTagName('a'):
					if div1.getAttribute('href'):
						for div2 in div1.getElementsByTagName('span'):
							if div2.getAttribute('class') == 'bg ':
								href  = div1.getAttribute('href')
								li = xbmcgui.ListItem(div2.firstChild.data.encode('utf8', 'ignore'), iconImage = icon, thumbnailImage = icon)
								xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showserials', 'href':div1.getAttribute('href'), 'genre':div2.firstChild.data.encode('utf8', 'ignore')})), li, True)
		xbmcplugin.endOfDirectory(h)


def showlatest(params):
	http = GET('http://www.ulitka.tv/')
	if http != None:
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http)
		for div0 in DT.getElementsByTagName('div'):
			if div0.getAttribute('class') == 'aidanews':
				for td in div0.getElementsByTagName('td'):
					img = td.getElementsByTagName('img')[0]
					episode = img.getAttribute('alt').encode('utf8', 'ignore')
					imgSrc = img.getAttribute('src').split('/')

					icon = 'http://www.ulitka.tv/images/posters/' + imgSrc[-1]
					show = str(imgSrc[-1]).replace('.jpg', '').replace('-', ' ')
					href = None

					#for span in td.getElementsByTagName('span'):
					#	if show == 'Unknown' and span.getAttribute('style') == ' font-size: 115%;':
					#		f.write(str(span.firstChild.data.encode('utf8')))

					for a in td.getElementsByTagName('a'):
						if a.getAttribute('title'):
							href = a.getAttribute('href')
							show = str(href.split('/')[-2]).replace('-', ' ')

					li = xbmcgui.ListItem("%season %s" % (show, episode), iconImage = icon, thumbnailImage = icon)
					li.setInfo(type = 'video', infoLabels = {'tvshowtitle':show})
					li.setProperty('IsPlayable', 'true')
					xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'watch', 'href': href})), li, False)

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
						if div3.getAttribute('src'): img = 'http://www.ulitka.tv' + div3.getAttribute('src')
			if (iHref != None) and (iName != ''):
				li = xbmcgui.ListItem(iName[3:], iconImage = img, thumbnailImage = img)
				xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showserial', 'href':iHref, 'genre':params['genre'], 'tvshowtitle':iName[3:]})), li, True)
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
						img = 'http://www.ulitka.tv' + div2.getAttribute('src')
				for div2 in div.getElementsByTagName('p'):
					if div2.firstChild.nodeType == div2.firstChild.TEXT_NODE:
						plot = div2.firstChild.data.encode('utf8')
				for div2 in div.getElementsByTagName('a'):
					if div2.getAttribute('href'):
						if div2.firstChild.nodeType == div2.firstChild.TEXT_NODE:
							li = xbmcgui.ListItem(div2.firstChild.data.encode('utf8'), iconImage = img, thumbnailImage = img)
							li.setInfo(type = 'video', infoLabels = {'plot':plot,'tvshowtitle':params['tvshowtitle']})
							xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showepisodes', 'href':div2.getAttribute('href'), 'genre':params['genre'], 'tvshowtitle':params['tvshowtitle']})), li, True)
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
								li = xbmcgui.ListItem(div3.firstChild.data.encode('utf8'), iconImage = icon, thumbnailImage = icon)
								li.setInfo(type = 'video', infoLabels = {'genre':params['genre'],'tvshowtitle':params['tvshowtitle']})
								li.setProperty('IsPlayable', 'true')
								xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'watch', 'href':div3.getAttribute('href')})), li, False)
		xbmcplugin.endOfDirectory(h)

def watch(params):
	http = GET('http://www.ulitka.tv' + params['href'])
	if http != None:
		jsDataRegexp = re.compile("function\(p,a,c,k,e,d\)\{([^\n]+)", re.IGNORECASE + re.DOTALL + re.MULTILINE)
		jsData = jsDataRegexp.findall(http)
		s = jsData[0]
		s = s[s.find('}(')+1:-1]
		initJs = eval('unpack' + s)

		url = 'http://ww.ulitka.tv:8080'

		fileRe = re.compile('so\.addVariable\("file",style\+"([^"]+)')
		url = url + fileRe.findall(initJs)[0]

		url = url + '?start=0&id=1&client=FLASH%20LNX%2010,2,159,1&version=4.3.132&width=640'
		i = xbmcgui.ListItem(path = url)
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

