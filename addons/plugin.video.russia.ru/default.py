#!/usr/bin/python
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, xbmcaddon
from urllib import urlretrieve, urlcleanup

HEADER     = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'
RUSSIA_URL = 'http://www.russia.ru'

__settings__ = xbmcaddon.Addon(id='plugin.video.russia.ru')
__language__ = __settings__.getLocalizedString

BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "resources" )
thumbnail_next = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "next.png" )
thumbnail_next = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "previous.png" )
russia_play    = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "play.png" )
russia_folder  = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "folder.png" )
russia_thumb   = os.path.join( os.getcwd(), "default.tbn" )
playlist_file  = os.path.join( xbmc.translatePath( "special://temp/" ), "www.russia.ru.m3u" )
thumbnail_file = os.path.join( xbmc.translatePath( "special://temp/" ), "www.russia.ru.tbn" )

download_flag = __settings__.getSetting('download')
download_ask  = __settings__.getSetting('download_ask')
download_path = __settings__.getSetting('download_path')

c_ns = __settings__.getSetting('count_nonstop')
count_nonstop = 15
if c_ns   == '1':
	count_nonstop = 30
elif c_ns == '2':
	count_nonstop = 100

c_ls = __settings__.getSetting('count_list')
count_list = 15
if c_ls   == '1':
	count_list = 30
elif c_ls == '2':
	count_list = 100

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
	remove=[('<span class="link-title">', ' '),('<span>',' '),('</span>',' '),('\n',' '),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-'),('<nobr>',''),('</nobr>',''),('<P>',''),('</P>','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def parse_dataxml(url):
	url = url + 'data.xml'
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
	except:
		xbmc.output('parse_dataxml: Cannot open URL: %s' % url)
		return
	a = f.read()
	f.close()
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


def play_video(url):
	if len(url) < 7:
		xbmc.output('play_video: short url: %s' % url)
		return
	(data_ar, info_ar, hero_ar, vid_ar, vids_ar, img_ar, imgs_ar) = parse_dataxml(url)
	if data_ar == None:
		return
	if os.path.isfile(thumbnail_file):
		os.remove(thumbnail_file)
	urllib.version = HEADER
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
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(vid_ar[0], listitem)

def show_videoarray(url):
	url = url + '?pagesize=' + str(count_list)
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		xbmc.output('show_videoarray: Error on Request! URL: %s' % url)
		return

	page_data = re.compile('<div class="date">(.+?)</div><a class="play-news" href="(.+?)"></a><a class="podrobno" href="(.+?)">(.+?)</a><a href="(.+?)"><img align="absmiddle" class="img" src="(.+?)" width="(.+?)" height="(.+?)"/></a><div class="info"><a class="hd" href="(.+?)">(.+?)</a><div class="text-news">(.+?)</div>').findall(a)
	if len(page_data) > 0:
		for time, url1, url2, raw, url3, img, raw1, raw2, url, name, info in page_data:
			title = clean(name)
			plot  = clean(info)
			video_url = RUSSIA_URL + url
			listitem = xbmcgui.ListItem( title, iconImage = img, thumbnailImage = img )
			listitem.setInfo( type = "Video", infoLabels = {
				"Title" : title,
				"Plot"  : plot
			} )
			url= sys.argv[0] + "?mode=play_video&url=" + urllib.quote_plus(video_url) + "&title=" + urllib.quote_plus(title)
			xbmcplugin.addDirectoryItem(handle, url, listitem, False)
	else:
		xbmc.output('show_videoarray: Error, page_data=0 A: %s' % a)
		return

def play_nonstop(url):
	dp = xbmcgui.DialogProgress()
	dp.create(__language__(30010))
	url = url + '?pagesize=' + str(count_nonstop)
	dp.update(0, url)
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
	except:
		xbmc.output('play_nonstop: Cannot open URL: %s' % url)
		return

	a = f.read()
	f.close()

	news_list = []
	start_news= re.compile('<div class="player"><embed name="player" src=".*" flashvars="name=(.+?)&playnext=.*".*</embed></div>').findall(a)
	if len(start_news) > 0:
		news_list.append('/video/'+start_news[0]+'/')
	page_data = re.compile('<div class="date">(.+?)</div><a class="play-news" href="(.+?)"></a><a class="podrobno" href="(.+?)">(.+?)</a><a href="(.+?)"><img align="absmiddle" class="img" src="(.+?)" width="(.+?)" height="(.+?)"/></a><div class="info"><a class="hd" href="(.+?)">(.+?)</a><div class="text-news">(.+?)</div>').findall(a)
	if len(page_data) > 0:
		for time, url1, url2, raw, url3, img, raw1, raw2, url, name, info in page_data:
			news_list.append(url)

	m3u_list = []
	m3u_list.append('#EXTM3U' + '\n')
	pos = 0

	for cur_news in news_list:

		percent = min((pos*100)/count_nonstop, 100)
		dp.update(percent, __language__(30011) + '\n' + RUSSIA_URL + cur_news)
		if dp.iscanceled():
			dp.close()

		url = RUSSIA_URL + cur_news

		(data_ar, info_ar, hero_ar, vid_ar, vids_ar, img_ar, imgs_ar) = parse_dataxml(url)
		if data_ar == None:
			return

		mp4_video = vid_ar[0]
		title     = data_ar[6]

		m3u_list.append('#EXTINF:-1,' + title + '\n')
		m3u_list.append(mp4_video + '\n')
		pos = pos + 1



	if os.path.isfile(playlist_file):
		os.remove(playlist_file)
	m3u_file = open(playlist_file, 'w')
	m3u_file.writelines(m3u_list)
	m3u_file.close()
	xbmc.Player().play(playlist_file)


def show_root_news():
	url = RUSSIA_URL + '/news'
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return


	page_data = re.compile('<div class="news-block-hd"><a href="(.+?)">(.+?)</a>').findall(a)
	if len(page_data) > 0:
		for url, name in page_data:
			title = __language__(30012) + ' / ' + clean(name).decode('utf-8')
			video_url = RUSSIA_URL + url
			listitem = xbmcgui.ListItem(title, iconImage = russia_thumb, thumbnailImage = russia_thumb)
			listitem.setInfo(type = "Video", infoLabels = {"Title" : title})
			u=sys.argv[0] + "?mode=show_news&url=" + urllib.quote_plus(video_url) + "&title=" + title
			xbmcplugin.addDirectoryItem(int(handle), u, listitem, True)

	page_data = re.compile('<div class="news-block-small-hd"><a href="(.+?)">(.+?)</a>').findall(a)
	if len(page_data) > 0:
		for url, name in page_data:
			title = __language__(30013) + ' / ' + clean(name).decode('utf-8')
			video_url = RUSSIA_URL + url
			listitem = xbmcgui.ListItem(title, iconImage = russia_thumb, thumbnailImage = russia_thumb)
			listitem.setInfo(type = "Video", infoLabels = {"Title" : title})
			u=sys.argv[0] + "?mode=show_news&url=" + urllib.quote_plus(video_url) + "&title=" + title
			xbmcplugin.addDirectoryItem(int(handle), u, listitem, True)

	page_data = re.compile('<div class="news-non-stop"><a href="(.+?)"><span class="text">(.+?)</span>').findall(a)
	if len(page_data) > 0:
		for url, name in page_data:
			title = clean(name)
			video_url = RUSSIA_URL + url
			listitem = xbmcgui.ListItem(title, iconImage = russia_play, thumbnailImage = russia_play)
			listitem.setInfo(type = "Video", infoLabels = {"Title" : title})
			u=sys.argv[0] + "?mode=play_nonstop_news&url=" + urllib.quote_plus(video_url) + "&title=" + urllib.quote_plus(title)
			xbmcplugin.addDirectoryItem(int(handle), u, listitem, False)

	page_data = re.compile('<a href="(.+?)" id="all-updates">(.+?)</a>').findall(a)
	if len(page_data) > 0:
		for url, name in page_data:
			title = clean(name)
			video_url = RUSSIA_URL + url
			listitem = xbmcgui.ListItem(title, iconImage = russia_thumb, thumbnailImage = russia_thumb)
			listitem.setInfo(type = "Video", infoLabels = {"Title" : title})
			u=sys.argv[0] + "?mode=play_nonstop_video&url=" + urllib.quote_plus(video_url) + "&title=" + urllib.quote_plus(title)
			xbmcplugin.addDirectoryItem(int(handle), u, listitem, False)




def show_root_programs():
	url = RUSSIA_URL + '/program' + '?pagesize=' + str(count_list)
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return
	page_data = re.compile('<div class="content">(.+?)<div class="clear">', re.DOTALL).findall(a)
	page_len = len(page_data)
	if page_len ==1:
		p1_data = re.compile('</div><a class="programm-name" href="(.+?)">(.+?)<b>(.+?)</b></a>').findall(page_data[0])
		p2_data = re.compile('<img align="absmiddle" src="(.+?)" width=".*" height=".*"/></a></div>').findall(page_data[0])
		p1_len = len(p1_data)
		p2_len = len(p2_data)
		if p1_len == p2_len:
			use_images = True
		else:
			use_images = False
		if p1_len > 0:
			x = 0
			for prog_url, prog_name, prog_count in p1_data:
				if use_images == True:
					img = p2_data[x]
				else:
					img = russia_thumb
				title = __language__(30014) + ' / ' + clean(prog_name).decode('utf-8')
				prog_url = RUSSIA_URL + prog_url
				listitem = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
				listitem.setInfo( type = "Video", infoLabels = {
					"Title" : title
				} )
				url= sys.argv[0] + "?mode=get_programs&url=" + urllib.quote_plus(prog_url) + "&title=" + title
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)
				x = x + 1

def show_root_link(title, mode, link):
	listitem = xbmcgui.ListItem(title, iconImage=russia_folder, thumbnailImage=russia_folder)
	listitem.setInfo( type = "Video", infoLabels = { "Title" : title } )
	u=sys.argv[0] + "?mode=" + mode + "&url=" + urllib.quote_plus(RUSSIA_URL + link) + "&title=" + title
	xbmcplugin.addDirectoryItem(int(handle), u, listitem, True)




def get_programs(url):
	url = url + '?pagesize=' + str(count_list)

	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return

	prog_list = []

	start_prog = re.compile('<embed name="player" src=".*" flashvars="name=(.+?)".*</embed>').findall(a)
	if len(start_prog) > 0:
		try:
			new_url = '/video/' + start_prog[0] + '/'
			(data_ar, info_ar, hero_ar, vid_ar, vids_ar, img_ar, imgs_ar) = parse_dataxml(RUSSIA_URL + new_url)
			new_title = data_ar[4] + ' ' + data_ar[5]
			prog_list.append([new_title, new_url, img_ar[1]])
		except:
			xbmc.output('get_programs -> EXCEPT IN start_prog')
			return

	bd_panel = re.compile('<div class="program-video-bg bd-image-panel">(.+?)<div class="clear">', re.DOTALL).findall(a)
	if len(bd_panel) > 0:
		panel_arr = re.compile('<div class="program-video-block"><div class="image"><div id="top-left" class="programs-block-small-round"></div><div id="top-right" class="programs-block-small-round"></div><div id="bottom-left" class="programs-block-small-round"></div><div id="bottom-right" class="programs-block-small-round"></div><a href="(.+?)"><img src="(.+?)" width="(.+?)" height="(.+?)"/></a></div><div class="caption">(.+?)</div><a class="link" href="(.+?)">(.+?)</a></div>').findall(bd_panel[0])
		if len(panel_arr) > 0:
			for URL, IMG, X, Y, DATE, URL2, TITLE in panel_arr:
				item_title = clean(DATE + ' ' + TITLE)
				if len(URL2) > len(URL):
					URL = URL2
				prog_list.append([item_title, URL, IMG])
		else:
			xbmc.output('get_programs -> panel_arr = 0')
			xbmc.output('get_programs -> A: %s' % a )

	else:
		xbmc.output('get_programs -> bd_panel_l = 0')
		xbmc.output('get_programs -> A: %s' % a )


	#xbmc.output('get_programs -> prog_list:  %s' % prog_list )

	if len(prog_list) > 0:

		for title, url, img in prog_list:
			video_url = RUSSIA_URL + url

			listitem = xbmcgui.ListItem( title, iconImage = img, thumbnailImage = img )

			listitem.setInfo( type = "Video", infoLabels = {
				"Title" : title
			} )

			url= sys.argv[0] + "?mode=play_video&url=" + urllib.quote_plus(video_url) + "&title=" + urllib.quote_plus(title)
			xbmcplugin.addDirectoryItem(handle, url, listitem, False)




def get_common(url, title, compl, mode):
	url = url + '?pagesize=' + str(count_list)
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return
	page_data = re.compile(compl).findall(a)
	if len(page_data) > 0:
		for url, name in page_data:
			caption = title + ' / ' + clean(name)
			video_url = RUSSIA_URL + url
			listitem = xbmcgui.ListItem(caption, iconImage=russia_folder, thumbnailImage=russia_folder)
			listitem.setInfo(type = "Video", infoLabels={"Title" : caption})
			u=sys.argv[0] + "?mode=" + mode + "&url=" + urllib.quote_plus(video_url) + "&title=" + urllib.quote_plus(caption)
			xbmcplugin.addDirectoryItem(int(handle), u, listitem, True)


params = get_params()


title = 'RUSSIA.RU'
mode  = None
url   = None

try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	title = urllib.unquote_plus(params["title"])
except:
	pass
try:
	url   = urllib.unquote_plus(params["url"])
except:
	pass

handle = int(sys.argv[1])

if mode == None:
	show_root_news()
	show_root_programs()
	show_root_link(__language__(30020), 'show_popular', '/popular')
	show_root_link(__language__(30021), 'get_myrussia', '/myrussia')
	show_root_link(__language__(30022),   'get_heroes',   '/hero')

elif mode=='get_programs':
	get_programs(url)

elif mode=='get_myrussia':
	get_common(url, title, '<div class="location-block-hd"><a href="(.+?)">(.+?)</a>', 'show_myrussia')

elif mode=='get_heroes':
	get_common(url, title, '<div class="heroes-block-hd"><a href="(.+?)">(.+?)</a>', 'show_heroes')

elif mode=='show_news':
	show_videoarray(url)

elif mode=='show_heroes':
	show_videoarray(url)

elif mode=='show_myrussia':
	show_videoarray(url)

elif mode=='play_nonstop_news':
	play_nonstop(url)

elif mode=='play_video':
	play_video(url)


xbmcplugin.setPluginCategory(handle, title )
xbmcplugin.endOfDirectory(handle)
