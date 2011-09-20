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

#---------- get serials types --------------------------------------------------
def Get_Serial_Type():
    # add search to the list
    name = '[ПОИСК]'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=SERIAL'
    u += '&name=%s'%urllib.quote_plus(name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    # add last viewed serial
    name = '[ИСТОРИЯ]'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=SERIAL'
    u += '&name=%s'%urllib.quote_plus(name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    # load serials types
    tree = ElementTree()
    tree.parse(os.path.join(os.getcwd(), r'resources', r'data', r'serials.xml'))

    for rec in tree.getroot().find('SERIALS'):
            name = rec.text.encode('utf-8')
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=SERIAL'
            u += '&name=%s'%urllib.quote_plus(name)
            xbmcplugin.addDirectoryItem(h, u, i, True)
    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

#---------- get serials for selected type --------------------------------------
def Get_Serial_List(params):
    s_type = urllib.unquote_plus(params['name'])
    if s_type == None: return False

    # show search dialog
    if s_type == '[ПОИСК]':
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск сериалов. Формат: name[:yyyy]')
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
            'Неверно задан формат поиска сериала.',
            'Используйте формат: ',
            '    <поиск по имени>[:<поиск по году YYYY>]')
            return False

    # load serials types
    tree = ElementTree()
    tree.parse(os.path.join(os.getcwd(), r'resources', r'data', r'serials.xml'))

    if s_type == '[ПОИСК]':
        for type in tree.getroot().find('SERIALS'):
            for rec in type:
                try:
                    #get serial details
                    i_name = rec.find('name').text
                    i_name = i_name.encode('utf-8')

                    if unicode(rec.find('year').text).isnumeric():
                        i_year      = int(rec.find('year').text)
                    else:
                        i_year      = 1900

                    # checkout by category or name/year
                    if s_name <> '':
                        if s_name not in i_name:
                            continue
                    if s_year <> '':
                        if int(s_year) <> i_year:
                            continue

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
    elif s_type == '[ИСТОРИЯ]':
        (info_serial_url, info_part_url, info_image, info_name) = Get_Last_Serial_Info()
        if info_serial_url == '-': return False

        # --
        url     = info_serial_url
        image   = info_image

        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()

        match=re.compile('<p>Смотреть .+ онлайн<span id(.+?)<p><strong>Сериал посмотрели?', re.MULTILINE|re.DOTALL).findall(link)
        if len(match) == 0:
            match=re.compile('<p>Смотреть .+ онлайн<(.+?)<p><strong>Сериал посмотрели?', re.MULTILINE|re.DOTALL).findall(link)
            if len(match) == 0:
                showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов id,name,link,numberOfMovies')
                return False

        list  =re.compile('<p>(.+?)</p>', re.MULTILINE|re.DOTALL).findall(match[0])

        season = ''
        for rec in list:
            if re.search('object', rec):
                v_url=re.compile('.txt&amp;pl=(.+?)&amp;link=', re.MULTILINE|re.DOTALL).findall(rec)
                v_list = Get_Serial_Video(v_url[0].replace('%26','&'))
                for v in v_list:
                    name = season+' '+v[0]#.decode('utf-8')
                    if v[1] == info_part_url:
                        name = '* '+name
                    else:
                        name = '  '+name
                    i = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)
                    u = sys.argv[0] + '?mode=PLAY'
                    u += '&name=%s'%urllib.quote_plus(name)
                    u += '&url=%s'%urllib.quote_plus(v[1])
                    u += '&serial=%s'%urllib.quote_plus(info_serial_url)
                    u += '&img=%s'%urllib.quote_plus(info_image)
                    i.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(h, u, i, False)
            else:
                season = rec#.decode('utf-8')
    else:
        for rec in tree.getroot().find('SERIALS').find('st_'+md5.md5(s_type).hexdigest()):
            try:
                #get serial details
                i_name      = rec.text.encode('utf-8')
                i_year      = int(rec.find('year').text)
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


#---------- get serial ---------------------------------------------------------
def Get_Serial(params):
    url = urllib.unquote_plus(params['url'])
    if url == None:
        return False

    image = urllib.unquote_plus(params['img'])

    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()

    match=re.compile('<p>Смотреть .+ онлайн<span id(.+?)<p><strong>Сериал посмотрели?', re.MULTILINE|re.DOTALL).findall(link)
    if len(match) == 0:
        match=re.compile('<p>Смотреть .+ онлайн<(.+?)<p><strong>Сериал посмотрели?', re.MULTILINE|re.DOTALL).findall(link)
        if len(match) == 0:
            showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов id,name,link,numberOfMovies')
            return False

    list  =re.compile('<p>(.+?)</p>', re.MULTILINE|re.DOTALL).findall(match[0])

    season = ''
    for rec in list:
        if re.search('object', rec):
            v_url=re.compile('.txt&amp;pl=(.+?)&amp;link=', re.MULTILINE|re.DOTALL).findall(rec)
            v_list = Get_Serial_Video(v_url[0].replace('%26','&'))
            for v in v_list:
                name = season+' '+v[0]#.decode('utf-8')
                i = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)
                u = sys.argv[0] + '?mode=PLAY'
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&url=%s'%urllib.quote_plus(v[1])
                u += '&serial=%s'%urllib.quote_plus(url)
                u += '&img=%s'%urllib.quote_plus(image)
                i.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(h, u, i, False)
        else:
            season = rec#.decode('utf-8')
    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

#---------- get serial video links ---------------------------------------------
def Get_Serial_Video(url):
    cj = cookielib.CookieJar()
    h  = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(h)
    urllib2.install_opener(opener)
    post = None

    xbmc.output('URL: %s' % urllib.unquote(url))

    request = urllib2.Request(urllib.unquote(url), post)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host', 'serialu.net')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer', 'http://serialu.net/media/uppod.swf')
    request.add_header('Cookie', 'MG_6532=1')

    o = urllib2.urlopen(request)
    http = o.read()
    o.close()
    video=re.compile('{"comment":"(.+?)","file":"(.+?)"}', re.MULTILINE|re.DOTALL).findall(http)

    return video
#-------------------------------------------------------------------------------

def PLAY(params):

	url = urllib.unquote_plus(params['url'])
        xbmc.output(url)
	i = xbmcgui.ListItem(path = urllib.unquote(url))
	#xbmcplugin.setResolvedUrl(h, True, i)
        xbmc.Player().play(url, i)

        img     = urllib.unquote_plus(params['img'])
        serial  = urllib.unquote_plus(params['serial'])
        name    = urllib.unquote_plus(params['name'])

        Save_Last_Serial_Info(serial, url, img, name)

#-------------------------------------------------------------------------------

def Save_Last_Serial_Info(serial, part, img, name):
    try:
        tree = ElementTree()
        tree.parse(os.path.join(path, r'history.xml'))
        xml1 = tree.getroot()
        xml1.find("Serial").text = serial
        xml1.find("Part").text   = part
        xml1.find("Image").text  = img
        xml1.find("Name").text   = name
    except:
        # create XML structure
        xml1 = Element("SERIALU_NET_HISTORY")
        SubElement(xml1, "Serial").text = serial
        SubElement(xml1, "Part").text   = part
        SubElement(xml1, "Image").text  = img
        SubElement(xml1, "Name").text   = name

    ElementTree(xml1).write(os.path.join(os.getcwd(), r'resources', r'data', r'history.xml'), encoding='utf-8')

def Get_Last_Serial_Info():
    try:
        tree = ElementTree()
        tree.parse(os.path.join(os.getcwd(), r'resources', r'data', r'history.xml'))
        xml1 = tree.getroot()
        serial = xml1.find("Serial").text
        part   = xml1.find("Part").text
        img    = xml1.find("Image").text
        name   = xml1.find("Name").text
    except:
        # create XML structure
        xml1 = Element("SERIALU_NET_HISTORY")
        SubElement(xml1, "Serial").text = '-'
        SubElement(xml1, "Part").text   = '-'
        SubElement(xml1, "Image").text  = '-'
        SubElement(xml1, "Name").text   = '-'
        ElementTree(xml1).write(os.path.join(os.getcwd(), r'resources', r'data', r'history.xml'), encoding='utf-8')
        #
        serial = '-'
        part   = '-'
        img    = '-'
        name   = '-'

    return serial, part, img, name

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
	Get_Serial_Type()

if mode == 'SERIAL':
	Get_Serial_List(params)
elif mode == 'LIST':
	Get_Serial(params)
elif mode == 'PLAY':
	PLAY(params)
