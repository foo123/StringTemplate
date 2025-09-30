##
#   StringTemplate,
#   a simple and flexible string template class for PHP, JavaScript, Python
#
#   @version: 1.1.0
#   https://github.com/foo123/StringTemplate
##
import re, math, time

NEWLINE = re.compile(r'\n\r|\r\n|\n|\r')
SQUOTE = re.compile(r"'")
T_REGEXP = type(SQUOTE)

GUID = 0
def guid():
    global GUID
    GUID += 1
    return str(int(time.time())) + '--' + str(GUID)


def createFunction(args, sourceCode, additional_symbols = dict()):
    # http://code.activestate.com/recipes/550804-create-a-restricted-python-function-from-a-string/

    funcName = 'py_dyna_func_' + guid()

    # The list of symbols that are included by default in the generated
    # function's environment
    SAFE_SYMBOLS = [
        "list", "dict", "enumerate", "tuple", "set", "long", "float", "object",
        "bool", "callable", "True", "False", "dir",
        "frozenset", "getattr", "hasattr", "abs", "cmp", "complex",
        "divmod", "id", "pow", "round", "slice", "vars",
        "hash", "hex", "int", "isinstance", "issubclass", "len",
        "map", "filter", "max", "min", "oct", "chr", "ord", "range",
        "reduce", "repr", "str", "type", "zip", "xrange", "None",
        "Exception", "KeyboardInterrupt"
    ]

    # Also add the standard exceptions
    __bi = __builtins__
    if type(__bi) is not dict:
        __bi = __bi.__dict__
    for k in __bi:
        if k.endswith("Error") or k.endswith("Warning"):
            SAFE_SYMBOLS.append(k)
    del __bi

    # Include the sourcecode as the code of a function funcName:
    s = "def " + funcName + "(%s):\n" % args
    s += sourceCode # this should be already properly padded

    # Byte-compilation (optional)
    byteCode = compile(s, "<string>", 'exec')

    # Setup the local and global dictionaries of the execution
    # environment for __TheFunction__
    bis   = dict() # builtins
    globs = dict()
    locs  = dict()

    # Setup a standard-compatible python environment
    bis["locals"]  = lambda: locs
    bis["globals"] = lambda: globs
    globs["__builtins__"] = bis
    globs["__name__"] = "SUBENV"
    globs["__doc__"] = sourceCode

    # Determine how the __builtins__ dictionary should be accessed
    if type(__builtins__) is dict:
        bi_dict = __builtins__
    else:
        bi_dict = __builtins__.__dict__

    # Include the safe symbols
    for k in SAFE_SYMBOLS:

        # try from current locals
        try:
          locs[k] = locals()[k]
          continue
        except KeyError:
          pass

        # Try from globals
        try:
          globs[k] = globals()[k]
          continue
        except KeyError:
          pass

        # Try from builtins
        try:
          bis[k] = bi_dict[k]
        except KeyError:
          # Symbol not available anywhere: silently ignored
          pass

    # Include the symbols added by the caller, in the globals dictionary
    globs.update(additional_symbols)

    # Finally execute the Function statement:
    eval(byteCode, globs, locs)

    # As a result, the function is defined as the item funcName
    # in the locals dictionary
    fct = locs[funcName]
    # Attach the function to the globals so that it can be recursive
    del locs[funcName]
    globs[funcName] = fct

    # Attach the actual source code to the docstring
    fct.__doc__ = sourceCode

    # return the compiled function object
    return fct


class StringTemplate:

    """
    StringTemplate for Python,
    https://github.com/foo123/StringTemplate
    """

    VERSION = "1.1.0"

    guid = guid
    createFunction = createFunction

    def multisplit(tpl, reps, as_array = False):
        a = [ [1, tpl] ]
        reps = enumerate(reps) if as_array else reps.items()
        for r, s in reps:

            c = []
            sr = s if as_array else r
            s = [0, s]
            for ai in a:

                if 1 == ai[0]:

                    b = ai[1].split(sr)
                    bl = len(b)
                    c.append([1, b[0]])
                    if bl > 1:
                        for bj in b[1:]:

                            c.append(s)
                            c.append([1, bj])

                else:

                    c.append(ai)


            a = c
        return a

    def multisplit_re(tpl, rex):
        a = []
        i = 0
        m = rex.search(tpl, i)
        while m:
            a.append([1, tpl[i:m.start()]])
            try:
                mg = m.group(1)
            except:
                mg = m.group(0)
            is_numeric = False
            try:
                mn = int(mg,10)
                is_numeric = False if math.isnan(mn) else True
            except ValueError:
                is_numeric = False
            a.append([0, mn if is_numeric else mg])
            i = m.end()
            m = rex.search(tpl, i)
        a.append([1, tpl[i:]])
        return a

    def arg(key = None, argslen = None):
        out = 'args'

        if key is not None:

            if isinstance(key, str):
                key = key.split('.') if len(key) else []
            else:
                key = [key]
            #givenArgsLen = bool(None !=argslen and isinstance(argslen,str))

            for k in key:
                is_numeric = False
                try:
                    kn = int(k, 10) if isinstance(k, str) else k
                    is_numeric = False if math.isnan(kn) else True
                except ValueError:
                    is_numeric = False
                if is_numeric:
                    out += '[' + str(kn) + ']';
                else:
                    out += '["' + str(k) + '"]';

        return out

    def compile(tpl, raw = False):
        global NEWLINE
        global SQUOTE

        if raw:

            out = 'return ('
            for tpli in tpl:

                notIsSub = tpli[0]
                s = tpli[1]
                out += s if notIsSub else StringTemplate.arg(s)

            out += ')'

        else:

            out = 'return ('
            for tpli in tpl:

                notIsSub = tpli[0]
                s = tpli[1]
                if notIsSub: out += "'" + re.sub(NEWLINE, "' + \"\\n\" + '", re.sub(SQUOTE, "\\'", s)) + "'"
                else: out += " + str(" + StringTemplate.arg(s, "argslen") + ") + "

            out += ')'

        return createFunction('args', "    " + out)


    defaultArgs = re.compile(r'\$(-?[0-9]+)')

    def __init__(self, tpl = '', replacements = None, compiled = False):
        global T_REGEXP

        self.id = None
        self.tpl = None
        self._renderer = None
        self._args = [tpl, StringTemplate.defaultArgs if not replacements else replacements, compiled]
        self._parsed = False

    def __del__(self):
        self.dispose()

    def dispose(self):
        self.id = None
        self.tpl = None
        self._renderer = None
        self._args = None
        self._parsed = None
        return self

    def parse(self):
        if self._parsed is False:
            # lazy init
            tpl = self._args[0]
            replacements = self._args[1]
            compiled = self._args[2]
            self._args = None
            self.tpl = StringTemplate.multisplit_re(tpl, replacements) if isinstance(replacements, T_REGEXP) else StringTemplate.multisplit(tpl, replacements)
            self._parsed = True
            if compiled is True: self._renderer = StringTemplate.compile(self.tpl)
        return self

    def render(self, args = None):
        if args is None: args = []

        # lazy init
        self.parse()
        if self._renderer: return self._renderer(args)

        out = ''
        for t in self.tpl:
            if 1 == t[0]:
                out += t[1]
            else:
                s = t[1]
                out += '' if s not in args else str(args[s])

        return out


__all__ = ['StringTemplate']

