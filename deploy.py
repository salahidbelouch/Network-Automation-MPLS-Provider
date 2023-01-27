import json
import gns3fy
from tabulate import tabulate
import time

topo_data= ""
with open("topology.json", "r") as topo:
    topo_data=json.load(topo)

#GNS3s
print(topo_data["topo"]["routers"][0]["ID"])

# Connect to the GNS3 server
server = gns3fy.Gns3Connector("http://10.56.67.183:3080")

print(
        tabulate(
            server.projects_summary(is_print=False),
            headers=["Project Name", "Project ID", "Total Nodes", "Total Links", "Status"],
        )
    )

projet= gns3fy.Project(name="Nouveau", connector=server)

projet.get()
print(projet)

id =projet.project_id
c7200 =0
projet.open()

for template in server.get_templates():
     if "c7200" in template["name"]:
        print(f"Template: {template['name']} -- ID: {template['template_id']}")
        c7200=template['template_id']
#projet.create()
# creation projet : 

print(projet.stats)



