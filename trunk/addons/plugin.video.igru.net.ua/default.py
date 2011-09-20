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
import re, os, urllib, urllib2, cookielib, md5
import xbmc, xbmcgui, xbmcplugin

# load XML library
sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
from ElementTree  import Element, SubElement, ElementTree

h = int(sys.argv[1])
icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- get movie types --------------------------------------------------
def Get_Movie_Type():
    # load movie types
    tree = ElementTree()
    tree.parse(os.path.join(os.getcwd(), r'resources', r'data', r'movies.xml'))

    # add search to the list
    name = '[ПОИСК]'
    tag = '*'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=TYPE'
    u += '&name=%s'%urllib.quote_plus(name)
    u += '&tag=%s'%urllib.quote_plus(tag)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    # add movie type to the list
    for rec in tree.getroot().find('TYPES'):
            name = rec.find('name').text.encode('utf-8')
            tag  = rec.tag.encode('utf-8')
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=TYPE'
            u += '&name=%s'%urllib.quote_plus(name)
            u += '&tag=%s'%urllib.quote_plus(tag)
            xbmcplugin.addDirectoryItem(h, u, i, True)
    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

#---------- get movies for selected type --------------------------------------
def Get_Movie_List(params):
    s_type = urllib.unquote_plus(params['tag'])
    if s_type == None: return False

    # show search dialog
    if s_type == '*':
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск фильмов. Формат: name[:yyyy]')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            s_name = SearchStr[0]
            if len(SearchStr) > 1:
                s_year = SearchStr[1]
            else:
                s_year = ''
        else:
            return False
        #--
        if not unicode(s_year).isnumeric() and (s_name == '' or s_year <> ''):
            xbmcgui.Dialog().ok('Ошибка поиска',
            'Неверно задан формат поиска фильма.',
            'Используйте формат: ',
            '    <поиск по имени>[:<поиск по году YYYY>]')
            return False
    # load movies
    tree = ElementTree()
    tree.parse(os.path.join(os.getcwd(), r'resources', r'data', r'movies.xml'))
    for rec in tree.getroot().find('MOVIES'):
        try:
            i_name = rec.find('name').text
            i_name = i_name.encode('utf-8')

            if unicode(rec.find('year').text).isnumeric():
                i_year      = int(rec.find('year').text)
            else:
                i_year      = 1900
            # checkout by category or name/year
            if s_type == '*':
                if s_name <> '':
                    if s_name not in i_name:
                        continue
                if s_year <> '':
                    if int(s_year) <> i_year:
                        continue
            else:
                if rec.find('categories').find(s_type) is None:
                    continue

            #get serial details
            i_image     = rec.find('img').text.encode('utf-8')
            i_url       = rec.find('url').text.encode('utf-8')
            i_director  = rec.find('director').text
            i_text      = rec.find('text').text
            i_genre     = rec.find('genre').text
            # set serial to XBMC
            i = xbmcgui.ListItem(i_name, iconImage=i_image, thumbnailImage=i_image)
            u = sys.argv[0] + '?mode=LIST'
            u += '&name=%s'%urllib.quote_plus(i_name)
            u += '&url=%s'%urllib.quote_plus(i_url)
            u += '&img=%s'%urllib.quote_plus(i_image)
            i.setInfo(type='video', infoLabels={ 'title':       i_name,
        						'year':        i_year,
        						'director':    i_director,
        						'plot':        i_text,
        						'genre':       i_genre})
            i.setProperty('fanart_image', i_image)
            xbmcplugin.addDirectoryItem(h, u, i, True)
        except:
            xbmc.log('***   ERROR '+rec.text.encode('utf-8'))

    xbmcplugin.endOfDirectory(h)


#---------- get movie ---------------------------------------------------------
def Get_Movie(params):
    url = urllib.unquote_plus(params['url'])

    if url == None:
        return False

    image = urllib.unquote_plus(params['img'])
    name  = urllib.unquote_plus(params['name'])

    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()

    match=re.compile('<object type="application/x-shockwave-flash"(.+?)</object>', re.MULTILINE|re.DOTALL).findall(link)
    if len(match) == 0:
        showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов id,name,link,numberOfMovies')
        return False

    part = 1

    for rec in match:
        v_url=re.compile('.txt&amp;file=(.+?)&amp;link=', re.MULTILINE|re.DOTALL).findall(rec)
        i_name = name
        if len(match) > 1:
            i_name = i_name + ' (часть '+str(part)+')'
            part = part+1
        #---
        i = xbmcgui.ListItem(i_name, iconImage=image, thumbnailImage=image)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(i_name)
        u += '&url=%s'%urllib.quote_plus(v_url[0])
        i.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

def PLAY(params):
	url = urllib.unquote_plus(params['url'])
        xbmc.output(url)
	i = xbmcgui.ListItem(path = urllib.unquote(url))
	#xbmcplugin.setResolvedUrl(h, True, i)
        xbmc.Player().play(url, i)

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

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Get_Movie_Type()

if mode == 'TYPE':
	Get_Movie_List(params)
elif mode == 'LIST':
	Get_Movie(params)
elif mode == 'PLAY':
	PLAY(params)

