# test/test_simple_model.py
"""
Тесты для упрощенной нейросети
"""

import unittest
import os
import sys
import tempfile
import shutil

# Добавляем путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from model.simple_nn.features import FeatureExtractor
from model.data_loader import validate_group, compare_groups

class TestSimpleNeural(unittest.TestCase):
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.feature_extractor = FeatureExtractor()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir)
    
    def test_feature_extraction(self):
        """Тест извлечения features"""
        history = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        features = self.feature_extractor.extract_features(history)
        
        self.assertEqual(len(features), 50)
        self.assertTrue(all(0 <= x <= 1 for x in features))
    
    def test_validate_group_valid(self):
        """Тест валидации корректной группы"""
        self.assertTrue(validate_group("1 2 3 4"))
        self.assertTrue(validate_group("26 25 24 23"))
    
    def test_validate_group_invalid(self):
        """Тест валидации некорректных групп"""
        self.assertFalse(validate_group("1 1 3 4"))  # Одинаковые числа в паре
        self.assertFalse(validate_group("1 2 3"))    # Мало чисел
        self.assertFalse(validate_group("1 2 3 4 5")) # Много чисел
        self.assertFalse(validate_group("0 2 3 4"))  # Число вне диапазона
        self.assertFalse(validate_group("1 2 3 27")) # Число вне диапазона
        self.assertFalse(validate_group("abc def ghi jkl")) # Не числа
    
    def test_compare_groups_no_matches(self):
        """Тест сравнения групп без совпадений"""
        group1 = (5, 22, 18, 11)
        group2 = (18, 10, 5, 14)  # 5 и 18 в разных парах
        
        result = compare_groups(group1, group2)
        self.assertEqual(result['total_matches'], 0)
        self.assertEqual(result['pair1_matches'], 0)
        self.assertEqual(result['pair2_matches'], 0)
    
    def test_compare_groups_one_match_first_pair(self):
        """Тест сравнения с одним совпадением в первой паре"""
        group1 = (5, 22, 18, 11)
        group2 = (19, 5, 10, 4)  # 5 в первой паре
        
        result = compare_groups(group1, group2)
        self.assertEqual(result['total_matches'], 1)
        self.assertEqual(result['pair1_matches'], 1)
        self.assertEqual(result['pair2_matches'], 0)
    
    def test_compare_groups_one_match_second_pair(self):
        """Тест сравнения с одним совпадением во второй паре"""
        group1 = (5, 22, 18, 11)
        group2 = (19, 1, 10, 18)  # 18 во второй паре
        
        result = compare_groups(group1, group2)
        self.assertEqual(result['total_matches'], 1)
        self.assertEqual(result['pair1_matches'], 0)
        self.assertEqual(result['pair2_matches'], 1)
    
    def test_compare_groups_two_matches(self):
        """Тест сравнения с двумя совпадениями"""
        group1 = (5, 22, 18, 11)
        group2 = (19, 5, 18, 4)  # 5 в первой паре + 18 во второй паре
        
        result = compare_groups(group1, group2)
        self.assertEqual(result['total_matches'], 2)
        self.assertEqual(result['pair1_matches'], 1)
        self.assertEqual(result['pair2_matches'], 1)
    
    def test_compare_groups_exact_matches(self):
        """Тест точных совпадений по позициям"""
        group1 = (1, 2, 3, 4)
        group2 = (1, 2, 5, 6)  # Точные совпадения на первых двух позициях
        
        result = compare_groups(group1, group2)
        self.assertEqual(result['exact_matches'], 2)
        self.assertEqual(result['total_matches'], 2)

if __name__ == '__main__':
    unittest.main()