import json




with open("topologyv3.json", "r") as topo:
    topo_data=json.load(topo)


#V3

for router in topo_data:
    if "BGP" in topo_data[router]:
        print(router)
        print(topo_data[router]["BGP"])