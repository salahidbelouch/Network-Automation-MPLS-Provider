import json
import gns3fy
from gns3fy import Node
from tabulate import tabulate
import time
import telnetlib


def AddingRemoveCE():
    task=input("add or remove a customer? ")
    name=input("name of customer (CE5 for ex.) ")
    PE=input("this customer is relarted to each PE? ")
    # if task=="add":
    ipCE=input("What ip address should he have? ")
    ipPE=input("What is the PE ip address? ")
    intCE=input("What is the CE related interface? (default g1/0) ") or "g1/0"
    intPE=input("What is the PE related interface? (ex: g3/0) ") 
    ASnum=input("AS number? ")
    vrf=input("vrf name: ")
    rd=input("Route distinguisher : ")
    rt=input("Route target : ")

    
    
    
    pass

if __name__ == '__main__':
    ### Connect to the GNS3 server
    server = gns3fy.Gns3Connector("http://192.168.137.1:3080")

    # Verif -----

    print(
        tabulate(
            server.projects_summary(is_print=False),
            headers=["Project NAME", "Project ID",
                    "Total Nodes", "Total Links", "Status"],
        )
    )

    #############################


    #### Lecture JSON

    with open("topologyv3.json", "r") as topo:
        topo_data = json.load(topo)

    #### Gestion Projet GNS3
    # Ouvre projet

    projet = gns3fy.Project(name="TEST2", connector=server)

    # Get info

    projet.get()
    #print(projet)

    # Variables projet
    id = projet.project_id
    c7200 = 0

    projet.open()

    # Debug
    for template in server.get_templates():
        if "c7200" in template["name"]:
            print(f"Template: {template['name']} -- ID: {template['template_id']}")
            c7200 = template['template_id']

    #### Ecriture sur routeurs 


    for node in projet.nodes:
        print(f"Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status} -- port {node.console} -- port {node.command_line}")
        tn = telnetlib.Telnet("192.168.137.1", node.console)
        routeur=topo_data[node.name]
        #Première implem Initialisation 

        tn.write(b"\r")
        tn.write(b"end\r")
        time.sleep(0.3)

        tn.write(b"\r")
        tn.write(b"conf t\r")
        tn.write(f"hostname {node.name}\r".encode())
        tn.write(b"end\r")
        time.sleep(0.3)

        #Implementation OSPF par routeur

        
        if "OSPF_id" in routeur:
            tn.write(b"conf t\r")
            tn.write(b"router ospf 10\r")
            tn.write(b"router id "+bytes(routeur["OSPF_id"], "utf-8") + b"\r")
            tn.write(b"end\r")
            print("OSPF DONE")
        if "ipcef" in routeur:
            tn.write(b"\r")
            tn.write(b"conf t\r")
            tn.write(b"ip cef\r")
            tn.write(b"end\r")
            time.sleep(0.3)
            print("ipcef DONE")

        # Implementation interface par interface des parametres

        for int in routeur["interfaces"]:

            tn.write(b"\r")
            tn.write(b"enable\r")
            time.sleep(0.3)
            time.sleep(0.3)

            tn.write(b"conf t\r")
            tn.write(b"int "+bytes(int["Interface"], "utf-8")+b"\r")
            tn.write(b"no shutdown\r")

            tn.write(b"ip add "+bytes(int["Address"][0], "utf-8") +
                    b" "+bytes(int["Address"][1], "utf-8")+b"\r")

            tn.write(b"end\r")
            
            #OSPF
            tn.write(b"conf t\r")
            tn.write(b"router ospf 10\r")
            if int["Interface"]=="Loopback0" :
                tn.write(b"network "+bytes(int["Address"][0], "utf-8")+b"0.0.0.0 area "+bytes(str(int["OSPF"]), "utf-8")+b"\r")
            else: # make the mask adaptable
                tn.write(b"network "+bytes(int["Address"][0], "utf-8")+b" 0.0.0.255 area "+bytes(str(int["OSPF"]), "utf-8")+b"\r")
            tn.write(b"end\r")


        
        #MPLS

            if "OSPF" in int:
                tn.write(b"conf t\r")
                tn.write(b"int "+bytes(int["Interface"], "utf-8")+b"\r")
                tn.write(b"ip ospf 10 area " +
                        bytes(str(int["OSPF"]), "utf-8")+b"\r")
                tn.write(b"end\r")
            
            #MPLS

            if "MPLS" in int:
                tn.write(b"conf t\r")
                tn.write(b"ip cef t\r")
                tn.write(b"int "+bytes(int["Interface"], "utf-8")+b"\r")
                tn.write(b"mpls ip\r")
                tn.write(b"mpls label protocol ldp\r")
                tn.write(b"end\r")

        #VRF
        if "VRF" in routeur:
            for VRF in routeur["VRF"]:

                NAME=VRF["name"]
                RD=VRF["rd"]
                IMPORT=VRF["rt_import"] #on a mis que c'est une liste au cas ou y en a plusieurs
                EXPORT=VRF["rt_export"]
                tn.write(b"\r")
                tn.write(b"conf t\r")
                tn.write(f"ip vrf {NAME}\r".encode())
                tn.write(f"rd {RD}\r".encode())
                for rt_in in IMPORT:
                    tn.write(f"route-target import {rt_in}\r".encode())
                for rt_out in EXPORT:
                    tn.write(f"route-target export {rt_out}\r".encode())
                tn.write(b"address-family ipv4\r")
                tn.write(b"end\r") 
                time.sleep(0.7)


        #BGP
        if "BGP" in routeur:
            AS=routeur["BGP"]["AS"]
            tn.write(b"conf t\r")
            tn.write(f"router bgp {AS}\r".encode())
            tn.write(b"bgp log-neighbor-changes\r")
            if "redistribute" in routeur["BGP"]:
                tn.write(b"redistribute connected\r")
            tn.write(b"end\r")
            time.sleep(0.3)

            if "Neighbors" in routeur["BGP"]:
                tn.write(b"\r")
                tn.write(b"conf t\r")
                tn.write(f"router bgp {AS}\r".encode())
                Neighbors=routeur["BGP"]["Neighbors"]
                for neighbor in Neighbors:
                    tn.write(f"neighbor {neighbor['addr']} remote-as {neighbor['AS']}\r".encode())
                    time.sleep(0.3)
                    # tn.write(f"neighbor {neighbor['addr']} activate\r".encode())
                    # tn.write(f"neighbor {neighbor['addr']} update-source loopback 0\r".encode()) 
                    time.sleep(0.3)
    
            if "ipv4" in routeur["BGP"]:
                tn.write(b"end\r")  
                tn.write(b"conf t\r")
                tn.write(f"router bgp {AS}\r".encode())
                tn.write(b"address-family ipv4\r")
                Neighbors=routeur["BGP"]["ipv4"]
                for neighbor in Neighbors:
                    tn.write(f"neighbor {neighbor['addr']} activate\r".encode())
                    time.sleep(0.3)
                tn.write(b"end\r")

            if "vpnv4" in routeur["BGP"]:
                Neighbors=routeur["BGP"]["vpnv4"]
                tn.write(b"end\r")  
                tn.write(b"conf t\r")
                tn.write(f"router bgp {AS}\r".encode())
                tn.write(b"address-family vpnv4\r")
                for neighbor in Neighbors:
                    tn.write(f"neighbor {neighbor['addr']} activate\r".encode())
                    tn.write(f"neighbor {neighbor['addr']} update-source loopback 0\r".encode())
                    # tn.write(f"neighbor {neighbor['addr']} send-community both\r".encode()) #PAS BESOIN ON IMPLEM DIRECT LES VRFS
                    time.sleep(0.3)
                tn.write(b"end\r")

            if "v_vrf" in routeur["BGP"]:
                Neighbors=routeur["BGP"]["v_vrf"]
                tn.write(b"end\r")  
                tn.write(b"conf t\r")
                tn.write(f"router bgp {AS}\r".encode())
                for neighbor in Neighbors:
                    VRF_name=neighbor["VRF"]
                    neigh=neighbor["Neighbors"]
                    tn.write(f"address-family ipv4 vrf {VRF_name}\r".encode())
                    for neig in neigh:
                        tn.write(f"neighbor {neig['addr']} remote-as {neig['AS']}\r".encode())
                        tn.write(f"neighbor {neig['addr']} activate\r".encode())
                        time.sleep(0.3)
                    tn.write(b"exit-address-family\r")
                    time.sleep(0.3)
        
        tn.write(b"end\r")
        tn.write(b"write\r")
        tn.write(b"\r")
        print( " Router DONE ")
        # node.start()

    
    # connection :
