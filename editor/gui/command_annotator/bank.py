from __future__ import annotations

# TODO - clean import
import json

from enum import Enum
from typing import Any, Dict, List, Optional
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2

class BadEncoder(json.JSONEncoder):
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
    Unknown             = 255
    StandardS32         = 0
    StandardString      = 1
    StandardF32         = 2

    Integer32           = 5

    InternalPlaceId     = 10
    InternalPuzzleId    = 11
    InternalMovieId     = 12
    InternalEventId     = 13

    StringGamemode      = 20
    StringAnimAsset     = 21
    StringBackground    = 22

    ColorComponent8     = 30

    ModeBackground      = 40

    IndexEventDataCharacter = 50
    IndexChapter            = 51
    IndexEventCounter       = 52

class OperandCompatibility(int, Enum):
    """Enum storing compatible base case for all overriden operands. Required for validating allowed context replacement.

    Args:
        Enum (_type_): _description_
    """

    Unknown             = OperandType.Unknown.value
    StandardS32         = OperandType.StandardS32.value
    StandardString      = OperandType.StandardString.value
    StandardF32         = OperandType.StandardF32.value

    Integer32           = OperandType.StandardS32.value

    InternalPlaceId     = OperandType.StandardS32.value
    InternalPuzzleId    = OperandType.StandardS32.value
    InternalMovieId     = OperandType.StandardS32.value
    InternalEventId     = OperandType.StandardS32.value

    StringGamemode      = OperandType.StandardString.value
    StringAnimAsset     = OperandType.StandardString.value
    StringBackground    = OperandType.StandardString.value

    ColorComponent8     = OperandType.StandardS32.value

    ModeBackground      = OperandType.StandardS32.value

    IndexEventDataCharacter = OperandType.StandardS32.value
    IndexChapter            = OperandType.StandardS32.value
    IndexEventCounter       = OperandType.StandardS32.value

class OperandDescription():
    def __init__(self, type : OperandType, description : str = ""):
        self.type : OperandType = type
        self.description : str  = description

class InstructionDescription():
    # TODO - Scoping, but tbh this won't be used anywhere sensitive
    def __init__(self, opcode = None):
        self.opcode                 : Optional[int]             = opcode
        self.description            : str                       = ""
        self.contextValid           : List[Context]             = []
        self.isUsed                 : bool                      = False
        self.permittedOperandTypes  : List[OperandDescription]  = []
        
    @staticmethod
    def fromJson(jsonObject : Dict[str, Any]):
        output = InstructionDescription()
        # TODO - Not good especially if versions change. Good luck lol
        goodCandidate = True
        for key in output.__dict__.keys():
            if key not in jsonObject:
                goodCandidate = False
                break
    
        if goodCandidate:
            for key in output.__dict__.keys():
                setattr(output, key, jsonObject[key])
        
            try:
                for indexOperand, operandType in enumerate(output.contextValid):
                    output.contextValid[indexOperand] = Context(operandType)

                for indexOperand, operandType in enumerate(output.permittedOperandTypes):
                    output.permittedOperandTypes[indexOperand] = OperandType(operandType)
                return output
            except Exception as e:
                print(e)
        return None

    def mergeDefinition(self, definition : InstructionDescription):
        """Merges definition of two of the same instruction to improve robustness.
        Will likely throw exception if using two different instructions during merge.
        Descriptions are not merged, so be careful not to lose data when merging.

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
        for idxOperand, selfDesc, mergeDesc in zip(range(minCountOperands), self.permittedOperandTypes[:minCountOperands], definition.permittedOperandTypes[:minCountOperands]):
            if not(self.changeOperandType(idxOperand, mergeDesc.type)):
                raise Exception("Inconsistent definition detected!")
        self.permittedOperandTypes = self.permittedOperandTypes[:minCountOperands]
    
    def addOperand(self, newType : OperandType) -> bool:
        self.permittedOperandTypes.append(OperandDescription(newType))
        self.minCountOperands = len(self.permittedOperandTypes)
        return True

    def changeOperandType(self, indexOperand : int, newType : OperandType) -> bool:
        if 0 <= indexOperand < len(self.permittedOperandTypes):
            compatibilityCurrent = OperandCompatibility(self.permittedOperandTypes[indexOperand].type.value)
            compatibilityNext = OperandCompatibility(newType.value)
            if compatibilityCurrent == compatibilityNext:
                self.permittedOperandTypes[indexOperand].type = newType
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
        output = "Used\t" + str(self.isUsed) + "\nCount\t" + str(self.minCountOperands) + "\nOprnds\t" + str(self.permittedOperandTypes)
        return output

class ScriptVerificationBank():
    def __init__(self):
        self.__version : float = 0.01
        self.__instructions : Dict[int, InstructionDescription] = {}
    
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

    def addInstruction(self, instruction : InstructionDescription) -> bool:
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
        initial = json.loads(jsonStr)
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
        return json.dumps(exportBank, indent=indent, cls=BadEncoder)