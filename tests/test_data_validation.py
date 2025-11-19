# test_data_validation.py
import logging
from ml.data.quality.validators import DataValidator

def test_data_validation():
    """Тестирование валидации данных"""
    logger = logging.getLogger("DATA_VALIDATION_TEST")
    
    validator = DataValidator()
    
    # Тестовые группы
    test_groups = [
        "1 2 3 4",        # валидная
        "25 26 1 2",      # валидная  
        "1 1 2 3",        # невалидная (дубликаты в паре)
        "27 1 2 3",       # невалидная (число > 26)
        "0 1 2 3",        # невалидная (число < 1)
        "1 2 3",          # невалидная (не 4 числа)
        "abc def ghi jkl" # невалидная (не числа)
    ]
    
    logger.info("🧪 Тестирование валидации данных...")
    
    for group in test_groups:
        is_valid = validator.validate_group(group)
        logger.info(f"   {group} -> {'✅ Валидна' if is_valid else '❌ Невалидна'}")
    
    assert True
