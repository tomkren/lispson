import json


def json_eval(json_o, lib=None, output_code=False):
    if lib is None:
        lib = {'native': {}}
    code_str = decode(json_o, lib)
    val = eval(code_str, lib['native'])
    if output_code:
        return val, code_str
    else:
        return val


def decode(json_o, lib):
    t = type(json_o)
    if t is list:
        return decode_list(json_o, lib)
    elif t is dict:
        return decode_dict(json_o, lib)
    else:
        return str(json_o)


def decode_list(json_list, lib):
    # Is json_list non-empty ?
    if json_list:

        fun = decode(json_list[0], lib)
        args = json_list[1:]

        # Is the function "the quote" ?
        if fun == "'":
            return json.dumps(args[0] if len(args) == 1 else args)

        # Is the function a macro ?
        macros = lib['macros']
        if fun in macros:
            macro = macros[fun]
            if not callable(macro):
                macro = json_eval(macro, lib)
                # Non-pure optimization saving the compiled macro (can be omitted)
                macros[fun] = macro
            return decode(macro(*args), lib)

        # todo: check for "fun in funs"
        # ...

        # Non-meta function
        else:
            return fun+'('+(', '.join([decode(o, lib) for o in args]))+')'

    # Empty json_list
    else:
        return '[]'


def decode_dict(json_dict, lib):
    keys = list(json_dict)
    if len(keys) == 1:
        head = keys[0]
        body = decode(json_dict[head], lib)
        return '(lambda '+head+': '+body+')'
    else:
        return json.dumps(json_dict)


# Utils, tests, etc ...

def decodes(json_str, lib):
    return decode(json.loads(json_str), lib)


def test_decode(lib, json_o):
    if isinstance(json_o, str):
        json_o = json.loads(json_o)
    val, code_str = json_eval(json_o, lib, output_code=True)
    print(json_o)
    print(' ->', code_str)
    print(' =>', val)
    return val


# def test_decodes(lib, json_str):
#    test_decode(lib, json.loads(json_str))


# Main with tests.
def main():

    lib = {
        'native': {
            'add': lambda a, b: a+b if not isinstance(a, dict) else dict(a, **b),
            'mkv': lambda k, v: {k: v},
            'mkp': lambda a, b: [a, b]
        },
        'funs': {
            'plus': 'add'
            # todo: přidat další
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

if __name__ == '__main__':
    main()
