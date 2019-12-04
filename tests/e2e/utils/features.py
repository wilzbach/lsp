shortcuts = {
    "l": "line",
    "c": "column",
}

types = {
    "line": int,
    "column": int,
}


def parse_options(text):
    """
    Parses completion options from comment strings.
    Example: # pos: l=1,c=28
    """
    options = {}
    for line in text.splitlines():
        if line.startswith("#"):
            feat, values = line[1:].split(":")
            if feat.strip() == "pos":
                for val in values.split(","):
                    k, v = val.split("=")
                    k = k.strip()
                    k = shortcuts.get(k, k)
                    assert k in types, f"{k} is an invalid pos option"
                    options[k] = types[k](v.strip())
    return options
