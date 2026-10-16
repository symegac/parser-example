import unittest

from parser.types import is_int, is_float, is_bool, is_none, parse_simple_type

class TestColtypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.not_strings = [None, 42, 3.14, 6/7]
        cls.int_strings = ['1', b'49', '\x31', '0', '-23']
        cls.numeric_strings = ['\b00110001', '\033[31m', '1/3', '4/4']
        cls.float_strings = ['1.23', '-9.63', '.0', '3.']
        cls.none_strings = ["None", "none", "NONE", "Null", "null", "NULL", "N/A", "n/a"]
        cls.bool_strings = ["True", "true", "TRUE", "False", "false", "FALSE"]

    def test_is_int(self):
        for not_string in self.not_strings:
            with self.assertRaises((AttributeError, TypeError)):
                is_int(not_string)

        for int_string in self.int_strings:
            self.assertTrue(is_int(int_string))

        for non_int_strings in [self.numeric_strings, self.float_strings, self.none_strings, self.bool_strings]:
            for non_int_string in non_int_strings:
                self.assertFalse(is_int(non_int_string))

    def test_is_float(self):
        for non_string in self.not_strings:
            with self.assertRaises((AttributeError, TypeError)):
                is_float(non_string)

        for float_string in self.float_strings:
            self.assertTrue(is_float(float_string))

        for non_float_strings in [self.numeric_strings, self.int_strings, self.none_strings, self.bool_strings]:
            for non_float_string in non_float_strings:
                try:
                    self.assertFalse(is_float(non_float_string))
                except TypeError:
                    continue

    def test_is_none(self):
        for non_string in self.not_strings:
            with self.assertRaises((AttributeError, TypeError)):
                is_none(non_string)

        for none_string in self.none_strings:
            self.assertTrue(is_none(none_string))

        for non_none_strings in [self.numeric_strings, self.int_strings, self.float_strings, self.bool_strings]:
            for non_none_string in non_none_strings:
                self.assertFalse(is_none(non_none_string))

    def test_is_bool(self):
        for non_string in self.not_strings:
            with self.assertRaises((AttributeError, TypeError)):
                is_bool(non_string)

        for bool_string in self.bool_strings:
            self.assertTrue(is_bool(bool_string))

        for non_bool_strings in [self.numeric_strings, self.int_strings, self.float_strings, self.none_strings]:
            for non_bool_string in non_bool_strings:
                self.assertFalse(is_bool(non_bool_string))

    def test_parse_simple_type(self):
        self.assertIsInstance(parse_simple_type('1'), int)
        self.assertIsInstance(parse_simple_type('1.'), float)
        self.assertIsInstance(parse_simple_type('trUe'), bool)
        self.assertIs(parse_simple_type('NONE'), None)
        self.assertIsInstance(parse_simple_type('H.C. Andersen'), str)
