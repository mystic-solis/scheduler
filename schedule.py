from loguru import logger
import click
import json
import time
import os
import subprocess
import schedule


# Чтение конфигурационного файла с задачами
def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)


# Функция для выполнения команды
def run_task(command, args, task_name):
    logger.info(f"Запуск {task_name}: {command} {' '.join(args)}")
    result = subprocess.run([command] + args, capture_output=True)
    logger.info(f"Задача {task_name} вернула код {result.returncode}")
    logger.info(f"stdout: {result.stdout.decode()}\nstderr: {result.stderr.decode()}")


def setup_logger(folder:str='logs', log_name:str='scheduler.log'):
    os.makedirs(folder, exist_ok=True)
    log_path = os.path.join(folder, log_name)
    # Настройка логирования
    logger.add(log_path, rotation="10 MB", retention="30 days", level="INFO")



    subprocess.run([command] + args)
    save_task_status(task_name, "completed")  # Обновляем статус задачи после выполнения


# Запланировать выполнение задач
# def schedule_tasks():
#     tasks = load_config()
#     for task in tasks['tasks']:
#         task_time = task['time']
#         command = task['command']
#         args = task['args']
        
#         # Конвертируем время из строки в формат для schedule
#         hours, minutes = map(int, task_time.split(":"))
#         schedule.every().day.at(f"{hours:02d}:{minutes:02d}").do(run_task, command, args, task['name'])


# Основной цикл планировщика
@click.command()
@click.option('--config', type=str, default='config.json', help='Путь к конфигу.')
@click.option('--log', type=str, default='logs', help='Директория для хранения логов.')
def main(config, log):
    setup_logger(folder=log)
    
    # schedule_tasks()
    
    # TODO Добавить статусы к заданиям (запущен, выполнен, ошибка)
    # TODO Добавить обновление конфига каждые несколько секунд
    # TODO Добавить старт скрипта
    # TODO Сделать парсинг времени и создание задач на основе времени (и даты возможно)
    
    while True:
        config_data = load_config(config)
        schedule.run_pending()
        time.sleep(30)

if __name__ == '__main__':
    main()
