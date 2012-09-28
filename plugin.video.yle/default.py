# vim: set fileencoding=utf8

import urllib, urllib2, sys, os
import feedparser
import xbmcplugin,xbmcgui,xbmc
import traceback
import yledl
from yledl import AreenaNGDownloader

# plugin handle
handle = int(sys.argv[1])



teemat={
	"TV-uutiset": "http://areena.yle.fi/.rss?q=uutiset&media=video",
	"Uusimmat ohjelmat": "http://areena.yle.fi/tv/kaikki.rss?jarjestys=uusin&media=video",
	"Ajankohtaisohjelmat": "http://areena.yle.fi/tv/dokumentit-ja-fakta/ajankohtaisohjelmat.rss",
	"Asiaviihde": "http://areena.yle.fi/tv/dokumentit-ja-fakta/asiaviihde.rss",
	"Luonto": "http://areena.yle.fi/tv/dokumentit-ja-fakta/luonto.rss"
	
}

def _start_media_thumbnail(self, attrsD):
	context = self._getContext()
	context.setdefault('media_thumbnail', [])
	context['media_thumbnail'].append(attrsD)

def getKeyboard(default = "", heading = "Hakusana", hidden = False):
	kboard = xbmc.Keyboard(default, heading, hidden)
	kboard.doModal()
	if (kboard.isConfirmed()):
		return urllib.quote_plus(kboard.getText())
	return default

class YleRssTitleAndUrlParser:
	def __init__(self):
		self.items=[]

	def parse(self, url):
		feedparser._FeedParserMixin._start_media_thumbnail = _start_media_thumbnail
		self.f = feedparser.parse(urllib2.urlopen(url))
		i = 0
		for e in self.f['entries']:
			if i < 2: print e
			i += 2
			print e.get('media_thumbnail')[0]['url']
			self.items.append((e.get('title'), e.get('link'), e.get('media_thumbnail')[1]['url']))
		return self.items

p=YleRssTitleAndUrlParser()

print sys.argv
request = {}

if not sys.argv[2]:
	for t in sorted(teemat):
		li = xbmcgui.ListItem(t, iconImage="DefaultFolder.png")
		url = sys.argv[0] + "?teema=" + urllib.quote_plus(t)
		xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
	it = xbmcgui.ListItem("Haku", iconImage="DefaultSearch.png")
	url = sys.argv[0] +"?search=hae"
	xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=it, isFolder=True)	
	xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
else:
	for r in str(sys.argv[2]).split('?')[-1].split('&'):
		key, val = r.split('=')
		request[key] = urllib.unquote_plus(val)

if 'teema' in request:
	teema = request['teema']
	items = p.parse(teemat[teema])
	for item in items:
		url = sys.argv[0] + "?item_url=" + item[1]
		li = xbmcgui.ListItem(item[0], iconImage=item[2])
		li.setInfo('video', {'Title': item[0]})
		li.setProperty("PageURL", item[1]);
		xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)
	xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

if 'search' in request:
	hakusana = getKeyboard()
	items = p.parse("http://areena.yle.fi/.rss?media=video&q=" + hakusana)
	print items
        for item in items:
                url = sys.argv[0] + "?item_url=" + item[1]
                li = xbmcgui.ListItem(item[0], iconImage=item[2])
                li.setInfo('video', {'Title': item[0]})
                li.setProperty("PageURL", item[1]);
                xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

if 'item_url' in request:
	print request
	item_url = request['item_url']
	areena = AreenaNGDownloader()
	try: 
		os.remove("/tmp/areenasub.fin.srt")
	except:
		pass
	output = areena.print_urls(item_url, False).rstrip()
	print output
	item = xbmcgui.ListItem("YLE");
	params = output.split(" ")
	skip = 0
	for param in params:
		skip+=1
		if skip != 1:
			print param.split("=",1)[0],param.split("=",1)[1]
			item.setProperty(param.split("=",1)[0], param.split("=",1)[1].replace(" ", ""))
	xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(item.getProperty("tcUrl")+"/"+item.getProperty("playpath") + output)
	xbmc.Player().setSubtitles('/tmp/areenasub.fin.srt')	



