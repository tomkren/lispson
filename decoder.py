import json
import tests


def eval_lispson(lispson, lib, output_code=False, output_all=False):
    code, defs, natives = decode(lispson, lib)
    def_codes = defs.values()
    defs_code = '\n'.join(def_codes)

    exec(defs_code, lib['native'])
    val = eval(code, lib['native'])

    if output_all:
        return val, code, def_codes, natives
    if output_code:
        return val, code, def_codes
    else:
        return val, natives  # todo HAX aby se nerozbil metadecoder


def decode(lispson, lib):
    acc = {
        'vars': set(),
        'natives': set(),
        'defs': {}
    }
    code_str = decode_acc(lispson, lib, acc)
    # print('natives (for ', lispson, '): ', acc['natives'])  # todo lépe
    return code_str, acc['defs'], acc['natives']


def decode_acc(json_o, lib, acc):
    t = type(json_o)
    if t is list:
        return decode_list(json_o, lib, acc)
    elif t is dict:
        return decode_dict(json_o, lib, acc)
    elif t is str:
        handle_def(json_o, lib, acc)
    return str(json_o)


def decode_dict(json_dict, lib, acc):
    decoded_dict = decode_dict_internal(json_dict, lib, acc)
    if decoded_dict['is_lambda']:
        return lib['lang']['target']['lam'](decoded_dict['head'], decoded_dict['body'])
    else:
        return decoded_dict['json_str']


def decode_dict_internal(json_dict, lib, acc):
    keys = list(json_dict)
    if len(keys) == 1:
        head = keys[0]
        head_vars = {var.strip() for var in head.split(',')}
        old_vars = acc['vars']
        acc['vars'] = old_vars.union(head_vars)
        body = decode_acc(json_dict[head], lib, acc)
        acc['vars'] = old_vars
        return {'is_lambda': True, 'head': head, 'body': body}
    else:
        return {'is_lambda': False, 'json_str': json.dumps(json_dict)}


def decode_list(json_list, lib, acc):
    if not json_list:  # Is empty ?
        return '[]'
    if is_infix(json_list, lib):
        return decode_infix(lib, acc, *json_list)
    fun = json_list[0]
    args = json_list[1:]

    fun_is_str = isinstance(fun, str)

    if fun_is_str:
        if fun == "'":  # Is the function "the quote" ?
            return decode_quote(args)
        if fun in lib['macros']:  # Is the function a macro ?
            return decode_macro(fun, args, lib, acc)
        if fun == "if":
            return decode_if(args, lib, acc)
        handle_def(fun, lib, acc)  # Handles definitions if needed.

    decoded_fun = fun if fun_is_str else decode_acc(fun, lib, acc)
    return lib['lang']['target']['app'](decoded_fun, decode_args(args, lib, acc))


def decode_args(args, lib, acc):
    return [decode_acc(o, lib, acc) for o in args]


def is_infix(json_list, lib):
    if len(json_list) == 3:
        op = json_list[1]
        return isinstance(op, str) and op in lib['lang']['infix']
    else:
        return False


def decode_infix(lib, acc, a, op, b):
    decoded_a = decode_acc(a, lib, acc)
    decoded_b = decode_acc(b, lib, acc)
    acc['natives'].add(('op', op))  # todo better handling
    return lib['lang']['target']['infix'](decoded_a, op, decoded_b)


def decode_quote(args):
    return json.dumps(args[0] if len(args) == 1 else args)


def decode_macro(macro_name, args, lib, acc):
    macros = lib['macros']
    macro = macros[macro_name]
    if not callable(macro):
        macro, macro_natives = eval_lispson(macro, lib, False)
        macros[macro_name] = macro  # Non-pure optimization saving the compiled macro (can be omitted)
        acc['natives'].update(macro_natives)
    return decode_acc(macro(*args), lib, acc)


# If needs a special treatment because of if's laziness
# (we must not evaluate both branches, so it cannot be a Python function)
def decode_if(args, lib, acc):
    if len(args) == 3:
        decoded_args = decode_args(args, lib, acc)
        return lib['lang']['target']['if'](*decoded_args)
    else:
        raise ValueError('if must have 3 args', len(args))


def handle_def(sym, lib, acc):
    defs = acc['defs']
    lib_defs = lib['defs']
    if sym in lib_defs:  # and sym not in defs:
        if sym not in defs:
            sym_def = lib_defs[sym]
            if not isinstance(sym_def, str):
                defs[sym] = None  # So it won't recurse forever ..

                if isinstance(sym_def, dict):
                    decoded_dict = decode_dict_internal(sym_def, lib, acc)
                    if decoded_dict['is_lambda']:
                        sym_def = lib['lang']['target']['def_fun'](sym, decoded_dict['head'], decoded_dict['body'])
                    else:
                        sym_def = lib['lang']['target']['def'](sym, decoded_dict['json_str'])
                else:
                    body = decode_acc(sym_def, lib, acc)
                    sym_def = lib['lang']['target']['def'](sym, body)

            defs[sym] = sym_def
    elif sym not in acc['vars']:
        acc['natives'].add(sym)


if __name__ == '__main__':
    tests.run_tests(eval_lispson)
