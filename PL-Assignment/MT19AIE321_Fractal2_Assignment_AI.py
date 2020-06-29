# Author : Suman Debnath
# Email : debnath.1@iitj.ac.in
# Roll No : MT19AIE321
# M.Tech-AI(2020)
# Date : 14th May 2020

#######################################
#  Programming assignment (Fractal-2) #
#######################################

### Importing the Modules 

import heapq
import itertools
import random
import collections

import fileinput

class Expr:
    
    def __init__(self, op, *args):
        self.op = str(op)
        self.args = args

    def __invert__(self):
        return Expr('~', self)

    def __and__(self, rhs):
        return Expr('&', self, rhs)

    def __rshift__(self, rhs):
        return Expr('>>', self, rhs)

    def __lshift__(self, rhs):
        return Expr('<<', self, rhs)

    def __matmul__(self, rhs):
        return Expr('@', self, rhs)

    def __or__(self, rhs):
        if isinstance(rhs, Expression):
            return Expr('|', self, rhs)
        else:
            return PartialExpr(rhs, self)

    def __rand__(self, lhs):
        return Expr('&', lhs, self)

    def __ror__(self, lhs):
        return Expr('|', lhs, self)

    def __rrshift__(self, lhs):
        return Expr('>>', lhs, self)

    def __rlshift__(self, lhs):
        return Expr('<<', lhs, self)

    def __call__(self, *args):
        if self.args:
            raise ValueError('Can only do a call for a Symbol, not an Expr')
        else:
            return Expr(self.op, *args)

    # Equality and repr
    def __eq__(self, other):
        return isinstance(other, Expr) and self.op == other.op and self.args == other.args

    def __lt__(self, other):
        return isinstance(other, Expr) and str(self) < str(other)

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)

    def __repr__(self):
        op = self.op
        args = [str(arg) for arg in self.args]
        if op.isidentifier():  # f(x) or f(x, y)
            return '{}({})'.format(op, ', '.join(args)) if args else op
        elif len(args) == 1:  # -x or -(x + 1)
            return op + args[0]
        else:  # (x - y)
            opp = (' ' + op + ' ')
            return '(' + opp.join(args) + ')'

Number = (int, float, complex)
Expression = (Expr, Number)


def Symbol(name):
    return Expr(name)


def symbols(names):
    return tuple(Symbol(name) for name in names.replace(',', ' ').split())


def subexpressions(x):
    yield x
    if isinstance(x, Expr):
        for arg in x.args:
            yield from subexpressions(arg)


def arity(expression):
    if isinstance(expression, Expr):
        return len(expression.args)
    else:  # expression is a number
        return 0
    
def expr(x):

    return eval(expr_handle_infix_ops(x), defaultkeydict(Symbol)) if isinstance(x, str) else x

infix_ops = '==> <== <=>'.split()

def expr_handle_infix_ops(x):

    for op in infix_ops:
        x = x.replace(op, '|' + repr(op) + '|')
    return x


class defaultkeydict(collections.defaultdict):

    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result

def find_if(predicate, seq):

    for x in seq:
        if predicate(x): return x
    return None

def extend(s, var, val):
    try:  # Python 3.5 and later
        return eval('{**s, var: val}')
    except SyntaxError:  # Python 3.4
        s2 = s.copy()
        s2[var] = val
        return s2
    
def dissociate(op, args):

    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result

def conjuncts(s):

    return dissociate('&', [s])

def to_cnf(s):

    s = expr(s)
    if isinstance(s, str):
        s = expr(s)
    s = eliminate_implications(s)  # Steps 1, 2 from p. 253
    s = move_not_inwards(s)  # Step 3
    return distribute_and_over_or(s)  # Step 4


def eliminate_implications(s):
    #s = expr(s)
    if not s.args or is_symbol(s.op):
        return s  # Atoms are unchanged.
    args = list(map(eliminate_implications, s.args))
    a, b = args[0], args[-1]
    if s.op == '>>':
        return b | ~a
    elif s.op == '<<':
        return a | ~b
    elif s.op == '<=>':
        return (a | ~b) & (b | ~a)
    elif s.op == '^':
        assert len(args) == 2  # TODO: relax this restriction
        return (a & ~b) | (~a & b)
    else:
        assert s.op in ('&', '|', '~')
        return Expr(s.op, *args)


def move_not_inwards(s):

    s = expr(s)
    if s.op == '~':
        def NOT(b):
            return move_not_inwards(~b)

        a = s.args[0]
        if a.op == '~':
            return move_not_inwards(a.args[0])  # ~~A ==> A
        if a.op == '&':
            return associate('|', list(map(NOT, a.args)))
        if a.op == '|':
            return associate('&', list(map(NOT, a.args)))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return Expr(s.op, *list(map(move_not_inwards, s.args)))


def distribute_and_over_or(s):

    if s.op == '|':
        s = associate('|', s.args)
        if s.op != '|':
            return distribute_and_over_or(s)
        if len(s.args) == 0:
            return FALSE
        if len(s.args) == 1:
            return distribute_and_over_or(s.args[0])
        conj = find_if((lambda d: d.op == '&'), s.args)
        if not conj:
            return s
        others = [a for a in s.args if a is not conj]
        rest = associate('|', others)
        return associate('&', [distribute_and_over_or(c|rest)
                               for c in conj.args])
    elif s.op == '&':
        return associate('&', map(distribute_and_over_or, s.args))
    else:
        return s


def associate(op, args):

    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)

_op_identity = {'&': True, '|': False, '+': 0, '*': 1}

def dissociate(op, args):

    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result


def conjuncts(s):

    return dissociate('&', [s])

def disjuncts(s):

    return dissociate('|', [s])

def first(iterable, default=None):
    return next(iter(iterable), default)

class KB:

    def __init__(self, sentence=None):
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        raise NotImplementedError

    def ask(self, query):
        return first(self.ask_generator(query), default=False)

    def ask_generator(self, query):
        raise NotImplementedError

    def retract(self, sentence):
        raise NotImplementedError

class PropKB(KB):

    def __init__(self, sentence=None):
        self.clauses = []
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        self.clauses.extend(conjuncts(to_cnf(sentence)))

    def ask_generator(self, query):
        if tt_entails(Expr('&', *self.clauses), query):
            yield {}

    def retract(self, sentence):
        for c in conjuncts(to_cnf(sentence)):
            if c in self.clauses:
                self.clauses.remove(c)


def KB_AgentProgram(KB):
    steps = itertools.count()

    def program(percept):
        t = steps.next()
        KB.tell(make_percept_sentence(percept, t))
        action = KB.ask(make_action_query(t))
        KB.tell(make_action_sentence(action, t))
        return action

    def make_percept_sentence(self, percept, t):
        return Expr("Percept")(percept, t)

    def make_action_query(self, t):
        return expr("ShouldDo(action, %d)" % t)

    def make_action_sentence(self, action, t):
        return Expr("Did")(action[expr('action')], t)

    return program


def is_symbol(s):

    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):

    return is_symbol(s) and s[0].islower()


def is_prop_symbol(s):

    return is_symbol(s) and s[0].isupper()


def variables(s):

    return {x for x in subexpressions(s) if is_variable(x)}

def is_variable(x):
    return isinstance(x, Expr) and not x.args and is_var_symbol(x.op)


def is_definite_clause(s):

    if is_symbol(s.op):
        return True
    elif s.op == '==>':
        antecedent, consequent = s.args
        return is_symbol(consequent.op) and all(is_symbol(arg.op) for arg in conjuncts(antecedent))
    else:
        return False


def parse_definite_clause(s):
    assert is_definite_clause(s)
    if is_symbol(s.op):
        return [], s
    else:
        antecedent, consequent = s.args
        return conjuncts(antecedent), consequent


# Useful constant Exprs used in examples and code:
TRUE, FALSE, ZERO, ONE, TWO = map(Expr, ['TRUE', 'FALSE', 0, 1, 2])
A, B, C, D, E, F, G, P, Q, a, x, y, z, u = map(Expr, 'ABCDEFGPQaxyzu')

def tt_entails(kb, alpha):

    assert not variables(alpha)
    return tt_check_all(kb, alpha, prop_symbols(kb & alpha), {})

def tt_check_all(kb, alpha, symbols, model):
    if not symbols:
        if pl_true(kb, model):
            result = pl_true(alpha, model)
            assert result in (True, False)
            return result
        else:
            return True
    else:
        P, rest = symbols[0], symbols[1:]
        return (tt_check_all(kb, alpha, rest, extend(model, P, True)) and
                tt_check_all(kb, alpha, rest, extend(model, P, False)))

def prop_symbols(x):
    if not isinstance(x, Expr):
        return []
    elif is_prop_symbol(x.op):
        return [x]
    else:
        return list(set(symbol for arg in x.args
                        for symbol in prop_symbols(arg)))

def tt_true(alpha):

    return tt_entails(TRUE, expr(alpha))

def pl_true(exp, model={}):

    op, args = exp.op, exp.args
    if exp == TRUE:
        return True
    elif exp == FALSE:
        return False
    elif is_prop_symbol(op):
        return model.get(exp)
    elif op == '~':
        p = pl_true(args[0], model)
        if p is None: return None
        else: return not p
    elif op == '|':
        result = False
        for arg in args:
            p = pl_true(arg, model)
            if p is True: return True
            if p is None: result = None
        return result
    elif op == '&':
        result = True
        for arg in args:
            p = pl_true(arg, model)
            if p is False: return False
            if p is None: result = None
        return result
    p, q = args
    if op == '>>':
        return pl_true(~p | q, model)
    elif op == '<<':
        return pl_true(p | ~q, model)
    pt = pl_true(p, model)
    if pt is None: return None
    qt = pl_true(q, model)
    if qt is None: return None
    if op == '<=>':
        return pt == qt
    elif op == '^':
        return pt != qt
    else:
        raise ValueError('Illegal operator in logic expression' + str(exp))

        
def main():

    # ### Raw Data from STDIN/File  - FOR LAPTOP
    # data = [] 
    # with open("input.txt") as f:
    #     data = f.readlines()

    ### Raw Data from STDIN/File - FOR Hacker Rank
    data = []
    for line in fileinput.input():
        data.append(line)

    data = [ d.rstrip() for d in data]
    con_formulae = data.pop() # Last element 

    no_formulae, mode = data.pop(0).split()
    no_formulae = int(no_formulae)
    mode = int(mode)

    knowledgebase = PropKB()

    for formulae in data:
        statement = formulae.replace(">",">>").replace("!","~").replace("=", "<=>")
        knowledgebase.tell(statement)

    conclusion = knowledgebase.ask(expr(con_formulae.replace(">",">>").replace("!","~").replace("=", "<=>")))

    if conclusion == False:
        print(0)
    else:
        print(1)

main()
