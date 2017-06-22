from celery import Celery
import subprocess
import os
import requests
import csv
from datetime import datetime
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)

app = Celery('dl_task', broker='redis://localhost:6379/0')


@app.task(ignore_result=True)
def download_file(url, download_location):
    FNULL = open(os.devnull, 'w')
    logger.info('[' + str(datetime.now()) + ']' + ' Starting download [' + url + ']')
    args = ['wget', '-q', '-b', '-t', '6', '--read-timeout', '5', '--waitretry', '5', '--user-agent', ' ', '-O', download_location, url]
    output = subprocess.Popen(args, stdout=FNULL)
    # output = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = output.communicate()

    # if stdout:
    #     logger.info(stdout)
    # if stderr:
    #     logger.error(stderr)


@app.task(ignore_result=True)
def download_file_by_curl(url, download_location):
    FNULL = open(os.devnull, 'w')
    logger.info('[' + str(datetime.now()) + ']' + ' Starting download [' + url + ']')
    args = ['curl', '-s', '-H', 'User-Agent: ', '-H', 'Accept-Encoding: gzip,deflate', 
            '-H', 'Connection: keep-alive', '-H', 'Accept: ', '-o', download_location, '-D', download_location+'.txt', url]
    output = subprocess.Popen(args, stdout=FNULL)
    # output = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = output.communicate()

    # if stdout:
    #     logger.info(stdout)
    # if stderr:
    #     logger.error(stderr)


@app.task(ignore_result=True)
def get_download_len(url, csv_location):
    headers = { 'User-Agent': None }
    try:
        resp = requests.head(url, timeout=5, headers=headers)
        if resp.status_code == 200:
            with open(csv_location,'ab') as f:
                csv_ptr = csv.writer(f)
                csv_ptr.writerow( ( '[' + str(datetime.now()) + ']', url, "Content-length[" + str(resp.headers['content-length']) + ']' ) )
        else:
            logger.warn('[' + str(datetime.now()) + ']' + ' Error: [' + url + '] Status Code: {'+ str( resp.status_code ) + '}')
    
    except requests.exceptions.RequestException as e:
        logger.warn(e)
    except requests.exceptions.ConnectionError as e:
        logger.warn(e)
    except requests.exceptions.HTTPError as e:
        logger.warn(e)
    except requests.exceptions.TooManyRedirects as e:
        logger.warn(e)
    except requests.exceptions.Timeout as e:
        logger.warn(e)
