#!/usr/bin/env python

'''
dyn_ip_chk
A dynamic IP checker script.
written by Jared Epstein
###
Planned Features:
    -add daemonizing (-d)
        -won't allow -o with daemon (only logging)
        -add a new option that will alert (email?) if IP changes
###
Known Issues:
    -must be run with sudo for logging to work
'''

#IMPORTS - built-ins
import optparse
import sys
import os
import time
import urllib2
import json
import logging
import logging.handlers

# CONSTANTS
# basics
NAME = "dyn_ip_chk"
VER = "0.0.1"
HOST = os.uname()[1]
PID = os.getpid()
PIDFILE = "/var/run/" + NAME + ".pid"
# logging
LOG_FILE = "/var/log/" + NAME + ".log"
LOG_ROLLOVER_BYTES = 500000  # 500KB
LOG_ROLLOVER_COUNT = 10
# args
DESC = "dyn_ip_chk will query for the public IP and log what it finds"
EPILOG = """
Version: %(ver)s
""" % {'ver': VER}

# ARGS
parser = optparse.OptionParser(description=DESC, epilog=EPILOG)
parser.add_option(
    '-V',
    '--version',
    help='print version and exit',
    dest="version",
    default=False,
    action="store_true")
parser.add_option(
    '-v',
    '--verbose',
    help='enable verbose logging',
    dest="verbose",
    default=False,
    action="store_true")
parser.add_option(
    '-o',
    '--out',
    help='output response to stdout',
    dest="out",
    default=False,
    action="store_true")

options, args = parser.parse_args()  # set up argument parser

if options.version:  # no need to go further if this is all we want
    print(VER)
    sys.exit()
 
# LOGGING
try:
    basedir = os.path.dirname(LOG_FILE)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
        log_create = True
except Exception:
    log_create = False

try:
    scr_logger = logging.getLogger(NAME)
    scr_logger.setLevel(logging.DEBUG)
    scr_fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_ROLLOVER_BYTES,
        backupCount=LOG_ROLLOVER_COUNT)
    scr_fh.setLevel(logging.DEBUG)
    scr_formatter = logging.Formatter(
        '%(asctime)s ' + HOST + ' ' + NAME +
        '[' + str(PID) + ']: %(message)s',
        "%Y-%m-%dT%H:%M:%S" + time.strftime('%z'))
    scr_fh.setFormatter(scr_formatter)
    scr_logger.addHandler(scr_fh)
    log_create = True
except Exception:
    log_create = False

# METHODS
def read_site(site,hdr):
    '''
    pulls content from provided site and returns content
    returns error if the request fails
    '''
    if options.verbose:
        if log_create == True:
            scr_logger.info("read_site()")
    req = urllib2.Request(site, headers=hdr)
    try:
        page = urllib2.urlopen(req)
        content = page.read()
    except urllib2.HTTPError, e:
        content = e.fp.read()
        if options.verbose:
            if log_create == True:
                scr_logger.info("read_site() failed: " + content)
    return content

def parse_response(content):
    '''
    parses json provided from read_site()
    if read_site() failed to pull json, this will return None
    '''
    if options.verbose:
        if log_create == True:
            scr_logger.info("parse_response()")
    try:
        load = json.loads(content)
        ip = load["ip"]
        return ip
    except Exception:
        return None

# MAIN
def main(argv):  # main script wrapper function
    if log_create == True:
        scr_logger.info("Starting dyn_ip_chk")
    site = "https://api.ipify.org/?format=json"
    hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    ip_address = parse_response(read_site(site,hdr))
    if ip_address != None:
        if log_create == True:
            scr_logger.info("Public IP address is: " + ip_address)
        if options.out:
            print(ip_address)
    else:
        if log_create == True:
            scr_logger.info("Failed to retrieve public IP") 
        if options.out:
            print("Failed to retrieve public IP")

if __name__ == "__main__":
    main(sys.argv[1:])