"""6.009 Lab 8A: carlae Interpreter"""

import sys

class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass

class LinkedList():
    '''
    class for linked lists in LISP framework
    '''
    def __init__(self, elements = []):
        '''
        creates next instance of list and sets current element to elements[0]

        Args:
            elements(list): elements left to add to list
                if None, no element is added and Next doesnt exist
        '''
        assert type(elements) == list
        self.elt = elements[0] if len(elements) > 0 else None #None if empty list
        self.next = LinkedList(elements[1:]) if len(elements) > 1 else None

    def car(self):
        ''' return the current element's value'''
        if self.elt == None:
            raise EvaluationError('tried to extract element of empty list')
        return self.elt

    def cdr(self):
        '''return the linked list starting from the next position'''
        if self.next == None or self.elt == None:
            raise EvaluationError('tried to get next element when there was none')
        return self.next

    def length(self):
        '''recursively get the length of the list'''
        if self.elt == None: return 0
        return 1 if self.next == None else 1 + self.next.length()

    def elt_at_index(self, i):
        '''return element at given index i in list relative to this element'''
        if i == 0: return self.car() #found it
        elif i > 0 and self.next != None: #recurse
            return self.next.elt_at_index(i-1)
        else: raise EvaluationError('index out of range')

    def concat(self, llists):
        '''
        make a copy of this list and return the concatenation
        of it with the remaining lists
        '''
        if len(llists) == 0:
            return self.copy() if self.elt != None else None
        else:
            remaining = llists[0].concat(llists[1:]) #concat the rest
            if self.elt == None: #dont concatenate empty element
                return remaining
            new = self.copy() #copy this node and concatenate it to remaining
            last = new.last_node()
            last.next = remaining
            return new

    def last_node(self):
        '''return last LinkedList object'''
        node = self
        while node.next != None:
            node = node.cdr()
        return node

    def copy(self):
        '''copy self by mapping identity function'''
        return self.mapp(lambda x: x[0])

    def mapp(self, f):
        '''apply map to copy of list and return it'''
        if self.elt == None:
            return LinkedList() #empty list
        else:
            new = LinkedList([f([self.elt])]) #make new element with map applied to this one
            new.next = self.next.mapp(f) if self.next != None else None #recurse
            return new

    def filterr(self, f):
        '''return sublist copy which obbeys condition f, retaining order of original'''
        if self.elt == None:
            return LinkedList()

        remaining = self.next.filterr(f) if self.next != None else None
        if f([self.elt]): #only append to result if it follows rule
            new = LinkedList([self.elt])
            new.next = remaining
            return new
        else: #otherwise only send result for remainder of list
            return remaining

    def reduce(self, f, val):
        '''
        apply reduce successively across list, retaining results.
        ex: (reduce * (list 9 8 7) 1) -> 1 * 9 = 9 -> * 8 = 72 -> * 7 = 504
        '''
        if self.elt == None:
            raise EvaluationError('cant reduce empty list')
        elif self.next is not None: #reduce remainder with updated value
            return self.next.reduce(f, f([val, self.elt]))
        else: #return reduced current val
            return f([val, self.elt])

    def __str__(self):
        '''return string of indices'''
        if self.elt != None:
            return str(self.elt) + ', ' + self.next.__str__() if self.next != None else str(self.elt)
        else:
            return self.next.__str__() if self.next != None else ''


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

def valid_relation(r, args):
    '''
    performs comparison on each pair of consective values,
    checking that condition is satisied
    for #f and #t, replace with False and True

    Args:
        r (str): relation
        args (list): values to compare

    Returns:
        '#t' if true, else '#f'
    '''
    args = list(map(lambda x: str(x), args)) #convert them to strings for eval
    arg2= args[0]
    for i in range(1, len(args)): #for each argument
        arg1, arg2 = arg2, args[i] #shift to next pair of args, checking every contiguous pair
        if not eval(arg1 + r + arg2): #if relation fails, return False
            return False
    return True

#simple builtins
carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': mult,
    '/': lambda args: mult([args[0]] + list(map(lambda x: 1/x, args[1:]))),
    '=?': lambda args: valid_relation('==', args),
    '<': lambda args: valid_relation('<', args),
    '<=': lambda args: valid_relation('<=', args),
    '>': lambda args: valid_relation('>', args),
    '>=': lambda args: valid_relation('>=', args),
    '#f': False,
    '#t': True,
    'not': lambda x: not(x[0]),
    'list': lambda args: LinkedList(args),
    'car': lambda args: args[0].car(),
    'cdr': lambda args: args[0].cdr(),
    'length': lambda args: args[0].length(),
    'elt-at-index': lambda args: args[0].elt_at_index(args[1]),
    'concat': lambda args: LinkedList() if len(args) == 0 else args[0].concat(args[1:]),
    'map': lambda args: args[1].mapp(args[0]),
    'filter': lambda args: args[1].filterr(args[0]),
    'reduce': lambda args: args[1].reduce(args[0], args[2]),
    'begin': lambda args: args[-1]
}

def evaluate(tree, env = None, evaluated_env = {}):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    env = env if env != None else {';parent': carlae_builtins}
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
                val = evaluate(['lambda', tree[1][1:], tree[2]], env, evaluated_env) #function deffinition or var value
            env[name] = val
            return val

        elif tree[0] == 'lambda': #creating a lambda function: 'lambda' args expression
            args, exp = tree[1:3]
            #lambda env is map of args to vals in dictionary with 'parent' as current env, then return lambda of evaluation of expression within this new environment
            return lambda vals: evaluate(exp, dict(list((args[i], vals[i]) for i in range(max(len(args), len(vals)))) + [(';parent', env)]), evaluated_env)

        elif tree[0] == 'if': #conditional
            cond, true_exp, false_exp = tree[1:] #if COND TRUE_EXP FALSE_EXP
            if evaluate(cond, env, evaluated_env):
                return evaluate(true_exp, env, evaluated_env)
            else:
                return evaluate(false_exp, env, evaluated_env)

        elif tree[0] == 'and': #and opperator, all expressions must be true
            for arg in tree[1:]:
                if not evaluate(arg, env, evaluated_env): #short circuit
                    return False
            return True

        elif tree[0] == 'or': #at least one expression is true
            for arg in tree[1:]:
                if evaluate(arg, env, evaluated_env): #short circuit
                    return True
            return False

        elif tree[0] == 'let':  #(let ((VAR1 VAL1) (VAR2 VAL2) (VAR3 VAL3) ...) BODY)
            new_env = {';parent': env} #make a new environment to hold local variables
            args = list(map(lambda x: evaluate(['define', x[0], x[1]], new_env), tree[1])) #define vars in new_env
            return evaluate(tree[2], new_env) #return locally evaluated BODY (not passed evaluated_env)

        elif tree[0] == 'set!': #set! VAR EXPR
            var, val = tree[1], evaluate(tree[2], env, evaluated_env)
            new_env = env
            while True: #recursively look it up in parent env
                if var in new_env:
                    new_env[var] = val
                    break
                if ';parent' not in new_env:
                    raise EvaluationError('variable ' + str(var) +' not defined') #couldnt find it
                new_env = new_env[';parent'] #recurse
            return val

        else: #evaluating operation (tree[0]) on args (tree[1:])
            args = list(map(lambda x: evaluate(x, env, evaluated_env), tree[1:])) #evaluate args
            f = evaluate(tree[0], env, evaluated_env) #get function object
            try: return f(args)
            except: raise EvaluationError('args:', args, 'wrong number of args for function', f)

    else: #single element evaluation
        if type(tree) in (int, float, bool):
            return tree
        else: #look up element by name
            assert type(tree) == str
            new_env = env
            while True: #recursively look it up in parent env
                if tree in new_env: #found it
                    evaluated_env[len(evaluated_env)] = new_env #this is where we found it
                    return new_env[tree]
                if ';parent' not in new_env:
                    break
                new_env = new_env[';parent'] #recurse
            raise EvaluationError('variable ' + str(tree) +' not defined') #couldnt find it

def repl(env = None):
    '''
    Read, Evaluate, Print Loop for testing
    tokenize, parse, evaluate on user input

    quit on user input 'quit'
    '''
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
    evaluated = {} #dictionary of times we evaluate and where it was evaluated
    output = evaluate(tree, env, evaluated)
    return (output, evaluated[0]) #the first evaluation

def evaluate_file(filename, env = None):
    '''
    reads in file as string and tokenizes, parses, and evaluates it, returning result

    Args:
        filename (str): filename
        env (dict): environment in which to evaluate expression

    Returns:
        evaluated file expression
    '''
    env = env if env != None else {';parent': carlae_builtins}
    lines = []
    with open(filename) as f:
        for line in f:
            lines.append(line)
    return evaluate(parse(tokenize(''.join(lines))), env)

if __name__ == '__main__':
    env = None
    for filename in sys.argv[1:]:
        result = evaluate_file(filename, env)
    repl(env)


#    test = False
#    if test:
#        tests = [['concat', ['list', 9, 8, 7]], ['concat', ['list', 1], ['list', 2, 3, 4, 5, 9, 10]], ['concat', ['list', 1], ['list', 2], ['list', 3]], ['concat', ['concat'], ['list', 1]], ['concat', ['list', 1], ['concat']], ['define', 'x', ['list', 1]], ['concat', 'x', 'x', 'x'], 'x']
#        tests = dict(zip(list(range(len(tests))), tests))
#        env = None
#    #    for i in tests:
#    #        print('----------')
#    #        print('test', i)
#    #        test = tests[i]
#    #        tokens = tokenize(test)
#    #        print('tokens', tokens)
#    #        parsed= parse(tokens)
#    #        print('parsed', parsed)
#    #        print('passing env:', env)
#    #        evaluated, env = result_and_env(parsed, env)
#    #        print('environment', env)
#    #        print('evaluated', evaluated)
#    #        print('----------')
#    #
#        for i in tests:
#            print('----------')
#            print('test', i)
#            test = tests[i]
#            parsed = test
#            print('parsed', parsed)
#            print('passing env:', env)
#            evaluated, env = result_and_env(parsed, env)
#            print('environment', env)
#            print('evaluated', evaluated)
#            print('----------')
#        pass
