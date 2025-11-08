import json
import subprocess
import traceback

def test_api_call():
    print("🔍 ТЕСТИРУЕМ API ВЫЗОВ...")
    
    url = "https://www.stoloto.ru/p/api/mobile/api/v35/service/games/details/draw-combination?game=dvazhdydva&draw=309053"
    
    try:
        print(f"📡 URL: {url}")
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
        ], capture_output=True, text=True, timeout=35)
        
        print(f"✅ Curl завершен с кодом: {result.returncode}")
        print(f"📄 Длина ответа: {len(result.stdout)} символов")
        
        if result.returncode == 0:
            print("🔍 Парсим JSON...")
            response_data = json.loads(result.stdout)
            print(f"📊 Структура ответа: {list(response_data.keys())}")
            
            if 'combination' in response_data:
                combination = response_data['combination']
                print(f"🎯 Combination: {combination}")
                if 'structured' in combination:
                    structured = combination['structured']
                    print(f"🔢 Structured: {structured} (тип: {type(structured)})")
                else:
                    print("❌ Нет structured в combination")
            else:
                print("❌ Нет combination в ответе")
        else:
            print(f"❌ Curl ошибка: {result.stderr}")
            
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        print(f"📄 Ответ: {result.stdout[:200]}...")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

test_api_call()
