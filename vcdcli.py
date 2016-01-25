#!/usr/bin/env python

from pprint import pprint
import requests
import base64
import xml.etree.ElementTree as ET
import time, datetime, os
import sys
from prettytable import PrettyTable
import argparse
    

def login_VCD(l_user,l_password,l_org,l_url):
    f_http = os.popen("http --session=vcloud -a " + l_user + "@" + l_org + ":" + l_password +" POST " + l_url + "/sessions 'Accept:application/*+xml;version=5.1'")
    f_xmldata = f_http.read()

def display_vapp(l_url):
    f_http = os.popen('http --session=vcloud GET ' + l_url + '/vApps/query?pageSize=200')
    xmldata = f_http.read()
    tree = ET.fromstring(xmldata)

    t_vapp = PrettyTable(['Vapp Name', 'CPU', 'Ram (MB)', 'Storage (KB)', 'Status', 'Deployed', 'Vdc'])
    t_vapp.align['Vapp Name'] = 'l'

    for elem in tree.iter(tag='{http://www.vmware.com/vcloud/v1.5}VAppRecord'):
        vappName = elem.attrib.get('name')
        vappStatus =  elem.attrib.get('status')
        vappDeploy =  elem.attrib.get('isDeployed')
        vappVdc =  elem.attrib.get('vdcName')
        vappCPU =  elem.attrib.get('numberOfCpus')
        vappMem = elem.attrib.get('memoryAllocationMB')
        vappStorage = elem.attrib.get('storageKB')
        t_vapp.add_row([vappName, vappCPU, vappMem, vappStorage, vappStatus, vappDeploy, vappVdc])

    print t_vapp.get_string(sortby="Vapp Name")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("vapp", nargs='?', help="operation on Vapp")
    parser.add_argument("template", nargs='?', help="operation on templates")
    parser.add_argument("--login", action="store_true", help="login into VCloud")
    parser.add_argument("--list", action="store_true", help="list data")
    parser.add_argument("--username", action="store_true", help="VCloud username")
    parser.add_argument("--password", action="store_true", help="VCloud password")
    parser.add_argument("--org", action="store_true", help="VCloud Organisation")
    parser.add_argument("--host", action="store_true", help="VCloud host")
    args = parser.parse_args()

    try:
        vcdHost = os.environ['vcdHost']
        vcdUsername = os.environ['vcdUser']
        vcdPassword = os.environ['vcdPass']
        vcdOrg = os.environ['vcdOrg']
        vcdUrl = "https://" + vcdHost + "/api"
    except:
        parser.print_help()
        sys.exit(1) 
    

    if args.login:
        login_VCD( vcdUsername, vcdPassword, vcdOrg, vcdUrl )

    if args.vapp:
        if args.list:
            display_vapp( vcdUrl )

