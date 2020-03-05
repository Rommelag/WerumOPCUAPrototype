import sys
sys.path.insert(0, "..")

import datetime
import opcua
from opcua import ua, Server, uamethod
from opcua.common.type_dictionary_buider import DataTypeDictionaryBuilder, get_ua_class
from IPython import embed

class DemoServer:

    def __init__(self):
        self.server = Server()

        self.server.set_endpoint('opc.tcp://0.0.0.0:4840')
        self.server.set_server_name('Custom structure demo server')
        # idx name will be used later for creating the xml used in data type dictionary
        self._idx_name = 'http://examples.freeopcua.github.io'
        self.idx = self.server.register_namespace(self._idx_name)

        self.dict_builder = DataTypeDictionaryBuilder(self.server, self.idx, self._idx_name, 'MyDictionary')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        quit()

    def start_server(self):
        self.server.start()

    def create_structure(self, name):
        # save the created data type
        return self.dict_builder.create_data_type(name)

    def complete_creation(self):
        self.dict_builder.set_dict_byte_string()

def start_cleaning(_, batchid, amount):
    print("=== Starting cleaning")
    print("Params:\n\tBatchID: %s\n\tWaterAmount: %s"%(
        batchid._value.__dict__, amount._value.__dict__
        ))
    return [ua.Variant(True)]

def start_sterilization(_, batchid, temperature):
    print("=== Starting sterilization")
    print("Params:\n\tBatchID: %s\n\tTemperature: %s"%(
        batchid._value.__dict__, temperature._value.__dict__
        ))
    return [ua.Variant(True)]

def start_production(_, batchid, count, expiry):
    print("=== Starting production")
    print("Params:\n\tBatchID: %s\n\tAmpouleCount: %s\n\tExpiryDate: %s"%(
        batchid._value.__dict__, count._value.__dict__, expiry._value.__dict__
        ))
    return [ua.Variant(True)]

if __name__ == '__main__':
    with DemoServer() as ua_server:
        parameter_struct_name = 'MESServiceMethodParameterStructure'
        parameter_struct = ua_server.create_structure(parameter_struct_name)
        parameter_struct.add_field('Value', ua.VariantType.Variant)
        parameter_struct.add_field('IsValid', ua.VariantType.Boolean)
        parameter_struct.add_field('Timestamp', ua.VariantType.DateTime)
        parameter_struct.add_field('User', ua.VariantType.String)
        parameter_struct.add_field('EngineeringUnit', ua.VariantType.String)

        ua_server.complete_creation()
        ua_server.server.load_type_definitions()
        print(getattr(ua_server.dict_builder, '_type_dictionary').get_dict_value())

        test_var = ua_server.server.nodes.objects.add_variable(ua.NodeId(namespaceidx=ua_server.idx), 'testStruct',
                                                                ua.Variant(None, ua.VariantType.Null),
                                                                datatype=parameter_struct.data_type)
        test_var.set_writable()
        test_value = get_ua_class(parameter_struct_name)()
        test_value.Value = ua.Variant(23.12)
        test_value.IsValid = True
        test_value.Timestamp = datetime.datetime.now()
        test_value.User = "Foo"
        test_value.EngineeringUnit = "lol"
        test_var.set_value(test_value)

        objects = ua_server.server.get_objects_node()
        mymachine = objects.add_object(2, "MyCoolMachine")
        myservice = mymachine.add_object(2, "MESServices")
        mymethods = myservice.add_object(2, "Methods")

        batchidarg = ua.Argument()
        batchidarg.Name = "BatchId"
        batchidarg.DataType = parameter_struct.data_type
        batchidarg.ValueRank = -1
        batchidarg.ArrayDimensions = []
        batchidarg.Description = ua.LocalizedText("The BatchID of the batch associated with this cleaning run")
        wateramountarg = ua.Argument()
        wateramountarg.Name = "WaterAmount"
        wateramountarg.DataType = parameter_struct.data_type
        wateramountarg.ValueRank = -1
        wateramountarg.ArrayDimensions = []
        wateramountarg.Description = ua.LocalizedText("The amount of water used for this cleaning run")
        start_cleaning_method = mymethods.add_method(2, "StartCleaning", start_cleaning, [batchidarg, wateramountarg], [ua.VariantType.Boolean])
        start_production_param_descs = start_cleaning_method.add_folder(2, "ParameterDescriptions")
        batchid_desc = start_production_param_descs.add_object(2, "BatchId")
        batchid_desc.add_property(2, "Optional", False)
        batchid_desc.add_property(2, "StandardEUInformation", None)
        batchid_desc.add_property(2, "ServiceType", "I didnt quite understand what servicetype means for pasx, sry")
        water_desc = start_production_param_descs.add_object(2, "WaterAmount")
        water_desc.add_property(2, "Optional", True)
        water_desc.add_property(2, "StandardEUInformation", "NotTechnicallyCorrect: kiloLitres")
        water_desc.add_property(2, "ServiceType", "I didnt quite understand what servicetype means for pasx, sry")

        batchidarg = ua.Argument()
        batchidarg.Name = "BatchId"
        batchidarg.DataType = parameter_struct.data_type
        batchidarg.ValueRank = -1
        batchidarg.ArrayDimensions = []
        batchidarg.Description = ua.LocalizedText("The BatchID of the batch associated with this sterilization run")
        temperaturearg = ua.Argument()
        temperaturearg.Name = "Temperature"
        temperaturearg.DataType = parameter_struct.data_type
        temperaturearg.ValueRank = -1
        temperaturearg.ArrayDimensions = []
        temperaturearg.Description = ua.LocalizedText("The temperature set during this sterilization run")
        start_sterilization_method = mymethods.add_method(2, "StartSterilization", start_sterilization, [batchidarg, temperaturearg], [ua.VariantType.Boolean])
        start_production_param_descs = start_sterilization_method.add_folder(2, "ParameterDescriptions")
        batchid_desc = start_production_param_descs.add_object(2, "BatchId")
        batchid_desc.add_property(2, "Optional", False)
        batchid_desc.add_property(2, "StandardEUInformation", None)
        batchid_desc.add_property(2, "ServiceType", "I didnt quite understand what servicetype means for pasx, sry")
        temp_desc = start_production_param_descs.add_object(2, "Temperature")
        temp_desc.add_property(2, "Optional", True)
        temp_desc.add_property(2, "StandardEUInformation", "NotTechnicallyCorrect: degreeC")
        temp_desc.add_property(2, "ServiceType", "I didnt quite understand what servicetype means for pasx, sry")

        batchidarg = ua.Argument()
        batchidarg.Name = "BatchId"
        batchidarg.DataType = parameter_struct.data_type
        batchidarg.ValueRank = -1
        batchidarg.ArrayDimensions = []
        batchidarg.Description = ua.LocalizedText("The BatchID of the batch associated with this sterilization run")
        amountarg = ua.Argument()
        amountarg.Name = "AmpouleCount"
        amountarg.DataType = parameter_struct.data_type
        amountarg.ValueRank = -1
        amountarg.ArrayDimensions = []
        amountarg.Description = ua.LocalizedText("The temperature set during this sterilization run")
        expiryarg = ua.Argument()
        expiryarg.Name = "ExpiryDate"
        expiryarg.DataType = parameter_struct.data_type
        expiryarg.ValueRank = -1
        expiryarg.ArrayDimensions = []
        expiryarg.Description = ua.LocalizedText("The temperature set during this sterilization run")
        start_production_method = mymethods.add_method(2, "StartProduction", start_production, [batchidarg, amountarg, expiryarg], [ua.VariantType.Boolean])
        start_production_param_descs = start_production_method.add_folder(2, "ParameterDescriptions")
        batchid_desc = start_production_param_descs.add_object(2, "BatchId")
        batchid_desc.add_property(2, "Optional", False)
        batchid_desc.add_property(2, "StandardEUInformation", None)
        batchid_desc.add_property(2, "ServiceType", "I didnt quite understand what servicetype means for pasx, sry")
        count_desc = start_production_param_descs.add_object(2, "AmpouleCount")
        count_desc.add_property(2, "Optional", False)
        count_desc.add_property(2, "StandardEUInformation", "NotTechnicallyCorrect: pieces")
        count_desc.add_property(2, "ServiceType", "I didnt quite understand what servicetype means for pasx, sry")
        expiry_desc = start_production_param_descs.add_object(2, "ExpiryDate")
        expiry_desc.add_property(2, "Optional", True)
        expiry_desc.add_property(2, "StandardEUInformation", None)
        expiry_desc.add_property(2, "ServiceType", "I didnt quite understand what servicetype means for pasx, sry")

        ua_server.start_server()
        #embed()
