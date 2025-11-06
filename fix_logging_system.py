# Читаем текущий файл
with open('utils/logging_system.py', 'r') as f:
    lines = f.readlines()

# Находим место перед setup_all_loggers для добавления псевдонима
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if 'def setup_all_loggers():' in line:
        # Добавляем псевдоним перед этой функцией
        new_lines.insert(i, '\n# Псевдонимы для обратной совместимости\nget_AutoLearningService_logger = get_auto_learning_logger\n\n')

# Записываем обратно
with open('utils/logging_system.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Псевдоним добавлен в правильное место")
