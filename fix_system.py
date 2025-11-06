# Исправляем отступы в ml/core/system.py
with open('ml/core/system.py', 'r') as f:
    content = f.read()

# Заменяем неправильно отформатированную функцию get_status
old_get_status = '''        def get_status(self):
        """Возвращает статус системы"""
        return {
            'is_trained': self.is_trained,
            'dataset_size': 0,  # TODO: заменить на реальный размер датасета
            'model_type': 'EnhancedNumberPredictor',
            'learning_stats': {
                'recent_accuracy_avg': 0.5
            }
    }'''

new_get_status = '''    def get_status(self):
        """Возвращает статус системы"""
        return {
            'is_trained': self.is_trained,
            'dataset_size': 0,  # TODO: заменить на реальный размер датасета
            'model_type': 'EnhancedNumberPredictor',
            'learning_stats': {
                'recent_accuracy_avg': 0.5
            }
        }'''

content = content.replace(old_get_status, new_get_status)

with open('ml/core/system.py', 'w') as f:
    f.write(content)

print("✅ Отступы исправлены")
