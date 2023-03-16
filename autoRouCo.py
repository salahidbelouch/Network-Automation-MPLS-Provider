import json
import gns3fy
from gns3fy import Node
from tabulate import tabulate
import time
import telnetlib
import sys


def AddingRemoveCE(projet):
    global ip
    # task=input("add or remove a customer? ")
    name=input("Name of the new customer (CE5 for ex.) : ")
    PE=input("This customer is going to be related to which PE? (PE1 for ex.) : ")
    # if task=="add":
    ipCE=input("What ip address should he have? ")
    ipPE=input("What is the PE ip address? ")
    intCE=input("What is the CE related interface? (default g1/0) ") or "g1/0"
    intPE=input("What is the PE related interface? (ex: g3/0) ") 
    vrf=input("vrf name: ")
    rd=input("Route distinguisher : ")
    rt_imp=[]
    rt_exp=[]
    nb_import=int(input("Number of RT to import (default: 1): ") or "1")
    nb_export=int(input("Number of RT to export (default: 1): ") or "1")
    for i in range(nb_import):
        rt_imp.append(input(" *  "+str(i)+"   Route target import : "))
    for i in range(nb_export):
        rt_exp.append(input(" *  "+str(i)+"   Route target export : "))
    splitted=((ipCE.split('.'))[:-1])
    splitted.append('0')
    net='.'.join(splitted)
    for node in projet.nodes:
        if node.name==name:
            print(f"##### Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status} -- port {node.console} -- port {node.command_line}")
            tn = telnetlib.Telnet(ip, node.console)
            tn.write(b"\r")
            tn.write(b"yes\r")
            time.sleep(16)
            time.sleep(0.3)
            tn.write(b"\r")
            tn.write(b"enable\r")
            tn.write(b"\r")
            tn.write(b"conf t\r")
            tn.write(b"no ip domain-lookup\r")
            tn.write(b"ip cef\r")
            tn.write(b"end\r")
            time.sleep(0.3)
            tn.write(b"\r")
            tn.write(b"enable\r")
            time.sleep(0.8)
            tn.write(b"conf t\r")
            tn.write(b"int "+bytes(intCE, "utf-8")+b"\r")
            tn.write(b"no shutdown\r")
            tn.write(b"ip add "+bytes(ipCE, "utf-8") +
                    b" "+bytes("255.255.255.0", "utf-8")+b"\r")
            tn.write(b"conf t\r")
            tn.write(b"router rip\r")
            tn.write(b"version 2\r")
            tn.write(f"network {net}\r".encode())
            tn.write(b"end\r")
            time.sleep(0.5)
            tn.write(b"end\r")
            tn.write(b"write\r")
            tn.write(b"\r")
            print("")
        if node.name==PE:
            tn = telnetlib.Telnet(ip, node.console)
            tn.write(b"\r")
            tn.write(b"end\r")
            time.sleep(0.3)
            tn.write(b"\r")
            time.sleep(0.8)
            tn.write(b"conf t\r")
            tn.write(b"int "+bytes(intPE, "utf-8")+b"\r")
            tn.write(b"no shutdown\r")
            tn.write(b"ip add "+bytes(ipPE, "utf-8") +
                    b" "+bytes("255.255.255.0", "utf-8")+b"\r")
            tn.write(b"\r")
            tn.write(b"conf t\r")
            tn.write(f"ip vrf {vrf}\r".encode())
            tn.write(f"rd {rd}\r".encode())
            for rt_in in rt_imp:
                tn.write(f"route-target import {rt_in}\r".encode())
            for rt_out in rt_exp:
                tn.write(f"route-target export {rt_out}\r".encode())
            # tn.write(b"address-family ipv4\r")
            tn.write(b"end\r") 
            time.sleep(0.7)
            print(node.name,"VRF",vrf,"DONE")
            tn.write(b"conf t\r")
            tn.write(b"router rip\r")
            tn.write(b"version 2\r")
            tn.write(f"address-family ipv4 vrf {vrf}\r".encode())
            tn.write(b"redistribute bgp 1 metric transparent\r")
            tn.write(f"network {net}\r".encode())
            tn.write(b"no auto-summary\r")
            tn.write(b"exit-address-family\r")
            tn.write(b"end\r")

        print( "##### Router",node.name," DONE ")
        print("#####################")
    
    pass



def projectSelector():
    global ip
    ip = input("\n The GNS3 Server IP is (for ex: 127.0.0.1) : ")
    server = gns3fy.Gns3Connector("http://"+ip+":3080")

    # Verif -----
    print("Here the list of all GNS3 projects opened : \n\n")
    print(
        tabulate(
            server.projects_summary(is_print=False),
            headers=["Project Name", "Project ID",
                    "Total Nodes", "Total Links", "Status"],
        )
    )
    projet = input("\n The project you want to open is (please put the Project Name) : ")
    project = gns3fy.Project(name=projet, connector=server)
    return project

def intro():
    print("     _     _  __ _      /    _                            ")
    print(" |V||_)---|_)/__|_)    /    |_|   _|_ _ __  _ _|_ _  _|   ")
    print(" | ||     |_)\_||     /     | ||_| |_(_)|||(_| |_(/_(_|   ")
    print(" _                    __        _    _                   ")
    print("|_) _    _|_ _  __   /   _ __ _|_ o (_|    __ _ _|_ _  __")
    print("| \(_)|_| |_(/_ |    \__(_)| | |  | __||_| | (_| |_(_) | ")
    print("               ############################    V.2")
    print("")
    if ((len(sys.argv) >= 2) and (sys.argv[1] == "addCE")):
        print("Starting in New Customer Mode")
        print("You are only going to do configurations needed to add one custumer.")
        print("If you want a total network configuration, run autoRouCo without arguments")
        print("Steps for new ")
        print("1.  Add one routeur manually in GNS3, name him CEx (where x is CE number) and connect it to a PE Router ")
        print("2.  Provide the program with the asked informations")
        print("3.  Wait for this configuration to end, both new CE and PE will be configurated.")
    else:
        print("1.  Open the provided project in GNS3")
        print("2.  Check in GNS3 the GNS3 Server IP")
        print("3.  Launch the project, and wait approximatively for a minute (Time for Routers to boot)")
        print("4.  Provide the program with this IP and the GNS3 Project Name")
        print("5.  Wait for configuration to end")
        print("6.  If you want to add another Customer Edge Router (CE), add one manually in GNS3, name him CEx (where x is CE number) and connect it to a PE Router ")
        print("7.  Provide the program with the asked informations")
        print("8.  Wait for this configuration to end, both new CE and PE will be configurated.")
        print("9.  Don't close the program : You can repeat steps from step 6. here. ")
        print("10. In case you stopped this program, you can launch it again: $ python3 autoRouCo addCE instead of : $ python3 autoRouCo ")
        print("\n\nStarting.\n")

if __name__ == '__main__':
    intro()

    with open("topologyv3.json", "r") as topo:

        topo_data = json.load(topo)
    
    projet = projectSelector()
    projet.get()
    projet.open()

    if ((len(sys.argv) >= 2) and (sys.argv[1] == "addCE")):
        AddingRemoveCE(projet)
        exit()

    #### Ecriture sur routeurs 


    for node in projet.nodes:
        if node.name not in topo_data: # nouveau routeur qui n'a pas de conf sur json
            pass

        print("#####################")
        print(f"##### Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status} -- port {node.console} -- port {node.command_line}")
        tn = telnetlib.Telnet(ip, node.console)
        routeur=topo_data[node.name]
        #Première implem Initialisation 
        tn.write(b"\r")
        tn.write(b"enable\r")
        tn.write(b"\r")
        tn.write(b"conf t\r")
        tn.write(b"no ip domain-lookup\r")
        time.sleep(0.5)
        tn.write(b"\r")
        tn.write(b"end\r")
        time.sleep(0.3)
        tn.write(b"\r")
        tn.write(b"enable\r")
        tn.write(b"conf t\r")
        tn.write(f"hostname {node.name}\r".encode())
        tn.write(b"end\r")
        time.sleep(0.3)
        #Implementation OSPF par routeur
        if "OSPF_id" in routeur:
            tn.write(b"conf t\r")
            tn.write(b"router ospf 10\r")
            tn.write(b"router-id "+bytes(routeur["OSPF_id"], "utf-8") + b"\r")
            tn.write(b"end\r")
            print("OSPF DONE")
        if "ipcef" in routeur:
            tn.write(b"\r")
            tn.write(b"conf t\r")
            tn.write(b"no ip icmp rate-limit unreachable\r")
            tn.write(b"ip tcp synwait-time 5")
            tn.write(b"ip cef\r")
            tn.write(b"end\r")
            time.sleep(0.3)
            print("ipcef DONE")
        # Implementation interface par interface des parametres
        for int in routeur["interfaces"]:
            if int["Interface"]=="Loopback0":
                print(int["Interface"]," : ", node.name)
            else:
                print(int["Interface"]," : ", node.name, "<->",int["With"])
            tn.write(b"\r")
            tn.write(b"enable\r")
            time.sleep(0.8)
            tn.write(b"conf t\r")
            tn.write(b"int "+bytes(int["Interface"], "utf-8")+b"\r")
            tn.write(b"no shutdown\r")
            tn.write(b"ip add "+bytes(int["Address"][0], "utf-8") +
                    b" "+bytes(int["Address"][1], "utf-8")+b"\r")
            tn.write(b"end\r")
            time.sleep(0.5)
            if "OSPF" in int:
                tn.write(b"conf t\r")
                tn.write(b"int "+bytes(int["Interface"], "utf-8")+b"\r")
                # tn.write(b"ip ospf 10 area " +
                        # bytes(str(int["OSPF"]), "utf-8")+b"\r")
                tn.write(b"end\r")
                tn.write(b"conf t\r")
                tn.write(b"router ospf 10\r")
                if int["Interface"]=="Loopback0" :
                    tn.write(b"network "+bytes(int["Address"][0], "utf-8")+b" 0.0.0.0 area "+bytes(str(int["OSPF"]), "utf-8")+b"\r")
                else: # make the mask adaptable
                    tn.write(b"network "+bytes(int["Address"][0], "utf-8")+b" 0.0.0.255 area "+bytes(str(int["OSPF"]), "utf-8")+b"\r")
                tn.write(b"end\r")
                if int["Interface"]=="Loopback0":
                    print(int["Interface"]," : ", node.name,"OSPF DONE")
                else:
                    print(int["Interface"]," : ", node.name, "<->",int["With"],"OSPF DONE")
                time.sleep(0.5)
            #MPLS
            if "MPLS" in int:
                tn.write(b"conf t\r")
                tn.write(b"ip cef t\r")
                tn.write(b"int "+bytes(int["Interface"], "utf-8")+b"\r")
                tn.write(b"mpls ip\r")
                tn.write(b"mpls label protocol ldp\r")
                tn.write(b"end\r")
                if int["Interface"]=="Loopback0":
                    print(int["Interface"]," : ", node.name,"MPLS DONE")
                else:
                    print(int["Interface"]," : ", node.name, "<->",int["With"],"MPLS DONE")
                time.sleep(0.5)
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
                # tn.write(b"address-family ipv4\r")
                tn.write(b"end\r") 
                time.sleep(0.7)
                print(node.name,"VRF",NAME,"DONE")
        #BGP
        if "BGP" in routeur:
            AS=routeur["BGP"]["AS"]
            tn.write(b"conf t\r")
            tn.write(f"router bgp {AS}\r".encode())
            # tn.write(b"bgp log-neighbor-changes\r")
            # if "redistribute" in routeur["BGP"]:
            #     tn.write(b"redistribute connected\r")
            tn.write(b"end\r")
            time.sleep(0.3)
            if "Neighbors" in routeur["BGP"]:
                tn.write(b"\r")
                tn.write(b"conf t\r")
                tn.write(f"router bgp {AS}\r".encode())
                Neighbors=routeur["BGP"]["Neighbors"]
                for neighbor in Neighbors:
                    # tn.write(f"network {neighbor['addr']} mask 255.255.255.0\r".encode())
                    tn.write(f"neighbor {neighbor['addr']} remote-as {neighbor['AS']}\r".encode())
                    time.sleep(0.3)
                    # tn.write(f"neighbor {neighbor['addr']} activate\r".encode())
                    nAS=str(neighbor["AS"])
                    if str(AS)==nAS:
                        tn.write(f"neighbor {neighbor['addr']} update-source Loopback0\r".encode()) 
                    time.sleep(0.3)
                print("BGP DONE")
            if "vpnv4" in routeur["BGP"]:
                Neighbors=routeur["BGP"]["vpnv4"]
                tn.write(b"end\r")  
                tn.write(b"conf t\r")
                tn.write(f"router bgp {AS}\r".encode())
                tn.write(b"address-family vpnv4\r")
                for neighbor in Neighbors:
                    tn.write(f"neighbor {neighbor['addr']} activate\r".encode())
                    # tn.write(f"neighbor {neighbor['addr']} send-community extended\r".encode()) #PAS BESOIN ON IMPLEM DIRECT LES VRFS
                    time.sleep(0.3)
                tn.write(b"end\r")
                print("VPNV4 BGP ACTIVATED")
            if "v_vrf" in routeur["BGP"]:
                Neighbors=routeur["BGP"]["v_vrf"]
                tn.write(b"end\r")  
                tn.write(b"conf t\r")
                tn.write(f"router bgp {AS}\r".encode())
                for neighbor in Neighbors:
                    VRF_name=neighbor["VRF"]
                # neigh=neighbor["Neighbors"]
                    tn.write(f"address-family ipv4 vrf {VRF_name}\r".encode())
                # tn.write(b"redistribute connected\r")
                    tn.write(b"redistribute rip\r")
                # for neig in neigh:
                #     tn.write(f"neighbor {neig['addr']} remote-as {neig['AS']}\r".encode())
                #     tn.write(f"neighbor {neig['addr']} activate\r".encode())
                #     time.sleep(0.3)
                    tn.write(b"exit-address-family\r")
                time.sleep(0.3)
                print("VRF REDISTRIBUTION DONE")
        #RIP
        if "RIP" in routeur:
            RIPconf=routeur["RIP"]
            if "vrf" in RIPconf:
                confVRF=RIPconf["vrf"]
                tn.write(b"conf t\r")
                tn.write(b"router rip\r")
                tn.write(b"version 2\r")
                tn.write(f"address-family ipv4 vrf {confVRF['name']}\r".encode())
                tn.write(b"redistribute bgp 1 metric transparent\r")
                tn.write(f"network {confVRF['network']}\r".encode())
                tn.write(b"no auto-summary\r")
                tn.write(b"exit-address-family\r")
                tn.write(b"end\r")
            if "network" in RIPconf:
                confRIP=RIPconf["network"]
                for net in confRIP:
                    tn.write(b"conf t\r")
                    tn.write(b"router rip\r")
                    tn.write(b"version 2\r")
                    tn.write(f"network {net}\r".encode())
                    tn.write(b"end\r")

        for int in routeur["interfaces"]:
            if "VRF" in int:
                tn.write(b"conf t\r")
                tn.write(b"int "+bytes(int["Interface"], "utf-8")+b"\r")
                tn.write(f"ip vrf forwarding {int['VRF']}\r".encode())
                tn.write(b"end\r")
        time.sleep(0.5)
        tn.write(b"end\r")
        tn.write(b"write\r")
        tn.write(b"\r")

        print( "##### Router",node.name," DONE ")
        print("#####################")

    while True :
        print("\n\n You can now add a new Customer. Add a router manually in GNS3, name him, and respond to the next questions.")
        print("If you don't want to add one, exit the program with Ctrl+C.")
        AddingRemoveCE(projet)