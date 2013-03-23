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
import base64
import time

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
	def __init__( self, db_name):
		self.lock = threading.RLock()
		self.db_name = db_name
		self.connection = 0
		self.cursor = 0
		self.last_error = 0
		self.addon = xbmcaddon.Addon( id = 'plugin.video.raketa.tv' )
		self.addon_path =   xbmc.translatePath(self.addon.getAddonInfo('path'))
		if (sys.platform == 'win32') or (sys.platform == 'win64'):
			self.addon_path = self.addon_path.decode('utf-8')
			
		self.data_path = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'plugin.video.raketa.tv') )
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
		
		self.Connect()
		self.cursor.execute('SELECT COUNT(id) FROM shedules WHERE end > %d' % int(time.time()))
		res = self.cursor.fetchone()[0]
		if res != 0:
			return
		print '[DataBase.UpdateSchedules] Download file http://raketa-tv.com//player/JSON/program_list.php'
		program = GET('http://raketa-tv.com//player/JSON/program_list.php')
		print '[DataBase.UpdateSchedules] Parsing json'
		jsonprog = json.loads(program)
		
		print 'delete old schedules'
		self.lock.acquire()
		try:
			self.cursor.execute("DELETE FROM shedules")
			self.connection.commit()
			print 'zip database'
			self.cursor.execute("VACUUM")
			self.connection.commit()
			print 'del seq in shedules'
			self.cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE Name='shedules'")
			self.connection.commit()
			for ch in jsonprog:
				for sch in ch['program']:
					self.cursor.execute("INSERT INTO shedules (channel_id, start, end, name) VALUES (%s, %s, %s, '%s')" % (ch['channel_number'], sch['ut_start'], sch['ut_stop'], sch['title']))

			self.connection.commit()
			self.lock.release()
		except Exception, e:
			print '[DataBase.UpdateSchedules] Error: %s' % e
			self.lock.release()
			self.last_error = e
			self.Disconnect()
			return
		self.Disconnect()
		xbmc.log('[DataBase.UpdateSchedules] End schedules is update %s' % time.time())
	
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
		self.connection = db.connect(database=self.db_name)
		try:
			self.cursor = self.connection.cursor()
			
		except Exception, e:
			self.last_error = e
			xbmc.log('Error [DataBase]: %s' % s)
	
	def Disconnect(self):
		self.cursor.close()
	
	def GetParts(self):
		self.Connect()
		ssql = 'SELECT id, name FROM groups'
		self.cursor.execute(ssql)
		res = self.cursor.fetchall()
		ret = []
		for line in res:
			ret.append({'id': line[0], 'name': line[1].encode('utf-8')})
		self.Disconnect()
		return ret
		
	def GetChannels(self, group = None, where = None):
		self.Connect()
		select = 'SELECT id, name, urlstream, imgurl, (SELECT gro.name FROM groups AS gro WHERE ch.group_id = gro.id) AS grname FROM channels AS ch';
		if where == None:
			if group == None:
				select = select + ' WHERE (adult = 1) OR (adult = 0)'
			else:
				select = select + ' WHERE (group_id = "%s")' % group
		else:
			select = select + ' WHERE (%s)' % where
		select = select + ' AND (del = 0)'
		select = select + ' ORDER BY count DESC, group_id ASC, name ASC'
		self.cursor.execute(select)
		res = self.cursor.fetchall()
		ret = []
		for line in res:
			ret.append({'id': line[0], 'name': line[1].encode('utf-8'), 'urlstream': line[2].encode('utf-8'), 'imgurl': line[3].encode('utf-8'), 'group_name': line[4].encode('utf-8')})
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
	
	def GetNewChannels(self):
		self.Connect()
		self.cursor.execute('SELECT ch.addsdate FROM channels as ch GROUP BY ch.addsdate ORDER BY ch.addsdate DESC')
		res = self.cursor.fetchone()
		self.Disconnect()
		return self.GetChannels(where = 'addsdate = "%s"' % res[0])
	
	def GetLatestChannels(self):
		return self.GetChannels(where = 'count > 0')
	
	def IncChannel(self, id):
		self.Connect()
		self.lock.acquire()
		try:
			self.cursor.execute('UPDATE channels SET count = count + 1 WHERE id = "%s"' % id)
			self.connection.commit()
			self.lock.release()
		except Exception, e:
			print '[DataBase.UpdateDB] Error: %s' % e
			self.lock.release()
			self.last_error = e
		self.Disconnect()
	
	def DelChannel(self, id):
		self.Connect()
		self.lock.acquire()
		try:
			self.cursor.execute('UPDATE channels SET del = 1 WHERE id = "%s"' % id)
			self.connection.commit()
			self.lock.release()
		except Exception, e:
			print '[DataBase.UpdateDB] Error: %s' % e
			self.lock.release()
			self.last_error = e

		self.Disconnect()
	
	def UpdateDB(self):
		data = GET('http://raketa-tv.com/player/JSON/channels_list.json')
		data = json.loads(data)
		grdict = []
		chdict = []
		grstr = ""
		chstr = ""
		for group in data['types']:
			if group['id'] != "203":
				grdict.append({'id': group['id'], 'name': group['title'], 'url': '', 'adult': 0})
				grstr = grstr + group['id'] + ","
		for ch in data['channels']:
			chdict.append({'id': ch['number'], 'name': ch['title'], 'url': '', 'adult': 0, 'group_id': ch['category_id'], 'sheduleurl': '', 'imgurl': ch['icon'], 'hd': ch['hd'], 'urlstream': base64.urlsafe_b64decode(ch['id'].replace('?', 'L').replace('|', 'M').encode('utf-8'))})
			chstr = chstr + ch['number'] + ","
		grstr = grstr[:grstr.__len__()-1]
		chstr = chstr[:chstr.__len__()-1]
		self.lock.acquire()
		self.Connect()
		try:
			self.cursor.execute('DELETE FROM groups WHERE (id NOT IN (%s))' % grstr)
			self.cursor.execute('DELETE FROM channels WHERE id NOT IN (%s)' % chstr)
			self.connection.commit()
			self.lock.release()
		except Exception, e:
			print '[DataBase.UpdateDB] Error: %s' % e
			self.lock.release()
			self.last_error = e
			self.Disconnect()
			return
		
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
		self.lock.acquire()
		try:
			for gr in newgr:
				self.cursor.execute('INSERT INTO groups (id, name) VALUES ("%s", "%s");' % (gr['id'], gr['name']))
		
			for ch in newch:
				td = datetime.date.today()
				print '[DataBase.UpdateDB] %s' % "INSERT INTO channels (id, name, urlstream, group_id, addsdate, imgurl, hd) VALUES ('%s', '%s', %s '%s', '%s', '%s', '%s');\r" % (
						ch['id'].encode('utf-8'), ch['name'].encode('utf-8'), ch['urlstream'].encode('utf-8'), ch['group_id'].encode('utf-8'), td, ch['imgurl'].encode('utf-8'), ch['hd'].encode('utf-8'))
				self.cursor.execute("INSERT INTO channels (id, name, urlstream, group_id, addsdate, imgurl, hd) VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s');\r" % (
						ch['id'], ch['name'], ch['urlstream'], ch['group_id'], td, ch['imgurl'], ch['hd'])
					)
			self.cursor.execute('UPDATE settings SET lastupdate = "%s"' % datetime.datetime.now())
			self.connection.commit()
			self.lock.release()
		except Exception, e:
			print '[DataBase.UpdateDB] Error: %s' % e
			self.lock.release()
			self.last_error = e
			return

		self.Disconnect()