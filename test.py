import json
import gns3fy
from gns3fy import Node
from tabulate import tabulate
import time
import telnetlib



with open("topologyv3.json", "r") as topo:
    topo_data=json.load(topo)

for i in topo_data:
    print(topo_data[i]['interfaces'])