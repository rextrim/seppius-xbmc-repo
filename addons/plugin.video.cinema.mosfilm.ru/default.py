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
import re, os, urllib, urllib2, cookielib
try:
    from hashlib import md5 as md5
except:
    import md5
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.cinema.mosfilm.ru')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

h = int(sys.argv[1])
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))

fcookies = os.path.join(Addon.getAddonInfo('path'), 'cookies.txt')
print fcookies

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10

class msgDialog(xbmcgui.Window):
  def __init__(self):
    #self.setCoordinateResolution(1) # 0 for 1080
    self.addControl(xbmcgui.ControlImage(60,189,600,102, os.path.join(Addon.getAddonInfo('path'), r'resources', r'image', r'background.png')))
    self.strActionInfo = xbmcgui.ControlLabel(170, 210, 500, 50, '', 'font14', '0xFFFF00FF')
    self.addControl(self.strActionInfo)
    self.strActionInfo.setLabel('***')

  def Set_Message(self, str):
    self.strActionInfo.setLabel(str)

  def onAction(self, action):
    if action == ACTION_PREVIOUS_MENU:
      self.close()

#---------- get film types -----------------------------------------------------
def Get_Movie_Type():
    # load movie types
    url = 'http://cinema.mosfilm.ru/Films.aspx?sim=2'
    post = None

    request = urllib2.Request(urllib.unquote(url), post)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'cinema.mosfilm.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://cinema.mosfilm.ru/Films.aspx')

    o = urllib2.urlopen(request)
    http = o.read()
    o.close()

    # get post data
    match=re.compile('<form (.+?)</form>', re.MULTILINE|re.DOTALL).findall(http)
    viewstate   = re.compile('id="__VIEWSTATE" value="(.+?)"', re.MULTILINE|re.DOTALL).findall(match[0])
    # get movie info
    match = re.compile('<div class="filter-box side">(.+?)</div>', re.MULTILINE|re.DOTALL).findall(http)
    glist = re.compile('href="javascript:__doPostBack\(\'(.+?)\',\'\'\)">(.+?)</a>', re.MULTILINE|re.DOTALL).findall(match[0])
    for g in glist:
        name = g[1]
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=TYPE'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&tag=%s'%urllib.quote_plus(g[0])
        u += '&viewstat=%s'%urllib.quote_plus(viewstate[0])
        xbmcplugin.addDirectoryItem(h, u, i, True)

    cj.save(fcookies, ignore_discard=True)
    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

#---------- get moviesfor selected type ----------------------------------------
def Get_Movie_List(params):
    s_type      = urllib.unquote_plus(params['tag'])
    s_name      = urllib.unquote_plus(params['name'])
    s_viewstat  = urllib.unquote_plus(params['viewstat'])

    cj.load(fcookies, ignore_discard=True)
    # load serials types
    url = 'http://cinema.mosfilm.ru/Films.aspx?sim=2'

    values = {'__EVENTTARGET'   : urllib.unquote(s_type),
              '__EVENTARGUMENT' : urllib.unquote(''),
              '__VIEWSTATE'     : urllib.unquote(s_viewstat),
              'ctl00$timeTag'   : '' }

    request = urllib2.Request(urllib.unquote(url), urllib.urlencode(values))
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'cinema.mosfilm.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://cinema.mosfilm.ru/Films.aspx?sim=2')

    o = urllib2.urlopen(request)
    http = o.read()
    o.close()

    flist = re.compile('<div class="movie">(.+?) class="description">(.+?)</a>', re.MULTILINE|re.DOTALL).findall(http)

    for film in flist:
        try:
            f_url_name = re.compile('<span class="name">.*<a href=\'(.+?)\'.*title=\'.*\'>(.+?)</a>', re.MULTILINE|re.DOTALL).findall(film[0])
            if len(f_url_name) == 0:
                continue
            f_year     = re.compile('<span class="year">(.+?)</span>', re.MULTILINE|re.DOTALL).findall(film[0])
            f_image    = re.compile('<img src=\'(.+?)\'', re.MULTILINE|re.DOTALL).findall(film[0])

            i_name = f_url_name[0][1]
            i_url  = f_url_name[0][0]
            if unicode(f_year[0]).isnumeric():
                i_year      = int(f_year[0])
            else:
                i_year      = 1900
            i_image     = 'http://cinema.mosfilm.ru/'+f_image[0]
            i_text      = film[1]
            i_genre     = s_name

            # set serial to XBMC
            i = xbmcgui.ListItem(i_name, iconImage=i_image, thumbnailImage=i_image)
            u = sys.argv[0] + '?mode=LIST'
            u += '&name=%s'%urllib.quote_plus(i_name)
            u += '&url=%s'%urllib.quote_plus(i_url)
            u += '&img=%s'%urllib.quote_plus(i_image)
            i.setInfo(type='video', infoLabels={
                                'title':       i_name,
        						'year':        i_year,
        						'plot':        i_text,
        						'genre':       i_genre})
            i.setProperty('fanart_image', i_image)
            xbmcplugin.addDirectoryItem(h, u, i, True)
        except:
            xbmc.log('***   ERROR '+i_name.encode('utf-8'))

    cj.save(fcookies, ignore_discard=True)
    xbmcplugin.endOfDirectory(h)

#---------- get movie ---------------------------------------------------------
def Get_Movie(params):
    url = urllib.unquote_plus(params['url'])

    if url == None:
        return False

    cj.load(fcookies, ignore_discard=True)

    image = urllib.unquote_plus(params['img'])
    name  = urllib.unquote_plus(params['name'])
    url = 'http://cinema.mosfilm.ru/'+url

    # get movie link
    post = None

    request = urllib2.Request(urllib.unquote(url), post)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'cinema.mosfilm.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://cinema.mosfilm.ru/Films.aspx')

    o = urllib2.urlopen(request)
    http = o.read()
    o.close()

    match=re.compile('<form (.+?)</form>', re.MULTILINE|re.DOTALL).findall(http)

    viewstate   = re.compile('id="__VIEWSTATE" value="(.+?)"', re.MULTILINE|re.DOTALL).findall(match[0])

    has_parts    = re.compile('<div class="side-head">Серии</div>.*<div class=\'content\'>.*<ul>(.+?)</ul>', re.MULTILINE|re.DOTALL).findall(match[0])
    if len(has_parts) == 0:
        #---
        i = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(url)
        u += '&eventtarget=%s'%urllib.quote_plus('ctl00$centerContentPlaceHolder$playLinkButton')
        u += '&viewstate=%s'%urllib.quote_plus(viewstate[0])
        #i.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(h, u, i, False)
    else:
        has_parts    = re.compile('<div class="side-head">Серии</div>(.+?)</ul>', re.MULTILINE|re.DOTALL).findall(match[0])
        part_list = re.compile('<a href="javascript:__doPostBack\(\'(.+?)\',\'\'\)">(.+?)</a>', re.MULTILINE|re.DOTALL).findall(has_parts[0])

        for rec in part_list:
            s = re.compile('<b>(.+?)</b>', re.MULTILINE|re.DOTALL).findall(rec[1])
            iname = name + ' ' + s[0]
            i = xbmcgui.ListItem(iname, iconImage=image, thumbnailImage=image)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(iname)
            u += '&url=%s'%urllib.quote_plus(url)
            u += '&eventtarget=%s'%urllib.quote_plus(rec[0])
            u += '&viewstate=%s'%urllib.quote_plus(viewstate[0])
            #i.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(h, u, i, False)

    cj.save(fcookies, ignore_discard=True)
    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

def PLAY(params):
    url         = urllib.unquote_plus(params['url'])
    eventtarget = urllib.unquote_plus(params['eventtarget'])
    viewstate   = urllib.unquote_plus(params['viewstate'])
    movie_name  = urllib.unquote_plus(params['name'])

    cj.load(fcookies, ignore_discard=True)

    str = 'Загрузка "'+movie_name+'"'
    show_msg = msgDialog()
    show_msg.Set_Message(str)
    show_msg.show()

    # get movie link
    s_tag = re.compile('id=(.+?)</tag>', re.MULTILINE|re.DOTALL).findall(url+'</tag>')
    tag = s_tag[0]

    values = {  '__EVENTARGUMENT'   : urllib.unquote(''),
                '__EVENTTARGET'     : urllib.unquote(eventtarget),
                '__VIEWSTATE'       : urllib.unquote(viewstate),
                'ctl00$centerContentPlaceHolder$captchaTextBox':urllib.unquote(''),
                'ctl00$centerContentPlaceHolder$commentTextBox':urllib.unquote(''),
                'ctl00$centerContentPlaceHolder$cookie':urllib.unquote(''),
                'ctl00$centerContentPlaceHolder$tag':urllib.unquote(tag),
                'ctl00$timeTag':urllib.unquote('')}

    request = urllib2.Request(urllib.unquote(url), urllib.urlencode(values))
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'cinema.mosfilm.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	urllib.unquote(url))

    o = urllib2.urlopen(request)
    http = o.read()
    o.close()

    purchase_ID = re.compile('<param id="ctl00_centerContentPlaceHolder_onlineVideoPlayer_initParam" name="initParams" value="movieType=privateOnline,host=cinema.mosfilm.ru,id=(.+?),', re.MULTILINE|re.DOTALL).findall(http)

    url2 = 'http://cinema.mosfilm.ru/GetMovieCode.ashx?purchaseID='+purchase_ID[0]

    request = urllib2.Request(urllib.unquote(url2), None)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'cinema.mosfilm.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')

    o = urllib2.urlopen(request)
    http = o.read()
    o.close()

    url2 = 'http://cinema.mosfilm.ru/MovieWithOutSessionState.ashx?code='+http

    #play movie
    i = xbmcgui.ListItem(path = urllib.unquote(url2))
    xbmc.Player().play(url2, i)

    show_msg.close()
    del show_msg

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

# get parameters
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.MozillaCookieJar()
cookie_handler  = urllib2.HTTPCookieProcessor(cj)
redirect_handler= urllib2.HTTPRedirectHandler()

opener = urllib2.build_opener(redirect_handler, cookie_handler)
urllib2.install_opener(opener)

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Get_Movie_Type()

if mode == 'TYPE':
	Get_Movie_List(params)
elif mode == 'LIST':
	Get_Movie(params)
if mode == 'PLAY':
	PLAY(params)


