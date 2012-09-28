# vim: set fileencoding=utf8

import urllib, urllib2, sys, os
import feedparser
import xbmcplugin,xbmcgui,xbmc
import traceback
import re

# plugin handle
handle = int(sys.argv[1])
teemat={
        "Uutiset ja fakta": "http://www.katsomo.fi/feed/rss.do?ref=uutiset_uusimmat",
        "Urheilu": "http://www.katsomo.fi/feed/rss.do?ref=urheilu_uusimmat",
        "Viihde ja sarjat": "http://www.katsomo.fi/feed/rss.do?ref=viihdeohjelmat_uusimmat",
        "Lifestyle": "http://www.katsomo.fi/feed/rss.do?ref=lifestyleohjelmat_uusimmat"	
	
}

def _start_media_thumbnail(self, attrsD):
    		context = self._getContext()
    		context.setdefault('media_thumbnail', [])
    		context['media_thumbnail'].append(attrsD)


class KatsomoUrlParser:
	def __init__(self):
		self.items=[]

	def parse(self, url):
		feedparser._FeedParserMixin._start_media_thumbnail = _start_media_thumbnail
		self.f = feedparser.parse(urllib2.urlopen(url))
		i = 0
		print self.f
		for e in self.f['entries']:
			print e
			print e.get('enclosure')
			self.items.append((e.get('title'), e.get('link')))
		return self.items

p=KatsomoUrlParser()

print sys.argv
request = {}

if not sys.argv[2]:
	for t in sorted(teemat):
		li = xbmcgui.ListItem(t, iconImage="DefaultFolder.png")
		url = sys.argv[0] + "?teema=" + urllib.quote_plus(t)
		xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
	xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
else:
	for r in str(sys.argv[2]).split('?')[-1].split('&'):
		key, val = r.split('=')
		request[key] = urllib.unquote_plus(val)

if 'teema' in request:
	teema = request['teema']
	items = p.parse(teemat[teema])
	for item in items:
		url = sys.argv[0] + "?item_url=" + urllib.quote(item[1])	
		li = xbmcgui.ListItem(item[0], iconImage="DefaultFolder.png")
		li.setInfo('video', {'Title': item[0]})
		li.setProperty("PageURL", item[1]);
		xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)
	xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
if 'item_url' in request:
	item_url = request['item_url']
	progId = item_url.split("=")[-1]
	firstUrl = "http://www.mtv3nettitv.fi/metafile.asx?p=" + progId + "&bw=40000"
	urlData = urllib2.urlopen(firstUrl).read()
	reg =  re.compile("\"(.*)\"")
	streamUrl = reg.findall(urlData)[-1]
	item = xbmcgui.ListItem("Katsomo")
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(streamUrl)

