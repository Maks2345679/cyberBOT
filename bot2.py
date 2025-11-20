

import telebot
import logging
import json
import time
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (замените на свой)
BOT_TOKEN = "8363179256:AAHCFyMJBOemXfshQbXO-u_pFTKYoi-T3fM"

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# ID администратора (замените на ваш Telegram ID)
ADMIN_ID = 123456789

# Хранилище статистики
stats = {
    'starts': 0,
    'button_presses': 0,
    'last_update': None
}

# Тексты для бота
TEXT_START = (
    "👋 Здравствуйте! Я бот, который поможет вам разобраться с проблемой кибербуллинга, Для просмотра всех команд введите /help.\n\n"
    "Выберите интересующую вас тему:"
)

TEXT_WHAT_IS = (
    "🔍 **Что такое кибербуллинг?**\n\n"
    "Кибербуллинг — это систематическое преследование, запугивание или унижение человека в интернете.\n\n"
    "Основные формы:\n"
    "• Оскорбления и угрозы в соцсетях\n"
    "• Распространение ложной информации\n"
    "• Публикация личных данных без согласия\n"
    "• Намеренное исключение из групп/чатов\n"
    "• Поддельные аккаунты для травли\n\n"
    "Важно: кибербуллинг — не шутка. Это серьёзное правонарушение, которое может иметь тяжёлые последствия."
)

TEXT_HOW_TO_COPE = (
    "💪 **Как бороться с кибербуллингом?**\n\n"
    "1. **Не отвечайте** — не вступайте в перепалку.\n"
    "2. **Сделайте скриншоты** — сохраните доказательства.\n"
    "3. **Заблокируйте обидчика** — используйте функции соцсетей.\n"
    "4. **Пожаловаться** — отправьте жалобу в поддержку платформы.\n"
    "5. **Расскажите близким** — не оставайтесь наедине с проблемой.\n"
    "6. **Ограничьте время в сети** — дайте себе передышку.\n"
    "7. **Обратитесь к специалисту** — психолог поможет справиться с эмоциями.\n\n"
    "Помните: вы не одиноки, и вам есть куда обратиться за помощью."
)

TEXT_IF_VICTIM = (
    "⚠️ **Если вы стали жертвой кибербуллинга:**\n\n"
    "1. **Сохраните спокойствие** — это не ваша вина.\n"
    "2. **Фиксируйте всё** — скриншоты, ссылки, даты.\n"
    "3. **Не удаляйте сообщения** — они нужны как доказательства.\n"
    "4. **Сообщите взрослым** — родителям, учителям, куратору.\n"
    "5. **Используйте настройки приватности** — ограничьте доступ к профилю.\n"
    "6. **Обратитесь в поддержку соцсетей** — большинство платформ блокируют травлю.\n"
    "7. **Звоните на горячие линии** (см. раздел «Полезные ресурсы»).\n\n"
    "Вы заслуживаете уважения — не позволяйте никому нарушать ваши границы!"
)

TEXT_RESOURCES = (
    "📚 **Полезные ресурсы:**\n\n"
    "**В России:**\n"
    "• Телефон доверия для детей: 8 800 2000 122\n"
    "• Проект «Дети онлайн»: detionline.com\n"
    "• Центр «Травли.NET»: травлинет.рф\n\n"
    "**Международные:**\n"
    "• Cyberbullying Research Center: cyberbullying.org\n"
    "• StopBullying.gov: stopbullying.gov\n\n"
    "**Соцсети (где подать жалобу):**\n"
    "• ВКонтакте: Настройки → Помощь → Сообщить о проблеме\n"
    "• Telegram: Настройки → Задать вопрос → Сообщить о нарушении\n"
    "• Instagram: Профиль → ⋮ → Сообщить о проблеме"
)

# Защита от спама
LAST_MESSAGE_TIME = {}


def is_spam(user_id):
    """Проверяет, не является ли сообщение спамом"""
    current_time = time.time()
    if user_id in LAST_MESSAGE_TIME:
        if current_time - LAST_MESSAGE_TIME[user_id] < 1:
            return True
    LAST_MESSAGE_TIME[user_id] = current_time
    return False

# Класс для аналитики
class Analytics:
    def __init__(self):
        self.user_data = {}
        self.total_interactions = 0

    def register_interaction(self, user_id, action):
        self.total_interactions += 1

        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'first_seen': datetime.now(),
                'last_seen': datetime.now(),
                'actions': 0,
                'action_types': {}
            }

        self.user_data[user_id]['actions'] += 1
        self.user_data[user_id]['last_seen'] = datetime.now()

        if action not in self.user_data[user_id]['action_types']:
            self.user_data[user_id]['action_types'][action] = 0
        self.user_data[user_id]['action_types'][action] += 1

    def get_stats(self):
        return {
            'total_users': len(self.user_data),
            'total_interactions': self.total_interactions,
            'avg_per_user': self.total_interactions / len(self.user_data) if self.user_data else 0
        }

# Инициализация аналитики
analytics = Analytics()

# Функция для создания главной клавиатуры
def get_main_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        telebot.types.InlineKeyboardButton("Что такое кибербуллинг?", callback_data='what_is'),
        telebot.types.InlineKeyboardButton("Как бороться?", callback_data='how_to_cope')
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("Я жертва — что делать?", callback_data='if_victim'),
        telebot.types.InlineKeyboardButton("Полезные ресурсы", callback_data='resources')
    )
    return keyboard

# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    try:
        stats["starts"] += 1
        stats["last_update"] = datetime.now()
        analytics.register_interaction(message.from_user.id, 'start')

        bot.send_message(
            message.chat.id,
            TEXT_START,
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке стартового сообщения: {e}", exc_info=True)
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте /start ещё раз.")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "📘 **Справка по командам**\n\n"
        "/start — начать работу с ботом\n"
        "/help — показать эту справку\n"
        "/ping — проверить работоспособность бота\n"
        "/emergency — экстренная помощь\n"
        "/stats — статистика (для админа)\n"
        "/exportstats — экспорт статистики (для админа)\n"
        "/about — информация о боте\n"
        "/commands — показать все доступные команды\n\n"
        "Используйте кнопки в меню для получения подробной информации о кибербуллинге."
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['commands'])
def commands_list(message):
    """Показывает полный список доступных команд бота"""
    commands_text = (
        "🛠 **Список всех команд бота**\n\n"
        "/start — начать работу с ботом (главное меню)\n"
        "/help — краткая справка по командам\n"
        "/commands — полный список всех команд (этот список)\n"
        "/ping — проверить, работает ли бот\n"
        "/emergency — экстренная помощь и контакты служб поддержки\n"
        "/stats — статистика использования бота (доступно только администратору)\n"
        "/exportstats — экспорт полной статистики в файл (доступно только администратору)\n"
        "/about — информация о боте и его назначении\n\n"
        "💡 **Примечание:**\n"
        "• Команды /stats и /exportstats доступны только администратору (владельцу бота).\n"
        "• Остальные команды доступны всем пользователям."
    )
    bot.send_message(message.chat.id, commands_text, parse_mode='Markdown')

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.send_message(message.chat.id, "✅ Бот работает!")


@bot.message_handler(commands=['emergency'])
def emergency_help(message):
    response = (
        "🚨 **Экстренная помощь**\n\n"
        "Если вы чувствуете угрозу жизни или здоровью:\n\n"
        "1. Позвоните в **службу спасения** по номеру 112\n"
        "2. Сообщите о ситуации близким людям\n"
        "3. Сохраните все доказательства (скриншоты, сообщения)\n\n"
        "Горячие линии психологической помощи:\n"
        "• Единый экстренный канал: **112**\n"
        "• Телефон доверия для детей и подростков: **8 800 2000 122**\n"
        "• Кризисная линия доверия: **8 499 216-92-90**\n\n"
        "Не оставайтесь наедине с проблемой — вам обязательно помогут!"
    )
    bot.send_message(message.chat.id, response, parse_mode='Markdown')


@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id == ADMIN_ID:
        stats_data = analytics.get_stats()
        response = (
            "📊 **Статистика бота**\n\n"
            "f!• Всего пользователей: {stats_data['total_users']}\n"
            "f!• Всего взаимодействий: {stats_data['total_interactions']}\n"
            "f!• Среднее на пользователя: {stats_data['avg_per_user']:.1f}\n"
           " f!• Запусков /start: {stats['starts']}\n"
            "f!• Нажатий кнопок: {stats['button_presses']}"
        )
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к статистике.")


@bot.message_handler(commands=['exportstats'])
def export_stats(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")
        return

    try:
        import json
        from datetime import datetime


        export_data = {
            'bot_stats': stats,
            'analytics': {
                'total_interactions': analytics.total_interactions,
                'total_users': len(analytics.user_data),
                'users': analytics.user_data
            },
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }

        filename = f"bot_stats_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)


        with open(filename, 'rb') as f:
            bot.send_document(
                message.chat.id,
                f,
                caption="Экспорт статистики бота"
            )

        import os
        os.remove(filename)

    except Exception as e:
        logger.error(f"Ошибка при экспорте статистики: {e}")
        bot.send_message(message.chat.id, "Не удалось экспортировать статистику.")


@bot.message_handler(commands=['about'])
def about_command(message):
    bot.send_message(
        message.chat.id,
        "🤖 **О боте**\n\n"
        "Этот бот создан для информирования о проблеме кибербуллинга и помощи жертвам.\n\n"
        "**Функции:**\n"
        "• Объясняет, что такое кибербуллинг\n"
        "• Даёт советы по противодействию\n"
        "• Помогает жертвам\n"
        "• Предоставляет контакты служб помощи\n"
        "• Ведёт статистику использования\n\n"
        "**Версия:** 1.0\n"
        "**Разработчик:** [@Speedrunmaks]",
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def button(call):
    try:
        user_id = call.from_user.id

        # Защита от частых нажатий
        current_time = time.time()
        if user_id in LAST_MESSAGE_TIME:
            if current_time - LAST_MESSAGE_TIME[user_id] < 1:
                bot.answer_callback_query(
                    call.id,
                    "Пожалуйста, подождите секунду перед следующим нажатием.",
                    show_alert=True
                )
                return
        LAST_MESSAGE_TIME[user_id] = current_time

        stats["button_presses"] += 1
        stats["last_update"] = datetime.now()
        analytics.register_interaction(user_id, f'button_{call.data}')

        if call.data == 'what_is':
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton("Назад", callback_data='back_to_main'))
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=TEXT_WHAT_IS,
                parse_mode='Markdown',
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
        elif call.data == 'how_to_cope':
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton("Назад", callback_data='back_to_main'))
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=TEXT_HOW_TO_COPE,
                parse_mode='Markdown',
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
        elif call.data == 'if_victim':
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton("Назад", callback_data='back_to_main'))
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=TEXT_IF_VICTIM,
                parse_mode='Markdown',
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
        elif call.data == 'resources':
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton("Назад", callback_data='back_to_main'))
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=TEXT_RESOURCES,
                parse_mode='Markdown',
                disable_web_page_preview=True,
                reply_markup=keyboard
            )
        elif call.data == 'back_to_main':
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=TEXT_START,
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )

        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Ошибка при обработке callback: {e}", exc_info=True)
        try:
            bot.answer_callback_query(
                call.id,
                "Произошла ошибка. Попробуйте снова.",
                show_alert=True
            )
        except:
            pass

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/') and message.text not in ['/start', '/help', '/commands', '/ping', '/emergency', '/stats', '/exportstats', '/about'])
def unknown_command(message):
    bot.send_message(
        message.chat.id,
        "⚠️ Неизвестная команда.\n"
        "Воспользуйтесь /help для просмотра списка доступных команд.",
        parse_mode='Markdown'
    )

@bot.message_handler(content_types=['photo', 'video', 'document', 'sticker'])
def handle_unsupported(message):
    bot.send_message(
        message.chat.id,
        "Я не поддерживаю этот тип сообщений. "
        "Воспользуйтесь /start для навигации по меню.",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: True)
def default_handler(message):
    if is_spam(message.from_user.id):
        return

    bot.send_message(
        message.chat.id,
        "Я понимаю только команды. Нажмите /start, чтобы открыть главное меню.",
        parse_mode='Markdown'
    )

# Планировщик для очистки старых записей
def scheduler():
    while True:
        time.sleep(3600)  # раз в час
        try:
            now = time.time()
            cutoff = now - 86400  # 24 часа
            for user_id in list(LAST_MESSAGE_TIME.keys()):
                if LAST_MESSAGE_TIME[user_id] < cutoff:
                    del LAST_MESSAGE_TIME[user_id]
        except Exception as e:
            logger.error(f"Ошибка в планировщике: {e}")


# Запуск планировщика в отдельном потоке
import threading
scheduler_thread = threading.Thread(target=scheduler, daemon=True)
scheduler_thread.start()

# Главный цикл с обработкой ошибок
def main():
    logger.info("Бот запущен и начинает polling...")


    while True:
        try:
            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=20,
                allowed_updates=['message', 'callback_query'],
                skip_pending=True
            )
        except telebot.apihelper.ApiException as e:
            if "Too Many Requests" in str(e):
                logger.warning("Ограничение Telegram: Too Many Requests. Ждём 60 сек...")
                time.sleep(60)
            elif "Conflict" in str(e):
                logger.error("Конфликт с другим экземпляром бота. Проверьте, не запущен ли ещё один экземпляр.")
                break
            else:
                logger.error(f"API‑ошибка: {e}", exc_info=True)
                time.sleep(10)
        except ConnectionError as e:
            logger.error(f"Ошибка соединения: {e}. Переподключение через 30 сек...")
            time.sleep(30)
        except KeyboardInterrupt:
            logger.info("Бот остановлен вручную пользователем")
            break
        except Exception as e:
            logger.critical(f"Критическая ошибка: {e}", exc_info=True)
            time.sleep(15)


    logger.info(f"Работа бота завершена. Статистика: "
              f"запусков=/start={stats['starts']}, "
              f"нажатий кнопок={stats['button_presses']}, "
              f"всего взаимодействий={analytics.total_interactions}")


if __name__ == '__main__':
    main()
