"""6.009 Lab 8A: carlae Interpreter"""

import sys


class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    lines = source.split('\n')
    for i in range(len(lines)): #filter out parts of lines after simicolons
        lines[i] = lines[i][:lines[i].index(';')] if ';' in lines[i] else lines[i]
    #go through and isolate parentheses and words, discarding white space
    tokens = []
    for line in lines:
        i = 0
        while i < len(line):
            if line[i] in ['(', ')']:
                tokens.append(line[i])
            elif line[i] != ' ': #if its a character
                j = i + 1 # collect ensuing characters into string until delimiter reached
                while j < len(line) and line[j] not in ['(', ')', ' ']:
                    j += 1
                tokens.append(line[i:j])
                i = j-1
            i += 1    
    return tokens
    
def parse_helper(tokens):
    '''
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    '''
    output = []
    i = 0
    
    while i < len(tokens): #while there are tokens to parse
        token = tokens[i]
        if token == ')':
            raise SyntaxError('mismatched parentheses: closed without openning')
        elif token == '(': #collect terms in parenthesized expression
            open_n = 1 #number of openned parentheses so far
            closed_n = 0 #number of closed parentheses so far
            pos = i #position traversed to (finding closing bracket)
            try: #find position of corresponding closing bracket
                while closed_n < open_n:
                    pos += 1
                    if tokens[pos] == '(':
                        open_n += 1
                    elif tokens[pos] == ')':
                        closed_n += 1
            except:
                raise SyntaxError('mismatched parentheses: not closed')
            
            output += [parse_helper(tokens[i+1:pos])] #parse the inner expression
            i = pos #skip ahead to end of expression to continue parsing
        elif token.isdigit(): #its an int
            output.append(int(token))
        elif token[1:].isdigit() and token[0] == '-': #negative int
            output.append(int(token))
        elif token.replace('.', '').isdigit() and token.count('.') == 1: #float
            output.append(float(token))
        elif token.replace('.', '').replace('-', '').isdigit() and token.count('.') == 1 and token[0] == '-': #negative float
            output.append(float(token))
        else:
            output.append(token) #string
        
        i+=1
    
    return output


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    return parse_helper(tokens)[0]

def mult(args):
    '''
    product of all args
    
    Args:
        args (list): values to multiply
    
    Returns:
        (int or float) product of args
    '''
    return args[0] if len(args) == 1 else args[0] * mult(args[1:])
    
carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': mult,
    '/': lambda args: mult([args[0]] + list(map(lambda x: 1/x, args[1:])))
}

def evaluate(tree, env = None, evaluated_env = {}):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    env = {'parent': carlae_builtins} if env == None else env
    if type(tree) == list: #handle a complex expression
        evaluated_env[0] = env #this is the environment in which the expression was evaluated    
        #it will keep replacing this until fully recursed and that will be final environment         
        if len(tree) == 0:
            raise EvaluationError('Empty Tree')
        
        if tree[0] == 'define': #defining new function/variable
            assert len(tree) == 3 #structure: 'define' name value
            if type(tree[1]) == str: #normal: (define add2 (lambda (x y) (+ x y)))
                name, val =  tree[1], evaluate(tree[2], env, evaluated_env)
            else: #shortcut: (define (add2 x y) (+ x y))
                name = tree[1][0]
                val = evaluate(['lambda', tree[1][1:], tree[2]], env) #function deffinition or var value
            env[name] = val
            return val
            
        elif tree[0] == 'lambda':
            assert len(tree) == 3 #structure: 'lambda' args expression
            args, exp = tree[1:3] 
            #lambda env is map of args to vals in dictionary with 'parent' as current env, then return lambda of evaluation of expression within this new environment 
            return lambda vals: evaluate(exp, dict(list((args[i], vals[i]) for i in range(max(len(args), len(vals)))) + [('parent', env)]))

        else: #evaluating operation (tree[0]) on args (tree[1:])
            args = list(map(lambda x: evaluate(x, env, evaluated_env), tree[1:])) #evaluate args
            f = evaluate(tree[0], env) #get function object
            try: return f(args)
            except: raise EvaluationError('wrong number of args')
    
    else: #single element evaluation
        if type(tree) in (int, float):
            return tree
        else: #look up element by name
            assert type(tree) == str
            new_env = env
            while True: #recursively look it up in parent env
                if tree in new_env: #found it
                    evaluated_env[len(evaluated_env)] = new_env #this is where we found it
                    return new_env[tree]
                if 'parent' not in new_env: break
                new_env = new_env['parent'] #recurse
            raise EvaluationError('variable not defined') #couldnt find it

def repl():
    '''
    Read, Evaluate, Print Loop for testing 
    tokenize, parse, evaluate on user input
    
    quit on user input 'quit'
    '''    
    env = {'parent': carlae_builtins}
    while True:
        inputt = input('in : ')
        if inputt.lower() == 'quit': return 
        try:
            output = evaluate(parse(tokenize(inputt)), env)
            print('out:', output)
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type.__name__)
        
def result_and_env(tree, env= None):
    '''
    evaluate but also return environment in which it was evaluated
    '''
    evaluated = {} #dictoinary of times we evaluate and where it was evaluated
    output = evaluate(tree, env, evaluated)
    return (output, evaluated[0]) 

if __name__ == '__main__':
#    tests = [[['lambda', ['x'], 'x'], 2, 3]]
#    tests = dict(zip(list(range(len(tests))), tests))  
#    env = None
#    for i in tests:
#        print('----------')
#        print('test', i)
#        test = tests[i]
#        tokens = tokenize(test)
#        print('tokens', tokens)
#        parsed= parse(tokens)
#        print('parsed', parsed)
#        print('passing env:', env)
#        evaluated, env = result_and_env(parsed, env)
#        print('environment', env)
#        print('evaluated', evaluated)
#        print('----------')
#    
#    env = None
#    for i in tests:
#        print('----------')
#        print('test', i)
#        test = tests[i]
#        parsed = test
#        print('parsed', parsed)
#        print('passing env:', env)
#        evaluated, env = result_and_env(parsed, env)
#        print('environment', env)
#        print('evaluated', evaluated)
#        print('----------')
    pass