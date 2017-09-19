import sys
import inspect
import itertools

def update():
    import requests
    with open('truth.py', 'wb') as f:
        f.write(requests.get('https://raw.githubusercontent.com/Ivoah/truth/master/truth.py').content)

operators = {
    '!': lambda a: not a,
    '&': lambda a, b: a and b,
    '|': lambda a, b: a or b,
    '^': lambda a, b: a ^ b,
    '>': lambda a, b: b if a else True,
    '=': lambda a, b: a == b
}

precedence = ['!', '&', '|', '^', '>', '=', '(', ')']

def tokenize(string):
    return list(string)

def infix_to_postfix(tokens):
    out_stack = []
    op_stack = []

    for i, c in enumerate(tokens):
        if c in operators:
            while len(op_stack) > 0 and precedence.index(op_stack[-1]) < precedence.index(c):
                out_stack.append(op_stack.pop())
            op_stack.append(c)
        elif c == '(':
            op_stack.append(c)
        elif c == ')':
            while op_stack[-1] != '(':
                out_stack.append(op_stack.pop())
            op_stack.pop()
        else:
            out_stack.append(c)
    while len(op_stack) > 0:
        out_stack.append(op_stack.pop())

    return out_stack

def postfix_to_ast(postfix):
    args = []

    for c in postfix:
        if c in operators:
            num_p = len(inspect.signature(operators[c]).parameters)
            args.append({'op': c, 'args': list(reversed([args.pop() for i in range(num_p)]))})
        else:
            args.append(c)

    return args[0]

def ast_to_infix(ast):
    if type(ast) == str:
        return ast
    else:
        args = [f'({ast_to_infix(arg)})' if type(arg) == dict and precedence.index(arg['op']) > precedence.index(ast['op']) else ast_to_infix(arg) for arg in ast['args']]
        if len(args) == 1:
            return f"{ast['op']}{args[0]}"
        else:
            return f"{args[0]}{ast['op']}{args[1]}"

def evaluate(ast, vars):
    if type(ast) == str:
        return vars[ast]
    else:
        return operators[ast['op']](*[evaluate(arg, vars) for arg in ast['args']])

def get_parts(ast):
    vars = []
    parts = []

    def recur(ast):
        if ast not in parts:
            if type(ast) == str and ast not in vars:
                vars.append(ast)
            elif type(ast) == dict and ast not in parts:
                for arg in ast['args']:
                    recur(arg)
                parts.append(ast)

    recur(ast)
    return vars, parts

def print_table(table):
    print('┏━' + '━┯━'.join('━'*len(row) for row in table[0]) + '━┓')
    print('┃ ' + ' │ '.join(table[0]) + ' ┃')
    print('┣━' + '━┿━'.join('━'*len(row) for row in table[0]) + '━┫')
    for row in table[1:]:
        print('┃ ' + ' │ '.join(f'{col:^{len(table[0][i])}}' for i, col in enumerate(row)) + ' ┃')
    print('┗━' + '━┷━'.join('━'*len(row) for row in table[0]) + '━┛')

if __name__ == '__main__':
    vars = []
    parts = []

    for expression in sys.argv[1:] if len(sys.argv) > 1 else (lambda x: input().split())(print('Enter expression(s): ', end = '')):
        tokens = tokenize(expression)
        postfix = infix_to_postfix(tokens)
        ast = postfix_to_ast(postfix)
        v, p = get_parts(ast)
        vars.extend(var for var in v if var not in vars)
        parts.extend(part for part in p if part not in parts)

    pparts = list(map(ast_to_infix, parts))
    table = [vars + pparts]

    for prod in itertools.product([True, False], repeat = len(vars)):
        table.append(['T' if evaluate(expr, {arg: prod[i] for i, arg in enumerate(vars)}) else 'F' for expr in vars + parts])

    print_table(table)
