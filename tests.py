import json

import decoder
import targets
import metadecoder
import lispson_js


tests = [
    [4, ['add', 2, 2]],
    [4, ["add2", 2, 2]],
    [4, [2, '+', 2]],
    ['Hello world!', ["add", ["'", "Hello "], ["'", "world!"]]],
    ['Hello world!', ["add", "'Hello '", "'world!'"]],
    [5, ["len", ["'", "hello"]]],
    [2, ["len", ["'", ["hello ", "world!"]]]],
    [2, ["len", ["'", "hello ", "world!"]]],
    [0, ["len", ["'"]]],
    [0, ["len", []]],
    [2, ["len", {'foo': 42, 'bar': 23}]],
    [1, ["len", ["'", {'foo': 42}]]],
    [3, [{"x,y": ["add", "x", "y"]}, 1, 2]],
    [3, [["lambda", "x, y", ["add", "x", "y"]], 1, 2]],
    [65, [["lambda", "x,y", ["add", "x", "y"]], 23, 42]],
    [4, ['let', 'x', 2, ["add", "x", "x"]]],
    [4, ['let', 'x', ["add", 1, 1], ["add", "x", "x"]]],
    [2, ['inc', 1]],
    [42, ['if', True, 42, 23]],
    [23, ['if', False, 42, 23]],
    [23, ['if', ['eq', 42, 23], 42, 23]],
    [True, ['even', 0]],
    [False, ['odd', 0]],
    [False, ['even', 1]],
    [True, ['odd', 1]],
    [True, ['even', 42]],
    [False, ['odd', 42]],
    [False, ['even', 23]],
    [True, ['odd', 23]],
    [42, 'answer'],
    ['bar', 'foo'],
    [23, ['sub', 'answer', 19]],
    [120, ['factorial', 5]],
    [42, ['ans']]
]


def test_decoder(eval_fun, lib, lispson):

    if isinstance(lispson, str):
        try:
            lispson = json.loads(lispson)
        except ValueError:
            pass

    val, code_str, def_codes = eval_fun(lispson, lib, True)
    print(lispson)
    if def_codes:
        print(' >> '+'\n    '.join(def_codes))
    print(' ->', code_str)
    print(' =>', val)
    return val


def run_tests(eval_fun):

    lib = {
        'lang': targets.langs['python'],
        'native': {
            'mkv': lambda k, v: {k: v},
            'mkp': lambda a, b: [a, b],
            'mks': lambda x: ['*', x],
            'mkl': lambda *xs: list(xs),
        },
        'defs': {
            'add': {'x, y': ['x', '+', 'y']},
            'add2': 'add',
            'sub': {'a, b': ['a', '-', 'b']},
            'mul': {'a, b': ['a', '*', 'b']},
            'eq': {'a, b': ['a', '==', 'b']},
            'inc': {'x': ['add', 'x', 1]},
            'add_dict': {'a, b': ['dict', 'a', ['**', 'b']]},
            'answer': 42,
            'ans': {'': 42},
            'foo': ["'", 'bar'],
            'even': {'n': ['if', ['eq', 'n', 0], True, ['odd', ['sub', 'n', 1]]]},
            'odd': {'n': ['if', ['eq', 'n', 0], False, ['even', ['sub', 'n', 1]]]},
            'factorial': {'n': ['if', ['n', '==', 0], 1, ['n', '*', ['factorial', ['n', '-', 1]]]]}
        },
        'macros': {
            'lambda': {"head, body": ["mkv", "head", "body"]},
            'let': {"head, val, body": ["mkp", ["mkv", "head", "body"], 'val']},
            'let2': {"head, val, body": ["mkp", ["mkv", "head", "body"], ['mks', 'val']]}
        }
    }

    num_not_tested = 0
    num_tested = 0

    def test(a, b=None):
        should_be, x = (a, b) if (b is not None) else (None, a)
        val = test_decoder(eval_fun, lib, x)
        if should_be is not None:
            nonlocal num_tested
            num_tested += 1
            assert val == should_be, 'Decode test failed!'
            print('OK\n')
        else:
            nonlocal num_not_tested
            num_not_tested += 1
            print()

    for t in tests:
        test(t[0], t[1])

    # todo : make ok in lispson_js and move to tests
    test(6, ['let2', 'x, y', ["'", 4, 2], ['x', '+', 'y']])
    test([1, 2, 3], ['mkl', 1, [1, '+', 1], 3])

    # tests without yet without should_be
    test(['add_dict', ["'", {'foo': 42}], ["'", {'bar': 23}]])
    test(['add_dict', {'foo': 42, "_": 1}, {'bar': 23, "_": 1}])
    test('add')



    print('tested:', num_tested)
    print('not tested:', num_not_tested)
    print('Everything tested was OK :)')

    return num_tested


if __name__ == '__main__':
    total_num_tested = run_tests(decoder.eval_lispson)
    total_num_tested += metadecoder.main()
    lispson_js.js_test()
    print('\nnum_tested from all tests:', total_num_tested)
