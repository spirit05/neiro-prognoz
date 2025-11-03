# api_data/telegram_webhook.py - исправляем обработчик

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Обработчик вебхука от Telegram"""
    try:
        # Получаем сырые данные и парсим JSON
        raw_data = request.get_data(as_text=True)
        logger.info(f"📨 Получены сырые данные: {raw_data[:200]}...")
        
        try:
            update = json.loads(raw_data)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            return jsonify({'status': 'error', 'message': 'Invalid JSON'})
        
        logger.info(f"📨 Получено сообщение от Telegram: {update}")
        
        if 'message' in update:
            message = update['message']
            text = message.get('text', '').strip()
            chat_id = message['chat']['id']
            
            if text == '/start':
                response = "🤖 <b>Добро пожаловать в AI Prediction System!</b>\n\n" \
                          "Доступные команды:\n" \
                          "/status - статус системы\n" \
                          "/help - помощь\n" \
                          "/predictions - последние прогнозы"
                send_telegram_message(chat_id, response)
                
            elif text == '/status':
                send_system_status(chat_id)
                
            elif text == '/predictions':
                send_last_predictions(chat_id)
                
            elif text == '/help':
                response = "🆘 <b>Помощь по командам:</b>\n\n" \
                          "/status - полный статус системы\n" \
                          "/predictions - последние 4 прогноза\n" \
                          "/help - эта справка"
                send_telegram_message(chat_id, response)
                
            else:
                response = "❌ Неизвестная команда. Используйте /help для списка команд"
                send_telegram_message(chat_id, response)
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
