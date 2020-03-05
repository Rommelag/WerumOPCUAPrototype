# Prototype for MES ⇔ L2 OPC UA Communication
This is a simple prototype for communicating in OPC-UA between a MES and a L2 equipment. This implements a very early specification prototype — please beware!

## Using
* Install any recent python3 distribution for your system. Linux has it easy, MacOS can use `homebrew`, and Windows can download it from the website or use `choco` or the new `WSL`, if brave enough
* In this folder, create a virtual-env so pip doesn’t install stuff in your system folder: `python3 -m venv venv/` and activate it (Linux: `source venv/bin/activate`, Windows: `\Scripts\activate.bat` or something?)
* Install dependencies: `pip install -r requirements.txt`
* Start the server: `python EquipmentSidedServer.py`
* Let the example client do some magic: `python ExampleClient.py`
* You should see the client invoking a method, and the server printing the received parameters.
* That’s it!

## Interface implemented
Currently, `EquipmentSidedServer.py` implements a very simple interface. We have:
* A set of methods within a machine-node under the Objects node
* Each method has multiple InputArguments
  * Each InputArgument is of a custom datatype, see below
* Each Method has a ParameterDescriptions child
  * The nodes under ParameterDescriptions **must** match the InputArguments
  * Static, required-before-runtime self-introduction data is offered in each ParameterDescription
* The InputArguments are of MESServiceMethodParameterStructure, defined in Types/DataTypes/BaseDataType/Structure/MESServiceMethodParameterStructure
* The MESServiceMethodParameterStructure includes information the MES needs to display a »function-block« to its (human) user

## Ugly parts
* The MESServiceMethodParameterStructure has a Value property. This property can be of multiple primitives (int, float, string, ...). To realize this, the actual type of that property is set to VariantType.Variant — this also allows nesting ExtensionObjects, Variants, etc - which is ugly. This means we don’t have any type-safety here. On the other hand, it allows Null-ability, which is great.
* The ParameterDescriptions folder is by-convention and not enforced in any technical way. Is there any way to have a HasTypeDefinition reference from a method to some type, where we could enforce this?
* EUInformation should be an EUInformation-type. For that I need a ExtensionObject (I think?), and I couldn’t figure out how to put a non-encoded object into one in my stack. Need a bit more time — and maybe a word from Jouni if this is the right way?

## Beware!
Some client (uaexpert / prosys client) don’t correctly display the custom type, neither its definition nor as a method parameter. With these clients you can’t call the methods at all.
