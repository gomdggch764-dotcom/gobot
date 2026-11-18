import random
import time
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ТОКЕН
BOT_TOKEN = "9132537199:AAGF7QnaYCyiPGAH67euOIeh-jDVJ8dwTnQ"
bot = telebot.TeleBot(BOT_TOKEN)

# Правила генерации (чередование согласных и гласных)
VOWELS = "aeiouy"
CONSONANTS = "bcdfghjklmnpqrstvwxz"

def generate_word(use_numbers=False):
    # Случайно выбираем длину: 5 или 6 символов
    length = random.choice([5, 6])
    word = ""
    
    for i in range(length):
        if i % 2 == 0:
            word += random.choice(CONSONANTS)
        else:
            word += random.choice(VOWELS)
            
    # Если включен режим с цифрами, заменяем 1-2 буквы (с вероятностью 60%)
    if use_numbers and random.random() < 0.6:
        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        letters = list(word)
        replaceable = [i for i, char in enumerate(letters) if char in leet_map]
        if replaceable:
            num_to_replace = random.randint(1, min(2, len(replaceable)))
            indices = random.sample(replaceable, num_to_replace)
            for idx in indices:
                letters[idx] = leet_map[letters[idx]]
        word = "".join(letters)
        
    return word

def check_username(username):
    try:
        r = requests.get(f"https://t.me/{username}", timeout=10)
        if r.status_code == 404:
            return True
        elif r.status_code == 429:
            return "BAN"
    except Exception:
        return None
    return False

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🅰️ Только буквы (5-6)", callback_data="check_letters"))
    markup.add(InlineKeyboardButton("🔢 С цифрами (5-6)", callback_data="check_numbers"))
    bot.send_message(message.chat.id, "Выбери режим поиска:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["check_letters", "check_numbers"])
def callback_check(call):
    use_numbers = (call.data == "check_numbers")
    mode_text = "с цифрами" if use_numbers else "только буквы"
    
    bot.answer_callback_query(call.id, f"⏳ Ищу ({mode_text})...")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"⏳ Ищу складные имена ({mode_text}, 5-6 символов)...")
    
    free_names = []
    checked = 0
    
    # Проверяем до 40 вариантов, чтобы найти хотя бы 10 свободных
    while len(free_names) < 10 and checked < 40:
        word = generate_word(use_numbers)
        result = check_username(word)
        
        if result == "BAN":
            bot.send_message(call.message.chat.id, "⚠️ Бан (429). Подожди немного.")
            return
        elif result is True:
            if word not in free_names:
                free_names.append(word)
                
        checked += 1
        time.sleep(1.5) 
        
    if free_names:
        text = f"✅ Найдены свободные имена ({mode_text}):\n\n"
        for name in free_names:
            text += f"🔗 @{name}\n"
    else:
        text = f"😔 Проверил {checked} вариантов ({mode_text}), свободных нет. Жми еще раз!"
        
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🅰️ Только буквы", callback_data="check_letters"))
    markup.add(InlineKeyboardButton("🔢 С цифрами", callback_data="check_numbers"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, disable_web_page_preview=True)

print("Бот запущен...")
bot.infinity_polling()
