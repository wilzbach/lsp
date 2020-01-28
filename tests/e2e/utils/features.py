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
        if line.startswith("#") and line.find(":") > 0:
            feat, values = line[1:].split(":")
            feat = feat.strip()
            if feat == "pos":
                for val in values.split(","):
                    k, v = val.split("=")
                    k = k.strip()
                    k = shortcuts.get(k, k)
                    assert k in types, f"{k} is an invalid pos option"
                    options[k] = types[k](v.strip())
            elif feat == "action":
                action = values.strip()
                assert action in (
                    "click",
                    "complete",
                ), "{action} is an invalid action"
                options[feat] = action
    return options
