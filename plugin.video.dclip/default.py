#!/usr/bin/python
# -*- coding: latin-1 -*-

import xbmc, xbmcplugin
import xbmcgui
import sys
import urllib, urllib2
import time
import re
from htmlentitydefs import name2codepoint as n2cp
import httplib
import urlparse
from os import path, system
import socket
from urllib2 import Request, URLError, urlopen
from urlparse import parse_qs
from urllib import unquote_plus

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.dclip"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
    cmd = "mkdir -p " + dataPath
    system(cmd)
viewMode = 500
Hostbase2 = "http://www.deviantclip.com"
Host2 = Hostbase2 + "/categories"
Hostbase = "http://www.dagay.com"
Host = Hostbase + "/categories"


def getUrl(url):
    # print "Here in getUrl url =", url
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def showContent():
    content = getUrl(Host)
    # print "content A =", content
    icount = 0
    start = 0
    n0 = content.find('<h2>CATEGORIES</h2>', start)
    if n0 < 0:
        return
    content = content[n0:]
    # print "content A2 =", content
    i1 = 0
    if i1 == 0:
        regexcat = '<a href="(.*?)" title="(.*?)">.*?src="(.*?)"'
        match = re.compile(regexcat, re.DOTALL).findall(content)
        ##print "match =", match
        for url, name, pic in match:
            url1 = Hostbase + url
            pic = pic
            ##print "Here in Showcontent url1 =", url1
            addDirectoryItem(name, {"name": name, "url": url1, "mode": 1}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)
        setView()

def getAllPages(name, url):
    pages = [1, 2, 3, 4, 5, 6]
    allitems = []
    for page in pages:
        allitems.extend(getPageVids(name, url + "/videos?p=" + str(page)))
    return allitems

def getPage(name, url):
    pages = [1, 2, 3, 4, 5, 6]
    allitems = getAllPages(name, url)
    if len(allitems) > 0:
        for item in allitems:
            xbmcplugin.addDirectoryItem(handle=item['handle'], url=item['url'], listitem=item['listitem'], isFolder=item['isFolder'])
        xbmcplugin.endOfDirectory(thisPlugin)
        setView()
    else:
        allok = True
        notok = False
        for page in pages:
            url1 = url + "/videos?p=" + str(page)
            name = "Page " + str(page)
            pic = " "
            allok = addPage(name, url1, 2, pic)
            if not allok:
                notok = True
            #addDirectoryItem(name, {"name": name, "url": url1, "mode": 2}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)
        setView()
        if notok:
            xbmc.log("Problem adding an item in getPage")

def getPageVids(nameofpage, urlofpage):
    content = getUrl(urlofpage)
    regexvideo = 'thumb_container video.*?href="(.*?)" title="(.*?)">.*?src="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    litems = []
    for url, name, pic in match:
        name = name.replace('"', '')
        url = Hostbase + url
        pic = pic
        litems.append(makeItem(name, {"name": name, "url": url, "mode": 3}, pic))
    return litems

def makeItem(name, parameters={}, pic=""):
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    litem = dict(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)
    litem.setdefault(litem.keys()[0])
    return litem

def addDirectoryItem(name, parameters={}, pic=""):
    #li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    #url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    item = makeItem(name, parameters, pic)
    return xbmcplugin.addDirectoryItem(handle=item['handle'], url=item['url'], listitem=item['listitem'], isFolder=item['isFolder'])

def addPage(itemname, urlpath, runmode, thumb):
    return addDirectoryItem(itemname, {"name": itemname, "url": urlpath, "mode": runmode}, thumb)

def setView():
    xbmc.executebuiltin("Container.SetViewMode(%s)" % viewMode)

def getVideos(name1, urlmain):
    content = getUrl(urlmain)
    regexvideo = 'thumb_container video.*?href="(.*?)" title="(.*?)">.*?src="(.*?)"'
    match = re.compile(regexvideo, re.DOTALL).findall(content)
    for url, name, pic in match:
        name = name.replace('"', '')
        url = Hostbase + url
        pic = pic
        addDirectoryItem(name, {"name": name, "url": url, "mode": 3}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)
    setView()


def playVideo(name, url):
    ##print "Here in playVideo url =", url
    fpage = getUrl(url)
    ##print "fpage C =", fpage
    start = 0
    pos1 = fpage.find("source src", start)
    if (pos1 < 0):
        return
    pos2 = fpage.find("http", pos1)
    if (pos2 < 0):
        return
    pos3 = fpage.find('"', (pos2 + 5))
    if (pos3 < 0):
        return

    url = fpage[(pos2):(pos3)]

    pic = "DefaultFolder.png"
    ##print "Here in playVideo url B=", url
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    player = xbmc.Player()
    player.play(url, li)


std_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
}

def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


params = parameters_string_to_dict(sys.argv[2])
name = str(params.get("name", ""))
url = str(params.get("url", ""))
url = urllib.unquote(url)
mode = str(params.get("mode", ""))

if not sys.argv[2]:
    ok = showContent()
else:
    if mode == str(1):
        ok = getPage(name, url)
    elif mode == str(2):
        ok = getVideos(name, url)
    elif mode == str(3):
        ok = playVideo(name, url)

