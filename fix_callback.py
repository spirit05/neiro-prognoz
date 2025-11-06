# Читаем текущий файл
with open('ml/core/system.py', 'r') as f:
    lines = f.readlines()

# Находим место для добавления метода (после метода _report_progress)
insert_index = None
for i, line in enumerate(lines):
    if 'def _report_progress(self, message):' in line:
        # Ищем конец этого метода
        for j in range(i+1, len(lines)):
            if lines[j].strip() and not lines[j].startswith('    ') and not lines[j].startswith('        '):
                insert_index = j
                break
        break

if insert_index is not None:
    # Добавляем метод set_progress_callback
    method_code = [
        '    def set_progress_callback(self, callback):\n',
        '        """Установка callback-функции для отслеживания прогресса"""\n',
        '        self.progress_callback = callback\n',
        '\n'
    ]
    lines[insert_index:insert_index] = method_code
    
    # Записываем обратно
    with open('ml/core/system.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Метод set_progress_callback добавлен")
else:
    print("❌ Не удалось найти место для вставки метода")
