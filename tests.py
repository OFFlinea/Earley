import unittest
from algo import Grammar, EarleyParser

class TestEarley(unittest.TestCase):
    
    def setUp(self):
        self.parser = EarleyParser()

    def _build_and_test(self, grammar, yes_words, no_words):
        self.parser.fit(grammar)
        
        for w in yes_words:
            with self.subTest(word=w, expected=True):
                self.assertTrue(self.parser.predict(w), f"Word '{w}' SHOULD be accepted")
        
        for w in no_words:
            with self.subTest(word=w, expected=False):
                self.assertFalse(self.parser.predict(w), f"Word '{w}' SHOULD be rejected")

    def test_01_classic_task_example(self):
        """Тест из условия задачи (S -> aSbS | epsilon)"""
        g = Grammar({"S"}, {"a", "b"}, "S")
        g.add_rule("S", ["a", "S", "b", "S"])
        g.add_rule("S", [])
        yes = ["aababb", "", "ab", "abab"]
        no = ["aabbba", "a", "b", "ba", "aabbb"]
        self._build_and_test(g, yes, no)

    def test_02_palindromes(self):
        """Палиндромы над {a, b}"""
        g = Grammar({"S"}, {"a", "b"}, "S")
        g.add_rule("S", ["a", "S", "a"])
        g.add_rule("S", ["b", "S", "b"])
        g.add_rule("S", ["a"])
        g.add_rule("S", ["b"])
        g.add_rule("S", [])
        yes = ["aba", "abba", "a", "b", "", "aaaaa"]
        no = ["ab", "abab", "aab"]
        self._build_and_test(g, yes, no)

    def test_03_balanced_brackets(self):
        """Правильные скобочные последовательности"""
        g = Grammar({"S"}, {"(", ")", "[", "]"}, "S")
        g.add_rule("S", ["S", "S"])
        g.add_rule("S", ["(", "S", ")"])
        g.add_rule("S", ["[", "S", "]"])
        g.add_rule("S", [])
        yes = ["()", "[]", "([])", "()[]", "([([])])", ""]
        no = ["(]", "([)]", "((", "]", ")(", "([)]"]
        self._build_and_test(g, yes, no)

    def test_04_arithmetic_precedence(self):
        """Арифметика с приоритетом операций"""
        g = Grammar({"E", "T", "F"}, {"+", "*", "(", ")", "a"}, "E")
        g.add_rule("E", ["E", "+", "T"])
        g.add_rule("E", ["T"])
        g.add_rule("T", ["T", "*", "F"])
        g.add_rule("T", ["F"])
        g.add_rule("F", ["(", "E", ")"])
        g.add_rule("F", ["a"])
        yes = ["a", "a+a", "a*a", "a+a*a", "(a+a)*a"]
        no = ["a+", "+a", "aa", "a+*a", "(a))"]
        self._build_and_test(g, yes, no)

    def test_05_long_rules(self):
        """Длинные правила (больше 2 символов)"""
        g = Grammar({"S"}, {"a", "b", "c", "d", "e"}, "S")
        g.add_rule("S", ["a", "b", "c", "d", "e"])
        yes = ["abcde"]
        no = ["abcd", "bcde", "abcdea", ""]
        self._build_and_test(g, yes, no)

    def test_06_chain_rules(self):
        """Цепные правила (Unit productions)"""
        g = Grammar({"S", "A", "B", "C"}, {"c"}, "S")
        g.add_rule("S", ["A"])
        g.add_rule("A", ["B"])
        g.add_rule("B", ["C"])
        g.add_rule("C", ["c"])
        yes = ["c"]
        no = ["cc", "", "A"]
        self._build_and_test(g, yes, no)

    def test_07_only_empty_string(self):
        """Язык только из пустой строки"""
        g = Grammar({"S"}, {"a"}, "S")
        g.add_rule("S", [])
        yes = [""]
        no = ["a", "aa"]
        self._build_and_test(g, yes, no)

    def test_08_mixed_terminals_nonterminals(self):
        """Смешанные правила (терминалы внутри правил)"""
        g = Grammar({"S", "B"}, {"a", "b", "c"}, "S")
        g.add_rule("S", ["a", "B", "c"])
        g.add_rule("B", ["b"])
        yes = ["abc"]
        no = ["ac", "abbc", "ab"]
        self._build_and_test(g, yes, no)

    def test_09_unknown_symbols(self):
        """Символы не из алфавита"""
        g = Grammar({"S"}, {"a"}, "S")
        g.add_rule("S", ["a"])
        self.parser.fit(g)
        self.assertFalse(self.parser.predict("b"))

    def test_10_complex_cnf_conversion(self):
        """Сложная конвертация в CNF (смесь проблем)"""
        g = Grammar({"S", "A", "B"}, {"a", "b"}, "S")
        g.add_rule("S", ["A", "S", "B"])
        g.add_rule("S", [])
        g.add_rule("A", ["a"])
        g.add_rule("B", ["b"])
        yes = ["", "ab", "aabb", "aaabbb"]
        no = ["a", "b", "ba", "aabbb", "aaabb"]
        self._build_and_test(g, yes, no)

    def test_11_cyclic_unit_rules(self):
        """
        Циклические unit rules: S -> A -> B -> S.
        Препроцессинг не должен зависнуть, а S должен в итоге иметь правило -> a.
        """
        g = Grammar({"S", "A", "B"}, {"a"}, "S")
        g.add_rule("S", ["A"])
        g.add_rule("A", ["B"])
        g.add_rule("B", ["S"])
        g.add_rule("A", ["a"])
        
        yes = ["a"]
        no = ["aa", "b", ""]
        self._build_and_test(g, yes, no)

    def test_12_unreachable_rules(self):
        """
        Символы, до которых нельзя добраться из Start.
        Они не должны влиять на разбор.
        """
        g = Grammar({"S", "X"}, {"a", "b"}, "S")
        g.add_rule("S", ["a"])
        g.add_rule("X", ["b"])
        
        yes = ["a"]
        no = ["b", "ab"]
        self._build_and_test(g, yes, no)

    def test_13_dead_nonterminals(self):
        """
        Нетерминалы, которые никогда не становятся терминалами.
        S -> A B, A -> a, B -> B B (бесконечная рекурсия без выхода)
        Язык должен быть пуст.
        """
        g = Grammar({"S", "A", "B"}, {"a"}, "S")
        g.add_rule("S", ["A", "B"])
        g.add_rule("A", ["a"])
        g.add_rule("B", ["B", "B"])
        
        yes = []
        no = ["a", "aa", ""]
        self._build_and_test(g, yes, no)

    def test_14_complex_nullable(self):
        """
        S -> A B C, где все A, B, C могут исчезнуть.
        Проверка корректного вычисления Nullable для длинных правил.
        """
        g = Grammar({"S", "A", "B", "C"}, {"a", "b", "c"}, "S")
        g.add_rule("S", ["A", "B", "C"])
        
        g.add_rule("A", ["a"])
        g.add_rule("A", [])
        
        g.add_rule("B", ["b"])
        g.add_rule("B", [])
        
        g.add_rule("C", ["c"])
        g.add_rule("C", [])
        
        yes = ["", "a", "b", "c", "ab", "ac", "bc", "abc"]
        no = ["cb", "aa"] 
        self._build_and_test(g, yes, no)

    def test_15_ambiguity_stress(self):
        """
        Сильная неоднозначность: S -> SS | a.
        Генерирует любую строку из 'a'.
        Таблица DP будет очень плотной.
        """
        g = Grammar({"S"}, {"a"}, "S")
        g.add_rule("S", ["S", "S"])
        g.add_rule("S", ["a"])
        
        yes = ["a", "aa", "aaa", "aaaaa"]
        no = ["", "b", "aab"]
        self._build_and_test(g, yes, no)

    def test_16_left_and_right_recursion(self):
        """
        Проверка левой и правой рекурсии одновременно.
        S -> S a | b S | c
        """
        g = Grammar({"S"}, {"a", "b", "c"}, "S")
        g.add_rule("S", ["S", "a"])
        g.add_rule("S", ["b", "S"])
        g.add_rule("S", ["c"])
        
        yes = ["c", "ca", "bc", "bca", "bbcaaa"]
        no = ["cc", "a", "b", "ac"]
        self._build_and_test(g, yes, no)

    def test_17_self_loop_elimination(self):
        """
        Прямой цикл S -> S.
        Должен корректно удалиться и не мешать другим правилам.
        S -> S | a
        """
        g = Grammar({"S"}, {"a"}, "S")
        g.add_rule("S", ["S"])
        g.add_rule("S", ["a"])
        
        yes = ["a"]
        no = ["", "aa"]
        self._build_and_test(g, yes, no)

    def test_18_many_mixed_terminals(self):
        """
        Длинное правило с кучей терминалов, требующее создания многих NT.
        S -> 1 S 0 S 1 | 0
        (Симметричные строки с разделителями)
        """
        g = Grammar({"S"}, {"0", "1"}, "S")
        g.add_rule("S", ["1", "S", "0", "S", "1"])
        g.add_rule("S", ["0"])
        
        yes = ["0", "10001", "110001001"]
        no = ["101", "11001", ""]
        self._build_and_test(g, yes, no)

    def test_19_user_case_ACA(self):
        """
        Проверка корректности работы с nullable.
        S -> A C A
        A -> epsilon | a
        C -> c
        Язык: {c, ac, ca, aca}
        """
        g = Grammar({"S", "A", "C"}, {"a", "c"}, "S")
        g.add_rule("S", ["A", "C", "A"])
        g.add_rule("A", [])
        g.add_rule("A", ["a"])
        g.add_rule("C", ["c"])
        
        yes = ["c", "ac", "ca", "aca"]
        no = ["a", "aa", "", "cc"] 
        
        self._build_and_test(g, yes, no)

if __name__ == '__main__':
    unittest.main(verbosity=2)
