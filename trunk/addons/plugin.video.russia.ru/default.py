#!/usr/bin/python
#/*
# *      Copyright (C) 2010 Kostynoy S. aka Seppius
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
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, urllib2, urllib, re, string, sys, os, traceback
from urllib import urlretrieve, urlcleanup

__settings__ = xbmcaddon.Addon(id='plugin.video.russia.ru')
__language__ = __settings__.getLocalizedString

Header_UserAgent = "Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60"
Header_Host      = "www.russia.ru"
Header_AccLang   = "ru, *"

russia_url = 'http://www.russia.ru/'
thumb = os.path.join(os.getcwd(), 'icon.png')
thumbnail_file = os.path.join( xbmc.translatePath("special://temp/"), "www.russia.ru.tbn")

def GET(target_url, postdata = None):
	try:
		req = urllib2.Request(target_url, postdata)
		req.add_header('User-Agent',      Header_UserAgent)
		req.add_header('Accept-Language', Header_AccLang)
		req.add_header('Host',            Header_Host)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a
	except:
		dialog = xbmcgui.Dialog()
		dialog.ok('ERROR on GET', 'Cannot GET URL %s' % target_url)
		return None

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
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

def clean(name):
	remove=[('<strong>',' '),('</strong>',' '),('<span>',' '),('</span>',' '),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-'),('<nobr>',''),('</nobr>',''),('<P>',''),('</P>','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def ListRSS(target):
	http = GET(russia_url + target)
	if http == None:
		return
	r1 = re.compile('<div class="column first">(.*?)<div class="clear">', re.DOTALL).findall(http)
	if len(r1) == 0:
		xbmc.output('ListRSS len(r1) == 0')
		return
	r2 = r1[0]
	r2 = r2.replace('\t', '')
	r2 = r2.replace('\n', '')
	r2 = r2.replace('\r', '')
	r2 = r2.replace('</a></p>', '</a></p>\n')
	r3 = re.compile('<p><a href="(.*?)"><img.*/>(.*?)</a></p>').findall(r2)
	x = 1
	for URL, NAME in r3:
		URL  = URL.replace('&quot;','')
		NAME = NAME.replace('&quot;','')
		listitem = xbmcgui.ListItem('%s.%s'%(x,NAME), iconImage = thumb, thumbnailImage = thumb)
		url = '%s?mode=%s&url=%s&name=%s'%(sys.argv[0], 'OpenRSS', urllib.quote_plus(URL), urllib.quote_plus(NAME))
		xbmcplugin.addDirectoryItem(handle, url, listitem, True)
		x += 1

def OpenRSS(target, name):
	http = GET(russia_url + target)
	if http == None:
		return
	r1 = re.compile('<item>(.*?)</item>', re.DOTALL).findall(http)
	if len(r1) == 0:
		xbmc.output('OpenRSS len(r1) == 0')
		return
	x = 1
	for r2 in r1:
		title    = re.compile('<title>(.*?)</title>').findall(r2)[0]
		link     = re.compile('<link>(.*?)</link>').findall(r2)[0]
		pubDate  = re.compile('<pubDate>(.*?)</pubDate>').findall(r2)[0]
		category0 = re.compile('<category>(.*?)</category>').findall(r2)
		if len(category0) == 0:
			category = __language__(30003)
		else:
			category = category0[0]
		img0      = re.compile('<img src=\"(.*?)\"/>').findall(r2)
		if len(img0) == 0:
			img = thumb
		else:
			img = img0[0]
		summary0  = re.compile('<itunes:summary>(.*?)</itunes:summary>').findall(r2)
		if len(summary0) == 0:
			summary = __language__(30002)
		else:
			summary = summary0[0]
			summary = summary.replace('<![CDATA[','')
			summary = summary.replace(']]>','')

		#xbmc.output('   title = %s'%title)
		#xbmc.output('    link = %s'%link)
		#xbmc.output(' pubDate = %s'%pubDate)
		#xbmc.output('category = %s'%category)
		#xbmc.output('     img = %s'%img)
		#xbmc.output(' summary = %s'%summary)
		listitem = xbmcgui.ListItem('%s. %s'%(x,title), iconImage = img, thumbnailImage = img)
		listitem.setInfo(type = 'Video', infoLabels = {
			'genre':	category,
			'director':	russia_url,
			'title':	title,
			'studio':	russia_url,
			'premiered':	pubDate,
			'aired':	pubDate,
			'plot':		summary })
		url = '%s?mode=%s&url=%s&name=%s&img=%s'%(sys.argv[0], 'PlayPage', urllib.quote_plus(link), urllib.quote_plus(title), urllib.quote_plus(img))
		xbmcplugin.addDirectoryItem(handle, url, listitem, False)
		x += 1

def parse_dataxml(url):
	url = url + 'data.xml'
	a = GET(url)
	if a == None:
		return
	video_data = re.compile('<video id="(.+?)" name="(.+?)" duration="(.+?)" view="(.+?)" posted="(.+?)">\s*<title>(.+?)</title>\s*<longtitle>(.+?)</longtitle>\s*<subtitle>(.+?)</subtitle>').findall(a)
	if len(video_data) == 0 :
		xbmc.output('parse_dataxml: not found <video..')
		xbmc.output('parse_dataxml: pagedump: %s' % a)
		return
	video_id		= '0'
	video_name		= 'noname'
	video_duration		= '0'
	video_view		= '0'
	video_posted		= '01.01.1970 00:00:00'
	title			= __language__(30001)
	longtitle		= __language__(30002)
	subtitle		= __language__(30003)
	video_id		= video_data[0][0]
	video_name		= video_data[0][1]
	video_duration		= video_data[0][2]
	video_view		= video_data[0][3]
	video_posted		= video_data[0][4]
	title			= video_data[0][5]
	longtitle		= video_data[0][6]
	subtitle		= video_data[0][7]
	video_return = [video_id, video_name, video_duration, video_view, video_posted, title, longtitle, subtitle]
	info_small = ''
	info_long  = ''
	info_data = re.compile('<info>\s*<item>(.+?)</item>\s*<item>(.+?)</item>\s*</info>').findall(a)
	if len(info_data) > 0 :
		info_small = info_data[0][0]
		info_long  = info_data[0][1]
	info_return = [info_small, info_long]
	hero_name = ''
	hero_link = ''
	hero_data = re.compile('<hero>\s*<title>(.+?)</title>\s*<link>(.+?)</link>\s*</hero>').findall(a)
	if len(hero_data) > 0 :
		hero_name = hero_data[0][0]
		hero_link = hero_data[0][1]
	hero_return = [hero_name, hero_link]
	formats_data = re.compile('<formats>(.+?)</formats>', re.DOTALL).findall(a)
	if len(formats_data) == 0 :
		xbmc.output('parse_dataxml: not found <formats> .. </formats>')
		xbmc.output('parse_dataxml: pagedump: %s' % a)
		return
	formats_block = re.compile('<format name="(.+?)" type="(.+?)" size="(.+?)">(.+?)</format>').findall(formats_data[0])
	if len(formats_block) == 0 :
		xbmc.output('parse_dataxml: not found <formats> <format name ... </format> </formats>')
		xbmc.output('parse_dataxml: pagedump: %s' % a)
		return
	video_div = 'video'
	image_div = 'image'
	hd_video = iphone_video = sd_video = None
	hd_size = iphone_size = sd_size = 0
	big_image = xl_image = l_image = iphone_image = s_image = None
	big_imgsize = xl_imgsize = l_imgsize = iphone_imgsize = s_imgsize= 0
	for format_name, format_type, format_size, format_url in formats_block:
		if (format_name == 'hd') and (format_type == video_div):
			hd_video = format_url
			hd_size  = format_size
	for format_name, format_type, format_size, format_url in formats_block:
		if (format_name == 'iphone') and (format_type == video_div):
			iphone_video = format_url
			iphone_size  = format_size
	for format_name, format_type, format_size, format_url in formats_block:
		if (format_name == 'sd') and (format_type == video_div):
			sd_video = format_url
			sd_size  = format_size
	for format_name, format_type, format_size, format_url in formats_block:
		if (format_name == 'big') and (format_type == image_div):
			big_image   = format_url
			big_imgsize = format_size
	for format_name, format_type, format_size, format_url in formats_block:
		if (format_name == 'xl') and (format_type == image_div):
			xl_image   = format_url
			xl_imgsize = format_size
	for format_name, format_type, format_size, format_url in formats_block:
		if (format_name == 'l') and (format_type == image_div):
			l_image   = format_url
			l_imgsize = format_size
	for format_name, format_type, format_size, format_url in formats_block:
		if (format_name == 'iphone') and (format_type == image_div):
			iphone_image   = format_url
			iphone_imgsize = format_size
	for format_name, format_type, format_size, format_url in formats_block:
		if (format_name == 's') and (format_type == image_div):
			s_image   = format_url
			s_imgsize = format_size
	video_urls  = []
	video_sizes = []
	image_urls  = []
	image_sizes = []
	if hd_video != None:
		video_urls.append(hd_video)
		video_sizes.append(hd_size)
	if iphone_video != None:
		video_urls.append(iphone_video)
		video_sizes.append(iphone_size)
	if sd_video != None:
		video_urls.append(sd_video)
		video_sizes.append(sd_size)
	if big_image != None:
		image_urls.append(big_image)
		image_sizes.append(big_imgsize)
	if xl_image != None:
		image_urls.append(xl_image)
		image_sizes.append(xl_imgsize)
	if l_image != None:
		image_urls.append(l_image)
		image_sizes.append(l_imgsize)
	if iphone_image != None:
		image_urls.append(iphone_image)
		image_sizes.append(iphone_imgsize)
	if s_image != None:
		image_urls.append(s_image)
		image_sizes.append(s_imgsize)
	return video_return, info_return, hero_return, video_urls, video_sizes, image_urls, image_sizes


def PlayPage(url):
	if len(url) < 7:
		xbmc.output('play_video: short url: %s' % url)
		return
	(data_ar, info_ar, hero_ar, vid_ar, vids_ar, img_ar, imgs_ar) = parse_dataxml(url)
	if data_ar == None:
		return
	if os.path.isfile(thumbnail_file):
		os.remove(thumbnail_file)
	urllib.version = Header_UserAgent
	urllib.urlretrieve(img_ar[0], thumbnail_file)
	plot = '"' + clean(info_ar[0]).decode('utf-8') + '"\n'
	plot = plot + clean(info_ar[1]).decode('utf-8') + '\n\n'
	plot = plot + __language__(30004) + clean(data_ar[6]).decode('utf-8')# + '\n'
	plot = plot + __language__(30005) + clean(data_ar[7]).decode('utf-8') + '\n'
	plot = plot + __language__(30006) + clean(data_ar[3]).decode('utf-8') + '\n'
	plot = plot + __language__(30007) + clean(data_ar[4]).decode('utf-8') + '\n'
	if hero_ar[0] != '':
		plot = plot + __language__(30008) + clean(hero_ar[0]).decode('utf-8') + '\n'
	if hero_ar[1] != '':
		plot = plot + __language__(30009) + clean(hero_ar[1]).decode('utf-8') + '\n'
	listitem = xbmcgui.ListItem( label = "Video", iconImage = thumbnail_file, thumbnailImage = thumbnail_file )
	listitem.setInfo( type = "Video", infoLabels={
		"Title": 	data_ar[5],
		"Studio": 	url,
		"Plot": 	plot
	} )
	h_1 = '|Referer=' + urllib.quote_plus(url)
	h_2 = '&User-Agent=' + urllib.quote_plus(Header_UserAgent)
	list = []
	spcn = len(vids_ar)
	dialog = xbmcgui.Dialog()
	if spcn == 1:
		selected = 0
	else:
		for x in range(spcn):
			list.append(vids_ar[x])
		selected = dialog.select('Quality?', list)
	if selected < 0:
		return

	xbmc.Player().play(vid_ar[selected] + h_1 + h_2, listitem)

handle = int(sys.argv[1])
params = get_params()

mode = 'ListRSS'
url  = 'http://www.russia.ru/'
name = 'None'


try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	url   = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name  = urllib.unquote_plus(params["name"])
except:
	pass

if mode == 'ListRSS':
	ListRSS('rss/')
	xbmcplugin.endOfDirectory(handle)

if mode == 'OpenRSS':
	OpenRSS(url, name)
	xbmcplugin.endOfDirectory(handle)

if mode == 'PlayPage':
	PlayPage(url)
