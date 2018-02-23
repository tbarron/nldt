# -----------------------------------------------------------------------------
def scan(text):
    """
    Scan a string of text, extracting numbers and returning the result

    Example:
        >>> scan('seventy-five')
        [75]
        >>> scan('seventy-six trombones led the big parade')
        [76, 'trombones led the big parade']
        >>> scan('ten o'clock on june third')
        [10, "o'clock on june", 3]
        >>> scan('three weeks before the fifth of may seven years ago')
        [3, 'weeks before the', 5, 'of may', 7, 'years ago']
        >>> scan('only three weeks before the fifth of may seven years ago')
        ['only', 3, 'weeks before the', 5, 'of may', 7, 'years ago']
    """
    def assemble_result(result, num, word):
        if num:
            result.append(num)
        if word:
            if len(result) < 1:
                result.append(word)
            elif isinstance(result[-1], str):
                result[-1] = " ".join([result[-1], word])
            else:
                result.append(word)
    result = []
    num, word, text = subscan(text)
    while text:
        assemble_result(result, num, word)
        num, word, text = subscan(text)

    assemble_result(result, num, word)
    return result


# -----------------------------------------------------------------------------
def subscan(textnum, numwords=None):
    """
    Read and translate the leading numeric expression

        Example:
        >>> subscan('seventy-five')
        (75, None, None)
        >>> subscan('seventy-six trombones led the big parade')
        (76, 'trombones', 'led the big parade')
        >>> subscan('ten o'clock on june third')
        10, "o'clock", "on june third")
        >>> subscan('three weeks before the fifth of may seven years ago')
        (3, 'weeks', 'before the fifth of may seven years ago']
        >>> scan('only three weeks before the fifth of may seven years ago')
        (None, 'only', 'three weeks before the fifth of may seven years ago')
    """
    if numwords is None:
        try:
            numwords = subscan._numwords
        except AttributeError:
            subscan._numwords = set_numwords()
            numwords = subscan._numwords

    ordinal_words = {'first':1, 'second':2, 'third':3, 'fifth':5, 'eighth':8, 'ninth':9,
                     'twelfth':12}
    ordinal_endings = [('ieth', 'y'), ('th', '')]


    textnum = textnum.replace('-', ' ')

    current = result = 0
    word, rest = tokenize(textnum)
    while word:
        if word in ordinal_words:
            scale, increment = (1, ordinal_words[word])
        else:
            for ending, replacement in ordinal_endings:
                if word.endswith(ending):
                    word = "%s%s" % (word[:-len(ending)], replacement)

            if word not in numwords:
                break
                # raise Exception("Illegal word: " + word)

            scale, increment = numwords[word]

        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

        word, rest = tokenize(rest)

    return result + current, word, rest

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
