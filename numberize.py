



    ordinal_words = {'first':1, 'second':2, 'third':3, 'fifth':5, 'eighth':8, 'ninth':9,
                     'twelfth':12}
    ordinal_endings = [('ieth', 'y'), ('th', '')]

    textnum = textnum.replace('-', ' ')

    current = result = 0
    for word in textnum.split():
        if word in ordinal_words:
            scale, increment = (1, ordinal_words[word])
        else:
            for ending, replacement in ordinal_endings:
                if word.endswith(ending):
                    word = "%s%s" % (word[:-len(ending)], replacement)

            if word not in numwords:
                raise Exception("Illegal word: " + word)

            scale, increment = numwords[word]

        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current
# -----------------------------------------------------------------------------
def set_numwords():
    """
    Set up the dictionary of numeric words
    """
    numwords = {}
    units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
        ]

    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
            "eighty", "ninety"]

    scales = ["hundred", "thousand", "million", "billion", "trillion"]

    numwords["and"] = (1, 0)
    for idx, word in enumerate(units):  numwords[word] = (1, idx)
    for idx, word in enumerate(tens):       numwords[word] = (1, idx * 10)
    for idx, word in enumerate(scales): numwords[word] = (10 ** (idx * 3 or 2), 0)

    return numwords

# -----------------------------------------------------------------------------
def tokenize(text):
    """
    Peel the first token off a string and return the tuple (token, remainder).
    If *text* is empty, both token and reminder are None. If *text* contains
    only one token, remainder is None.

    Example:
        >>> tokenize('   Twas brillig and the slithe toves')
        ('Twas', 'brillig and the slithe toves')
        >>> tokenize('humpty    ')
        ('humpty', None)
        >>> tokenize('    ')
        (None, None)
    """
    if text is None:
        (token, remainder) = (None, None)
    elif isinstance(text, str):
        try:
            (token, remainder) = text.strip().split(None, 1)
        except ValueError:
            token = text.strip()
            if not token:
                token = None
            remainder = None
    else:
        (token, remainder) = (text, None)
    return token, remainder
