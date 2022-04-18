# https://github.com/vijfhoek/regexbot/blob/master/regexbot.py

import regex as re

SED_PATTERN = r"^s/((?:\\\S|[^/])+)/((?:\\\S|[^/])*)(/.*)?"
GROUP0_RE = re.compile(r"(?<!\\)((?:\\\\)*)\\0")


def cleanup_pattern(match):
    from_ = match.group(1)
    to = match.group(2)

    to = to.replace("\\/", "/")
    to = GROUP0_RE.sub(r"\1\\g<0>", to)

    return from_, to


def make_regex(inp, message):
    """Get pattern and message and return output"""
    match = re.match(SED_PATTERN, inp)
    fr, to = cleanup_pattern(match)

    try:
        fl = match.group(3) or ""
        fl = fl[1:]
    except IndexError:
        fl = ""

    # Build Python regex flags
    count = 1
    flags = 0
    for f in fl.lower():
        if f == "i":
            flags |= re.IGNORECASE
        elif f == "m":
            flags |= re.MULTILINE
        elif f == "s":
            flags |= re.DOTALL
        elif f == "g":
            count = 0
        elif f == "x":
            flags |= re.VERBOSE
        else:
            return "unknown flag: {}".format(f)

    def substitute(m):
        s, i = re.subn(fr, to, m, count=count, flags=flags)
        if i > 0:
            return s
        return m

    try:
        return "[SED] " + substitute(message)
    except Exception as e:
        return f"Invalid Regex Pattern: {e}"
