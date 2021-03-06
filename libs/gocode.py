from . import utils


def get_suggestions(api, view, loc):
    src = view.substr(api.new_region(0, view.size()))
    filename = view.file_name()
    cloc = "c{0}".format(loc)
    code, sout, serr = utils.run_go_tool(
        api,
        ["gocode", "-f=csv", "autocomplete", filename, cloc],
        src,
        view,
    )
    if code != 0:
        print("Error while running gocode, err: " + serr)
        return None

    result = []
    for line in filter(bool, sout.split("\n")):
        arg = line.split(",,")
        hint, subj = hint_and_subj(*arg)
        result.append([hint, subj])

    return result


# go to balanced pair, e.g.:
# ((abc(def)))
# ^
# \--------->^
#
# returns -1 on failure
def skip_to_balanced_pair(str, i, open, close):
    count = 1
    i += 1
    while i < len(str):
        if str[i] == open:
            count += 1
        elif str[i] == close:
            count -= 1

        if count == 0:
            break
        i += 1
    if i >= len(str):
        return -1
    return i


# split balanced parens string using comma as separator
# e.g.: "ab, (1, 2), cd" -> ["ab", "(1, 2)", "cd"]
# filters out empty strings
def split_balanced(s):
    out = []
    i = 0
    beg = 0
    while i < len(s):
        if s[i] == ',':
            out.append(s[beg:i].strip())
            beg = i+1
            i += 1
        elif s[i] == '(':
            i = skip_to_balanced_pair(s, i, "(", ")")
            if i == -1:
                i = len(s)
        else:
            i += 1

    out.append(s[beg:i].strip())
    return list(filter(bool, out))


def extract_arguments_and_returns(sig):
    sig = sig.strip()
    if not sig.startswith("func"):
        return [], []

    # find first pair of parens, these are arguments
    beg = sig.find("(")
    if beg == -1:
        return [], []
    end = skip_to_balanced_pair(sig, beg, "(", ")")
    if end == -1:
        return [], []
    args = split_balanced(sig[beg+1:end])

    # find the rest of the string, these are returns
    sig = sig[end+1:].strip()
    sig = sig[1:-1] if sig.startswith("(") and sig.endswith(")") else sig
    returns = split_balanced(sig)
    return args, returns


# takes gocode's candidate and returns sublime's hint and subj
def hint_and_subj(cls, name, type):
    subj = name
    if cls == "func":
        hint = cls + " " + name
        args, returns = extract_arguments_and_returns(type)
        if returns:
            hint += "\t" + ", ".join(returns)
        if args:
            sargs = []
            for i, a in enumerate(args):
                ea = a.replace("{", "\\{").replace("}", "\\}")
                sargs.append("${{{0}:{1}}}".format(i+1, ea))
            subj += "(" + ", ".join(sargs) + ")"
        else:
            subj += "()"
    else:
        hint = cls + " " + name + "\t" + type
    return hint, subj
