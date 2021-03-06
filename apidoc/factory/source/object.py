from apidoc.object.source_raw import ObjectObject, ObjectArray, ObjectNumber, ObjectString, ObjectBool, ObjectReference, ObjectType, ObjectNone, ObjectDynamic, ObjectConst, ObjectEnum, EnumValue
from apidoc.object.source_raw import Object as ObjectRaw

from apidoc.factory.source.element import Element as ElementFactory

from apidoc.lib.util.cast import to_bool


class Object(ElementFactory):
    """ Object Factory
    """

    def create_from_name_and_dictionary(self, name, datas):
        """Return a populated object Object from dictionary datas
        """
        if "type" not in datas:
            raise ValueError("Missing type in object \"%s\"  \"%s\"." % (name, repr(datas)))

        str_type = str(datas["type"]).lower()
        if not str_type in ObjectRaw.Types:
            type = ObjectRaw.Types("type")
        else:
            type = ObjectRaw.Types(str_type)

        if type is ObjectRaw.Types.object:
            object = ObjectObject()
            object.properties = self.create_dictionary_of_element_from_dictionary("properties", datas)
        elif type is ObjectRaw.Types.array:
            object = ObjectArray()
            if "items" in datas:
                object.items = self.create_from_name_and_dictionary("items", datas["items"])
            if "sample_count" in datas:
                object.sample_count = int(datas["sample_count"])
        elif type is ObjectRaw.Types.number:
            object = ObjectNumber()
        elif type is ObjectRaw.Types.string:
            object = ObjectString()
        elif type is ObjectRaw.Types.bool:
            object = ObjectBool()
            if "sample" in datas:
                object.sample = to_bool(datas["sample"])
        elif type is ObjectRaw.Types.reference:
            object = ObjectReference()
            if "reference" in datas:
                object.reference_name = str(datas["reference"])
        elif type is ObjectRaw.Types.type:
            object = ObjectType()
            object.type_name = str(datas["type"])
        elif type is ObjectRaw.Types.none:
            object = ObjectNone()
        elif type is ObjectRaw.Types.dynamic:
            object = ObjectDynamic()
            if "items" in datas:
                object.items = self.create_from_name_and_dictionary("items", datas["items"])
            if "sample" in datas:
                if isinstance(datas["sample"], dict):
                    object.sample = {}
                    for k, v in datas["sample"].items():
                        object.sample[str(k)] = str(v)
                else:
                    raise ValueError("A dictionnary is expected for dynamic\s object in \"%s\"" % name)
        elif type is ObjectRaw.Types.const:
            object = ObjectConst()
            if "const_type" in datas:
                const_type = str(datas["const_type"])
                if not const_type in ObjectConst.Types:
                    raise ValueError("Const type \"%s\" unknwon" % const_type)
            else:
                const_type = ObjectConst.Types.string
            object.const_type = const_type
            if not "value" in datas:
                raise ValueError("Missing const value")
            object.value = datas["value"]
        elif type is ObjectRaw.Types.enum:
            object = ObjectEnum()
            if not "values" in datas or not isinstance(datas['values'], list):
                raise ValueError("Missing enum values")
            object.values = [str(value) for value in datas["values"]]
            if "descriptions" in datas and isinstance(datas['descriptions'], dict):
                for (value_name, value_description) in datas["descriptions"].items():
                    value = EnumValue()
                    value.name = value_name
                    value.description = value_description
                    object.descriptions.append(value)

            descriptions = [description.name for description in object.descriptions]
            for value_name in [value for value in object.values if value not in descriptions]:
                value = EnumValue()
                value.name = value_name
                object.descriptions.append(value)
        else:
            object = ObjectRaw()

        self.set_common_datas(object, name, datas)
        object.type = type

        if "optional" in datas:
            object.optional = to_bool(datas["optional"])

        return object
