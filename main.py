import sys
from algo import Grammar, EarleyParser, GrammarException

def get_next_line():
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if line: 
            return line

def read_input_interactive():
    try:
        line1 = sys.stdin.readline()
        if not line1: return None, []
        
        parts = line1.strip().split()
        if not parts: return None, []
        
        num_nt, num_t, num_p = map(int, parts)
        
        nt_line = sys.stdin.readline().strip()
        non_terminals = set(c for c in nt_line if c.strip())
        
        t_line = sys.stdin.readline().strip()
        terminals = set(c for c in t_line if not c.isspace())
        
        grammar = Grammar(non_terminals, terminals, "S")
        
        for _ in range(num_p):
            raw_rule = sys.stdin.readline().strip()
            
            if "->" not in raw_rule:
                continue
                
            left, right = raw_rule.split("->", 1)
            left = left.strip()
            right = right.strip()
            
            right_syms = [c for c in right]
            grammar.add_rule(left, right_syms)
            
        start_symbol = sys.stdin.readline().strip()
        grammar.start_symbol = start_symbol
        
        m_line = sys.stdin.readline().strip()
        if not m_line:
            m = 0
        else:
            m = int(m_line)
            
        words = []
        for _ in range(m):
            w = sys.stdin.readline().strip()
            words.append(w)
            
        return grammar, words

    except ValueError:
        raise GrammarException("Invalid integer format in input")

if __name__ == "__main__":
    try:
        grammar, words = read_input_interactive()
        
        if grammar:
            parser = EarleyParser()
            parser.fit(grammar)
            
            for w in words:
                result = parser.predict(w)
                print("Yes" if result else "No")
                
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
