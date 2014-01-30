import re
import urllib2

class sg_parsers:

    def __init__(self):
        self.quality = ''

    def get_parsed_link(self, url):
        try:
			if url.find('.minizal.net/video/md5hash') > -1:
				url1 = 'http://s2.minizal.net/php/play.php?name=film/pod.krovatju.2012.bdrip.flv'
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
	
			if url.find('brb.to/video') > -1 or url.find('fs.to/video') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall("url: '/get/play/(.*)',", page)
					if len(code) > 0:
						md5hash = code[0]
						url = 'http://brb.to/get/play/' + md5hash
				except Exception as ex:
					print ex
	
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
				url1 = 'http://my-hit.org/film/18620/online/'
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
					
        except Exception as ex:
            print ex
            print 'sgparsed_link'

        return url