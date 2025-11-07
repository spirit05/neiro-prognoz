"""
Обработчики команд Telegram бота
"""

import json
import logging
import subprocess
from typing import Dict, Callable
from config.paths import TELEGRAM_CONFIG_FILE
from services.auto_learning.service import AutoLearningService
from ml.learning.self_learning import SelfLearningSystem
from ml.utils.data_utils import load_predictions

logger = logging.getLogger('telegram_bot')

class CommandHandler:
    """Обработчик команд Telegram бота"""
    
    def __init__(self, auto_service: AutoLearningService = None):
        self.auto_service = auto_service
        self.commands: Dict[str, Callable] = {
            '/start': self.handle_start,
            '/status': self.handle_status,
            '/predictions': self.handle_predictions,
            '/autoprognoz': self.handle_autoprognoz,
            '/help': self.handle_help,
            '/restart': self.handle_restart,
            '/stop': self.handle_stop,
            '/run_once': self.handle_run_once,
            '/service_status': self.handle_service_status,
        }
    
    def handle_command(self, command: str, chat_id: int) -> str:
        """Обработка команды"""
        handler = self.commands.get(command)
        if handler:
            return handler(chat_id)
        else:
            return "❌ Неизвестная команда. Используйте /help"
    
    def handle_start(self, chat_id: int) -> str:
        """Обработчик команды /start"""
        return (
            "🤖 <b>AI Prediction System активирован!</b>\n\n"
            "Доступные команды:\n"
            "/status - статус системы\n" 
            "/predictions - последние прогнозы\n"
            "/autoprognoz - включить/выключить авто-прогнозы\n"
            "/service_status - статус автосервиса\n"
            "/restart - перезапуск сервиса после ошибок\n"
            "/run_once - единичный запуск\n"
            "/stop - остановка сервиса\n"
            "/help - помощь"
        )
    
    def handle_status(self, chat_id: int) -> str:
        """Обработчик команды /status"""
        from .utils import SystemChecker
        checker = SystemChecker(self.auto_service)
        return checker.get_system_status()
    
    def handle_predictions(self, chat_id: int) -> str:
        """Обработчик команды /predictions"""
        try:
            predictions = load_predictions()
            
            if predictions:
                message = "🔮 <b>ПОСЛЕДНИЕ ПРОГНОЗЫ</b>\n\n"
                for i, (group, score) in enumerate(predictions[:4], 1):
                    confidence = "🟢" if score > 0.02 else "🟡" if score > 0.01 else "🔴"
                    message += f"{i}. {group[0]} {group[1]} {group[2]} {group[3]}\n"
                    message += f"   Уверенность: {score:.4f} {confidence}\n\n"
                return message
            else:
                return "📝 Прогнозы еще не сгенерированы"
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения прогнозов: {e}")
            return f"❌ Ошибка получения прогнозов: {e}"
    
    def handle_autoprognoz(self, chat_id: int) -> str:
        """Обработчик команды /autoprognoz"""
        try:
            with open(TELEGRAM_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            current_state = config.get('notifications', {}).get('predictions', False)
            new_state = not current_state
            
            if 'notifications' not in config:
                config['notifications'] = {}
            config['notifications']['predictions'] = new_state
            
            with open(TELEGRAM_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            status = "ВКЛЮЧЕНЫ" if new_state else "ВЫКЛЮЧЕНЫ"
            message = f"🔔 Авто-прогнозы **{status}**\n\n"
            message += "Теперь после каждого дообучения новые прогнозы будут автоматически отправляться в этот чат." if new_state else "Автоматическая отправка прогнозов отключена."
            
            logger.info(f"🔧 Авто-прогнозы {'включены' if new_state else 'выключены'} для чата {chat_id}")
            return message
            
        except Exception as e:
            logger.error(f"❌ Ошибка переключения авто-прогнозов: {e}")
            return f"❌ Ошибка: {e}"
    
    def handle_help(self, chat_id: int) -> str:
        """Обработчик команды /help"""
        return (
            "🆘 <b>Помощь по командам:</b>\n\n"
            "/status - полный статус системы\n"
            "/predictions - последние 4 прогноза\n" 
            "/autoprognoz - включить/выключить авто-прогнозы\n"
            "/service_status - детальный статус автосервиса\n"
            "/restart - перезапуск после ошибок API\n"
            "/run_once - запустить одну итерацию\n"
            "/stop - остановить автосервис\n"
            "/help - эта справка"
        )
    
    def handle_restart(self, chat_id: int) -> str:
        """Обработчик команды /restart"""
        if not self.auto_service:
            return "❌ Автосервис не инициализирован"
        
        try:
            if self.auto_service.manual_restart():
                logger.info(f"🔧 Автосервис перезапущен через Telegram командой от {chat_id}")
                return "✅ <b>СЕРВИС ПЕРЕЗАПУЩЕН</b>\n\nАвтосервис снова активен после ошибок API"
            else:
                return "ℹ️ Сервис уже активен"
        except Exception as e:
            logger.error(f"❌ Ошибка перезапуска сервиса: {e}")
            return f"❌ Ошибка перезапуска сервиса: {e}"
    
    def handle_stop(self, chat_id: int) -> str:
        """Обработчик команды /stop"""
        if not self.auto_service:
            return "❌ Автосервис не инициализирован"
        
        try:
            self.auto_service.service_active = False
            self.auto_service.save_service_state()
            logger.info(f"🔧 Автосервис остановлен через Telegram командой от {chat_id}")
            return "🛑 <b>СЕРВИС ОСТАНОВЛЕН</b>\n\nАвтосервис приостановлен. Используйте /restart для возобновления."
        except Exception as e:
            logger.error(f"❌ Ошибка остановки сервиса: {e}")
            return f"❌ Ошибка остановки сервиса: {e}"
    
    def handle_run_once(self, chat_id: int) -> str:
        """Обработчик команды /run_once"""
        if not self.auto_service:
            return "❌ Автосервис не инициализирован"
        
        try:
            success = self.auto_service.run_once()
            
            if success:
                return "✅ <b>ОБРАБОТКА ЗАВЕРШЕНА</b>\n\nНовые данные получены и обработаны"
            else:
                return "❌ <b>ОБРАБОТКА НЕ УДАЛАСЬ</b>\n\nПроверьте логи для деталей"
                
        except Exception as e:
            logger.error(f"❌ Ошибка при единичном запуске: {e}")
            return f"❌ Ошибка при единичном запуске: {e}"
    
    def handle_service_status(self, chat_id: int) -> str:
        """Обработчик команды /service_status"""
        if not self.auto_service:
            return "❌ Автосервис не инициализирован"
        
        try:
            status = self.auto_service.get_service_status()
            
            message = "🔧 <b>СТАТУС АВТОСЕРВИСА</b>\n\n"
            message += f"📊 Статус: {'🟢 АКТИВЕН' if status.get('service_active') else '🔴 ОСТАНОВЛЕН'}\n"
            message += f"🤖 Система: {'✅ Инициализирована' if status.get('system_initialized') else '❌ Не инициализирована'}\n"
            message += f"📈 Ошибок API подряд: {status.get('consecutive_api_errors', 0)}/{status.get('max_consecutive_errors', 3)}\n"
            
            last_draw = status.get('last_processed_draw', 'Не обработан')
            message += f"🎯 Последний тираж: {last_draw}\n"
            
            if status.get('model_trained'):
                message += f"🧠 Модель: ✅ Обучена\n"
                message += f"📊 Групп в датасете: {status.get('dataset_size', 0)}\n"
            else:
                message += f"🧠 Модель: ❌ Не обучена\n"
            
            learning_stats = status.get('learning_stats', {})
            if learning_stats and 'message' not in learning_stats:
                message += f"\n📈 <b>АНАЛИТИКА САМООБУЧЕНИЯ:</b>\n"
                message += f"🎯 Средняя точность: {learning_stats.get('recent_accuracy_avg', 0)*100:.1f}%\n"
                message += f"📊 Проанализировано прогнозов: {learning_stats.get('total_predictions_analyzed', 0)}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса сервиса: {e}")
            return f"❌ Ошибка получения статуса сервиса: {e}"