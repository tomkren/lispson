import json


def eval_lispson(lispson, lib, output_code=False):
    code, defs = decode(lispson, lib)
    def_codes = defs.values()
    defs_code = '\n'.join(def_codes)

    exec(defs_code, lib['native'])
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
    decoded_dict = decode_dict_internal(json_dict, lib, defs)
    if decoded_dict['is_lambda']:
        return lib['target']['lam'](decoded_dict['head'], decoded_dict['body'])
    else:
        return decoded_dict['json_str']


def decode_dict_internal(json_dict, lib, defs):
    keys = list(json_dict)
    if len(keys) == 1:
        head = keys[0]
        body = decode_acc(json_dict[head], lib, defs)
        return {'is_lambda': True, 'head': head, 'body': body}
    else:
        return {'is_lambda': False, 'json_str': json.dumps(json_dict)}


def decode_list(json_list, lib, defs):
    if not json_list:  # Is empty ?
        return '[]'
    if is_infix(json_list, lib):
        return decode_infix(lib, defs, *json_list)
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


def is_infix(json_list, lib):
    if len(json_list) == 3:
        op = json_list[1]
        return isinstance(op, str) and op in lib['infix']
    else:
        return False


def decode_infix(lib, defs, a, op, b):
    decoded_a = decode_acc(a, lib, defs)
    decoded_b = decode_acc(b, lib, defs)
    return lib['target']['infix'](decoded_a, op, decoded_b)


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

            if isinstance(sym_def, dict):

                decoded_dict = decode_dict_internal(sym_def, lib, defs)
                if decoded_dict['is_lambda']:
                    sym_def = lib['target']['def_fun'](sym, decoded_dict['head'], decoded_dict['body'])
                else:
                    sym_def = lib['target']['def'](sym, decoded_dict['json_str'])

            else:
                body = decode_acc(sym_def, lib, defs)
                sym_def = lib['target']['def'](sym, body)

        defs[sym] = sym_def


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
            'def_fun': lambda name, head, body: 'def '+name+'('+head+'): return '+body,
            'infix': lambda a, op, b: '('+a+' '+op+' '+b+')'
        },
        'native': {
            'mkv': lambda k, v: {k: v},
            'mkp': lambda a, b: [a, b]
        },
        'defs': {
            'add': {'x, y': ['x', '+', 'y']},
            'sub': {'a, b': ['a', '-', 'b']},
            'mul': {'a, b': ['a', '*', 'b']},
            'eq': {'a, b': ['a', '==', 'b']},
            'inc': {'x': ['add', 'x', 1]},
            'add_dict': {'a, b': ['dict', 'a', ['**', 'b']]},
            'answer': 42,
            'foo': ["'", 'bar'],
            'even': {'n': ['if', ['eq', 'n', 0], True, ['odd', ['sub', 'n', 1]]]},
            'odd': {'n': ['if', ['eq', 'n', 0], False, ['even', ['sub', 'n', 1]]]},
            'factorial': {'n': ['if', ['n', '==', 0], 1, ['n', '*', ['factorial', ['n', '-', 1]]]]}
        },
        'macros': {
            'lambda': {"head, body": ["mkv", "head", "body"]},
            'let_=_in_': {"head, val, body": ["mkp", ["mkv", "head", "body"], 'val']}
        },
        'infix': {
            '==', '!=', 'and', 'or', '+', '-', '*', '/'
        }
    }

    num_not_tested = 0
    num_tested = 0

    def test(a, b=None):
        should_be, x = (a, b) if (b is not None) else (None, a)
        val = test_decode(lib, x)
        if should_be is not None:
            nonlocal num_tested
            num_tested += 1
            assert val == should_be, 'Decode test failed!'
            print('OK\n')
        else:
            nonlocal num_not_tested
            num_not_tested += 1
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

    test(4, [2, '+', 2])

    test(['add_dict', ["'", {'foo': 42}], ["'", {'bar': 23}]])
    test(['add_dict', {'foo': 42, "_": 1}, {'bar': 23, "_": 1}])

    print('tested:', num_tested)
    print('not tested:', num_not_tested)
    print('Everything tested was OK :)')


if __name__ == '__main__':
    run_tests()
