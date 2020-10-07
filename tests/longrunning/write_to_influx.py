#!/usr/bin/env python3

import json
import os
import sys
import argparse
import glob
from influxdb import InfluxDBClient


parser = argparse.ArgumentParser(description='Writing test data to InfluxDB.')
parser.add_argument('-d', '--dbname', help='name of the database to use.')
parser.add_argument('-o', '--dbhost', help='host of influxdb.')
parser.add_argument('-p', '--dbport', help='port of influxdb.')
parser.add_argument('-u', '--dbuser', help='user of the database to use.')
parser.add_argument('-w', '--dbpasswd',
                    help='password of the given database user.')
parser.add_argument('-a', '--pathToDataDir',
                    help='path to the data directory.')
parser.add_argument('-m', '--mode', help='the testcase mode: single or cgp.')                                    
args = parser.parse_args()


def write_single(datadir, drop=False):
    client = InfluxDBClient(host=args.dbhost, port=args.dbport,
                            username=args.dbuser, password=args.dbpasswd, database=args.dbname)

    if drop:
        client.drop_measurement('qualitymetrics')

    with open(datadir + 'test_version_data.json') as json_file:
        version_data = json.load(json_file)

    eval_dir = datadir + 'eval/'
    for metric_file in glob.glob(eval_dir + '*.json'):
        with open(metric_file) as json_file:
            metric_data = json.load(json_file)

            # do not save the execution time as tag
            metric_data['execution_time'] = version_data['execution_time']
            
            json_body = [
                {
                    "measurement": "qualitymetrics",
                    "tags": {
                        'mode': 'single',
                        "hash": version_data['revision'],
                        'softmasking': version_data['softmasking'],
                        'testcase': os.path.basename(metric_file).replace('.json', '')
                    },
                    "time": version_data['commit_date'],
                    "fields": metric_data
                }
            ]

            client.write_points(json_body)
            # print(json_body)


def write_cgp(datadir, drop=False):
    client = InfluxDBClient(host=args.dbhost, port=args.dbport,
                            username=args.dbuser, password=args.dbpasswd, database=args.dbname)

    if drop:
        client.drop_measurement('qualitymetrics')

    with open(datadir + 'test_version_data.json') as json_file:
        version_data = json.load(json_file)

    eval_dir = datadir + 'ACCURACY/'
    for metric_file in glob.glob(eval_dir + '*.json'):
        with open(metric_file) as json_file:
            metric_data = json.load(json_file)

            # do not save the execution time as tag
            metric_data['execution_time'] = version_data['execution_time']
            
            json_body = [
                {
                    "measurement": "qualitymetrics",
                    "tags": {
                        'mode': 'cgp',
                        "hash": version_data['revision'],
                        'softmasking': version_data['softmasking'],
                        'testcase': os.path.basename(metric_file).replace('.json', '')
                    },
                    "time": version_data['commit_date'],
                    "fields": metric_data
                }
            ]

            client.write_points(json_body)
            # print(json_body)


def expand_dir(path):
    tmp = path
    if len(path)>0 and path[len(path)-1] != '/':
        tmp += '/'
    return tmp


if __name__ == '__main__':
    # drops the mesurement 'qualitymetrics' before writing
    # write(drop=True) # requires privilege to drop mesurement

    if args.dbname is None:
        print('The database to use is required, please make use of --dbname to pass the name of the database...')
        sys.exit()

    if args.dbhost is None:
        print('The host of influxdb is required, please make use of --dbhost to pass the host...')
        sys.exit()

    if args.dbport is None:
        print('The port of influxdb is required, please make use of --dbport to pass the name of the database...')
        sys.exit()

    if args.dbuser is None:
        print(
            'The database user is required, please make use of --dbuser to pass the user...')
        sys.exit()

    if args.dbpasswd is None:
        print('The password of the given user is required, please make use of --dbpasswd to pass the password...')
        sys.exit()

    if args.mode is None:
        print('The testcase mode (single or cgp) is required, please make use of --mode to pass the mode...')
        sys.exit()

    if args.pathToDataDir is None:
        print('The path to the data directory is required, please make use of --pathToDataDir to pass the path...')
        sys.exit()
    
    datadir = expand_dir(args.pathToDataDir)
    if not os.path.isdir(args.pathToDataDir):
        print('Given data folder ' +  datadir + ' not found!')
        sys.exit()

    if args.mode == 'single':
        write_single(datadir)
    elif args.mode == 'cgp':
        write_cgp(datadir)
    else:
        print('The mode must be \'cgp\' or \'single\'.')
        sys.exit()

