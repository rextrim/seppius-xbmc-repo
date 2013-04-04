import os
import sys
import re
from traceback import print_exc
import xbmc
import xbmcgui
import xbmcaddon

settings = xbmcaddon.Addon(id='script.module.torrent.ts')
language = settings.getLocalizedString
addonDir = settings.getAddonInfo("path")
#XBMC_SKIN  = xbmc.getSkinDir()

  
class WASEngine(xbmcgui.WindowXMLDialog):
	def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback = True):
		self.isCanceled=False
		self.showCancel=True
		
		pass
	def onInit(self):
		self.progress=0
		
		self.controls = {}
		#try:
	#		self.getControls()
	#	except:
	#		print_exc()
		self.button = self.getControl(2005)
		self.button.setLabel(language(1006))
		self.setFocus(self.getControl(2005))
		self.label = self.getControl(2002)
		self.label.setLabel('')
		self.label = self.getControl(2003)
		self.label.setLabel('')
		self.button = self.getControl(2005)
		self.button.setLabel(language(1006))

	def updater(self,progress,text1,text2):
		self.label = self.getControl(2004)
		self.label.setPercent(progress)
		self.label = self.getControl(2002)
		self.label.setLabel(text1)
		self.label = self.getControl(2003)
		self.label.setLabel(text2)
		self.button = self.getControl(2005)
		self.button.setLabel(language(1006))
		self.button.setVisible(self.showCancel)
		self.setFocus(self.getControl(2005))

	def onClick(self, controlID):
		if controlID==2005: 
			self.isCanceled=True


class dwprogress():
	def __init__(self, *args, **kwargs):
		self.ui = WASEngine("DialogDownloadProgress.xml",addonDir, "default")
		self.ui.show()
	def updater(self,progress=0,text1='',text2=''):
		self.ui.updater(progress,text1,text2)
	def close(self):
		self.ui.close()