#!/usr/bin/python
# Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, os

sys.path.append(os.path.join(os.getcwd().replace(';', ''), 'resources', 'lib'))

if (__name__ == "__main__" ):
	import xbmcrussia
	xbmcrussia.addon_main()
