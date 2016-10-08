import json


def def_fun_bare(name, head, xs):
    body = '\n'.join('    '+x for x in xs.split('\n'))
    return 'function ' + name + '(' + head + ') {\n'+body+'\n}'


def def_fun_with_code(name, head, code, result):
    delim = '\n' if len(code) else ''
    return def_fun_bare(name, head, code + delim + 'return '+result+';')


def do_notation(lines):
    return lines[0] + [do_notation(lines[1:])] if len(lines) > 1 else lines[0]


def set_val(o, key, val):
    o[key] = val
    return val


def get_by_keys(o, keys):
    return get_by_keys(o[keys[0]], keys[1:]) if keys else o


def gets_notation(o, *keys):
    return ['get', o] + [["'", key] for key in keys]


langs = {
    'python': {
        'target': {
            'app': lambda fun, args: fun+'('+(', '.join(args))+')',
            'lam': lambda head, body: '(lambda '+head+': '+body+')',
            'if': lambda p, a, b: '('+a+' if '+p+' else '+b+')',
            'def': lambda var, code: var+' = '+code,
            'def_fun': lambda name, head, body: 'def '+name+'('+head+'): return '+body,
            'infix': lambda a, op, b: '('+a+' '+op+' '+b+')'
        },
        'infix': {  # TODO todle je nešťastný, udělat pořádně, pak něco jako tento jazyk podporuje tyto infixy
                    # TODO a pokud ne tak přepis na prefix adekvátní
            '==', '!=', 'and', 'or', '+', '-', '*', '/', ',', 'is', 'in'
        },
        'defs': {
            'star_app': {'fun, args': ['mkp', 'fun', ['mkp', ["'", '*'], 'args']]},
            'add_dict': {'a, b': ['dict', 'a', ['**', 'b']]}
        },
        'native': {
            'mkv': lambda k, v: {k: v},
            'mkp': lambda a, b: [a, b],
            'cons': lambda x, xs: [x] + xs,
            'mks_py': lambda x: ['*', x],
            'mks_js': lambda x: ['...', x],
            'mkl': lambda *xs: list(xs),
            'do_notation': lambda *lines: do_notation(lines),
            'gets_notation': gets_notation,
            'get': lambda o, *keys: get_by_keys(o, keys),
            'set_val': set_val,
            'tail': lambda xs: xs[1:],
            'n_join': lambda xs: '\n'.join(xs),
            'json_dumps': json.dumps
        },
        'native0': {
            'mkv':           "lambda k, v: {k: v}",
            'mkp':           "lambda a, b: [a, b]",
            'cons':          "lambda x, xs: [x] + xs",
            'mks_py':        "lambda x: ['*', x]",
            'mks_js':        "lambda x: ['...', x]",
            'mkl':           "lambda *xs: list(xs)",
            'do_notation':   lambda *lines: do_notation(lines),
            'gets_notation': gets_notation,
            'get':           lambda o, *keys: get_by_keys(o, keys),
            'set_val':       set_val,
            'tail':          "lambda xs: xs[1:]",
            'n_join':        "lambda xs: '\\n'.join(xs)",
            'json_dumps':    json.dumps
        }
    },
    'javascript': {
        'target': {
            'app': lambda fun, args: fun+'('+(', '.join(args))+')',
            'lam': lambda head, body: '(function('+head+'){return '+body+';})',
            'if': lambda p, a, b: '('+p+' ? '+a+' : '+b+')',
            'def': lambda var, code: 'var '+var+' = '+code+';',
            'def_fun': lambda name, head, body: 'function '+name+' ('+head+') {\n    return '+body+';\n}',
            'def_fun_with_code': def_fun_with_code,  # todo konzistentně !
            'infix': lambda a, op, b: '('+a+' '+op+' '+b+')'
        },
        'infix': {
            '==', '!=', 'and', 'or', '+', '-', '*', '/', ',', 'is', 'in'  # todo !
        },
        'defs': {
            'star_app': {'fun, args': ['mkp', 'fun', ['mkp', ["'", '...'], 'args']]},
            'len': '_.size',
            'mkl': '(function(...xs){return xs;})',  # TODO --- HAX !!! ... vyjasnit
            'add_dict': '(function(a,b){return _.defaults(b,a);})'  # todo vyjasnit kde ma být ta je to napřic targety konzistentní
        },
        # 'native': {},
        'bool': {
            'True': 'true',
            'False': 'false'
        }
    }
}
