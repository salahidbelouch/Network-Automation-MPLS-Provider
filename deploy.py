import json
import gns3fy
from gns3fy import Node
from tabulate import tabulate
import time
import telnetlib


topo_data= ""
with open("topologyv3.json", "r") as topo:
    topo_data=json.load(topo)

#GNS3s

for int in topo_data["routers"][0]["P1"]["interfaces"] :
    print(int["InterfaceName"])

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
    tn = telnetlib.Telnet("10.56.67.183",node.console)
    iteration=0
    for int in topo_data["routers"][0][node.name]["interfaces"] :

        tn.write(b"\r")
        tn.write(b"end\r")
        tn.write(b"conf t\r")

        tn.write(b"int "+bytes(int["InterfaceName"],"utf-8")+b"\r")
        tn.write(b"no shutdown\r")

        tn.write(b"ip add "+bytes(int["Address"][0],"utf-8")+b" "+bytes(int["Address"][1],"utf-8")+b"\r")

        tn.write(b"end\r")
        if "OSPF" in int : 
            print( " I got here ______________________________________--")
            if iteration==0:
                iteration=1
                tn.write(b"conf t\r")
                tn.write(b"router ospf 10\r")
                tn.write(b"router id "+bytes(topo_data["routers"][0][node.name]["OSPF_id"],"utf-8")+ b"\r")
                tn.write(b"end\r")


            tn.write(b"conf t\r")
            tn.write(b"int "+bytes(int["InterfaceName"],"utf-8")+b"\r")
            tn.write(b"ip ospf 10 area "+bytes(str(int["OSPF"]),"utf-8")+b"\r")
            tn.write(b"end\r")


        if "MPLS" in int : 

            tn.write(b"conf t\r")
            tn.write(b"ip cef t\r")
            tn.write(b"int "+bytes(int["InterfaceName"],"utf-8")+b"\r")
            tn.write(b"mpls ip\r")
            tn.write(b"mpls label protocol ldp\r")
            tn.write(b"end\r")
            
            






    #node.start()


# connection : 









