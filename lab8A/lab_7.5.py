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
    for i in range(len(lines)):
        lines[i] = lines[i][:lines[i].index(';')] if ';' in lines[i] else lines[i]
    
    tokens = []
    for line in lines:
        i = 0
        while i < len(line):
            if line[i] in ['(', ')']:
                tokens.append(line[i])
            elif line[i] != ' ':
                j = i + 1
                while j < len(line) and line[j] not in ['(', ')', ' ']:
                    j += 1
                tokens.append(line[i:j])
                i = j-1
            i += 1
    return tokens
    
def parse_helper(tokens):
    output = []
    i = 0
    
    while i < len(tokens):
        token = tokens[i]
        if token == ')':
            raise SyntaxError('mismatched parentheses: closed without openning')
        elif token == '(': #is nested sublist
            open_n = 1
            closed_n = 0
            pos = i
            try:
                while closed_n < open_n:
                    pos += 1
                    if tokens[pos] == '(':
                        open_n += 1
                    elif tokens[pos] == ')':
                        closed_n += 1
            except:
                raise SyntaxError('mismatched parentheses: not closed')
            
            output += [parse_helper(tokens[i+1:pos])]
            i = pos
        elif token.isdigit(): #its an int
            output.append(int(token))
        elif token[1:].isdigit() and token[0] == '-': #negative int
            output.append(int(token))
        elif token.replace('.', '').isdigit() and token.count('.') == 1: #float
            output.append(float(token))
        elif token.replace('.', '').replace('-', '').isdigit() and token.count('.') == 1 and token[0] == '-': #negative float
            output.append(float(token))
        else:
            output.append(token)
        
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
            
        
            
            
    


carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
}


def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    raise NotImplementedError


if __name__ == '__main__':
    test = ';add the numbers 2 and 3\n(+ ; this expression\n 2     ; spans multiple\n 3  ; lines\n)'
    test = '(define circle-area (lambda (r) (* 3.14 (* r r))))'
    tokens = tokenize(test)
    print(tokens)
    parsed= parse(tokens)
    print(parsed)