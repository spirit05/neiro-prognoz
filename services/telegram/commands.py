#/opt/model/services/telegram/commands.py
"""
Команды Telegram бота - используем только WorkflowManager через MLDispatcher
"""

import logging
import json
from typing import Dict, Callable, Any, List
from datetime import datetime

from .ml_dispatcher import MLDispatcher
from .security import SecurityManager

logger = logging.getLogger('telegram_bot.commands')


class CommandHandler:
    """Обработчик команд Telegram бота"""
    
    def __init__(self, ml_dispatcher: MLDispatcher, security_manager: SecurityManager):
        self.ml_dispatcher = ml_dispatcher
        self.security_manager = security_manager
        
        # Регистрация команд
        self.commands: Dict[str, Callable] = {
            '/start': self.handle_start,
            '/help': self.handle_help,
            '/status': self.handle_status,
            '/predictions': self.handle_predictions,
            '/data': self.handle_data,
            '/train': self.handle_train,
            '/results': self.handle_results,
            '/add': self.handle_add_group,
            '/version': self.handle_version,
            '/system': self.handle_system,
            '/retrain': self.handle_retrain,
            '/generate': self.handle_generate_predictions,
            '/logs': self.handle_logs,
        }
    
    def handle_command(self, text: str, chat_id: int) -> str:
        """Обработка команды"""
        try:
            # Разделяем команду и аргументы
            parts = text.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            # Проверяем, есть ли такая команда
            if command in self.commands:
                logger.info(f"🔧 Выполнение команды: {command} от {chat_id}")
                return self.commands[command](chat_id, args)
            else:
                # Если команда начинается с "/", но не найдена
                if command.startswith('/'):
                    return f"❌ Неизвестная команда: {command}\nИспользуйте /help для списка команд"
                else:
                    return "❌ Сообщение не является командой. Используйте /help для списка команд"
                    
        except Exception as e:
            logger.error(f"❌ Ошибка обработки команды '{text}': {e}")
            return f"❌ Внутренняя ошибка при обработке команды: {str(e)[:100]}"
    
    def handle_start(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /start"""
        return (
            "🤖 <b>AI Prediction System - Telegram Bot</b>\n\n"
            "Добро пожаловать в систему прогнозирования на основе новой модульной архитектуры!\n\n"
            "📋 <b>Доступные команды:</b>\n"
            "• /start - Начало работы\n"
            "• /help - Справка по командам\n"
            "• /status - Полный статус системы\n"
            "• /predictions - Последние прогнозы\n"
            "• /data - Информация о датасете\n"
            "• /train - Обучение модели\n"
            "• /results - Аналитика обучения\n"
            "• /add - Добавить группу вручную\n"
            "• /version - Версия системы\n\n"
            "🚧 <b>Примечание:</b> Управление автосервисом будет доступно после Этапа 12 миграции."
        )
    
    def handle_help(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /help"""
        return (
            "🆘 <b>Помощь по командам Telegram бота</b>\n\n"
            "<b>📊 Информационные команды:</b>\n"
            "/status - Полный статус ML системы\n"
            "/data - Информация о датасете\n"
            "/results - Аналитика обучения\n"
            "/version - Версия системы\n\n"
            "<b>🎯 Команды управления:</b>\n"
            "/train - Запустить полное обучение модели\n"
            "/retrain - Переобучить модель\n"
            "/generate - Сгенерировать новые прогнозы\n"
            "/add [числа] - Добавить группу вручную (например: /add 1 2 3 4)\n\n"
            "<b>🔮 Команды прогнозов:</b>\n"
            "/predictions - Показать сохраненные прогнозы\n\n"
            "<b>⚙️ Системные команды:</b>\n"
            "/logs - Просмотр системных логов\n"
            "/system - Детальная информация о системе\n\n"
            "🚧 <i>Управление автосервисом будет добавлено в Этапе 12</i>"
        )
    
    def handle_status(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /status - полный статус системы - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            status = self.ml_dispatcher.get_system_status()
            
            if not status.get('is_initialized'):
                return "❌ ML система не инициализирована"
            
            # 🔧 ПРАВИЛЬНОЕ ФОРМАТИРОВАНИЕ
            response = "📊 <b>СТАТУС ML СИСТЕМЫ</b>\n\n"
            
            # Основная информация
            response += f"🏗 <b>Архитектура:</b> {status.get('architecture', 'НЕИЗВЕСТНО')}\n"
            response += f"🤖 <b>Тип модели:</b> {status.get('model_type', 'НЕИЗВЕСТНО')}\n"
            
            # Статус модели
            if status.get('model_loaded'):
                response += f"📦 <b>Модель:</b> ✅ Загружена\n"
                response += f"🧠 <b>Обучена:</b> {'✅ Да' if status.get('is_trained') else '❌ Нет'}\n"
            else:
                response += f"📦 <b>Модель:</b> ❌ Не загружена\n"
            
            # Информация о данных
            dataset_size = status.get('dataset_size', 0)
            response += f"📁 <b>Датасет:</b> {dataset_size} групп\n"
            response += f"📈 <b>Достаточно данных:</b> {'✅ Да' if status.get('has_sufficient_data') else '❌ Нет (нужно минимум 50)'}\n"
            
            # Прогнозы
            predictions_count = status.get('predictions_count', 0)
            response += f"🔮 <b>Прогнозов сохранено:</b> {predictions_count}\n\n"
            
            # Зарегистрированные модели
            models = status.get('registered_models', [])
            if models:
                response += f"📋 <b>Зарегистрированные модели:</b>\n"
                for model in models:
                    response += f"  • {model}\n"
            
            # Рекомендации
            if dataset_size < 50:
                needed = 50 - dataset_size
                response += f"\n📝 <b>Рекомендация:</b> Добавьте еще {needed} групп для обучения модели\n"
                response += f"   Используйте команду: /add 1 2 3 4"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса: {e}")
            return f"❌ Ошибка получения статуса: {str(e)[:100]}"
    
    def handle_predictions(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /predictions - показать прогнозы"""
        try:
            result = self.ml_dispatcher.get_predictions()
            
            if not result.get('success'):
                return f"❌ {result.get('message', 'Неизвестная ошибка')}"
            
            predictions = result.get('predictions', [])
            
            if not predictions:
                return "📭 Нет сохраненных прогнозов"
            
            response = f"🔮 <b>ПОСЛЕДНИЕ ПРОГНОЗЫ</b> ({len(predictions)} из {result.get('total_count', 0)})\n\n"
            
            for i, pred in enumerate(predictions[:5], 1):  # Показываем первые 5
                group = pred.get('group', [])
                score = pred.get('score', 0)
                timestamp = pred.get('timestamp', '')
                
                # Форматируем группу
                group_str = ' '.join(str(x) for x in group[:4]) if len(group) >= 4 else 'Некорректная группа'
                
                # Форматируем уверенность
                confidence = "🟢 Высокая" if score > 0.3 else "🟡 Средняя" if score > 0.1 else "🔴 Низкая"
                
                response += f"{i}. {group_str}\n"
                response += f"   Уверенность: {score:.3f} ({confidence})\n"
                
                if timestamp:
                    # Пытаемся парсить timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        response += f"   Время: {dt.strftime('%H:%M')}\n"
                    except:
                        pass
                # 🔧 ИСПРАВЛЕНИЕ: Если timestamp отсутствует, не добавляем строку
                
                response += "\n"
            
            if len(predictions) > 5:
                response += f"📋 ... и еще {len(predictions) - 5} прогнозов\n"
            
            if result.get('last_updated'):
                try:
                    dt = datetime.fromisoformat(result['last_updated'].replace('Z', '+00:00'))
                    response += f"\n🕒 <i>Обновлено: {dt.strftime('%d.%m.%Y %H:%M')}</i>"
                except:
                    pass
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения прогнозов: {e}")
            return f"❌ Ошибка получения прогнозов: {str(e)[:100]}"
    
    def handle_data(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /data - информация о датасете"""
        try:
            result = self.ml_dispatcher.get_dataset_info()
            
            if not result.get('success'):
                return f"❌ {result.get('message', 'Неизвестная ошибка')}"
            
            response = "📁 <b>ИНФОРМАЦИЯ О ДАННЫХ</b>\n\n"
            response += f"📊 <b>Всего групп:</b> {result.get('dataset_size', 0)}\n"
            response += f"✅ <b>Валидных групп:</b> {result.get('valid_groups', 0)}\n"
            response += f"📈 <b>Достаточно данных:</b> {'✅ Да' if result.get('has_sufficient_data') else '❌ Нет'}\n"
            
            # Рекомендации
            dataset_size = result.get('dataset_size', 0)
            if dataset_size < 50:
                response += f"\n⚠️ <b>Рекомендация:</b> Добавьте еще {50 - dataset_size} групп для качественного обучения\n"
                response += "   Используйте команду /add или веб-интерфейс"
            elif dataset_size < 100:
                response += f"\n✅ <b>Достаточно для обучения:</b> {dataset_size}/50 групп\n"
                response += "   Можете запускать обучение командой /train"
            else:
                response += f"\n🎯 <b>Отлично!</b> {dataset_size} групп - можно обучать продвинутые модели\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о данных: {e}")
            return f"❌ Ошибка получения информации о данных: {str(e)[:100]}"
    
    def handle_train(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /train - запуск обучения"""
        try:
            # Проверяем наличие данных
            data_result = self.ml_dispatcher.get_dataset_info()
            if not data_result.get('has_sufficient_data', False):
                return (
                    "❌ <b>НЕДОСТАТОЧНО ДАННЫХ</b>\n\n"
                    f"Для обучения нужно минимум 50 групп, а у вас только {data_result.get('dataset_size', 0)}.\n\n"
                    "📝 <b>Что делать:</b>\n"
                    "1. Добавьте группы через команду /add\n"
                    "2. Или используйте веб-интерфейс для добавления\n"
                    "3. Или дождитесь автосервиса (Этап 12)"
                )
            
            # Запускаем обучение
            response = "🔄 <b>ЗАПУСК ОБУЧЕНИЯ МОДЕЛИ</b>\n\n"
            response += "Система начала обучение. Это может занять несколько минут...\n\n"
            response += "⏳ <i>Ожидайте завершения...</i>"
            
            # Отправляем сообщение о начале обучения
            # (реальный запуск обучения будет асинхронным)
            
            # Запускаем обучение в отдельном потоке или синхронно
            result = self.ml_dispatcher.run_full_training()
            
            if result.get('success'):
                execution_time = result.get('execution_time', 0)
                message = result.get('message', 'Обучение завершено')
                
                response = f"✅ <b>ОБУЧЕНИЕ ЗАВЕРШЕНО</b>\n\n"
                response += f"{message}\n"
                response += f"⏱ Время выполнения: {execution_time:.1f} секунд\n\n"
                
                # Дополнительная информация из data
                data = result.get('data', {})
                if data:
                    models_trained = data.get('models_trained', 0)
                    predictions_generated = data.get('predictions_generated', 0)
                    
                    response += f"🤖 Обучено моделей: {models_trained}\n"
                    response += f"🔮 Сгенерировано прогнозов: {predictions_generated}\n"
                
                response += "\n📊 Используйте команду /results для просмотра аналитики"
                
            else:
                response = f"❌ <b>ОШИБКА ОБУЧЕНИЯ</b>\n\n"
                response += f"{result.get('message', 'Неизвестная ошибка')}\n\n"
                response += "🔧 Проверьте логи системы командой /logs"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска обучения: {e}")
            return f"❌ Ошибка запуска обучения: {str(e)[:100]}"
    
    def handle_results(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /results - аналитика обучения"""
        try:
            result = self.ml_dispatcher.get_learning_analytics()
            
            if not result.get('success'):
                return f"❌ {result.get('message', 'Неизвестная ошибка')}"
            
            data = result.get('data', {})
            
            if not data:
                return "📭 Нет данных аналитики обучения"
            
            response = "📈 <b>АНАЛИТИКА ОБУЧЕНИЯ</b>\n\n"
            
            # Основные метрики
            total_sessions = data.get('total_training_sessions', 0)
            recent_accuracy = data.get('recent_accuracy', 0)
            best_accuracy = data.get('best_accuracy', 0)
            worst_accuracy = data.get('worst_accuracy', 0)
            avg_training_time = data.get('average_training_time', 0)
            
            response += f"📊 <b>Сессий обучения:</b> {total_sessions}\n"
            response += f"🎯 <b>Последняя точность:</b> {recent_accuracy*100:.1f}%\n"
            response += f"🏆 <b>Лучшая точность:</b> {best_accuracy*100:.1f}%\n"
            response += f"📉 <b>Худшая точность:</b> {worst_accuracy*100:.1f}%\n"
            response += f"⏱ <b>Среднее время обучения:</b> {avg_training_time:.1f}с\n\n"
            
            # Тренд точности
            trend = data.get('prediction_accuracy_trend', [])
            if trend and len(trend) > 1:
                response += f"📈 <b>Тренд точности:</b>\n"
                for i, acc in enumerate(trend[-5:]):  # Последние 5 значений
                    response += f"  Сессия {len(trend)-4+i if len(trend)>5 else i+1}: {acc*100:.1f}%\n"
            
            # Кривые обучения
            learning_curves = data.get('learning_curves', {})
            if learning_curves:
                train_loss = learning_curves.get('training_loss', [])
                val_loss = learning_curves.get('validation_loss', [])
                
                if train_loss:
                    response += f"\n📉 <b>Последний loss обучения:</b> {train_loss[-1]:.4f}\n"
                if val_loss:
                    response += f"📉 <b>Последний loss валидации:</b> {val_loss[-1]:.4f}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения аналитики: {e}")
            return f"❌ Ошибка получения аналитики: {str(e)[:100]}"
    
    def handle_add_group(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /add - добавление группы вручную"""
        try:
            if not args:
                return (
                    "❌ <b>НЕПРАВИЛЬНЫЙ ФОРМАТ</b>\n\n"
                    "📝 <b>Использование:</b>\n"
                    "/add [число1] [число2] [число3] [число4]\n\n"
                    "🔢 <b>Пример:</b>\n"
                    "/add 1 2 3 4\n"
                    "/add 10 15 20 25\n\n"
                    "⚠️ <b>Ограничения:</b>\n"
                    "• Числа от 1 до 26\n"
                    "• Ровно 4 числа через пробел"
                )
            
            # Валидация группы
            group = self.security_manager.validate_group_input(args)
            
            if not group:
                return (
                    "❌ <b>НЕВАЛИДНАЯ ГРУППА</b>\n\n"
                    "Группа должна содержать 4 числа от 1 до 26.\n\n"
                    "📝 <b>Примеры валидных групп:</b>\n"
                    "• 1 2 3 4\n"
                    "• 10 15 20 25\n"
                    "• 5 12 18 24\n\n"
                    "🔄 <b>Попробуйте снова:</b>\n"
                    "/add [4 числа через пробел]"
                )
            
            # Добавляем группу
            response = f"🔄 <b>ДОБАВЛЕНИЕ ГРУППЫ</b>\n\n"
            response += f"Группа: {' '.join(str(x) for x in group)}\n\n"
            response += "Добавляю группу в датасет..."
            
            result = self.ml_dispatcher.add_single_group(group)
            
            if result.get('success'):
                execution_time = result.get('execution_time', 0)
                message = result.get('message', 'Группа добавлена')
                
                response = f"✅ <b>ГРУППА ДОБАВЛЕНА</b>\n\n"
                response += f"{message}\n"
                response += f"⏱ Время выполнения: {execution_time:.1f} секунд\n\n"
                
                # Дополнительная информация
                data = result.get('data', {})
                if data:
                    group_added = data.get('group_added', '')
                    predictions_generated = data.get('predictions_generated', 0)
                    
                    if group_added:
                        response += f"📝 Добавлена группа: {group_added}\n"
                    if predictions_generated:
                        response += f"🔮 Сгенерировано прогнозов: {predictions_generated}\n"
                
                # Проверяем, достаточно ли теперь данных для обучения
                data_result = self.ml_dispatcher.get_dataset_info()
                dataset_size = data_result.get('dataset_size', 0)
                
                if dataset_size >= 50:
                    response += f"\n🎯 <b>Теперь достаточно данных для обучения!</b>\n"
                    response += f"Используйте команду /train для обучения модели"
                else:
                    needed = 50 - dataset_size
                    response += f"\n📊 <b>Всего групп:</b> {dataset_size}\n"
                    response += f"📈 <b>Нужно еще:</b> {needed} групп для обучения"
                
            else:
                response = f"❌ <b>ОШИБКА ДОБАВЛЕНИЯ</b>\n\n"
                response += f"{result.get('message', 'Неизвестная ошибка')}"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка добавления группы: {e}")
            return f"❌ Ошибка добавления группы: {str(e)[:100]}"
    
    def handle_version(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /version - версия системы"""
        try:
            status = self.ml_dispatcher.get_system_status()
            
            response = "⚙️ <b>ВЕРСИЯ СИСТЕМЫ</b>\n\n"
            response += f"🏗 <b>Архитектура:</b> НОВАЯ МОДУЛЬНАЯ (Этап 10+)\n"
            response += f"🤖 <b>Тип модели:</b> УСИЛЕННАЯ НЕЙРОСЕТЬ\n"
            response += f"📅 <b>Этап миграции:</b> 11/14 (Telegram бот)\n\n"
            response += "📋 <b>Основные компоненты:</b>\n"
            response += "• MLOrchestrator с фасадом\n"
            response += "• WorkflowManager для всех операций\n"
            response += "• Модульные менеджеры (Model, Data, Workflow)\n"
            response += "• Интеграция с веб-интерфейсом\n\n"
            response += "🚀 <b>Следующий этап:</b> 12 - Миграция автосервиса"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения версии: {e}")
            return "⚙️ <b>ВЕРСИЯ СИСТЕМЫ</b>\n\nНовая модульная архитектура (Этап 11)"
    
    def handle_system(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /system - детальная информация"""
        try:
            status = self.ml_dispatcher.get_system_status()
            
            response = "🖥 <b>ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О СИСТЕМЕ</b>\n\n"
            
            # Инициализация
            response += f"📡 <b>Инициализация:</b> {'✅ Выполнена' if status.get('is_initialized') else '❌ Не выполнена'}\n"
            response += f"🧠 <b>Модель обучена:</b> {'✅ Да' if status.get('is_trained') else '❌ Нет'}\n\n"
            
            # Данные
            dataset_size = status.get('dataset_size', 0)
            response += f"📊 <b>Данные:</b>\n"
            response += f"  • Групп в датасете: {dataset_size}\n"
            response += f"  • Достаточно для обучения: {'✅ Да' if dataset_size >= 50 else f'❌ Нет (нужно {50-dataset_size} еще)'}\n\n"
            
            # Модели
            models = status.get('registered_models', [])
            response += f"🤖 <b>Зарегистрированные модели:</b> {len(models)}\n"
            for model in models:
                response += f"  • {model}\n"
            
            # Прогнозы
            predictions_count = status.get('predictions_count', 0)
            response += f"\n🔮 <b>Прогнозы:</b> {predictions_count} сохранено\n"
            
            # Системный обзор
            overview = status.get('system_overview', {})
            if overview:
                response += f"\n📈 <b>Системный обзор:</b>\n"
                response += f"  Статус системы: {overview.get('system_status', 'unknown')}\n"
                response += f"  Статус модели: {overview.get('model_status', 'unknown')}\n"
                response += f"  Статус данных: {overview.get('data_status', 'unknown')}\n"
                
                last_training = overview.get('last_training')
                if last_training:
                    response += f"  Последнее обучение: {last_training[:10] if len(last_training) > 10 else last_training}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения системной информации: {e}")
            return f"❌ Ошибка получения системной информации: {str(e)[:100]}"
    
    def handle_retrain(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /retrain - переобучение (синоним /train)"""
        return self.handle_train(chat_id, "force")
    
    def handle_generate_predictions(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /generate - генерация новых прогнозов"""
        try:
            # Проверяем, обучена ли модель
            status = self.ml_dispatcher.get_system_status()
            if not status.get('is_trained'):
                return (
                    "❌ <b>МОДЕЛЬ НЕ ОБУЧЕНА</b>\n\n"
                    "Сначала обучите модель командой /train\n\n"
                    "📝 <b>Проверьте:</b>\n"
                    "1. Достаточно ли данных? /data\n"
                    "2. Обучена ли модель? /status\n"
                    "3. Если данных мало, добавьте группы /add"
                )
            
            # Генерируем прогнозы
            result = self.ml_dispatcher.generate_predictions()
            
            if result.get('success'):
                execution_time = result.get('execution_time', 0)
                message = result.get('message', 'Прогнозы сгенерированы')
                
                response = f"✅ <b>ПРОГНОЗЫ СГЕНЕРИРОВАНЫ</b>\n\n"
                response += f"{message}\n"
                response += f"⏱ Время выполнения: {execution_time:.1f} секунд\n\n"
                
                # Дополнительная информация
                data = result.get('data', {})
                if data:
                    predictions_generated = data.get('predictions_generated', 0)
                    models_used = data.get('models_used', [])
                    
                    response += f"🔮 Сгенерировано прогнозов: {predictions_generated}\n"
                    if models_used:
                        response += f"🤖 Использованные модели: {', '.join(models_used)}\n"
                
                response += "\n📋 Используйте команду /predictions для просмотра"
                
            else:
                response = f"❌ <b>ОШИБКА ГЕНЕРАЦИИ</b>\n\n"
                response += f"{result.get('message', 'Неизвестная ошибка')}"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации прогнозов: {e}")
            return f"❌ Ошибка генерации прогнозов: {str(e)[:100]}"
    
    def handle_logs(self, chat_id: int, args: str = "") -> str:
        """Обработчик команды /logs - информация о логах"""
        return (
            "📋 <b>СИСТЕМНЫЕ ЛОГИ</b>\n\n"
            "Логи системы находятся в следующих файлах:\n\n"
            "📁 <b>Основные логи:</b>\n"
            "/opt/model/logs/ - директория с логами\n\n"
            "🔧 <b>Для просмотра логов:</b>\n"
            "1. Подключитесь к серверу по SSH\n"
            "2. Перейдите в директорию /opt/model/\n"
            "3. Используйте команды:\n"
            "   • `tail -f logs/app.log` - логи приложения\n"
            "   • `tail -f logs/telegram_bot.log` - логи бота\n"
            "   • `cat logs/error.log` - ошибки\n\n"
            "⚠️ <i>Прямой доступ к логам через Telegram не реализован из соображений безопасности</i>"
        )
