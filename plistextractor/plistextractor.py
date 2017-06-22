import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import logging
import m3u8
import helper


urllib3.disable_warnings()


class PListExtractor:
    def __init__(self, url, logger = None):
        self.url = url
        self.logger = logger or logging.getLogger(__name__)
        self.req_headers = { 'User-Agent': None, 'Accept': None,
                             'Accept-Encoding': 'gzip,deflate', 'Connection': 'keep-alive' }
        self.response = None


    @staticmethod
    def requestsRetrySession( retries=3, backoff_factor=0.3,
                              status_forcelist=(500, 502, 504), session=None, headers=None):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        if not( headers == None ):
            session.headers.update(headers)

        return session

    def _getFromURL(self, headers=None):
        r_header = headers or self.req_headers

        try:
            response = PListExtractor.requestsRetrySession(headers=r_header).get( self.url )
            if response.status_code == 200:
                self.response = response
            else:
                self.logger.warn("Getting from[" + self.url + "]: Response Error[" + str(response.status_code) + ']')

        except Exception as x:
            self.logger.warn("Getting from[" + self.url + "]: Response exception[" + str(x) + "]" )

        return self.response

    def _postToURL(self, headers=None, data=None):
        r_header = headers or self.req_headers

        try:
            response = PListExtractor.requestsRetrySession(headers=r_header).post( self.url, data )
            if response.status_code == 200:
                self.response = response
            else:
                self.logger.warn("Posting to[" + self.url + "]: Response Error[" + str(response.status_code) + ']')

        except Exception as x:
            self.logger.warn("Posting to[" + self.url + "]: Response exception[" + str(x) + "]" )

        return self.response

    def retrieveAndProcess(self):
        pass

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class indexPListExtr(PListExtractor):

    def retrieveAndProcess(self, headers=None):
        self._getFromURL(headers)

        if self.response == None or self.response.status_code != 200:
            return False

        if not self.response.text[:7] == "#EXTM3U":
            self.logger.warn("Not m3u playlist [" + self.url + "]")
            return False

        m3u8_obj = m3u8.loads(self.response.text)

        # print(m3u8_obj.__dict__)

        # Is this a variant playlist?
        # If yes, we extract the highest resolution stream

        live_plist_uri = self.url

        if m3u8_obj.is_variant:
            highest_res = 0

            for p in m3u8_obj.playlists:
                si = p.stream_info

                # bandwidth = si.bandwidth / (1024)
                # # quality = p.media[0].name
                # quality = p.media

                resolution = si.resolution if si.resolution else "?"
                uri = p.uri

                w, h = resolution
                if highest_res < h:
                    highest_res = h
                    live_plist_uri = uri

            # Is the plist_uri relative path or absolute path?
            live_plist_uri = helper.validateReturnURL( self.url, live_plist_uri )

            return {'plist_url': live_plist_uri, 'plist_array': None}

        else:
            # This is not a variant playlist. Should be the live playlist
            return {'plist_url': live_plist_uri, 'plist_array': m3u8_obj}


