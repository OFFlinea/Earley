from collections import defaultdict
from typing import List, Set, Dict, Tuple, Optional

class GrammarException(Exception):
    pass

class Grammar:
    """
    Класс грамматики.
    Позволяет задавать грамматику через исходный код (методы),
    не завися от ввода с консоли.
    """
    def __init__(self, non_terminals: Set[str], terminals: Set[str], start_symbol: str):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.start_symbol = start_symbol
        self.rules: Dict[str, List[List[str]]] = defaultdict(list)

    def add_rule(self, left: str, right: List[str]):
        """Добавление правила через код."""
        for sym in right:
            if sym not in self.non_terminals and sym not in self.terminals:
                pass
        self.rules[left].append(right)

class ParsingAlgorithm:
    def fit(self, grammar: Grammar): raise NotImplementedError
    def predict(self, word: str) -> bool: raise NotImplementedError

class EarleyItem:
    """
    Элемент состояния Эрли: [A -> alpha . beta, i]
    head: A
    body: alpha beta (полный список символов правой части)
    dot: индекс точки (от 0 до len(body))
    start: индекс начала разбора (i)
    """
    def __init__(self, head: str, body: tuple, dot: int, start: int):
        self.head = head
        self.body = body
        self.dot = dot
        self.start = start
        self._hash = hash((head, body, dot, start))

    def is_complete(self):
        return self.dot >= len(self.body)

    def next_symbol(self):
        if self.is_complete():
            return None
        return self.body[self.dot]

    def __repr__(self):
        body_str = list(self.body)
        body_str.insert(self.dot, "•")
        return f"[{self.head} -> {''.join(body_str)}, {self.start}]"

    def __eq__(self, other):
        if self is other: return True
        if not isinstance(other, EarleyItem): return False
        return (self.head == other.head and 
                self.body == other.body and 
                self.dot == other.dot and 
                self.start == other.start)

    def __hash__(self):
        return self._hash


class EarleyParser(ParsingAlgorithm):
    def __init__(self):
        self.grammar = None
        self.augmented_start = "__AUG_S__"

    def fit(self, grammar: Grammar):
        if grammar.start_symbol not in grammar.non_terminals:
            raise GrammarException(f"Start symbol '{grammar.start_symbol}' is not in NonTerminals")

        self.grammar = grammar
        pass

    def predict(self, word: str) -> bool:
        for char in word:
            if char not in self.grammar.terminals:
                return False

        n = len(word)
        D = [set() for _ in range(n + 1)]
        Q = [[] for _ in range(n + 1)]

        start_item = EarleyItem(self.augmented_start, (self.grammar.start_symbol,), 0, 0)
        D[0].add(start_item)
        Q[0].append(start_item)

        for j in range(n + 1):
            idx = 0
            while idx < len(Q[j]):
                item = Q[j][idx]
                idx += 1
                
                if not item.is_complete():
                    next_sym = item.next_symbol()
                    
                    if next_sym in self.grammar.non_terminals:
                        self._predict(next_sym, j, D, Q)
                    elif next_sym in self.grammar.terminals:
                        self._scan(item, next_sym, word, j, D, Q)
                else:
                    self._complete(item, j, D, Q)

        final_item = EarleyItem(self.augmented_start, (self.grammar.start_symbol,), 1, 0)
        return final_item in D[n]

    def _predict(self, non_terminal, current_pos, D, Q):
        for body in self.grammar.rules[non_terminal]:
            new_item = EarleyItem(non_terminal, tuple(body), 0, current_pos)
            if new_item not in D[current_pos]:
                D[current_pos].add(new_item)
                Q[current_pos].append(new_item)

    def _scan(self, item, symbol, word, current_pos, D, Q):
        if current_pos < len(word) and word[current_pos] == symbol:
            new_item = EarleyItem(item.head, item.body, item.dot + 1, item.start)
            if new_item not in D[current_pos + 1]:
                D[current_pos + 1].add(new_item)
                Q[current_pos + 1].append(new_item)

    def _complete(self, completed_item, current_pos, D, Q):
        source_pos = completed_item.start
        
        for waiting_item in list(D[source_pos]):
            if not waiting_item.is_complete() and waiting_item.next_symbol() == completed_item.head:
                new_item = EarleyItem(waiting_item.head, waiting_item.body, waiting_item.dot + 1, waiting_item.start)
                if new_item not in D[current_pos]:
                    D[current_pos].add(new_item)
                    Q[current_pos].append(new_item)