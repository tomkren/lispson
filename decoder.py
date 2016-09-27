import json


def eval_lispson(lispson, lib=None, output_code=False):
    if lib is None:
        lib = {'native': {}}
    code, defs = decode(lispson, lib)
    def_codes = mk_def_codes(defs, lib)

    exec('\n'.join(def_codes), lib['native'])
    val = eval(code, lib['native'])

    if output_code:
        return val, code, def_codes
    else:
        return val


def decode(lispson, lib):
    if isinstance(lispson, str):
        try:
            lispson = json.loads(lispson)
        except ValueError:
            pass
    defs = {}
    code_str = decode_acc(lispson, lib, defs)
    return code_str, defs


def decode_acc(json_o, lib, defs):
    t = type(json_o)
    if t is list:
        return decode_list(json_o, lib, defs)
    elif t is dict:
        return decode_dict(json_o, lib, defs)
    elif t is str:
        handle_def(json_o, lib, defs)
    return str(json_o)


def decode_dict(json_dict, lib, defs):
    keys = list(json_dict)
    if len(keys) == 1:
        head = keys[0]
        body = decode_acc(json_dict[head], lib, defs)
        return lib['target']['lam'](head, body)
    else:
        return json.dumps(json_dict)


def decode_list(json_list, lib, defs):
    if not json_list:  # Is empty ?
        return '[]'
    fun = decode_acc(json_list[0], lib, defs)
    args = json_list[1:]
    if fun == "'":  # Is the function "the quote" ?
        return decode_quote(args)
    if fun in lib['macros']:  # Is the function a macro ?
        return decode_macro(fun, args, lib, defs)
    decoded_args = [decode_acc(o, lib, defs) for o in args]
    if fun == "if":
        return decode_if(decoded_args, lib)
    handle_def(fun, lib, defs)  # Handles definitions if needed.
    return lib['target']['app'](fun, decoded_args)


def decode_quote(args):
    return json.dumps(args[0] if len(args) == 1 else args)


def decode_macro(macro_name, args, lib, defs):
    macros = lib['macros']
    macro = macros[macro_name]
    if not callable(macro):
        macro = eval_lispson(macro, lib)
        macros[macro_name] = macro  # Non-pure optimization saving the compiled macro (can be omitted)
    return decode_acc(macro(*args), lib, defs)


# If needs a special treatment because of if's laziness (we must not evaluate both branches)
def decode_if(decoded_args, lib):
    if len(decoded_args) == 3:
        return lib['target']['if'](*decoded_args)
    else:
        raise ValueError('if must have 3 args', len(decoded_args))


def handle_def(sym, lib, defs):
    lib_defs = lib['defs']
    if sym in lib_defs and sym not in defs:
        sym_def = lib_defs[sym]
        if not isinstance(sym_def, str):
            defs[sym] = None  # So it won't recurse forever ..
            sym_def = decode_acc(sym_def, lib, defs)
            lib_defs[sym] = sym_def  # Again non-pure optimization ..
        defs[sym] = sym_def


def mk_def_codes(defs, lib):
    mk_def = lib['target']['def']
    return [mk_def(var, code) for var, code in defs.items()]


# TESTS :

def test_decode(lib, lispson):
    val, code_str, def_codes = eval_lispson(lispson, lib, output_code=True)
    print(lispson)
    if def_codes:
        print(' >> '+'\n    '.join(def_codes))
    print(' ->', code_str)
    print(' =>', val)
    return val


def run_tests():

    lib = {
        'target': {
            'app': lambda fun, args: fun+'('+(', '.join(args))+')',
            'lam': lambda head, body: '(lambda '+head+': '+body+')',
            'if': lambda p, a, b: a+' if '+p+' else '+b,
            'def': lambda var, code: var+' = '+code,
            'def_fun': lambda name, head, body: 'def '+name+'('+head+'): return '+body
        },
        'native': {
            'eq': lambda a, b: a == b,
            'add': lambda a, b: a + b if not isinstance(a, dict) else dict(a, **b),
            'sub': lambda a, b: a - b,
            'mul': lambda a, b: a * b,
            'mkv': lambda k, v: {k: v},
            'mkp': lambda a, b: [a, b]
        },
        'defs': {
            'plus': 'add',
            'inc': {'x': ['add', 'x', 1]},
            'even': {'n': ['if', ['eq', 'n', 0], True, ['odd', ['sub', 'n', 1]]]},
            'odd': {'n': ['if', ['eq', 'n', 0], False, ['even', ['sub', 'n', 1]]]},
            'factorial': {'n': ['if', ['eq', 'n', 0], 1, ['mul', 'n', ['factorial', ['sub', 'n', 1]]]]},
            'answer': 42,
            'foo': ["'", 'bar']
        },
        'macros': {
            'lambda': {"head, body": ["mkv", "head", "body"]},
            'let_=_in_': {"head, val, body": ["mkp", ["mkv", "head", "body"], 'val']}
        }
    }

    def test(a, b=None):
        should_be, x = (a, b) if (b is not None) else (None, a)
        val = test_decode(lib, x)
        if should_be is not None:
            assert val == should_be, 'Decode test failed!'
            print('OK\n')
        else:
            print()

    test(4, '["add",2,2]')
    test('Hello world!', '''["add","'Hello '","'world!'"]''')
    test('Hello world!', ["add", ["'", "Hello "], ["'", "world!"]])
    test(5, ["len", ["'", "hello"]])
    test(2, '''["len",["'",["hello ","world!"]]]''')
    test(2, ["len", ["'", "hello ", "world!"]])
    test(0, ["len", ["'"]])
    test(0, ["len", []])
    test(2, ["len", {'foo': 42, 'bar': 23}])
    test(1, ["len", ["'", {'foo': 42}]])
    test(3, '[{"x,y":["add","x","y"]},1,2]')
    test(3, '[["lambda","x,y",["add","x","y"]],1,2]')
    test(65, '[["lambda","x,y",["add","x","y"]],23,42]')
    test(['add', ["'", {'foo': 42}], ["'", {'bar': 23}]])
    test(['add', {'foo': 42, "_": 1}, {'bar': 23, "_": 1}])
    test(4, ['let_=_in_', 'x', 2, ["add", "x", "x"]])
    test(4, ['let_=_in_', 'x', ["add", 1, 1], ["add", "x", "x"]])

    test(2, ['inc', 1])
    test(42, ['if', True, 42, 23])
    test(23, ['if', False, 42, 23])
    test(23, ['if', ['eq', 42, 23], 42, 23])

    test(True, ['even', 0])
    test(False, ['odd', 0])
    test(False, ['even', 1])
    test(True, ['odd', 1])
    test(True, ['even', 42])
    test(False, ['odd', 42])
    test(False, ['even', 23])
    test(True, ['odd', 23])

    test(42, 'answer')
    test('bar', 'foo')

    test(23, ['sub', 'answer', 19])
    test(120, ['factorial', 5])

    print('Everything tested was OK :)')


if __name__ == '__main__':
    run_tests()
