#!/usr/bin/python
# Copyright (c) MEGOGO.NET. All rights reserved.
# Copyright (c) XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2012, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, os, xbmcaddon
__addon__=xbmcaddon.Addon(id='plugin.video.megogo.net')
sys.path.append(os.path.join(__addon__.getAddonInfo('path'),'resources','lib'))
if (__name__ == '__main__' ):
	import megogo2xbmc
	megogo2xbmc.addon_main()
