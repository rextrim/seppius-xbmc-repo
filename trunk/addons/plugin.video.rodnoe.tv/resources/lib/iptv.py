# Rodnoe.TV python class
# (c) Eugene Bond, 2010
# eugene.bond@gmail.com

import urllib2
import demjson
from md5 import md5
import datetime
import re, os, sys

__author__ = 'Eugene Bond <eugene.bond@gmail.com>'
__version__ = '1.4'

try:
	import xbmc, xbmcaddon
except ImportError:
	class xbmc_boo:
		
		def __init__(self):
			self.nonXBMC = True
		
		def output(self, data):
			print data
		
		def getInfoLabel(self, param):
			return '%s unknown' % param
	
	class xbmcaddon_foo:
		def __init__(self, id):
			self.id = id
		
		def getAddonInfo(self, param):
			if param == 'version':
				return __version__
			elif param == 'id':
				return self.id + ' by %s' % __author__
			else:
				return '%s unknown' % param
	
	class xbmcaddon_boo:
		def Addon(self, id = ''):
			if not id:
				id = os.path.basename(__file__)
			return xbmcaddon_foo(id)
	
	xbmc = xbmc_boo()
	xbmcaddon = xbmcaddon_boo()


#
# platform package usage disabled as
# cousing problems with x64 platforms
#
#try:
#	import platform
#except ImportError:
class platform_boo:
	
	def system(self):
		return os.name
	
	def release(self):
		plat = sys.platform
		return plat
			
	def python_version(self):
		ver = sys.version_info
		return '%s.%s.%s' % (ver[0], ver[1], ver[2])

platform = platform_boo()
	

RODNOE_API = 'http://file-teleport.com/iptv/api/json/%s'


class rodnoe:
	
	def __init__(self, login, password, addonid = '', SID = None, SID_NAME = None):
		
		if not addonid:
			addonid = os.path.basename(__file__)
		
		self.SID = SID
		self.SID_NAME = SID_NAME
		self.media_key = None
		self.login = login
		self.password = password
		self.uid = None
		self.to = None
		self.timeshift = 0
		self.addonid = addonid
		self.last_settings = None
		
		self.supported_settings = {'time_shift': {'name': 'time_shift', 'language_key': 34002, 'defined': [('0', '0'), ('60', '1'), ('120', '2'), ('180', '3'), ('240', '4'), ('300', '5'), ('360', '6'), ('420', '7'), ('480', '8'), ('540', '9'), ('600', '10'), ('660', '11'), ('720', '12')]}, 'time_zone': {'name': 'time_zone', 'language_key': 34003, 'defined': [('-720', '-12 GMT (New Zealand Standard Time)'), ('-660', '-11 GMT (Midway Islands Time)'), ('-600', '-10 GMT (Hawaii Standard Time)'), ('-540', '-9 GMT (Alaska Standard Time)'), ('-480', '-8 GMT (Pacific Standard Time)'), ('-420', '-7 GMT (Mountain Standard Time)'), ('-360', '-6 GMT (Central Standard Time)'), ('-300', '-5 GMT (Eastern Standard Time)'), ('-240', '-4 GMT (Puerto Rico and US Virgin Islands Time)'), ('-180', '-3 GMT (Argentina Standard Time)'), ('-120', '-2 GMT'), ('-60', '-1 GMT (Central African Time)'), ('0', '0 GMT (Greenwich Mean Time)'), ('60', '+1 GMT (European Central Time)'), ('120', '+2 GMT (Eastern European Time)'), ('180', '+3 GMT (Eastern African Time)'), ('240', '+4 GMT (Near East Time)'), ('300', '+5 GMT (Pakistan Lahore Time)'), ('360', '+6 GMT (Bangladesh Standard Time)'), ('420', '+7 GMT (Vietnam Standard Time)'), ('480', '+8 GMT (China Taiwan Time)'), ('540', '+9 GMT (Japan Standard Time)'), ('600', '+10 GMT (Australia Eastern Time)'), ('660', '+11 GMT (Solomon Standard Time)')]}}
		
	def _request(self, cmd, params, inauth = None):
		
		if self.SID == None:
			if inauth == None:
				self._auth(self.login, self.password)
		
		url = RODNOE_API % cmd
		url = url + '?' + params
		
		xbmc.output('[Rodnoe.TV] Requesting %s' % url);
		
		osname = '%s %s' % (platform.system(), platform.release())
		pyver = platform.python_version()
		
		__settings__ = xbmcaddon.Addon(self.addonid)
		
		isXBMC = 'XBMC'
		if getattr(xbmc, "nonXBMC", None) is not None:
			isXBMC = 'nonXBMC'
		
		ua = '%s v%s (%s %s [%s]; %s; python %s) as %s' % (__settings__.getAddonInfo('id'), __settings__.getAddonInfo('version'), isXBMC, xbmc.getInfoLabel('System.BuildVersion'), xbmc.getInfoLabel('System.ScreenMode'), osname, pyver, self.login)
		
		xbmc.output('[Rodnoe.TV] UA: %s' % ua)
		
		req = urllib2.Request(url, None, {'User-agent': ua, 'Connection': 'Close', 'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded'})
		
		if (self.SID != None):
			req.add_header("Cookie", self.SID_NAME + "=" + self.SID + ";")
		
		rez = urllib2.urlopen(req).read()
		
		xbmc.output('[Rodnoe.TV] Got %s' % rez)
		
		
		try:
			res = demjson.decode(rez)
		except:
			xbmc.output('[Rodnoe.TV] Error.. :(')
			
		xbmc.output('[Rodnoe.TV] Got JSON: %s' % res)
		
		self._errors_check(res)
		
		return res
	
	def _auth(self, user, password):
		
		md5pass = md5(md5(self.login).hexdigest() + md5(self.password).hexdigest()).hexdigest()
		
		response = self._request('login', 'login=%s&pass=%s' % (self.login, md5pass), 1)
		
		if response['sid']:
			self.media_key = response['media_key']
			self.SID = response['sid']
			self.SID_NAME = response['sid_name']
				
	def _errors_check(self, json):
		if 'error' in json:
			err = json['error']
			if 'message' in err:
				message = err['message']
				if message == None:
					message = err['code']
				xbmc.output('[Rodnoe.TV] ERROR: %s' % message.encode('utf8'))
				self.SID = None
	
	
	def testAuth(self):
		if self.SID:
			account = self._request('get_settings', '')
		if self.SID == None:
			self._auth(self.login, self.password)
		
		if self.SID != None:
			return True
		return False
	
	def getChannelsList(self):
		response = self._request('get_list_tv', '')
		res = []
		for group in response['groups']:
			for channel in group['channels']:
				icon = re.sub('%ICON%', channel['icon'], response['icons']['w40h30'])
				res.append({ 
					'title':	channel['name'],
					'id':		channel['id'],
					'icon':		icon,
					'info':		channel['epg_current_info'] or "",
					'subtitle':	channel['epg_current_title'] or "",
					'is_video':	('is_video' in channel) and (int(channel['is_video'])),
					'have_archive': ('has_archive' in channel) and (int(channel['has_archive'])),
					'have_epg':	True,
					'is_protected': ('protected' in channel) and (int(channel['protected'])),
					'source':	channel,
					'genre':	group['name'] or ""
				})
		
		return res
	
	def getEPG(self, chid, dt = None):
		if dt == None:
			dt = datetime.date.today().strftime('%Y%m%d')
		
		response = self._request('get_epg', 'cid=%s&day=%s' % (chid, dt))
		res = []
		for channel in response['channels']:
			for epg in channel['epg']:
				res.append({ 
					'title':		epg['title'],
					'time':			epg['begin'],
					'info':			epg['info'],
					'is_video':		0,
					'source':		epg
				})
		return res   
	
	def getCurrentInfo(self, chid):
		response = self._request('get_epg', 'cid=%s' % (chid))
		res = []
		
		for prg in response['channels']:
			for what in ('current', 'next'):
				res.append({ 
					'title':		prg[what]['title'],
					'time':			prg[what]['begin'],
					'info':			prg[what]['info'],
					'is_video':		0
				})
			
		return res
	
	def getStreamUrl(self, id, gmt = None, code = None): 
		if self.SID == None:
			self._auth(self.login, self.password)
		
		params = 'cid=%s' % id
		if gmt != None:
			params += '&lts=%s' % gmt
		
		if code != None:
			params += '&protect_code=%s' % code
		
		response = self._request('get_url_tv', params)
		if 'url' in response:
			return response['url']
	
	def getSettingCurrent(self, setting_name):
		setting = self.supported_settings[setting_name]
		if self.last_settings == None:
			self.last_settings = self._request('get_settings', '')
		
		if setting_name in self.last_settings:
			server_setting = self.last_settings[setting_name]
			
			oplist = []
			if 'defined' in setting:
				oplist = setting['defined']	
			elif 'list' in server_setting:
				for set in server_setting['list']:
					if 'lookup' in setting:
						oplist.append((str(set[setting['lookup']]), str(set[setting['display']])))
					else:
						oplist.append((str(set), str(set)))
		else:
			server_setting = 'Error'
			oplist = []
			
		return (server_setting, oplist)
	
	def setSettingCurrent(self, setting_name, setting_value):
		res = self._request('set', 'var=%s&val=%s' % (setting_name, setting_value))
	
	def getSettingsList(self):
		
		res = []
		for set in self.supported_settings:
			setting = self.supported_settings[set]
			value, options = self.getSettingCurrent(set)
			res.append({
				'name':			setting['name'],
				'language_key':	setting['language_key'],
				'value':		value,
				'options':		options
			})
		xbmc.output('[Rodnoe.TV] settings: %s' % res)
		return res

	
	
	def test(self):
		
		print(self.testAuth())
		
		channels = self.getChannelsList()    
		print(channels)   
		ch_url = self.getStreamUrl(102) 

		
			
if __name__ == '__main__':
	foo = rodnoe('demo', 'demo')
	foo.test()   
