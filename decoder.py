import json


def json_eval(json_o, lib):
    code_str = decode(json_o, lib)
    return eval(code_str, lib['funs'])


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
            if len(args) == 1:
                return json.dumps(args[0])
            else:
                return json.dumps(args)

        # Is the function a macro ?
        macros = lib['macros']
        if fun in macros:
            macro = macros[fun]
            if not callable(macro):
                macro = json_eval(macro, lib)
                macros[fun] = macro
            return decode(macro(*args), lib)

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


def decodes(json_str, lib):
    return decode(json.loads(json_str), lib)


def test_decode(lib, json_o):
    print(json_o)
    code_str = decode(json_o, lib)
    print(' ->', code_str)
    val = eval(code_str, lib['funs'])
    print(' =>', val, '\n')


def test_decodes(lib, json_str):
    test_decode(lib, json.loads(json_str))


def main():

    lib = {
        'funs': {
            'add': lambda a, b: a+b if not isinstance(a, dict) else dict(a, **b),
            'mkv': lambda key, val: {key: val}
        },
        'macros': {
            'lambda': {"head, body": ["mkv", "head", "body"]}
        }
    }

    def test(x):
        test_decodes(lib, x) if isinstance(x, str) else test_decode(lib, x)

    test('["add",2,2]')
    test('''["add","'Hello '","'world!'"]''')
    test(["add", ["'", "Hello "], ["'", "world!"]])
    test(["len", ["'", "hello"]])
    test('''["len",["'",["hello ","world!"]]]''')
    test(["len", ["'", "hello ", "world!"]])
    test(["len", ["'"]])
    test(["len", []])
    test(["len", {'foo': 42, 'bar': 23}])
    test(["len", ["'", {'foo': 42}]])
    test('[{"x,y":["add","x","y"]},1,2]')
    test('[["lambda","x,y",["add","x","y"]],1,2]')
    test('[["lambda","x,y",["add","x","y"]],23,42]')

    test(['add', ["'", {'foo': 42}], ["'", {'bar': 23}]])
    test(['add', {'foo': 42, "_": 1}, {'bar': 23, "_": 1}])

if __name__ == '__main__':
    main()
