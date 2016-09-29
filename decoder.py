import json
import tests


def eval_lispson(lispson, lib, output_code=False):
    code, defs = decode(lispson, lib)
    def_codes = defs.values()
    defs_code = '\n'.join(def_codes)

    exec(defs_code, lib['native'])
    val = eval(code, lib['native'])

    if output_code:
        return val, code, def_codes
    else:
        return val


def decode(lispson, lib):
    defs = {}
    code_str = decode_acc(lispson, lib, defs)
    return code_str, defs


def decode_acc(json_o, lib, defs):
    t = type(json_o)
    if t is list:
        return decode_list(json_o, lib, defs)
    elif t is dict:
        return decode_dict(json_o, lib, defs)
    elif t is str:
        handle_def(json_o, lib, defs)
    return str(json_o)


def decode_dict(json_dict, lib, defs):
    decoded_dict = decode_dict_internal(json_dict, lib, defs)
    if decoded_dict['is_lambda']:
        return lib['lang']['target']['lam'](decoded_dict['head'], decoded_dict['body'])
    else:
        return decoded_dict['json_str']


def decode_dict_internal(json_dict, lib, defs):
    keys = list(json_dict)
    if len(keys) == 1:
        head = keys[0]
        body = decode_acc(json_dict[head], lib, defs)
        return {'is_lambda': True, 'head': head, 'body': body}
    else:
        return {'is_lambda': False, 'json_str': json.dumps(json_dict)}


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


def decode_macro(macro_name, args, lib, defs):
    macros = lib['macros']
    macro = macros[macro_name]
    if not callable(macro):
        macro = eval_lispson(macro, lib)
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


if __name__ == '__main__':
    tests.run_tests(eval_lispson)
