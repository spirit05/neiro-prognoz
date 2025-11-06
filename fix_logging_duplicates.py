# Читаем текущий файл
with open('utils/logging_system.py', 'r') as f:
    content = f.read()

# Удаляем все существующие псевдонимы
import re
content = re.sub(r'# Псевдонимы для обратной совместимости\s*get_AutoLearningService_logger = get_auto_learning_logger\s*', '', content)

# Добавляем один псевдоним в правильное место - после всех функций и перед setup_all_loggers
# Находим последнюю функцию перед setup_all_loggers
lines = content.split('\n')
insert_index = None
for i, line in enumerate(lines):
    if 'def setup_all_loggers():' in line:
        insert_index = i
        break

if insert_index is not None:
    # Вставляем псевдоним перед setup_all_loggers
    lines.insert(insert_index, '')
    lines.insert(insert_index, 'get_AutoLearningService_logger = get_auto_learning_logger')
    lines.insert(insert_index, '# Псевдонимы для обратной совместимости')

# Записываем обратно
with open('utils/logging_system.py', 'w') as f:
    f.write('\n'.join(lines))

print("✅ Дубликаты удалены, псевдоним добавлен в правильное место")
