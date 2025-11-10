# [file name]: ml/learning/self_learning.py
"""
Система самообучения на ошибках - РЕФАКТОРИНГ ДЛЯ НОВОЙ СТРУКТУРЫ
"""

import json
import os
from typing import List, Tuple, Dict, Any
from datetime import datetime

# Импорты из новой структуры
from ml.core.data_processor import DataProcessor
from ml.features.extractor import BaseFeatureExtractor
from config.paths import DATA_DIR

class SelfLearningSystem:
    def __init__(self, results_file: str = None):
        if results_file is None:
            results_file = os.path.join(DATA_DIR, "analytics", "learning_results.json")
        self.results_file = results_file
        self.learning_data = self._load_learning_data()
   
    def _load_learning_data(self) -> Dict:
        """Загрузка данных обучения с исправлением структуры"""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"🔍 Загружены данные типа: {type(data)}")
                
                # 🔧 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Восстанавливаем правильную структуру
                if isinstance(data, list):
                    print("⚠️  Обнаружен массив данных, восстанавливаем структуру...")
                    
                    # Создаем новую правильную структуру
                    correct_structure = {
                        'predictions_accuracy': [],
                        'model_performance': {},
                        'learning_patterns': {},
                        'error_patterns': [],
                        'last_analysis': None
                    }
                    
                    for i, item in enumerate(data):
                        if isinstance(item, dict):
                            # Если это основной словарь со всей структурой (неправильно вложенный)
                            if 'predictions_accuracy' in item and isinstance(item['predictions_accuracy'], list):
                                print(f"📦 Найден основной словарь с {len(item['predictions_accuracy'])} записями")
                                # Переносим все записи точности
                                correct_structure['predictions_accuracy'].extend(item['predictions_accuracy'])
                                
                                # Переносим ошибки
                                if 'error_patterns' in item and isinstance(item['error_patterns'], list):
                                    correct_structure['error_patterns'] = item['error_patterns']
                                
                                # Переносим остальные поля
                                for key in ['model_performance', 'learning_patterns', 'last_analysis']:
                                    if key in item:
                                        correct_structure[key] = item[key]
                            
                            # Если это отдельная запись анализа
                            elif 'timestamp' in item and 'actual_group' in item:
                                print(f"📊 Добавляем запись анализа: {item.get('actual_group', 'N/A')}")
                                correct_structure['predictions_accuracy'].append(item)
                            
                            # Если это запись тиража
                            elif 'draw' in item and 'combination' in item:
                                print(f"🎯 Добавляем запись тиража: {item.get('draw', 'N/A')}")
                                # Преобразуем в формат анализа
                                analysis_entry = {
                                    'timestamp': item.get('timestamp'),
                                    'actual_group': item.get('combination', ''),
                                    'draw': item.get('draw', ''),
                                    'service_type': item.get('service_type', 'auto_learning'),
                                    'learning_success': item.get('learning_success', True),
                                    'new_predictions_count': item.get('new_predictions_count', 0)
                                }
                                
                                # Вычисляем accuracy_score из сравнения
                                if 'comparison' in item and 'matches_found' in item['comparison']:
                                    matches_count = item['comparison']['matches_found']
                                    analysis_entry['matches_count'] = matches_count
                                    analysis_entry['accuracy_score'] = matches_count / 4.0
                                
                                correct_structure['predictions_accuracy'].append(analysis_entry)
                    
                    print(f"✅ Восстановлено {len(correct_structure['predictions_accuracy'])} записей точности")
                    print(f"✅ Восстановлено {len(correct_structure['error_patterns'])} записей ошибок")
                    
                    # Сохраняем исправленную структуру
                    self.learning_data = correct_structure
                    self._save_learning_data()  # Сохраняем в правильном формате
                    print("💾 Структура данных исправлена и сохранена")
                    
                    return correct_structure
                    
                elif isinstance(data, dict):
                    print("✅ Данные уже в правильном формате")
                    return data
                else:
                    print(f"❌ Неизвестный формат данных: {type(data)}")
                    
            except Exception as e:
                print(f"⚠️  Ошибка загрузки данных обучения: {e}")
                import traceback
                traceback.print_exc()
        
        # Возвращаем структуру по умолчанию
        return {
            'predictions_accuracy': [],
            'model_performance': {},
            'learning_patterns': {},
            'error_patterns': [],
            'last_analysis': None
        }

    def get_performance_stats(self) -> Dict:
        """Получение полной статистики производительности"""
        try:
            if isinstance(self.learning_data, dict):
                accuracy_data = self.learning_data.get('predictions_accuracy', [])
                print(f"📊 Всего записей точности: {len(accuracy_data)}")
            else:
                accuracy_data = []
            
            if not accuracy_data:
                return {
                    'message': 'Нет данных для анализа',
                    'total_predictions_analyzed': 0,
                    'recent_accuracy_avg': 0,
                    'best_accuracy': 0,
                    'worst_accuracy': 0,
                    'stability_score': 0,
                    'trend': 'unknown',
                    'recommendations': ['📊 Собираем данные для анализа...']
                }
            
            # Фильтруем только записи с accuracy_score
            valid_data = [item for item in accuracy_data if isinstance(item, dict) and 'accuracy_score' in item]
            print(f"✅ Валидных записей с accuracy_score: {len(valid_data)}")
            
            if not valid_data:
                return {
                    'message': 'Недостаточно валидных данных для анализа',
                    'total_predictions_analyzed': 0,
                    'recent_accuracy_avg': 0,
                    'best_accuracy': 0,
                    'worst_accuracy': 0,
                    'stability_score': 0,
                    'trend': 'unknown',
                    'recommendations': ['🔧 Требуется проверка формата данных']
                }
            
            # Анализ последних данных (20 записей или все если меньше)
            recent_data = valid_data[-20:]
            recent_accuracy = [a.get('accuracy_score', 0) for a in recent_data]
            
            # Расширенная статистика
            accuracy_values = [a.get('accuracy_score', 0) for a in valid_data]
            
            # Анализ тренда
            trend = "stable"
            if len(recent_accuracy) >= 5:
                first_half = recent_accuracy[:len(recent_accuracy)//2]
                second_half = recent_accuracy[len(recent_accuracy)//2:]
                avg_first = sum(first_half) / len(first_half)
                avg_second = sum(second_half) / len(second_half)
                
                if avg_second > avg_first + 0.15:
                    trend = "improving"
                elif avg_second < avg_first - 0.15:
                    trend = "declining"
            
            # Стабильность (стандартное отклонение)
            if len(recent_accuracy) > 1:
                mean_accuracy = sum(recent_accuracy) / len(recent_accuracy)
                variance = sum((x - mean_accuracy) ** 2 for x in recent_accuracy) / len(recent_accuracy)
                stability_score = max(0, 1 - (variance ** 0.5))  # 1 = идеальная стабильность
            else:
                stability_score = 1.0
            
            # Распределение точности
            perfect_matches = len([a for a in accuracy_values if a == 1.0])
            good_matches = len([a for a in accuracy_values if a >= 0.5])
            poor_matches = len([a for a in accuracy_values if a < 0.25])
            
            return {
                'total_predictions_analyzed': len(valid_data),
                'recent_accuracy_avg': sum(recent_accuracy) / len(recent_accuracy),
                'best_accuracy': max(recent_accuracy) if recent_accuracy else 0,
                'worst_accuracy': min(recent_accuracy) if recent_accuracy else 0,
                'stability_score': stability_score,
                'trend': trend,
                'distribution': {
                    'perfect_matches': perfect_matches,
                    'good_matches': good_matches,
                    'poor_matches': poor_matches,
                    'total_matches': len(valid_data)
                },
                'recommendations': self.get_learning_recommendations(),
                'debug_info': {
                    'total_entries': len(accuracy_data),
                    'valid_entries': len(valid_data),
                    'recent_analyzed': len(recent_data),
                    'data_format': 'corrected'
                }
            }
            
        except Exception as e:
            print(f"❌ Ошибка в get_performance_stats: {e}")
            import traceback
            traceback.print_exc()
            return {
                'message': f'Ошибка анализа: {str(e)}',
                'total_predictions_analyzed': 0,
                'recent_accuracy_avg': 0,
                'best_accuracy': 0,
                'worst_accuracy': 0,
                'stability_score': 0,
                'trend': 'error',
                'recommendations': ['⚠️ Ошибка анализа данных']
            }
            
        except Exception as e:
            print(f"❌ Ошибка в get_performance_stats: {e}")
            import traceback
            traceback.print_exc()
            return {'message': f'Ошибка анализа: {str(e)}'}

    def get_learning_recommendations(self) -> List[str]:
        """Получение комплексных рекомендаций для улучшения"""
        recommendations = []
        
        try:
            # Получаем данные
            if isinstance(self.learning_data, dict):
                accuracy_data = self.learning_data.get('predictions_accuracy', [])
                error_patterns = self.learning_data.get('error_patterns', [])
            else:
                accuracy_data = []
                error_patterns = []
            
            # Фильтруем валидные данные
            valid_data = [item for item in accuracy_data if isinstance(item, dict) and 'accuracy_score' in item]
            
            print(f"🔍 Комплексный анализ: {len(valid_data)} записей, {len(error_patterns)} ошибок")
            
            # 1. Анализ на основе точности предсказаний
            if valid_data:
                recent_accuracy = [a['accuracy_score'] for a in valid_data[-10:]]
                all_accuracy = [a['accuracy_score'] for a in valid_data]
                
                avg_recent = sum(recent_accuracy) / len(recent_accuracy)
                avg_all = sum(all_accuracy) / len(all_accuracy)
                
                # Рекомендации по точности
                if avg_recent < 0.2:
                    recommendations.append("🚨 **Критически низкая точность** - требуется срочное переобучение")
                elif avg_recent < 0.3:
                    recommendations.append("⚠️ **Низкая точность** - рекомендуется полное переобучение модели")
                elif avg_recent < 0.5:
                    recommendations.append("📉 **Средняя точность** - добавьте разнообразные данные для обучения")
                elif avg_recent > 0.7:
                    recommendations.append("✅ **Высокая точность** - система работает стабильно")
                elif avg_recent > 0.8:
                    recommendations.append("🏆 **Отличная точность** - модель показывает выдающиеся результаты")
                
                # Анализ тренда
                if len(recent_accuracy) >= 5:
                    first_part = recent_accuracy[:len(recent_accuracy)//2]
                    second_part = recent_accuracy[len(recent_accuracy)//2:]
                    avg_first = sum(first_part) / len(first_part)
                    avg_second = sum(second_part) / len(second_part)
                    
                    improvement = avg_second - avg_first
                    if improvement > 0.1:
                        recommendations.append("📈 **Положительная динамика** - точность улучшается, продолжайте текущую стратегию")
                    elif improvement < -0.1:
                        recommendations.append("📉 **Отрицательная динамика** - проверьте качество новых данных")
                
                # Стабильность предсказаний
                accuracy_std = (sum((x - avg_recent) ** 2 for x in recent_accuracy) / len(recent_accuracy)) ** 0.5
                if accuracy_std > 0.3:
                    recommendations.append("🎭 **Нестабильные результаты** - модель требует стабилизации")
                elif accuracy_std < 0.1:
                    recommendations.append("⚖️ **Стабильная работа** - модель показывает consistent результаты")
            
            # 2. Анализ паттернов ошибок
            if error_patterns:
                recent_errors = error_patterns[-20:]
                
                # Анализ частых ошибок
                missed_numbers = {}
                false_numbers = {}
                
                for error in recent_errors:
                    for num in error.get('missed_numbers', []):
                        missed_numbers[num] = missed_numbers.get(num, 0) + 1
                    for num in error.get('false_numbers', []):
                        false_numbers[num] = false_numbers.get(num, 0) + 1
                
                # Рекомендации по числам
                if missed_numbers:
                    most_missed = max(missed_numbers.items(), key=lambda x: x[1])
                    if most_missed[1] >= 3:
                        recommendations.append(f"🔍 **Число {most_missed[0]} часто пропускается** - увеличьте его вес в features")
                
                if false_numbers:
                    most_false = max(false_numbers.items(), key=lambda x: x[1])
                    if most_false[1] >= 3:
                        recommendations.append(f"🎯 **Число {most_false[0]} часто ложно предсказывается** - уменьшите его приоритет")
                
                # Частота серьезных ошибок
                severe_errors = [e for e in recent_errors if e.get('accuracy', 1) < 0.25]
                if len(severe_errors) > len(recent_errors) * 0.6:
                    recommendations.append("🔄 **Много серьезных ошибок** - пересмотрите feature engineering")
            
            # 3. Анализ распределения успешности
            if valid_data:
                accuracy_values = [a['accuracy_score'] for a in valid_data]
                perfect_count = len([a for a in accuracy_values if a == 1.0])
                good_count = len([a for a in accuracy_values if a >= 0.5])
                poor_count = len([a for a in accuracy_values if a < 0.25])
                
                total_count = len(valid_data)
                
                if perfect_count > 0:
                    perfect_percent = (perfect_count / total_count) * 100
                    recommendations.append(f"⭐ **{perfect_count} идеальных предсказаний** ({perfect_percent:.1f}%)")
                
                if poor_count > total_count * 0.4:
                    recommendations.append("🔧 **Много промахов** - проверьте preprocessing данных")
                
                success_rate = (good_count / total_count) * 100
                if success_rate > 60:
                    recommendations.append("💪 **Хороший success rate** - модель эффективна")
                elif success_rate < 30:
                    recommendations.append("🎯 **Низкий success rate** - рассмотрите смену алгоритма")
            
            # 4. Рекомендации по объему и качеству данных
            total_entries = len(valid_data)
            if total_entries < 10:
                recommendations.append("📈 **Мало данных** - продолжайте сбор статистики для надежного анализа")
            elif total_entries < 50:
                recommendations.append("📊 **Достаточно данных** - можно проводить глубокий анализ паттернов")
            elif total_entries > 100:
                recommendations.append("💾 **Большая база данных** - надежные статистические выводы")
            
            # 5. Общие рекомендации если нет специфических
            if not recommendations:
                if valid_data:
                    recent_avg = sum([a['accuracy_score'] for a in valid_data[-5:]]) / min(5, len(valid_data))
                    if recent_avg < 0.4:
                        recommendations.append("🔄 **Требуется оптимизация** - рассмотрите fine-tuning модели")
                    else:
                        recommendations.append("⚡ **Продолжайте обучение** - текущая стратегия эффективна")
                else:
                    recommendations.append("📝 **Начальная фаза** - рекомендации появятся после анализа нескольких тиражей")
            
            # 6. Рекомендации по частоте обучения
            if len(valid_data) > 20:
                recent_timestamps = [a.get('timestamp') for a in valid_data[-5:] if a.get('timestamp')]
                if recent_timestamps:
                    try:
                        from datetime import datetime
                        timestamps = [datetime.fromisoformat(ts) for ts in recent_timestamps if ts]
                        if timestamps:
                            time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]
                            if time_diffs:
                                avg_interval = sum(time_diffs) / len(time_diffs)
                                if avg_interval > 86400:  # более суток
                                    recommendations.append("⏰ **Редкое обучение** - увеличьте частоту дообучения")
                                elif avg_interval < 3600:  # менее часа
                                    recommendations.append("⚡ **Частое обучение** - хороший темп обновления модели")
                    except:
                        pass
        
        except Exception as e:
            print(f"❌ Ошибка в get_learning_recommendations: {e}")
            recommendations = ["⚠️ **Временная ошибка анализа** - рекомендации будут обновлены после следующего тиража"]
        
        # Ограничиваем для читабельности и выбираем наиболее важные
        if len(recommendations) > 6:
            # Приоритет: критические -> точность -> ошибки -> общие
            critical = [r for r in recommendations if '🚨' in r or '⚠️' in r]
            accuracy = [r for r in recommendations if '📈' in r or '📉' in r or '✅' in r]
            errors = [r for r in recommendations if '🔍' in r or '🎯' in r]
            general = [r for r in recommendations if r not in critical + accuracy + errors]
            
            recommendations = critical + accuracy[:2] + errors[:2] + general[:1]
        
        return recommendations[:6]  # Максимум 6 рекомендаций
       
    def analyze_prediction_accuracy(self, actual_group: str) -> Dict:
        """Анализ точности последних предсказаний"""
        try:
            from ml.utils.data_utils import compare_groups, load_predictions
            
            actual_numbers = [int(x) for x in actual_group.strip().split()]
            actual_tuple = tuple(actual_numbers)
            
            previous_predictions = load_predictions()
            if not previous_predictions:
                return None
            
            best_match = None
            best_score = 0
            best_prediction = None
            
            # Ищем лучшее совпадение среди предсказаний
            for pred_group, score in previous_predictions:
                comparison = compare_groups(pred_group, actual_tuple)
                total_matches = comparison['total_matches']
                
                if total_matches > best_score:
                    best_score = total_matches
                    best_match = comparison
                    best_prediction = pred_group
            
            # Сохраняем результат анализа
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'actual_group': actual_group,
                'best_prediction': best_prediction,
                'matches_count': best_score,
                'comparison_details': best_match,
                'accuracy_score': best_score / 4.0  # Нормализованная точность
            }
            
            # ⚡ ИСПРАВЛЕНИЕ: Проверяем существование ключа перед добавлением
            if 'predictions_accuracy' not in self.learning_data:
                self.learning_data['predictions_accuracy'] = []
                
            self.learning_data['predictions_accuracy'].append(analysis_result)
            self._save_learning_data()
            
            # Анализируем паттерны ошибок
            self._analyze_error_patterns(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Ошибка анализа точности: {e}")
            return None
    
    def _analyze_error_patterns(self, analysis_result: Dict):
        """Анализ паттернов ошибок для улучшения предсказаний"""
        accuracy = analysis_result['accuracy_score']
        
        if accuracy < 0.5:  # Низкая точность
            actual_group = analysis_result['actual_group']
            predicted_group = analysis_result['best_prediction']
            
            if predicted_group:
                # Анализируем, какие числа были пропущены
                actual_numbers = [int(x) for x in actual_group.split()]
                predicted_numbers = list(predicted_group)
                
                missed_numbers = set(actual_numbers) - set(predicted_numbers)
                false_numbers = set(predicted_numbers) - set(actual_numbers)
                
                # Сохраняем паттерны ошибок
                if 'error_patterns' not in self.learning_data:
                    self.learning_data['error_patterns'] = []
                
                error_pattern = {
                    'timestamp': analysis_result['timestamp'],
                    'missed_numbers': list(missed_numbers),
                    'false_numbers': list(false_numbers),
                    'accuracy': accuracy
                }
                
                self.learning_data['error_patterns'].append(error_pattern)

    def adjust_ensemble_weights(self, ensemble_predictor) -> bool:
        """Корректировка весов ансамбля на основе производительности"""
        try:
            accuracy_data = self.learning_data.get('predictions_accuracy', [])
            if len(accuracy_data) < 5:  # Нужно достаточно данных
                return False
            
            # Анализ производительности разных стратегий
            recent_accuracy = accuracy_data[-10:]
            accuracy_scores = [a['accuracy_score'] for a in recent_accuracy if 'accuracy_score' in a]
            
            if not accuracy_scores:
                return False
                
            avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
            
            if avg_accuracy < 0.4:
                # Увеличиваем вес нейросети
                if hasattr(ensemble_predictor, 'weights') and 'neural' in ensemble_predictor.weights:
                    ensemble_predictor.weights['neural'] = min(0.5, ensemble_predictor.weights['neural'] + 0.1)
                    if 'frequency' in ensemble_predictor.weights:
                        ensemble_predictor.weights['frequency'] = max(0.2, ensemble_predictor.weights['frequency'] - 0.05)
                    print("🔧 Скорректированы веса ансамбля в пользу нейросети")
                    return True
                
            return False
            
        except Exception as e:
            print(f"❌ Ошибка корректировки весов: {e}")
            return False
    
    def _save_learning_data(self):
        """Сохранение данных обучения"""
        try:
            os.makedirs(os.path.dirname(self.results_file), exist_ok=True)
            self.learning_data['last_analysis'] = datetime.now().isoformat()
            
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения данных обучения: {e}")

    def reset_learning_data(self):
        """Сброс данных обучения"""
        self.learning_data = {
            'predictions_accuracy': [],
            'model_performance': {},
            'learning_patterns': {},
            'error_patterns': [],
            'last_analysis': None
        }
        self._save_learning_data()
        print("✅ Данные обучения сброшены")

# Функции для обратной совместимости
def create_self_learning_system():
    """Создание системы самообучения (для обратной совместимости)"""
    return SelfLearningSystem()
