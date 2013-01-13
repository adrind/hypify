from urllib2 import urlopen
from bs4 import BeautifulSoup as BS
from argparse import ArgumentParser
from spotify.manager import (SpotifySessionManager, SpotifyPlaylistManager,
    SpotifyContainerManager)
from spotify import PlaylistContainer
import sys




class Hypify(SpotifySessionManager):
    def __init__(self, *a, **kw):
        SpotifySessionManager.__init__(self, *a, **kw)
        self.pcntr = None
        self.pname = 'testing'
        #self.pman = HypifyPlaylistManager()

    def logged_in(self, session, error):
        if error:
            print error
        else:
            print "Success - logged in welcome " + str(session.display_name())
            self.pcntr = session.playlist_container()
            if not self.p_exists:
                self.pcntr.add_new_playlist(self.pname)
            print "Watched"
            self.grab_tracks(session)
            print "Added"

    def p_exists(self, pname):
        for plist in self.pcntr:
            if plist.name() == self.pname:
                return True
        return False

    def connection_error(self, session, error):
        print error
        self.disconnect()

    def grab_tracks(self, session):
        url = "http://hypem.com/feed/loved/adrind/1/feed.xml"
        soup = BS(urlopen(url))
        titles = soup.findAll('title')[1:]
        songs = [self.parse_artist(title.string) for title in titles]
        songs = songs[:5]
        print "Found songs"
        for song in songs:
            print "Searching for " + str(song)
            session.search(str(song), self.find_song)
        self.disconnect()

    def parse_artist(self, song):
        artist, title = song.strip().split('-')
        return str(artist)

    def find_song(self, results, userdata):
        if results.tracks():
            tracks = results.tracks()
            print "Added a song to " + str(self.pcntr[0].name())
            self.pcntr[0].add_tracks(0, [tracks[0]])
        else:
            print "Could not find"

if __name__ == "__main__":
    parser=ArgumentParser(prog='hypify', description='Syncs Spotify and Hypem.')
    parser.add_argument('hypemid', nargs='?', default='adrind', metavar='hypem_userid', help="Spotify username")
    parser.add_argument("-u", "--username", help="Spotify username")
    parser.add_argument("-p", "--password", help="Spotify password")
    args=parser.parse_args(sys.argv)
    session = Hypify(args.username, args.password)
    print "Loggin in"
    session.connect()
    print "Complete"
    sys.exit()


