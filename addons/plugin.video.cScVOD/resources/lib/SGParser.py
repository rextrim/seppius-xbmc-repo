import sys
sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/cScVOD')
sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/cScVOD/Libs')
import urllib2, urllib
import os, re, json

def hdrezka_film(url):
	parts = url.split('@')
	url = parts[1]
	request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
	'Connection': 'Close'})
	try:
		page = urllib2.urlopen(request).read()
		code = re.findall('name="post_id" id="post_id" value="(.*)" />', page)
		if len(code) > 0:
			url2 = 'http://hdrezka.tv/engine/ajax/getvideo.php'
	
			headers = {
				"Accept" : "text/plain, */*; q=0.01",
				"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
				"Host" : "hdrezka.tv",
				"Referer" : url,
				"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0",
				"X-Requested-With" : "XMLHttpRequest"
			}
			
			data = urllib.urlencode({
				"id" : code[0]
			})
			plist = []
			plist2 = []
			request = urllib2.Request(url2, data, headers)
			response = urllib2.urlopen(request).read()
			page = json.loads(response)
			url2 = json.loads(page['link'])
			if url2['mp4'] > 0:
				code_url = 'http://93.188.161.204/php/rezka.php?url=' + url2['mp4']
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				hash = urllib2.urlopen(request2).read()
				url = hash
				print url
			url = url
			print url
		url = url
		print url
		
	except Exception as ex:
		print ex
	
	return url

def hdrezka_serial(url):
	parts = url.split('@')
	url = parts[1]
	season = parts[3]
	episode = parts[2]
	
	request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
	'Connection': 'Close'})
	try:
		page = urllib2.urlopen(request).read()
		code = re.findall('class="b-content__inline_item" data-id="(.*)"', page)
		if len(code) > 0:
			print 'get video'
			url2 = 'http://hdrezka.tv/engine/ajax/getvideo.php'
	
			headers = {
				"Accept" : "text/plain, */*; q=0.01",
				"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
				"Host" : "hdrezka.tv",
				"Referer" : url,
				"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0",
				"X-Requested-With" : "XMLHttpRequest"
			}
			
			data = urllib.urlencode({
				'id': code[0],
				'season':  season,
				'episode': episode
			})
			plist = []
			request = urllib2.Request(url2, data, headers)
			response = urllib2.urlopen(request).read()
			page = json.loads(response)
			url2 = json.loads(page['link'])
			if url2['mp4'] > 0:
				code_url = 'http://93.188.161.204/php/rezka.php?url=' + url2['mp4']
				request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				hash = urllib2.urlopen(request2).read()
				url = hash
				print 'hdrezka serial: ' + url
			url = url
			print url
		url = url
		print url
				
	except Exception as ex:
		print ex
	
	return url
	
def hdrezka_gid(url):
	parts = url.split('@')
	url = parts[1]
	request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
	'Connection': 'Close'})
	try:
		page = urllib2.urlopen(request).read()
		code_list = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", page)
		for urls in code_list:
			if urls.find('720.mp4/manifest') > 0:
				url = urls
			elif urls.find('480.mp4/manifest') > 0:
				url = urls
			# elif urls.find('360.mp4/manifest') > 0:
				# url = urls
			
			
		url = url
		url = url.replace("',", "")
		url = url.replace('/manifest.f4m', '')
		print 'gggggg' + url
		
	except Exception as ex:
		print ex
	
	return url
	
	
class sg_parsers:
	
	def __init__(self):
		self.quality = ''
	
	def get_parsed_link(self, url):
		try:
			if url.find('.lovekino.tv/video/md5hash') > -1:
				url1 = 'http://s2.lovekino.tv/player/play.php?name=films/klyatva.na.krovi.2010.xvid.iptvrip.filesx.flv'
				request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
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
				request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall('film/(.*?)/', page)
					if len(code) > 0:
						md5hash = code[0]
						url = url.replace('md5hash', md5hash)
				except Exception as ex:
					print ex
	
			# if url.find('brb.to/video') > -1 or url.find('fs.to/video') > -1:
				# request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				# 'Connection': 'Close'})
				# try:
					# page = urllib2.urlopen(request).read()
					# code = re.findall("url: '/get/play/(.*)',", page)
					# if len(code) > 0:
						# md5hash = code[0]
						# url = 'http://brb.to/get/play/' + md5hash
				# except Exception as ex:
					# print ex
	
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
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code_list = re.findall(',"file":"(.*)","f', page)
					if len(code_list) > 0:
						code = code_list[0]
						code_url = 'http://93.188.161.204/php/kaban/kaban.php?code=' + code
						request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
						'Connection': 'Close'})
						try:
							hash = urllib2.urlopen(request2).read()
							code_list2 = re.findall('or (.*)', hash)
							if len(code_list2) > 0:
								url = code_list2[0]
								print 'kabantv'
								print url
							else:
								url = hash
						except Exception as ex:
							print ex
	
				except Exception as ex:
					print ex
	
			if url.find('poiuytrew.pw/') > -1:
				url1 = 'http://filmix.net/dramy/82725-vnutri-lyuina-devisa-inside-llewyn-davis-2013.html'
				request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code_list = re.findall('&amp;file=(.*)&amp;.*&amp;', page)
					if len(code_list) > 0:
						code = code_list[0]
						code_url = 'http://93.188.161.204/php/filmix.php?code=' + code
						request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
						'Connection': 'Close'})
						hash = urllib2.urlopen(request2).read()
						url = url.replace('md5hash', hash)
						if url.find('[720,480,360]') > -1:
							url = url.replace('[720,480,360]','720')
						elif url.find('[,480,360]') > -1:
							url = url.replace('[,480,360]','720')
						else:
							url = url
						print 'filmix'
						print url
				except Exception as ex:
					print ex
	
			if url.find('pirateplayer.com/') > -1:
				url1 = 'http://online.stepashka.com/filmy/detektiv/29140-falshivaya-kukla-hamis-a-baba-1991.html'
				request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code_list = re.findall('st=http:\\/\\/online.stepashka.com\\/player\\/.*\\/.*\\/(.*)\\/"', page)
					if len(code_list) > 0:
						code = code_list[0]
						url = url.replace('md5hash', code)
						print 'stepashka'
						print url
				except Exception as ex:
					print ex
	
			if url.find('.videokub.com/embed/') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code_list = re.findall('file:"(.*?)/",', page)
					if len(code_list) > 0:
						url = code_list[0]
						print 'videokub'
						print url
				except Exception as ex:
					print ex
	
			if url.find('hotcloud.org/') > -1:
				url1 = 'https://my-hit.org/film/558/playlist.txt'
				request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall('id=(.*?)"}]}', page)
					if len(code) > 0:
						md5hash = code[0]
						url = url.replace('md5hash', md5hash)
				except Exception as ex:
					print ex
	
			if url.find('moviestape.com/') > -1:
				url1 = 'http://fs0.moviestape.com/show.php?name=films/Captain.Phillips.mp4'
				request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall("file : 'http:\\/\\/.*\\/video\\/(.*)\\/.*\\/.*mp4'};", page)
					if len(code) > 0:
						md5hash = code[0]
						url = url.replace('md5hash', md5hash)
				except Exception as ex:
					print ex
					
			if url.find('aburmu4.tv') > -1:
				url1 = 'http://s1.aburmu4.tv/player/play.php?s=1&name=vsfw/antboy_2013.flv'
				request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall("file : 'http:\\/\\/.*\\/v\\/(.*)\\/.*\\/.*flv'};", page)
					if len(code) > 0:
						md5hash = code[0]
						url = url.replace('md5hash', md5hash)
						url = url.replace('aburmu4.tv@', '')
				except Exception as ex:
					print ex
			
			if url.find('serialo.ru/video') > -1:
				url5 = 'http://latino-serialo.ru/italianskie_seriali_online/2638-polny-ocharovaniya-cheias-de-charme-seriya-10.html'
				request = urllib2.Request(url5, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					hash_list = re.findall(';pl=(.*?)"', page)
					if len(hash_list) > 0:
						hash = hash_list[0]
						print 'hash ' + hash
						request2 = urllib2.Request(hash, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
						'Connection': 'Close'})
						page = urllib2.urlopen(request2).read()
						page = page.replace('\n', '')
						tmp = re.findall('file":"(.*?)"', page)
						tmp = tmp[0]
						print 'tmp ' + tmp
						md5hash = re.findall('\\/video\\/(.*?)\\/', tmp)
						md5hash = md5hash[0]
						tmp2 = tmp.replace(md5hash, 'md5hash')
						md4hash = re.findall('\\/md5hash\\/(.*?)\\/', tmp2)
						md4hash = md4hash[0]
						print 'md5hash ' + md5hash
						print 'md4hash ' + md4hash
						url2 = url.replace('md5hash', md5hash)
						url = url2.replace('md4hash', md4hash)
						print "PLAY URL" + url
				except Exception as ex:
					print ex
			
			if url.find('divan.tv/') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall('file: "(.*?)",', page)
					if len(code) > 0:
						url = code[0]
				except Exception as ex:
					print ex
			
			if url.find('baskino.com/films') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code_list = re.findall('file:"(.*?)"', page)
					if len(code_list) > 0:
						url = code_list[0]
						print 'baskino'
						print url
				except Exception as ex:
					print ex
			
			if url.find('hdrezka.tv/films') > -1:
				url = hdrezka_film(url)
				url = url
			
			if url.find('hdrezka.tv/series') > -1:
				url = hdrezka_serial(url)
				url = url
			
			if url.find('hdrezka.tv/gidtv') > -1:
				url = hdrezka_gid(url)
				url = url
			
			if url.find('kinobar.net/player') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code_list = re.findall('<source src="(.*)" type=', page)
					if len(code_list) > 0:
						url = code_list[0]
						print 'kinobar'
						print url
				except Exception as ex:
					print ex
				
			if url.find('serials.tv/') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code_list = re.findall("src: '(.*?)',", page)
					if len(code_list) > 0:
						url = code_list[0]
						print 'kinobar'
						print url
				except Exception as ex:
					print ex
					
			if url.find('.jampo.tv/play') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code_list = re.findall('<video width=".*?" height=".*?" src="(.*?)" controls />', page)
					if len(code_list) > 0:
						url = code_list[0]
						print 'jampo'
						print url
				except Exception as ex:
					print ex
			
			if url.find('lidertvvv') > -1:
				url = url.replace('lidertvvv','')
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall('file: "(.*?)",', page)
					if len(code) > 0:
						url = code[0]
				except Exception as ex:
					print ex
			
			if url.find('moonwalk.cc/video') > -1:
				url = url.replace('/iframe', '/index.m3u8')
				url = url
			
			if url.find('moonwalk.cc/serial') > -1:
				url1 = url
				request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall("video_token: '(.*)',", page)
					if len(code) > 0:
						url = 'http://moonwalk.cc/video/' + code[0] + '/index.m3u8'
				except Exception as ex:
					print ex
			
		except Exception as ex:
			print ex
			print 'sgparsed_link'
	
		return url