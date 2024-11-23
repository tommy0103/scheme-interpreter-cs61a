import sys

from pair import *
from scheme_utils import *
from ucb import main, trace
from scheme_builtins import *

import scheme_forms

##############
# Eval/Apply #
##############

def lookup_procedure(name, env):
    eval_procedure = None
    for procedure in BUILTINS:
        if procedure[0] == name:
            eval_procedure = BuiltinProcedure(procedure[1], expect_env=procedure[3])
            break
    # if name == 'eval':
    #     eval_procedure = BuiltinProcedure(scheme_eval, expect_env=True)
    if eval_procedure == None:
        try:
            eval_procedure = env.lookup(name)
            if(isinstance(eval_procedure, (LambdaProcedure, MuProcedure))):
                return eval_procedure
        except SchemeError:
            raise SchemeError("Invalid operator: {0}".format(name))
    return eval_procedure

#  ((lambda (x) (list x (list (quote quote) x))) (quote (lambda (x) (list x (list (quote quote) x)))))
Pair(Pair(Pair('f', Pair(Pair('+', Pair('x', Pair(1, nil))), nil)), nil), Pair(Pair('+', Pair('x', Pair(2, nil))), nil))

def scheme_eval(expr, env, _=None):  # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # Evaluate atoms
    if scheme_symbolp(expr):
        return env.lookup(expr)
    elif self_evaluating(expr):
        return expr

    # ((lambda (x) (list x (list x))) ((lambda (x) (list x (list x)))))
    # Pair(Pair('lambda', 
    #           Pair(Pair('x', nil), 
    #                Pair(Pair('list', Pair('x', nil)), nil))), Pair(Pair('quote', Pair('x', nil)), nil))
    # All non-atomic expressions are lists (combinations)
    if not scheme_listp(expr):
        raise SchemeError('malformed list: {0}'.format(repl_str(expr)))
    first, rest = expr.first, expr.rest
    def scheme_eval_closure(expr):
        return scheme_eval(expr, env)
    if scheme_symbolp(first) and first in scheme_forms.SPECIAL_FORMS:
        return scheme_forms.SPECIAL_FORMS[first](rest, env)
    elif isinstance(first, Pair) and scheme_symbolp(first.first) and first.first in scheme_forms.SPECIAL_FORMS:
        result = scheme_forms.SPECIAL_FORMS[first.first](first.rest, env) # I don't know why I do this.
        if(isinstance(result, str)): # I don't know whether this will exist
            eval_procedure = lookup_procedure(result, env)
            return scheme_apply(eval_procedure, rest.map(scheme_eval_closure), env)
        if(isinstance(result, Procedure)):
            return scheme_apply(result, rest.map(scheme_eval_closure), env)
        raise SchemeError("Something wrong with the Special Form.")
    else:
        # BEGIN PROBLEM 3
        # "*** YOUR CODE HERE ***"
        eval_procedure = None
        if isinstance(first, Pair):
            try:
                # eval_procedure = lookup_procedure(first.first, env)
                # first = scheme_apply(eval_procedure, first.rest.map(scheme_eval_closure), env)
                while first.rest == nil:
                    first = first.first
                eval_procedure = lookup_procedure(first.first, env)
                first = scheme_apply(eval_procedure, first.rest.map(scheme_eval_closure), env)
            except TypeError:
                raise SchemeError("Pair is not available. {0}\n{1}\n{2}\n{3}".format(first.first, first, rest, expr))
        # print(first, type(first))
        if isinstance(first, str):
            if first == 'eval':
                # print(first)
                return scheme_eval(scheme_eval(rest.first, env), env)
            eval_procedure = lookup_procedure(first, env)
        else:
            eval_procedure = first
        # eval_procedure = lookup_procedure(first)
        return scheme_apply(eval_procedure, rest.map(scheme_eval_closure), env)
        # END PROBLEM 3

def eval_all(expressions, env):
    """Evaluate each expression in the Scheme list EXPRESSIONS in
    Frame ENV (the current environment) and return the value of the last.

    >>> eval_all(read_line("(1)"), create_global_frame())
    1
    >>> eval_all(read_line("(1 2)"), create_global_frame())
    2
    >>> x = eval_all(read_line("((print 1) 2)"), create_global_frame())
    1
    >>> x
    2
    >>> eval_all(read_line("((define x 2) x)"), create_global_frame())
    2
    """
    # BEGIN PROBLEM 6
    # return scheme_eval(expressions.first, env)  # replace this with lines of your own code
    # scheme_eval()
    # Pair('begin', Pair(Pair('print', Pair(3, nil)), Pair(Pair('quote', Pair(Pair('+', Pair(2, Pair(3, nil))), nil)), nil)))
    result = None
    expr = expressions
    while(expr != nil):
        result = scheme_eval(expr.first, env)
        expr = expr.rest
    return result
    # END PROBLEM 6

def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    validate_procedure(procedure)
    if isinstance(procedure, BuiltinProcedure):
        # BEGIN PROBLEM 2
        "*** YOUR CODE HERE ***"
        args_list = []
        while isinstance(args, Pair):
            args_list.append(args.first)
            args = args.rest
        if procedure.expect_env == True:
            args_list.append(env)
        try:
            result = procedure.py_func(*args_list)
            return result
        except TypeError:
            raise SchemeError('BuiltinProcedure: Incorrect number of arguments')
        # END PROBLEM 2
    elif isinstance(procedure, LambdaProcedure):
        # BEGIN PROBLEM 9
        # "*** YOUR CODE HERE ***"
        if(len(procedure.formals) != len(args)):
            raise SchemeError('LambdaProcedure: Incorrect number of arguments')
        # print("Lambda:", procedure.formals, args, procedure.body)
        if(procedure.formals == nil):
            child_env = procedure.env.make_child_frame(nil, nil)
            if(len(args) != 0):
                result = eval_all(procedure.body, child_env)
                # print(result, args)
                return scheme_eval(Pair(result, args), child_env)
            
        else:
            child_env = procedure.env.make_child_frame(procedure.formals, args)
        return eval_all(procedure.body, child_env)
        # END PROBLEM 9
    elif isinstance(procedure, MuProcedure):
        # BEGIN PROBLEM 11
        "*** YOUR CODE HERE ***"
        # if(len(procedure.formals) != len(args)):
        #     raise SchemeError('MuProcedure: Incorrect number of arguments\n{0}\n{1}'.format(procedure.formals, args))
        # print("Mu:", procedure.formals, args, procedure.body)
        if(procedure.formals == nil):
            child_env = env.make_child_frame(nil, nil)
            if(len(args) != 0):
                result = eval_all(procedure.body, child_env)
                # print(result, args)
                return scheme_eval(Pair(result, args), child_env)
        else:
            child_env = env.make_child_frame(procedure.formals, args)
        return eval_all(procedure.body, child_env)
        # END PROBLEM 11
    else:
        assert False, "Unexpected procedure: {}".format(procedure)
# Pair(Pair('lambda', Pair(Pair('y', nil), Pair(Pair('+', Pair(5, Pair('y', nil))), nil))), Pair(5, nil))
# Pair(Pair('lambda', Pair(Pair('y', nil), Pair(Pair('+', Pair(5, Pair('y', nil))), nil))), Pair(5, nil))
# Pair('lambda', Pair(Pair('y', nil), Pair(Pair('+', Pair(5, Pair('y', nil))), nil)))
##################
# Tail Recursion #
##################

class Unevaluated:
    """An expression and an environment in which it is to be evaluated."""

    def __init__(self, expr, env):
        """Expression EXPR to be evaluated in Frame ENV."""
        self.expr = expr
        self.env = env


def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not an Unevaluated."""
    validate_procedure(procedure)
    val = scheme_apply(procedure, args, env)
    if isinstance(val, Unevaluated):
        return scheme_eval(val.expr, val.env)
    else:
        return val


def optimize_tail_calls(unoptimized_scheme_eval):
    """Return a properly tail recursive version of an eval function."""
    def optimized_eval(expr, env, tail=False):
        """Evaluate Scheme expression EXPR in Frame ENV. If TAIL,
        return an Unevaluated containing an expression for further evaluation.
        """
        if tail and not scheme_symbolp(expr) and not self_evaluating(expr):
            return Unevaluated(expr, env)

        result = Unevaluated(expr, env)
        # BEGIN PROBLEM EC
        "*** YOUR CODE HERE ***"
        # END PROBLEM EC
    return optimized_eval


################################################################
# Uncomment the following line to apply tail call optimization #
################################################################
# scheme_eval = optimize_tail_calls(scheme_eval)
