import time
import json
from pyfina import pyfina

pyfina = pyfina("data/")

# pyfina.create("lab.battery",10)

pyfina.prepare("lab.battery",time.time(),100)
pyfina.save()

print json.dumps(pyfina.pipe("lab.battery"))
# print json.dumps(pyfina.data("lab.temperature",1420636578000-(86400000*300),1420636578000,86400))
