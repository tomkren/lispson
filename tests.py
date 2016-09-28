import decoder
import targets


def test_decoder(eval_fun, lib, lispson):
    val, code_str, def_codes = eval_fun(lispson, lib, output_code=True)
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
    test(4, ['let', 'x', 2, ["add", "x", "x"]])
    test(4, ['let', 'x', ["add", 1, 1], ["add", "x", "x"]])

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

    test('add')

    test(6, ['let2', 'x, y', ["'", 4, 2], ['x', '+', 'y']])
    test([1, 2, 3], ['mkl', 1, [1, '+', 1], 3])

    test(42, ['ans'])

    print('tested:', num_tested)
    print('not tested:', num_not_tested)
    print('Everything tested was OK :)')


if __name__ == '__main__':
    run_tests(decoder.eval_lispson)
