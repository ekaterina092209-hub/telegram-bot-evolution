import telebot
from telebot import types

# ========== НАСТРОЙКИ - ЗАМЕНИТЕ НА СВОИ ДАННЫЕ ==========
BOT_TOKEN = "8293332030:AAHXyEzkJU6m8v9AIfUk_IjrcHryDBseCvw"

# Реквизиты для оплаты
PAYMENT_METHODS = {
    "card": {
        "name": "Картой 🇷🇺 для граждан России",
        "details": """
 <b>Оплата по карте:</b>

Номер карты Т-банк: <code>5536 9138 5529 2336</code>
Получатель: Екатерина Щ.
<b>Сумма: 690 руб/месяц.</b>

Нажмите на номер карты, чтобы скопировать.
"""
    },
    
    "card_kz": {
        "name": "Картой 🇰🇿 для граждан Казахстана",
        "details": """
 <b>Оплата по карте:</b>

Номер карты Kaspi: <code>4400 4302 8365 5105</code>
Получатель: Ekaterina S.
<b>Сумма: 4200 тг/месяц.</b>

Нажмите на номер карты, чтобы скопировать.
"""
    }
}

# Ссылки на продукт (то, что получит пользователь после оплаты)
PRODUCT_LINKS = """
<b>Добро пожаловать в Эволюцию 💔
Твоя подписка активирована</b>

<a href="https://t.me/+iSTXC-AoyXYxZDFi">это канал с материалами</a> — обязательно изучи закрепленные сообщения и загляни [библиотеку эволюции], в ней ссылки на все полезные посты и лекции.

<a href="https://t.me/+ST-_XOJmEeowNmYy">это чат</a> — где можно знакомиться, общаться и задавать вопросы по теме. В закрепленных сообщениях есть правила чата, не забудь ознакомиться. 

Очень надеюсь что, в Эволюции ты найдёшь то, что ищешь. Добро пожаловать в команду и пусть у тебя всё получиться.

Если возникнут вопросы, пишите мне в личку — @kat_mikhelson
"""

# ========== КОД БОТА ==========
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения выбранного способа оплаты каждого пользователя
user_payment_method = {}


@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start - первое сообщение пользователю"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "друг"
    
    # Создаём клавиатуру с кнопками способов оплаты
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for method_key, method_data in PAYMENT_METHODS.items():
        button = types.InlineKeyboardButton(
            text=method_data["name"],
            callback_data=f"pay_{method_key}"
        )
        markup.add(button)
    
    # Приветственное сообщение
    welcome_text = f"""
<b>Привет, {user_name}!</b>

Если ты здесь значит, ты приняла лучшее для себя решение — изменить свою жизнь и рутину к лучшему.
Эволюция — это самое подходящее, для этого место. Добро пожаловать! 

<b>→ Стоимость ежемесячной подписки на Эволюцию:</b> 690 руб/месяц или 4200 тг/месяц.

Выбери комфортный способ оплаты:
"""
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def payment_method_selected(call):
    """Обработчик выбора способа оплаты"""
    user_id = call.from_user.id
    method = call.data.replace('pay_', '')
    
    # Сохраняем выбранный способ оплаты
    user_payment_method[user_id] = method
    
    # Отправляем реквизиты
    payment_details = PAYMENT_METHODS[method]["details"]
    bot.send_message(
        call.message.chat.id,
        payment_details,
        parse_mode='HTML'
    )
    
    # Напоминание отправить чек
    bot.send_message(
        call.message.chat.id,
        " <b>Не забудь отправить чек об оплате!</b>\n\n"
        "Просто пришли фото или скриншот чека в этот чат.",
        parse_mode='HTML'
    )
    
    # Подтверждаем нажатие кнопки
    bot.answer_callback_query(call.id, " Реквизиты отправлены!")


@bot.message_handler(content_types=['photo'])
def receipt_received(message):
    """Обработчик получения фото (чека об оплате)"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Пользователь"
    payment_method = user_payment_method.get(user_id, "неизвестно")
    
    # Сообщение пользователю
    bot.send_message(
        message.chat.id,
        " <b>Чек получен!</b>\n\n"
        "Проверяю оплату... Обычно это занимает несколько минут.",
        parse_mode='HTML'
    )
    
    # ВАЖНО: Здесь вы получите уведомление о новом платеже
    # Отправьте себе уведомление (замените YOUR_ADMIN_ID на ваш Telegram ID)
    ADMIN_ID = 197410590
    try:
        # Создаём кнопки для одобрения/отклонения
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        approve_btn = types.InlineKeyboardButton(
            text="Одобрить",
            callback_data=f"admin_approve_{user_id}"
        )
        reject_btn = types.InlineKeyboardButton(
            text="Отклонить",
            callback_data=f"admin_reject_{user_id}"
        )
        admin_markup.add(approve_btn, reject_btn)
        
        bot.send_message(
            ADMIN_ID,
            f"💁🏻‍♀️ <b>Новый платёж!</b>\n\n"
            f" От: {user_name} (@{message.from_user.username or 'нет username'})\n"
            f" ID: <code>{user_id}</code>\n"
            f" Способ: {payment_method}",
            parse_mode='HTML',
            reply_markup=admin_markup
        )
        # Пересылаем чек админу
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    except:
        pass  # Если не удалось отправить админу, продолжаем работу


@bot.message_handler(commands=['approve'])
def approve_payment(message):
    """Команда для подтверждения оплаты (только для админа)"""
    # Проверяем, что команду отправил админ
    ADMIN_ID = 197410590
    
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        # Извлекаем ID пользователя из команды
        user_id = int(message.text.split()[1])
        
       # Создаём кнопку для связи при проблемах
        support_markup = types.InlineKeyboardMarkup()
        support_button = types.InlineKeyboardButton(
            text="Написать Кате, что ссылка не работает",
            url="https://t.me/kat_mikhelson"
        )
        support_markup.add(support_button)
        
        # Отправляем пользователю ссылки на продукт с кнопкой
        bot.send_message(
            user_id,
            PRODUCT_LINKS,
            parse_mode='HTML',
            reply_markup=support_markup
        )
        
        # Подтверждение админу
        bot.send_message(
            message.chat.id,
            f"🌝 Доступы отправлены пользователю {user_id}"
        )
        
        # Удаляем информацию о способе оплаты
        if user_id in user_payment_method:
            del user_payment_method[user_id]
            
    except (IndexError, ValueError):
        bot.send_message(
            message.chat.id,
            "Неверный формат команды. Используйте: /approve USER_ID"
        )


@bot.message_handler(commands=['reject'])
def reject_payment(message):
    """Команда для отклонения платежа (только для админа)"""
    # Проверяем, что команду отправил админ
    ADMIN_ID = 197410590
    
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        # Извлекаем ID пользователя из команды
        user_id = int(message.text.split()[1])
        
        # Отправляем пользователю сообщение об отклонении
        bot.send_message(
            user_id,
            "<b>К сожалению, не удалось подтвердить оплату по вашему чеку.</b>\n\n"
            "Пожалуйста, свяжитесь со мной напрямую @kat_mikhelson, чтобы разобраться в ситуации.",
            parse_mode='HTML'
        )
        
        # Подтверждение админу
        bot.send_message(
            message.chat.id,
            f"Сообщение об отклонении отправлено пользователю {user_id}"
        )
        
        # Удаляем информацию о способе оплаты
        if user_id in user_payment_method:
            del user_payment_method[user_id]
            
    except (IndexError, ValueError):
        bot.send_message(
            message.chat.id,
            "Неверный формат команды. Используйте: /reject USER_ID"
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_buttons_handler(call):
    """Обработчик кнопок одобрения/отклонения для админа"""
    ADMIN_ID = 197410590
    
    if call.from_user.id != ADMIN_ID:
        return
    
    action = call.data.split('_')[1]  # approve или reject
    user_id = int(call.data.split('_')[2])
    
    if action == "approve":
        # Создаём кнопку для пользователя
        support_markup = types.InlineKeyboardMarkup()
        support_button = types.InlineKeyboardButton(
            text="Написать Кате, что ссылка не работает",
            url="https://t.me/kat_mikhelson"
        )
        support_markup.add(support_button)
        
        # Отправляем доступы пользователю
        bot.send_message(
            user_id,
            PRODUCT_LINKS,
            parse_mode='HTML',
            reply_markup=support_markup
        )
        
        # Уведомляем админа
        bot.answer_callback_query(call.id, "Доступы отправлены!")
        bot.edit_message_text(
            f"{call.message.text}\n\n <b>ОДОБРЕНО</b>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML'
        )
        
        # Удаляем информацию о способе оплаты
        if user_id in user_payment_method:
            del user_payment_method[user_id]
    
    elif action == "reject":
        # Отправляем отклонение пользователю
        bot.send_message(
            user_id,
            "<b>К сожалению, не удалось подтвердить оплату по вашему чеку.</b>\n\n"
            "Пожалуйста, свяжитесь со мной напрямую @kat_mikhelson, чтобы разобраться в ситуации.",
            parse_mode='HTML'
        )
        
        # Уведомляем админа
        bot.answer_callback_query(call.id, "Платёж отклонён")
        bot.edit_message_text(
            f"{call.message.text}\n\n <b>ОТКЛОНЕНО</b>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML'
        )
        
        # Удаляем информацию о способе оплаты
        if user_id in user_payment_method:
            del user_payment_method[user_id]

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Обработчик всех остальных сообщений"""
    bot.send_message(
        message.chat.id,
        "Пожалуйста, отправьте фото или скриншот чека об оплате"
    )


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()