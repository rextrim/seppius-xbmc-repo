import sqlite3 as db
import urllib2
import xbmc
import threading
import datetime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import re
import xbmcaddon
import time
import os
import sys


def GET(target, post=None, cookie = ""):
	pass
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		if cookie != "":
			req.add_header('Cookie', cookie)
			
		resp = urllib2.urlopen(req)
			
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( 'GET EXCEPT [%s]' % (e), 4 )

class _DBThread(threading.Thread):
	def _com_received(self,text):
		pass

	def __init__(self,func, params):
		threading.Thread.__init__(self)
		self.daemon = True
		self.func = func
		self.params = params
	def run(self):
		self.func(self.params)
		
class DataBase:
	def __init__( self, db_name, cookie ):
		self.db_name = db_name
		self.cookie = cookie
		self.connection = 0
		self.cursor = 0
		self.last_error = 0
		__addon__ = xbmcaddon.Addon( id = 'plugin.video.torrent.tv' )
		_ADDON_PATH =   xbmc.translatePath(__addon__.getAddonInfo('path'))
		if (sys.platform == 'win32') or (sys.platform == 'win64'):
			_ADDON_PATH = _ADDON_PATH.decode('utf-8')
		if not os.path.exists(db_name):
			fsql = open(os.path.join(_ADDON_PATH, 'resources/tvbase.sql'), 'r')
			ssql = fsql.read()
			ssql = ssql.split('----')
			fsql.close()
			con = db.connect(database=db_name)
			cur = con.cursor()
			for st in ssql:
				cur.execute(st)
			con.commit()
			cur.close()
				
	def Connect(self):
		pass
		self.connection = db.connect(database=self.db_name)
		try:
			self.cursor = self.connection.cursor()
			
		except Exception, e:
			self.last_error = e
			xbmc.log('Error [DataBase]: %s' % s)
	
	def Disconnect(self):
		pass
		self.cursor.close()
			
	def CheckDB(self):
		pass
		self.Connect()
		self.cursor.execute('SELECT COUNT(*) as c FROM groups')
		self.connection.commit()
		g = self.cursor.fetchone()
		self.cursor.execute('SELECT COUNT(*) as c FROM channels')
		self.connection.commit()
		c = self.cursor.fetchone()
		self.cursor.execute('SELECT COUNT(*) as c FROM shedules')
		self.connection.commit()
		s = self.cursor.fetchone()
		if (g[0] == 0) or (c[0] == 0) or (s[0] == 0):
			return False
		else:
			return True
	
	def UpdateUrlsStream(self, updlist = None, thread = False):
		pass
		if thread:
			thr = _DBThread(self.UpdateUrlsStream, updlist)
			thr.start()
			return
		self.Connect()
		schs = ""
		if updlist != None:
			for ch in updlist:
				schs = schs + ('%s' % ch) + ","
			
			schs = schs[:schs.__len__() - 1]
			self.cursor.execute('SELECT id, url FROM channels WHERE id IN (%s)' % schs)
		else:
			self.cursor.execute('SELECT id, url FROM channels WHERE urlstream <> ""')
		
		res = self.cursor.fetchall()
		ret = []
		for ch in res:
			torr_link = ''
			try:
				page = GET('http://torrent-tv.ru/' + ch[1])
				beautifulSoup = BeautifulSoup(page)
				tget = beautifulSoup.find('div', attrs={'class':'tv-player-wrapper'})
				m=re.search('http:(.+)"', str(tget))
				if m:
					torr_link= m.group(0).split('"')[0]
				else:
					m = re.search('load.*', str(tget))
					torr_link = m.group(0).split('"')[1]
			except Exception, e:
				torr_link = ''
				self.last_error = e
				xbmc.log('ERROR [UpdateUrlsStream]: %s' % e)
				
			self.cursor.execute('UPDATE channels SET urlstream = "%s" WHERE id = "%s"' % (torr_link, ch[0]))
			self.connection.commit()
			ret.append({'id': ch[0], 'urlstream': torr_link})
		self.Disconnect()
		return ret
	
	def GetParts(self):
		self.Connect()
		self.cursor.execute('SELECT id, name FROM groups')
		res = self.cursor.fetchall()
		ret = []
		for line in res:
			ret.append({'id': line[0], 'name': line[1].encode('utf-8')})
		self.Disconnect()
		return ret
		
	def GetChannels(self, group = None, where = None):
		self.Connect()
		if where == None:
			if group == None:
				self.cursor.execute('SELECT id, name, url, urlstream, imgurl FROM channels')
			else:
				self.cursor.execute('SELECT id, name, url, urlstream, imgurl FROM channels WHERE group_id = "%s"' % group)
		else:
			self.cursor.execute('SELECT id, name, url, urlstream, imgurl FROM channels WHERE %s' % where)
			
		res = self.cursor.fetchall()
		ret = []
		for line in res:
			ret.append({'id': line[0], 'name': line[1].encode('utf-8'), 'url': line[2].encode('utf-8'), 'urlstream': line[3].encode('utf-8'), 'imgurl': line[4].encode('utf-8')})
		self.Disconnect()
		return ret
		
	def GetChannelsHD(self):
		return self.GetChannels(where = 'hd = 1')
		
	def GetLastUpdate(self):
		self.Connect()
		self.cursor.execute('SELECT lastupdate FROM settings WHERE id = 1')
		res = self.cursor.fetchone()
		if res[0] == None:
			self.Disconnect()
			return None
		else:
			dt = datetime.datetime.fromtimestamp(time.mktime(time.strptime(res[0], '%Y-%m-%d %H:%M:%S.%f')))
			self.Disconnect()
			return dt
		return None
	
	def GetNewChannels(self, group = True):
		self.Connect()
		self.cursor.execute('SELECT ch.addsdate FROM channels as ch GROUP BY ch.addsdate ORDER BY ch.addsdate DESC')
		res = self.cursor.fetchone()
		self.cursor.execute('SELECT id, name, url, urlstream, imgurl, (SELECT gro.name FROM groups AS gro WHERE ch.group_id = gro.id) AS grname ' +
			'FROM channels as ch WHERE addsdate = "%s" ORDER BY group_id ASC' % res[0])
		res = self.cursor.fetchall()
		ret = []
		for line in res:
			ret.append(
				{'id': line[0], 'name': line[1].encode('utf-8'), 'url': line[2].encode('utf-8'), 'urlstream': line[3].encode('utf-8'), 'imgurl': line[4].encode('utf-8'), 'group_name': line[5].encode('utf-8')}
			)
		self.Disconnect()
		return ret
	
	def UpdateDB(self):
		try:
			pass
			self.Connect()
			page = GET('http://torrent-tv.ru/channels.php', cookie = self.cookie)
			beautifulSoup = BeautifulSoup(page)
			el = beautifulSoup.findAll('a', attrs={'class': 'simple-link'})
			
			grdict = []
			chdict = []
			grstr = ""
			chstr = ""
			for gr in el:
				link = gr['href'].find('category')
				access = 0
				
				if link > -1:
					if gr.string.encode('utf-8').find('Для взрослых') > -1:
						access = 1
					grdict.append({'id': gr['href'][17:], 'name': gr.string, 'url': gr['href'], 'adult': access})
					grstr = grstr + gr['href'][17:] + ","
					
				chs = gr.parent.findAll('a')
				for ch in chs:
					hd = 0
					if ch.string.encode('utf-8') == gr.string.encode('utf-8'):
						continue
					
					if gr['href'][17:].encode('utf-8') == '':
						continue
					
					if (ch.string.encode('utf-8').find(' HD') > -1) or (ch.string.encode('utf-8').find('HD ') > -1):
						hd = 1

					chdict.append({'id': ch['href'][31:], 'name': ch.string, 'url': ch['href'], 'adult': access, 'group_id': gr['href'][17:], 'sheduleurl': '', 'imgurl': '', 'hd': hd})
					chstr = chstr + ch['href'][31:] + ","
					
			grstr = grstr[:grstr.count(grstr)-2]
			chstr = chstr[:chstr.count(chstr)-2]
			self.cursor.execute('DELETE FROM groups WHERE (id NOT IN (%s))' % grstr)
			self.cursor.execute('DELETE FROM channels WHERE id NOT IN (%s)' % chstr)
			self.connection.commit()
			self.cursor.execute('SELECT id FROM groups')
			bdgrres = self.cursor.fetchall()
			bdgr = []
			bdch = []
			for line in bdgrres:
				bdgr.append('%s' % line[0])
			newgr = filter(lambda gr: not (gr['id'] in bdgr), grdict)
			self.cursor.execute('SELECT id, urlstream FROM channels')
			bdchres = self.cursor.fetchall()
			for line in bdchres:
				bdch.append('%s' % line[0])
				
			newch = filter(lambda ch: not (ch['id'] in bdch), chdict)
			for gr in newgr:
				self.cursor.execute('INSERT INTO groups (id, name, url, adult) VALUES ("%s", "%s", "%s", "%d");' % (gr['id'], gr['name'], gr['url'], gr['adult']))
			
			for ch in newch:
				td = datetime.date.today()
				self.cursor.execute('INSERT INTO channels (id, name, url, adult, group_id,sheduleurl, addsdate, imgurl, hd) VALUES ("%s", "%s", "%s", "%d", "%s", "%s", "%s", "%s", "%s");\r' % (
						ch['id'], ch['name'], ch['url'], ch['adult'], ch['group_id'], ch['sheduleurl'], td, ch['imgurl'], ch['hd'])
					)
			self.cursor.execute('UPDATE settings SET lastupdate = "%s"' % datetime.datetime.now())
			self.connection.commit()
			
			imgbs = BeautifulSoup(page)
			imgels=imgbs.findAll('div', attrs={'class': 'best-channels-content'})
			imgs = filter(lambda x: not (x.find('a')['href'][31:] in bdch), imgels)
			for img in imgs:
				self.cursor.execute('UPDATE channels SET imgurl = "%s" WHERE id = "%s"' % ('http://torrent-tv.ru/'+img.find('img')['src'], img.find('a')['href'][31:]))
			self.connection.commit()
			
			self.cursor.execute('SELECT id FROM channels WHERE urlstream <> ""')
			sqlres = self.cursor.fetchall()
			updch = []
			for ch in sqlres:
				updch.append(ch[0])
			self.UpdateUrlsStream(updch, True)
			self.Disconnect()
		except Exception, e:
			self.last_error = e
			xbmc.log('ERROR [DataBase]: %s' % e)