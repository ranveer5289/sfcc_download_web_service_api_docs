#!/usr/bin/env python3
import requests
from zipfile import ZipFile
import sys
import os
import subprocess
import shutil
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

HOSTNAME = config['DEFAULT']['HOSTNAME']
USERNAME = config['DEFAULT']['USERNAME']
PASSWORD = config['DEFAULT']['PASSWORD']

SERVER_PARTIAL_PATH = '/on/demandware.servlet/WFS/StudioWS/Sites'
WSDL_FOLDER_NAME = config['DEFAULT']['WEBREFERENCE_FOLDER']
WSDL_NAME = config['DEFAULT']['WSDL_FILE_NAME'] # without extension

GENERATE_JAVA_DOCS = config.getboolean('DEFAULT', 'GENERATE_JAVA_DOCS')

CURRENT_WORKING_DIR = os.getcwd()
DOWNLOADED_API_DOCS_NAME = WSDL_NAME + '.zip'
DOWNLOADED_API_DOCS_PATH = os.path.join(CURRENT_WORKING_DIR, DOWNLOADED_API_DOCS_NAME)
EXTRACT_ZIP_DIR = os.path.join(CURRENT_WORKING_DIR, 'output')

WS_FILE_LOCATION_PREFIX = None
if WSDL_FOLDER_NAME == 'webreferences':
    WS_FILE_LOCATION_PREFIX = 'webrefgen/webreferences/' + WSDL_NAME + '/' + WSDL_NAME + '.api.zip'
else:
    WS_FILE_LOCATION_PREFIX = 'webrefgen2/' + WSDL_NAME + '/' + WSDL_NAME + '.api.zip'

WS_API_DOCS_URL = 'https://' + HOSTNAME + SERVER_PARTIAL_PATH + '/' + WS_FILE_LOCATION_PREFIX

print('Going to download webservice api docs from url ' + WS_API_DOCS_URL)


r = requests.get(WS_API_DOCS_URL, auth=(USERNAME, PASSWORD))

if (r.status_code != 200):
    print('Error downloading webservice documentation form server. Http status code ' + str(r.status_code))
    sys.exit(0)

if os.path.exists(DOWNLOADED_API_DOCS_PATH):
    os.remove(DOWNLOADED_API_DOCS_PATH)

if os.path.exists(EXTRACT_ZIP_DIR):
    shutil.rmtree(EXTRACT_ZIP_DIR)

with open(DOWNLOADED_API_DOCS_PATH, 'wb') as f:
    f.write(r.content)
print('API docs zip downloaded to ' + DOWNLOADED_API_DOCS_PATH)

with ZipFile(DOWNLOADED_API_DOCS_PATH, 'r') as zipObj:
   zipObj.extractall(EXTRACT_ZIP_DIR)

print('API docs zip extracted to ' + EXTRACT_ZIP_DIR)

if (GENERATE_JAVA_DOCS):
    API_DOCS_JAVA_FILES = EXTRACT_ZIP_DIR + os.path.sep + WSDL_FOLDER_NAME + os.path.sep + WSDL_NAME + os.path.sep

    os.chdir(API_DOCS_JAVA_FILES)
    print('change current working directory to ' + API_DOCS_JAVA_FILES)

    # /path/to/javadoc -d output_dir java_files_glob_pattern
    command = 'javadoc -d docs *.java'
    print('generating java docs')
    output = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    DOCUMENTATION_LOCATION = os.path.join(API_DOCS_JAVA_FILES, 'docs')
    print('javadoc generated ' + DOCUMENTATION_LOCATION)
else:
    print('Javadoc generation disabled')
