import sys
sys.path.insert(0, "..")

import datetime
import opcua

print("connecting")
c=opcua.Client("opc.tcp://localhost:4840/")
c.connect()
print("connected, loading custom type defs")
c.load_type_definitions()

print("got typedefs, finding methods node")
methods = c.get_objects_node().get_child("2:MyCoolMachine/2:MESServices/2:Methods".split("/"))
print("found method node %s, building args"%methods)
batchid_arg = opcua.ua.MESServiceMethodParameterStructure()
batchid_arg.Value = opcua.ua.Variant("BluePill-XXX")
batchid_arg.IsValid = True
batchid_arg.Timestamp = datetime.datetime.now()
batchid_arg.User = "Horst Hofheimer"
water_arg = opcua.ua.MESServiceMethodParameterStructure()
water_arg.Value = opcua.ua.Variant(50.172)
water_arg.IsValid = False
water_arg.Timestamp = datetime.datetime(2001, 12, 24, 18, 24)
water_arg.User = "The measurement man whos years too slow"

print("calling method StartCleaning with args", batchid_arg.__dict__, water_arg.__dict__)
result = methods.call_method("2:StartCleaning", batchid_arg, water_arg)
print("called successfully, result is", result)

c.disconnect()
