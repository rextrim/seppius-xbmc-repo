import urllib, urllib2, re, sys, os
import xbmcplugin, xbmcgui
import urlparse
import codecs
import xbmcaddon
import xbmc
from YoutubeParser import get_yt
from m3u8parser import parse_megogo, best_m3u8
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from strings import *
import pickle
import xml.dom.minidom as mn
from urlparse import parse_qs
import hashlib
from urllib import unquote_plus
Addon = xbmcaddon.Addon( id = 'plugin.video.cScVOD' )
hos = int(sys.argv[1])
#addon_fanart  = Addon.getAddonInfo('fanart')
addon_id      = Addon.getAddonInfo('id')
xbmcplugin.setContent(hos, 'movies')
std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
		
def _downloadUrl(url):
		u = urllib2.urlopen(url)
		content = u.read()
		u.close()

		return content

def GET(target, post=None):
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        req.add_header('Accept', '*/*')
        req.add_header('Accept-Language', 'ru-RU')
        req.add_header('Accept-Charset', 'utf-8')
        resp = urllib2.urlopen(req)
        http = resp.read()

        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)		
				
def Categories(params):
	if Addon.getSetting('mac') != None:
		box_mac = Addon.getSetting('mac')
	else:
		box_mac = None
	try: searchon = params['search']
	except: searchon = None
	try: 
		url=urllib.unquote(params['link'])
		if box_mac != None:
			sign = '?'
			if url.find('?') > -1:	
				sign = '&'
			url = url + sign + 'box_mac=' + box_mac
		else:
			url = url
		xml = _downloadUrl(url)
		print 'HTTP LEN = [%s]' % len(xml)
		xml = mn.parseString(xml)
		n = 0
		if searchon == None:
			try: search = xml.getElementsByTagName('search_on')[0].firstChild.data
			except: search = None
		if search != None:
			kbd = xbmc.Keyboard()
			kbd.setDefault('')
			kbd.setHeading('Search')
			kbd.doModal()
			if kbd.isConfirmed():
				sts=kbd.getText();
				sign = '?'
				if url.find('?') > -1:	
					sign = '&'
				url2 = url + sign + 'search=' + sts
				xml = _downloadUrl(url2)
			else:
				xml = _downloadUrl(url)
			print 'HTTP LEN = [%s]' % len(xml)
			xml = mn.parseString(xml)
			for prev_page_url in xml.getElementsByTagName('prev_page_url'):
				prev_url = xml.getElementsByTagName('prev_page_url')[0].firstChild.data
				prev_title =  "[COLOR FFFFFF00]<-" + prev_page_url.getAttribute('text').encode('utf-8') +'[/COLOR]'
				uri = construct_request({
					'func': 'Categories',
					'link':prev_url 
					})	
				listitem=xbmcgui.ListItem(prev_title, 'DefaultVideo.png', 'DefaultVideo.png')
				xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
			for next_page_url in xml.getElementsByTagName('next_page_url'):
				next_url = xml.getElementsByTagName('next_page_url')[0].firstChild.data
				next_title =  "[COLOR FFFFFF00]->" + next_page_url.getAttribute('text').encode('utf-8') +'[/COLOR]'
				uri = construct_request({
					'func': 'Categories',
					'link':next_url 
					})	
				listitem=xbmcgui.ListItem(next_title, 'DefaultVideo.png', 'DefaultVideo.png')
				xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
			for channel in xml.getElementsByTagName('channel'):
				try: title = channel.getElementsByTagName('title')[0].firstChild.data.encode('utf-8')
				except: title = 'No title or error'
				title = title.replace('<b>', '')
				title = title.replace('</b>', '')
				try:
					description = channel.getElementsByTagName('description')[0].firstChild.data.encode('utf-8')
					img_src_list = re.findall('img .*?src="(.*?)"', description)
					if len(img_src_list) > 0:
						img_src = img_src_list[0]
					else:
						img_src_list = re.findall("img .*?src='(.*?)'", description)
						if len(img_src_list) > 0:
							img_src = img_src_list[0]
					description = description.replace('<br>', '\n')
					description = description.replace('<br/>', '\n')
					description = description.replace('</h1>', '</h1>\n')
					description = description.replace('</h2>', '</h2>\n')
					description = description.replace('&nbsp;', ' ')
					description4playlist_html = description
					text = re.compile('<[\\/\\!]*?[^<>]*?>')
					description = text.sub('', description)
					plot = description
				except: 
					description = 'No description'
					plot = description
					img_src = 'DefaultVideo.png'
				n = n+1
				try: 
					link = channel.getElementsByTagName('playlist_url')[0].firstChild.data
					mysetInfo={}
					mysetInfo['plot'] = plot
					mysetInfo['plotoutline'] = plot
					uri = construct_request({
						'func': 'Categories',
						'link':link 
						})	
					listitem=xbmcgui.ListItem(title, img_src, img_src)
					listitem.setInfo(type = 'video', infoLabels = mysetInfo)
					xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
				except: link = None
				try: 
					stream = channel.getElementsByTagName('stream_url')[0].firstChild.data
					mysetInfo={}
					mysetInfo['plot'] = plot
					mysetInfo['plotoutline'] = plot
					if img_src != None:
						uri = construct_request({
							'func': 'Play',
							'title':title,
							'img':img_src,
							'stream':stream 
							})	
					else:
						uri = construct_request({
							'func': 'Play',
							'title':title,
							'stream':stream 
							})
					listitem=xbmcgui.ListItem(title, img_src, img_src)
					listitem.setInfo(type = 'video', infoLabels = mysetInfo)
					xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
				except: stream = None
			xbmc.executebuiltin('Container.SetViewMode(504)')
			xbmcplugin.endOfDirectory(hos)
		else:
			for prev_page_url in xml.getElementsByTagName('prev_page_url'):
				prev_url = xml.getElementsByTagName('prev_page_url')[0].firstChild.data
				prev_title =  "[COLOR FFFFFF00]<-" + prev_page_url.getAttribute('text').encode('utf-8') +'[/COLOR]'
				uri = construct_request({
					'func': 'Categories',
					'link':prev_url 
					})	
				listitem=xbmcgui.ListItem(prev_title, 'DefaultVideo.png', 'DefaultVideo.png')
				xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
			for next_page_url in xml.getElementsByTagName('next_page_url'):
				next_url = xml.getElementsByTagName('next_page_url')[0].firstChild.data
				next_title =  "[COLOR FFFFFF00]->" + next_page_url.getAttribute('text').encode('utf-8') +'[/COLOR]'
				uri = construct_request({
					'func': 'Categories',
					'link':next_url 
					})	
				listitem=xbmcgui.ListItem(next_title, 'DefaultVideo.png', 'DefaultVideo.png')
				xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
			for channel in xml.getElementsByTagName('channel'):
				try: title = channel.getElementsByTagName('title')[0].firstChild.data.encode('utf-8')
				except: title = 'No title or error'
				title = title.replace('<b>', '')
				title = title.replace('</b>', '')
				try:
					description = channel.getElementsByTagName('description')[0].firstChild.data.encode('utf-8')
					img_src_list = re.findall('img .*?src="(.*?)"', description)
					if len(img_src_list) > 0:
						img_src = img_src_list[0]
					else:
						img_src_list = re.findall("img .*?src='(.*?)'", description)
						if len(img_src_list) > 0:
							img_src = img_src_list[0]
					description = description.replace('<br>', '\n')
					description = description.replace('<br/>', '\n')
					description = description.replace('</h1>', '</h1>\n')
					description = description.replace('</h2>', '</h2>\n')
					description = description.replace('&nbsp;', ' ')
					description4playlist_html = description
					text = re.compile('<[\\/\\!]*?[^<>]*?>')
					description = text.sub('', description)
					plot = description
				except: 
					description = 'No description'
					plot = description
					img_src = 'DefaultVideo.png'
				n = n+1
				try: 
					link = channel.getElementsByTagName('playlist_url')[0].firstChild.data
					mysetInfo={}
					mysetInfo['plot'] = plot
					mysetInfo['plotoutline'] = plot
					uri = construct_request({
						'func': 'Categories',
						'link':link 
						})	
					listitem=xbmcgui.ListItem(title, img_src, img_src)
					listitem.setInfo(type = 'video', infoLabels = mysetInfo)
					xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
				except: link = None
				try: 
					stream = channel.getElementsByTagName('stream_url')[0].firstChild.data
					mysetInfo={}
					mysetInfo['plot'] = plot
					mysetInfo['plotoutline'] = plot
					if img_src != None:
						uri = construct_request({
							'func': 'Play',
							'title':title,
							'img':img_src,
							'stream':stream 
							})	
					else:
						uri = construct_request({
							'func': 'Play',
							'title':title,
							'stream':stream 
							})
					listitem=xbmcgui.ListItem(title, img_src, img_src)
					listitem.setInfo(type = 'video', infoLabels = mysetInfo)
					xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
				except: stream = None
			xbmc.executebuiltin('Container.SetViewMode(504)')
			xbmcplugin.endOfDirectory(hos)
		print 'Channels = [%s]' % n
	except:
		uri = construct_request({
			'func': 'Categories',
			'link': 'http://93.188.161.204/vod/start.xml' 
			})	
		listitem=xbmcgui.ListItem('SashaGamliy and mocckba', 'http://www.kartina.tv/media/glossary/5/img.png', 'http://www.kartina.tv/media/glossary/5/img.png')
		xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
		uri = construct_request({
			'func': 'Categories',
			'link':	'http://enigma2.videonavigator.net.ua/portal.xml' 
			})	
		listitem=xbmcgui.ListItem('cvykas and sb69', 'http://img23.binimage.org/28/fc/3f/portal_sb69.png', 'http://img23.binimage.org/28/fc/3f/portal_sb69.png')
		xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
		uri = construct_request({
			'func': 'Categories',
			'link': 'http://obovse.ru/alexkdpu.php' 
			})	
		listitem=xbmcgui.ListItem('alexdpu', 'http://www.kartina.tv/media/glossary/5/img.png', 'http://www.kartina.tv/media/glossary/5/img.png')
		xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
		xbmc.executebuiltin('Container.SetViewMode(504)')
		xbmcplugin.endOfDirectory(hos)

def Play(params):
	url = urllib.unquote(params['stream'])
	try: img = params['img']
	except: img = 'DefaultVideo.png'
	title = params['title']
	if url.find('vk.com') > -1:
		http=GET(params['stream'])
		soup = BeautifulSoup(http, fromEncoding="windows-1251")
		av=0
		for rec in soup.findAll('param', {'name':'flashvars'}):
		#print rec
			for s in rec['value'].split('&'):
				if s.split('=',1)[0] == 'uid':
					uid = s.split('=',1)[1]
				if s.split('=',1)[0] == 'vtag':
					vtag = s.split('=',1)[1]
				if s.split('=',1)[0] == 'host':
					host = s.split('=',1)[1]
				if s.split('=',1)[0] == 'vid':
					vid = s.split('=',1)[1]
				if s.split('=',1)[0] == 'oid':
					oid = s.split('=',1)[1]
				if s.split('=',1)[0] == 'hd':
					hd = s.split('=',1)[1]
			url = host+'u'+uid+'/videos/'+vtag+'.240.mp4'
			if int(hd)==3:
				url = host+'u'+uid+'/videos/'+vtag+'.720.mp4'
			if int(hd)==2:
				url = host+'u'+uid+'/videos/'+vtag+'.480.mp4'
			if int(hd)==1:
				url = host+'u'+uid+'/videos/'+vtag+'.360.mp4'
		#print video
			#video = url
			
	if url.find('.minizal.net/video/md5hash') > -1:
		url1 = 'http://s2.minizal.net/php/play.php?name=film/pod.krovatju.2012.bdrip.flv'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('video/(.*?)/', page)
			if len(code) > 0:
				md5hash = code[0]
				url = url.replace('md5hash', md5hash)
		except Exception as ex:
			print ex

	if url.find('.lovekino.tv/video/md5hash') > -1:
		url1 = 'http://s2.lovekino.tv/player/play.php?name=films/klyatva.na.krovi.2010.xvid.iptvrip.filesx.flv'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('video/(.*?)/', page)
			if len(code) > 0:
				md5hash = code[0]
				url = url.replace('md5hash', md5hash)
		except Exception as ex:
			print ex

	if url.find('.kinoylei.ru') > -1:
		url1 = 'http://server1.kinoylei.ru/get2/3074'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('film/(.*?)/', page)
			if len(code) > 0:
				md5hash = code[0]
				url = url.replace('md5hash', md5hash)
		except Exception as ex:
			print ex

	if url.find('fs.to/view') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall("url: '/get/play/(.*)',", page)
			if len(code) > 0:
				md5hash = code[0]
				url = 'http://fs.to/get/play/' + md5hash
		except Exception as ex:
			print ex

	if url.find('moonwalk.cc/video') > -1:
		url = url.replace('http://moonwalk.cc/video/', '')
		url = url.replace('/iframe', '')
		url1 = 'http://93.188.161.204/php/token.php?token=' + url
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('"manifest_m3u8":"(.*)"}', page)
			if len(code) > 0:
				url = code[0]
		except Exception as ex:
			print ex
					
	if url.find('stepashka.com/video/') > -1:
		url1 = 'http://online.stepashka.com/filmy/trillery/26171-oblivion-oblivion-2013.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.0; rv:12.0) Gecko/20100101 Firefox/12.0',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall('"st=http://online.stepashka.com\\/player\\/26171\\/.*\\/(.*)\\/1"', page)
			if len(code_list) > 0:
				md5 = code_list[0]
				url = url.replace('md5hash', md5)
				print 'stepashka'
				print url
		except Exception as ex:
			print ex

	if url.find('kaban.tv/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall(',"file":"(.*)","f', page)
			if len(code_list) > 0:
				code = code_list[0]
				code_url = 'http://93.188.161.204/php/kaban/kaban.php?code=' + code
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
					'Connection': 'Close'})
				hash = urllib2.urlopen(request2).read()
				url = hash
				print 'kabantv'
				print url
		except Exception as ex:
			print ex
	
	if url.find('dailymotion.com') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			regex = re.findall('stream_h264_url":"(.*?)"', page)
			url = regex[0].replace('\\', '')
		except Exception as ex:
			print ex

	if url.find('mp333.do.am') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			regex1 = re.findall('var link1 = "(.*?)[?]lang', page)
			regex2 = re.findall('var link1 = ".*?lang=(.*?)&', page)
			regex3 = re.findall('var link1 = ".*?&id=(.*?)"', page)
			url = regex1[0] + regex2[0] + '/' + regex3[0]
		except Exception as ex:
			print ex

	if url.find('hubu.ru') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			regex = re.findall(",'(.*?)'", page)
			url = regex[0]
		except Exception as ex:
			print ex

	if url.find('zaycev.net') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			regex = re.findall('encodeURIComponent.*?id=(.*?)&', page)
			regex2 = re.findall('encodeURIComponent.*?id=.*?&ass=(.*?)"', page)
			regex3 = re.findall('encodeURIComponent.*?id=(.*?)..&', page)
			url = 'http://dl.zaycev.net/mini/' + regex3[0] + '/' + regex[0] + '/' + regex2[0] + '.mp3'
		except Exception as ex:
			print ex
	
	if url.find('loveradio.ru') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			regex = re.findall("{uid: '(.*?)'", page)
			regex2 = re.findall('icons/(.*?).png', page)
			if regex2[0] == 'loveradio' or regex2[0] == 'top40' or regex2[0] == 'jlo':
				regex3 = regex2[0]
			else:
				regex3 = 'love_' + regex2[0]
			url = 'http://stream2.loveradio.ru:9000/' + regex3 + '_64?type=.flv&UID=' + regex[0]
		except Exception as ex:
			print ex

	if url.find('mediacdn.ru') > -1:
		event = re.findall('event=(\\d+)', url)
		request = urllib2.Request('http://app1.bonus-tv.ru/api/channels', None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'X-Requested-With': 'XMLHttpRequest',
			'Host': 'app.bonus-tv.ru',
			'Referer': 'http://bonus-tv.ru:90/lg/publish/',
			'X_USERNAME': 'c3d33d76a835a59ff32bb65e77dfa45c',
			'X_PASSWORD': 'c3d33d76a835a59ff32bb65e77dfa45c'})
		try:
			page = urllib2.urlopen(request).read()
			hash = re.findall('event=' + event[0] + '&hash=(.*?)"', page)
			url = url + hash[0]
		except Exception as ex:
			print ex
	
	if url.find('//kino-v-online.tv/kino/md5') > -1 or url.find('//kino-v-online.tv/serial/md5') > -1 or url.find('?st=1') > -1:
		url1 = 'http://kino-v-online.tv/2796-materik-online-film.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			hash_list = re.findall('/kino/(.*?)/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('kinoprosmotr.net/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall(';file=(.*?)\\.flv', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = hash + '.flv'
		except Exception as ex:
			print ex

	if url.find('kinoprosmotr.org/video/') > -1:
		url1 = 'http://kinoprosmotr.net/serial/1839-ne-ver-su-iz-kvartiry-23.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('serial.php%3Fip%3D(.*?)%26fi', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('film-center.info/') > -1:
		url1 = 'http://srv1.film-center.info/player/play.php?name=flv/full/zavtrak.na.trave.1979.dvdrip.flv'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('\\/video\\/(.*?)\\/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('onlinefilmx.ru/video') > -1 or url.find('onlinefilmx.tv/video') > -1:
		url1 = 'http://s2.onlinefilmx.tv/player/play.php?id=882'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('\\/video\\/(.*?)\\/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('minizal.net/') > -1:
		url1 = 'http://s2.minizal.net/php/playlist.php?pl=/syn_otca_narodov.txt'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('\\/video\\/(.*?)\\/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('porntube.com') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			q = re.findall('\\?\\?(.*?)\\&\\&', url)
			q = q[0]
			print 'aaaaaaaaaaaaaaaaaaaa q:' + q
			pos = page.find('<stream label="' + q)
			tmp = page[page.find('<stream label="' + q):page.find('</stream>', pos)]
			print 'bbbbbbbbbbbbbbbbbbbb tmp:' + tmp
			film = re.findall('<file>(.*?)<', tmp)
			if len(film) > 0:
				film = film[0]
				url = film.replace('&amp;', '&')
		except Exception as ex:
			print ex

	if url.find('latino-serialo.ru') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall(';pl=(.*?)"', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				print 'hash ' + hash
				request2 = urllib2.Request(hash, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				page = urllib2.urlopen(request2).read()
				page = page.replace('\n', '')
				tmp = re.findall('file":"(.*?)"', page)
				tmp = tmp[0]
				print 'rrrrrrrrrrrrrrrrrrrrrrrrrr tmp ' + tmp
				md5hash = re.findall('\\/video\\/(.*?)\\/', tmp)
				md5hash = md5hash[0]
				tmp2 = tmp.replace(md5hash, 'md5hash')
				md4hash = re.findall('\\/md5hash\\/(.*?)\\/', tmp2)
				md4hash = md4hash[0]
				print 'aaaaaaaaaaaaaaaaaaaaaaaa md5hash ' + md5hash
				print 'bbbbbbbbbbbbbbbbbbbbbbbbbbb md4hash ' + md4hash
				string = re.findall('\\?\\?(.*?)\\&\\&', url)
				string = string[0]
				print 'bbbbbbbbbbbbbbbbbbbbbbbbbbb string ' + string
				url2 = string.replace('md5hash', md5hash)
				url = url2.replace('md4hash', md4hash)
		except Exception as ex:
			print ex

	if url.find('allserials.tv/s/md5') > -1:
		url1 = 'http://allserials.tv/get.php?action=playlist&pl=Osennie.cvety.2009'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			if len(page) > 0:
				code_url = 'http://gegen-abzocke.com/xml/nstrim/allserials/code.php?code_url=' + page
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				hash = urllib2.urlopen(request2).read()
				url = url.replace('md5hash', hash)
				print 'filmix'
				print url
		except Exception as ex:
			print ex

	if url.find('kinopod.org/get/md5') > -1 or url.find('flvstorage.com/get/md5') > -1:
		url1 = 'http://kinopod.tv/serials/episode/38967.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('\\/get\\/(.*?)\\/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('kino-live.org/s/md5') > -1:
		url1 = 'http://kino-live.org/hq/715505-slova.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('\\/s\\/(.*?)\\/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('kinobanda.net/') > -1:
		url1 = 'http://kinobanda.net/get.php?pl=23298/1/0/'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			if len(page) > 0:
				hash = page[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('kino-dom.tv/s/md5') > -1:
		url1 = 'http://kino-dom.tv/drama/1110-taynyy-krug-the-sesret-sirsle-1-sezon-1-seriya-eng-onlayn.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('pl:"http:\\/\\/kino-dom\\.tv\\/(.*?)\\/play\\/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('new-kino.net') > -1:
		url1 = 'http://new-kino.net/komedii/5631-igrushka-1982.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('\\/dd11\\/(.*?)\\/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('linecinema.org/s/md5') > -1:
		url1 = 'http://www.linecinema.org/newsz/boevyk-online/508954-bliznecy-drakony-twin-dragons-1992-dvdrip-onlayn.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('linecinema\\.org\\/s\\/(.*?)\\/', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = url.replace('md5hash', hash)
		except Exception as ex:
			print ex

	if url.find('//figvam.ru/') > -1:
		url = url.replace('figvam.ru', 'go2load.com')
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('\n', '')
			hash_list = re.findall('ftp\\:\\/\\/(.*?)"', page)
			if len(hash_list) > 0:
				hash = hash_list[0]
				url = 'ftp://' + hash
			print url
		except Exception as ex:
			print ex

	if url.find('allinspace.com/') > -1:
		url_row = re.findall('&(.*?)&&', url)
		url_row = url_row[0]
		request = urllib2.Request(url_row, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			url1 = re.findall('ttp://(.*?)&', url)
			url1 = url1[0]
			url = 'http://' + url1
		except Exception as ex:
			print ex

	if url.find('.igru-film.net/') > -1:
		url_row = re.findall('xyss(.*?)xys', url)
		url_row = url_row[0]
		url_film = 'http://fepcom.net/' + url_row
		film = re.findall('ssa(.*?)xyss', url)
		film = film[0]
		request = urllib2.Request(url_film, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			film_row = re.findall(';file=([^&]*)', page)
			if len(film_row) > 0:
				film_row = film_row[0]
				code_url = 'http://gegen-abzocke.com/xml/nstrim/fepcom/code.php?code_url=' + film_row
				request = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				code = urllib2.urlopen(request).read()
				url = film.replace('md5hash', code)
		except Exception as ex:
			print ex

	if url.find('kinoylei.ru/') > -1:
		url1 = 'http://server1.kinoylei.ru/player/pl.php?id=2902-3142'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('video/(.*?)/supervideo', page)
			if len(code) > 0:
				md5hash = code[0]
				url = url.replace('md5hash', md5hash)
		except Exception as ex:
			print ex

	if url.find('//77.120.114') > -1 or url.find('nowfilms.ru/') > -1:
		url_row = re.findall('xyss(.*?)xys', url)
		url_row = url_row[0]
		url_film = 'http://' + url_row
		film = re.findall('ssa(.*?)xyss', url)
		film = film[0]
		film_end = re.findall('/md5hash/(.*?)xys', url)
		film_end = film_end[0]
		request = urllib2.Request(url_film, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			link = urllib2.urlopen(request).read()
			film_row = re.findall(';pl=([^"]*)', link)
			if len(film_row) > 0:
				film_row = film_row[0]
				if film_row.find('/tmp/') > 0:
					request2 = urllib2.Request(film_row, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
					'Connection': 'Close'})
					link = urllib2.urlopen(request2).read()
					indexer = link.find(film_end)
				if indexer > 0:
					md5hash = link[indexer - 23:indexer - 1]
					url = film.replace('md5hash', md5hash)
			else:
				url = re.findall(';file=([^"]*)', link)
				url = url[0]
		except Exception as ex:
			print ex

	if url.find('mightyupload') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			link1 = urllib2.urlopen(request).read()
			if link1.find('|mkv|') > -1:
				hash = re.findall('mkv\\|(.*?)\\|', link1)
				hash = hash[0]
				ip = re.findall('false\\|(.*?)\\|', link1)
				ip = ip[0]
				mp4 = 'mkv'
				url = 'http://192.96.204.' + ip + ':182/d/' + hash + '/video.' + mp4
			else:
				hash = re.findall('video\\|(.*?)\\|', link1)
				hash = hash[0]
				ip = re.findall('www\\|(.*?)\\|', link1)
				ip = ip[0]
				mp4 = re.findall('image\\|(.*?)\\|', link1)
				mp4 = mp4[0]
				url = 'http://192.96.204.' + ip + ':182/d/' + hash + '/video.' + mp4
		except Exception as ex:
			print ex

	if url.find('baskino.com') > -1:
		string = re.findall('\\?\\?(.*?)\\&\\&', url)
		string = string[0]
		print string + 'string'
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			indexer = page.find(string)
			link2 = page[indexer - 150:indexer]
			link2 = link2.replace('\\', '')
			link2 = link2 + string + '"'
			url1 = re.findall('file:"(.*?)"', link2)
			url = url1[0]
		except Exception as ex:
			print ex

	if url.find('kset.kz') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('ImZpbGUi(.*?)=', page)
			code = code[0]
			if len(code) > 0:
				code_url = 'http://gegen-abzocke.com/xml/nstrim/kset/code.php?code_url=' + code
				request3 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				url = urllib2.urlopen(request3).read()
		except Exception as ex:
			print ex

	if url.find('//kinostok.tv/video/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('file: "(.*?)"', page)
			code = code[0]
			if len(code) > 0:
				code_url = 'http://gegen-abzocke.com/xml/nstrim/kinostok/code.php?code_url=' + code
				request3 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				url = urllib2.urlopen(request3).read()
		except Exception as ex:
			print ex

	if url.find('//kinostok.tv/player/') > -1 or url.find('//kinostok.tv/embed') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			if len(page) > 0:
				code_url = 'http://gegen-abzocke.com/xml/nstrim/kinostok/code.php?code_url=' + page
				request3 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				tmp = urllib2.urlopen(request3).read()
				url1 = re.findall('file":"(.*?)"', tmp)
				url = url1[0]
		except Exception as ex:
			print ex

	if url.find('.kinoxa-x.ru') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('video.*src="(.*)"', page)
			code = code[0]
			if len(code) > 0:
				url = code
		except Exception as ex:
			print ex

	if url.find('kinohd.org') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall("file : '(.*?)'", page)
			code = code[0]
			if len(code) > 0:
				url = code
		except Exception as ex:
			print ex

	if url.find('imovies.ge/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('file>(.*?)<', page)
			code = code[0]
			if len(code) > 0:
				url = code
		except Exception as ex:
			print ex

	if url.find('veterok.tv/v/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('file:"(.*?)"', page)
			code = code[0]
			if len(code) > 0:
				url = code
		except Exception as ex:
			print ex

	if url.find('.tushkan.net/php') > -1 or url.find('rugailo.net/php') > -1 or url.find('videose.org/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall("file:'(.*?)'", page)
			code = code[0]
			if len(code) > 0:
				url = code
		except Exception as ex:
			print ex

	if url.find('.tushkan.net/video') > -1:
		url1 = 'http://srv3.tushkan.net/php/tushkan.php?name=film/Slova.2012.flv'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('video/(.*?)/', page)
			if len(code) > 0:
				md5hash = code[0]
				url = url.replace('md5hash', md5hash)
		except Exception as ex:
			print ex

	if url.find('jampo.com.ua') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall("flashvars.File = '(.*?)'", page)
			code = code[0]
			if len(code) > 0:
				url = code
		except Exception as ex:
			print ex

	if url.find('api.video.mail.ru/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code = re.findall('sd":"(.*?)"', page)
			code = code[0]
			if len(code) > 0:
				url = code
		except Exception as ex:
			print ex

	if url.find('/streaming.video.') > -1:
		try:
			id_list = re.findall('get-location/(.*)/m', url)
			id = id_list[0]
			url1 = 'http://static.video.yandex.ru/get-token/' + id + '?nc=0.50940609164536'
			request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
			page = urllib2.urlopen(request).read()
			hash_list = re.findall('token>(.*)</token>', page)
			hash = hash_list[0]
			link1 = url.replace('md5hash', hash)
			request2 = urllib2.Request(link1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
			page2 = urllib2.urlopen(request2).read()
			film_list = re.findall('video-location>(.*)</video-location>', page2)
			film = film_list[0]
			url = film.replace('&amp;', '&')
		except Exception as ex:
			print ex

	if url.find('embed.nowvideo.eu/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			film1 = re.findall('flashvars.file="(.*)";', page)
			film = film1[0]
			filekey1 = re.findall('flashvars.filekey="(.*)";', page)
			filekey = filekey1[0]
			xml_url = 'http://www.nowvideo.eu/api/player.api.php?user=undefined&codes=1&key=' + filekey + '&pass=undefined&file=' + film
			request = urllib2.Request(xml_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
			page = urllib2.urlopen(request).read()
			url2 = re.findall('http(.*)&title', page)
			url1 = url2[0]
			url = 'http' + url1
		except Exception as ex:
			print ex

	if url.find('novamov.com/embed') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			film1 = re.findall('flashvars.file="(.*)";', page)
			film = film1[0]
			filekey1 = re.findall('flashvars.filekey="(.*)";', page)
			filekey = filekey1[0]
			xml_url = 'http://www.novamov.com/api/player.api.php?user=undefined&codes=1&key=' + filekey + '&pass=undefined&file=' + film
			request = urllib2.Request(xml_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
			page = urllib2.urlopen(request).read()
			url2 = re.findall('http(.*)&title', page)
			url1 = url2[0]
			url = 'http' + url1
		except Exception as ex:
			print ex

	if url.find('videoweed.es/file/') > -1 or url.find('videoweed.es/embed') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			film1 = re.findall('flashvars.file="(.*)";', page)
			film = film1[0]
			filekey1 = re.findall('flashvars.filekey="(.*)";', page)
			filekey = filekey1[0]
			xml_url = 'http://www.videoweed.es/api/player.api.php?user=undefined&codes=1&key=' + filekey + '&pass=undefined&file=' + film
			request = urllib2.Request(xml_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
			'Connection': 'Close'})
			page = urllib2.urlopen(request).read()
			url2 = re.findall('http(.*)&title', page)
			url1 = url2[0]
			url = 'http' + url1
		except Exception as ex:
			print ex

	if url.find('/video.sibnet.ru') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			page = page.replace('&amp;', '&')
			url_list = re.findall('<file>(.*?)<\\/file>', page)
			if len(url_list) > 0:
				url = url_list[0]
				print 'sibnet'
				print url
		except Exception as ex:
			print ex

	if url.find('namba.net/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			id = re.findall('video\\/(.*?)\\/', url)
			id = id[0]
			page = urllib2.urlopen(request).read()
			url_list = re.findall("CSRF_TOKEN='(.*?)'", page)
			print url_list
			if len(url_list) > 0:
				token = url_list[0]
				url1 = 'http://namba.net/api/?service=video&action=video&token=' + token + '&id=' + id
				request2 = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				page = urllib2.urlopen(request2).read()
				url_list2 = re.findall('flv":"(.*?)"', page)
				film2 = url_list2[0]
				url = film2.replace('\\', '')
				print 'namba'
				print url
		except Exception as ex:
			print ex

	if url.find('filmix.net/s/md5hash') > -1 or url.find('filevideosvc.org/s/md5hash') > -1:
		url1 = 'http://filmix.net/semejnyj/36974-tor-legenda-vikingov-legends-of-valhalla-thor-2011.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall(';file=(.*?)&', page)
			if len(code_list) > 0:
				code = code_list[0]
				code_url = 'http://gegen-abzocke.com/xml/nstrim/filmix/code.php?code_url=' + code
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				hash = urllib2.urlopen(request2).read()
				url = url.replace('md5hash', hash)
				print 'filmix'
				print url
		except Exception as ex:
			print ex

	if url.find('.tfilm.tv/') > -1:
		url1 = 'http://filmin.ru/28234-buket.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall(';file=(.*?)&', page)
			if len(code_list) > 0:
				code = code_list[0]
				code_url = 'http://gegen-abzocke.com/xml/nstrim/filmin/code.php?code_url=' + code
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				hash = urllib2.urlopen(request2).read()
				url = url.replace('md5hash', hash)
				print 'filmin'
				print url
		except Exception as ex:
			print ex

	if url.find('bigcinema.tv') > -1:
		url1 = 'http://bigcinema.tv/movie/prometey---prometheus.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall('file:"(.*?)"', page)
			if len(code_list) > 0:
				code = code_list[0]
				code_url = 'http://gegen-abzocke.com/xml/nstrim/bigcinema/code.php?code_url=' + code
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				hash = urllib2.urlopen(request2).read()
				url = url.replace('md5hash', hash)
				print 'filmix'
				print url
		except Exception as ex:
			print ex

	if url.find('.datalock.ru/') > -1:
		url1 = 'http://newseriya.ru/serial-3151-Kak_ya_vstretil_vashu_mamu-7-season.html'
		request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall('"pl":"(.*?)"', page)
			if len(code_list) > 0:
				code = code_list[0]
				code_url = 'http://gegen-abzocke.com/xml/nstrim/seasonvar/code.php?code_url=' + code
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				hash = urllib2.urlopen(request2).read()
				url = url.replace('md5hash', hash)
				print 'seasonvar'
				print url
		except Exception as ex:
			print ex

	
	if url.find('//77.120.119') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall('file":"(.*?)"', page)
			if len(code_list) > 0:
				code = code_list[0]
				code_url = 'http://gegen-abzocke.com/xml/nstrim/liveonline/code.php?code_url=' + code
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				url = urllib2.urlopen(request2).read()
				print 'filmix'
				print url
		except Exception as ex:
			print ex

	if url.find('uletfilm.net/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall('file":"(.*?)"', page)
			if len(code_list) > 0:
				code = code_list[0]
				code_url = 'http://gegen-abzocke.com/xml/nstrim/uletno/code.php?code_url=' + code
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				url = urllib2.urlopen(request2).read()
				print 'filmix'
				print url
		except Exception as ex:
			print ex

	if url.find('//vtraxe.com/') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall('3Fv=(.*?)&', page)
			if len(code_list) > 0:
				code = code_list[0]
				code_url = 'http://gegen-abzocke.com/xml/nstrim/uletno/code.php?code_url=' + code
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
				'Connection': 'Close'})
				url = urllib2.urlopen(request2).read()
				print 'filmix'
				print url
		except Exception as ex:
			print ex

	if url.find('uakino') > -1:
		request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 cScVOD 1.0 for XBMC',
		'Connection': 'Close'})
		try:
			page = urllib2.urlopen(request).read()
			code_list = re.findall('file":"(.*?)"', page)
			if len(code_list) > 0:
				url = code_list[0]
				print 'uakino'
				print url
		except Exception as ex:
			print ex
	
	if url.find('youtube.com') > -1:
		try:
			video = get_yt(url)
			url = video
			print url
		except Exception as ex:
			print ex
			
	if url.find('m3u8') > -1:
		best_m3u8(url)		
			
	if url.find('megogo') > -1:
		try:
			req = urllib2.Request(url, None, {'User-agent': 'QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1 Service Pack 3)'})
			page = urllib2.urlopen(req).read()
		except Exception as ex:
			print ex
        
		print 'fillm url = ', url
		video = parse_megogo(url)
		url = video
		print '#'		
		
	i = xbmcgui.ListItem(title, url, img, img)
	xbmc.Player().play(url, i)
	
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
	
params = get_params(sys.argv[2])
try:
    func = params['func']
    del params['func']
except:
    func = None
    xbmc.log( '[%s]: Primary input' % addon_id, 1 )
    Categories(params)
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)