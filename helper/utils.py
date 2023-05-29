import os
import re
from time import strftime
import distutils.dir_util as du
import sys
import signal
import shutil
import psutil
import time
from pyvirtualdisplay.display import Display

# Need modify for different server
# geckodrive_path = '/root/wfp/geckodriver'  # geckodriver path
MY_IP = "myip"    # The host ip (run 'ifconfig' in terminal)

USED_GATEWAY_IP = "routeip"  # run 'route -n' in terminal
LOCALHOST_IP = "127.0.0.1"   # default localhost IP (run 'ifconfig' in terminal)

# Hyperparameter
STREAM_CLOSE_TIMEOUT = 5     # wait 5 seconds before raising an alarm signal
INTERVAL_BETWEEN_VISIT = 1  # Interval time between instances
WAIT_AFTER_DUMP = 5          # Waiting time after opening dumpcap

INTERVAL_WAIT_FOR_LAUNCH = 30
INTERVAL_WAIT_AFTER_RESTART = 20
INTERVAL_WHEN_TOR_LAUNCH_ERROR = 1

# BOTH < INTERVAL_DUMP - INTERVAL_WAIT_FOR_RESTART - INTERVAL_BETWEEN_VISIT
# BOTH < SOFT_VISIT_TIMEOUT
WAIT_FOR_VISIT = 120          # Waiting time for each url
WAIT_FOR_VISIT_ONION = 240    # Waiting time for each onion url (onion sites are slower)

SOFT_VISIT_TIMEOUT = 200     # timeout used by selenium and dumpcap
HARD_VISIT_TIMEOUT = SOFT_VISIT_TIMEOUT + 10  # signal based hard timeout in case soft timeout fails


# Constant
DEFAULT_SOCKS_PORT = 9050  # SYSTEM TOR PORTS
DEFAULT_CONTROL_PORT = 9051
TBB_SOCKS_PORT = 9150  # TBB TOR PORTS
TBB_CONTROL_PORT = 9151
STEM_SOCKS_PORT = 9250  # STEM port
STEM_CONTROL_PORT = 9251
USED_SOCKS_PORT = DEFAULT_SOCKS_PORT
USED_CONTROL_PORT = DEFAULT_CONTROL_PORT

DEFAULT_XVFB_WIN_W = 1280  # Default dimensions for the virtual display
DEFAULT_XVFB_WIN_H = 800


def start_xvfb(win_width=DEFAULT_XVFB_WIN_W,
               win_height=DEFAULT_XVFB_WIN_H):
    """Start and return virtual display using XVFB."""
    print("INFO\tStarting XVFB: {} x {}".format(win_width, win_height))
    xvfb_display = Display(visible=False, size=(win_width, win_height))
    xvfb_display.start()
    return xvfb_display


def stop_xvfb(xvfb_display):
    """Stop the given virtual display."""
    if xvfb_display:
        xvfb_display.stop()


class TimeExceededError(Exception):
    pass


def cal_now_time(_flag=False):
    res_time = None
    if _flag:
        res_time = time.time()
    else:
        stamp = time.localtime(time.time())
        res_time = time.strftime("%Y-%m-%d %H:%M:%S", stamp)
    return res_time


def create_dir(dir_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def append_timestamp(_str=''):
    """Append a timestamp to a string and return it."""
    return _str + strftime('%y%m%d_%H%M%S')


def clone_dir_with_timestap(orig_dir_path):
    """Copy a folder into the same directory and append a timestamp."""
    new_dir = create_dir(append_timestamp(orig_dir_path))
    try:
        du.copy_tree(orig_dir_path, new_dir)
    except Exception as e:
        print("ERROR\tError while cloning the dir with timestamp" + str(e))
    finally:
        return new_dir


def get_filename_from_url(url, prefix):
    """Return base filename for the url."""
    url = url.replace('https://', '')
    url = url.replace('http://', '')
    url = url.replace('www.', '')
    dashed = re.sub(r'[^A-Za-z0-9._]', '-', url)
    return '%s-%s' % (prefix, re.sub(r'-+', '-', dashed))


def cancel_timeout():
    """Cancel a running alarm."""
    signal.alarm(0)


def gen_all_children_procs(parent_pid):
    parent = psutil.Process(parent_pid)
    for child in parent.children(recursive=True):
        yield child


def raise_signal(signum, frame):
    raise TimeExceededError


def timeout(duration):
    """Timeout after given duration."""
    signal.signal(signal.SIGALRM, raise_signal)  # linux only !!!
    signal.alarm(duration)  # alarm after X seconds


def kill_all_children(parent_pid):
    """Kill all child process of a given parent."""
    for child in gen_all_children_procs(parent_pid):
        child.kill()


if __name__ == "__main__":
    print('test')
