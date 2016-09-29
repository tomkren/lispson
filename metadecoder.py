import targets
import json
import tests
import decoder

# These will be overwritten in main
eval_lispson = None
decode_acc = None
decode_dict = None
decode_dict_internal = None

part = None
part2 = None
part3 = None


def print_defs(def_codes):
    print('\n' + '\n'.join(list(def_codes)))


def main():
    meta_lib = {
        'lang': targets.langs['python'],
        'macros': {
            'let': {"head, val, body": ["mkp", ["mkv", "head", "body"], 'val']},
            'let*': {"head, val, body": ["mkp", ["mkv", "head", "body"], ['mkp', ["'", '*'], 'val']]},
            'dot': {"obj, key": [['obj', '+', ["'", '.']], '+', 'key']},
            'do': {"lines": ['mk_do', "lines"]},
        },
        'native': {
            'mkv': lambda k, v: {k: v},
            'mkp': lambda a, b: [a, b],
            'mkl': lambda *xs: list(xs),
            'mk_do': do_notation,
            'get': lambda xs, i: xs[i],
            'n_join': lambda xs: '\n'.join(xs),
            'decode_list': decode_list,
            'handle_def': handle_def,
            'json_dumps': json.dumps
        },
        'defs': {
            'eval_lispson': {'lispson, lib, output_code': ['do', [
                ['let*', 'code, defs', ['decode', 'lispson', 'lib']],
                ['let', 'def_codes', [['dot', 'defs', 'values']]],
                ['let', 'defs_code', ['n_join', 'def_codes']],
                ['let', '_', ['exec', 'defs_code', ['get', 'lib', ["'", 'native']]]],
                ['let', 'val', ['eval', 'code', ['get', 'lib', ["'", 'native']]]],
                ['if', 'output_code', ["mkl", 'val', 'code', 'def_codes'], 'val']
            ]]},
            'decode': {'lispson, lib': ['do', [
                    ['let', 'defs', {}],
                    ['let', 'code_str', ['decode_acc', 'lispson', 'lib', 'defs']],
                    ['mkl', 'code_str', 'defs']
            ]]},
            'decode_acc': {'json_o, lib, defs':
                ['let', 't', ['type', 'json_o'],
                ['if', ['t', 'is', 'list'],
                    ['decode_list', 'json_o', 'lib', 'defs'],
                    ['if', ['t', 'is', 'dict'],
                        ['decode_dict', 'json_o', 'lib', 'defs'],
                        ['if', ['t', 'is', 'str'],
                            ['do', [
                                ['let', '_', ['handle_def', 'json_o', 'lib', 'defs']],
                                ['str', 'json_o']
                            ]],
                            ['str', 'json_o']
                        ]
                    ]
            ]]},
            'decode_dict': {'json_dict, lib, defs': ['do', [
                    ['let', 'decoded_dict', ['decode_dict_internal', 'json_dict', 'lib', 'defs']],
                    ['if', ['get', 'decoded_dict', ["'", 'is_lambda']],
                        [['get', ['get', ['get', 'lib', ["'", 'lang']], ["'", 'target']], ["'", "lam"]],
                         ['get', 'decoded_dict', ["'", 'head']], ['get', 'decoded_dict', ["'", 'body']]],
                        ['get', 'decoded_dict', ["'", 'json_str']]
                    ]
                ]]
            },
            'add_dict': {'a, b': ['dict', 'a', ['**', 'b']]},  # todo udělat pak líp než přes add_dict ale spíš evalnout vnitřky objektů
            'decode_dict_internal': {'json_dict, lib, defs': [
                'let', 'keys', ['list', 'json_dict'],
                ['if', [['len', 'keys'], '==', 1],
                    ['do', [
                        ['let', 'head', ['get', 'keys', 0]],
                        ['let', 'body', ['decode_acc', ['get', 'json_dict', 'head'], 'lib', 'defs']],
                        ['add_dict', ['mkv', ["'", 'is_lambda'], True], ['add_dict', ['mkv', ["'", 'head'], 'head'], ['mkv', ["'", 'body'], 'body']]]
                    ]],
                    ['add_dict', ['mkv', ["'", 'is_lambda'], False], ['mkv', ["'", 'json_str'], ['json_dumps', 'json_dict']]]
                ]]
            }
        }
    }

    global eval_lispson, decode_acc, decode_dict, decode_dict_internal
    eval_lispson, _, def_codes = decoder.eval_lispson('eval_lispson', meta_lib, True)
    decode_acc = decoder.eval_lispson('decode_acc', meta_lib)
    decode_dict = decoder.eval_lispson('decode_dict', meta_lib)
    decode_dict_internal = decoder.eval_lispson('decode_dict_internal', meta_lib)

    global part, part2, part3
    # part,  _, def_codes_1 = decoder.eval_lispson('part', meta_lib, True)
    # part2, _, def_codes_2 = decoder.eval_lispson('part2', meta_lib, True)
    # part3, _, def_codes_3 = decoder.eval_lispson('part3', meta_lib, True)

    num_tested = tests.run_tests(eval_lispson)
    print_defs(def_codes)
    # print_defs(def_codes_1)
    # print_defs(def_codes_2)
    # print_defs(def_codes_3)
    return num_tested


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
    return lib['lang']['target']['app'](fun, decoded_args)


def is_infix(json_list, lib):
    if len(json_list) == 3:
        op = json_list[1]
        return isinstance(op, str) and op in lib['lang']['infix']
    else:
        return False


def decode_infix(lib, defs, a, op, b):
    decoded_a = decode_acc(a, lib, defs)
    decoded_b = decode_acc(b, lib, defs)
    return lib['lang']['target']['infix'](decoded_a, op, decoded_b)


def decode_quote(args):
    return json.dumps(args[0] if len(args) == 1 else args)

# 'decode_quote': {
#    'args': ['json.dumps', ['if', [['len', 'args'], '==', 1], ['at', 'args', 0], 'args']]
# }


def decode_macro(macro_name, args, lib, defs):
    macros = lib['macros']
    macro = macros[macro_name]
    if not callable(macro):
        macro = eval_lispson(macro, lib, False)
        macros[macro_name] = macro  # Non-pure optimization saving the compiled macro (can be omitted)
    return decode_acc(macro(*args), lib, defs)


# If needs a special treatment because of if's laziness (we must not evaluate both branches)
def decode_if(decoded_args, lib):
    if len(decoded_args) == 3:
        return lib['lang']['target']['if'](*decoded_args)
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
                    sym_def = lib['lang']['target']['def_fun'](sym, decoded_dict['head'], decoded_dict['body'])
                else:
                    sym_def = lib['lang']['target']['def'](sym, decoded_dict['json_str'])

            else:
                body = decode_acc(sym_def, lib, defs)
                sym_def = lib['lang']['target']['def'](sym, body)

        defs[sym] = sym_def


def do_notation(lines):
    return lines[0] + [do_notation(lines[1:])] if len(lines) > 1 else lines[0]


if __name__ == '__main__':
    main()
