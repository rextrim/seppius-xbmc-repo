import sys
import urllib2
import urllib
import os
import re
import json
from datetime import datetime
from time import time
from time import sleep
from net import Net
import jsunpack
class Base36:

    def __init__(self, ls = False):
        self.ls = False
        if ls:
            self.ls = ls



    def base36encode(self, number, alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        """Converts an integer to a base36 string."""
        if not isinstance(number, (int, long)):
            raise TypeError('number must be an integer')
        base36 = ''
        sign = ''
        if number < 0:
            sign = '-'
            number = -number
        if 0 <= number < len(alphabet):
            return sign + alphabet[number]
        while number != 0:
            (number, i,) = divmod(number, len(alphabet))
            base36 = alphabet[i] + base36

        return sign + base36



    def base36decode(self, number):
        return int(number, 36)



    def param36decode(self, match_object):
        if self.ls:
            param = int(match_object.group(0), 36)
            return str(self.ls[param])
        else:
            return False

def unpack_js(p, k):
    """emulate js unpacking code"""
    k = k.split('|')
    for x in range(len(k) - 1, -1, -1):
        if k[x]:
            p = re.sub('\\b%s\\b' % Base36().base36encode(x), k[x], p)

    return p			
			
def exec_javascript(lsParam):
        return re.sub('[a-zA-Z0-9]+', Base36(lsParam[3]).param36decode, str(lsParam[0]))
		
def debug(obj, text = ''):
    print datetime.fromtimestamp(time()).strftime('[%H:%M:%S]')
    print '%s' % text + ' %s\n' % obj

def mod_request(url, param = None):
    try:
        debug(url, 'MODUL REQUEST URL')
        req = urllib2.Request(url, param, {'User-agent': 'QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1 Service Pack 3)'})
        html = urllib2.urlopen(req).read()
    except Exception as ex:
        print ex
        print 'REQUEST Exception'

    return html

class europe_parsers:
	def __init__(self):
		self.quality = ''
		self.net = Net()
	
	def get_parsed_link(self, url):
		try:
			if url.find('nowvideo.sx') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
				'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					key = re.compile('flashvars.filekey=(.+?);').findall(page)
					ip_key = key[0]
					pattern = 'var %s="(.+?)".+?flashvars.file="(.+?)"' % str(ip_key)
					r = re.search(pattern, page, re.DOTALL)
					if r:
						(filekey, filename,) = r.groups()
					else:
						print "errrrroor nowvideo"
					api = 'http://www.nowvideo.sx/api/player.api.php?key=%s&file=%s' % (filekey, filename)
					request2 = urllib2.Request(api, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
					'Connection': 'Close'})
					try:
						html = urllib2.urlopen(request2).read()
						code = re.findall('url=(.*?)&title', html)
						code = code[0]
						if len(code) > 0:
							url = code
					except:
						print "nowvideo api error"
				except Exception as ex:
					print ex
			if url.find('movshare.net') > -1:
				page = mod_request(url)
				r = re.search('<param name="src" value="(.+?)"', page)
				if not r:
					key = re.compile('flashvars.filekey=".*?-(.+?)";').findall(page)
					filekey = key[0]
					key2 = re.compile('flashvars.file="(.*?)";').findall(page)
					media_id = key2[0]
					api = 'http://www.movshare.net/api/player.api.php?key=%s&file=%s' % (filekey, media_id)
					try:
						html = mod_request(api)
						r = re.search('url=(.+?)&title', html)
					except:
						print "movshare errorrrrrrrrr"
				if r:
					stream_url = r.group(1)
				url = stream_url
			if url.find('videoweed.es') > -1:
				page = mod_request(url)
				key = re.compile('flashvars.filekey=".*?-(.+?)";').findall(page)
				filekey = key[0]
				key2 = re.compile('flashvars.file="(.*?)";').findall(page)
				media_id = key2[0]
				api_call = ('http://www.videoweed.es/api/player.api.php?user=undefined&codes=1&file=%s' + '&pass=undefined&key=%s') % (media_id, filekey)
				try:
					html = mod_request(api_call)
					r = re.search('url=(.+?)&title', html)
				except:
					print "videoweed errorrrrrrrrr"
				if r:
					stream_url = r.group(1)
				url = stream_url
			if url.find('novamov.com') > -1:
				page = mod_request(url)
				key = re.compile('flashvars.filekey=".*?-(.+?)";').findall(page)
				filekey = key[0]
				key2 = re.compile('flashvars.file="(.*?)";').findall(page)
				media_id = key2[0]
				api = 'http://www.novamov.com/api/player.api.php?key=%s&file=%s' % (filekey, media_id)
				try:
					html = mod_request(api)
					r = re.search('url=(.+?)&title', html)
				except:
					print "novamov errorrrrrrrrr"
				if r:
					stream_url = r.group(1)
				url = stream_url
			if url.find('divxstage.to') > -1:
				page = mod_request(url)
				key = re.compile('flashvars.filekey=".*?-(.+?)";').findall(page)
				filekey = key[0]
				key2 = re.compile('flashvars.file="(.*?)";').findall(page)
				media_id = key2[0]
				api = 'http://www.divxstage.eu/api/player.api.php?user=undefined&key=' + filekey + '&pass=undefined&codes=1&file=' + media_id
				try:
					html = mod_request(api)
					r = re.search('url=(.+?)&title', html)
				except:
					print "divxstage errorrrrrrrrr"
				if r:
					stream_url = r.group(1)
				url = stream_url
			if url.find('youwatch.org') > -1:
				url = url.replace('.org/','.org/embed-')
				url = url + '.html'
				soup = mod_request(url)
				html = soup.decode('utf-8')
				jscript = re.findall('function\\(p,a,c,k,e,d\\).*return p\\}(.*)\\)', html)
				if jscript:
					lsParam = eval(jscript[0].encode('utf-8'))
					flashvars = exec_javascript(lsParam)
					r = re.findall('file:"(.*)",provider', flashvars)
					if r:
						stream_url = r[0].encode('utf-8')
				url = stream_url
			if url.find('vodlocker.com') > -1:
				post_url = url
				resp = self.net.http_GET(url)
				html = resp.content
				data = {}
				r = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)">', html)
				data['usr_login']=''
				for name, value in r: 
					data[name] = value
				data['imhuman']='Proceed to video'
				data['btn_download']='Proceed to video'
				sleep(20)
				html = self.net.http_POST(post_url, data).content
				r = re.search('file\s*:\s*"(http://.+?)"', html)
				if r:
					stream_url = str(r.group(1))
				url = stream_url
			if url.find('vidto.me') > -1:
				print '39'
				print url
				html = self.net.http_GET(url).content
				#common.addon.show_countdown(6, title='Vidto', text='Loading Video...')
				#import time
				sleep(6)
				data = {}
				r = re.findall('type="(?:hidden|submit)?" name="(.+?)"\\s* value="?(.+?)">', html)
				for (name, value,) in r:
					data[name] = value
	
				html = self.net.http_POST(url, data).content
				r = re.search('<a id="lnk_download" href="(.+?)"', html)
				if r:
					r = re.sub(' ', '%20', r.group(1))
					url2 = r
				url = url2
			if url.find('sharevid.org') > -1:
				html = self.net.http_GET(url).content
				data = {}
				r = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)">', html)
				for name, value in r:
					data[name] = value
				html = self.net.http_POST(url, data).content
				r = re.search("file\s*:\s*'(.+?)'", html)
				if r:
					url2 = r.group(1)
				url = url2
			if url.find('sharerepo.com') > -1:
				request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
					'Connection': 'Close'})
				try:
					page = urllib2.urlopen(request).read()
					code = re.findall("var lnk1 = '(.*?)';", page)
					if len(code) > 0:
						md5hash = code[0]
						url = md5hash
				except Exception as ex:
					print ex
			if url.find('allmyvideos.net') > -1:
				html = self.net.http_GET(url).content
				data = {}
				r = re.findall('type="hidden" name="(.+?)"\\s* value="?(.+?)">', html)
				for (name, value,) in r:
					data[name] = value
	
				html = self.net.http_POST(url, data).content
				r = re.search('"sources"\\s*:\\s*.\n*\\s*.\n*\\s*"file"\\s*:\\s*"(.+?)"', html)
				if r:
					url = r.group(1)
			if url.find('played.to') > -1:
				web_url = url
				html = self.net.http_GET(web_url, {'host': 'played.to'}).content
				id = re.compile('<input type="hidden" name="id" value="(.+?)">').findall(html)[0]
				fname = re.compile('<input type="hidden" name="fname" value="(.+?)">').findall(html)[0]
				hash = re.compile('<input type="hidden" name="hash" value="(.+?)">').findall(html)[0]
				data = {'op': 'download1',
				'usr_login': '',
				'id': id,
				'fname': fname,
				'referer': '',
				'hash': hash,
				'imhuman': 'Continue+to+Video'}
				html = self.net.http_POST(web_url, data).content
				played = re.compile('file: "(.+?)"').findall(html)
				url = played[0]
			if url.find('gorillavid.in') > -1:
				web_url = url
				resp = self.net.http_GET(web_url)
				html = resp.content
				r = re.findall('<title>404 - Not Found</title>', html)
				if r:
					print 'File Not Found or removed'
				#post_url = resp.get_url()
				form_values = {}
				for i in re.finditer('<input type="hidden" name="(.+?)" value="(.+?)">', html):
					form_values[i.group(1)] = i.group(2)
	
				html = self.net.http_POST(web_url, form_data=form_values).content
				r = re.search('file: "(.+?)"', html)
				if r:
					url = r.group(1)
		except Exception as ex:
			print ex
			print 'sgparsed_international_link'	
			
		return url