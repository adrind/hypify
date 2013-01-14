from urllib2 import urlopen
from bs4 import BeautifulSoup as BS
from argparse import ArgumentParser
from spotify.manager import (SpotifySessionManager, SpotifyPlaylistManager,
    SpotifyContainerManager)
from spotify import PlaylistContainer, SpotifyError
import sys

class Hypify(SpotifySessionManager):
    def __init__(self, *a, **kw):
        SpotifySessionManager.__init__(self, *a, **kw)
        self.pcntr = None
        self.pname = 'testing'
        self.current_p = None
        #self.pman = HypifyPlaylistManager()

    #called on login success
    def logged_in(self, session, error):
        if error:
            print error
        else:
            print "Success - logged in welcome " + str(session.display_name())
            self.pcntr = session.playlist_container()
            #creates playlist 'pname' if it doesn't already exist
            if not self.p_exists(self.pname):
                print "Making new playlist " + str(self.pname)
                self.pcntr.add_new_playlist(self.pname)
                self.current_p = self.pcntr[0]
            print "Grabbing"
            self.grab_tracks(session)

    #checks if pname is a playlist
    def p_exists(self, pname):
        for plist in self.pcntr:
            if plist.name() == self.pname:
                self.current_p = plist
                print "Found playlist " + str(self.pname)
                return True
        return False

    def connection_error(self, session, error):
        print error
        self.disconnect()

    #calls find_song for each song in parsed hypem xml
    def grab_tracks(self, session):
        url = "http://hypem.com/feed/loved/adrind/1/feed.xml"
        soup = BS(urlopen(url))
        titles = soup.findAll('title')[1:]
        songs = [self.parse_artist(title.string) for title in titles]
        songs = songs[:5]
        print "Found songs from adrind"
        for song in songs:
            print "Searching for " + str(song)
            session.search(str(song), self.find_song)
        self.disconnect()

    def parse_artist(self, song):
        artist, title = song.strip().split('-')
        return str(artist + title)

    def find_song(self, results, userdata):
        if results.tracks():
            tracks = results.tracks()
            print "Added a song to " + str(self.current_p.name())
            self.current_p.add_tracks(0, [tracks[0]])
        else:
            print "Could not find"

if __name__ == "__main__":
    parser=ArgumentParser(prog='hypify', description='Syncs Spotify and Hypem.')
    parser.add_argument('hypemid', nargs='?', default='adrind', metavar='hypem_userid', help="Spotify username")
    parser.add_argument("-u", "--username", help="Spotify username")
    parser.add_argument("-p", "--password", help="Spotify password")
    args=parser.parse_args(sys.argv)
    session = Hypify(args.username, args.password)
    print "Loggin in..."
    try:
        session.connect()
        print "Completed"
    except SpotifyError:
        print "Error: Must specify Spotify username/password"
    sys.exit()


