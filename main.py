import schedule
import time
import telebot
from telebot import types
import os
import re
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

bot = telebot.TeleBot('6746553299:AAFsZbDwbvON6koaMdYNKONxlb4kSmqWFVM')


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)


def get_today_date():
    return datetime.date.today().strftime("%d.%m.%Y")


def get_tomorrow_date():
    return (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")


def extract_schedule(text):
    text = (
        text.replace('Производственная практика', '').replace('Каникулы', '').replace('Занятие', '').replace('Время', '').replace(
            'Дисциплина', '').replace('Ауд.', '').replace('Преподаватель', ''))

    text = re.sub(r'№.*?50', '', text, flags=re.DOTALL)

    pattern = r'(\d{2}\.\d{2}\.\d{4})\s+([\s\S]*?)(?=\d{2}\.\d{2}\.\d{4}|\Z)'
    matches = re.findall(pattern, text)
    schedules = []
    for match in matches:
        date = match[0]
        schedule_text = match[1]
        if not schedule_text.strip():
            continue
        schedules.append((date, schedule_text))
    return schedules


def save_schedule(schedules, parent_folder):
    table_folder = parent_folder
    os.makedirs(table_folder, exist_ok=True)
    main_folder_name = os.path.basename(os.path.dirname(parent_folder))
    for schedule in schedules:
        date, schedule_text = schedule
        filename = re.sub(r'[^a-zA-Z0-9а-яА-Я.]+', '_', date)

        filename = f"{main_folder_name}_{filename}"
        with open(f"{table_folder}/{filename}.txt", "w", encoding="utf-8") as file:
            file.write(f"Дата: {date}\n\n")
            file.write(schedule_text)

def update_schedule(spreadsheet_name):
    try:
        spreadsheet = client.open(spreadsheet_name)
        parent_folder = spreadsheet.title
        sheets = spreadsheet.worksheets()

        for sh in sheets:

            rows = sh.get_all_values()
            sheet_folder = f"{parent_folder}/{sh.title}"

            save_schedule(extract_schedule('\n'.join(['\t'.join(row) for row in rows])), sheet_folder)
        print(f"Данные для таблицы {spreadsheet_name} успешно обновлены.")
    except Exception as e:
        print(f"Произошла ошибка при обновлении данных для таблицы {spreadsheet_name}: {e}")



schedule.every(30).minutes.do(update_schedule, spreadsheet_name='1103')
schedule.every(30).minutes.do(update_schedule, spreadsheet_name='1104')

def run_continuously():
    while True:
        schedule.run_pending()
        time.sleep(1)

import threading
update_thread = threading.Thread(target=run_continuously)
update_thread.start()


def register_handlers():
    @bot.message_handler(content_types=['text'], commands=['start'])
    def welcome(message):
        markup_folders = types.ReplyKeyboardMarkup(resize_keyboard=True)
        itembtn1_folder = types.KeyboardButton('1104')
        itembtn2_folder = types.KeyboardButton('1103')
        markup_folders.add(itembtn1_folder, itembtn2_folder)
        bot.send_message(message.chat.id, "Выберите группу:", reply_markup=markup_folders)

    @bot.message_handler(func=lambda message: message.text in ['1104', '1103'])
    def handle_folders(message):
        selected_folder = message.text.strip()
        markup_date = types.ReplyKeyboardMarkup(resize_keyboard=True)
        itembtn_today = types.KeyboardButton('Сегодня')
        itembtn_tomorrow = types.KeyboardButton('Завтра')
        markup_date.add(itembtn_today, itembtn_tomorrow)
        bot.send_message(message.chat.id, "Выберите дату для получения расписания:", reply_markup=markup_date)
        bot.register_next_step_handler(message, lambda msg: handle_date(msg, selected_folder))

def handle_date(message, selected_folder):
    def process_date(msg, selected_folder, requested_date):
        expected_date_format = datetime.datetime.strptime(requested_date, "%d.%m.%Y").strftime("%d.%m.%Y")
        root_directory = r"C:\Users\dento\PycharmProjects\tablica"
        if selected_folder == '1104':
            root_directory = os.path.join(root_directory, '1104')
        elif selected_folder == '1103':
            root_directory = os.path.join(root_directory, '1103')
        found_schedule = False
        for root, dirs, files in os.walk(root_directory):
            for file in files:
                if file.endswith(".txt") and expected_date_format in file:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as schedule_file:
                        schedule_text = schedule_file.read()
                        bot.reply_to(msg, schedule_text)
                    found_schedule = True
        if not found_schedule:
            bot.reply_to(msg, "Расписание на указанную дату отсутствует")
        bot.register_next_step_handler(msg, lambda msg: handle_date(msg, selected_folder))

    if message.text.lower() == "сегодня":
        requested_date = get_today_date()
        process_date(message, selected_folder, requested_date)
    elif message.text.lower() == "завтра":
        requested_date = get_tomorrow_date()
        process_date(message, selected_folder, requested_date)


register_handlers()
print('бот готов')

bot.polling()
