# std libs
import time

# third party libs

# Functions
def get_facts(gnmi_object, orgs) -> dict:
    result = {}

    data = gnmi_object.get(path=["/openconfig-system:system", "openconfig-platform:components", "/openconfig-interfaces:interfaces"])

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


def get_interfaces(gnmi_object, orgs) -> dict:
    result = {}

    data = gnmi_object.get(path=["/openconfig-interfaces:interfaces"])

    if_list = "openconfig-interfaces:interface" if "openconfig-interfaces:interface" in data["notification"][0]["update"][0]["val"] \
        else "interface"

    for item in data["notification"][0]["update"][0]["val"][if_list]:
        result[item["name"]] = {}
        
        # Oper state
        try:
            result[item["name"]]["is_up"] = item["state"]["oper-status"]

        except:
            result[item["name"]]["is_up"] = False

        # Admin state
        try:
            result[item["name"]]["is_enabled"] = item["state"]["enabled"]

        except:
            result[item["name"]]["is_enabled"] = False

        # Description
        try:
            result[item["name"]]["description"] = item["state"]["description"]

        except:
            result[item["name"]]["description"] = ""

        # Last flap
        try:
            result[item["name"]]["last_flapped"] = int(item["state"]["last-change"]) / 10 ** 9

        except:
            result[item["name"]]["last_flapped"] = -1

        # MTU
        try:
            result[item["name"]]["mtu"] = item["state"]["mtu"]

        except:
            result[item["name"]]["mtu"] = ""

        eth_dict = "openconfig-if-ethernet:ethernet" if "openconfig-if-ethernet:ethernet" in item \
            else "ethernet"

        # MAC addres
        try:
            result[item["name"]]["mac_address"] = item[eth_dict]["state"]["mac-address"]

        except:
            result[item["name"]]["mac_address"] = ""

        # Speed
        try:
            speeds = {
                        "SPEED_10MB": 10,
                        "SPEED_100MB": 100,
                        "SPEED_1GB": 1000,
                        "SPEED_2500MB": 2500,
                        "SPEED_5GB": 5000,
                        "SPEED_10GB": 10000,
                        "SPEED_25GB": 25000,
                        "SPEED_40GB": 40000,
                        "SPEED_50GB": 50000,
                        "SPEED_100GB": 100000,
                        "SPEED_200GB": 200000,
                        "SPEED_400GB": 400000,
                        "SPEED_600GB": 600000,
                        "SPEED_800GB": 800000,
                        "SPEED_UNKNOWN": -1
            }
            result[item["name"]]["speed"] = speeds[item[eth_dict]["state"]["port-speed"]]

        except:
            result[item["name"]]["speed"] = -1

    return result


def get_lldp_neighbors(gnmi_object, orgs) -> dict:
    result = {}

    data = gnmi_object.get(path=["/openconfig-lldp:lldp"])

    lldp_dict = "openconfig-lldp:interfaces" if "openconfig-lldp:interfaces" in data["notification"][0]["update"][0]["val"] \
        else "interfaces"

    for item in data["notification"][0]["update"][0]["val"][lldp_dict]["interface"]:
        result[item["name"]] = {}

        try:
            for item2 in item["neighbors"]["neighbor"]:
                result[item["name"]]["hostname"] = item2["state"]["system-name"]
                result[item["name"]]["port"] = item2["state"]["port-id"]

        except:
            pass

    return result

def get_interfaces_counters(gnmi_object, orgs) -> dict:
    result = {}

    data = gnmi_object.get(path=["/openconfig-interfaces:interfaces"])

    if_list = "openconfig-interfaces:interface" if "openconfig-interfaces:interface" in data["notification"][0]["update"][0]["val"] \
        else "interface"

    #tx_errors

    for item in data["notification"][0]["update"][0]["val"][if_list]:
        result[item["name"]] = {}

        #tx_errors
        try:
            result[item["name"]]["tx_errors"] = int(item["state"]["counters"]["out-errors"])

        except:
            result[item["name"]]["tx_errors"] = -1

        #rx_errors
        try:
            result[item["name"]]["rx_errors"] = int(item["state"]["counters"]["in-errors"])

        except:
            result[item["name"]]["rx_errors"] = -1

        #tx_discards
        try:
            result[item["name"]]["tx_discards"] = int(item["state"]["counters"]["out-discards"])

        except:
            result[item["name"]]["tx_discards"] = -1

        #rx_discards
        try:
            result[item["name"]]["rx_discards"] = int(item["state"]["counters"]["in-discards"])

        except:
            result[item["name"]]["rx_discards"] = -1

        #tx_octets
        try:
            result[item["name"]]["tx_octets"] = int(item["state"]["counters"]["out-octets"])

        except:
            result[item["name"]]["tx_octets"] = -1

        #rx_octets
        try:
            result[item["name"]]["rx_octets"] = int(item["state"]["counters"]["in-octets"])

        except:
            result[item["name"]]["rx_octets"] = -1

        #tx_unicast_packets
        try:
            result[item["name"]]["tx_unicast_packets"] = int(item["state"]["counters"]["out-unicast-pkts"])

        except:
            result[item["name"]]["tx_unicast_packets"] = -1

        #rx_unicast_packets
        try:
            result[item["name"]]["rx_unicast_packets"] = int(item["state"]["counters"]["in-unicast-pkts"])

        except:
            result[item["name"]]["rx_unicast_packets"] = -1

        #tx_multicast_packets
        try:
            result[item["name"]]["tx_multicast_packets"] = int(item["state"]["counters"]["out-multicast-pkts"])

        except:
            result[item["name"]]["tx_multicast_packets"] = -1

        #rx_multicast_packets
        try:
            result[item["name"]]["rx_multicast_packets"] = int(item["state"]["counters"]["in-multicast-pkts"])

        except:
            result[item["name"]]["rx_multicast_packets"] = -1

        #tx_broadcast_packets
        try:
            result[item["name"]]["tx_broadcast_packets"] = int(item["state"]["counters"]["out-broadcast-pkts"])

        except:
            result[item["name"]]["tx_broadcast_packets"] = -1

        #rx_broadcast_packets
        try:
            result[item["name"]]["rx_broadcast_packets"] = int(item["state"]["counters"]["in-broadcast-pkts"])

        except:
            result[item["name"]]["rx_broadcast_packets"] = -1

    return result