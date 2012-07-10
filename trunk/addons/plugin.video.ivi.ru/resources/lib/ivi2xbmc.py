#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 	Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com
# 	Writer (c) 2012, Nevenkin A.V., E-mail: nuimons@gmail.com
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html
import platform
import urllib
import urllib2
import trans
import sys
import os
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import time
import random
from urllib import unquote, quote, quote_plus
try:
	from hashlib import md5
except:
	from md5 import md5

conf_file = xbmc.translatePath('special://temp/'+ 'settings.ivi.new')
adv_file = xbmc.translatePath('special://temp/'+ 'settings.ivi.adv')

Addon = xbmcaddon.Addon(id='plugin.video.ivi.ru')
language = Addon.getLocalizedString
addon_icon    = Addon.getAddonInfo('icon')
addon_fanart  = Addon.getAddonInfo('fanart')
addon_path    = Addon.getAddonInfo('path')
addon_type    = Addon.getAddonInfo('type')
addon_id      = Addon.getAddonInfo('id')
addon_author  = Addon.getAddonInfo('author')
addon_name    = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

hos = int(sys.argv[1])

def get_len():
	try:
		if Addon.getSetting("cnt_v") == '0': return 10
		if Addon.getSetting("cnt_v") == '1': return 25
		if Addon.getSetting("cnt_v") == '2': return 50
		if Addon.getSetting("cnt_v") == '3': return 75
		if Addon.getSetting("cnt_v") == '4': return 100
		return 50
	except: return 50
show_len=get_len()

xbmcplugin.setContent(hos, 'movies')

VERSION = '4.3as'
DOMAIN = '131896016'
GATrack='UA-30985824-1'

try:
	xbmcver=xbmc.getInfoLabel( "System.BuildVersion" ).replace(' ','_').replace(':','_')
	UA = 'XBMC/%s (%s; U; %s %s %s %s) %s/%s XBMC/%s'% (xbmcver,platform.system(),platform.system(),platform.release(), platform.version(), platform.machine(),addon_id,addon_version,xbmcver)
except:
	UA = 'XBMC/Unknown %s/%s/%s' % (urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))

if os.path.isfile(conf_file):
	try:
		f = open(conf_file, 'r')
		GAcookie=f.readline()
		uniq_id=f.readline()
		f.close()
	except:
		f = open(conf_file, 'w')
		GAcookie ="__utma%3D"+DOMAIN+"."+str(random.randint(0, 0x7fffffff))+"."+str(random.randint(0, 0x7fffffff))+"."+str(int(time.time()))+"."+str(int(time.time()))+".1%3B"
		uniq_id=random.random()*time.time()
		f.write(GAcookie)
		f.write('\n')
		f.write(str(uniq_id))
		f.close()
else:
	f = open(conf_file, 'w')
	GAcookie ="__utma%3D"+DOMAIN+"."+str(random.randint(0, 0x7fffffff))+"."+str(random.randint(0, 0x7fffffff))+"."+str(int(time.time()))+"."+str(int(time.time()))+".1%3B"
	uniq_id=random.random()*time.time()
	f.write(GAcookie)
	f.write('\n')
	f.write(str(uniq_id))
	f.close()

genres_data = []
genres_dat_file = os.path.join(addon_path, 'genres.dat')
if os.path.isfile(genres_dat_file):
	try:
		gdf = open(genres_dat_file, 'r')
		genres_data = json.loads(gdf.read())
		gdf.close()
	except: pass

def send_request_to_google_analytics(utm_url, ua):

	try:

		req = urllib2.Request(utm_url, None, {'User-Agent':UA} )
		response = urllib2.urlopen(req).read()
		#print utm_url

	except:
		ShowMessage('ivi.ru', "GA fail: %s" % utm_url, 2000)
	return response

def track_page_view(path,nevent='', tevent='',UATRACK='UA-11561457-31'):
	#print GAcookie
	domain = DOMAIN
	document_path = unquote(path)
	utm_gif_location = "http://www.google-analytics.com/__utm.gif"
	extra = {}
	extra['screen'] = xbmc.getInfoLabel('System.ScreenMode')

	md5String = md5(str(uniq_id)).hexdigest()
	gvid="0x" + md5String[:16]
	utm_url = utm_gif_location + "?" + \
		"utmwv=" + VERSION + \
		"&utmn=" + get_random_number() + \
		"&utmsr=" + quote(extra.get("screen", "")) + \
		"&utmt=" + nevent + \
		"&utme=" + tevent +\
		"&utmhn=localhost" + \
		"&utmr=" + quote('-') + \
		"&utmp=" + quote(document_path) + \
		"&utmac=" + UATRACK + \
		"&utmvid=" + gvid + \
		"&utmcc="+ GAcookie

	return send_request_to_google_analytics(utm_url, UA)

try:
	import json
except ImportError:
	try:
		import simplejson as json
		xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
	except ImportError:
		try:
			import demjson3 as json
			xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
		except ImportError:
			xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

def get_random_number():
	return str(random.randint(0, 0x7fffffff))

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def ShowMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: ShowMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: ShowMessage: exec failed [%s]' % (addon_id, e), 3 )

def GET(target, post=None):
	try:
		req = urllib2.Request(url = target, data = post, headers = {'User-Agent':UA})
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		ShowMessage('HTTP ERROR', e, 5000)

def genre2name(gid):
	gdf = open(genres_dat_file, 'r')
	genres_data = json.loads(gdf.read())
	gdf.close()
	try:
		for n in genres_data:
			#print n
			if int(n.split(';')[0]) == (gid):
				reti=n.split(';')[1]
				#showMessage('Genre', reti, 2000)
		return reti
	except: return None

class ivi_player(xbmc.Player):

	def __init__( self, *args, **kwargs ):
		self.init()
		
	def init(self):
		self.active = True
		self.api_url = 'http://api.digitalaccess.ru/api/json/'
		self.log_url = 'http://api.digitalaccess.ru'
		self.sID='s15'
		self.vID=None
		ShowMessage('ivi.ru player',language(30010), 2000)
		self.content_file=None
		self.ads_file=None
		self.state='pre_roll'
		self.started=None
		self.started = False
		self.Time = 0.0
		self.TotalTime = 0.0
		self.percent = 0
		self.resume_timer=0.0
		self.playlist = []
		self.playl=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		self.playl.clear()
		self.pos=[]
		self.ads=[]
		self.title=''
		self.tns_id=None
		self.GA_id=None

		self.watchid=None
		self.advwatchid=None
		self.lastad=None
		self.start_timer=None
		self.preroll_end=None
		self.pre=None
		self.adstart_timer=None
		self.svideo_timer=None
		self.content_start=None
		self.paused=None
		self.min=0
		self.vstopped=None
		
	def POSTAPI(self, post):
		req = urllib2.Request(self.api_url)
		req.add_header('User-Agent', UA)
		f = urllib2.urlopen(req, json.dumps(post))
		js = json.loads(f.read())
		f.close()
		try:
			e_m = js['error']
			ShowMessage('ERROR %s SERVER %s' % (e_m['code'], js['server_name']), e_m['message'], times = 15000, pics = addon_icon)
			return None
		except:
			return js

	def getAds(self):
		advtimer=int(time.time())-int(self.lastad)
		json1 = self.POSTAPI({'method':'da.adv.get', 'params':[self.vID, {'contentid':self.vID,'site':self.sID, 'watchid':self.watchid, 'last_adv':advtimer, 'uid':uniq_id} ]})
		if json1:
			try:
				for ad in json1['result']:
					ad_file = self.find_best(ad)
					if ad_file:
						adrow = {'url': ad_file, 'id': ad['id'], 'title': ad['title'].encode('utf-8'), 'px_audit': ad['px_audit'],
						'duration': ad['duration'], 'percent_to_mark': int(ad['percent_to_mark'])-1, 'save_show': ad['save_show']}
						if ad['type'] == 'preroll': self.preroll_params.append(adrow)
						elif ad['type'] == 'postroll': self.postroll_params.append(adrow)
						elif ad['type'] == 'midroll':self.midroll_params.append(adrow)
			except:
				pass

	def report_ads(self, curr_ads):
		json1 = self.POSTAPI({'method':'da.adv.watched', 'params':[self.vID, curr_ads[0]['id'], {'contentid':self.vID,'site':self.sID, 'watchid':str(self.watchid),'advid':curr_ads[0]['id'],'uid':uniq_id, "advwatchid":str(self.advwatchid)} ]})
		links= curr_ads[0]['px_audit']

		f = open(adv_file, 'w')
		last_ad=str(int(time.time()))
		f.write(last_ad)
		f.close()
		self.lastad=last_ad
		if links:
			if len(links)<8:
				for n in links:
					GET(n)
			else: GET(links)

	def sendstat(self,path,post):
		post=urllib.urlencode(post).replace('.','%2E').replace('_','%5F')
		#print post
		req = urllib2.Request(path,post)
		req.add_header('Accept', 'text/plain')
		req.add_header('Content-Type','application/x-www-form-urlencoded')
		f = urllib2.urlopen(req)
		js = f.read()
	def getparam(self, vID):
		self.playl.clear()
		self.preroll_params = []
		self.postroll_params = []
		self.midroll_params = []
		self.midroll = []
		http = GET('http://www.ivi.ru/mobileapi/videoinfo/?id=%s' % self.vID)
		if http:
			data = get_video_data(json.loads(http))
			if data:
				self.PosterImage = data['image']
				self.main_item = xbmcgui.ListItem(data['title'], iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
				json0 = self.POSTAPI({'method':'da.content.get', 'params':[self.vID, {'contentid':self.vID,'watchid':self.watchid,'site':self.sID, 'uid':uniq_id} ]})
				vc = json0['result']
				self.content_file = self.find_best(vc)
				try:    self.content_percent_to_mark = int(vc['percent_to_mark'])
				except: self.content_percent_to_mark = 0
				try:    self.GA_id = int(vc['google_analytics_id'])
				except: self.GA_id = None
				try:    self.tns_id = int(vc['tns_id'])
				except: self.tns_id = None
				self.title=vc['title']
				try:    self.credits_begin_time = int(vc['credits_begin_time'])
				except: self.credits_begin_time = -1
				if self.credits_begin_time==0: self.credits_begin_time=-1
				try:    self.midroll = vc['midroll']
				except: self.midroll = []
				self.getAds()
				if self.preroll_params and len(self.preroll_params):
					self.ads_file = (self.preroll_params[0]['url'])
					self.send_ads=self.preroll_params
				else:
					self.state='play'

	def find_best(self, data):
		play_file = None
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'MP4-hi': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'FLV-hi': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'MP4-lo': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'FLV-lo': play_file = vcfl['url']
		return play_file

	def ivi_play(self, vID):
		track_page_view('','event','5(Video*Videostart)')
		track_page_view('','event','5(Video*Videostart)',UATRACK=GATrack)
		self.vID=vID
		ind=1
		assert not self.isPlaying(), 'Player is already playing a video'
		self.getparam(vID)
		i = xbmcgui.ListItem(self.title, iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
		iad = xbmcgui.ListItem(language(30011), iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
		if self.state=='pre_roll':
			self.playl.add(self.ads_file,iad)
			self.ads.append({
				'type':'preroll',
				'ind':ind,
				'time':-1
			})
			ind=ind+1
			self.cont_ind=1

		else: self.cont_ind=0
		self.playl.add(self.content_file,listitem=i)

		for na in self.midroll:
			try:
				self.ads.append({
					'type':'play_mid',
					'ind':ind,
					'time':na})
				ind=ind+1
				self.playl.add(self.midroll_params[0]['url'],iad)
			except: pass

		try:
			if len(self.postroll_params)>0:
				self.ads.append({
					'type':'postroll',
					'ind':ind,
					'time':self.credits_begin_time
				})
				self.playl.add(self.postroll_params[0]['url'],iad)
				self.post_r=ind
				self.playl.add(self.content_file,listitem=i)
		except: pass
		
		json1 = self.POSTAPI({'params':[self.vID, {'contentid':self.vID,'site':self.sID, 'watchid':self.watchid ,'uid':uniq_id} ],'method':'da.content.watched' })
		self.play(self.playl)

	def myloop(self):
		self.last_ads_time=0
		self.send_ads=None
		while self.active:

			try:
				self.Time = int(self.getTime())
				self.TotalTime = self.getTotalTime()
				self.percent = (100 * self.Time) / self.TotalTime
			except:
				pass

			if not self.paused:
				if self.state=='play' and self.content_start:
					seconds=int(time.time()-self.content_start)
					if seconds<=60:
						if self.state=='play' and self.content_start:
							self.sendstat('http://api.digitalaccess.ru/logger/content/time/',{'contentid':self.vID,'watchid':self.watchid,'fromstart':int(self.Time),'seconds':seconds})
					if seconds>=60: self.min=self.min+1
					if self.min>=60:
						if self.state=='play' and self.content_start:
							self.sendstat('http://api.digitalaccess.ru/logger/content/time/',{'contentid':self.vID,'watchid':self.watchid,'fromstart':int(self.Time),'seconds':seconds})
							self.min=0


				if self.state=='pre_roll' and self.adstart_timer:
					self.sendstat('http://api.digitalaccess.ru/logger/adv/time/',{'watchid':quote(self.watchid),'advwatchid':quote(self.advwatchid),'seconds':int(time.time()-self.adstart_timer)})
					
			if self.percent==self.content_percent_to_mark and self.state=='play':
				self.content_percent_to_mark=-1
				pass
			for m in self.ads:
				if self.send_ads:
					self.report_ads(self.send_ads)
					self.send_ads=None
				if int(self.Time)==m['time'] and int(self.Time)!=self.last_ads_time and self.state=='play':

					if self.state=='play':
						if len(self.midroll_params)>0:
							self.last_ads_time=int(self.Time)
							self.state=m['type']
							self.playselected(m['ind'])
							self.showed_ad=False
							self.resume_timer=self.Time
					else:
						pass

			self.sleep(1000)


	def onPlayBackPaused( self ):
		self.paused=1
		ShowMessage('ivi.ru player', language(30012), 2000)

	def onPlayBackResumed( self ):
		self.paused=None
		ShowMessage('ivi.ru player', language(30013), 2000)

	def onPlayBackStarted( self ):
		if self.started and self.state=='pre_roll':
			self.preroll_end=time.time()
			self.state='play'
		self.paused=None
		long_time=time.time()-self.start_timer
		if self.state=='play':
			#self.min=0
			if self.preroll_end:
					self.sendstat('http://api.digitalaccess.ru/logger/mediainfo/speed/',{'watchid':self.watchid,'speed':time.time()-self.preroll_end})
					self.content_start=time.time()
					self.pre=1
					self.preroll_end=None
			elif not self.pre:
				self.sendstat('http://api.digitalaccess.ru/logger/mediainfo/speed/',{'watchid':self.watchid,'speed':time.time()-self.preroll_end})
				self.content_start=time.time()
				self.preroll_end=None
			if self.resume_timer>0:
				self.seekTime(self.resume_timer)
			self.svideo_timer=time.time()
		if self.state=='pre_roll' and not self.started:
			self.pre=1
			self.advwatchid='%s_%s'%(self.preroll_params[0]['id'],str(int(time.time()*1000)))
			self.send_ads=self.preroll_params
			self.showed_ad=True
			self.adstart_timer=time.time()
			self.started=1
		if self.state=='postroll':
			self.send_ads=self.postroll_params
			self.showed_ad=True
			self.adstart_timer=time.time()
		if self.state=='play_mid':
			self.showed_ad=True
			self.send_ads=self.midroll_params
			self.adstart_timer=time.time()
	def onPlayBackEnded( self ):
		
		if self.state=='play':
			if self.credits_begin_time <= 0 and len(self.postroll_params)>0:
				self.state='postroll'
			else: 
				self.stop()
				self.playl.clear()
				self.active = False

		if self.state=='pre_roll':
			self.preroll_end=time.time()
			self.playselected(self.cont_ind)
			self.state='play'

		if self.state=='postroll':
			if self.credits_begin_time <= 0:
				self.stop()
				self.playl.clear()
				self.active = False
			else:
				self.playselected(self.cont_ind)
				self.state='play'

		if self.state=='play_mid':
			self.playselected(self.cont_ind)
			self.state='play'

	def onPlayBackStopped( self ):
		self.active = False
		self.vstopped = 1
		self.playl.clear()
	def sleep(self, s):
		xbmc.sleep(s)



def main_screen(params):

	li = xbmcgui.ListItem(language(30014), iconImage = addon_icon, thumbnailImage = addon_icon)
	uri = construct_request({
		'func': 'promo',
		'url': 'http://www.ivi.ru/mobileapi/promo/v2/?%s'
	})
	li.setProperty('fanart_image', addon_fanart)
	xbmcplugin.addDirectoryItem(hos, uri, li, True)

	http = GET('http://www.ivi.ru/mobileapi/categories/')
	jsdata = json.loads(http)
	for categoryes in jsdata:
		li = xbmcgui.ListItem(categoryes['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
		li.setProperty('fanart_image', addon_fanart)
		uri = construct_request({
			'func': 'read_category',
			'category': categoryes['id']
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
		for genre in categoryes['genres']:
			genres_data.append(str(genre['id'])+';'+genre['title'])
	gf = open(genres_dat_file, 'w')
	gf.write(json.dumps(genres_data))
	gf.close()

	li = xbmcgui.ListItem(language(30015), iconImage = addon_icon, thumbnailImage = addon_icon)
	li.setProperty('fanart_image', addon_fanart)
	uri = construct_request({
		'func': 'run_search'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
	li = xbmcgui.ListItem(language(30030), iconImage = addon_icon, thumbnailImage = addon_icon)
	li.setProperty('fanart_image', addon_fanart)
	uri = construct_request({
		'func': 'run_settings'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, False)
	
	xbmcplugin.endOfDirectory(hos)

def run_settings(params):
	Addon.openSettings()
	
def read_category(params):
	show_len=get_len()
	categ=params['category']
	if categ=='14':
		track_page_view('movies')
		track_page_view('movies',UATRACK=GATrack)
	if categ=='15':
		track_page_view('series')
		track_page_view('series',UATRACK=GATrack)
	if categ=='16':
		track_page_view('shows')
		track_page_view('shows',UATRACK=GATrack)
	if categ=='17':
		track_page_view('animation')
		track_page_view('animation',UATRACK=GATrack)
	http = GET('http://www.ivi.ru/mobileapi/categories/')
	jsdata = json.loads(http)
	for categoryes in jsdata:
		if categoryes['id']==int(params['category']):
			li = xbmcgui.ListItem(language(30016), iconImage = addon_icon, thumbnailImage = addon_icon)
			li.setProperty('fanart_image', addon_fanart)
			uri = construct_request({
				'func': 'run_search',
				'category': categoryes['id']
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
			li = xbmcgui.ListItem(language(30017), iconImage = addon_icon, thumbnailImage = addon_icon)
			li.setProperty('fanart_image', addon_fanart)
			uri = construct_request({
				'func': 'read_dir',
				'category': categoryes['id'],
				'sort':'new',
				'from':0,
				'to':show_len-1

			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
			li = xbmcgui.ListItem(language(30018), iconImage = addon_icon, thumbnailImage = addon_icon)
			li.setProperty('fanart_image', addon_fanart)
			uri = construct_request({
				'func': 'read_dir',
				'category': categoryes['id'],
				'sort':'pop',
				'from':0,
				'to':show_len-1
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
			for genre in categoryes['genres']:
				li = xbmcgui.ListItem(genre['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
				li.setProperty('fanart_image', addon_fanart)
				uri = construct_request({
					'func': 'read_dir',
					'genre': genre['id'],
					'sorted':1,
					'from':0,
					'to':show_len-1
				})
				xbmcplugin.addDirectoryItem(hos, uri, li, True)

	xbmcplugin.endOfDirectory(hos)

def read_dir(params):
	try:
		target = params['url']
		del params['url']
	except: target = 'http://www.ivi.ru/mobileapi/catalogue/v2/?%s'
	try:
		list = params['list']
		del params['list']
	except: list=None
	try:
		if params['sorted']:
			params['sort'] = get_sort()
			params['sorted'] =None
	except: pass
	http = GET(target % urllib.urlencode(params))
	if http == None:
		ShowMessage('Error', 'Cant received data', 2000)
		return False

	jsdata = json.loads(http)
	cnt=0
	v_list=''
	if list:
		for video_ind in jsdata:
			vdata=get_video_data(video_ind)
			if int(vdata['seasons_cnt'])==-1:
				v_list=v_list+str(vdata['id'])+';'
	for video_ind in jsdata:
		vdata=get_video_data(video_ind)
		li = xbmcgui.ListItem(vdata['title'], iconImage = vdata['image'], thumbnailImage = vdata['image'])
		li.setProperty('fanart_image', addon_fanart)
		try: li.setInfo(type='video', infoLabels = vdata['info'])
		except: pass
		if int(vdata['seasons_cnt'])==-1:
			uri = construct_request({
				'func': 'playid',
				'id':vdata['id'],
				'playlist':v_list
			})
			cnt=cnt+1
			xbmcplugin.addDirectoryItem(hos, uri, li, False)
		if int(vdata['seasons_cnt'])==0 or int(vdata['seasons_cnt'])==1:
			uri = construct_request({
				'func': 'read_dir',
				'id':vdata['id'],
				'url': 'http://www.ivi.ru/mobileapi/videofromcompilation/?%s',
				'sorted':1,
				'from':0,
				'list':'list',
				'to':show_len-1
			})
			cnt=cnt+1
			li.setProperty('fanart_image', addon_fanart)
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
		if int(vdata['seasons_cnt'])>1:
			uri = construct_request({
				'func': 'getser',
				'id':vdata['id'],
				'seasons_cnt':vdata['seasons_cnt']
			})
			cnt=cnt+1
			li.setProperty('fanart_image', addon_fanart)
			xbmcplugin.addDirectoryItem(hos, uri, li, True)

	if cnt >= int(show_len):
		li = xbmcgui.ListItem(language(30019), iconImage = addon_icon, thumbnailImage = addon_icon)
		li.setProperty('fanart_image', addon_fanart)
		params['url']=target
		params['func'] = 'read_dir'
		params['from'] = int(params['from'])+int(show_len)
		params['to'] = int(params['from']) + int(show_len)
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)
	


def playid(params):
	v_list=[]
	try:
		v_list = params['playlist']
		m_list=v_list.split(';')
		del params['playlist']
		pl_from=int(m_list.index(params['id']))
		pl_to=int(len(m_list)-1)
		sm_list=m_list[pl_from:pl_to]
	except: m_list=None
	
	if m_list:
		iviplay=ivi_player()
		iviplay.init()
		for id in sm_list:
			
			if not iviplay.vstopped:
				try:
					f = open(adv_file, 'r')
					last_ad=f.readline()

				except:
					f = open(adv_file, 'w')
					last_ad=str(int(time.time()))
					f.write(last_ad)
					f.close()
				iviplay.init()
				iviplay.lastad=last_ad
				iviplay.start_timer=time.time()
				iviplay.watchid='%s_%s_%s'%(id,uniq_id,str(int(time.time()*1000)))
				iviplay.ivi_play(id)
				iviplay.myloop()
				while iviplay.active:
					xbmc.sleep(1000)
				iviplay.stop
				xbmc.sleep(1000)
	else:
		try:
			f = open(adv_file, 'r')
			last_ad=f.readline()

		except:
			f = open(adv_file, 'w')
			last_ad=str(int(time.time()))
			f.write(last_ad)
			f.close()
	
		iviplay=ivi_player()
		iviplay.lastad=last_ad
		iviplay.start_timer=time.time()
		iviplay.watchid='%s_%s_%s'%(params['id'],uniq_id,str(int(time.time()*1000)))
		iviplay.ivi_play(params['id'])
		iviplay.myloop()
		iviplay.stop

def getser(params):
	params['to']=999
	target='http://www.ivi.ru/mobileapi/videofromcompilation/?%s'
	http = GET(target % urllib.urlencode(params))
	total=json.loads(http)
	v_id = int(params['id'])
	seasons=[]
	for episode in total:
		if episode['season'] not in seasons:
			seasons.append(episode['season'])
	seasons.sort()	
	for ind in seasons:	
		i = xbmcgui.ListItem(language(30020) % ind, iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		osp = {'func':'read_dir', 'id': v_id, 'url': 'http://www.ivi.ru/mobileapi/videofromcompilation/?%s', 'season':ind,'from':0,'to':show_len-1,'list':'list'}
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode(osp))
		i.setInfo(type = 'video', infoLabels = {'season': ind})
		xbmcplugin.addDirectoryItem(hos, uri, i, True)
	xbmcplugin.endOfDirectory(hos)


def get_video_data(video):
	mysetInfo={}
	try: title=video['title']
	except: title=None
	try: duration=video['duration']
	except: duration=None
	try: id=video['id']
	except: id=None
	try: seasons_cnt = video['seasons_count']
	except: seasons_cnt = -1
	try: images=video['thumbnails']
	except: images=None
	try: season=video['season']
	except: season=None
	try: episode=video['episode']
	except: episode=None
	try: genre=video['genres']
	except: genre=None
	try:    
		mysetInfo['plot'] = video['descrtiption']
		mysetInfo['plotoutline'] = video['descrtiption']
	except: pass
	try:    
		mysetInfo['year'] = int(video['years'][0])
	except: pass
	try:    
		v_ivi_rating = video['ivi_rating'] 
		mysetInfo['rating'] = float(v_ivi_rating*2)
	except: v_ivi_rating = None
	if not v_ivi_rating:
		try:    
			v_ivi_rating = video['ivi_rating_10']
			mysetInfo['rating'] = float(v_ivi_rating)
		except: v_ivi_rating = None
	try:    
		mysetInfo['duration'] = v_duration
	except: pass
	lth = 0
	ltw = 0
	ltu = addon_icon


	try:
		for thumbnail in images:
			if int(thumbnail['height']) >= lth:
				ltu = thumbnail['path']
				lth = int(thumbnail['height'])
				ltw = int(thumbnail['width'])
	except:

		try: ltu = images[1]['path']
		except: pass
		try: ltu = images[0]['path']
		except: pass
		pass
	genres=None
	glist = []
	if genre:
		for gid in genre:
			g_name = genre2name(gid)

			if g_name:
				try: glist.index(g_name)
				except: glist.append(g_name)
		if len(glist):
			mysetInfo['genre'] = ', '.join(glist)

	export={'id':id,'title':title, 'duration':duration, 'seasons_cnt':seasons_cnt, 'image':ltu, 'info':mysetInfo}
	return export

def promo(params): 					# показ промо контента
	track_page_view('promo')
	track_page_view('promo',UATRACK=GATrack)
	http = GET('http://www.ivi.ru/mobileapi/promo/')
	if http == None: return False
	jsdata = json.loads(http)
	if jsdata:
		for video in jsdata:
			li = xbmcgui.ListItem(video['title'], thumbnailImage=video['img_wp7']['path'])
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'playid', 'id': video['content_id']}))
			li.setProperty('fanart_image', addon_fanart)
			li.setInfo('video',{'plot': video['text']})
			xbmcplugin.addDirectoryItem(hos, uri, li, False)
		xbmcplugin.endOfDirectory(hos)

def run_search(params):				# Поиск
	track_page_view('search')
	track_page_view('search',UATRACK=GATrack)
	kbd = xbmc.Keyboard()
	kbd.setDefault('')
	kbd.setHeading(language(30021))
	kbd.doModal()
	out=''
	if kbd.isConfirmed():
		try:
			out = trans.detranslify(kbd.getText())
			out=out.encode("utf-8")
		except:
			out = kbd.getText()

	params['query'] = out
	params['url'] = 'http://www.ivi.ru/mobileapi/search/v2/?%s'
	read_dir(params)

def get_sort():

	if __addon__.getSetting("sort_v") == '1': return 'pop'
	else: return 'new'

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
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param


def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
		del params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		main_screen(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			ShowMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
#stop