import xbmcgui
import time
import xbmcaddon
import calendar
import datetime

import defines

class DateForm(xbmcgui.WindowXMLDialog):
    def __ini__(self, *args, **kwargs):
        self.li = None
        self.get_method = None
        self.session = None
        self.result = 'None'
        self.date = time.localtime()
        self.list = None
        pass

    def onInit(self):
        lblDate = self.getControl(102)
        lblDate.setLabel(self.date.date().isoformat())
        
        self.list = self.getControl(103)
        self.fillDays(self.date)
        pass

    def fillDays(self, date):
        self.list.reset()
        item = xbmcgui.ListItem("..")
        item.setProperty("type", "day")
        self.list.addItem(item)
        
        maxdays = calendar.monthrange(date.year, date.month)[1]
        i = 1
        while i <= maxdays:

            if i == self.date.day and date.month == self.date.month and date.year == self.date.year:
                item = xbmcgui.ListItem("[COLOR FF0080FF]%s[/COLOR]" % i)
            else:
                item = xbmcgui.ListItem("%s" % i)
            item.setProperty("value", "%s" % i)
            item.setProperty("type", "day")
            item.setProperty("date", datetime.date(date.year, date.month, i).isoformat())
            self.list.addItem(item)
            i = i + 1
        if date.month == self.date.month and date.year == self.date.year:
            self.list.selectItem(self.date.day)
        self.setFocus(self.list)

    def fillMonth(self, date):
        self.list.reset()
        item = xbmcgui.ListItem("..")
        item.setProperty("type", "month")
        self.list.addItem(item)
        month = 12
        i = 1
        while i <= month:
            if i == self.date.month and date.year == self.date.year:
                item = xbmcgui.ListItem("[COLOR FF0080FF]%s[/COLOR]" % i)
            else:
                item = xbmcgui.ListItem("%s" % i)
            item.setProperty("value", "%s" % i)
            item.setProperty("type", "month")
            self.list.addItem(item)
            i = i + 1

        if date.year == self.date.year:
            self.list.selectItem(self.date.month)
        self.setFocus(self.list)

    def fillYear(self, date):
        self.list.reset()
        i = 2013
        while i <= date.year:
            if i == self.date.year:
                item = xbmcgui.ListItem("[COLOR FF0080FF]%s[/COLOR]" % i)
            else:
                item = xbmcgui.ListItem("%s" % i)
            item.setProperty("value", "%s" % i)
            item.setProperty(date.strftime())
            item.setProperty("type", "year")
            self.list.addItem(item)
            i = i + 1

        self.list.selectItem(i - 2013)
        self.setFocus(self.list)

    def onClick(self, controlId):
        if controlId == 103:
            self.list = self.getControl(controlId)
            selItem = self.list.getSelectedItem()
            if selItem.getLabel() == "..":
                if selItem.getProperty("type") == "day":
                    self.fillMonth(self.date)
                elif selItem.getProperty("type") == "month":
                    self.fillYear(self.date)
            else:
                if selItem.getProperty("type") == "day":
                    self.date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(selItem.getProperty("date"), "%Y-%m-%d")))
                    self.close()
                elif selItem.getProperty("type") == "month":
                    date = datetime.date(self.date.year, int(selItem.getProperty("value")), 1)
                    self.fillDays(date)
                elif selItem.getProperty("type") == "year":
                    date = datetime.date(int(selItem.getProperty("value")), 1, 1)
                    self.fillMonth(date)

        super.onClick(self, controlId)

