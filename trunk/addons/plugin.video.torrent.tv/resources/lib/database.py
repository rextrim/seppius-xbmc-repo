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
		self.addon = xbmcaddon.Addon( id = 'plugin.video.torrent.tv' )
		self.addon_path =   xbmc.translatePath(self.addon.getAddonInfo('path'))
		if (sys.platform == 'win32') or (sys.platform == 'win64'):
			self.addon_path = self.addon_path.decode('utf-8')
			
		self.data_path = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'plugin.video.torrent.tv') )
		if (sys.platform == 'win32') or (sys.platform == 'win64'):
			self.data_path = self.data_path.decode('utf-8')
			
		self.CreateDB()
	
	def GetDBVer(self):
		xbmc.log('Connect to database')
		self.Connect()
		xbmc.log('Get DataBase version')
		self.cursor.execute('SELECT dbver FROM settings WHERE id = 1')
		return self.cursor.fetchone()[0]
	
	def UpdateSchedules(self, thread=False):
		if thread:
			thr = _DBThread(self.UpdateSchedules, False)
			thr.start()
			return
		sur = os.path.join(self.addon_path, 'resources/schedules/raketa.dat')
		if not os.path.exists(sur):
			print '[ERROR] DataBase::UpdateSchedules: Not found resource file raketa.dat'
			return False
		
		suf = open(sur, 'r')
		line = suf.readline()
		program = GET('http://raketa-tv.com//player/JSON/program_list.php')
		jsonprog = json.loads(program)

		self.Connect()
		print 'delete old schedules'
		self.cursor.execute("DELETE FROM shedules")
		self.connection.commit()
		print 'zip database'
		self.cursor.execute("VACUUM")
		self.connection.commit()
		print 'del seq in shedules'
		self.cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE Name='shedules'")
		self.connection.commit()

		while line:
			aline = line.split(';')
			if aline[0].find('###'):
				for ch in jsonprog:
					if ch['channel_number'] == aline[1]:
						for sch in ch['program']:
							self.cursor.execute("INSERT INTO shedules (channel_id, start, end, name) VALUES (%s, %s, %s, '%s')" % (aline[0], sch['ut_start'].encode('utf-8'), sch['ut_stop'].encode('utf-8'), sch['title'].encode('utf-8')))
						break
			line = suf.readline()
					
			self.connection.commit()
		self.Disconnect()
	
	def GetSchedules(self, chid, limit = None, start = None):
		self.Connect()
		ssql = 'SELECT (SELECT name FROM channels WHERE sch.channel_id = id), channel_id, start, end, name FROM shedules as sch'
		ssql = ssql + ' WHERE (channel_id = %s)' % chid
		if start != None:
			ssql = ssql + ' AND (end > %s)' % start
		ssql = ssql + ' ORDER BY channel_id ASC, start ASC'
		if limit != None:
			ssql = ssql + ' LIMIT %s' % limit
		self.cursor.execute(ssql)
		res = self.cursor.fetchall()
		self.Disconnect()
		chn = 0
		chsch = {}
		ret = []
		for sch in res:
			if chn != sch[1]:
				chn = sch[1]
				chsch['name'] = sch[0]
				chsch['program'] = []
			chsch['program'].append({'start': sch[2], 'end': sch[3], 'title': sch[4]})

		ret.append(chsch)
		return ret
	
	def CreateDB(self):
		
		if not os.path.exists(self.db_name):
			xbmc.log('Create DataBase')
			fsql = open(os.path.join(self.addon_path, 'resources/tvbase.sql'), 'r')
			ssql = fsql.read()
			ssql = ssql.split('----')
			fsql.close()
			con = db.connect(database=self.db_name)
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
		self.cursor.close()
			
	def UpdateUrlsStream(self, updlist = None, thread = False):
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
			self.cursor.execute('SELECT id, url FROM channels WHERE (urlstream <> "") AND (del = 0)')
		
		res = self.cursor.fetchall()
		ret = []
		for ch in res:
			torr_link = ''
			try:
				page = GET('http://torrent-tv.ru/' + ch[1])
				beautifulSoup = BeautifulSoup(page)
				tget = beautifulSoup.find('div', attrs={'class':'tv-player'})
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
	
	def GetParts(self, adult = True):
		self.Connect()
		ssql = 'SELECT id, name FROM groups'
		if adult == 'true':
			ssql = ssql + ' WHERE adult = 0'
		
		self.cursor.execute(ssql)
		res = self.cursor.fetchall()
		ret = []
		for line in res:
			ret.append({'id': line[0], 'name': line[1].encode('utf-8')})
		self.Disconnect()
		return ret
		
	def GetChannels(self, group = None, where = None, adult = True):
		self.Connect()
		select = 'SELECT id, name, url, urlstream, imgurl, (SELECT gro.name FROM groups AS gro WHERE ch.group_id = gro.id) AS grname FROM channels AS ch';
		if where == None:
			if group == None:
				#select = select + ' WHERE (adult = 0)'
				if adult == 'true':
					select = select + ' WHERE (adult = 0)'
				else:
					select = select + ' WHERE (adult = 1) OR (adult = 0)'
			else:
				select = select + ' WHERE (group_id = "%s")' % group
				if adult == 'true':
					select = select + ' AND (adult = 0)'
		else:
			select = select + ' WHERE (%s)' % where
			if adult == 'true':
				select = select + ' AND (adult = 0)'
		select = select + ' AND (del = 0)'
		select = select + ' ORDER BY count DESC, group_id ASC, name ASC'
		self.cursor.execute(select)
		res = self.cursor.fetchall()
		ret = []
		for line in res:
			ret.append({'id': line[0], 'name': line[1].encode('utf-8'), 'url': line[2].encode('utf-8'), 'urlstream': line[3].encode('utf-8'), 'imgurl': line[4].encode('utf-8'), 'group_name': line[5].encode('utf-8')})
		self.Disconnect()
		return ret
		
	def GetChannelsHD(self, adult = True):
		return self.GetChannels(where = 'hd = 1', adult = adult)
		
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
	
	def GetNewChannels(self, adult = True):
		self.Connect()
		self.cursor.execute('SELECT ch.addsdate FROM channels as ch GROUP BY ch.addsdate ORDER BY ch.addsdate DESC')
		res = self.cursor.fetchone()
		self.Disconnect()
		return self.GetChannels(where = 'addsdate = "%s"' % res[0], adult = adult)
	
	def GetLatestChannels(self, adult = True):
		return self.GetChannels(where = 'count > 0', adult = adult)
	
	def IncChannel(self, id):
		self.Connect()
		self.cursor.execute('UPDATE channels SET count = count + 1 WHERE id = "%s"' % id)
		self.connection.commit()
		self.Disconnect()
	
	def DelChannel(self, id):
		self.Connect()
		self.cursor.execute('UPDATE channels SET del = 1 WHERE id = "%s"' % id)
		self.connection.commit()
		self.Disconnect()
	
	def UpdateDB(self):
		try:
			self.Connect()
			self.cursor.execute('SELECT COUNT(id) FROM shedules WHERE end > %d' % int(time.time()))
			res = self.cursor.fetchone()[0]
			if res == 0:
				self.UpdateSchedules(True)
				
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
			
			import time
			self.cursor.execute('SELECT id FROM channels WHERE (urlstream <> "") AND (del = 0)')
			sqlres = self.cursor.fetchall()
			updch = []
			for ch in sqlres:
				updch.append(ch[0])
			
			self.UpdateUrlsStream(updch, True)
			self.Disconnect()
		except Exception, e:
			self.last_error = e
			xbmc.log('ERROR [DataBase]: %s' % e)

