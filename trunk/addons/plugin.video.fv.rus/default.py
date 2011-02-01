import xbmc, xbmcgui, xbmcplugin, xbmcaddon, os, urllib, socket, xml.dom.minidom, base64

__settings__ = xbmcaddon.Addon(id='plugin.video.fv.rus')
__language__ = __settings__.getLocalizedString



handle = int(sys.argv[1])

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))


def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def GET(targeturl):
	targeturl = base64.b64decode(__language__(30001)) + targeturl
	import httplib
	conn =   httplib.HTTPConnection(host=base64.b64decode(__language__(30000)), port=80)
	html_headers =  {'User-Agent':'XBMC/plugin.video.fv.rus','Host':base64.b64decode(__language__(30000))}
	conn.request(method='GET', url=targeturl, headers=html_headers) # , body=doc.toxml(encoding='utf-8')
	response = conn.getresponse()
	#hdrs = response.getheader('Set-Cookie')
	#if hdrs != None:
		#__settings__.setSetting('rrrr', eeeee)
		#print 'Save %s'%hdrs
	#print 'Set-Cookie %s'%hdrs
	#print 'status %d'%response.status
	#print 'reason %s'%response.reason
	#print 'DATA %s'%response.read()
	html = response.read()
	conn.close()
	#print 'DATA %s'%html
	return html





def getitems(params):
	#xbmc.output('def getitems(params=%s):'%params)
	try:    initurl = urllib.unquote_plus(params['path'])
	except: initurl = ''
	try:    timeout = urllib.unquote_plus(params['timeout'])
	except: timeout = 10
	socket.setdefaulttimeout(timeout)

	http = GET(initurl)
	if http == None: return False


	document = xml.dom.minidom.parseString(http)

	for item in document.getElementsByTagName('item'):

			info = {}

			try:
				v_idx = long(item.getElementsByTagName('v_idx')[0].firstChild.data)
			except:
				#xbmc.output(' * ERROR PARSING : v_idx')
				v_idx = None

			try:
				v_count = int(item.getElementsByTagName('v_count')[0].firstChild.data)
				info['count'] = v_count
			except:
				#xbmc.output(' * ERROR PARSING : v_count')
				v_count = None

			try:
				v_size = long(item.getElementsByTagName('v_size')[0].firstChild.data)
				info['size'] = v_size
			except:
				#xbmc.output(' * ERROR PARSING : v_size')
				v_size = None

			try:
				v_date = item.getElementsByTagName('v_date')[0].firstChild.data
				info['date'] = v_date
			except:
				#xbmc.output(' * ERROR PARSING : v_date')
				v_date = None

			try:
				v_genre = item.getElementsByTagName('v_genre')[0].firstChild.data
				info['genre'] = v_genre
			except:
				#xbmc.output(' * ERROR PARSING : v_genre')
				v_genre = None

			try:
				v_year = int(item.getElementsByTagName('v_year')[0].firstChild.data)
				info['year'] = v_year
			except:
				#xbmc.output(' * ERROR PARSING : v_year')
				v_year = None

			try:
				v_episode = int(item.getElementsByTagName('v_episode')[0].firstChild.data)
				info['episode'] = v_episode
			except:
				#xbmc.output(' * ERROR PARSING : v_episode')
				v_episode = None

			try:
				v_season = int(item.getElementsByTagName('v_season')[0].firstChild.data)
				info['season'] = v_season
			except:
				#xbmc.output(' * ERROR PARSING : v_season')
				v_season = None

			try:
				v_top250 = int(item.getElementsByTagName('v_top250')[0].firstChild.data)
				info['top250'] = v_top250
			except:
				#xbmc.output(' * ERROR PARSING : v_top250')
				v_top250 = None

			try:
				v_tracknumber = int(item.getElementsByTagName('v_tracknumber')[0].firstChild.data)
				info['tracknumber'] = v_top250
			except:
				#xbmc.output(' * ERROR PARSING : v_tracknumber')
				v_tracknumber = None

			try:
				v_rating = float(item.getElementsByTagName('v_rating')[0].firstChild.data)
				info['rating'] = v_rating
			except:
				#xbmc.output(' * ERROR PARSING : v_rating')
				v_rating = None

			try:
				v_playcount = int(item.getElementsByTagName('v_playcount')[0].firstChild.data)
				info['playcount'] = v_playcount
			except:
				#xbmc.output(' * ERROR PARSING : v_playcount')
				v_playcount = None

			try:
				v_overlay = int(item.getElementsByTagName('v_overlay')[0].firstChild.data)
				info['overlay'] = v_overlay
			except:
				#xbmc.output(' * ERROR PARSING : v_overlay')
				v_overlay = None

			try:
				v_cast = list(item.getElementsByTagName('v_cast')[0].firstChild.data)
				info['cast'] = v_cast
			except:
				#xbmc.output(' * ERROR PARSING : v_cast')
				v_cast = None

			try:
				v_castandrole = list(item.getElementsByTagName('v_castandrole')[0].firstChild.data)
				info['castandrole'] = v_castandrole
			except:
				#xbmc.output(' * ERROR PARSING : v_castandrole')
				v_castandrole = None

			try:
				v_director = item.getElementsByTagName('v_director')[0].firstChild.data
				info['director'] = v_director
			except:
				#xbmc.output(' * ERROR PARSING : v_director')
				v_director = None

			try:
				v_mpaa = item.getElementsByTagName('v_mpaa')[0].firstChild.data
				info['mpaa'] = v_mpaa
			except:
				#xbmc.output(' * ERROR PARSING : v_mpaa')
				v_mpaa = None

			try:
				v_plot = item.getElementsByTagName('v_plot')[0].firstChild.data
				info['plot'] = v_plot
			except:
				#xbmc.output(' * ERROR PARSING : v_plot')
				v_plot = None

			try:
				v_plotoutline = item.getElementsByTagName('v_plotoutline')[0].firstChild.data
				info['plotoutline'] = v_plotoutline
			except:
				#xbmc.output(' * ERROR PARSING : v_plotoutline')
				v_plotoutline = None

			try:
				v_title = item.getElementsByTagName('v_title')[0].firstChild.data
				info['title'] = v_title
			except:
				#xbmc.output(' * ERROR PARSING : v_title')
				v_title = None

			try:
				v_duration = item.getElementsByTagName('v_duration')[0].firstChild.data
				info['duration'] = v_duration
			except:
				#xbmc.output(' * ERROR PARSING : v_duration')
				v_duration = None

			try:
				v_studio = item.getElementsByTagName('v_studio')[0].firstChild.data
				info['studio'] = v_studio
			except:
				#xbmc.output(' * ERROR PARSING : v_studio')
				v_studio = None

			try:
				v_tagline = item.getElementsByTagName('v_tagline')[0].firstChild.data
				info['tagline'] = v_tagline
			except:
				#xbmc.output(' * ERROR PARSING : v_tagline')
				v_tagline = None

			try:
				v_writer = item.getElementsByTagName('v_writer')[0].firstChild.data
				info['writer'] = v_writer
			except:
				#xbmc.output(' * ERROR PARSING : v_writer')
				v_writer = None

			try:
				v_tvshowtitle = item.getElementsByTagName('v_tvshowtitle')[0].firstChild.data
				info['tvshowtitle'] = v_tvshowtitle
			except:
				#xbmc.output(' * ERROR PARSING : v_tvshowtitle')
				v_tvshowtitle = None

			try:
				v_premiered = item.getElementsByTagName('v_premiered')[0].firstChild.data
				info['premiered'] = v_premiered
			except:
				#xbmc.output(' * ERROR PARSING : v_premiered')
				v_premiered = None

			try:
				v_status = item.getElementsByTagName('v_status')[0].firstChild.data
				info['status'] = v_status
			except:
				#xbmc.output(' * ERROR PARSING : v_status')
				v_status = None

			try:
				v_code = item.getElementsByTagName('v_code')[0].firstChild.data
				info['code'] = v_code
			except:
				#xbmc.output(' * ERROR PARSING : v_code')
				v_code = None

			try:
				v_aired = item.getElementsByTagName('v_aired')[0].firstChild.data
				info['aired'] = v_aired
			except:
				#xbmc.output(' * ERROR PARSING : v_aired')
				v_aired = None

			try:
				v_credits = item.getElementsByTagName('v_credits')[0].firstChild.data
				info['credits'] = v_credits
			except:
				#xbmc.output(' * ERROR PARSING : v_credits')
				v_credits = None

			try:
				v_lastplayed = item.getElementsByTagName('v_lastplayed')[0].firstChild.data
				info['lastplayed'] = v_lastplayed
			except:
				#xbmc.output(' * ERROR PARSING : v_lastplayed')
				v_lastplayed = None

			try:
				v_album = item.getElementsByTagName('v_album')[0].firstChild.data
				info['album'] = v_album
			except:
				#xbmc.output(' * ERROR PARSING : v_album')
				v_album = None

			try:
				v_votes = item.getElementsByTagName('v_votes')[0].firstChild.data
				info['votes'] = v_votes
			except:
				#xbmc.output(' * ERROR PARSING : v_votes')
				v_votes = None

			try:
				v_trailer = item.getElementsByTagName('v_trailer')[0].firstChild.data
				info['trailer'] = v_trailer
			except:
				#xbmc.output(' * ERROR PARSING : v_trailer')
				v_trailer = None

			try:
				v_fanartimage = item.getElementsByTagName('v_fanartimage')[0].firstChild.data
			except:
				#xbmc.output(' * ERROR PARSING : v_fanartimage')
				v_fanartimage = None

			try:
				v_iconImage = item.getElementsByTagName('v_iconImage')[0].firstChild.data
			except:
				#xbmc.output(' * ERROR PARSING : v_iconImage')
				v_iconImage = ''

			try:
				v_thumbnailImage = item.getElementsByTagName('v_thumbnailImage')[0].firstChild.data
			except:
				#xbmc.output(' * ERROR PARSING : v_thumbnailImage')
				v_thumbnailImage = ''

			try:
				IsPlayable = (item.getElementsByTagName('IsPlayable')[0].firstChild.data == '1')
			except:
				IsPlayable = False

			try:
				IsFolder = (item.getElementsByTagName('IsFolder')[0].firstChild.data == '1')
			except:
				IsFolder = False

			uri = sys.argv[0] + item.getElementsByTagName('next_url')[0].firstChild.data


			#try:
			li = xbmcgui.ListItem(v_title, iconImage = v_iconImage, thumbnailImage = v_thumbnailImage)
			li.setInfo(type = 'video', infoLabels = info)
			if v_fanartimage != None: li.setProperty('fanart_image', v_fanartimage)
			if IsPlayable: li.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(handle, uri, li, IsFolder)
			#except:
			#		#xbmc.output(' * ERROR ADDING : xbmcplugin.addDirectoryItem')
			#		pass


	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DURATION)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)

	xbmcplugin.endOfDirectory(handle)



def play(params):
	#xbmc.output('def play(params=%s):'%params)

	try:    path = urllib.unquote_plus(params['path'])
	except: path = None

	try:    timeout = urllib.unquote_plus(params['timeout'])
	except: timeout = 10
	socket.setdefaulttimeout(timeout)

	http = GET(path)
	i = xbmcgui.ListItem(path = base64.b64decode(http))
	xbmcplugin.setResolvedUrl(handle, True, i)




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
try:    mode = urllib.unquote_plus(params['mode'])
except: getitems(params)
if mode != None:
	try:    func = globals()[mode]
	except: pass
	if func: func(params)
