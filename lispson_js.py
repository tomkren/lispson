import decoder
import targets
import utils
import tests


def mk_js_test(lib, lispson_test, i):
    lispson = lispson_test[1]
    code, defs, natives = decoder.decode(lispson, lib)
    def_codes = sorted(defs.values())
    defs_code = '\n'.join(def_codes)
    def_fun = lib['lang']['target']['def_fun_with_code']
    return def_fun('', '', defs_code, code)


def mk_js_tests(lib, lispson_tests):
    tests_code = 'var tests = [\n'
    for i, lispson_test in enumerate(lispson_tests):
        tests_code += '[' + utils.ordered_dumps(lispson_tests[i][0]) + ', (' + mk_js_test(lib, lispson_test, i) + ')],\n'
    tests_code += '];'
    return tests_code


def lispson_tests_to_file(lib, filename, lispson_tests):
    f = open(filename, 'w')
    result_js = mk_js_tests(lib, lispson_tests)
    print(result_js)
    f.write(result_js)


def js_test():

    lib = {
        'lang': targets.langs['javascript'],
        # 'native': {},
        # 'native': {
        #     'mkv': lambda k, v: {k: v},
        #     'mkp': lambda a, b: [a, b],
        #     'mks': lambda x: ['...', x],
        #     'mkl': lambda *xs: list(xs)
        # },
        'defs': {
            'add': {'x, y': ['x', '+', 'y']},
            'add2': 'add',
            'inc': {'x': ['add', 'x', 1]},
            'eq': {'a, b': ['a', '==', 'b']},
            'even': {'n': ['if', ['eq', 'n', 0], True, ['odd', ['sub', 'n', 1]]]},
            'odd': {'n': ['if', ['eq', 'n', 0], False, ['even', ['sub', 'n', 1]]]},
            'sub': {'a, b': ['a', '-', 'b']},
            'answer': 42,
            'ans': {'': 42},
            'foo': ["'", 'bar'],
            'factorial': {'n': ['if', ['n', '==', 0], 1, ['n', '*', ['factorial', ['n', '-', 1]]]]}
        },
        'macros': {  # todo: aby bylo nepovinný
            'lambda': {"head, body": ["mkv", "head", "body"]},
            'let': {"head, val, body": ["mkp", ["mkv", "head", "body"], 'val']},
            'let2': {"head, val, body": ["mkp", ["mkv", "head", "body"], ['mks_js', 'val']]}
        }
    }

    lispson_tests_to_file(lib, 'js/out.js', tests.tests)


if __name__ == '__main__':
    js_test()
