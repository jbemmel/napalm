# std libs
import time

# third party libs

# Functions
def get_facts(gnmi_object, orgs) -> dict:
    result = {}

    data = gnmi_object.get(path=["/openconfig-system:system", "openconfig-platform:components", "/openconfig-interfaces:interfaces"])
#    print(json.dumps(data, indent=4))

    # Get hostname
    try:
        hostname = data["notification"][0]["update"][0]["val"]["openconfig-system:state"]["hostname"]
        
    except:
        try: 
            hostname = data["notification"][0]["update"][0]["val"]["state"]["hostname"]

        except:
            hostname = ""

    result["hostname"] = hostname

    # Get fqdn
    try:
        domain = data["notification"][0]["update"][0]["val"]["openconfig-system:state"]["domain-name"]
    except:
        try: 
            domain = data["notification"][0]["update"][0]["val"]["state"]["domain-name"]

        except:
            domain = ""

    result["fqdn"] = hostname + "." + domain if domain else hostname

    # Get vendors
    known_vendors = {"cisco", "arista", "nokia", "juniper"}

    vendor = known_vendors & orgs

    result["vendor"] = vendor.pop().capitalize()

    # Get Model
    # TODO test against real device, as vEOS doesn't have HW type
    model = ""
    try:
        for item in data["notification"][1]["update"][0]["val"]["openconfig-platform:component"]:
            if item["name"] == "Chassis":
                model = item["state"]["type"]
    except:
        try: 
            for item in data["notification"][1]["update"][0]["val"]["component"]:
                if item["name"] == "Chassis":
                    model = item["state"]["type"]
        except:
            model = ""

    result["model"] = model

    # Get serial_number
    # TODO test against real device, as vEOS doesn't have SN
    serial_number = ""

    result["serial_number"] = serial_number

    # Get OS_verson
    # TODO it looks like there is no OS verson available in any YANG model implemnted in Arista 
    os_version = ""

    result["os_version"] = os_version

    # Get uptime
    # Provided in nanoseconds per gNMI spe
    try:
        uptime = time.time_ns() - int(data["notification"][0]["update"][0]["val"]["openconfig-system:state"]["boot-time"])
    except:
        try: 
            uptime = time.time_ns() - int(data["notification"][0]["update"][0]["val"]["state"]["boot-time"])

        except:
            uptime = 0

    result["uptime"] = uptime / 10 ** 9 ## Converting to seconds to match NAPALM


    # Get Interfaces list
    interface_list = []
    try:
        for item in data["notification"][2]["update"][0]["val"]["openconfig-interfaces:interface"]:
            interface_list.append(item["name"])
    except:
        try: 
            for item in data["notification"][2]["update"][0]["val"]["interface"]:
                interface_list.append(item["name"])

        except:
            uptime = 0

    result["interface_list"] = interface_list

    return result