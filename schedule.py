from loguru import logger
import click
import json
import time
import os
import subprocess
import schedule
from datetime import datetime

# Чтение конфигурационного файла с задачами
def load_tasks():
    with open('tasks_config.json', 'r') as f:
        return json.load(f)

# Обновление статуса задачи в конфигурации
def save_task_status(task_name, status):
    tasks = load_tasks()
    for task in tasks['tasks']:
        if task['name'] == task_name:
            task['status'] = status
            break
    with open('tasks_config.json', 'w') as f:
        json.dump(tasks, f, indent=4)

# Функция для выполнения команды
def run_task(command, args, task_name):
    print(f"Executing: {command} {' '.join(args)}")
    subprocess.run([command] + args)
    save_task_status(task_name, "completed")  # Обновляем статус задачи после выполнения

# Запланировать выполнение задач
def schedule_tasks():
    tasks = load_tasks()
    for task in tasks['tasks']:
        if task['status'] != "completed":  # Пропустить выполненные задачи
            task_time = task['time']
            command = task['command']
            args = task['args']
            
            # Конвертируем время из строки в формат для schedule
            hours, minutes = map(int, task_time.split(":"))
            schedule.every().day.at(f"{hours:02d}:{minutes:02d}").do(run_task, command, args, task['name'])


def setup_logger():
    log_path = os.path.join("logs", "scheduler.log")
    os.makedirs(log_path, exist_ok=True)
    logger.add("scheduler.log", rotation="1 MB", retention="10 days", level="INFO")
    logger.info("Task scheduler started.")


# Основной цикл планировщика
@click.command()
@click.option('--config', type=str, default='config.json', help='Путь к конфигу.')
@click.option('--log', type=str, default=None, help='Путь к конфигу.')
def main(config, log):
    setup_logger()
    
    # schedule_tasks()
    
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)  # Проверка каждую минуту

if __name__ == '__main__':
    main()
