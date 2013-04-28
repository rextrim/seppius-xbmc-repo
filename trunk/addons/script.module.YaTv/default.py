#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import socket
import xbmcaddon
import cookielib
import urllib2

settings = xbmcaddon.Addon(id='script.module.YaTv')
language = settings.getLocalizedString
version = "0.0.1"
plugin = "YaTv" + version

import YaTv
YaTv.upd12(0, 0)
YaTv.GetUpdateProg()
#YaTv.updb_fast(0)
for i in range (0,200):
	try:
		if xbmc.abortRequested: break
		else:
			YaTv.updb_fast(i)
			xbmc.sleep(500)
	except: 
		print "список кончился"

#YaTv.updb()
#while 1==1:
#	YaTv.updb()
#	for i in range (0,30):
#		YaTv.upd12(0,0)
#		xbmc.sleep(60000)