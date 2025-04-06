from loguru import logger
import click
import json
import time
import os
import subprocess
import schedule

from utils.parser import parse_datetime


CONFIG_PATH = None
CONFIG_DATA = None
weekdays_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


# Чтение конфигурационного файла с задачами
def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)


def change_task_status(task_name, status):
    task = list(filter(lambda x: x['name'] == task_name, CONFIG_DATA['tasks']))
    task[0]['status'] = status


def update_config():
    with open(CONFIG_PATH, "w") as file:
        json.dump(CONFIG_DATA, file)


# Функция для выполнения команды
def run_task(command, args, task_name):
    logger.info(f"Запуск {task_name}: {command} {' '.join(args)}")
    result = subprocess.run(command, *args, capture_output=True)
    logger.info(f"stdout: {result.stdout.decode()} | stderr: {result.stderr.decode()}")


def setup_logger(folder:str='logs', log_name:str='scheduler.log'):
    os.makedirs(folder, exist_ok=True)
    log_path = os.path.join(folder, log_name)
    # Настройка логирования
    logger.add(log_path, rotation="10 MB", retention="30 days", level="INFO")


def init_tasks(config):
    """Запланировать выполнение задач с учетом дней недели"""
    # TODO сделать чтобы если задание пропущено почему то, то сразу запускать
    
    for task in config['tasks']:
        days, task_time = parse_datetime(task['time'])  # days - список чисел (0-6), task_time - время 
        command = task['command']
        args = task['args']
        task_name = task['name']
        
        if not days: # Если дни не указаны - ежедневно
            schedule.every().day.at(task_time).do(run_task, command, args, task_name)
            change_task_status(task_name, 'running')
            continue
        
        for day_num in days:
            # Получаем название дня недели для schedule
            weekday = weekdays_list[day_num]
            getattr(schedule.every(), weekday).at(task_time).do(
                run_task, command, args, task_name
            )
            change_task_status(task_name, 'running')
    update_config()


@click.command()
@click.option('--config', type=str, default='config.json', help='Путь к конфигу.')
@click.option('--log', type=str, default='logs', help='Директория для хранения логов.')
def main(config, log):
    """Планировщик задач"""
    global CONFIG_PATH, CONFIG_DATA
    
    setup_logger(folder=log)
    
    CONFIG_PATH = config
    
    CONFIG_DATA = load_config(CONFIG_PATH)
    CONFIG_DATA = init_tasks(CONFIG_DATA)
    
    # TODO сделать проверку на уникальности имени
    # TODO добавить класс для удобства
    # TODO сделать запуск каждое какое то время
    
    # TODO Добавить статусы к заданиям (запущен, выполнен, ошибка)
    # TODO Добавить обновление конфига каждые несколько секунд
    # TODO Добавить старт скрипта
    # TODO Сделать парсинг времени и создание задач на основе времени (и даты возможно)
    
    while True:
        schedule.run_pending()
        time.sleep(5)

if __name__ == '__main__':
    main()
