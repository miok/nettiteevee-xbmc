# vim: set fileencoding=utf8

import urllib, urllib2, sys, os
import xml.parsers.expat
import xbmcplugin,xbmcgui,xbmc


# plugin handle
handle = int(sys.argv[1])

teemat={
	"Ruutu uusimmat jaksot": "http://feeds.feedburner.com/Ruutufi-Uusimmat-Jaksot",
	"Ruutu uusimmat klipit": "http://feeds.feedburner.com/Ruutufi-Uusimmat-Klipit",
	"Nelonen uusimmat jaksot": "http://feeds.feedburner.com/NelonenNettiTVUusimmat",
	"Nelonen uusimmat klipit": "http://feeds.feedburner.com/NelonenNettitvUusimmatKlipit",
	"Jim uusimmat jaksot": "http://feeds.feedburner.com/JimNettitv",
	"Liv uusimmat jaksot": "http://feeds.feedburner.com/LivNettitvUusimmatSarjat",
}

class RssTitleAndUrlParser:
	def __init__(self):
		self.in_item=False
		self.in_title=False
		self.in_link=False
		self.items=[]
		self.p = xml.parsers.expat.ParserCreate()
		self.p.StartElementHandler = self.start_element
		self.p.EndElementHandler = self.end_element
		self.p.CharacterDataHandler = self.char_data

	def start_element(self, name, attrs):
		if name=="rss":
			self.items=[]
		if name=="item":
			self.in_item=True
			self.title=str()
			self.link=str()
		if self.in_item and name=="title":
			self.in_title=True
		if self.in_item and name=="link":
			self.in_link=True

	def end_element(self, name):
		if name=="item":
			self.in_item=False
			self.items.append((self.title, self.link))
		if self.in_item and name=="title":
			self.in_title=False
		if self.in_item and name=="link":
			self.in_link=False
			
	def char_data(self, data):
		if self.in_title: self.title = self.title + data
		if self.in_link: self.link = self.link + data

	def parse(self, url):
		self.p.ParseFile(urllib2.urlopen(url))
		return self.items

p=RssTitleAndUrlParser()

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
		li.setInfo('video', {'Title': item[0], 'Genre': ''})
		li.setProperty("PageURL", item[1]);
		xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)
	xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

if 'item_url' in request:
	item_url = request['item_url']
	progId = urllib2.urlopen(item_url).geturl().split("=")[-1]
	try:
		itemi = xbmcgui.ListItem("Ruutu.fi video");
		itemi.setProperty("PlayPath", "mp4:" + progId + ".mp4")
		itemi.setProperty("SWFPlayer", "http://n.sestatic.fi/sites/all/modules/media/Nelonen_mediaplayer_static_latest.swf")
		itemi.setProperty("PageURL", "http://www.ruutu.fi/video?vt=video_episode&vid=" + progId)
		xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play("rtmp://streamh1.nelonen.fi/vod", itemi)
	except Exception, err:
		print "Error" + str(err)
		

