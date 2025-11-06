# Читаем текущий файл
with open('utils/logging_system.py', 'r') as f:
    lines = f.readlines()

# Удаляем все строки с get_AutoLearningService_logger
new_lines = [line for line in lines if 'get_AutoLearningService_logger' not in line]

# Добавляем один псевдоним в конец файла (перед setup_all_loggers)
for i, line in enumerate(new_lines):
    if 'def setup_all_loggers():' in line:
        new_lines.insert(i, '\n# Псевдонимы для обратной совместимости\nget_AutoLearningService_logger = get_auto_learning_logger\n\n')
        break

# Записываем обратно
with open('utils/logging_system.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Дубликаты удалены, добавлен один псевдоним")
