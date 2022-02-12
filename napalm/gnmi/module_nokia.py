# std libs
import json, time
# third party libs

# Fix an issue with timezone processing in Python 3.6
from dateutil.parser import parse as dateutil_parse

# NAPALM base
from napalm.base.utils import string_parsers


# Functions
def get_facts(gnmi_object, orgs) -> dict:
    # SRL specific version, TODO split up SR Linux / SR OS
    result = gnmi_object.get(path=["/system","/platform","/interface"], encoding='json_ietf')
    # print( f"get_facts:{result}")

    system = result['notification'][0]['update'][0]['val']
    platform = result['notification'][1]['update'][0]['val']
    interface = result['notification'][2]['update'][0]['val']['srl_nokia-interfaces:interface']
    version = system['srl_nokia-system-info:information']['version']
    hostname = system['srl_nokia-system-name:name']['host-name']
    domain = system['srl_nokia-system-name:name']['domain-name'] if 'domain-name' in system['srl_nokia-system-name:name'] else "undefined"
    # interfaces_dict = result[2]["interfaces"]

    uptime = time.time() - dateutil_parse(system['srl_nokia-system-info:information']['last-booted']).timestamp()

    chassis = platform['srl_nokia-platform-chassis:chassis']

    interfaces = [ i['name'] for i in interface ]
    interfaces = string_parsers.sorted_nicely(interfaces)

    return {
        "hostname": hostname,
        "fqdn": hostname + '.' + domain,
        "vendor": "Nokia",
        "model": chassis['type'],
        "serial_number": chassis['serial-number'],
        "os_version": version,
        "uptime": int(uptime),
        "interface_list": interfaces,
    }
