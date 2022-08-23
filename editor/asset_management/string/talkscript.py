from re import search
from typing import Dict, List, Union
from widebrim.engine.anim.font.const import BLEND_MAP
from widebrim.engine.string.const import DECODE_MAP

# TODO - Switch to either fully scan-based or regex solution

ENCODE_MAP : Dict[str, str] = {}
for k, v in DECODE_MAP.items():
    ENCODE_MAP[v] = k

class Command():
    def __init__(self) -> None:
        pass

    def getEncoded(self) -> str:
        return ""
    
    def isValid(self) -> bool:
        return True

class CommandLineBreak(Command):
    def __init__(self) -> None:
        pass

    def getEncoded(self) -> str:
        return "@B"

class CommandSwitchColor(Command):
    def __init__(self, colorCode : str) -> None:
        self.code = colorCode
    
    def getEncoded(self) -> str:
        if self.isValid():
            return "#" + self.code
        return ""
    
    def isValid(self) -> bool:
        return self.code in BLEND_MAP

class CommandSwitchAnimation(Command):
    def __init__(self, animation : str, charId : int) -> None:
        self.nameAnimation : str = animation
        self.idChar : int = charId
    
    def getEncoded(self) -> str:
        encoded = "&setani %i %s&" % (self.idChar, self.nameAnimation.replace(" ", "_"))
        if (len(encoded) - 2) <= 32:
            return encoded
        return ""
    
    def isValid(self) -> bool:
        return self.getEncoded() != ""

class CommandPause(Command):
    def __init__(self) -> None:
        pass
    
    def getEncoded(self) -> str:
        return "@p"

class CommandClear(Command):
    def __init__(self) -> None:
        pass
    
    def getEncoded(self) -> str:
        return "@c"

class CommandSetPitch(Command):
    def __init__(self, pitch : int) -> None:
        self.pitch : int = pitch
    
    def getEncoded(self) -> str:
        if len(str(self.pitch)) == 1:
            return "@v" + str(self.pitch)
        return ""
    
    def isValid(self) -> bool:
        return self.getEncoded() != ""

class Segment():
    def __init__(self, lines : List[Union[str, Command]], hasSplit : bool = False):
        # TODO - Scope once used a bit
        self.commandsAfterFinish : List[Command]        = []
        self.lines : List[List[Union[str, Command]]]    = [[]]

        linesEncoded = lines
        if hasSplit:
            for idxElement in reversed(range(len(linesEncoded))):
                element = linesEncoded[idxElement]
                if type(element) == CommandPause:
                    self.commandsAfterFinish = linesEncoded[idxElement:]
                    linesEncoded = linesEncoded[:idxElement]

            # TODO - Cull properly - e.g, useless color switches, anim switches, etc.
            for idxCommand in reversed(range(len(self.commandsAfterFinish))):
                if type(self.commandsAfterFinish[idxCommand]) == CommandLineBreak:
                    self.commandsAfterFinish.pop(idxCommand)
        
        for item in linesEncoded:
            if type(item) == CommandLineBreak:
                self.lines.append([])
            else:
                if type(item) == str or item.isValid():
                    self.lines[-1].append(item)
    
    def getEncodedString(self) -> str:
        # TODO - Remove disallowed characters
        output = ""
        for line in self.lines:
            lastStrIdx = 0
            for idxToken in reversed(range(len(line))):
                if type(line[idxToken]) == str:
                    lastStrIdx = idxToken
                    break

            for idxToken, token in enumerate(line):
                if type(token) == str:
                    for char in token:
                        if char in ENCODE_MAP:
                            output += "<" + ENCODE_MAP[char] + ">"
                        else:
                            output += char
                    if idxToken == lastStrIdx:
                        output = output.rstrip()
                else:
                    output += token.getEncoded()
            
            # TODO - Match output of linebreak
            if line != self.lines[-1]:
                output += "@B"

        for token in self.commandsAfterFinish:
            output += token.getEncoded()
        return output

    def __str__(self):
        output = []
        for line in self.lines:
            newLine = ""
            for token in line:
                if type(token) == str:
                    newLine = newLine + token
            output.append(newLine)
        return "\n".join(output)

def convertTalkStringToSegments(talkString : str) -> List[Segment]:

    def extractTokensFromLine(line : str) -> List[Union[str, Command]]:

        def extractPauseTokens(segment : str, checkSymbol="P") -> List[Union[str, Union[CommandPause, CommandClear, CommandLineBreak]]]:
            sections = []
            if segment == "":
                return [segment]

            matchString = "@[" + checkSymbol.upper() + "/" + checkSymbol.lower() + "]"

            while (result := search(matchString, segment)) != None:
                start, end = result.span()
                prefix = segment[:start]
                if prefix != "":
                    sections.append(prefix)
                if checkSymbol.upper() == "P":
                    sections.append(CommandPause())
                elif checkSymbol.upper() == "B":
                    sections.append(CommandLineBreak())
                else:
                    sections.append(CommandClear())
                segment = segment[end:]
            if segment != "":
                sections.append(segment)
            return sections
        
        def extractClearTokens(segment : str) -> List[Union[str, CommandClear]]:
            return extractPauseTokens(segment, checkSymbol="C")
        
        def extractLineBreakTokens(segment : str) -> List[Union[str, CommandLineBreak]]:
            return extractPauseTokens(segment, checkSymbol="B")

        def extractSetAniTokens(segment : str) -> List[Union[str, CommandSwitchAnimation]]:
            sections = []
            if segment == "":
                return [segment]

            # There is a limit to length of the SetAni string (32 chars?) but if it doesn't fit, remove it anyways
            matchString = "&([\s\S]*)&"
            setAniString = "[S/s][E/e][T/t][A/a][N/n][I/i]\s([0-9]+)\s([\S\s]+)"

            while (result := search(matchString, segment)) != None:
                
                start, end = result.span()
                prefix = segment[:start]
                if prefix != "":
                    sections.append(prefix)
                
                # TODO - Check length limit
                if (animNameMatch := search(setAniString, result.group(1))) != None and len(result.group(1)) <= 32:
                    sections.append(CommandSwitchAnimation(animNameMatch.group(2).replace("_", " "), int(animNameMatch.group(1))))

                segment = segment[end:]
                
            if segment != "":
                sections.append(segment)
            return sections

        def extractSwitchPitchTokens(segment : str) -> List[Union[str, CommandSetPitch]]:
            sections = []
            if segment == "":
                return [segment]

            matchString = "@v(\S)"

            # TODO - A while loop isn't needed
            while (result := search(matchString, segment)) != None:
                
                start, end = result.span()
                prefix = segment[:start]
                if prefix != "":
                    sections.append(prefix)
                
                if result.group(1).isdigit():
                    sections.append(CommandSetPitch(int(result.group(1))))

                segment = segment[end:]
                
            if segment != "":
                sections.append(segment)
            return sections

        output = [line]
        hasChanged = True
        x = 0
        while True:
            if x >= len(output):
                if not(hasChanged):
                    break
                hasChanged = False
                x = 0
            
            phrase = output.pop(x)
            if type(phrase) != str:
                output.insert(x, phrase)
            else:
                extractors = [extractPauseTokens, extractClearTokens, extractLineBreakTokens, extractSetAniTokens, extractSwitchPitchTokens]
                for extractor in extractors:
                    
                    replacement = extractor(phrase)
                    if replacement[0] != phrase:
                        for item in reversed(replacement):
                            output.insert(x, item)
                        hasChanged = True
                        break
                    else:
                        if extractor == extractors[-1]:
                            output.insert(x, phrase)

            x += 1
        return output

    def applySubstitutionsToSection(sectionLine : List[Union[str, Command]]) -> List[Union[str, Command]]:
        def replaceSubstitutions(segment : str) -> str:
            matchString = "<([\S]*)>"

            while (result := search(matchString, segment)) != None:
                start, end = result.span()
                charCode = result.group(1)
                if charCode in DECODE_MAP:
                    segment = segment[:start] + DECODE_MAP[charCode] + segment[end:]
                else:
                    segment = segment[:start] + segment[end:]

            return segment

        for idxPhrase, phrase in enumerate(sectionLine):
            if type(phrase) == str:
                phraseReplaced = replaceSubstitutions(phrase)
                if phraseReplaced != phrase:
                    sectionLine[idxPhrase] = phraseReplaced
        return sectionLine

    def generateSections(sectionList : List[Union[str, Command]]) -> List[Segment]:
        if sectionList == []:
            return []

        segments = []
        currentSegment = None
        metCondition = False
        for section in sectionList:
            if currentSegment == None:
                currentSegment = []
                
            currentSegment.append(section)
            if issubclass(type(section), Command):
                if type(section) == CommandPause:
                    metCondition = True
                elif type(section) == CommandClear:
                    if metCondition:
                        segments.append(currentSegment)
                        currentSegment = None
            else:
                if metCondition:
                    metCondition = False

        if currentSegment != None:
            segments.append(currentSegment)

        for idxSegment, listCommands in enumerate(segments):
            segments[idxSegment] = Segment(listCommands, hasSplit = idxSegment < (len(segments) - 1))

        return segments

    segments = extractTokensFromLine(talkString)
    segments = applySubstitutionsToSection(segments)
    segments = generateSections(segments)
    return segments