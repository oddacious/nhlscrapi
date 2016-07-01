
import requests

from nhlscrapi.scrapr.datacontainer import DataContainer

class NHLCn(object):
    """
    Builds the URLs, makes the HTTP calls and retreives the raw HTML and/or JSON associated with various NHL 
    report data. If an error occurs in the retrieval process, the error is recorded in ``req_err``.
    """
    __domain = 'http://www.nhl.com/'
    __old_json_domain = 'http://live.nhl.com/'
    __new_json_domain = 'http://statsapi.web.nhl.com/'

    def __init__(self):
        self.html_src = None
        """The HTML source of the last NHL page requested."""
        self.json_src = None
        """The JSON source of the last NHL page requested."""
        self.req_err = None
        """Error from the last HTTP request."""

    def __html_rep(self, game_key, rep_code):
        """Retrieves the nhl html reports for the specified game and report code"""
        seas, gt, num = game_key.to_tuple()
        url = [ self.__domain, "scores/htmlreports/", str(seas-1), str(seas),
                "/", rep_code, "0", str(gt), ("%04i" % (num)), ".HTM" ]
        url = ''.join(url)

        return self.__open(url)

    def __json_feed(self, game_key):
        """Retrieves the NHL json reports for the specified game and report code - Currently only Play-by-play is
        available"""
        seas, gt, num = game_key.to_tuple()

        # E.g. http://live.nhl.com/GameData/20132014/2013021226/PlayByPlay.json
        # url = [ self.__old_json_domain, "GameData/", str(seas-1), str(seas),
        #        "/", str(seas-1), "0", str(gt), ("%04i" % (num)), "/", "PlayByPlay", ".json" ]

        # E.g. http://statsapi.web.nhl.com/api/v1/game/2013021226/feed/live
        # This source is more informative (includes blocks and faceoffs, for example)
        url = [ self.__new_json_domain, "/api/v1/game/", str(seas-1), "0", str(gt), ("%04i" % (num)), "/feed/live" ]
        url = ''.join(url)

        return self.__open(url, text_type='JSON')


    def game_roster(self, game_key):
        """
        :returns: raw HTML for game rosters (RO)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'RO'))

    def rtss(self, game_key):
        """
        :returns: raw HTML for RTSS play by play (PL)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'PL'),
                json=self.__json_feed(game_key))

    def home_toi(self, game_key):
        """
        :returns: raw HTML for home TOI by player (TH)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'TN'))

    def away_toi(self, game_key):
        """
        :returns: raw HTML for away TOI by player (TV)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'TV'))

    def face_offs(self, game_key):
        """
        :returns: raw HTML for face off comparisons (FC)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'FC'))

    def shootout(self, game_key):
        """
        :returns: raw HTML for the game's shootout (SO)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'SO'))

    def game_summary(self, game_key):
        """
        :returns: raw HTML for game summary report (GS)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'GS'))

    def event_summary(self, game_key):
        """
        :returns: raw HTML for the event summary report (ES)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'ES'))

    def shot_summary(self, game_key):
        """
        :returns: raw HTML for the shot summary report (SS)
        :rtype: string
        """
        return DataContainer(html=self.__html_rep(game_key, 'SS'))

    def __open(self, url, text_type='HTML'):
        req = None
        try:
            req = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'
            })
            if text_type == 'HTML':
                self.html_src = req.text
            elif text_type == 'JSON':
                self.json_src = req.text
            else:
                raise ValueError("Unsupported content type: %s" + str(text_type))
        except Exception as e:
            self.req_err = e

        if text_type == 'HTML':
            return self.html_src
        elif text_type == 'JSON':
            return self.json_src
