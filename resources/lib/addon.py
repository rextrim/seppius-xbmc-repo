#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
#   Writer (c) 15/05/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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
import os, urllib, urllib2, httplib, xml.dom.minidom

import html5lib
from html5lib import treebuilders

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


headers = {'User-Agent': 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.8.131 Version/11.10',
	'Accept': 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1',
	'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Cache-Control': 'no-cache',
	'Connection': 'Keep-Alive'}


def GET(target, headers, post = None):
	try:
		connection = httplib.HTTPConnection('newstube.ru')
		if post == None: method = 'GET'
		else:
			method = 'POST'
			headers['X-Requested-With'] = 'XMLHttpRequest'
			headers['Content-Transfer-Encoding'] = 'binary'
			headers['Content-Type'] = 'application/x-www-form-urlencoded'
			headers['Content-Length'] = len(post)
			headers['Accept'] = '*/*'
		connection.request(method, target, post, headers = headers)
		response = connection.getresponse()
		http = response.read()
		return http
	except:
		return None


def showroot():
	li = xbmcgui.ListItem('Последние новости', iconImage = icon, thumbnailImage = icon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'getitems', 'href':'/medialast'})), li, True)
	li = xbmcgui.ListItem('Темы дня', iconImage = icon, thumbnailImage = icon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'getitems', 'href':'/events'})), li, True)
	li = xbmcgui.ListItem('Каналы', iconImage = icon, thumbnailImage = icon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'getchannels', 'href':'/channels'})), li, True)
	xbmcplugin.endOfDirectory(h)


def getchannels(params):
	http = GET(params['href'], headers)
	if http != None:
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http.decode('utf-8'))
		for _div in DT.getElementsByTagName('li'):
			if _div.getAttribute('class') == 'item':
				href  = None
				title = None
				plot  = None
				img = None
				_div2 = _div.getElementsByTagName('h2')
				if len(_div2) > 0:
					_div3 = _div2[0].getElementsByTagName('a')
					if len(_div3) > 0:
						href  = _div3[0].getAttribute('href')
						title = _div3[0].firstChild.data.encode('utf8', 'ignore')
				for _div2 in _div.getElementsByTagName('div'):
					if _div2.getAttribute('class') == 'body':
						_div3 = _div2.getElementsByTagName('p')
						if len(_div3) > 0:
							plot = _div3[0].firstChild.data.encode('utf8', 'ignore')
						for _div3 in _div2.getElementsByTagName('div'):
							if _div3.getAttribute('class') == 'channelLogo':
								_div4 = _div3.getElementsByTagName('img')
								if len(_div4) > 0:
									img = _div4[0].getAttribute('src')
				if (href != None) and (title != None) and (img != None):
					li = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
					li.setInfo(type = 'video', infoLabels = {'plot': plot})
					xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showchannel', 'href':href})), li, True)
		xbmcplugin.endOfDirectory(h)



def showchannel(params):

	import datetime, time

	iindex = 0
	tryes = 0
	basecount = 0
	try: page = int(params['page'])
	except: page  = 1

	nhref = params['href']

	while tryes < 3:
		target = '%s?page=%d' % (nhref, page)
		print 'CURRENT TARGET = [%s]' % target
		if page == 1: headers['Referer'] = 'http://newstube.ru/channels'
		else:         headers['Referer'] = 'http://newstube.ru%s?page=%d' % (nhref, page-1)

		http = GET(target, headers)
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http.decode('utf-8'))
		realcount = 0
		for div in DT.getElementsByTagName('li'):
			if div.getAttribute('class') == 'mediaitem2':
				href  = None
				title = None
				img = icon
				#player_id = None
				tags = ' '

				info = {}
				pwatch = {'func':'watch'}


				for div2 in div.getElementsByTagName('h2'):
					if div2.getAttribute('class') == 'header':
						for div3 in div2.getElementsByTagName('a'):
							if len(div3.getAttribute('href')) > 0:
								title = div3.firstChild.data.encode('utf8', 'ignore') ###

				for div2 in div.getElementsByTagName('img'):
					if div2.getAttribute('class') == 'keyframe':
						img = div2.getAttribute('src') ###

				for div2 in div.getElementsByTagName('p'):
					if div2.getAttribute('class') == 'description':
						info['plot'] = div2.firstChild.data.encode('utf8', 'ignore')

				for div2 in div.getElementsByTagName('div'):
					div2_class = div2.getAttribute('class')
					if div2_class == 'player':
						#player_id =
						pwatch['guid'] = div2.getAttribute('id').encode('utf8', 'ignore') ###


					elif div2_class == 'image':
						for div3 in div2.getElementsByTagName('a'):
							onclick = div3.getAttribute('onclick')
							if onclick:
								try:
									print 'onclick = %s' % onclick
									(rr1, rr2, rr3, rr4, rr5) = re.compile("expose3\(\'(.*?)\', \'(.*?)\', \'(.*?)\', \'(.*?)\', (.*?)\)").findall(onclick)[0]
									#print 'rr1 = %s' % rr1
									#print 'rr2 = %s' % rr2
									#print 'rr3 = %s' % rr3
									#print 'rr4 = %s' % rr4
									#print 'rr5 = %s' % rr5
									pwatch['guid'] = rr2
									pwatch['location'] = rr4
									pwatch['state'] = rr5
									print pwatch
								except: pass

					elif div2_class == 'tags':
						for div3 in div2.getElementsByTagName('a'):
							tags += ' %s' % div3.firstChild.data.encode('utf8', 'ignore')
						info['tagline'] = tags[1:]

					elif div2_class == 'toolbar':
						#print '=toolbar='
						subdata = div2.toxml().encode('utf8', 'ignore')
						#print 'subdata = %s' % subdata
						try:
								# 11.05.2011 18:40
							film_date   = re.compile('title=\"Дата съёмки\".*?<span>(.*?)</span>').findall(subdata)[0]
							#print 'film_date=', film_date
							pdb = datetime.datetime.strptime(str(film_date),'%d.%b.%Y %H:%M')
							info['date'] = str(pdb.strftime('%d.%m.%Y'))
							info['year'] = int(pdb.strftime('%Y'))
							#print 'info[date]=', info['date']
							#print 'info[year]=', info['year']

						except: pass
						try:
							film_author = re.compile('title=\"Автор ролика\".*?<a href=.+?>(.*?)</a></span>').findall(subdata)[0]
							#print 'film_author=' + film_author
							#studio
							#director
							info['playcount'] = film_author
							info['playcount'] = film_author

						except: pass
						try:
							film_scount = re.compile('title=\"Количество просмотров\".*?<span>(.*?)</span>').findall(subdata)[0]
							#print 'film_scount=' + film_scount
							info['playcount'] = int(film_scount)

						except: pass

				if (title != None) and (img != None):
					realcount += 1
					iindex += 1
					name = '%d. %s' % (iindex,title)
					li = xbmcgui.ListItem(name, iconImage = img, thumbnailImage = img)
					li.setInfo(type = 'video', infoLabels = info)
					li.setProperty('IsPlayable', 'true')
					xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(pwatch)), li)
		if tryes == 0: basecount = realcount

		page += 1
		tryes += 1

	if basecount == realcount:
		li = xbmcgui.ListItem('Предыдущее >', iconImage = icon, thumbnailImage = icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showchannel', 'href':params['href'], 'page':page})), li, True)

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


def watch(params):

	print ' = = = = = watch = = = = = '
	guid = params['guid']
	try:    state = params['state']
	except: state = 'nostate'
	try:    location = params['location']
	except: location = 'n2'

	print 'guid    =%s' % guid
	print 'state   =%s' % state
	print 'location=%s' % location




#	GET /n2sitews/player.asmx/GetStartInfo3?includePlayInfo=false&location=n2&sessionHash=nosid&state=1889244281&placement=embed&id=608065cc%2D1329%2D475c%2D8625%2D81eec85f8965 HTTP/1.1
#	Host: app.newstube.ru
#	Connection: keep-alive
#	Referer: http://newstube.ru/FreshPlayer.swf?guid=608065cc-1329-475c-8625-81eec85f8965&state=1889244281&location=n2
#	User-Agent: Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.32 SUSE/13.0.751.0 (KHTML, like Gecko) Chrome/13.0.751.0 Safari/534.32
#	Accept: */*
#	Accept-Encoding: gzip,deflate,sdch
#	Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4
#	Accept-Charset: windows-1251,utf-8;q=0.7,*;q=0.3
#	Cookie: __utmz=193759666.1305470667.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=193759666.828666062.1305470667.1305470667.1305470667.1


#	try:
	req = urllib2.Request('http://app.newstube.ru/n2sitews/player.asmx/GetStartInfo3?includePlayInfo=false&location=%s&sessionHash=nosid&state=%s&placement=embed&id=%s' % (location, state, urllib.quote_plus(guid)))
	req.add_header(     'User-Agent','Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.32 SUSE/13.0.751.0 (KHTML, like Gecko) Chrome/13.0.751.0 Safari/534.32')
	req.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*')
	req.add_header(        'Referer','http://newstube.ru/FreshPlayer.swf?guid=%s&state=%s&location=%s' % (guid,state,location))
	req.add_header('Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
	req.add_header( 'Accept-Charset','utf-8, utf-16, *;q=0.1')
	req.add_header('Accept-Encoding','identity, *;q=0')
	req.add_header(     'Connection','Keep-Alive')
	f = urllib2.urlopen(req)
	a = f.read()
	f.close()
	print a

#HTTP/1.1 200 OK
#Cache-Control: private, max-age=0
#Content-Length: 1215
#Content-Type: text/xml; charset=utf-8
#Server: Microsoft-IIS/6.0
#MicrosoftOfficeWebServer: 5.0_Pub
#X-Powered-By: ASP.NET
#X-AspNet-Version: 2.0.50727
#Date: Mon, 16 May 2011 19:34:49 GMT
#<?xml version="1.0" encoding="utf-8"?>
#<ContentInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://app1.newstube.ru/N2SiteWS/player.asmx">
#  <Medias>
#    <MediaInfo>
#      <Id>608065cc-1329-475c-8625-81eec85f8965</Id>
#      <Name>.............. .......... .......... "................" ..............</Name>
#      <KeyFrame>http://image.newstube.ru/4646716</KeyFrame>
#      <Url>http://www.newstube.ru/media.aspx?mediaid=608065cc-1329-475c-8625-81eec85f8965&amp;linked=embed</Url>
#      <Duration>148020</Duration>
#      <Width xsi:nil="true" />
#      <Height xsi:nil="true" />
#      <Streams>
#        <StreamInfo>
#          <Id>3235892</Id>
#          <QualityId>1</QualityId>
#          <Name>FMS FLV</Name>
#          <Width>400</Width>
#          <Height>294</Height>
#          <Bitrate>0</Bitrate>
#        </StreamInfo>
#        <StreamInfo>
#          <Id>3235893</Id>
#          <QualityId>8</QualityId>
#          <Name>FLV Hi-Resolution</Name>
#          <Width>400</Width>
#          <Height>288</Height>
#          <Bitrate>0</Bitrate>
#        </StreamInfo>
#      </Streams>
#    </MediaInfo>
#  </Medias>
#</ContentInfo>


#GET /n2sitews/player.asmx/GetPlayInfo3?location=n2&sessionHash=nosid&state=1889244281&placement=embed&id=608065cc%2D1329%2D475c%2D8625%2D81eec85f8965 HTTP/1.1
#Host: app.newstube.ru
#Connection: keep-alive
#Referer: http://newstube.ru/FreshPlayer.swf?guid=608065cc-1329-475c-8625-81eec85f8965&state=1889244281&location=n2
#User-Agent: Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.32 SUSE/13.0.751.0 (KHTML, like Gecko) Chrome/13.0.751.0 Safari/534.32
#Accept: */*
#Accept-Encoding: gzip,deflate,sdch
#Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4
#Accept-Charset: windows-1251,utf-8;q=0.7,*;q=0.3
#Cookie: __utmz=193759666.1305470667.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=193759666.828666062.1305470667.1305470667.1305470667.1



	req = urllib2.Request('http://app.newstube.ru/n2sitews/player.asmx/GetPlayInfo3?location=%s&sessionHash=nosid&state=%s&placement=embed&id=%s' % (location, state, urllib.quote_plus(guid)))
	req.add_header(     'User-Agent','Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.32 SUSE/13.0.751.0 (KHTML, like Gecko) Chrome/13.0.751.0 Safari/534.32')
	req.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*')
	req.add_header(        'Referer','http://newstube.ru/FreshPlayer.swf?guid=%s&state=%s&location=%s' % (guid,state,location))
	req.add_header('Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
	req.add_header( 'Accept-Charset','utf-8, utf-16, *;q=0.1')
	req.add_header('Accept-Encoding','identity, *;q=0')
	req.add_header(     'Connection','Keep-Alive')
	f = urllib2.urlopen(req)
	http2 = f.read()
	f.close()
	print http2


#HTTP/1.1 200 OK
#Cache-Control: private, max-age=0
#Content-Length: 1571
#Content-Type: text/xml; charset=utf-8
#Server: Microsoft-IIS/6.0
#MicrosoftOfficeWebServer: 5.0_Pub
#X-Powered-By: ASP.NET
#X-AspNet-Version: 2.0.50727
#Date: Mon, 16 May 2011 19:34:51 GMT
#<?xml version="1.0" encoding="utf-8"?>
#<ContentInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://app1.newstube.ru/N2SiteWS/player.asmx">
#  <Medias>
#    <MediaInfo>
#      <Duration>0</Duration>
#      <Width xsi:nil="true" />
#      <Height xsi:nil="true" />
#      <Streams>
#        <StreamInfo>
#          <Id>3235892</Id>
#          <QualityId>1</QualityId>
#          <Name>FMS FLV</Name>
#          <Width>400</Width>
#          <Height>294</Height>
#          <Bitrate>0</Bitrate>
#          <MediaLocation>
#            <Server>85.26.148.89:80</Server>
#            <App>auth2</App>
#          </MediaLocation>
#        </StreamInfo>
#        <StreamInfo>
#          <Id>3235893</Id>
#          <QualityId>8</QualityId>
#          <Name>FLV Hi-Resolution</Name>
#          <Width>400</Width>
#          <Height>288</Height>
#          <Bitrate>0</Bitrate>
#          <MediaLocation>
#            <Server>85.26.148.79:80</Server>
#            <App>auth2</App>
#          </MediaLocation>
#        </StreamInfo>
#      </Streams>
#    </MediaInfo>
#  </Medias>
#  <Advertising>
#    <PreRolls>
#      <Item>
#        <Id>12</Id>
#        <Url>
#      http://ads.adfox.ru/158247/getCode?p1=bgob&p2=egss&pfc=a&pfb=a&puid1=tvc
#</Url>
#        <Data>
#      http://ads.adfox.ru/158247/getCode?p1=bgob&amp;p2=egss&amp;pfc=a&amp;pfb=a&amp;puid1=tvc
#</Data>
#        <TypeId>1</TypeId>
#      </Item>
#    </PreRolls>
#    <Teasers />
#    <PauseBars />
#  </Advertising>
#</ContentInfo>

	Dom     = xml.dom.minidom.parseString(http2)
	StreamInfo = Dom.getElementsByTagName('StreamInfo')

	stream_Id = StreamInfo[0].getElementsByTagName('Id')[0].firstChild.data.encode('utf8', 'ignore')
	print ' *** stream_Id = %s' % stream_Id

	MediaLocation = StreamInfo[0].getElementsByTagName('MediaLocation')
	Media_Server = MediaLocation[0].getElementsByTagName('Server')[0].firstChild.data.encode('utf8', 'ignore')
	Media_App    = MediaLocation[0].getElementsByTagName('App')[0].firstChild.data.encode('utf8', 'ignore')

	print ' *** Media_Server = %s' % Media_Server
	print ' *** Media_App    = %s' % Media_App




#GET /n2sitews/player.asmx/AdvertisingIsPresent?isPresent=false&id=12 HTTP/1.1
#Host: app.newstube.ru
#Connection: keep-alive
#Referer: http://newstube.ru/FreshPlayer.swf?guid=608065cc-1329-475c-8625-81eec85f8965&state=1889244281&location=n2
#User-Agent: Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.32 SUSE/13.0.751.0 (KHTML, like Gecko) Chrome/13.0.751.0 Safari/534.32
#Accept: */*
#Accept-Encoding: gzip,deflate,sdch
#Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4
#Accept-Charset: windows-1251,utf-8;q=0.7,*;q=0.3
#Cookie: __utmz=193759666.1305470667.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=193759666.828666062.1305470667.1305470667.1305470667.1

#HTTP/1.1 200 OK
#Cache-Control: private, max-age=0
#Content-Length: 0
#Server: Microsoft-IIS/6.0
#MicrosoftOfficeWebServer: 5.0_Pub
#X-Powered-By: ASP.NET
#X-AspNet-Version: 2.0.50727
#Date: Mon, 16 May 2011 19:34:51 GMT



	req = urllib2.Request('http://%s/fcs/ident2' % Media_Server)
	req.add_header(     'User-Agent','Shockwave Flash')
	req.add_header(         'Accept','*/*')
	req.add_header('Cache-Control','no-cache')
	req.add_header( 'Content-Type','application/x-fcs')
	req.add_header('Content-Length','1')
	req.add_header(     'Connection','Keep-Alive')
	f = urllib2.urlopen(req, chr(0))
	Media_ServerW = f.read()
	f.close()
	#Media_ServerW
	print 'Media_ServerW =' + Media_ServerW # srv IP



#POST /fcs/ident2 HTTP/1.1
#Host: 85.26.148.89
#Accept: */*
#User-Agent: Shockwave Flash
#Connection: Keep-Alive
#Cache-Control: no-cache
#Content-Type: application/x-fcs
#Content-Length: 1
#.
#HTTP/1.1 200 OK
#Cache-Control: no-cache
#Connection: Keep-Alive
#Content-Length: 12
#Server: FlashCom/3.5.1
#Content-Type: text/plain

#85.26.148.89


	req = urllib2.Request('http://%s/open/1' % Media_ServerW)
	req.add_header(       'Accept','*/*')
	req.add_header(   'User-Agent','Shockwave Flash')
	req.add_header(   'Connection','Keep-Alive')
	req.add_header('Cache-Control','no-cache')
	req.add_header( 'Content-Type','application/x-fcs')
	req.add_header(   'User-Agent','Shockwave Flash')
	req.add_header(   'Connection','Keep-Alive')
	req.add_header('Cache-Control','no-cache')
	req.add_header( 'Content-Type','application/x-fcs')
	req.add_header('Content-Length','1')

	f = urllib2.urlopen(req, chr(0))
	http4 = f.read()
	f.close()
	print 'http4=' + http4 # srv IP

	req = urllib2.Request('http://%s/open/1' % Media_ServerW)
	req.add_header(       'Accept','*/*')
	req.add_header(   'User-Agent','Shockwave Flash')
	req.add_header(   'Connection','Keep-Alive')
	req.add_header('Cache-Control','no-cache')
	req.add_header( 'Content-Type','application/x-fcs')
	req.add_header(   'User-Agent','Shockwave Flash')
	req.add_header(   'Connection','Keep-Alive')
	req.add_header('Cache-Control','no-cache')
	req.add_header( 'Content-Type','application/x-fcs')
	req.add_header('Content-Length','1')

	f = urllib2.urlopen(req, chr(0))
	http5 = f.read()
	f.close()
	print 'http5=' + http5 # srv IP


#POST /open/1 HTTP/1.1
#Host: 85.26.148.89
#Accept: */*
#User-Agent: Shockwave Flash
#Connection: Keep-Alive
#Cache-Control: no-cache
#Content-Type: application/x-fcs
#User-Agent: Shockwave Flash
#Connection: Keep-Alive
#Cache-Control: no-cache
#Content-Type: application/x-fcs
#Content-Length: 1
#.
#HTTP/1.1 200 OK
#Cache-Control: no-cache
#Connection: Keep-Alive
#Content-Length: 17
#Server: FlashCom/3.5.1
#Content-Type:  application/x-fcs
#2-tmaQJe98nOkYd2
#POST /open/1 HTTP/1.1
#Host: 85.26.148.89
#Accept: */*
#User-Agent: Shockwave Flash
#Connection: Keep-Alive
#Cache-Control: no-cache
#Content-Type: application/x-fcs
#User-Agent: Shockwave Flash
#Connection: Keep-Alive
#Cache-Control: no-cache
#Content-Type: application/x-fcs
#User-Agent: Shockwave Flash
#Connection: Keep-Alive
#Cache-Control: no-cache
#Content-Type: application/x-fcs
#Content-Length: 1
#.
#HTTP/1.1 200 OK
#Cache-Control: no-cache
#Connection: Keep-Alive
#Content-Length: 17
#Server: FlashCom/3.5.1
#Content-Type:  application/x-fcs
#2gtmaQJe88nu8Ij2




#GET /UpEmbedCount.aspx?location=n2&rnd=0%2E42503856075927615&mediaguid=608065cc%2D1329%2D475c%2D8625%2D81eec85f8965 HTTP/1.1
#Host: app1.newstube.ru
#Connection: keep-alive
#Referer: http://newstube.ru/FreshPlayer.swf?guid=608065cc-1329-475c-8625-81eec85f8965&state=1889244281&location=n2
#User-Agent: Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.32 SUSE/13.0.751.0 (KHTML, like Gecko) Chrome/13.0.751.0 Safari/534.32
#Accept: */*
#Accept-Encoding: gzip,deflate,sdch
#Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4
#Accept-Charset: windows-1251,utf-8;q=0.7,*;q=0.3
#Cookie: __utmz=193759666.1305470667.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=193759666.828666062.1305470667.1305470667.1305470667.1

#HTTP/1.1 200 OK
#Cache-Control: private, no-store
#Date: Mon, 16 May 2011 19:34:52 GMT
#Pragma: no-cache
#Content-Type: text/xml
#Expires: Fri, 31 Dec 1999 21:00:00 GMT
#Server: Microsoft-IIS/6.0
#MicrosoftOfficeWebServer: 5.0_Pub
#X-Powered-By: ASP.NET
#X-AspNet-Version: 2.0.50727
#Content-Encoding: gzip
#Vary: Accept-Encoding
#Transfer-Encoding: chunked

#e8
#XML OK
#0



#85.26.148.89

#app auth2/v3
#flashVer LNX 10,3,181,14
#swfUrl http://newstube.ru/FreshPlayer.swf?guid=608065cc-1329.-475c-8625-81eec85f8965&state=1889244281&location=n2
#tcUrl rtmp://85.26.148.89:80/auth2/v3
#pageUrl http://newstube.ru/FreshPlayer.swf?guid=608065cc-132.9-475c-8625-81eec85f8965&state=1889244281&location=n2
#.c..o..(.0l..O.....S..1..6..T.k..9...3A.6..$T......B..f5..i.B.sT./.....0y........$..{Y...kN...]|?.............&%..............&%..................................._result.?..........fmsVer..
#FMS/3,5,1,516..capabilities.@?........mode.?.............level...status..code...NetConnection.Con.nect.Success..description...Connection succeeded...objectEncoding.@.........data.......version...3,5,1,516.........Z.........&%.......N.......
#setStreamPath.............3235892..'01/608065CC-1329-475C-8625-81EEC85F8965C...........createStream.@........B.....
#.........................._result.@.........?.............E.........play............'01/608065CC-1329-475C-8625-81EEC85F8965


	#Media_ServerW # ip
	#Media_App

	FILE = 'rtmpt://%s:80/%s/v3' % (Media_ServerW, Media_App)
	#PlayPath = '%s/%s' % (stream_Id, guid.upper())
	PlayPath = '%s/01/%s' % (stream_Id, guid.upper())
	swfUrl = 'http://newstube.ru/FreshPlayer.swf?guid=%s&state=%s&location=%s' % (guid,state,location)
	tcUrl = 'rtmp://%s:80/%s/v3' % (Media_ServerW, Media_App)
	pageUrl = swfUrl
	u = '%s PlayPath=%s swfUrl=%s tcUrl=%s pageUrl=%s swfVfy=True'%(FILE, PlayPath, swfUrl, tcUrl, pageUrl)
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

