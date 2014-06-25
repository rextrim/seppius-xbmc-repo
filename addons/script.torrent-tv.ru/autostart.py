import defines
import os
from xml.etree.ElementTree import ElementTree

print 'STARTUP TTVPROXY'
dom = ElementTree()
dom.parse(defines.ADDON_PATH + '/resources/settings.xml')
xset = None
skins = []
for set in dom.find('category').findall('setting'):
     if set.attrib['id'] == 'skin':
         skins.append(set.attrib['values'])
         xset = set

dirs = os.listdir(defines.ADDON_PATH + '/resources/skins/');
xset.attrib['values'] = "|".join(dirs);
dom.write(defines.ADDON_PATH + '/resources/settings.xml', 'utf-8')            