# -*- coding: utf-8 -*-

import urllib
import urllib2
import zipfile
from datetime import datetime
import time
from cStringIO import StringIO
import xml.etree.ElementTree as ET

import xbmcplugin
import xbmcgui

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer


RTMP_PREFIX = "rtmp://streamh1.nelonen.fi/hot/mp4:"
ZIP_URL = "http://ruutu.s3.amazonaws.com/ruutu_11.zip"
CACHE_TIME = 1  # hours

cache = StorageServer.StorageServer("video.ruutu", CACHE_TIME)


def list_types():
    add_dir('Jaksot', 'jaksot', 1, '')
    add_dir('Klipit', 'klipit', 1, '')
    add_dir('Sarjat', 'sarjat', 1, '')


def list_channels(channels=[], next_mode=3):
    add_dir('Kaikki', 'kaikki', next_mode, '')
    for channel in channels:
        add_dir(channel, channel.lower(), next_mode, '')


def list_series(series=[]):
    for s in series:
        add_dir(s, s.lower(), 4, '')


def list_programs(programs=[]):
    for p in programs:
        add_link(p)


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


def fetch_ruutu_xml():
    print 'Fetching XML...'
    try:
        remotezip = urllib2.urlopen(ZIP_URL)
        zipinmemory = StringIO(remotezip.read())
        zip = zipfile.ZipFile(zipinmemory)
        for fn in zip.namelist():
            if fn == 'ruutu.xml':
                xml = zip.read(fn)
                return xml
    except urllib2.HTTPError as e:
        print "HTTP error " + str(e.code)


def parse_programs(xml_string):
    videos = ET.fromstring(xml_string)
    programs = []
    for program in videos:
        p = {}
        for child in program:

            if child.text:
                child.text = child.text.encode("utf-8")

            if child.tag == 'channel' and not child.text:
                p['channel'] = 'Ruutu'
            elif child.tag == 'length':
                p['length'] = convert_duration(child.text)
            elif child.tag == 'pubdate':
                d = parse_date(child.text)
                p['date'] = d
            else:
                p[child.tag] = child.text
        programs.append(p)
    programs.sort(key=lambda item:item['date'], reverse=True)
    return programs


def get_distinct_channels(programs=[], videotype='Kaikki'):
    channels = list(set([p['channel'] for p in programs \
        if (videotype == 'Kaikki' or p['type'] == videotype) \
        or (videotype == 'Sarjat' and p['series'])]))
    channels.sort()
    return channels


def get_distinct_series(programs=[], channel='Kaikki', videotype='Kaikki'):
    series = list(set([p['series'] for p in programs if p['series'] != None \
        and (videotype == 'Kaikki' or p['type'] == videotype) \
        and (channel == 'Kaikki' or p['channel'] == channel)]))
    series.sort()
    return series


def filter_programs(programs=[], videotype='Kaikki',\
        channel='Kaikki', series=None):
    cp = []
    for p in programs:
        if (channel == 'Kaikki' or p['channel'] == channel) \
        and (videotype == 'Kaikki' or p['type'] == videotype) \
        and (not series or p['series'] == series):
            cp.append(p)
    return cp


def parse_date(date_str):
    # Skipping timezone since '%z' is platform dependent
    date_str = date_str[:23]
    format = '%a, %d %b %y %H:%M:%S'
    try:
        d = datetime.strptime(date_str, format)
    except TypeError:
        timestamp = time.mktime(time.strptime(date_str, format))
        d = datetime.fromtimestamp(timestamp)
    return d


def convert_duration(duration_str):
    duration = duration_str.split(':')
    seconds = int(duration[0]) * 60 + int(duration[1])
    return seconds


def add_link(program):
    ok = True

    labels = {}
    labels["title"] = program["title"]
    if program["date"]:
        labels["dateadded"] = program["date"].strftime("%Y-%m-%d %H:%M:%S")
        labels["date"] = program["date"].strftime("%d.%m.%Y")
        labels["title"] += ' (' + \
            program["date"].strftime("%d.%m.") + ')'

    li = xbmcgui.ListItem(labels["title"],
            iconImage="DefaultVideo.png",
            thumbnailImage=program["thumbnail"])

    li.setInfo(type="Video", infoLabels=labels)

    if program["length"] and hasattr(li, "addStreamInfo"):
        li.addStreamInfo('video', {'duration': program["length"]})

    url = RTMP_PREFIX + program["origvideourl"]
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
            url=url, listitem=li)
    return ok


def add_dir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url)
    u += "&mode=" + str(mode)
    u += "&name=" + urllib.quote_plus(name)
    ok = True
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png",
            thumbnailImage=iconimage)
    li.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
            url=u, listitem=li, isFolder=True)
    return ok

# Saving these to cache
ruutuxml = cache.cacheFunction(fetch_ruutu_xml)
programs = cache.cacheFunction(parse_programs, ruutuxml)

#ruutuxml = fetch_ruutu_xml()
#programs = parse_programs(ruutuxml)

params = get_params()
url = None
name = None
mode = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None or url == None or len(url) < 1:
    print ""

    # Clear cache on plugin start
    cache.delete("%")
    ruutuxml = cache.cacheFunction(fetch_ruutu_xml)
    programs = cache.cacheFunction(parse_programs, ruutuxml)

    list_types()

elif mode == 1:
    m = 3
    if name == "Sarjat":
        m = 2
    c = get_distinct_channels(programs=programs, videotype=name)
    list_channels(channels=c, next_mode=m)

elif mode == 2:
    s = get_distinct_series(programs=programs, channel=name,
        videotype="Jaksot")
    list_series(series=s)

elif mode == 3:
    programs = filter_programs(programs=programs,
        channel=name, videotype="Jaksot")
    list_programs(programs=programs)

elif mode == 4:
    programs = filter_programs(programs=programs, series=name,
        videotype="Jaksot")
    list_programs(programs=programs)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
