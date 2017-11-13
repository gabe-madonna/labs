"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def assign_val(clauses, var, val, indices):
    '''
    reduces the cnf by reducing the indicies in accordance with logic rules
    
    Args:
        clauses (list): the cnf
        var (string): the variable
        val (bool): the boolean value being tested
        indices (dict of sets): set of literal indices for each clause
    Returns:
        None if any of the clauses evaluate to false, otherwise
        removed (dict of sets): the indiced which were removed from indices
    '''
    to_rem = {} #to be removed
    valid_clauses = set() #clauses which eval to true
    for clause in indices:
        for literal in indices[clause]: #for each literal
            if clauses[clause][literal] == (var, val): #if its a match, the clause is valid
                to_rem[clause] = indices[clause].copy() #remove all members of the claise
                valid_clauses.add(clause) #signal that these dont indicate a failure
                break
            elif clauses[clause][literal] == (var, not(val)): #mismatch -> remove literal from clause
                to_rem.setdefault(clause, set()).add(literal) #remove it 
     
    for clause in to_rem: #check if any clauses were emptied (not by validity)
        if len(indices[clause]) == len(to_rem[clause]) and clause not in valid_clauses:
            return None
           
    for clause in to_rem: #remove indices marked earlier
        indices[clause].difference_update(to_rem[clause])
    return to_rem  

def test_var(clauses, var, val, indices):
    '''
    tests a variable assignment
    
    Args:
        clauses (list): cnf
        var (string): the variable
        val (bool): value being tested
        indices (dict of sets): viable indices
    Returns:
        None if failure otherwise
        env (dict): viable environment 
    '''
    removed = assign_val(clauses, var, val, indices)  
    
    if removed == None:
        return None      
        
    env = satisfying_assignment(clauses, indices)
    
    if env is not None:
        env[var] = val #build up env
        return env
    
    for clause in removed: #reolace the lost indices if failure
        indices[clause].update(removed[clause])
    return None

def satisfying_assignment(clauses, indices = 'not given'):
    """Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    {'a': True}
    >>> satisfying_assignment([[('a', True)], [('a', False)]])"""
    
    if indices == 'not given':
        indices = {}
        for clause in range(len(clauses)): #make indices from lengths of clauses
            indices[clause] = set(range(len(clauses[clause])))  

    for clause in indices:
        if len(indices[clause]) == 1: #if there is a legth one clause, we know what the value has to be
            literal = indices[clause].pop() 
            indices[clause].add(literal)
            var, val = clauses[clause][literal]
            return test_var(clauses, var, val, indices)   #dont need to check other possibility  
   
    var = -1 #dummy val
    for clause in indices:
        if len(indices[clause]) > 0: #use first variable whos literal is viable
            literal =indices[clause].pop() #just any old literal will do
            indices[clause].add(literal)
            var, val = clauses[clause][literal]
    
    if var == -1: #all empty -> success
        return {}
    
    env = test_var(clauses, var, val, indices) #try with true
    if env is not None:
        return env
    else: #try with false
        return test_var(clauses, var, not(val), indices)
    
def full_cnf(key, vals, key_first = True):
    '''
    builds full cnf using one key value paired with a range of vals to make variables
    makes all possible combinations
    
    Args:
        key (string): the part of the variables which is preserved throughout
        vals (set): the part of the variables which changes
        key_first (bool): tells whether key is prefix or suffix of variables
        
    Returns:
        sub_cnf (nested list): list of all possible or-clauses
    '''
    val = vals.pop()
    if key_first: #how to order variables
        variable = key + '_' + val
    else:
        variable = val + '_' + key
    
    if len(vals) == 0: #base case
        return [[(variable, True)], [(variable, False)]]
    else: #add 
        sub_cnf = full_cnf(key, vals, key_first)
        for i in range(len(sub_cnf)-1, -1, -1):
            clause = sub_cnf[i] #add a new cnf for both bool values, one can take the place of the old one
            sub_cnf[i] = clause + [(variable, True)] 
            sub_cnf.append(clause + [(variable, False)])
        return sub_cnf

def cnf_true_range(key, vals, key_first, minn, maxx):
    '''
    reduce cnf to conform to a range of desired possible truths
    
    Args:
        key (string): the part of the variables which is preserved throughout
        vals (set): the part of the variables which changes
        key_first (bool): tells whether key is prefix or suffix of variables
        minn (int): the minnimum possible num of truths
        maxx (int): the maximum possible num of truths
        
    Returns:
        cnf (nested list): list of remaining clauses
    '''
    
    cnf = full_cnf(key, vals, key_first)
    for i in range(len(cnf) -1, -1, -1):
        num_false = sum(list(map(lambda literal: not(literal[1]), cnf[i])))
        if minn <= num_false <= maxx: #if the number of false (corresponding to number of true in DNF) is in the range, remove the clause
            if i == len(cnf) - 1:
                cnf.pop()
            else:
                cnf[i] = cnf.pop()
    return cnf    
    
def boolify_scheduling_problem(student_preferences, session_capacities):
    """Convert a quiz-room-scheduling problem into a Boolean formula.
    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session
    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    
    example student preferences:
    {'Alice': {'basement', 'penthouse'},
     'Bob':   {'kitchen', 'penthouse'}}
     
    example session capacities:
    {'basement':  1,
     'kitchen':   2,
     'penthouse': 3}
    
    """
    cnf, loc_students =  [], {}
    
    for student in student_preferences:
        for loc in student_preferences[student]:
            loc_students.setdefault(loc, set()).add(student) #build dictionary for each location's students
        cnf += cnf_true_range(student, student_preferences[student], key_first = True, minn = 1, maxx = 1) #add to cnf

    for loc in session_capacities:
        if len(loc_students.get(loc, set())) > 0: #if there are students who can go there
            cnf += cnf_true_range(loc, loc_students[loc], key_first = False, minn = 0, maxx = session_capacities[loc])       
    print(cnf)
    return cnf

