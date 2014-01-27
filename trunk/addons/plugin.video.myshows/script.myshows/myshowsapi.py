# -*- coding: utf-8 -*-
#

import xbmc
import xbmcaddon
import xbmcgui
import time, socket
import math
import kp
import base64

from utilities import Debug, notification, get_string_setting, get_bool_setting, get_int_setting
from urllib2 import Request, urlopen, HTTPError, URLError
from httplib import HTTPException

try:
    import simplejson as json
except ImportError:
    import json

try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1

# read settings
__addon__ = xbmcaddon.Addon("script.myshows")
__addonversion__ = __addon__.getAddonInfo("version")
__language__ = __addon__.getLocalizedString
try:__myshows__ = xbmcaddon.Addon("plugin.video.myshows")
except:__myshows__=None

class myshowsAuthProblem(Exception):
    def __init__(self, value, code):
        self.value = value
        self.code = code
    def __str__(self):
        return repr(self.value)
class myshowsServerBusy(Exception):
    def __init__(self, value, code):
        self.value = value
        self.code = code
    def __str__(self):
        return repr(self.value)

class myshowsAPI(object):

    __apikey = "b6135e0f7510a44021fac8c03c36c81a17be35d9"
    __baseURL = "https://api.myshows.tv"
    __timeout = 60
    __username = ""
    __password = ""
    validUser = False

    def __init__(self):
        try:
            self.__username = __myshows__.getSetting('username').strip()
            self.__password = __myshows__.getSetting("password").strip()
            Debug("[myshowsAPI] Initializing")
            self.settings = None
            if self.testAccount():
                Debug("[myshowsAPI] Myshows.ru account '%s' is valid." % self.__username)
        except:
            pass
        login=get_string_setting('login')
        password=get_string_setting('password')
        cookie=get_string_setting('cookie')
        if cookie=='': cookie=None
        if login!='' and password!='':
            kpLogin=kp.Login(login,password,cookie)
        else:
            raise Exception('No login or password!')
        if kpLogin.testAcc():
            Debug("[myshowsAPI] KinoPosik.ru account '%s' is valid." % login)

    def __getData(self, url, args):
        data = None
        try:
            Debug("[myshowsAPI] __getData(): urllib2.Request(%s)" % url)

            if args == None:
                req = Request(url)
            else:
                req = Request(url, args)

            Debug("[myshowsAPI] __getData(): urllib2.urlopen()")
            t1 = time.time()
            response = urlopen(req, timeout=self.__timeout)
            t2 = time.time()

            Debug("[myshowsAPI] __getData(): response.read()")
            data = response.read()

            Debug("[myshowsAPI] __getData(): Response Code: %i" % response.getcode())
            Debug("[myshowsAPI] __getData(): Response Time: %0.2f ms" % ((t2 - t1) * 1000))
            Debug("[myshowsAPI] __getData(): Response Headers: %s" % str(response.info().dict))

        except IOError, e:
            if hasattr(e, "code"): # error 401 or 503, possibly others
                Debug("[myshowsAPI] __getData(): Error Code: %s" % str(e.code))
                
                error = {}

                # read the error document, strip newlines, this will make an html page 1 line
                error_data = e.read().replace("\n", "").replace("\r", "")

                # try to parse the data as json
                try:
                    error = json.loads(error_data)
                except ValueError:
                    Debug("[myshowsAPI] __getData(): Error data is not JSON format - %s" % error_data)
                    # manually add status, and the page data returned.
                    error["status"] = "failure"
                    error["error"] = error_data

                # add error code, and string type to error dictionary
                error["code"] = e.code
                error["type"] = "protocol"

                if e.code == 401: # authentication problem
                    # {"status":"failure","error":"failed authentication"}
                    Debug("[myshowsAPI] __getData(): Authentication Failure (%s)" % error_data)
                    # reset internal valid user
                    self.validUser = False

                elif e.code == 503: # server busy problem
                    # {"status":"failure","error":"server is over capacity"}
                    Debug("[myshowsAPI] __getData(): Server Busy (%s)" % error_data)

                else:
                    Debug("[myshowsAPI] __getData(): Other problem (%s)" % error_data)

                return json.dumps(error)
            elif hasattr(e, "reason"): # usually a read timeout, or unable to reach host
                Debug("[myshowsAPI] __getData(): Network error: %s" % str(e.reason))
                if isinstance(e.reason, socket.timeout):
                    notification("myshows", __language__(1108).encode( "utf-8", "ignore" ) + " (timeout)") # can't connect to myshows
                return '{"status":"failure","error":"%s","type":"network"}' % e.reason
            else:
                return '{"status":"failure","error":"%s"}' % e.message
        return data
    
    # make a JSON api request to myshows
    # method: http method (GET or POST)
    # req: REST request (ie '/user/library/movies/all.json/%%API_KEY%%/%%USERNAME%%')
    # args: arguments to be passed by POST JSON (only applicable to POST requests), default:{}
    # returnStatus: when unset or set to false the function returns None upon error and shows a notification,
    #    when set to true the function returns the status and errors in ['error'] as given to it and doesn't show the notification,
    #    use to customise error notifications
    # silent: default is True, when true it disable any error notifications (but not debug messages)
    # passVersions: default is False, when true it passes extra version information to myshows to help debug problems
    # hideResponse: used to not output the json response to the log
    def myshowsRequest(self, method, url, args=None, returnStatus=False, silent=True, passVersions=False, hideResponse=False):
        raw = None
        data = None
        jdata = {}
        retries = get_int_setting("retries")

        if args is None:
            args = {}

        if not (method == 'POST' or method == 'GET'):
            Debug("[myshowsAPI] myshowsRequest(): Unknown method '%s'" % method)
            return None
        
        if method == 'POST':
            # debug log before username and sha1hash are injected
            Debug("[myshowsAPI] myshowsRequest(): Request data: '%s'" % str(json.dumps(args)))
            
            # inject username/pass into json data
            args["username"] = self.__username
            args["password"] = self.__password
            
            # check if plugin version needs to be passed
            if passVersions:
                args['plugin_version'] = __addonversion__
                args['media_center_version'] = xbmc.getInfoLabel("system.buildversion")
                args['media_center_date'] = xbmc.getInfoLabel("system.builddate")
            
            # convert to json data
            jdata = json.dumps(args)

        Debug("[myshowsAPI] myshowsRequest(): Starting retry loop, maximum %i retries." % retries)
        
        # start retry loop
        for i in range(retries):    
            Debug("[myshowsAPI] myshowsRequest(): (%i) Request URL '%s'" % (i, url))
            
            # get data from myshows.tv
            raw = self.__getData(url, jdata)
            
            # check if we are closing
            if xbmc.abortRequested:
                Debug("[myshowsAPI] myshowsRequest(): (%i) xbmc.abortRequested" % i)
                break

            # check that returned data is not empty
            if not raw:
                Debug("[myshowsAPI] myshowsRequest(): (%i) JSON Response empty" % i)
                xbmc.sleep(1000)
                continue

            try:
                # get json formatted data    
                data = json.loads(raw)
                if hideResponse:
                    Debug("[myshowsAPI] myshowsRequest(): (%i) JSON response recieved, response not logged" % i)
                else:
                    Debug("[myshowsAPI] myshowsRequest(): (%i) JSON response: '%s'" % (i, str(data)))
            except ValueError:
                # malformed json response
                Debug("[myshowsAPI] myshowsRequest(): (%i) Bad JSON response: '%s'", (i, raw))
                if not silent:
                    notification("myshows", __language__(1109).encode( "utf-8", "ignore" ) + ": Bad response from myshows") # Error
                
            # check for the status variable in JSON data
            if 'status' in data:
                if data['status'] == 'success':
                    break
                else:
                    Debug("[myshowsAPI] myshowsRequest(): (%i) JSON Error '%s' -> '%s'" % (i, data['status'], data['error']))
                    if data.has_key("type"):
                        if data["type"] == "protocol":
                            # protocol error, so a 4xx or 5xx
                            if data["code"] == 401:
                                # auth error, no point retrying
                                self.validUser = False
                                return None
                            else:
                                pass
                        elif data["type"] == "network":
                            # network communication error, sleep for a
                            # bit longer before continuing
                            xbmc.sleep(5000)
                            continue
                    else:
                        #should never get here
                        pass
                    
                    xbmc.sleep(1000)
                    continue
            
            # check to see if we have data
            if data:
                Debug("[myshowsAPI] myshowsRequest(): Have JSON data, breaking retry.")
                break

            xbmc.sleep(500)
        
        # handle scenario where all retries fail
        if not data:
            Debug("[myshowsAPI] myshowsRequest(): JSON Request failed, data is still empty after retries.")
            return None
        
        if 'status' in data:
            if data['status'] == 'failure':
                Debug("[myshowsAPI] myshowsRequest(): Error: %s" % str(data['error']))
                if returnStatus:
                    return data
                if not silent:
                    notification("myshows", __language__(1109).encode( "utf-8", "ignore" ) + ": " + str(data['error'])) # Error
                return None
            elif data['status'] == 'success':
                Debug("[myshowsAPI] myshowsRequest(): JSON request was successful.")

        return data

    # helper for onSettingsChanged
    def updateSettings(self):

        _username = get_string_setting("username")
        _password = sha1(get_string_setting("password")).hexdigest()

        if not ((self.__username == _username) and (self.__password == _password)):
            self.__username = _username
            self.__password = _password
            self.testAccount(force=True)

    # http://api.myshows.tv/account/test/<apikey>
    # returns: {"status": "success","message": "all good!"}
    def testAccount(self, force=False, daemon=True):
        return True

    # url: http://api.myshows.tv/account/settings/<apikey>
    # returns: all settings for authenticated user

    # url: http://api.myshows.tv/<show|movie>/watching/<apikey>
    # returns: {"status":"success","message":"watching The Walking Dead 1x01","show":{"title":"The Walking Dead","year":"2010","imdb_id":"tt123456","tvdb_id":"153021","tvrage_id":"1234"},"season":"1","episode":{"number":"1","title":"Days Gone Bye"},"facebook":false,"twitter":false,"tumblr":false}
    def watching(self, type, data):
        if self.testAccount():
            url = "%s/%s/watching/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[myshowsAPI] watching(url: %s, data: %s)" % (url, str(data)))
            return True
    
    def watchingEpisode(self, tvdb_id, title, year, season, episode, uniqueid, duration, percent):
        data = {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'season': season, 'episode': episode, 'episode_tvdb_id': uniqueid, 'duration': math.ceil(duration), 'progress': math.ceil(percent)}
        #return self.watching("show", data)
    def watchingMovie(self, imdb_id, title, year, duration, percent):
        data = {'imdb_id': imdb_id, 'title': title, 'year': year, 'duration': math.ceil(duration), 'progress': math.ceil(percent)}
        #return self.watching("movie", data)

    # url: http://api.myshows.tv/<show|movie>/scrobble/<apikey>
    # returns: {"status": "success","message": "scrobbled The Walking Dead 1x01"}
    def scrobble(self, type, data):
        if self.testAccount():
            url = "%s/%s/scrobble/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[myshowsAPI] scrobble(url: %s, data: %s)" % (url, str(data)))
            #return self.myshowsRequest("POST", url, data, passVersions=True)

    def scrobbleEpisode(self, tvdb_id, title, year, season, episode, uniqueid, duration, percent):
        data = {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'season': season, 'episode': episode, 'episode_tvdb_id': uniqueid, 'duration': math.ceil(duration), 'progress': math.ceil(percent)}
        #return self.scrobble("show", data)
    def scrobbleMovie(self, imdb_id, title, year, duration, percent):
        data = {'imdb_id': imdb_id, 'title': title, 'year': year, 'duration': math.ceil(duration), 'progress': math.ceil(percent)}
        #return self.scrobble("movie", data)

    # url: http://api.myshows.tv/<show|movie>/cancelwatching/<apikey>
    # returns: {"status":"success","message":"cancelled watching"}
    def cancelWatching(self, type):
        if self.testAccount():
            url = "%s/%s/cancelwatching/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[myshowsAPI] cancelWatching(url: %s)" % url)
            return True
        
    def cancelWatchingEpisode(self):
        return True
    def cancelWatchingMovie(self):
        return True

    # url: http://api.myshows.tv/user/library/<shows|movies>/collection.json/<apikey>/<username>/min
    # response: [{"title":"Archer (2009)","year":2009,"imdb_id":"tt1486217","tvdb_id":110381,"seasons":[{"season":2,"episodes":[1,2,3,4,5]},{"season":1,"episodes":[1,2,3,4,5,6,7,8,9,10]}]}]
    # note: if user has nothing in collection, response is then []
    def getLibrary(self, type):
        if self.testAccount():
            url = "%s/user/library/%s/collection.json/%s/%s/min" % (self.__baseURL, type, self.__apikey, self.__username)
            Debug("[myshowsAPI] getLibrary(url: %s)" % url)
            return True

    def getShowLibrary(self):
        return self.getLibrary("shows")
    def getMovieLibrary(self):
        return self.getLibrary("movies")

    # url: http://api.myshows.tv/user/library/<shows|movies>/watched.json/<apikey>/<username>/min
    # returns: [{"title":"Archer (2009)","year":2009,"imdb_id":"tt1486217","tvdb_id":110381,"seasons":[{"season":2,"episodes":[1,2,3,4,5]},{"season":1,"episodes":[1,2,3,4,5,6,7,8,9,10]}]}]
    # note: if nothing watched in collection, returns []
    def getWatchedLibrary(self, type):
        if self.testAccount():
            url = "%s/user/library/%s/watched.json/%s/%s/min" % (self.__baseURL, type, self.__apikey, self.__username)
            Debug("[myshowsAPI] getWatchedLibrary(url: %s)" % url)
            return True

    def getWatchedEpisodeLibrary(self,):
        return self.getWatchedLibrary("shows")
    def getWatchedMovieLibrary(self):
        return self.getWatchedLibrary("movies")

    # url: http://api.myshows.tv/<show/episode|movie>/library/<apikey>
    # returns: {u'status': u'success', u'message': u'27 episodes added to your library'}
    def addToLibrary(self, type, data):
        if self.testAccount():
            url = "%s/%s/library/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[myshowsAPI] addToLibrary(url: %s, data: %s)" % (url, str(data)))
            return True

    def addEpisode(self, data):
        return self.addToLibrary("show/episode", data)
    def addMovie(self, data):
        return self.addToLibrary("movie", data)

    # url: http://api.myshows.tv/<show/episode|movie>/unlibrary/<apikey>
    # returns:
    def removeFromLibrary(self, type, data):
        if self.testAccount():
            url = "%s/%s/unlibrary/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[myshowsAPI] removeFromLibrary(url: %s, data: %s)" % (url, str(data)))
            return True

    def removeEpisode(self, data):
        return self.removeFromLibrary("show/episode", data)
    def removeMovie(self, data):
        return self.removeFromLibrary("movie", data)

    # url: http://api.myshows.tv/<show/episode|movie>/seen/<apikey>
    # returns: {u'status': u'success', u'message': u'2 episodes marked as seen'}
    def updateSeenInLibrary(self, type, data):
        if self.testAccount():
            url = "%s/%s/seen/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[myshowsAPI] updateSeenInLibrary(url: %s, data: %s)" % (url, str(data)))
            return True

    def updateSeenEpisode(self, data):
        return self.updateSeenInLibrary("show/episode", data)
    def updateSeenMovie(self, data):
        return self.updateSeenInLibrary("movie", data)

    # url: http://api.myshows.tv/<show/episode|movie>/summary.format/apikey/title[/season/episode]
    # returns: returns information for a movie or episode
    def getSummary(self, type, data):
        if self.testAccount():
            url = "%s/%s/summary.json/%s/%s" % (self.__baseURL, type, self.__apikey, data)
            Debug("[myshowsAPI] getSummary(url: %s)" % url)
            return True

    def getShowSummary(self, imdb_id, season, episode):
        data = "%s/%s/%s" % (imdb_id, season, episode)
        return self.getSummary("show/episode", data)
    def getMovieSummary(self, imdb_id):
        data = str(imdb_id)
        return self.getSummary("movie", data)

    # url: http://api.myshows.tv/rate/<episode|movie>/apikey
    # returns: {"status":"success","message":"rated Portlandia 1x01","type":"episode","rating":"love","ratings":{"percentage":100,"votes":2,"loved":2,"hated":0},"facebook":true,"twitter":true,"tumblr":false}
    def rate(self, type, data):
        if self.testAccount():
            url = "%s/rate/%s/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[myshowsAPI] rate(url: %s, data: %s)" % (url, str(data)))
            return True

    def rateEpisode(self, data):
        return self.rate("episode", data)
    def rateMovie(self, data):
        return self.rate("movie", data)
