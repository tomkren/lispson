import targets
import json
import tests
import decoder


def main():
    meta_lib = {
        'lang': targets.langs['python'],
        'macros': {
            'let': {"head, val, body": ["mkp", ["mkv", "head", "body"], 'val']},
            'let*': {"head, val, body": ["mkp", ["mkv", "head", "body"], ['mkp', ["'", '*'], 'val']]},
            'dot': {"obj, key": [['obj', '+', ["'", '.']], '+', 'key']},
            'do': 'do_notation',
            'gets': 'gets_notation'
        },
        'native': {
            'mkv': lambda k, v: {k: v},
            'mkp': lambda a, b: [a, b],
            'mkl': lambda *xs: list(xs),
            'do_notation': lambda *lines: do_notation(lines),
            'gets_notation': gets_notation,
            'get': lambda o, *keys: get_by_keys(o, keys),
            'set_val': set_val,
            'tail': lambda xs: xs[1:],
            'n_join': lambda xs: '\n'.join(xs),
            'json_dumps': json.dumps
        },
        'defs': {
            'eval_lispson': {'lispson, lib, output_code': ['do',
                ['let*', 'code, defs', ['decode', 'lispson', 'lib']],
                ['let', 'def_codes', [['dot', 'defs', 'values']]],
                ['let', 'defs_code', ['n_join', 'def_codes']],
                ['let', '_', ['exec', 'defs_code', ['gets', 'lib', 'native']]],
                ['let', 'val', ['eval', 'code', ['gets', 'lib', 'native']]],
                ['if', 'output_code', ["mkl", 'val', 'code', 'def_codes'], 'val']
            ]},
            'decode': {'lispson, lib': ['do',
                    ['let', 'defs', {}],
                    ['let', 'code_str', ['decode_acc', 'lispson', 'lib', 'defs']],
                    ['mkl', 'code_str', 'defs']
            ]},
            'decode_acc': {'json_o, lib, defs':
                ['let', 't', ['type', 'json_o'],
                ['if', ['t', 'is', 'list'],
                    ['decode_list', 'json_o', 'lib', 'defs'],
                    ['if', ['t', 'is', 'dict'],
                        ['decode_dict', 'json_o', 'lib', 'defs'],
                        ['if', ['t', 'is', 'str'],
                            ['do',
                                ['let', '_', ['handle_def', 'json_o', 'lib', 'defs']],
                                ['str', 'json_o']
                            ],
                            ['str', 'json_o']
                        ]
                    ]
            ]]},
            'decode_dict': {'json_dict, lib, defs': ['do',
                    ['let', 'decoded_dict', ['decode_dict_internal', 'json_dict', 'lib', 'defs']],
                    ['if', ['gets', 'decoded_dict', 'is_lambda'],
                        [['gets', 'lib', 'lang', 'target', "lam"],
                         ['gets', 'decoded_dict', 'head'], ['gets', 'decoded_dict', 'body']],
                        ['gets', 'decoded_dict', 'json_str']
                    ]
                ]
            },
            'add_dict': {'a, b': ['dict', 'a', ['**', 'b']]},  # todo udělat pak líp než přes add_dict ale spíš evalovat obecně vnitřky objektů
            'decode_dict_internal': {'json_dict, lib, defs': [
                'let', 'keys', ['list', 'json_dict'],
                ['if', [['len', 'keys'], '==', 1],
                    ['do',
                        ['let', 'head', ['get', 'keys', 0]],
                        ['let', 'body', ['decode_acc', ['get', 'json_dict', 'head'], 'lib', 'defs']],
                        ['add_dict', ['mkv', ["'", 'is_lambda'], True], ['add_dict', ['mkv', ["'", 'head'], 'head'], ['mkv', ["'", 'body'], 'body']]]
                    ],
                    ['add_dict', ['mkv', ["'", 'is_lambda'], False], ['mkv', ["'", 'json_str'], ['json_dumps', 'json_dict']]]
                ]]
            },
            'decode_list': {'json_list, lib, defs':
                ['if', ['not', 'json_list'],
                    ["'", '[]'],
                ['if', ['is_infix', 'json_list', 'lib'],
                    ['decode_infix', 'lib', 'defs', ['*', 'json_list']],
                ['do',
                ['let', 'fun', ['decode_acc', ['get', 'json_list', 0], 'lib', 'defs']],
                ['let', 'args', ['tail', 'json_list']],
                ['if', ['fun', '==', ["'", "'"]],
                    ['decode_quote', 'args'],
                ['if', ['fun', 'in', ['gets', 'lib', 'macros']],
                    ['decode_macro', 'fun', 'args', 'lib', 'defs'],
                ['do', ['let', 'decoded_args', ['list', ['map', {'o': ['decode_acc', 'o', 'lib', 'defs']}, 'args']]],  # todo je tu list(map(..))
                ['if', ['fun', '==', ["'", 'if']],
                    ['decode_if', 'decoded_args', 'lib'],
                ['do',
                ['let', '_', ['handle_def', 'fun', 'lib', 'defs']],
                [['gets', 'lib', 'lang', 'target', 'app'], "fun", 'decoded_args']]]]]]]]]
            },
            'decode_quote': {
                'args': ['json_dumps', ['if', [['len', 'args'], '==', 1], ['get', 'args', 0], 'args']]
            },
            'is_infix': {'json_list, lib':
                ['if', [['len', 'json_list'], '==', 3],
                    ['do',
                        ['let', 'op', ['get', 'json_list', 1]],
                        [['isinstance', 'op', 'str'], 'and', ['op', 'in', ['gets', 'lib', 'lang', 'infix']]]
                    ],
                    False
                ]
            },
            'decode_infix': {'lib, defs, a, op, b':
                ['do',
                    ['let', 'decoded_a', ['decode_acc', 'a', 'lib', 'defs']],
                    ['let', 'decoded_b', ['decode_acc', 'b', 'lib', 'defs']],
                    [['gets', 'lib', 'lang', 'target', 'infix'], 'decoded_a', 'op', 'decoded_b']
            ]},
            'decode_macro': {'macro_name, args, lib, defs': ['do',
                ['let', 'macros', ['gets', 'lib', "macros"]],
                ['let', 'macro', ['get', 'macros', 'macro_name']],
                ['let', 'macro_fun', ['eval_lispson', 'macro', 'lib', False]],
                ['decode_acc', ['macro_fun', ['*', 'args']], 'lib', 'defs']
            ]},
            'decode_if': {'decoded_args, lib':
                [['gets', 'lib', 'lang', 'target', 'if'], ['*', 'decoded_args']]
            },
            'handle_def': {'sym, lib, defs': [
                'let', 'lib_defs', ['gets', 'lib', 'defs'],
                ['if', [['sym', 'in', 'lib_defs'], 'and', ['not', ['sym', 'in', 'defs']]],
                    ['let', 'sym_def', ['get', 'lib_defs', 'sym'],
                        ['if', ['isinstance', 'sym_def', 'str'],
                            ['set_val', 'defs', 'sym', 'sym_def'],
                            ['do',
                                ['let', '_', ['set_val', 'defs', 'sym', 'None']],
                                ['if', ['isinstance', 'sym_def', 'dict'],
                                    ['handle_def_dict', 'sym', 'lib', 'defs', 'sym_def'],
                                    ['handle_def_non_dict', 'sym', 'lib', 'defs', 'sym_def']]
                            ]
                        ]],
                    'None'
                ]
            ]},
            'handle_def_dict': {'sym, lib, defs, sym_def': ['do',
                ['let', 'decoded_dict', ['decode_dict_internal', 'sym_def', 'lib', 'defs']],
                ['let', 'target', ['gets', 'lib', 'lang', 'target']],
                ['let', 'sym_def',
                    ['if', ['gets', 'decoded_dict', 'is_lambda'],
                        [['gets', 'target', 'def_fun'], 'sym', ['gets', 'decoded_dict', 'head'], ['gets', 'decoded_dict', 'body']],
                        [['gets', 'target', 'def'], 'sym', ['gets', 'decoded_dict', 'json_str']]]],
                ['set_val', 'defs', 'sym', 'sym_def']
            ]},
            'handle_def_non_dict': {'sym, lib, defs, sym_def': ['do',
                ['let', 'body', ['decode_acc', 'sym_def', 'lib', 'defs']],
                ['let', 'sym_def',
                 [['gets', 'lib', 'lang', 'target', 'def'], 'sym', 'body']],
                ['set_val', 'defs', 'sym', 'sym_def']
            ]}
        },
    }

    eval_lispson, _, def_codes = decoder.eval_lispson('eval_lispson', meta_lib, True)

    num_tested = tests.run_tests(eval_lispson)
    print_defs(def_codes)
    return num_tested


def do_notation(lines):
    return lines[0] + [do_notation(lines[1:])] if len(lines) > 1 else lines[0]


def set_val(o, key, val):
    o[key] = val
    return val


def get_by_keys(o, keys):
    return get_by_keys(o[keys[0]], keys[1:]) if keys else o


def gets_notation(o, *keys):
    return ['get', o] + [["'", key] for key in keys]


def print_defs(def_codes):
    print('\n' + '\n'.join(list(def_codes)))


if __name__ == '__main__':
    main()
