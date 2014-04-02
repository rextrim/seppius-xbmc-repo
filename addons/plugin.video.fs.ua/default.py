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

import sys
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcvfs

__settings__ = xbmcaddon.Addon(id='plugin.video.fs.ua')
__addondir__ = xbmc.translatePath(__settings__.getAddonInfo('profile'))
if not xbmcvfs.exists(__addondir__):
    xbmcvfs.mkdir(__addondir__)

# sys.path.append(os.path.join(__settings__.getAddonInfo('path'), 'resources', 'lib'))
icon = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'icon.png'))

import urllib
import urllib2
import re
import cookielib
import socket
import simplejson as json

import SimpleDownloader as downloader
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

socket.setdefaulttimeout(50)

__author__ = "Dmitry Khrysev"
__license__ = "GPL"
__maintainer__ = "Dmitry Khrysev"
__email__ = "x86demon@gmail.com"
__status__ = "Production"

__language__ = __settings__.getLocalizedString

siteUrl = 'brb.to'
httpSiteUrl = 'http://' + siteUrl
cookiepath = os.path.join(__addondir__, 'plugin.video.fs.ua.cookies.lwp')
if isinstance(cookiepath, unicode):
    cookiepath = cookiepath.encode('utf8')

h = int(sys.argv[1])

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))


def htmlEntitiesDecode(string):
    return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]


def show_message(heading, message, times=3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, icon))


headers = {
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
'Accept-Charset': 'utf-8, utf-16, *;q=0.1',
'Accept-Encoding': 'identity, *;q=0'
}


def get_full_url(url):
    if not '://' in url:
        url = httpSiteUrl + url
    return url


def GET(url, referer, post_params=None):
    headers['Referer'] = referer
    url = get_full_url(url)

    if post_params is not None:
        post_params = urllib.urlencode(post_params)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif headers.has_key('Content-Type'):
        del headers['Content-Type']

    jar = cookielib.LWPCookieJar(cookiepath)
    if xbmcvfs.exists(cookiepath):
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
    __settings__.setSetting("Login", "")
    __settings__.setSetting("Password", "")


def check_login():
    login = __settings__.getSetting("Login")
    password = __settings__.getSetting("Password")

    if len(login) > 0:
        http = GET(httpSiteUrl, httpSiteUrl)
        if http is None:
            return False

        beautifulSoup = BeautifulSoup(http)
        userPanel = beautifulSoup.find('a', 'b-header__user-profile')

        if userPanel is None:
            xbmcvfs.delete(cookiepath)

            loginResponse = GET(httpSiteUrl + '/login.aspx', httpSiteUrl, {
                'login': login,
                'passwd': password,
                'remember': 'on'
            })

            loginSoup = BeautifulSoup(loginResponse)
            userPanel = loginSoup.find('a', 'b-header__user-profile')
            if userPanel is None:
                show_message('Login', 'Check login and password', 3000)
            else:
                return True
        else:
            return True
    return False


def get_url_with_sort_by(url, section, start, view_mode):
    sortBy = __settings__.getSetting("Sort by")
    perPage = __settings__.getSetting("Items per page")
    sortByMap = {'0': 'new', '1': 'rating', '2': 'year'}

    separator = '?'
    if separator in url:
        separator = '&'

    request_params = {
        'view': view_mode,
        'sort': sortByMap[sortBy],
        'scrollload': 1,
        'start': start,
        'length': perPage
    }
    return url + get_filters(section) + separator + urllib.urlencode(request_params)


def get_filters(section):
    filter_params = []
    ret = ''
    sectionSettings = {
        'video': ['mood', 'vproduction', 'quality', 'translation'],
        'audio': ['genre', 'aproduction']
    }
    for settingId in sectionSettings[section]:
        setting = __settings__.getSetting(settingId)
        if setting != 'Any':
            filter_params.append(setting)
    if len(filter_params) > 0:
        ret = '/fl_%s/' % ('_'.join(filter_params))
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
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    categorySubmenu = beautifulSoup.find('div', 'b-subcategories')
    if categorySubmenu is None:
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False

    subcategories = categorySubmenu.findAll('a')
    if len(subcategories) == 0:
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False
    for subcategory in subcategories:
        li = xbmcgui.ListItem(subcategory.string)
        uri = construct_request({
            'href': httpSiteUrl + subcategory['href'],
            'mode': 'readcategory',
            'cleanUrl': httpSiteUrl + subcategory['href'],
            'section': section,
            'start': 0,
            'filter': ''
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

    xbmcplugin.endOfDirectory(h)


def getFavoriteCategories(params):
    http = GET(httpSiteUrl + '/myfavourites.aspx?page=' + params['type'], httpSiteUrl)
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    favSectionsContainer = beautifulSoup.find('div', 'b-tabpanels')
    if favSectionsContainer is None:
        show_message('ОШИБКА', 'В избранном пусто', 3000)
        return False

    favSections = favSectionsContainer.findAll('div', 'b-category')
    if len(favSections) == 0:
        show_message('ОШИБКА', 'В избранном пусто', 3000)
        return False
    sectionRegexp = re.compile("\s*\{\s*section:\s*'([^']+)")
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


def fix_string(string):
    if isinstance(string, unicode):
        return string.encode('utf8')
    return string

def readfavorites(params):
    href = httpSiteUrl + "/myfavourites.aspx?ajax&section=" + params['section'] \
           + "&subsection=" + params['subsection'] \
           + "&rows=1&curpage=" + params['page'] \
           + "&action=get_list&setrows=3&page=" + params['type']
    favoritesUrl = urllib.unquote_plus(href)

    http = GET(favoritesUrl, httpSiteUrl)
    if http is None:
        return False

    data = json.loads(str(http))
    http = data['content'].encode('utf-8')

    beautifulSoup = BeautifulSoup(http)
    itemsContainer = beautifulSoup.find('div', 'b-posters')
    if itemsContainer is None:
        show_message('ОШИБКА', 'В избранном пусто', 3000)
        return False
    items = itemsContainer.findAll('a')
    if len(items) == 0:
        show_message('ОШИБКА', 'В избранном пусто', 3000)
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

            li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = getThumbnailImage(cover),
                                  thumbnailImage = getPosterImage(cover))
            li.setProperty('IsPlayable', 'false')

            id = item['href'].split('/')[-1]
            li.addContextMenuItems([
                (
                __language__(50003), "XBMC.RunPlugin(%s)" % construct_request({
                        'mode': 'addto',
                        'section': 'favorites',
                        'id': id,
                        'title': title
                    })
                ),
                (
                __language__(50004), "XBMC.RunPlugin(%s)" % construct_request({
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

    if data['islast'] is False:
        li = xbmcgui.ListItem('[NEXT PAGE >]')
        li.setProperty('IsPlayable', 'false')
        params['page'] = int(params['page']) + 1
        uri = construct_request(params)
        xbmcplugin.addDirectoryItem(h, uri, li, True)
    xbmcplugin.endOfDirectory(h)


def readcategory(params):
    start = int(params['start'])
    showUpdateInfo = __settings__.getSetting("Show update info") == "true"
    category_href = urllib.unquote_plus(params['href'])

    viewMode = 'list'
    if not showUpdateInfo:
        viewMode = 'detailed'

    categoryUrl = get_url_with_sort_by(
        category_href,
        params['section'],
        params['start'],
        viewMode
    )

    data = GET(categoryUrl, httpSiteUrl)
    if data is None:
        return False
    data = json.loads(data)
    if data is None:
        return False
    http = data['content']

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
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False
    else:
        if start == 0 and 'hideFirstPageData' not in params:
            load_first_page_sections(category_href, params)

        for item in items:
            title = None
            cover = None
            href = None

            img = item.find('img')
            link = item.find('a', 'subject-link')
            if img is not None:
                cover = img['src']
                title = img['alt']
                href = httpSiteUrl + link['href']

            if title is not None:
                plot = ''
                if showUpdateInfo:
                    additionalInfo = ''
                    numItem = item.find('b', 'num')
                    if numItem is not None:
                        additionalInfo = " / " + numItem.string.strip() + " "
                    dateInfo = item.find('b', 'date')
                    if dateInfo is not None:
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
                li = xbmcgui.ListItem(titleText, iconImage=getThumbnailImage(cover),
                                      thumbnailImage=getPosterImage(cover))
                if plot != '':
                    li.setInfo(type=params['section'], infoLabels={'title': titleText, 'plot': plot})
                li.setProperty('IsPlayable', 'false')

                id = str(link['href'].split('/')[-1])
                li.addContextMenuItems([
                    (
                    __language__(50001), "XBMC.RunPlugin(%s)" % construct_request({
                            'mode': 'addto',
                            'section': 'favorites',
                            'id': id
                        })
                    ),
                    (
                    __language__(50002), "XBMC.RunPlugin(%s)" % construct_request({
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

    perPage = int(__settings__.getSetting("Items per page"))
    li = xbmcgui.ListItem('[NEXT PAGE >]')
    li.setProperty('IsPlayable', 'false')
    uri = construct_request({
        'href': category_href,
        'mode': 'readcategory',
        'section': params['section'],
        'filter': params['filter'],
        'start': start + perPage,
        'firstPage': 'no'
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    xbmcplugin.endOfDirectory(h)


def load_first_page_sections(href, params):
    #Add search list item
    li = xbmcgui.ListItem("[ПОИСК]")
    li.setProperty('IsPlayable', 'false')
    uri = construct_request({
        'mode': 'runsearch',
        'section': params['section'],
        'url': urllib.unquote_plus(params['cleanUrl'])
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    first_page_data = GET(href, httpSiteUrl)
    if first_page_data is None:
        return False

    beautifulSoup = BeautifulSoup(first_page_data)
    if beautifulSoup is None:
        return False

    groups = beautifulSoup.find('ul', 'm-group')
    if groups is not None:
        yearLink = groups.find('a', href=re.compile(r'year'))
        if yearLink is not None:
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
        if genreLink is not None:
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

def getGenreList(params):
    http = GET(urllib.unquote_plus(params['href']), httpSiteUrl)
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    items = beautifulSoup.find('div', params['css']).findAll('a')

    if len(items) == 0:
        show_message('ОШИБКА', 'Неверная страница', 3000)
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
                'start': 0,
                'hideFirstPageData': 1
            })
            xbmcplugin.addDirectoryItem(h, uri, li, True)
        xbmcplugin.endOfDirectory(h)


def read_materials(params):
    folder_url = urllib.unquote_plus(params['href'])

    material_id_regexp = re.compile('\/(\w+)-')
    material_id = material_id_regexp.findall(folder_url)[0]

    materials_cache_file = os.path.join(__addondir__, 'materials_files_cache-%s.json' % material_id)
    material_files = []
    if xbmcvfs.exists(materials_cache_file):
        if params['folder'] != "0":
            fp = open(materials_cache_file, 'r')
            material_files = json.load(fp)
            fp.close()
    if len(material_files) == 0:
        item_data = get_material_ids(material_id, params)
        item_request_params = urllib.urlencode({
            'f': 'files_list',
            'item_id': item_data['id'],
            'id': 'false',
            'u': item_data['uid']
        })
        material_files_url = '%s/jsfilemanager.aspx?%s' % (httpSiteUrl, item_request_params)
        material_files_data = GET(material_files_url, folder_url)
        if material_files_data is None:
            read_directory_unuthorized(params)
        material_files = json.loads(material_files_data)

        fp = open(materials_cache_file, 'w')
        json.dump(material_files, fp)
        fp.close()

    read_material_files(material_files, params)


def read_material_files(files, params):
    cover = urllib.unquote_plus(params['cover'])
    href = urllib.unquote_plus(params['href'])
    for item in files:
        if (item['fid']) == params['folder']:
            if item['type'] == 'folder':
                title = htmlEntitiesDecode(item['name'].encode('utf8'))
                if 'meta1' in item and item['meta1'] is not None:
                    title += ' - ' + htmlEntitiesDecode(item['meta1'].encode('utf8'))
                if 'meta2' in item and item['meta2'] is not None:
                    title += ' ' + htmlEntitiesDecode(item['meta2'].encode('utf8'))
                li = xbmcgui.ListItem(
                    title,
                    iconImage=getThumbnailImage(cover),
                    thumbnailImage=getPosterImage(cover)
                )
                li.setProperty('IsPlayable', 'false')

                uri = construct_request({
                    'href': href,
                    'referer': httpSiteUrl,
                    'mode': 'read_materials',
                    'cover': cover,
                    'folder': item['id'],
                    'isMusic': params['isMusic']
                })

                xbmcplugin.addDirectoryItem(h, uri, li, True)
            else:
                item_type = 'video'
                if params['isMusic'] == 'yes':
                    item_type = 'music'
                add_folder_file({
                    'title': item['name'],
                    'cover': cover,
                    'href': item['link'],
                    'referer': httpSiteUrl,
                    'type': item_type,
                    'fallbackHref': item['link']
                })

    xbmcplugin.endOfDirectory(h)

def get_material_ids(material_id, params):
    materials_cache_file = os.path.join(__addondir__, 'materials_cache.json')
    if xbmcvfs.exists(materials_cache_file):
        fp = open(materials_cache_file, 'r')
        materials_cache = json.load(fp)
        fp.close()
    else:
        materials_cache = {}

    if material_id not in materials_cache:
        material_edit_url = httpSiteUrl + '/materials/edit/' + material_id + '?win=files'

        http = GET(material_edit_url, httpSiteUrl)
        if http is None:
            read_directory_unuthorized(params)

        item_id_regexp = re.compile('ITEM_ID = "(\w+)"')
        user_id_regexp = re.compile('ITEM_UID = "(\w+)"')

        item_id = item_id_regexp.findall(http)[0]
        item_uid = user_id_regexp.findall(http)[0]

        item_data = {
            'id': item_id,
            'uid': item_uid
        }
        materials_cache[material_id] = item_data
        fp = open(materials_cache_file, 'w')
        json.dump(materials_cache, fp)
        fp.close()

    return materials_cache[material_id]


def readdir(params):
    if is_hidden_allowed():
        try:
            read_materials(params)
        except:
            read_directory_unuthorized(params)
    else:
        read_directory_unuthorized(params)


def is_hidden_allowed():
    show_hidden = __settings__.getSetting('Show hidden materials') == 'true'
    return show_hidden and check_login()


def read_directory_unuthorized(params):
    folderUrl = urllib.unquote_plus(params['href'])
    cover = urllib.unquote_plus(params['cover'])
    folder = params['folder']

    http = GET(folderUrl + '?ajax&folder=' + folder, httpSiteUrl)
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    if params['folder'] == '0':
        has_blocked = beautifulSoup.find('div', attrs={'id': 'file-block-text'})
        if has_blocked is not None:
            if check_login():
                li = xbmcgui.ListItem(
                    '[Показать скрытое]',
                    iconImage=getThumbnailImage(cover),
                    thumbnailImage=getPosterImage(cover)
                )
                li.setProperty('IsPlayable', 'false')
                uri = construct_request({
                    'href': folderUrl,
                    'referer': httpSiteUrl,
                    'mode': 'read_materials',
                    'cover': cover,
                    'folder': "0",
                    'isMusic': params['isMusic']
                })

                xbmcplugin.addDirectoryItem(h, uri, li, True)
            else:
                show_message('Blocked content', 'Некоторые файлы заблокированы')

    mainItems = beautifulSoup.find('ul', 'filelist')

    if mainItems is None:
        show_message('ОШИБКА', 'No filelist', 3000)
        return False

    items = mainItems.findAll('li')

    folderRegexp = re.compile('(\d+)')
    if len(items) == 0:
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False
    else:
        langRegexp = re.compile('\s*m\-(\w+)\s*')
        for item in items:
            isFolder = item['class'] == 'folder'
            playLink = None
            lang = None
            if isFolder:
                linkItem = item.find('a', 'title')
                lang_data = langRegexp.findall(linkItem['class'])
                if len(lang_data) > 0:
                    lang = str(lang_data[0])
                playLinkClass = ''
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
                    if titleB is None:
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
                if lang is not None:
                    title = lang.upper() + ' - ' + title

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

                if isFolder:
                    li = xbmcgui.ListItem(
                        htmlEntitiesDecode(title),
                        iconImage=getThumbnailImage(cover),
                        thumbnailImage=getPosterImage(cover)
                    )
                    li.setProperty('IsPlayable', 'false')

                    uri = construct_request({
                        'cover': cover,
                        'href': folderUrl,
                        'referer': folderUrl,
                        'mode': 'read_directory_unuthorized',
                        'folder': folder,
                        'isMusic': params['isMusic']
                    })
                    xbmcplugin.addDirectoryItem(h, uri, li, isFolder)
                else:
                    item_type = 'video'
                    if params['isMusic'] == 'yes':
                        item_type = 'music'

                    add_folder_file({
                        'title': title,
                        'cover': cover,
                        'href': href,
                        'referer': folderUrl,
                        'type': item_type,
                        'fallbackHref': fallbackHref
                    })

    xbmcplugin.endOfDirectory(h)


def add_folder_file(item):
    title = item['title']
    cover = item['cover']
    href = item['href']
    referer = item['referer']
    item_type = item['type']
    fallbackHref = item['fallbackHref']
    useFlv = __settings__.getSetting('Use flv files for playback') == 'true'

    li = xbmcgui.ListItem(
        htmlEntitiesDecode(title),
        iconImage=getThumbnailImage(cover),
        thumbnailImage=getPosterImage(cover),
        path=href
    )
    li.setProperty('IsPlayable', 'true')

    li.setInfo(type=item_type, infoLabels={'title': title})
    if not useFlv:
        li.addContextMenuItems([
            (
            __language__(40001), "XBMC.RunPlugin(%s)" % construct_request({
                'mode': 'download',
                'file_url': str(href.encode('utf-8')),
                'file_name': htmlEntitiesDecode(title)
            })
            )
        ])

    if item_type == 'music' or (__settings__.getSetting('Autoplay next') == 'true' and not useFlv):
        uri = construct_request({
            'file': str(href.encode('utf-8')),
            'referer': referer,
            'mode': 'play'
        })
    elif useFlv:
        uri = construct_request({
            'file': href,
            'referer': referer,
            'mode': 'playflv',
            'fallbackHref': fallbackHref
        })
    else:
        uri = get_full_url(href)

    xbmcplugin.addDirectoryItem(h, uri, li, False)


def download(params):
    fileUrl = get_full_url(urllib.unquote_plus(params['file_url']))
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
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    items = beautifulSoup.find('div', 'l-content').find('table').findAll('tr')

    if len(items) == 0:
        show_message('ОШИБКА', 'Ничего не найдено', 3000)
        return False
    else:
        for item in items:
            link = item.find('a')

            if link is not None:
                title = str(link['title'].encode('utf-8'))
                href = httpSiteUrl + link['href']
                cover = item.find('img')['src']

                if title is not None:
                    li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage=getThumbnailImage(cover),
                                          thumbnailImage=getPosterImage(cover))
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
        if nextPageLink is not None:
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
    show_message('Result', "Toggled state in " + params['section'], 5000)


def playflv(params):
    referer = urllib.unquote_plus(params['referer'])
    plfile = urllib.unquote_plus(params['file'])
    try:
        http = GET(plfile, referer)
        if http is None:
            raise Exception('HTTP Error', 'page loading error')

        fileRegexp = re.compile("playlist:\s*\[\s*\{\s*url:\s*'([^']+)", re.IGNORECASE + re.DOTALL + re.MULTILINE)
        playerLink = fileRegexp.findall(http)
        if playerLink is None or len(playerLink) == 0:
            raise Exception('Flv search', 'link not found')

        plfile = urllib.urlopen(get_full_url(str(playerLink[0])))
        fileUrl = plfile.geturl()
    except:
        fileUrl = urllib.unquote_plus(params['fallbackHref'])

    i = xbmcgui.ListItem(path=get_full_url(fileUrl))
    xbmcplugin.setResolvedUrl(h, True, i)


def play(params):
    referer = urllib.unquote_plus(params['referer'])
    plfile = urllib.unquote_plus(params['file'])
    headers['Referer'] = referer

    plfile = urllib.urlopen(get_full_url(plfile))
    fileUrl = plfile.geturl()

    i = xbmcgui.ListItem(path=get_full_url(fileUrl))
    xbmcplugin.setResolvedUrl(h, True, i)


def get_params(paramstring):
    param = []
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


params = get_params(sys.argv[2])

mode = None
func = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    main(params)

if mode is not None:
    try:
        func = globals()[mode]
    except:
        pass
    if func:
        func(params)
