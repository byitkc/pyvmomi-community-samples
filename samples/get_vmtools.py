#!/usr/bin/env python3
#
# Modified for Python3 by Brandon Young
# GitHub: https://github.com/byitkc
# Email: b@byitkc.com
#
# Written by JM Lopez
# GitHub: https://github.com/jm66
# Email: jm@jmll.me
# Website: http://jose-manuel.me
#
# Note: Example code For testing purposes only
#
# This code has been released under the terms of the Apache-2.0 license
# http://opensource.org/licenses/Apache-2.0
#

import argparse
import atexit
import requests
import ssl
from getpass import getpass
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

_columns_four = "{0:<20} {1:<30} {2:<30} {3:<20}"

def get_args():
    """
    This sample uses different arguments than the standard sample. We also
    need the vihost to work with.
    """
    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='Remote host to connect to')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-v', '--vmname',
                        required=False,
                        action='store',
                        help='Name of the Virtual Machine to get VMware Tools status from')

    parser.add_argument('-S', '--disable_ssl_verification',
                        required=False,
                        action='store_true',
                        help='Disable ssl host certificate verification')

    args = parser.parse_args()
    if not args.password:
        args. password = getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))

    return args


def get_obj(content, vim_type, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vim_type, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def get_vms(content):

    obj_view = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True)
    vms_list = obj_view.view
    obj_view.Destroy()
    return vms_list


def print_vmwareware_tools_status(vm):
    print(_columns_four.format(vm.name,
                               vm.guest.toolsRunningStatus,
                               vm.guest.toolsVersion,
                               vm.guest.toolsVersionStatus2))


def main():
    args = get_args()

    if args.disable_ssl_verification:
        sslContext = ssl._create_unverified_context()
    else:
        sslContext = None

    # connect to vc
    si = SmartConnect(
        host=args.host,
        user=args.user,
        pwd=args.password,
        port=args.port,
        sslContext=sslContext)

    # disconnect vCenter automatically at exit
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()

    if args.vmname:
        print('Searching for VM {}'.format(args.vmname))
        vm_obj = get_obj(content, [vim.VirtualMachine], args.vmname)
        if vm_obj:
            print(_columns_four.format('Name', 'Status',
                                       'Version', 'Version Status'))
            print_vmwareware_tools_status(vm_obj)
        else:
            print("VM not found")
    else:
        print(_columns_four.format('Name', 'Status',
                                   'Version', 'Version Status'))
        for vm_obj in get_vms(content):
            print_vmwareware_tools_status(vm_obj)

# start
if __name__ == "__main__":
    main()