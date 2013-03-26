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
YaTv.updb_fast()
while 1==1:
	YaTv.updb()
	for i in range (0,30):
		YaTv.upd1(0,0)
		xbmc.sleep(60000)