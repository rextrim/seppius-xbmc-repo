#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Writer (c) 23/06/2011, Khrysev D.A., E-mail: x86demon@gmail.com
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

import urllib
import urllib2
import re
import sys
import os
import cookielib
import simplejson as json
import SimpleDownloader as downloader

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

__author__ = "Dmitry Khrysev"
__license__ = "GPL"
__maintainer__ = "Dmitry Khrysev"
__email__ = "x86demon@gmail.com"
__status__ = "Production"

__settings__ = xbmcaddon.Addon(id='plugin.video.fs.ua')
__language__ = __settings__.getLocalizedString
__addondir__ =xbmc.translatePath(__settings__.getAddonInfo('profile'))
__addondir__ = __addondir__.decode(sys.getfilesystemencoding())

if os.path.exists(__addondir__) == False:
	os.mkdir(__addondir__)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'brb.to'
httpSiteUrl = 'http://' + siteUrl
cookiepath = os.path.join(__addondir__, 'plugin.video.fs.ua.cookies.lwp')

h = int(sys.argv[1])

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def htmlEntitiesDecode(string):
	return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

headers  = {
	'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

def getFullUrl(url):
        if not '://' in url:
		url = httpSiteUrl + url
        return url

def GET(url, referer, post_params = None):
	
	headers['Referer'] = referer
	url = getFullUrl(url)
	
	if post_params != None:
		post_params = urllib.urlencode(post_params)
		headers['Content-Type'] = 'application/x-www-form-urlencoded'
	elif headers.has_key('Content-Type'):
		del headers['Content-Type']

	jar = cookielib.LWPCookieJar(cookiepath)
	if os.path.isfile(cookiepath):
		jar.load()

	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
	urllib2.install_opener(opener)
	req = urllib2.Request(url, post_params, headers)

	response = opener.open(req)
	the_page = response.read()
	response.close()

	jar.save()

	return the_page

def logout(params):
	GET(httpSiteUrl + '/logout.aspx', httpSiteUrl)
	__settings__.setSetting("Login", "");
	__settings__.setSetting("Password", "");

def check_login():
	login = __settings__.getSetting("Login")
	password = __settings__.getSetting("Password")

	if len(login) > 0:
		http = GET(httpSiteUrl, httpSiteUrl)
		if http == None: return False

		beautifulSoup = BeautifulSoup(http)
		userPanel = beautifulSoup.find('div', 'b-header__user-panel')

		if userPanel == None:
			os.remove(cookiepath)
			
			loginResponse = GET(httpSiteUrl + '/login.aspx', httpSiteUrl, {
				'login': login,
				'passwd': password,
				'remember': 1
			})

			loginSoup = BeautifulSoup(loginResponse)
			userPanel = loginSoup.find('div', 'b-header__user-panel')
			if userPanel == None:
				showMessage('Login', 'Check login and password', 3000)
			else:
				return True
		else:
			return True
	return False

def getUrlWithSortBy(url, section):
	sortBy = __settings__.getSetting("Sort by")
	sortByMap = {'0': 'new', '1': 'rating', '2': 'year'}
	if '?' in url:
		return url
	else:
		return url + '?view=list&sort=' + sortByMap[sortBy] + getFilters(section)
	
def getFilters(section):
	params = [];
	ret = ''
	sectionSettings = {
		'video': ['mood', 'vproduction', 'quality', 'translation'],
		'audio': ['genre', 'aproduction']
	}
	for settingId in sectionSettings[section]:
		setting = __settings__.getSetting(settingId)
		if setting != 'Any':
			params.append(setting)
	if len(params) > 0:
		ret = '&fl=' + ','.join(params)
	return ret

def main(params):
	li = xbmcgui.ListItem('[Видео]')
	uri = construct_request({
		'href': httpSiteUrl + '/video/',
		'mode': 'getCategories',
		'category': 'video',
		'filter': '',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('[Аудио]')
	uri = construct_request({
		'href': httpSiteUrl + '/audio/',
		'mode': 'getCategories',
		'category': 'audio',
		'filter': '',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	if check_login():
		li = xbmcgui.ListItem('В процессе')
		uri = construct_request({
			'mode': 'getFavoriteCategories',
			'type': 'inprocess'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

		li = xbmcgui.ListItem('Избранное')
		uri = construct_request({
			'mode': 'getFavoriteCategories',
			'type': 'favorites'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

		li = xbmcgui.ListItem('Рекомендуемое')
		uri = construct_request({
			'mode': 'getFavoriteCategories',
			'type': 'recommended'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

		li = xbmcgui.ListItem('На будущее')
		uri = construct_request({
			'mode': 'getFavoriteCategories',
			'type': 'forlater'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

		li = xbmcgui.ListItem('Я рекомендую')
		uri = construct_request({
			'mode': 'getFavoriteCategories',
			'type': 'irecommended'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

		li = xbmcgui.ListItem('Завершенное')
		uri = construct_request({
			'mode': 'getFavoriteCategories',
			'type': 'finished'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def getCategories(params):
	section = params['category']
	categoryUrl = urllib.unquote_plus(params['href'])

	http = GET(categoryUrl, httpSiteUrl)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	topMenu = beautifulSoup.find('ul', 'b-header-menu')

	if topMenu == None:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	categorySubmenu = topMenu.find('li', 'm-%s' % section)
	if categorySubmenu == None:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False

	subcategories = categorySubmenu.findAll('a')
	if len(subcategories) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	for subcategory in subcategories:
		li = xbmcgui.ListItem(subcategory.string)
		uri = construct_request({
			'href': getUrlWithSortBy(httpSiteUrl + subcategory['href'], section),
			'mode': 'readcategory',
			'cleanUrl': httpSiteUrl + subcategory['href'],
			'section': section,
			'filter': '',
			'firstPage': 'yes'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def getFavoriteCategories(params):
	http = GET(httpSiteUrl + '/myfavourites.aspx?page=' + params['type'], httpSiteUrl)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	favSectionsContainer = beautifulSoup.find('div', 'b-tabpanels')
	if favSectionsContainer == None:
		showMessage('ОШИБКА', 'В избранном пусто', 3000)
		return False

	favSections = favSectionsContainer.findAll('div', 'b-category')
	if len(favSections) == 0:
		showMessage('ОШИБКА', 'В избранном пусто', 3000)
		return False
	sectionRegexp = re.compile("\s*{\s*section:\s*'([^']+)")
	subsectionRegexp = re.compile("subsection:\s*'([^']+)")
	for favSection in favSections:
		rel = favSection.find('a', 'b-add')['rel'].encode('utf-8')
		section = sectionRegexp.findall(rel)[0]
		subsection = subsectionRegexp.findall(rel)[0]
		title = str(favSection.find('a', 'item').find('b').string)
		li = xbmcgui.ListItem(title)

		uri = construct_request({
			'mode': 'readfavorites',
			'section': section,
			'subsection': subsection,
			'type': params['type'],
			'page': 0
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)
	xbmcplugin.endOfDirectory(h)

def getPosterImage(src):
	return getImage(src, '1')

def getThumbnailImage(src):
	return getImage(src, '6')

def getImage(src, quality):
	src = src.split('/')
	src[-2] = quality
	return '/'.join(src)

def readfavorites(params):
	href = httpSiteUrl + "/myfavourites.aspx?ajax&section=" + params['section'] + "&subsection=" + params['subsection'] + "&rows=1&curpage=" + params['page'] + "&action=get_list&setrows=3&page=" + params['type']
	favoritesUrl = urllib.unquote_plus(href)

	http = GET(favoritesUrl, httpSiteUrl)
	if http == None: return False
	
	data = json.loads(str(http))
	http = data['content'].encode('utf-8')

	beautifulSoup = BeautifulSoup(http)
	itemsContainer = beautifulSoup.find('div', 'b-posters')
	if itemsContainer == None:
		showMessage('ОШИБКА', 'В избранном пусто', 3000)
		return False
	items = itemsContainer.findAll('a')
	if len(items) == 0:
		showMessage('ОШИБКА', 'В избранном пусто', 3000)
		return False
	else:
		coverRegexp = re.compile("url\s*\('([^']+)")
		for item in items:
			cover = coverRegexp.findall(str(item['style']))[0]
			title = str(item.find('span').string)
			href = httpSiteUrl + item['href']

			isMusic = "no"
			if re.search('audio', href):
				isMusic = "yes"

			li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = getThumbnailImage(cover), thumbnailImage = getPosterImage(cover))
			li.setProperty('IsPlayable', 'false')

			id = item['href'].split('/')[-1]
			li.addContextMenuItems([
				(
					__language__( 50003 ), "XBMC.RunPlugin(%s)" % construct_request({
						'mode': 'addto',
						'section': 'favorites',
						'id': id,
						'title': title
					})
				),
				(
					__language__( 50004 ), "XBMC.RunPlugin(%s)" % construct_request({
						'mode': 'addto',
						'section': 'playlist',
						'id': id,
						'title': title
					})
				)
			])

			uri = construct_request({
				'href': href,
				'referer': href,
				'mode': 'readdir',
				'cover': cover,
				'folder': 0,
				'isMusic': isMusic
			})
			xbmcplugin.addDirectoryItem(h, uri, li, True)

	if data['islast'] == False:
		li = xbmcgui.ListItem('[NEXT PAGE >]')
		li.setProperty('IsPlayable', 'false')
		params['page'] = int(params['page']) + 1
		uri = construct_request(params)
		xbmcplugin.addDirectoryItem(h, uri, li, True)
	xbmcplugin.endOfDirectory(h)

def readcategory(params):
	showUpdateInfo = __settings__.getSetting("Show update info") == "true"
	categoryUrl = getUrlWithSortBy(urllib.unquote_plus(params['href']), params['section'])
        delimiter = '?'
        if '?' in categoryUrl: 
                delimiter = '&'
        viewMode = 'list'
        if not showUpdateInfo:
               viewMode = 'detailed'
        categoryUrl = categoryUrl + delimiter + 'view=' + viewMode
        
	http = GET(categoryUrl, httpSiteUrl)
	if http == None: return False
	try:
		params['filter']
	except:
		params['filter'] = ''

	beautifulSoup = BeautifulSoup(http)
        if showUpdateInfo:        
        	items = beautifulSoup.findAll('div', 'b-poster-section')
        else:
                items = beautifulSoup.findAll('div', 'b-poster-section-detail')

	if len(items) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		if params['firstPage'] == 'yes':
			#Add search list item
			li = xbmcgui.ListItem("[ПОИСК]")
			li.setProperty('IsPlayable', 'false')
			uri = construct_request({
				'mode': 'runsearch',
				'section': params['section'],
				'url': urllib.unquote_plus(params['cleanUrl'])
			})
			xbmcplugin.addDirectoryItem(h, uri, li, True)
			
			#Genre
			groups = beautifulSoup.find('ul', 'm-group')
			if groups != None:
				yearLink = groups.find('a', href=re.compile(r'year'))
				if yearLink != None:
					li = xbmcgui.ListItem("[По годам]")
					li.setProperty('IsPlayable', 'false')
					uri = construct_request({
						'mode': 'getGenreList',
						'section': params['section'],
						'filter': params['filter'],
						'href': httpSiteUrl + yearLink['href'],
						'cleanUrl': urllib.unquote_plus(params['cleanUrl']),
						'css': 'main'
					})
					xbmcplugin.addDirectoryItem(h, uri, li, True)
				genreLink = groups.find('a', href=re.compile(r'genre'))
				if genreLink != None:
					li = xbmcgui.ListItem("[Жанры]")
					li.setProperty('IsPlayable', 'false')
					uri = construct_request({
						'mode': 'getGenreList',
						'section': params['section'],
						'filter': params['filter'],
						'href': httpSiteUrl + genreLink['href'],
						'cleanUrl': urllib.unquote_plus(params['cleanUrl']),
						'css': 'b-list-subcategories'
					})
					xbmcplugin.addDirectoryItem(h, uri, li, True)

		for item in items:
			title = None
			cover = None
			href = None

			img = item.find('img')
                        link = item.find('a', 'subject-link')
			if img != None:
				cover = img['src']
				title = img['alt']
				href = httpSiteUrl + link['href']

			if title != None:
                                plot = ''
				if showUpdateInfo:
					additionalInfo = ''
					numItem = item.find('b', 'num')
					if numItem != None:
						additionalInfo = " / " + numItem.string.strip() + " "
					dateInfo = item.find('b', 'date')
					if dateInfo != None:
						additionalInfo += dateInfo.string.strip()
					title += additionalInfo
                                else:
                                        plot = []
                                        details = item.find('div', 'text').contents
                                        for detail in details:
                                                try:
                                                        plot.append(detail.encode('utf-8'))
                                                except:
                                                        pass
                                        plot = htmlEntitiesDecode("\n".join(plot))
                                titleText = htmlEntitiesDecode(title)
				li = xbmcgui.ListItem(titleText, iconImage = getThumbnailImage(cover), thumbnailImage = getPosterImage(cover))
                                if plot != '':
                                        li.setInfo(type=params['section'], infoLabels={'title': titleText, 'plot': plot})
				li.setProperty('IsPlayable', 'false')

				id = str(link['href'].split('/')[-1])
				li.addContextMenuItems([
					(
						__language__( 50001 ), "XBMC.RunPlugin(%s)" % construct_request({
							'mode': 'addto',
							'section': 'favorites',
							'id': id
						})
					),
					(
						__language__( 50002 ), "XBMC.RunPlugin(%s)" % construct_request({
							'mode': 'addto',
							'section': 'playlist',
							'id': id
						})
					)
				])

				isMusic = 'no'
				if params['section'] == 'audio':
					isMusic = 'yes'

				uri = construct_request({
					'href': href,
					'referer': categoryUrl,
					'mode': 'readdir',
					'cover': cover,
					'folder': 0,
					'isMusic': isMusic
				})

				xbmcplugin.addDirectoryItem(h, uri, li, True)

	nextPageLink = beautifulSoup.find('a', 'next-link')
	if nextPageLink != None:
		li = xbmcgui.ListItem('[NEXT PAGE >]')
		li.setProperty('IsPlayable', 'false')
		uri = construct_request({
			'href': httpSiteUrl + nextPageLink['href'].encode('utf-8'),
			'mode': 'readcategory',
			'section': params['section'],
			'filter': params['filter'],
			'firstPage': 'no'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def getGenreList(params):
	http = GET(urllib.unquote_plus(params['href']), httpSiteUrl)
	if http == None: return False
	
	beautifulSoup = BeautifulSoup(http)
	items = beautifulSoup.find('div', params['css']).findAll('a')

	if len(items) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for item in items:
			li = xbmcgui.ListItem(item.string)
			li.setProperty('IsPlayable', 'false')
			uri = construct_request({
				'href': httpSiteUrl + item['href'].encode('utf-8'),
				'mode': 'readcategory',
				'section': params['section'],
				'filter': '',
				'cleanUrl': urllib.unquote_plus(params['cleanUrl']),
				'firstPage': 'yes'
			})
			xbmcplugin.addDirectoryItem(h, uri, li, True)
		xbmcplugin.endOfDirectory(h)
		

def readdir(params):
	folderUrl = urllib.unquote_plus(params['href'])
	cover = urllib.unquote_plus(params['cover'])
	folder = params['folder']

	http = GET(folderUrl + '?ajax&folder=' + folder, httpSiteUrl)
	if http is None: return False

	beautifulSoup = BeautifulSoup(http)
	mainItems = beautifulSoup.find('ul', 'filelist')
	if mainItems is None:
		showMessage('ОШИБКА', 'No filelist', 3000)
		return False

	items = mainItems.findAll('li')

	folderRegexp = re.compile('(\d+)')
	if len(items) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for item in items:
			isFolder = item['class'] == 'folder'
			linkItem = None
			playLink = None
			if isFolder:
				linkItem = item.find('a', 'title')
			else:
                                playLinkClass = 'b-file-new__link-material'
				linkItem = item.find('a', 'b-file-new__link-material-download')
				playLink = item.find('a', playLinkClass)
				if playLink is None:
                                        playLinkClass = 'b-file-new__material'
					playLink = item.find('div', playLinkClass)
			
			if linkItem is not None:
				title = ""
				if isFolder:
					titleB = linkItem.find('b')
					if titleB == None:
						title = str(linkItem.string)
					else:
						title = str(titleB.string)
					quality = item.findAll('span', 'material-size')
					if len(quality) > 1:
						 title = title + " [" + str(quality[0].string) + "]"
				else:
					try:
						title = str(playLink.find('span', playLinkClass + '-filename-text').string)
					except:
						pass

				useFlv = __settings__.getSetting('Use flv files for playback') == 'true'
				fallbackHref = linkItem['href']
				if useFlv and playLink is not None and playLink.name == 'a':
					try:
						href = httpSiteUrl + str(playLink['href'])
					except:
						href = fallbackHref
				else:
					href = fallbackHref
					try:
						folder = folderRegexp.findall(linkItem['rel'])[0]
					except:
						pass

				li = None
				uri = None
				
				if isFolder:
					li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = getThumbnailImage(cover), thumbnailImage = getPosterImage(cover))
					li.setProperty('IsPlayable', 'false')

					uri = construct_request({
						'cover': cover,
						'href': folderUrl,
						'referer': folderUrl,
						'mode': 'readdir',
						'folder': folder,
						'isMusic': params['isMusic']
					})
				else:
					li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = getThumbnailImage(cover), thumbnailImage = getPosterImage(cover), path = href)
					li.setProperty('IsPlayable', 'true')
					type = 'video'
					if params['isMusic'] == 'yes':
						type = 'music'
					li.setInfo(type = type, infoLabels={'title': title})
                                        if not useFlv:
					        li.addContextMenuItems([
						        (
							        __language__( 40001 ), "XBMC.RunPlugin(%s)" % construct_request({
								        'mode': 'download',
								        'file_url': str(href.encode('utf-8')),
								        'file_name': htmlEntitiesDecode(title)
							        })
						        )
					        ])

					if type == 'music' or (__settings__.getSetting('Autoplay next') == 'true' and not useFlv):
						uri = construct_request({
							'file': str(href.encode('utf-8')),
							'referer': folderUrl,
							'mode': 'play'
						})
					elif useFlv:
						uri = construct_request({
							'file': href,
							'referer': folderUrl,
							'mode': 'playflv',
							'fallbackHref': fallbackHref
						})
					else:
						uri = getFullUrl(href)

				xbmcplugin.addDirectoryItem(h, uri, li, isFolder)

	xbmcplugin.endOfDirectory(h)

def download(params):
        fileUrl = getFullUrl(urllib.unquote_plus(params['file_url']))
        fileName = fileUrl.split('/')[-1]
	download_params = {
		'url': fileUrl,
		'download_path': __settings__.getSetting('Download Path')
	}
	client = downloader.SimpleDownloader()        
	client.download(fileName, download_params)

def runsearch(params):
	skbd = xbmc.Keyboard()
	skbd.setHeading('Что ищем?')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		searchUrl = '%ssearch.aspx?search=%s' % (urllib.unquote_plus(params['url']), urllib.quote_plus(SearchStr))
		params = {
			'href': searchUrl,
			'section': params['section']
		}
		return render_search_results(params)


def render_search_results(params):
	searchUrl = urllib.unquote_plus(params['href'])
	http = GET(searchUrl, httpSiteUrl)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	items = beautifulSoup.find('div', 'l-content').find('table').findAll('tr')

	if len(items) == 0:
		showMessage('ОШИБКА', 'Ничего не найдено', 3000)
		return False
	else:
		for item in items:
			link = item.find('a')

			if link != None:
				title = str(link['title'].encode('utf-8'))
				href = httpSiteUrl + link['href']
				cover = item.find('img')['src']

				if title != None:
					li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = getThumbnailImage(cover), thumbnailImage = getPosterImage(cover))
					li.setProperty('IsPlayable', 'false')

					isMusic = 'no'
					if params['section'] == 'audio':
						isMusic = 'yes'

					uri = construct_request({
						'href': href,
						'referer': searchUrl,
						'mode': 'readdir',
						'cover': cover,
						'folder': 0,
						'isMusic': isMusic
					})

					xbmcplugin.addDirectoryItem(h, uri, li, True)

		nextPageLink = beautifulSoup.find('a', 'next-link')
		if nextPageLink != None:
			li = xbmcgui.ListItem('[NEXT PAGE >]')
			li.setProperty('IsPlayable', 'false')
			uri = construct_request({
				'href': httpSiteUrl + str(nextPageLink['href'].encode('utf-8')),
				'mode': 'render_search_results',
				'section': params['section']
			})
			xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def addto(params):
        idRegexp = re.compile("([^-]+)")
        itemId = idRegexp.findall(params['id'])[0]
	addToHref = httpSiteUrl + "/addto/" + params['section'] + '/' + itemId + "?json"
	GET(addToHref, httpSiteUrl)
	showMessage('Result', "Toggled state in " + params['section'], 5000)

def playflv(params):
	referer = urllib.unquote_plus(params['referer'])
	plfile = urllib.unquote_plus(params['file'])
	try:
		http = GET(plfile, referer)
		if http == None:
			raise Exception('HTTP Error', 'page loading error')

		fileRegexp = re.compile("playlist:\s*\[\s*\{\s*url:\s*'([^']+)", re.IGNORECASE + re.DOTALL + re.MULTILINE)
		playerLink = fileRegexp.findall(http)
		if playerLink == None or len(playerLink) == 0:
			raise Exception('Flv search', 'link not found')

		plfile = urllib.urlopen(getFullUrl(str(playerLink[0])))
		fileUrl = plfile.geturl()
	except:
		fileUrl = urllib.unquote_plus(params['fallbackHref'])

	i = xbmcgui.ListItem(path = getFullUrl(fileUrl))
	xbmcplugin.setResolvedUrl(h, True, i)

def play(params):
	referer = urllib.unquote_plus(params['referer'])
	plfile = urllib.unquote_plus(params['file'])
	headers['Referer'] = referer

	plfile = urllib.urlopen(getFullUrl(plfile))
	fileUrl = plfile.geturl()

	i = xbmcgui.ListItem(path = getFullUrl(fileUrl))
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

params = get_params(sys.argv[2])

mode   = None
func   = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	main(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)
