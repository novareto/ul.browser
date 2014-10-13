# -*- coding: utf-8 -*-

def eval_loader(expr):
    """load  a class / function

    :param expr: dotted name of the module ':' name of the class / function
    :raises RuntimeError: if expr is not a valid expression
    :raises ImportError: if module or object not found
    """
    modname, elt = expr.split(':', 1)
    if modname:
        try:
            module = __import__(modname, {}, {}, ['*'])
            val = getattr(module, elt, marker)
            if val is marker:
                raise ImportError('')
            return val
        except ImportError:
            raise ImportError(
                "Bad specification %s: no item name %s in %s." %
                (expr, elt, modname))
    else:
        raise RuntimeError("Bad specification %s: no module name." % expr)
