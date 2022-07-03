def getShortenedString(text : str, maxChars=36, extra="(...)", addSpace=True) -> str:
    """Shorten string to fit character length.

    Args:
        text (str): Input string.
        maxChars (int, optional): Max character count to shorten to, including extension. Defaults to 36.
        extra (str, optional): Extension to fit to long strings. Defaults to "(...)".
        addSpace (bool, optional): Add space before extension. Defaults to True.

    Returns:
        str: Shortened string.
    """
    text = " ".join(text.split("\n"))
    if len(text) <= maxChars:
        return text
    else:
        if addSpace:
            extra = " " + extra

        text = text[:maxChars - len(extra)]

        # Rewind to space before last cutoff word
        while len(text) > 0 and text[-1] != " ":
            text = text[:-1]

        # Rewind to word before spaces
        while len(text) > 0 and text[-1] == " ":
            text = text[:-1]

        text = text + extra
        if addSpace:
            checkLen = len(extra) + 1
            if len(text) >= checkLen:
                if text[-checkLen] == " ":
                    return text[:-checkLen] + extra[1:]

        return text