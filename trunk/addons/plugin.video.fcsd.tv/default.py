#!/usr/bin/python


import sys, os, xbmcaddon

__addon__ = xbmcaddon.Addon( id = 'plugin.video.fcsd.tv' )
sys.path.append( os.path.join( __addon__.getAddonInfo( 'path' ), 'resources', 'lib') )

if (__name__ == '__main__' ):
	import ivi2fcsd
	ivi2fcsd.addon_main()
