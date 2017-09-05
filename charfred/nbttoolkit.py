from nbt import TAG_Int, TAG_Long, TAG_Byte, TAG_List, TAG_Float
from nbt import TAG_Short, TAG_String, TAG_Double, TAG_Compound


def addByteTAG(nbtobj, name, value):
    byteTag = TAG_Byte(name=name, value=value)
    nbtobj.value.append(byteTag)


def addShortTAG(nbtobj, name, value):
    shortTag = TAG_Short(name=name, value=value)
    nbtobj.value.append(shortTag)


def addIntTAG(nbtobj, name, value):
    intTag = TAG_Int(name=name, value=value)
    nbtobj.value.append(intTag)


def addLongTAG(nbtobj, name, value):
    longTag = TAG_Long(name=name, value=value)
    nbtobj.value.append(longTag)


def addFloatTAG(nbtobj, name, value):
    floatTag = TAG_Float(name=name, value=value)
    nbtobj.value.append(floatTag)


def addDoubleTAG(nbtobj, name, value):
    doubleTag = TAG_Double(name=name, value=value)
    nbtobj.value.append(doubleTag)


def addStringTAG(nbtobj, name, value):
    stringTag = TAG_String(name=name, value=value)
    nbtobj.value.append(stringTag)


def addListTAG(nbtobj, name, value):
    listTag = TAG_List(name=name, value=value)
    nbtobj.value.append(listTag)


def addCompoundTAG(nbtobj, name, value):
    compTag = TAG_Compound(name=name, value=value)
    nbtobj.value.append(compTag)
