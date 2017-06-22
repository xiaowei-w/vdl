import os
import ConfigParser
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


class ConfigManager:
    def __init__(self, channel):
        self.channel = channel
        self.destination = None
        self.fileduration = 5
        self.save_playlist = False
        self.url = None
        self.logger = None

    def setup_logging(self, config, title, section=None ):
        log_path = config.get('log', 'log_path') if config.has_option('log', 'log_path') else 'vlogs'
        log_path = os.path.join(os.getcwd(), log_path )

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        level = getattr(logging, config.get('log', 'level'))
        format = '%(asctime)s - %(levelname)s [{}] - %(message)s'.format(title)
        try:
            filename = config.get('log', 'filename')

            # filename = <section>_clog.txt
            filename = section + '_'+ filename

            filename = os.path.join( log_path, filename )

            handler = TimedRotatingFileHandler(filename, when='midnight', encoding='utf-8', interval=1)
            if config.has_option('log', 'suffix'):
                handler.suffix = config.get('log', 'suffix')

        except ConfigParser.NoOptionError:
            handler = logging.StreamHandler()

        handler.setFormatter(logging.Formatter(format))

        self.logger = logging.getLogger()
        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    @staticmethod
    def searchSetting(config_psr, configSection, configKey, envKey=None ):
        ret = None

        if not isinstance( config_psr, ConfigParser.RawConfigParser ):
            return ret

        if config_psr.has_option(configSection, configKey):
            ret = config_psr.get(configSection, configKey)

        # ENV supersede ConfigParser
        if envKey != None and os.environ.get(envKey) != None:
            ret = os.environ.get(envKey)

        return ret

    def load(self, path=None):
        if path is None:
            path = os.getenv('HLSCLIENT_CONFIG', os.getcwd() + '/' + 'config.ini')

        config_p = ConfigParser.RawConfigParser()
        try:
            with open(path) as f:
                config_p.readfp(f)
        except Exception as error:
            print "ConfigManager::load() " + str(error)
            return False

        if not config_p.has_section( self.channel ):
            print "ConfigManager::load() " + 'Channel ['+ str(self.channel) +'] is not available'
            return False

        self.setup_logging(config_p, "SOAP download", self.channel)

        # Lookup and create destination folder
        destination_base = ConfigManager.searchSetting(config_p, 'soap', 'destination_base', 'SOAP_DESTBASE')

        start_time_str = datetime.now().strftime("%Y%m%d-%H-%M-%S-%f")

        # Destination path format: <destination_base>/<channel>/<20120525-23-45-45-123456>
        self.destination = os.path.join(destination_base, self.channel, start_time_str)

        if not os.path.exists(self.destination):
            os.makedirs(self.destination)

        # URL
        self.url = ConfigManager.searchSetting(config_p, self.channel, 'playlist_path')

        # Delay Time
        self.fileduration = int(ConfigManager.searchSetting(config_p, self.channel, 'delay_time'))

        # Save Playlist?
        save_plist = ConfigManager.searchSetting(config_p, self.channel, 'save_playlist')
        self.save_playlist = True if save_plist == "1" else False


        return True
    
    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

