#!/usr/bin/env python
import sys
from configmgr.configmanager import ConfigManager
from plistextractor.plistextractor import indexPListExtr
import helper
import time
import os
from dl_task.dl_task import download_file_by_curl
from datetime import datetime


def downloadSegments(plist_data, file_list, dest_dir):
    if not( plist_data.get('plist_array') and plist_data.get('plist_url')):
        return

    segments = plist_data['plist_array'].segments
    media_seq = int(plist_data['plist_array'].media_sequence)
    latest_datetime_str = datetime.now().strftime("%Y%m%d-%H-%M-%S-%f")

    # Download segments
    for item in segments:
        if not file_list.get( item.uri ):
            ts_url = helper.validateReturnURL( plist_data['plist_url'], item.uri )
            dest_file = str(media_seq) + '.ts'

            # print(ts_url)
            # print(os.path.join(dest_dir, dest_file))

            download_file_by_curl.apply_async((ts_url, os.path.join(dest_dir, dest_file)), expires=120)

            file_list[item.uri] = media_seq

        media_seq += 1
        
    # Download keys
    for key in plist_data['plist_array'].keys:
        if key:  # First one could be None
            key_uri = helper.validateReturnURL(plist_data['plist_url'], key.uri)

            key_filepath = os.path.join(dest_dir, latest_datetime_str) + '_key'
            download_file_by_curl.apply_async((key_uri, key_filepath), expires=120)


def main():
    if len(sys.argv) == 1:
        print 'No source URLs given.'
        sys.exit()

    # Get channel
    channel = sys.argv[1]
    cfgMgr = ConfigManager(channel)

    if not cfgMgr.load():
        sys.exit()

    # dest_url: this url can change
    dest_url = cfgMgr.url
    file_list = {}

    while True:
        plist_extr = indexPListExtr(dest_url, cfgMgr.logger)
        ret_plist = plist_extr.retrieveAndProcess()

        if not isinstance(ret_plist, dict):
            time.sleep(cfgMgr.fileduration)
            continue

        if ret_plist['plist_array']:
            downloadSegments(ret_plist, file_list, cfgMgr.destination)
        else:
            dest_url = ret_plist['plist_url']

        time.sleep(cfgMgr.fileduration)


if __name__ == '__main__':
    main()