#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 Silen
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
import re, os, urllib, urllib2, cookielib, time
from time import gmtime, strftime
import urlparse

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.my-hit.ru')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    page    = '1'
    genre   = ''
    genre_name = ''
    letter  = ''
    letter_name = ''
    year    = ''
    search  = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    year        = ''
    genre       = ''
    country     = ''
    director    = ''
    text        = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = ''

    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = ''
    #-- letter
    try:    p.letter = urllib.unquote_plus(params['letter'])
    except: p.letter = ''
    try:    p.letter_name = urllib.unquote_plus(params['letter_name'])
    except: p.letter_name = ''
    #-- year
    try:    p.year = urllib.unquote_plus(params['year'])
    except: p.year = ''
    #--search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-----
    return p

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None):
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           xbmc.log('We failed to reach a server.')
        elif hasattr(e, 'code'):
           xbmc.log('The server couldn\'t fulfill the request.')

    html = f.read()

    return html

#---------- get MY-HIT.RU URL --------------------------------------------------
def Get_URL(par):
    # http://my-hit.ru/index.php?module=search&func=view&result_orderby=score&result_order_asc=0&search_string=%EA%E8%ED&x=0&y=0

    url = 'http://my-hit.ru/index.php?module=video&func=film_list&fsave=1&fsort=film_displayname&fask=1&search_string=%EA%E8%ED'

    #-- year
    if par.year <> '':
        url += '&fyear='+par.year
    #-- genre
    if par.genre <> '':
        url += '&genre_id='+par.genre
    #-- letter
    if par.letter <> '':
        url += '&letter_id='+par.letter
    #-- page
    url += '&page='+par.page

    return url

#----------- get Header string ---------------------------------------------------
def Get_Header(par, mcount, pcount):

    info  = 'Фильмов: ' + '[COLOR FF00FF00]' + str(mcount) + '[/COLOR]'

    if pcount > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(pcount) +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre_name + '[/COLOR]'

    if par.year <> '':
        info += ' | Год: ' + '[COLOR FFFFF000]'+ par.year + '[/COLOR]'

    if par.letter <> '':
        info += ' | Название: ' + '[COLOR FFFF00FF]'+ par.letter_name + '[/COLOR]'

    if par.search <> '':
        info += ' | Поиск: ' + '[COLOR FFFF9933]'+ par.search + '[/COLOR]'

    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(par.genre)
    u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
    u += '&letter=%s'%urllib.quote_plus(par.letter)
    u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
    u += '&year=%s'%urllib.quote_plus(par.year)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search
    if par.genre == '' and par.letter == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFF9933][Поиск][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=SEARCH'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&letter=%s'%urllib.quote_plus(par.letter)
        u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- genres
    if par.genre == '' and par.letter == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FF00FFF0][Жанры][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRES'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&letter=%s'%urllib.quote_plus(par.letter)
        u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- alphabet
    if par.letter == '' and par.genre == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFF00FF][Алфавит][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=ALPHABET'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&letter=%s'%urllib.quote_plus(par.letter)
        u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- year
    if par.year == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFFF000][Год][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=YEAR'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&letter=%s'%urllib.quote_plus(par.letter)
        u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
        #-- get filter parameters
        par = Get_Parameters(params)

        #== get movie list =====================================================
        url = Get_URL(par)
        html = get_HTML(url)

        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        is_page_found = 0
        pcount = 1
        is_movie_count = 0
        mcount = 0

        nav = soup.find("table", { "class" : "outer" })
        for mov in nav.findAll('tr'):
            if is_page_found == 0:
                if mov.find('b'):
                    #-- number of pages
                    pnumb = re.compile(u'Страницы: \((.+?)\/(.+?)\)', re.MULTILINE|re.DOTALL).findall(mov.find('b').text)
                    try:
                        pcount = int(pnumb[0][1])
                        is_page_found = 1
                    except: pass
            #-- number of movies
            if is_movie_count == 0:
                for mc in mov.findAll('td'):
                    mnumb = re.compile(u'Фильмов: (.+?)\(', re.MULTILINE|re.DOTALL).findall(mc.text)
                    try:
                        mcount = int(mnumb[0])
                        is_movie_count = 1
                    except: pass

            #-- add header info
            if is_movie_count == 1:
                Get_Header(par, mcount, pcount)
                is_movie_count = 2

            #-- get movie info
            if not mov.find('img'): continue #-- if not movie go forward
            #-- image
            mi.img = 'http://my-hit.ru' + mov.find('img')['src']
            #-- check if onlain view is available
            mi.url = '*'
            for lnk in mov.findAll('a'):
                if lnk.text == u'Фильм онлайн &raquo;':
                    mi.url = 'http://my-hit.ru' + lnk['href']
            #-- title
            title = mov.findNext('tr')
            mi.title = unescape(title.find('a').text).encode('utf-8')

            info = title.findNext('tr').find('ul', {"class" : "line_none"})
            for inf in info.findAll('li'):
                if not inf.find('b'): continue
                #-- year
                if inf.find('b').text == u'Год:':
                    mi.year = inf.find('a').text
                #-- genres
                genre = ''
                if inf.find('b').text == u'Жанр:':
                    for g in inf.findAll('a'):
                        if len(genre) > 0: genre += ','
                        genre += g.text
                    mi.genre = unescape(genre).encode('utf-8')
                #-- country
                if inf.find('b').text == u'Страна:':
                    mi.country = unescape(inf.find('a').text).encode('utf-8')
                #-- director
                if inf.find('b').text == u'Режиссер:':
                    mi.director = unescape(inf.find('a').text).encode('utf-8')
                #-- description
                if inf.find('b').text == u'Краткое описание:':
                    mi.text = unescape(inf.find('p').text).encode('utf-8')

            #-- add movie to the list ------------------------------------------
            if mi.url == '*':
                name = '[COLOR FFFF0000]'+mi.title+'[/COLOR]'
            else:
                name = '[COLOR FFC3FDB8]'+mi.title+'[/COLOR]'

            i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            i.setInfo(type='video', infoLabels={ 'title':      mi.title,
                        						'year':        mi.year,
                        						'director':    mi.director,
                        						'plot':        mi.text,
                        						'country':     mi.country,
                        						'genre':       mi.genre})
            i.setProperty('fanart_image', mi.img)
            xbmcplugin.addDirectoryItem(h, u, i, False)

        #-- next page link
        if int(par.page) < pcount :
            name    = '[NEXT PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&letter=%s'%urllib.quote_plus(par.letter)
            u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
            u += '&year=%s'%urllib.quote_plus(par.year)
            xbmcplugin.addDirectoryItem(h, u, i, True)

        xbmcplugin.endOfDirectory(h)

#---------- search movie list --------------------------------------------------
def Search_List(params):
        list = []
        #-- get filter parameters
        par = Get_Parameters(params)

        # show search dialog
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск фильмов.')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            par.search = SearchStr[0]
        else:
            return False

        #== get movie list =====================================================
        url = 'http://my-hit.ru/index.php?module=search&func=view&result_orderby=score&result_order_asc=0&result_perpage=1000&search_string=%EA%E8%ED&x=0&y=0'
        html = get_HTML(url)

        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        pcount = 1
        mcount = 0

        # -- get list of found movies
        flag = 0
        for rec in soup.findAll("tr"):
            try:
                if rec.find('a').text.find(u'(фильм)')<>-1:
                    m_name = rec.find('a').text.replace(u'(фильм)', '').encode('utf-8')
                    flag = 1
                elif flag==1:
                    m_url  = rec.find('a')['href']
                    m_url = 'http://my-hit.ru/film/'+m_url.split('&id=')[1]+'/online'

                    m_img  = 'http://my-hit.ru'+rec.find('img')['src']
                    m_text = unescape(rec.text).encode('utf-8')
                    flag = 0
                    list.append({'name':m_name, 'url':m_url, 'img':m_img, 'text':m_text})
            except:
                pass
        mcount = len(list)

        if mcount == 0:
            return False

        #-- add header info
        Get_Header(par, mcount, pcount)

        for mov in list:
            #-- add movie to the list ------------------------------------------
            name = '[COLOR FFC3FDB8]'+mov['name']+'[/COLOR]'

            i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(mov['name'])
            u += '&url=%s'%urllib.quote_plus(mov['url'])
            u += '&img=%s'%urllib.quote_plus(mov['img'])
            i.setInfo(type='video', infoLabels={ 'title':      mov['name'],
                        						'plot':        mov['text']})
            i.setProperty('fanart_image', mov['img'])
            xbmcplugin.addDirectoryItem(h, u, i, False)

        xbmcplugin.endOfDirectory(h)

#---------- get genge list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://my-hit.ru/index.php?module=video&func=film_list&fsave=1&fsort=film_displayname&fask=0'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    nav = soup.find("table", { "id" : "_genres_" }).find("table")
    for genre in nav.findAll('td'):
        genre_id = genre.find('a')['href'].replace('/films/genre/', '')
        name     = unescape(genre.text).encode('utf-8')
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(genre_id)
        u += '&genre_name=%s'%urllib.quote_plus(name)
        u += '&letter=%s'%urllib.quote_plus(par.letter)
        u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#---------- get year list -----------------------------------------------------
def Year_List(params):
    list = []
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://my-hit.ru/index.php?module=video&func=film_list&fsave=1&fsort=film_displayname&fask=0'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    nav = soup.find("table", { "id" : "_years_" }).find("table")
    for year in nav.findAll('td'):
        try: list.append(int(year.text))
        except: continue

    for year in sorted(list, reverse=True):
        name     = str(year).encode('utf-8')
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&letter=%s'%urllib.quote_plus(par.letter)
        u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
        u += '&year=%s'%urllib.quote_plus(name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get year list -----------------------------------------------------
def Alphabet_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://my-hit.ru/index.php?module=video&func=film_list&fsave=1&fsort=film_displayname&fask=0'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    nav = soup.find("table", { "id" : "_alpha_" })
    for alpha in nav.findAll('a'):
        letter      = alpha.text
        letter_id   = alpha['href'].replace('/films/letter/', '')

        name     = unescape(letter).encode('utf-8')
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&letter=%s'%urllib.quote_plus(letter_id)
        u += '&letter_name=%s'%urllib.quote_plus(name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    if url == '*':
        return False

    # -- check if video available
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    nav = soup.find("embed")
    p_refer = nav['src']
    p_params = dict([part.split('=') for part in  nav['flashvars'].split('&')])
    p_host = urlparse.urlparse(p_params['file']).hostname

    # -- assemble RTMP link ----------------------------------------------------
    video = '%s?start=0&id=%s' % (p_params['file'], p_params['id'])

    i = xbmcgui.ListItem(name, path = urllib.unquote(video), thumbnailImage=img)
    xbmc.Player().play(video, i)

#-------------------------------------------------------------------------------

def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

def get_url(url):
    return "http:"+urllib.quote(url.replace('http:', ''))

#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.FileCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Movie_List(params)

if mode == 'MOVIE':
	Movie_List(params)
if mode == 'SEARCH':
	Search_List(params)
elif mode == 'GENRES':
    Genre_List(params)
elif mode == 'YEAR':
    Year_List(params)
elif mode == 'ALPHABET':
	Alphabet_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


