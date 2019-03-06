#!/usr/bin/env python3

'''
Created by Brandon Young
GitHub: https://github.com/byitkc
Email: b@byitkc.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
Simple script to get a list of Hard Disks on a VM along with their scsi information.
Created in part to match up with the disks on the host OS
'''

import argparse
import atexit
import ssl

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from getpass import getpass

#? Disable for Debugging
'''
def get_args():
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
        args.password = getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))

    return args
'''

def db_get_args():
    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')

    parser.add_argument('-s', '--host',
                        default='vcenter.corp.bnky.io',
                        action='store',
                        help='Remote host to connect to')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        default='roapi@vsphere.local',
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        default='VME0SH9xORCEH3gKqe!d',
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-v', '--vmname',
                        default='app02 (Sonarr)',
                        action='store',
                        help='Name of the Virtual Machine to get VMware Tools status from')

    parser.add_argument('-S', '--disable_ssl_verification',
                        default=True,
                        action='store_true',
                        help='Disable ssl host certificate verification')

    args = parser.parse_args()
    if not args.password:
        args.password = getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))

    return args

'''
def print_vm_info(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    summary = virtual_machine.summary
    print("Name       : ", summary.config.name)
    print("Template   : ", summary.config.template)
    print("Path       : ", summary.config.vmPathName)
    print("Guest      : ", summary.config.guestFullName)
    print("Instance UUID : ", summary.config.instanceUuid)
    print("Bios UUID     : ", summary.config.uuid)
    annotation = summary.config.annotation
    if annotation:
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
        if tools_version is not None:
            print("VMware-tools: ", tools_version)
        else:
            print("Vmware-tools: None")
        if ip_address:
            print("IP         : ", ip_address)
        else:
            print("IP         : None")
    if summary.runtime.question is not None:
        print("Question  : ", summary.runtime.question.text)
    print("")
'''

def main():

    #? Skipping Args for Debugging
    # args = get_args()

    args = db_get_args()

    if args.disable_ssl_verification:
        sslContext = ssl._create_unverified_context()
    else:
        sslContext = None

    

    si = connect.SmartConnect(
                                    host=args.host,
                                    user=args.user,
                                    pwd=args.password,
                                    port=int(args.port),
                                    sslContext=sslContext)

    atexit.register(connect.Disconnect, si)

    content = si.RetrieveContent()

    container = content.rootFolder  # starting point to look into
    viewType = [vim.VirtualMachine]  # object types to look for
    recursive = True  # whether we should look into it recursively
    containerView = content.viewManager.CreateContainerView(
        container, viewType, recursive)

    children = containerView.view
    for child in children:

        # Skipping all VM's that don't match the name we provided
        if child.name != args.vmname:
            continue

        scsi_controllers = {}
        disks = []
        hw_devices = child.config.hardware.device
        for device in hw_devices:
            if isinstance(device, vim.vm.device.VirtualIDEController):
                print("IDE Controller")
            elif isinstance(device, vim.vm.device.VirtualLsiLogicController):
                print("SCSI Controller")
                scsi_controllers[device.key] = {
                    "name": device.deviceInfo.label,
                    "key": device.key,
                    "controllerKey": device.controllerKey,
                    "busNumber": device.busNumber
                }
            elif isinstance(device, vim.vm.device.VirtualDisk):
                print("Virtual Disk")
                disks.append(
                    {
                        "name": device.deviceInfo.label,
                        "key": device.key,
                        "controllerKey": device.controllerKey,
                        "unitNumber": device.unitNumber,
                        "size": device.capacityInBytes,
                    }
                )

        disk_map = []
        for disk in disks:
            controller = scsi_controllers[disk['controllerKey']]
            _add = {
                "controller": controller,
                "bus": controller['busNumber'],
                "unit": disk['unitNumber'],
                "info": "{}:{}".format(controller['busNumber'], disk['unitNumber']),
                "size": None,
            }
            print("{} (Size: {}): {}".format(disk['name'],disk['size'],_add['info']))
        print("break!")

    return 0

# Start program
if __name__ == "__main__":
    main()
