from __future__ import annotations

from json import JSONEncoder, dumps, loads
from enum import Enum
from traceback import print_exc
from typing import Any, Dict, List, Optional
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2

class BadEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__  

class Context(int, Enum):
    Stubbed             = 255
    Unused              = 254           # !!! Don't use any of these! Signature is unknown.
    UnusedVerified      = 253           # Unused but checked signature. All functional but really don't need to be used (some are leftovers)
    Base                = 0             # Allowed when playing events outside of DramaEvent. So really only during the logo sequence
    DramaEvent          = 1             # Traditional event sequences
    Movie               = 2             # Movie playback (subtitles only)
    PuzzleDivide        = 3             # Puzzle where you need to draw a line to cut the board
    PuzzleDrawInput     = 4             # Puzzle where you write your input
    PuzzleKnight        = 5             # Puzzle where you move the knight around the chessboard
    PuzzleLamp          = 6             # Puzzle where you place lights in the forest
    PuzzleOnOff         = 7             # Puzzle where you can turn animation tiles on and off on a grid
    PuzzleOnOff2        = 8             # Puzzle where you light up colored tiles on a grid (the foot one)
    PuzzlePancake       = 9             # Puzzle where you do the pancake version of Towers of Hanoi
    PuzzlePegSolitaire  = 10            # Puzzle where you have the marbles on the board and remove all but one
    PuzzleBridge        = 11            # Puzzle where you cross the bridge (yes, it's redundant)
    PuzzleRose          = 12            # Puzzle where you have to fill the board with enough roses
    PuzzleSkate         = 13            # Puzzle where Layton scoots everywhere
    PuzzleSlide2        = 14            # Puzzle where you slide pieces around the board
    PuzzleTile          = 15            # Puzzle where you drag tiles into places in the correct order
    PuzzleTile2         = 16            # Puzzle where you drag tiles into places in the correct order...
    PuzzleTouch         = 17            # Puzzle where you tap to change images until you think the combination is right
    PuzzleTrace         = 18            # Puzzle where you circle the answer
    PuzzleTraceOnly     = 19            # Puzzle where you circle the answer...
    PuzzleTraceButton   = 20            # Puzzle where you circle the answer......
    PuzzleCouple        = 21            # Puzzle where you move the salt and pepper in pairs

class OperandType(int, Enum):

    def  __str__(self):
        return str(self.name)

    Unknown             = 255
    StandardS32         = 0
    StandardString      = 1
    StandardF32         = 2
    StandardU16         = 3

    Integer1            = 4
    Integer8            = 5
    Integer16           = 6
    Integer32           = 7

    InternalPlaceId     = 10
    InternalPuzzleId    = 11
    InternalMovieId     = 12
    InternalEventId     = 13
    InternalSoundId     = 14
    InternalCharacterId = 15
    PuzzleGroupId       = 16

    StringGamemode      = 20
    StringAnimAsset     = 21
    StringBackground    = 22
    StringAnimation     = 23

    ColorComponent8     = 30
    ColorComponent5     = 31

    Volume              = 35
    Pitch               = 36

    ModeBackground      = 40

    CountStoryPuzzle    = 45

    IndexEventDataCharacter = 50
    IndexChapter            = 51
    IndexEventCounter       = 52
    IndexMystery            = 53
    IndexSubGame            = 54
    IndexPhotoPiece         = 55
    IndexVoiceId            = 56
    IndexGenericTxt2        = 57

    IndexCharacterSlot  = 69

    FlagCharacter       = 70
    FlagAutoEvent       = 71
    FlagStoryItem       = 72
    FlagMemo            = 73

    TimeFrameCount      = 90
    TimeDefinitionEntry = 91
    TimeCharacterFade   = 92

    StringTalkScript    = 100
    StringCharAnim      = 101
    
class OperandCompatibility(int, Enum):
    """Enum storing compatible base case for all overriden operands. Required for validating allowed context replacement.

    Args:
        Enum (_type_): _description_
    """

    Unknown             = OperandType.Unknown.value
    StandardS32         = OperandType.StandardS32.value
    StandardString      = OperandType.StandardString.value
    StandardF32         = OperandType.StandardF32.value
    StandardU16         = OperandType.StandardU16.value

    Integer1            = OperandType.StandardS32.value
    Integer8            = OperandType.StandardS32.value
    Integer16           = OperandType.StandardS32.value
    Integer32           = OperandType.StandardS32.value

    InternalPlaceId     = OperandType.StandardS32.value
    InternalPuzzleId    = OperandType.StandardS32.value
    InternalMovieId     = OperandType.StandardS32.value
    InternalEventId     = OperandType.StandardS32.value
    InternalSoundId     = OperandType.StandardS32.value
    InternalCharacterId = OperandType.StandardS32.value
    PuzzleGroupId       = OperandType.StandardS32.value

    StringGamemode      = OperandType.StandardString.value
    StringAnimAsset     = OperandType.StandardString.value
    StringBackground    = OperandType.StandardString.value
    StringAnimation     = OperandType.StandardString.value

    ColorComponent8     = OperandType.StandardS32.value
    ColorComponent5     = OperandType.StandardS32.value

    Volume              = OperandType.StandardF32.value
    Pitch               = OperandType.StandardS32.value

    ModeBackground      = OperandType.StandardS32.value

    CountStoryPuzzle    = OperandType.StandardS32.value

    IndexEventDataCharacter = OperandType.StandardS32.value
    IndexChapter            = OperandType.StandardS32.value
    IndexEventCounter       = OperandType.StandardS32.value
    IndexMystery            = OperandType.StandardS32.value
    IndexSubGame            = OperandType.StandardS32.value
    IndexPhotoPiece         = OperandType.StandardS32.value
    IndexVoiceId            = OperandType.StandardS32.value
    IndexGenericTxt2        = OperandType.StandardS32.value

    IndexCharacterSlot  = OperandType.StandardS32.value

    FlagCharacter       = OperandType.StandardS32.value
    FlagAutoEvent       = OperandType.StandardS32.value
    FlagStoryItem       = OperandType.StandardS32.value
    FlagMemo            = OperandType.StandardS32.value

    TimeFrameCount      = OperandType.StandardS32.value
    TimeDefinitionEntry = OperandType.StandardS32.value
    TimeCharacterFade   = OperandType.StandardS32.value

    StringTalkScript    = OperandType.StandardString.value
    StringCharAnim      = OperandType.StandardString.value

class OperandDescription():
    # TODO - Scoping
    def __init__(self, type : OperandType, description : str = ""):
        self.operandType : OperandType = type
        self.description : str  = description
    
    def isBaseTypeCompatible(self, newType : OperandType) -> bool:
        compatibilityCurrent = OperandCompatibility[self.operandType.name]
        compatibilityNext = OperandCompatibility[newType.name]
        return compatibilityCurrent.value == compatibilityNext.value

    def __str__(self):
        return str(self.operandType) + "\t" + self.description

class InstructionDescription():
    # TODO - Scoping, but tbh this won't be used anywhere sensitive
    def __init__(self, opcode = None):
        self.opcode                 : Optional[int]             = opcode
        self.name                   : str                       = ""
        self.description            : str                       = ""
        self.contextValid           : List[Context]             = []
        self.isUsed                 : bool                      = False
        self.permittedOperandTypes  : List[OperandDescription]  = []
        
    @staticmethod
    def fromJson(jsonObject : Dict[str, Any]) -> Optional[InstructionDescription]:
        output = InstructionDescription()
        # TODO - Not good especially if versions change. Good luck lol
        goodCandidate = True
        for key in output.__dict__.keys():
            if key not in jsonObject:
                goodCandidate = False
                break
                
        # TODO - Make non-essential fields non-breaking. Eg we can exclude descriptions and its still functionally equivalent
        if goodCandidate:
            output.name = jsonObject["name"]
            output.opcode = jsonObject["opcode"]
            output.description = jsonObject["description"]
            output.isUsed = jsonObject["isUsed"]
            try:
                for operandDef in jsonObject["contextValid"]:
                    output.contextValid.append(Context(operandDef))

                for operandDef in jsonObject["permittedOperandTypes"]:
                    newOperand = OperandDescription(OperandType(operandDef["operandType"]))
                    newOperand.description = operandDef["description"]
                    output.addOperandObject(newOperand)
                return output
            except Exception as e:
                print_exc()
        return None

    def mergeDefinition(self, definition : InstructionDescription):
        """Merges definition of two of the same instruction to improve robustness.
        Will likely throw exception if using two different instructions during merge.
        Descriptions and names are not merged, so be careful not to lose data when merging.

        Args:
            definition (InstructionDescription): Definition of same operand.

        Raises:
            Exception: Thrown if operand types were not consistent.
        """
        for context in definition.contextValid:
            if context not in self.contextValid:
                self.contextValid.append(context)
        
        self.isUsed = self.isUsed | definition.isUsed
        minCountOperands = min(self.getCountOperands(), definition.getCountOperands())

        if minCountOperands > 0:
            for idxOperand, selfDesc, mergeDesc in zip(range(minCountOperands), self.permittedOperandTypes[:minCountOperands], definition.permittedOperandTypes[:minCountOperands]):
                if not(self.changeOperandType(idxOperand, mergeDesc.operandType)):
                    raise Exception("Inconsistent definition detected!")
            self.permittedOperandTypes = self.permittedOperandTypes[:minCountOperands]
        else:
            # TextWindow breaks because there are some poorly formatted entries in ROM, e.g., 20032.
            # To fix this, we only perform a merge when there's more than 1 minimum count.
            # Else, we just accept the first available definition. 
        
            # TODO - Nothing stopping us from getting mode operand count, except counting every definition...
            if self.getCountOperands() < definition.getCountOperands():
                self.permittedOperandTypes = definition.permittedOperandTypes

    def addOperand(self, newType : OperandType) -> bool:
        self.permittedOperandTypes.append(OperandDescription(newType))
        return True
    
    def addOperandObject(self, newOperand : OperandDescription) -> bool:
        self.permittedOperandTypes.append(newOperand)
        return True

    def changeOperandType(self, indexOperand : int, newType : OperandType) -> bool:
        if 0 <= indexOperand < len(self.permittedOperandTypes):
            if self.permittedOperandTypes[indexOperand].isBaseTypeCompatible(newType):
                self.permittedOperandTypes[indexOperand].operandType = newType
                return True
        return False

    def getCountOperands(self):
        return len(self.permittedOperandTypes)
    
    def getOperand(self, indexOperand : int) -> Optional[OperandDescription]:
        if 0 <= indexOperand < self.getCountOperands():
            return self.permittedOperandTypes[indexOperand]
        return None

    def popOperand(self, indexOperand : int) -> Optional[OperandDescription]:
        if 0 <= indexOperand < self.getCountOperands():
            return self.permittedOperandTypes.pop(indexOperand)
        return None

    def getDescription(self) -> str:
        return self.description

    def setDescription(self, desc : str):
        self.description = desc

    def __str__(self):
        output = "Used\t" + str(self.isUsed) + "\nCount\t" + str(self.getCountOperands())
        for indexOperand, operand in enumerate(self.permittedOperandTypes):
            if indexOperand == 0:
                preamble = "\nOprnds\t"
            else:
                preamble = "\n      \t"
            output += preamble + str(operand)
        return output

class ScriptVerificationBank():
    def __init__(self):
        self.__version : float = 0.02
        self.__instructions : Dict[int, InstructionDescription] = {}
        self.__hasChanged = False
    
    def __str__(self) -> str:
        output = ""
        for key in self.__instructions.keys():
            output += "Opcode\t" + str(OPCODES_LT2(key))
            output += "\n" + str(self.__instructions[key]) + "\n\n"
        
        if len(output) > 0:
            output = output[:-2]
        return output

    def toStringByContext(self) -> str:
        outputTree = {"None" : []}
        for context in Context:
            outputTree[context] = []
            self.__instructions
            for opcode in self.getAllInstructionOpcodes():
                if context in self.__instructions[opcode].contextValid:
                    outputTree[context].append(opcode)

        for opcode in self.getAllInstructionOpcodes():
            if self.__instructions[opcode].contextValid == []:
                outputTree["None"].append(opcode)
        
        outputStr = ""
        for context in outputTree.keys():
            outputStr += "\n" + str(context)
            for opcode in outputTree[context]:
                outputStr += "\n\t" + str(opcode) + "\t" + str(OPCODES_LT2(opcode))
        return outputStr

    def hasBankChanged(self) -> str:
        # May not be accurate...
        return self.__hasChanged

    def addInstruction(self, instruction : InstructionDescription) -> bool:
        self.__hasChanged = True
        if instruction.opcode in self.__instructions.keys():
            self.__instructions[instruction.opcode].mergeDefinition(instruction)
        else:
            self.__instructions[instruction.opcode] = instruction
        return True
    
    def removeInstructionByOpcode(self, opcode : int) -> bool:
        if opcode in self.__instructions.keys():
            del self.__instructions[opcode]
            return True
        return False
    
    def removeInstructionByObject(self, instruction : InstructionDescription) -> bool:
        # TODO - Can break since opcode can be changed due to no scoping
        return self.removeInstructionByOpcode(instruction.opcode)

    def getInstructionByOpcode(self, opcode : int) -> Optional[InstructionDescription]:
        if opcode in self.__instructions.keys():
            return self.__instructions[opcode]
        return None
    
    def getAllInstructionOpcodes(self):
        return list(self.__instructions.keys())

    def load(self, jsonStr : str, force = False) -> bool:
        """Loads string representation of database into this object.

        Args:
            jsonStr (str): JSON string containing database.
            force (bool, optional): Override sanity checks to prevent bad JSON parsing. Defaults to False.

        Returns:
            bool: True if loading to any degree was successful.
        """
        def loadData(jsonDict):
            for key in jsonDict.keys():
                if key.isdigit():
                    if (entry := InstructionDescription.fromJson(initial[key])) != None:
                        self.addInstruction(entry)
            return True

        # TODO - type handling
        initial = loads(jsonStr)
        if "version" in initial.keys():
            if initial["version"] <= self.__version or force:
                return loadData(initial)
        elif force:
            return loadData(initial)
        return False

    def export(self, sorted : bool = True, prettyPrint : bool = False) -> str:
        """Returns a JSON string representation of the contents of this object.

        Args:
            sorted (bool, optional): Sort instructions by opcode. Defaults to True.
            prettyPrint (bool, optional): Makes the JSON string larger but more human-readable. Defaults to False.

        Returns:
            str: JSON string.
        """
        exportBank = {"version" : self.__version}
        keys = list(self.__instructions.keys())
        if sorted:
            keys.sort()
        for key in keys:
            exportBank[key] = self.__instructions[key]
        
        if prettyPrint:
            indent = 4
        else:
            indent = None
        return dumps(exportBank, indent=indent, cls=BadEncoder)