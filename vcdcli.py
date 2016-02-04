#!/usr/bin/env python

from pprint import pprint
import requests
import base64
import xml.etree.ElementTree as ET
import time, datetime, os
import sys
from prettytable import PrettyTable
import argparse
from math import *

def login_VCD(l_user,l_password,l_org,l_url):
    f_http = os.popen("http --session=vcdcli -a " + l_user + "@" + l_org + ":" + l_password +" POST " + l_url + "/sessions 'Accept:application/*+xml;version=5.1'")
    f_xmldata = f_http.read()

def display_vapp(l_url):
    # Make the query to gather the info
    f_http = os.popen('http --session=vcdcli GET ' + l_url + '/vApps/query?pageSize=200')
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
    f_http = os.popen('http --session=vcdcli GET "' + l_url + '/query?type=vAppTemplate&pageSize=200"')
    xmldata = f_http.read()
    tree = ET.fromstring(xmldata)

    #print tree.tag
    #print tree.attrib
    #print xmldata
    
    t_template = PrettyTable(['Template Name', 'Storage (KB)', 'NumCPU', 'Mem Alloc (MB)', '# VM', 'Status', 'Catalog Name'])
    t_template.align['Template Name'] = 'l'
    
    for elem in tree:
        templateName = elem.attrib.get('name')
        templateStatus = elem.attrib.get('status')
        templateStorage = elem.attrib.get('storageKB')
        templateCatalog = elem.attrib.get('catalogName')
        templateNumCPU = elem.attrib.get('numberOfCpus')
        templateMemAlloc = elem.attrib.get('memoryAllocationMB')
        templateNumVM = elem.attrib.get('numberOfVMs')
        
        if templateName:
            t_template.add_row([templateName, templateStorage, templateNumCPU, templateMemAlloc, templateNumVM, templateStatus, templateCatalog])

    print t_template.get_string(sortby="Template Name")

def display_pool(l_url):
    f_http = os.popen('http --session=vcdcli GET "' + l_url + '/query?type=orgVdc&pageSize=200"')
    xmldata = f_http.read()
    tree = ET.fromstring(xmldata)

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
            poolMemoryUsedPercent = int((float(poolMemoryUsed) / float(poolMemoryLimit)) * 100)
            poolMemoryUsed = poolMemoryUsed + '  (' + str(poolMemoryUsedPercent) + '%)'
            poolStorageUsedPercent = int((float(poolStorageUsed) / float(poolStorageLimit)) * 100)
            poolStorageUsed = poolStorageUsed + '  (' + str(poolStorageUsedPercent) + '%)'
            t_pool.add_row([poolName, poolVapps, poolCpuUsed, poolCpuLimit,poolMemoryUsed,poolMemoryLimit,poolStorageUsed,poolStorageLimit])

    print t_pool.get_string(sortby="Pool Name")


def show_vapp_info(l_url, l_vappName):
    vappInfo = get_vapp_info(l_url,l_vappName)
    l_vappUrl = vappInfo['vappUrl']

    f_http = os.popen('http --session=vcdcli GET ' + l_vappUrl)
    xmldata = f_http.read()
    Vapptree = ET.fromstring(xmldata)

    for elem in Vapptree.iter('{http://www.vmware.com/vcloud/v1.5}Vm'):
        l_vmUrl = elem.attrib.get('href')
    
    vmCusto = get_vm_custo(l_vmUrl)

    t_vappInfo = PrettyTable(['Attribute', 'Value'])
    t_vappInfo.align['Value'] = 'l'
    
    
    for key, value in vappInfo.iteritems():
        t_vappInfo.add_row([key, value])

    t_vappInfo.add_row(['-------- VM ---------',''])
    for key, value in vmCusto.iteritems():
        t_vappInfo.add_row([key, value])
    
    print t_vappInfo

def get_vm_custo(vm_url):
    f_http = os.popen('http --session=vcdcli GET ' + vm_url + '/guestCustomizationSection/')
    xmldata = f_http.read()

    vmCusto = {}

    Vmtree = ET.fromstring(xmldata)
    for elem in Vmtree:
        #print elem.tag, elem.text
        if elem.tag == '{http://www.vmware.com/vcloud/v1.5}Enabled':
            vmCusto['CustoEnabled'] = elem.text
        elif elem.tag == '{http://www.vmware.com/vcloud/v1.5}ChangeSid':
            vmCusto['ChangeSid'] = elem.text
        elif elem.tag == '{http://www.vmware.com/vcloud/v1.5}JoinDomainEnabled':
            vmCusto['JoinDomainEnabled'] = elem.text
        elif elem.tag == '{http://www.vmware.com/vcloud/v1.5}AdminPasswordEnabled':
            vmCusto['AdminPasswordEnabled'] = elem.text
        elif elem.tag == '{http://www.vmware.com/vcloud/v1.5}AdminPasswordAuto':
            vmCusto['AdminPasswordAuto'] = elem.text
        elif elem.tag == '{http://www.vmware.com/vcloud/v1.5}AdminPassword':
            vmCusto['AdminPassword'] = elem.text
        elif elem.tag == '{http://www.vmware.com/vcloud/v1.5}ResetPasswordRequired':
            vmCusto['ResetPasswordRequired'] = elem.text
        elif elem.tag == '{http://www.vmware.com/vcloud/v1.5}ComputerName':
            vmCusto['ComputerName'] = elem.text

    return vmCusto
    

def get_vapp_info(l_url,l_vappName):
    f_http = os.popen('http --session=vcdcli GET "' + l_url + '/query?type=vApp&filter=(name==' + l_vappName + ')"')
    xmldata = f_http.read()
    tree = ET.fromstring(xmldata)
    
    for elem in tree.findall('{http://www.vmware.com/vcloud/v1.5}VAppRecord'):
        vappUrl = elem.attrib.get('href')
        vappName = elem.attrib.get('name')
        vappStatus =  elem.attrib.get('status')
        vappDeploy =  elem.attrib.get('isDeployed')
        vappVdc =  elem.attrib.get('vdcName')
        vappCPU =  elem.attrib.get('numberOfCpus')
        vappMem = elem.attrib.get('memoryAllocationMB')
        vappStorage = elem.attrib.get('storageKB')
        vappCreationDate = elem.attrib.get('creationDate')
        vappOwnerName = elem.attrib.get('ownerName')

    return {'vappName':vappName, 'vappUrl':vappUrl, 'vappStatus':vappStatus, 'vappDeploy':vappDeploy, 'vappVdc':vappVdc, 'vappCPU':vappCPU, 'vappMem':vappMem, 'vappStorage':vappStorage, 'vappCreationDate':vappCreationDate, 'vappOwnerName':vappOwnerName}

def show_tmpl_info(l_url,l_tmplName):
    print 'show template info' + l_tmplName
    tmpl_info = get_tmpl_info(l_url,l_tmplName)

def get_tmpl_info(l_url,l_tmplName):
    f_http = os.popen('http --session=vcdcli GET "' + l_url + '/query?type=vAppTemplate&filter=(name==' + l_tmplName + ')"')
    xmldata = f_http.read()
    #print xmldata
    tree = ET.fromstring(xmldata)
    
    for elem in tree.findall('{http://www.vmware.com/vcloud/v1.5}VAppTemplateRecord'):
        tmplUrl = elem.attrib.get('href')
        tmplName = elem.attrib.get('name')
        tmplStatus = elem.attrib.get('status')
        tmplOwner = elem.attrib.get('ownerName')
        tmplCpuAllocMhz = elem.attrib.get('cpuAllocationInMhz')
        tmplMemAlloc = elem.attrib.get('memoryAllocationMB')
        tmplNumVM = elem.attrib.get('numberOfVMs')
        tmplVdcName = elem.attrib.get('vdcName')
        tmplStorage = elem.attrib.get('storageKB')
        tmplCreationDate = elem.attrib.get('creationDate')
        tmplNumCPU = elem.attrib.get('numberOfCpus')
    
    return {'tmplName':tmplName, 'tmplUrl':tmplUrl, 'tmplStatus':tmplStatus, 'tmplOwner':tmplOwner, 'tmplCpuAllocMhz':tmplCpuAllocMhz, 'tmplMemAlloc':tmplMemAlloc, 'tmplNumVM':tmplNumVM, 'tmplVdcName':tmplVdcName, 'tmplStorage':tmplStorage, 'tmplCreationDate':tmplCreationDate, 'tmplNumCPU':tmplNumCPU }

def delete_template(l_url,l_tmplName):
    #print 'Deleting template ' + l_tmplName
    tmpl_info = get_tmpl_info(l_url, l_tmplName)
    tmplUrl = tmpl_info['tmplUrl']
    
    if tmplUrl:   
        f_http = os.popen('http --session=vcdcli DELETE ' + tmplUrl)
        xmldata = f_http.read()
        task_info = decode_task_info(xmldata)
        print task_info['taskOperation']
        l_taskUrl = task_info['taskUrl']
        wait_for_task(l_taskUrl)

def decode_task_info(l_xmlTask):
    taskTree = ET.fromstring(l_xmlTask)
    taskStatus = taskTree.attrib.get('status')
    taskStarttime = taskTree.attrib.get('startTime')
    taskOperation = taskTree.attrib.get('operation')
    taskId = taskTree.attrib.get('id').split( ':' )
    taskID = taskId[3]
    taskUrl = taskTree.attrib.get('href')
    
    return { 'taskStatus':taskStatus, 'taskId':taskID, 'taskUrl':taskUrl, 'taskOperation':taskOperation }

def get_task_info(l_taskUrl):
    f_http = os.popen('http --session=vcdcli GET "' + l_taskUrl + '"')
    l_xmlTask = f_http.read()
    
    taskTree = ET.fromstring(l_xmlTask)    
    taskStatus = taskTree.attrib.get('status')
    taskStarttime = taskTree.attrib.get('startTime')
    taskOperation = taskTree.attrib.get('operation')
    taskId = taskTree.attrib.get('id').split( ':' )
    taskID = taskId[3]
    taskUrl = taskTree.attrib.get('href')
    
    return { 'taskStatus':taskStatus, 'taskId':taskID, 'taskUrl':taskUrl, 'taskOperation':taskOperation }

def wait_for_task(l_taskUrl):
    task_info = get_task_info(l_taskUrl)
    taskStatus = task_info['taskStatus']
    while taskStatus == 'running' or taskStatus == 'preRunning':
        sys.stdout.write('#')
        sys.stdout.flush()
        task_info = get_task_info(l_taskUrl)
        taskStatus = task_info['taskStatus']
    
    if taskStatus == 'error':
        print 'Task Error.'
    else:
        print '\nDone.'
        

"""
************************************** Main **********************************************************
"""
if __name__ == '__main__':
    # Parsing of the command line aguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", nargs='?', help="vapp, template...")
    parser.add_argument("--login", action="store_true", help="login with new credentials")
    parser.add_argument("--list", action="store_true", help="list data")
    parser.add_argument("--show", dest='objName', action="store", help="show data")
    parser.add_argument("--delete", dest='objToDelete', action="store", help="delete data")
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
        elif args.objName:
            show_vapp_info(vcdUrl,args.objName)
    elif args.operation == 'pool':
        if args.list:
            display_pool(vcdUrl)

    elif args.operation == 'template':
        if args.list:
            display_template(vcdUrl)
        elif args.objName:
            show_tmpl_info(vcdUrl,args.objName)
        elif args.objToDelete:
            delete_template(vcdUrl,args.objToDelete)
    else:
        parser.print_help()
        
    sys.exit(0) 


