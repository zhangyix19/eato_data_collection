from __future__ import annotations

import argparse
import os
import sys
import traceback

from helper import log, utils
from models.crawler import Crawler

sys.path.append('models')


if __name__ == '__main__':
    # Init
    SOCKS_PORT = utils.USED_SOCKS_PORT
    CONTROLLER_PORT = utils.USED_CONTROL_PORT

    # Parse arguments
    parser = argparse.ArgumentParser(description='Crawl a list of URLs in several batches.')

    # Add arguments
    parser.add_argument('--urls_closeworld', default='', type=str, help='Close world URLs file path')
    parser.add_argument('--urls_openworld', default='', type=str, help='Open world URLs file path')
    parser.add_argument('--batch', default=5, type=int, help='Number of batches')
    parser.add_argument('--output', default='output', type=str, help='Path of the output file')
    parser.add_argument('--tbbpath', default='../tbb/tor-browser_zh-CN', type=str, help='Path of tbb')
    parser.add_argument('--xvfb', default=False, type=bool, help='Use XVFB (for headless testing)')
    parser.add_argument('--screenshot', default=False, type=bool, help='Capture page screenshots)')
    parser.add_argument('--torrc_dir_path', default='', type=str, help='path to torrc config dir')
    parser.add_argument('--open_world', default='cw', type=str, help='close world(cw)/open world(ow)')
    parser.add_argument('--open_world_num', default=10000, type=int, help='open world num')
    parser.add_argument('--open_world_server_conf_path', default='', type=str, help='open_world_server_conf_path')
    parser.add_argument('--myexip', default='/root/myexip', type=str, help='path to myexip')

    args = parser.parse_args()

    # Load data
    urls_closeworld = args.urls_closeworld
    num_batches = args.batch
    output = args.output
    tbb_path = args.tbbpath
    xvfb = args.xvfb
    screenshot = args.screenshot
    urls_openworld = args.urls_openworld
    torrc_dir_path = args.torrc_dir_path
    is_open_world = args.open_world == 'ow'
    open_world_num = args.open_world_num
    open_world_server_conf_path = args.open_world_server_conf_path
    myexip = args.myexip

    urls_closeworld_list = []
    assert os.path.isfile(urls_closeworld)
    assert urls_closeworld
    with open(urls_closeworld, 'r') as fp:
        urls_closeworld_list = fp.read().splitlines()

    urls_openworld_list = []
    if is_open_world:
        assert os.path.isfile(urls_openworld)
        assert urls_openworld
        with open(urls_openworld, 'r') as fp:
            urls_openworld_list = fp.read().splitlines()
        for i in urls_closeworld_list:
            urls_openworld_list.remove(i) if i in urls_openworld_list else None

    assert os.path.isdir(torrc_dir_path)
    torrc_paths = [os.path.join(torrc_dir_path, torrc_path) for torrc_path in os.listdir(torrc_dir_path)]

    if is_open_world:
        assert os.path.isfile(myexip)
        assert os.path.isfile(open_world_server_conf_path)
        with open(myexip, 'r') as fp:
            myip = fp.read().splitlines()[0]
        open_world_servers_list = []
        with open(args.open_world_server_conf_path, 'r') as fp:
            open_world_servers_list = fp.read().splitlines()
        assert myip in open_world_servers_list
        open_world_start_index = int(open_world_num*(open_world_servers_list.index(myip)/len(open_world_servers_list)))
        open_world_end_index = int(
            (open_world_num*(open_world_servers_list.index(myip)+1)/len(open_world_servers_list)))
    else:
        open_world_start_index = 0
        open_world_end_index = 0

    crawler = Crawler(torrc_paths, urls_closeworld_list, urls_openworld_list, is_open_world, tbb_path,
                      output, xvfb, screenshot, open_world_start_index, open_world_end_index)
    print('INFO\tInit crawler finish in {}'.format(utils.cal_now_time()))
    print("INFO\tCommand line parameters: %s" % sys.argv)

    # Run the crawl

    try:
        print('INFO\tData Collection start in {}'.format(utils.cal_now_time()))
        print('INFO\tPredicted time: {:.1f} hours'.format((utils.WAIT_AFTER_DUMP+utils.INTERVAL_WAIT_AFTER_RESTART +
              utils.WAIT_FOR_VISIT)*len(urls_closeworld_list)*num_batches/3600))
        crawler.crawl(num_batches)
    except KeyboardInterrupt:
        log.wl_log.warning("WARNING\tKeyboard interrupt! Quitting in {}...".format(utils.cal_now_time()))
    except Exception as e:
        log.wl_log.error("ERROR\tException in {}: \n {}".format(utils.cal_now_time(), traceback.format_exc()))
    finally:
        crawler.stop_crawl()

    print('INFO\tData Collection done in {}'.format(utils.cal_now_time()))
