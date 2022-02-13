#NANOG84 Hackathon project

![Blog_Nanog84_Hackathon](https://user-images.githubusercontent.com/2031627/153724164-65441a81-5684-4ed7-96ee-54980790a962.png)

This multi-vendor gNMI driver was created for the NANOG84 Hackathon on February 12th 2022 in Austin, Texas.
It is based on the Arista EOS driver (thanks everyone!) with the EOS API replaced by pygNMI gRPC calls

# Setup

```
sudo apt install -y python38-venv
python3 -m pip install pip --upgrade
git clone https://github.com/jbemmel/napalm.git --branch nanog84-hackathon-gnmi-driver
cd napalm
python3 -m venv ./venv
source venv/bin/activate
python3 -m pip install -r requirements.txt -r requirements-dev.txt
python3 -m setup install
```

## NetBox
At https://github.com/jbemmel/netbox-docker/tree/nanog84-hackathon is a branch to build a NetBox image with the new gNMI NAPALM driver built in

# Test
Using NAPALM CLI:
```
napalm --vendor gnmi --user admin --password admin clab-n84_hackathon-srl1 call get_facts
napalm --vendor gnmi --user admin --password admin --optional_args port=6030,insecure=True clab-n84_hackathon-ceos1 call get_facts
```

![Napalm_olypics](https://user-images.githubusercontent.com/2031627/153724175-69f9fcd0-bcbe-49e5-8676-89de32c1f9b3.png)
