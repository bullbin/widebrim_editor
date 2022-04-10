from __future__ import annotations

# TODO - clean import
import json

from enum import Enum
from msilib.schema import MoveFile
from typing import Any, Dict, List, Optional

from pkg_resources import UnknownExtra
from widebrim.engine.file import FileInterface, File
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.hat_io.asset_script import GdScript, Instruction
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2

# TODO - 0xc culling

PATH_PACK_EVENT = "/data_lt2/event/ev_d%s.plz"

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

class InstructionDescription():
    # TODO - Scoping, but tbh this won't be used anywhere sensitive
    def __init__(self, opcode = None):
        self.opcode       : Optional[int]   = opcode
        self.contextValid : List[Context]   = []
        self.isUsed       : bool            = False

        self.minCountOperands       : int               = 0
        self.permittedOperandTypes  : List[OperandType]= []
        
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

        Args:
            definition (InstructionDescription): Definition of same operand.

        Raises:
            Exception: Thrown if operand types were not consistent.
        """
        for context in definition.contextValid:
            if context not in self.contextValid:
                self.contextValid.append(context)
        
        self.isUsed = self.isUsed | definition.isUsed
        self.minCountOperands = min(self.minCountOperands, definition.minCountOperands)
        for idxOperand, typeSelf, typeDef in zip(range(self.minCountOperands), self.permittedOperandTypes[:self.minCountOperands], definition.permittedOperandTypes[:self.minCountOperands]):
            if not(self.changeOperandType(idxOperand, typeDef)):
                raise Exception("Inconsistent definition detected!")
        self.permittedOperandTypes = self.permittedOperandTypes[:self.minCountOperands]
    
    def correctMinCount(self):
        self.minCountOperands = len(self.permittedOperandTypes)
    
    def addOperand(self, newType : OperandType) -> bool:
        self.permittedOperandTypes.append(newType)
        self.minCountOperands = len(self.permittedOperandTypes)
        return True

    def changeOperandType(self, indexOperand : int, newType : OperandType) -> bool:
        if 0 <= indexOperand < len(self.permittedOperandTypes):
            compatibilityCurrent = OperandCompatibility(self.permittedOperandTypes[indexOperand].value)
            compatibilityNext = OperandCompatibility(newType.value)
            if compatibilityCurrent == compatibilityNext:
                self.permittedOperandTypes[indexOperand] = newType
                return True
        return False

    def __str__(self):
        output = "Used\t" + str(self.isUsed) + "\nCount\t" + str(self.minCountOperands) + "\nOprnds\t" + str(self.permittedOperandTypes)
        return output

def generateDescriptionForCommand(command : Instruction, forceContext=[]) -> InstructionDescription:
    """Creates template description given valid command.

    Args:
        command (Instruction): Instruction with any operands.

    Raises:
        Exception: Raised if an operand could not be decoded.

    Returns:
        InstructionDescription: Template instruction definition.
    """
    newDefinition = InstructionDescription(int.from_bytes(command.opcode,  byteorder='little'))
    newDefinition.isUsed = True
    newDefinition.minCountOperands = len(command.operands)
    newDefinition.contextValid = list(forceContext)

    for operand in command.operands:
        if operand.type == 1:
            newDefinition.permittedOperandTypes.append(OperandType.StandardS32)
        elif operand.type == 2:
            newDefinition.permittedOperandTypes.append(OperandType.StandardF32)
        elif operand.type == 3:
            newDefinition.permittedOperandTypes.append(OperandType.StandardString)
        elif operand.type == 0xc:
            pass
        else:
            raise Exception("Operand", operand.type, "not recognised!")
    
    return newDefinition

def generateDescriptionForUnused(opcode : int) -> InstructionDescription:
    output = InstructionDescription(opcode)
    output.isUsed = False
    output.contextValid.append(Context.Unused)
    return output 

def parseScript(script : GdScript, destMap : Dict[int, InstructionDescription], id : Optional[str] = None, forceContext=[]):
    """Parses through script to add descriptions for all contained commands.
    Assumes the script is valid.

    Args:
        script (GdScript): Script file to read instructions from.
        id (Optional[str], optional): Identifier replaced when definition is updated. Useful for debugging. Defaults to None.
    """
    for idxCommand in range(script.getInstructionCount()):
        command = script.getInstruction(idxCommand)
        opcodeTrans = int.from_bytes(command.opcode, byteorder = "little")
        if opcodeTrans not in destMap.keys():
            destMap[opcodeTrans] = generateDescriptionForCommand(command, forceContext)
        else:
            definition = generateDescriptionForCommand(command, forceContext)
            destMap[opcodeTrans].mergeDefinition(definition)

def extractCommands(packScript : LaytonPack, destMap : Dict[int, InstructionDescription], forceContext : List[Context] = []):
    # TODO - Abstract, wtf was I thinking??
    for file in packScript.files:
        file : File
        if len(file.name) >= 4 and file.name[-4:] == ".gds":
            script = GdScript()
            script.load(file.data)
            parseScript(script, destMap, file.name, forceContext=forceContext)

def fillUnusedInstructions(destMap : Dict[int, InstructionDescription]):
    unused = []
    for opcode in range(1,163):
        if opcode not in destMap.keys():
            unused.append(opcode)
    
    for opcodeUnused in unused:
        destMap[opcodeUnused] = generateDescriptionForUnused(opcodeUnused)

    print(len(unused), "valid instructions were not used in-game.")
    print(unused)

def fillUsedInstructions(destMap : Dict[int, InstructionDescription]):
    """Uses scripts inside ROM to build descriptions on instructions.
    """
    for indexEventScript in range(10, 31):
        # Skip unused directories (less warnings)
        if indexEventScript in [27,28,29]:
            pass
        elif indexEventScript == 24:
            for segment in ["24a", "24b", "24c"]:
                if (data := FileInterface.getData(PATH_PACK_EVENT % segment)) != None:
                    pack = LaytonPack()
                    pack.load(data)
                    extractCommands(pack, destMap, [Context.DramaEvent])
        else:
            if (data := FileInterface.getData(PATH_PACK_EVENT % str(indexEventScript))) != None:
                pack = LaytonPack()
                pack.load(data)
                extractCommands(pack, destMap, [Context.DramaEvent])

    if (data := FileInterface.getData("/data_lt2/script/movie.plz")) != None:
        pack = LaytonPack()
        pack.load(data)
        extractCommands(pack, destMap, [Context.Movie])

    if (data := FileInterface.getData("/data_lt2/script/puzzle.plz")) != None:
        pack = LaytonPack()
        pack.load(data)
    extractCommands(pack, destMap)

    if (data := FileInterface.getData("/data_lt2/script/logo.gds")) != None:
        script = GdScript()
        script.load(data)
        parseScript(script, destMap, "logo.gds", forceContext=[Context.Base])

def tidy(destMap : Dict[int, InstructionDescription]):
    for key in destMap.keys():
        destMap[key].correctMinCount()

def printBank(destMap : Dict[int, InstructionDescription]):
    keys = list(destMap.keys())
    keys.sort()
    for key in keys:
        print("Opcode\t" + str(OPCODES_LT2(key)))
        print(str(destMap[key]))
        print()

def exportBank(filename : str, destMap : Dict[int, InstructionDescription], sorted=True, prettyPrint=True) -> bool:
    keys = list(destMap.keys())
    if sorted:
        keys.sort()
    outputMap = {}
    for key in keys:
        outputMap[key] = destMap[key]

    if prettyPrint:
        indent = 4
    else:
        indent = None

    try:
        with open(filename, 'w+') as jsonOut:
            jsonOut.write(json.dumps(outputMap, indent=indent, cls=BadEncoder))
            return True
    except OSError:
        return False

def importBank(filename : str) -> Dict[int, InstructionDescription]:
    initial = {}
    try:
        with open(filename, 'r') as jsonIn:
            initial = json.loads(jsonIn.read())
    except:
        pass
    
    output = {}
    for key in initial.keys():
        if (entry := InstructionDescription.fromJson(initial[key])) != None:
            output[int(key)] = entry
    return output