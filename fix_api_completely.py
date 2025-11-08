# Полная замена метода _call_api
import re

with open('services/auto_learning/api_client.py', 'r') as f:
    content = f.read()

# Находим начало и конец метода _call_api
start = content.find('def _call_api(self)')
if start == -1:
    print("❌ Не найден метод _call_api")
    exit(1)

# Находим конец метода (следующий def или конец класса)
end = content.find('def ', start + 1)
if end == -1:
    end = content.find('class ', start + 1)
if end == -1:
    end = len(content)

# Заменяем метод
old_method = content[start:end]
new_method = '''    def _call_api(self) -> Optional[Dict[str, Any]]:
        """Вызов API stoloto.ru - ПОЛНОСТЬЮ ПЕРЕПИСАННЫЙ"""
        try:
            # Подготовка URL
            info = self.get_current_info()
            current_draw_str = info.get('current_draw', '0')
            
            try:
                current_draw = int(current_draw_str)
                next_draw = current_draw + 1
            except (ValueError, TypeError):
                next_draw = 1
            
            url = f"https://www.stoloto.ru/p/api/mobile/api/v35/service/games/details/draw-combination?game=dvazhdydva&draw={next_draw}"
            
            # Выполнение запроса через curl
            result = subprocess.run([
                'curl', 
                '-s', '--max-time', '30',
                '-H', 'User-Agent: Mozilla/5.0', 
                '-H', 'Accept: application/json, text/plain, */*',
                '-H', 'Device-Platform: WEB_MOBILE_LINUX',
                '-H', 'Device-Type: MOBILE', 
                '-H', 'Gosloto-Partner: bXMjXFRXZ3coWXh6R3s1NTdUX3dnWlBMLUxmdg',
                '-H', 'gosloto-token: 76b9725602-dcfb02-4fb151-b0df27-949295930e0c26', 
                '-H', 'referer: https://www.stoloto.ru/dvazhdydva/archive',
                url
            ], capture_output=True, text=True, check=True, timeout=35)
            
            if result.returncode != 0:
                print(f"❌ Curl ошибка: код {result.returncode}")
                return None
            
            # Парсим JSON
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                print(f"📄 Ответ: {result.stdout[:200]}...")
                return None
            
            # ⚡ КРИТИЧЕСКАЯ ПРОВЕРКА: response_data может быть None
            if not response_data:
                print("❌ response_data is None")
                return None
            
            # ⚡ КРИТИЧЕСКАЯ ПРОВЕРКА: combination может отсутствовать
            if 'combination' not in response_data:
                print("⚠️ В ответе API нет 'combination'")
                return None
            
            combination = response_data['combination']
            
            # ⚡ КРИТИЧЕСКАЯ ПРОВЕРКА: structured может отсутствовать или быть None
            if not combination or 'structured' not in combination:
                print("⚠️ В combination нет 'structured'")
                return None
            
            combination_structured = combination['structured']
            
            # ⚡ КРИТИЧЕСКАЯ ПРОВЕРКА: combination_structured может быть None
            if combination_structured is None:
                print("❌ combination_structured is None")
                return None
            
            # ⚡ КРИТИЧЕСКАЯ ПРОВЕРКА: combination_structured должен быть списком
            if not isinstance(combination_structured, list):
                print(f"❌ combination_structured не список: {type(combination_structured)}")
                return None
            
            # ⚡ КРИТИЧЕСКАЯ ПРОВЕРКА: список не должен быть пустым
            if not combination_structured:
                print("❌ combination_structured пустой список")
                return None
            
            # ТОЛЬКО ТЕПЕРЬ безопасно создаем строку
            combination_string = " ".join(str(num) for num in combination_structured)
            self._save_info(str(next_draw), combination_string)
            
            print(f"✅ Получена комбинация для тиража {next_draw}: {combination_string}")
            return response_data
            
        except subprocess.TimeoutExpired:
            print("❌ Таймаут вызова API")
            return None
        except Exception as e:
            print(f"❌ Неожиданная ошибка вызова API: {e}")
            return None'''

content = content[:start] + new_method + content[end:]

with open('services/auto_learning/api_client.py', 'w') as f:
    f.write(content)

print("✅ Метод _call_api полностью переписан!")
