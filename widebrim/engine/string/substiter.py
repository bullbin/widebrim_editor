from .const import DECODE_MAP

def getSubstitutedString(inString):
    # Not fully accurate

    indexChar = 0
    stringKey = ""
    output = ""
    while indexChar < len(inString):
        if inString[indexChar] == "<":
            stringKey = ""
            while inString[indexChar] != ">":
                indexChar += 1
                stringKey += inString[indexChar]
            stringKey = stringKey[:-1]

            if stringKey in DECODE_MAP:
                output += DECODE_MAP[stringKey]
            else:
                print("Did not have substitution for", stringKey)
        else:
            output += inString[indexChar]
        
        indexChar += 1

    if len(output) > 1536:
        return output[:1536]
    return output