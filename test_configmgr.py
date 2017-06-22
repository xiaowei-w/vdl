import unittest
import os
from configmgr.configmanager import ConfigManager
import ConfigParser

class ConfigMgrTests(unittest.TestCase):

    def setUp(self):
        self.testA_cfg_psr = ConfigParser.RawConfigParser()
        self.testA_cfg_psr.add_section("test_a")
        self.testA_cfg_psr.set("test_a", "url", "http://www.google.com")
        self._oldenv = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._oldenv)

    def testSearchSettingValidParamsNoENV(self):
        self.assertEqual(ConfigManager.searchSetting(self.testA_cfg_psr, "test_a", "url"), "http://www.google.com", 'Invalid Param')

    def testSearchSettingValidENV(self):
        os.environ['TEST_ENV_URL'] = "http://yahoo.com"
        self.assertEqual(ConfigManager.searchSetting(self.testA_cfg_psr, "test_a", "url", "TEST_ENV_URL"), "http://yahoo.com", 'Test option error' )

    def testSearchSettingsNoParser(self):
        self.assertEqual(ConfigManager.searchSetting(None, "test_a", "url"), None, 'Test parser instance error' )

    def testSearchSettingsNotRawConfigParser(self):
        self.assertEqual(ConfigManager.searchSetting("NotRawConfigParserInstance", "test_a", "url"), None, 'Test parser instance error' )

    def testSearchSettingNoSection(self):
        self.assertEqual(ConfigManager.searchSetting(self.testA_cfg_psr, "test_b", "url"), None, 'Test section error' )

    def testSearchSettingNoOption(self):
        self.assertEqual(ConfigManager.searchSetting(self.testA_cfg_psr, "test_a", "uri"), None, 'Test option error' )

    def testSearchSettingInvalidENV(self):
        os.environ['INVALID_TEST_ENV_URL'] = "http://yahoo.com"
        self.assertEqual(ConfigManager.searchSetting(self.testA_cfg_psr, "test_a", "url", "TEST_ENV_URL"), "http://www.google.com", 'Test ENV error' )

def main():
    unittest.main()

if __name__ == '__main__':
    main()