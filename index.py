#!/usr/bin/env python3
import requests
from termcolor import colored

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

SERVER_PARTIAL_PATH = '/on/demandware.servlet/WFS/StudioWS/Sites/'
WSDL_FOLDER_NAME = config['DEFAULT']['WEBREFERENCE_FOLDER']
WSDL_NAME = config['DEFAULT']['WSDL_FILE_NAME']  # without extension

GENERATE_JAVA_DOCS = config.getboolean('DEFAULT', 'GENERATE_JAVA_DOCS')

CURRENT_WORKING_DIR = os.getcwd()
DOWNLOADED_API_DOCS_NAME = WSDL_NAME + '.zip'
DOWNLOADED_API_DOCS_PATH = os.path.join(CURRENT_WORKING_DIR, DOWNLOADED_API_DOCS_NAME)
EXTRACT_ZIP_DIR = os.path.join(CURRENT_WORKING_DIR, 'output')

wsdl_file_location_on_server = None
if WSDL_FOLDER_NAME == 'webreferences':
    # webrefgen/webreferences/WSDL_NAME/WSDL_NAME.api.zip
    wsdl_file_location_on_server = 'webrefgen/webreferences/' + WSDL_NAME + '/' + WSDL_NAME + '.api.zip'
else:
    # webrefgen2/WSDL_NAME/WSDL_NAME.api.zip
    wsdl_file_location_on_server = 'webrefgen2/' + WSDL_NAME + '/' + WSDL_NAME + '.api.zip'

# e.g. https://HOSTNAME/on/demandware.servlet/WFS/StudioWS/Sites/webrefgen/webreferences/WSDL_NAME/WSDL_NAME.api.zip
WS_API_DOCS_URL = 'https://' + HOSTNAME + SERVER_PARTIAL_PATH + wsdl_file_location_on_server

print(colored('Going to download webservice api docs from url ' + WS_API_DOCS_URL, 'green'))


r = requests.get(WS_API_DOCS_URL, auth=(USERNAME, PASSWORD))

if (r.status_code != 200):
    status_code = r.status_code
    if status_code == 401:
        print(colored('401 : Unauthorized Request. Please check your credentials', 'red'))
    elif status_code == 404:
        print(colored('404 : incorrect wsdl or webservice api docs does not yet exists on the server', 'red'))
    else:
        print(colored('Error downloading webservice documentation form server. Http status code ' + str(r.status_code), 'red'))

    sys.exit(0)

# delete any already existing zip
if os.path.exists(DOWNLOADED_API_DOCS_PATH):
    os.remove(DOWNLOADED_API_DOCS_PATH)

if os.path.exists(EXTRACT_ZIP_DIR):
    shutil.rmtree(EXTRACT_ZIP_DIR)

# save the zip to local disk
with open(DOWNLOADED_API_DOCS_PATH, 'wb') as f:
    f.write(r.content)
print(colored('API docs zip downloaded to ' + DOWNLOADED_API_DOCS_PATH, 'green'))

# extract zip to local disk
with ZipFile(DOWNLOADED_API_DOCS_PATH, 'r') as zipObj:
    zipObj.extractall(EXTRACT_ZIP_DIR)
print(colored('API docs zip extracted to ' + EXTRACT_ZIP_DIR, 'green'))


if (GENERATE_JAVA_DOCS):
    API_DOCS_JAVA_FILES = EXTRACT_ZIP_DIR + os.path.sep + WSDL_FOLDER_NAME + os.path.sep + WSDL_NAME + os.path.sep

    # change current working directory so that is it easy to run javadoc command
    os.chdir(API_DOCS_JAVA_FILES)
    print(colored('changing current working directory to ' + API_DOCS_JAVA_FILES, 'green'))

    # /path/to/javadoc -d output_dir java_files_glob_pattern
    command = 'javadoc -d docs *.java'
    print(colored('generating java docs......', 'green'))
    output = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    DOCUMENTATION_LOCATION = os.path.join(API_DOCS_JAVA_FILES, 'docs')
    print(colored('javadoc generated under ' + DOCUMENTATION_LOCATION, 'green'))
else:
    print(colored('Javadoc generation disabled', 'yellow'))
