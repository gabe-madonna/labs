# NO IMPORTS!

class Trie:
    ##################################################
    ## basic methods
    ##################################################

    def __init__(self):
        self.frequency = 0
        self.children = {}
        
    def insert(self, word, frequency=1):
        """ add word with given frequency to the trie. """            
        current_node = self
        
        for letter in word: #set current node to be the child by letter for each letter
            current_node = current_node.children.setdefault(letter, Trie())
        current_node.frequency += frequency #incriment frequency

    def find(self,prefix):
        """ return trie node for specified prefix, None if not in trie. """
        letter = 0
        current_node = self
        
        while current_node != None and letter < len(prefix): #search for node by incrimenting letters
            current_node = current_node.children.get(prefix[letter], None) #get next node, None if it doesnt exist
            letter += 1
        return current_node         

    def __contains__(self, word):
        """ is word in trie? return True or False. """
        trie = self.find(word) #get the trie (None if it doesnt exist)
        return trie != None and trie.frequency > 0 #makes sure its not None and has frequency > 0

    def __iter__(self):
        """ generate list of (word,freq) pairs for all words in
            this trie and its children.  Must be a generator! """
        if len(self.children) == 0:
            yield ('', self.frequency) #yield self if no children (frequency must be > 0)
        else:
            if self.frequency: #yield self if frequency > 0
                yield ('', self.frequency)
            #also, for each yielded pair in children, add their letter and then yield same pair
            for letter in self.children: 
                for (suffix, freq) in self.children[letter]:
                    yield (letter + suffix, freq)
                    
    ##################################################
    ## additional methods
    ##################################################

    def autocomplete(self, prefix, N):
        """ return the list of N most-frequently occurring words
            that start with prefix. """
        root = self.find(prefix)
        
        if root == None: return [] #return empty list if its not there
        
        words = {}
        for word, freq in root: #add word to set for words of that frequency in dict
            words.setdefault(freq, set()).add(prefix + word)
                
        output = []
        for freq in sorted(list(words.keys()), reverse = True): #go through highest frequencies first
            bound = min(N, len(words[freq])) #upper bound determined by N and number of words at frequency
            output += list(words[freq])[:bound]
            N -= bound #update N
            if N == 0: break
        
        return output
      
    
    def autocorrect(self, prefix, N):
        """ return the list of N most-frequent words that start with
            prefix or that are valid words that differ from prefix
            by a small edit:kj
            
            A single-character insertion 
            (add any one character in the range "a" to "z" at any place in the word)
            A single-character deletion 
            (remove any one character from the word)
            A single-character replacement 
            (replace any one character in the word with a character in the range a-z)
            A two-character transpose 
            (switch the positions of any two adjacent characters in the word)
        """
        def edit(word):
            '''
            edits the word through insertion, deletion, replacement, and swapping
            
            Args:
                word (str): word to edit
            Returns:
                generator: all of the possile edits
            '''
            
            letters = 'abcdefghijklmnopqrstuvwxyz'
            for index in range(len(word)):
                yield word[:index] + word[index+1:] #deletion
                for index2 in range(index+1, len(word)): #swapping
                    yield word[:index] + word[index2] + word[index+1:index2] + word[index] + word[index2+1:]
                for letter in letters:
                    yield word[:index] + letter + word[index:] #insertion                   
                    yield word[:index] + letter + word[index+1:] #replacement
        
        output = self.autocomplete(prefix, N) #initial autocompletes
        N -= len(output)
        
        if N > 0: #if there is N left over
            words = {}
            for new_word in edit(prefix): #iterate over all possible edits
                node = self.find(new_word) #try to find new word
                if node and node.frequency > 0: #if it exists and has frequency > 0
                    words.setdefault(node.frequency, set()).add(new_word) #add it to freq dict
        
            for freq in sorted(list(words.keys()), reverse = True): #start with highest frequencies again
                bound = min(N, len(words[freq]))
                output += list(words[freq])[:bound]
                N -= bound
                if N == 0:
                    break
                
        return output
                    
    def filter(self,pattern):
        """ return list of (word, freq) for all words in trie that match
            pattern.  pattern is a string, interpreted as explained below:
             * matches any sequence of zero or more characters,
             ? matches any single character,
             otherwise char in pattern char must equal char in word. """
        
        def add_results(output, chars, to_filter):
            '''
            add the results if a filter to output
            
            Args:
                chars (list of str): letters to iterate over
                to_filter (str): pattern being filtered
                
            Returns:
                None (just updates output)
            '''
            for char in chars:
                for (suffix, freq) in self.children[char].filter(to_filter):
                    output[char + suffix] = freq
        
        output = {}
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        child_list = list(self.children.keys()) #children of node
        
        if (len(pattern) == 0 or pattern == '*') and self.frequency > 0:
            output[''] = self.frequency #add self if pattern empty or *and frequency > 0
                
        if len(pattern) > 0: #if pattern exists
            first_char = pattern[0]
            if first_char == '*': #case 1: star (*)
                add_results(output, child_list, pattern) #add everything and keep star in pattern
                add_results(output, child_list, pattern[1:]) #add everything and remove star from pattern
            
            elif first_char == '?': #case 2: question mark (?)
                add_results(output, child_list, pattern[1:]) #add everything
            
            elif first_char in alphabet and first_char in child_list: #case 3: character
                add_results(output, [first_char], pattern[1:]) #add char
        
        return list(output.items()) #return in list of tuples form
