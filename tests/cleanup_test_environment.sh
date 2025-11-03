# [file name]: tests/cleanup_test_environment.sh
#!/bin/bash
# ОЧИСТКА тестовой среды

echo "🧹 ОЧИСТКА ТЕСТОВОЙ СРЕДЫ..."

cd /opt/project/tests

# Удаляем тестовые директории (кроме самих тестов)
rm -rf test_data/ test_logs/ test_config/

echo "✅ Тестовая среда очищена"
echo "💡 Для восстановления: python3 setup_test_environment.py"