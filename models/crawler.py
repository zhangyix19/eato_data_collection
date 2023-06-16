from __future__ import annotations

import os
import random
import sys
import time
from shutil import copyfile

from selenium.common.exceptions import TimeoutException
from .torutils import TorController
from .visit import Visit

from helper import utils

sys.path.append('../..')


class Crawler():
    '''
    Provides methods to collect traffic traces.
    '''

    def __init__(self, torrc_paths: list[str], urls_closeworld_list: list[str], urls_openworld_list: list[str], open_world: bool, tbb_path: str, output: str, xvfb: bool = False, screenshot: bool = False, open_world_start_index: int = 0, open_world_end_index: int = 0, use_http: bool = False) -> None:
        # Create instance of Tor controller and sniffer used for the crawler
        self.crawl_dir: str
        self.crawl_logs_dir: str
        self.visit: Visit
        self.urls_closeworld = urls_closeworld_list
        self.urls_openworld = urls_openworld_list
        self.tbb_path = tbb_path
        self.xvfb = xvfb
        self.screenshot = screenshot
        self.open_world = open_world
        self.open_world_start_index = open_world_start_index
        self.open_world_end_index = open_world_end_index
        self.torrc_paths = torrc_paths
        self.use_http = use_http

        # Initializes
        self.init_crawl_dirs(output)
        self.tor_controller = TorController(tbb_path)

    def init_crawl_dirs(self, output):
        # Creates results and logs directories for this crawl.
        self.crawl_dir, self.crawl_logs_dir = self.create_crawl_dir(output)
        self.log_env_variables()

    def create_crawl_dir(self, output):
        # Create a timestamped crawl.
        if not os.path.exists(output):
            utils.create_dir(output)  # ensure that we've a results dir
        # 'output/crawl-xtab'
        crawl_dir_wo_ts = os.path.join(output, 'crawl')
        # 'output/crawl+timestamped'
        crawl_dir = utils.create_dir(crawl_dir_wo_ts)
        # 'output/crawl+timestamped/logs'
        crawl_logs_dir = os.path.join(crawl_dir, 'logs')
        utils.create_dir(crawl_logs_dir)
        return crawl_dir, crawl_logs_dir

    def log_env_variables(self):
        # Dump my IP and the roter IP
        with open(os.path.join(self.crawl_dir, "ip"), "w") as f:
            f.write(f"{utils.MY_IP}\n")
            f.write(f"{utils.USED_GATEWAY_IP}\n")

        # Dump now timestamp
        with open(os.path.join(self.crawl_dir, "timestamp"), "w") as f:
            f.write(str(int(time.time())))

        # Copy torrc
        for torrc_path in self.torrc_paths:
            copyfile(torrc_path, os.path.join(
                self.crawl_dir, os.path.basename(torrc_path)))

        # Dump utils
        copyfile(utils.__file__, os.path.join(self.crawl_dir, "utils.py"))

        # Dump settings
        with open(os.path.join(self.crawl_dir, "settings"), "w") as f:
            for torrc_path in self.torrc_paths:
                f.write(torrc_path+"\n")
            f.write("open_world: "+str(self.open_world)+"\n")

        # Dump urllist
        with open(os.path.join(self.crawl_dir, "urls-crawled.csv"), 'w') as f:
            if self.open_world:
                [f.write(
                    i+'\n') for i in self.urls_openworld[self.open_world_start_index:self.open_world_end_index]]
            else:
                [f.write(i+'\n') for i in self.urls_closeworld]

    def crawl(self, num_batches=10):
        activate_torrc_path = None
        url_list = self.urls_openworld[self.open_world_start_index:
                                       self.open_world_end_index] if self.open_world else self.urls_closeworld
        # for each batch
        print("INFO\tCrawl configuration: batches: {0}, number: {1}, crawl dir: {2}".format
              (num_batches, len(url_list), self.crawl_dir))

        for batch_num in range(num_batches):
            print("INFO\tStarting batch {} in {}".format(
                batch_num, utils.cal_now_time()))
            site_num = 0
            batch_dir = utils.create_dir(os.path.join(
                self.crawl_dir, 'batch-'+str(batch_num)))

            # sites_crawled_with_same_proc = 0
            random.shuffle(url_list)
            for page_url in url_list:
                print('INFO\tCrawling {} url: {} in {}'.format(
                    site_num, page_url, utils.cal_now_time()))
                url_dir = utils.create_dir(
                    os.path.join(batch_dir, 'url-'+str(site_num)))

                with open(os.path.join(url_dir, 'label'), 'w') as fp:
                    fp.write(page_url+'\n')

                self.visit = None
                try:
                    print("INFO\tInit visit in {}".format(utils.cal_now_time()))
                    self.visit = Visit(page_url, url_dir,
                                       self.tor_controller, self.tbb_path, self.xvfb, self.screenshot)
                    print("INFO\tStart visit in {}".format(utils.cal_now_time()))
                    start_time = time.time()
                    self.visit.get()
                    end_time = time.time()
                    with open(os.path.join(url_dir, 'time'), 'w') as fp:
                        fp.write(f'{start_time}\n')
                        fp.write(f'{end_time}\n')

                except KeyboardInterrupt:  # CTRL + C
                    raise KeyboardInterrupt
                except TimeoutException as exc:
                    print("CRITICAL\tVisit timed out! %s %s" % (exc, type(exc)))
                    if self.visit:
                        self.visit.cleanup_visit()
                except Exception as exc:
                    print("CRITICAL\tException crawling: %s" % exc)
                    if self.visit:
                        self.visit.cleanup_visit()
                # END - for each visit
                site_num += 1
                time.sleep(utils.INTERVAL_BETWEEN_VISIT)

    def stop_crawl(self, pack_results=True):
        """ Cleans up crawl and kills tor process in case it's running."""
        print("Stopping crawl...")
        if self.visit:
            self.visit.cleanup_visit()


if __name__ == "__main__":
    print('test')
