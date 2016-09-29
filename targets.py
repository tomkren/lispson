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
        }
    }
}
