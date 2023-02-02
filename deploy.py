import json
import gns3fy
from gns3fy import Node
from tabulate import tabulate
import time
import telnetlib


topo_data= ""
with open("topology.json", "r") as topo:
    topo_data=json.load(topo)

#GNS3s
print(topo_data["topo"]["routers"][0]["ID"])

# Connect to the GNS3 server
server = gns3fy.Gns3Connector("http://10.56.67.183:3080")

#verif -----

print(
        tabulate(
            server.projects_summary(is_print=False),
            headers=["Project Name", "Project ID", "Total Nodes", "Total Links", "Status"],
        )
    )


# ouvre projet 

projet= gns3fy.Project(name="Nouveau", connector=server)

# get info 
projet.get()
print(projet)

# variables projet
id =projet.project_id
c7200 =0

projet.open()

for template in server.get_templates():
     if "c7200" in template["name"]:
        print(f"Template: {template['name']} -- ID: {template['template_id']}")
        c7200=template['template_id']

for node in projet.nodes:
    print(f"Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status} -- port {node.console} -- port {node.command_line}")
    #node.start()


# connection : 


tn = telnetlib.Telnet("10.56.67.183",5008)

tn.write(b"\r")
tn.write(b"end\r")
tn.write(b"conf t\r")

tn.write(b"int g1/0\r")
tn.write(b"no shutdown\r")

tn.write(b"ip add 10.0.1.1 255.255.255.252\r")

tn.write(b"end\r")
tn.write(b"write\r")
tn.write(b"y\r")









