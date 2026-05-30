import unittest
from logic import filter_perfumes, get_longevity_label, is_already_in_favorites, get_budget_display
from auth import hash_password

class TestBusinessLogic(unittest.TestCase):
    
    def setUp(self):
        # örnek parfüm veritabanı 
        self.sample_perfumes = [
            {'id': 1, 'name': 'Cloud', 'gender': 'female', 'budget': 'mid', 'season': 'fall,winter', 'mood': 'daily', 'notes': 'sweet,vanilla,floral'},
            {'id': 2, 'name': 'Aventus', 'gender': 'male', 'budget': 'luxury', 'season': 'spring,summer', 'mood': 'work', 'notes': 'fruity,woody,smoky'},
            {'id': 3, 'name': 'Jazz Club', 'gender': 'unisex', 'budget': 'luxury', 'season': 'fall,winter', 'mood': 'evening', 'notes': 'sweet,woody,tobacco'}
        ]
        
        #  örnek favori listesi
        self.sample_favorites = [{'perfume_id': 1}, {'perfume_id': 3}]

    #  logic.py Testleri 

    def test_get_longevity_label(self):
        # Sınır değerleri (boundary values) test ediyoruz
        self.assertEqual(get_longevity_label(3), 'Short lasting')
        self.assertEqual(get_longevity_label(4), 'Short lasting')
        self.assertEqual(get_longevity_label(6), 'Moderate')
        self.assertEqual(get_longevity_label(7), 'Moderate')
        self.assertEqual(get_longevity_label(9), 'Long lasting')
        self.assertEqual(get_longevity_label(10), 'Long lasting')
        self.assertEqual(get_longevity_label(12), 'Very long lasting')

    def test_filter_perfumes_by_gender(self):
        # Sadece kadın parfümlerini filtreleme
        result = filter_perfumes(self.sample_perfumes, gender='female', budget='', season='', mood='', note='')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Cloud')

    def test_filter_perfumes_by_note(self):
        # İçinde "woody" notası geçenleri filtreleme (Aventus ve Jazz Club gelmeli)
        result = filter_perfumes(self.sample_perfumes, gender='', budget='', season='', mood='', note='woody')
        self.assertEqual(len(result), 2)
        names = [p['name'] for p in result]
        self.assertIn('Aventus', names)
        self.assertIn('Jazz Club', names)

    def test_filter_perfumes_multiple_criteria(self):
        # Hem lüks bütçeli hem de kışın kullanılabilenleri getirmeli
        result = filter_perfumes(self.sample_perfumes, gender='', budget='luxury', season='winter', mood='', note='')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Jazz Club')

    def test_filter_perfumes_no_match(self):
        # Eşleşmeyen bir arama
        result = filter_perfumes(self.sample_perfumes, gender='male', budget='budget', season='', mood='', note='')
        self.assertEqual(len(result), 0)

    def test_is_already_in_favorites(self):
        # Favorilerde olan ve olmayan ID'lerin kontrolü
        self.assertTrue(is_already_in_favorites(self.sample_favorites, 1))
        self.assertFalse(is_already_in_favorites(self.sample_favorites, 2))
        self.assertTrue(is_already_in_favorites(self.sample_favorites, 3))

    def test_get_budget_display(self):
        # Sözlük dönüşümlerinin doğruluğu
        self.assertEqual(get_budget_display('budget'), 'Budget-Friendly')
        self.assertEqual(get_budget_display('mid'), 'Mid-Range')
        self.assertEqual(get_budget_display('luxury'), 'Luxury')
        # Tanımlı olmayan bir değer gelirse kendisini dönmeli
        self.assertEqual(get_budget_display('cheap'), 'cheap')