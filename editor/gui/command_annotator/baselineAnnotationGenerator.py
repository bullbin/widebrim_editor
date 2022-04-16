from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from widebrim.engine.file import FileInterface, File
from widebrim.madhatter.hat_io.asset import LaytonPack
from widebrim.madhatter.hat_io.asset_script import GdScript, Instruction
from widebrim.madhatter.typewriter.stringsLt2 import OPCODES_LT2

from .bank import InstructionDescription, OperandDescription, OperandType, Context, ScriptVerificationBank

PATH_PACK_EVENT = "/data_lt2/event/ev_d%s.plz"

class BaselineVerificationBank(ScriptVerificationBank):
    def __init__(self):
        super().__init__()

    def __parseScript(self, script : GdScript, id : Optional[str] = None, forceContext=[]):
        """Parses through script to add descriptions for all contained commands.
        Assumes the script is valid.

        Args:
            script (GdScript): Script file to read instructions from.
            id (Optional[str], optional): Identifier replaced when definition is updated. Useful for debugging. Defaults to None.
        """

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

            for operand in command.getFilteredOperands():
                if operand.type == 1:
                    newDefinition.addOperand(OperandType.StandardS32)
                elif operand.type == 2:
                    newDefinition.addOperand(OperandType.StandardF32)
                elif operand.type == 3:
                    newDefinition.addOperand(OperandType.StandardString)
                elif operand.type == 0xc:
                    pass
                else:
                    raise Exception("Operand", operand.type, "not recognised!")
            
            return newDefinition

        for idxCommand in range(script.getInstructionCount()):
            self.addInstruction(generateDescriptionForCommand(script.getInstruction(idxCommand), forceContext))

    def __extractCommands(self, packScript : LaytonPack, forceContext : List[Context] = []):
        # TODO - Abstract, wtf was I thinking??
        for file in packScript.files:
            file : File
            if len(file.name) >= 4 and file.name[-4:] == ".gds":
                script = GdScript()
                script.load(file.data)
                self.__parseScript(script, file.name, forceContext=forceContext)

    def populateBankFromRom(self):
        """Recommended. This pass generates definitions using all scripts in ROM before adding empty definitions for any missing instructions.
        """
        self.fillUsedInstructions()
        self.fillUnusedInstructions()

    def fillUnusedInstructions(self):
        """This pass adds empty definitions for all accessible opcodes in the game that do not have an existing definition.
        """

        def generateDescriptionForUnused(opcode : int) -> InstructionDescription:
            output = InstructionDescription(opcode)
            output.isUsed = False
            output.contextValid.append(Context.Unused)
            return output 

        unused = []
        used = self.getAllInstructionOpcodes()
        for opcode in range(1,163):
            if opcode not in used:
                unused.append(opcode)
        
        for opcodeUnused in unused:
            self.addInstruction(generateDescriptionForUnused(opcodeUnused))

        print(len(unused), "valid instructions were not used in-game.")
        print(unused)

    def fillUsedInstructions(self):
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
                        self.__extractCommands(pack, [Context.DramaEvent])
            else:
                if (data := FileInterface.getData(PATH_PACK_EVENT % str(indexEventScript))) != None:
                    pack = LaytonPack()
                    pack.load(data)
                    self.__extractCommands(pack, [Context.DramaEvent])

        if (data := FileInterface.getData("/data_lt2/script/movie.plz")) != None:
            pack = LaytonPack()
            pack.load(data)
            self.__extractCommands(pack, [Context.Movie])

        if (data := FileInterface.getData("/data_lt2/script/puzzle.plz")) != None:
            pack = LaytonPack()
            pack.load(data)
            self.__extractCommands(pack)

        if (data := FileInterface.getData("/data_lt2/script/logo.gds")) != None:
            script = GdScript()
            script.load(data)
            self.__parseScript(script, "logo.gds", forceContext=[Context.Base])
    
    def applyDefaultHeuristics(self):
        """Unsafe but recommended. Relies on an unmodified scripting engine, but will cleanup definitions from prior methods by employing known good heuristics.

        6 passes are applied to the definitions and they may be destructive:
        - Opcodes executable at the lowest level of the scripting pipeline are confirmed
        - Opcodes executable only during event execution are confirmed
        - Opcodes that are stubbed are confirmed
        - Puzzle-specific opcodes are generated by using known instruction names
        - Remaining puzzle opcodes are cleaned up by applying them to remaining handlers
        - Remaining opcodes are cleaned up by employing known research
        """
        def confirmBaseContext():
            for opcode in [1,2,3,5,6,7,8,9,10,11,12,
                        33,34,45,49,50,51,52,53,54,55,56,
                        105,106,107,108,112,114,115,
                        122,124,127,128,129,131,
                        135,136,137,142,143,144,145,146,
                        152,153,160]:
                if (instruction := self.getInstructionByOpcode(opcode)) != None:
                    if Context.Base not in instruction.contextValid:
                        instruction.contextValid.append(Context.Base)
                    if Context.DramaEvent not in instruction.contextValid:
                        instruction.contextValid.append(Context.DramaEvent)
                else:
                    print("BAD", opcode)

        def confirmEventContext():
            for opcode in [47,141,147,154]:
                if (instruction := self.getInstructionByOpcode(opcode)) != None:
                    if Context.DramaEvent not in instruction.contextValid:
                        instruction.contextValid.append(Context.DramaEvent)
                else:
                    print("BAD", opcode)

        def confirmStubbedContext():
            for opcode in [10,154,86]:
                if (instruction := self.getInstructionByOpcode(opcode)) != None:
                    if Context.Stubbed not in instruction.contextValid:
                        instruction.contextValid.append(Context.Stubbed)
                else:
                    print("BAD", opcode)

        def confirmPuzzleContext():
            
            def groupByTerm(term, targetContext):
                for opcode in self.getAllInstructionOpcodes():
                    name = str(OPCODES_LT2(opcode))
                    instruction = self.getInstructionByOpcode(opcode)
                    if term in name and targetContext not in instruction.contextValid:
                        instruction.contextValid.append(targetContext)
                        print("TERM\t" + str(OPCODES_LT2(opcode)), "->", str(targetContext))
            
            def groupByRange(rangeOp : Tuple[int,int], targetContext : Context, force = True):
                for opcode in range(rangeOp[0], rangeOp[1] + 1):
                    instruction = self.getInstructionByOpcode(opcode)
                    if instruction != None:
                        if not(force):
                            if instruction.contextValid == []:
                                instruction.contextValid.append(targetContext)
                                print("RNGE\t" + str(OPCODES_LT2(opcode)), "->", str(targetContext))
                        else:
                            instruction.contextValid.append(targetContext)
                            print("FRNGE\t" + str(OPCODES_LT2(opcode)), "->", str(targetContext))

            mapTerms : Dict[str, List[Context]] = {"AddOnOffButton" : [Context.PuzzleBridge, Context.PuzzleOnOff],
                                                   "Rose" : [Context.PuzzleRose],
                                                   "OnOff2" : [Context.PuzzleOnOff2],
                                                   "Lamp_" : [Context.PuzzleLamp],
                                                   "Skate_" : [Context.PuzzleSkate],
                                                   "Slide2" : [Context.PuzzleSlide2],
                                                   "Tile2" : [Context.PuzzleTile2],
                                                   "Couple" : [Context.PuzzleCouple],
                                                   "Pancake" : [Context.PuzzlePancake],
                                                   "Knight" : [Context.PuzzleKnight],
                                                   "PegSol" : [Context.PuzzlePegSolitaire]}
            
            mapRange : Dict[Context, List[Tuple[Tuple[int,int], bool]]] = {Context.PuzzleTraceButton : [((24,24), False)],
                                                                           Context.PuzzleTrace : [((25,28), True)],
                                                                           Context.PuzzleTraceOnly : [((25,28), True)],
                                                                           Context.PuzzleDivide : [((13,41), False)],
                                                                           Context.PuzzleDrawInput : [((65,67), False)],
                                                                           Context.PuzzleTile : [((57,60), False)],
                                                                           Context.PuzzleTouch : [((46,46), False)]}

            for term in mapTerms.keys():
                for context in mapTerms[term]:
                    groupByTerm(term, context)
            
            for context in mapRange.keys():
                for opRangeCheck in mapRange[context]:
                    opRange, force = opRangeCheck
                    groupByRange(opRange, context, force=force)

        def applyToRemaining(targetContext : Context):
            for opcode in self.getAllInstructionOpcodes():
                instruction = self.getInstructionByOpcode(opcode)
                if instruction.contextValid == []:
                    instruction.contextValid.append(targetContext)
                    print("NONE\t" + str(OPCODES_LT2(opcode)), "->", str(targetContext))

        def improveUnusedCoverage():

            commandCoverage : Dict[OPCODES_LT2, List[OperandType]]  = {OPCODES_LT2.ExitScript : [],
                                                                       OPCODES_LT2.SetAutoEventNum : [],
                                                                       OPCODES_LT2.AddMatch : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardF32],
                                                                       OPCODES_LT2.AddMatchSolution : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardF32, OperandType.StandardF32, OperandType.StandardF32],
                                                                       OPCODES_LT2.AddBlock : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardString],
                                                                       OPCODES_LT2.AddSprite : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardString, OperandType.StandardString],
                                                                       OPCODES_LT2.SetShapeSolutionPosition : [OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.SetMaxDist : [OperandType.StandardF32],
                                                                       OPCODES_LT2.SetTraceCorrectZone : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.GridAddBlock : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.GridAddLetter : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.AddCup : [OperandType.StandardString, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.SetLiquidColor : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.SetType : [OperandType.StandardS32],
                                                                       OPCODES_LT2.SetSpriteAlpha : [OperandType.StandardS32, OperandType.StandardF32],
                                                                       OPCODES_LT2.SetEventCounter : [OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.ModifySubBGPal : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.AddTileRotateSolution : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardF32, OperandType.StandardF32],
                                                                       OPCODES_LT2.AddDrag2 : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardString],
                                                                       OPCODES_LT2.AddDrag2Anim : [OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.AddDrag2Point : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.AddDrag2Check : [OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.Tile2_AddPointGrid : [OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.Tile2_AddReplace : [OperandType.StandardS32],
                                                                       OPCODES_LT2.StopStream : [OperandType.StandardS32],
                                                                       OPCODES_LT2.SEStop : [OperandType.StandardS32],
                                                                       OPCODES_LT2.MokutekiScreen : [OperandType.StandardS32, OperandType.StandardS32],
                                                                       OPCODES_LT2.DoDiaryAddScreen : [OperandType.StandardS32]}

            for opcode in self.getAllInstructionOpcodes():
                description = self.getInstructionByOpcode(opcode)
                if Context.Unused in description.contextValid:
                    opcode = OPCODES_LT2(opcode)
                    if opcode in commandCoverage:
                        for _idxOperand in range(description.getCountOperands()):
                            description.popOperand(0)
                        for typeOperand in commandCoverage[opcode]:
                            description.addOperand(typeOperand)
                        description.contextValid.pop(description.contextValid.index(Context.Unused))
                        description.contextValid.append(Context.UnusedVerified)
        
        confirmBaseContext()
        confirmEventContext()
        confirmStubbedContext()
        confirmPuzzleContext()
        applyToRemaining(Context.PuzzleTraceButton)
        improveUnusedCoverage()