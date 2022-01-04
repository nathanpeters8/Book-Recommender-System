from hw1 import *
import unittest, numpy as np, pandas as pd, random, sqlite3, pickle
from compare_pandas import *
import sys, io 
from unittest.mock import patch
from contextlib import redirect_stdout

''' 
Auxiliary files needed:
    
'''

class TestFns(unittest.TestCase):
    def setUp(self):
        c1 = sqlite3.connect('small.db')
        c2 = sqlite3.connect('bookstore.db')
        self.file_ends = [('_small', c1), ('_small3', c1), ('_bkstore', c2), ('_bkstore7', c2)]
        self.vals_all = {
            'purchase': [pickle.load(open('purchase' + x[0] + '.pkl', 'rb')) for x in self.file_ends[0:3:2]],
            'empty_count': [pd.read_pickle('empty_count' + x[0] + '.pkl') for x in self.file_ends[0:3:2]],
            'full_count': [pd.read_pickle('full_count' + x[0] + '.pkl') for x in self.file_ends[0:3:2]],
            'probability': [pd.read_pickle('probability' + x[0] + '.pkl') for x in self.file_ends[0:3:2]],
            'sparse': [pickle.load(open('sparse' + x[0] + '.pkl', 'rb')) for x in self.file_ends[0:3:2]],
            }
    
    def test_get_purchase_matrix(self):
        for i in range(2):
            fend, conn = self.file_ends[2*i]
            self.assertEqual(self.vals_all['purchase'][i], get_purchase_matrix(conn))
    
    def test_get_empty_count_matrix(self):
        for i in range(2):
            fend, conn = self.file_ends[2*i]
            self.assertTrue(compare_frames(self.vals_all['empty_count'][i], get_empty_count_matrix(conn)))
    
    def test_fill_count_matrix(self):
        for i in range(2):
            fend, conn = self.file_ends[2*i]
            self.assertIsNone(fill_count_matrix(self.vals_all['empty_count'][i], self.vals_all['purchase'][i]))
            self.assertTrue(compare_frames(self.vals_all['full_count'][i], self.vals_all['empty_count'][i]))
    
    def test_make_probability_matrix(self):
        for i in range(2):
            fend, conn = self.file_ends[2*i]
            self.assertTrue(compare_frames(self.vals_all['probability'][i], make_probability_matrix(
                self.vals_all['full_count'][i])))
    
    def test_sparse_p_matrix(self):
        for i in range(2):
            fend, conn = self.file_ends[2*i]
            self.assertEqual(self.vals_all['sparse'][i], sparse_p_matrix(self.vals_all['probability'][i]))
    
    def test_get_cust_id(self):
        conn = sqlite3.connect('small.db')
        conn.row_factory = sqlite3.Row
        with patch('builtins.input', side_effect = [1, 3, '']):
            with io.StringIO() as buf, redirect_stdout(buf):
                self.assertEqual(1, get_cust_id(conn))
                self.assertEqual('CID       Name\n-----     -----\n' +
                                 '    1     Thompson, Rich\n' +
                                 '    2     Marzanna, Alfie\n' +
                                 '    3     Knut, Dan\n---------------\n', buf.getvalue())
                self.assertEqual(3, get_cust_id(conn))
                self.assertIsNone(get_cust_id(conn))
        
    
    def test_purchase_history(self):
        conn = sqlite3.connect('small.db')
        conn.row_factory = sqlite3.Row
        ret1 = ('Purchase history for Rich Thompson\n' + 
        '----------------------------------\n' +
        'Sams Teach Yourself SQL in 10 Minutes\n' +
        'Python Data Science Handbook: Essential Tools for Working with Data\n' + 
        '----------------------------------------\n')
        ret2 = ('Purchase history for Dan Knut\n' +
        '-----------------------------\n' +
        'Sams Teach Yourself SQL in 10 Minutes\n' +
        'Python More\n' +
        '----------------------------------------\n')
        self.assertEqual(ret1, purchase_history(1, self.vals_all['purchase'][0][1], conn))
        self.assertEqual(ret2, purchase_history(3, self.vals_all['purchase'][0][3], conn))
    
    def test_get_recent(self):
        random.seed(27)
        conn = sqlite3.connect('bookstore.db')
        conn.row_factory = sqlite3.Row
        isbns = ['978-0465094257', '978-0441020423',
                 '978-1942111177', '978-0440226451',
                 '978-0679733379', '978-0143129608']
        for i in range(6):
            self.assertEqual(isbns[i], get_recent((i + 1) * 2, conn))
    
    def test_get_recommendation(self):
        random.seed(4)
        conn = sqlite3.connect('small.db')
        conn.row_factory = sqlite3.Row
        ret1 = ('Recommendations for Rich Thompson\n' +
                '---------------------------------\n' +
                'Python More\n' +
                'Fundamentals of Database Systems\n')
        ret2 = ('Recommendations for Dan Knut\n' +
                '----------------------------\n' +
                'Fundamentals of Database Systems\n' +
                'Python Data Science Handbook: Essential Tools for Working with Data\n')
        self.assertEqual(ret1, get_recommendation(1, self.vals_all['sparse'][0], 
            self.vals_all['purchase'][0][1], conn))
        self.assertEqual(ret2, get_recommendation(3, self.vals_all['sparse'][0], 
            self.vals_all['purchase'][0][3], conn))
        
def main():
    test = unittest.defaultTestLoader.loadTestsFromTestCase(TestFns)
    results = unittest.TextTestRunner().run(test)
    print('Correctness score = ', str((results.testsRun - len(results.errors) - len(results.failures)) / results.testsRun * 100) + ' / 100')
    
    
if __name__ == "__main__":
    main()