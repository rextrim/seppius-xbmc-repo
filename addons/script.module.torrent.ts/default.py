import sys,os,time,threading,random,re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import socket
import xbmcaddon
import cookielib
import urllib2,urllib
import simplejson as json

settings = xbmcaddon.Addon(id='script.module.torrent.ts')
language = settings.getLocalizedString
version = "0.0.1"
plugin = "torrent.ts-" + version


Addon = xbmcaddon.Addon(id='script.module.torrent.ts')

Addon.setSetting('stopped','1')

lock_file = xbmc.translatePath('special://temp/'+ 'ts.lock')
if os.path.exists(lock_file): os.remove(lock_file)