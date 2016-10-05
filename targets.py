def def_fun_bare(name, head, xs):
    body = '\n'.join('    '+x for x in xs.split('\n'))
    return 'function ' + name + '(' + head + ') {\n'+body+'\n}'


def def_fun_with_code(name, head, code, result):
    delim = '\n' if len(code) else ''
    return def_fun_bare(name, head, code + delim + 'return '+result+';')
#    return 'function '+name+' ('+head+') {\n  return '+result+';\n}'


langs = {
    'python': {
        'target': {
            'app': lambda fun, args: fun+'('+(', '.join(args))+')',
            'lam': lambda head, body: '(lambda '+head+': '+body+')',
            'if': lambda p, a, b: a+' if '+p+' else '+b,
            'def': lambda var, code: var+' = '+code,
            'def_fun': lambda name, head, body: 'def '+name+'('+head+'): return '+body,
            'infix': lambda a, op, b: '('+a+' '+op+' '+b+')'
        },
        'infix': {  # TODO todle je nešťastný, udělat pořádně, pak něco jako tento jazyk podporuje tyto infixy
                    # TODO a pokud ne tak přepis na prefix adekvátní
            '==', '!=', 'and', 'or', '+', '-', '*', '/', ',', 'is', 'in'
        },
        'defs': {}
    },
    'javascript': {
        'target': {
            'app': lambda fun, args: fun+'('+(', '.join(args))+')',
            'lam': lambda head, body: '(function('+head+'){return '+body+';})',
            'if': lambda p, a, b: '('+p+' ? '+a+' : '+b+')',
            'def': lambda var, code: 'var '+var+' = '+code+';',
            'def_fun': lambda name, head, body: 'function '+name+' ('+head+') {\n    return '+body+';\n}',
            'def_fun_with_code': def_fun_with_code,
            'infix': lambda a, op, b: '('+a+' '+op+' '+b+')'
        },
        'infix': {
            '==', '!=', 'and', 'or', '+', '-', '*', '/', ',', 'is', 'in'  # todo !
        },
        'defs': {
            'len': '_.size'
        }
    }
}

