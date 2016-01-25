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
    # Make the query to gather the info
    f_http = os.popen('http --session=vcloud GET ' + l_url + '/vApps/query?pageSize=200')
    xmldata = f_http.read()
    tree = ET.fromstring(xmldata)

    # Build a table to display info
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

def display_template(l_url):
    f_http = os.popen('http --session=vcloud GET ' + l_url + '/query?type=vAppTemplate&pageSize=200')
    xmldata = f_http.read()
    tree = ET.fromstring(xmldata)

    #print tree.tag
    #print tree.attrib
    #print xmldata
    
    t_template = PrettyTable(['Template Name', 'Storage (KB)', 'Status', 'Catalog Name'])
    t_template.align['Template Name'] = 'l'
    
    for elem in tree:
        templateName = elem.attrib.get('name')
        templateStatus = elem.attrib.get('status')
        templateStorage = elem.attrib.get('storageKB')
        templateCatalog = elem.attrib.get('catalogName')
        if templateName:
            t_template.add_row([templateName, templateStorage, templateStatus, templateCatalog])

    print t_template.get_string(sortby="Template Name")

def display_pool(l_url):
    f_http = os.popen('http --session=vcloud GET ' + l_url + '/query?type=orgVdc&pageSize=200')
    xmldata = f_http.read()
    tree = ET.fromstring(xmldata)
    
    #print tree.tag
    #print tree.attrib
    #print xmldata

    t_pool = PrettyTable(['Pool Name', '# of Vapps', 'Cpu Used(MHz)', 'Cpu Limit(MHz)', 'Memory Used(MB)', 'Memory Limit(MB)', 'Storage Used(MB)', 'Storage Limit(MB)'])
    t_pool.align['Pool Name'] = 'l'
    
    for elem in tree:
        poolName = elem.attrib.get('name')
        poolVapps = elem.attrib.get('numberOfVApps')
        poolCpuUsed = elem.attrib.get('cpuUsedMhz')
        poolCpuLimit = elem.attrib.get('cpuLimitMhz')
        poolMemoryUsed = elem.attrib.get('memoryUsedMB')
        poolMemoryLimit = elem.attrib.get('memoryLimitMB')
        poolStorageUsed = elem.attrib.get('storageUsedMB')
        poolStorageLimit = elem.attrib.get('storageLimitMB')
        if poolName:
            t_pool.add_row([poolName, poolVapps, poolCpuUsed, poolCpuLimit,poolMemoryUsed,poolMemoryLimit,poolStorageUsed,poolStorageLimit])

    print t_pool.get_string(sortby="Pool Name")

    #print 'pool list ok'


if __name__ == '__main__':
    # Parsing of the command line aguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", nargs='?', help="vapp, template...")
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
        
    #print args
    
    if args.login:
        login_VCD( vcdUsername, vcdPassword, vcdOrg, vcdUrl )

    if args.operation == 'vapp':
        if args.list:
            display_vapp(vcdUrl)

    if args.operation == 'pool':
        if args.list:
            display_pool(vcdUrl)

    if args.operation == 'template':
        if args.list:
            display_template(vcdUrl)
    
    sys.exit(0) 


