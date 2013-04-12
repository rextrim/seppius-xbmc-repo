__author__ = 'Admin'
import json
externals=dict({'btchat':'BTchatCom', 'rutracker':'RuTrackerOrg', 'tpb':'ThePirateBaySe', 'nnm':'NNMClubRu','kz':'Kino_ZalTv','torrenterall':'torrenterall'})
for i in externals.iterkeys():
    if externals[i]=='ThePirateBaySe':
        print i