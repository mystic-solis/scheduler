import asyncio
from loguru import logger
import click
import json
import time
import os
import subprocess
import schedule

from utils.parser import parse_datetime
from utils.validators import check_names_unique


WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
CONFIG_TEMPLATE = {'tasks': []}


# TODO сделать запуск каждое какое то время (рекуррентные задачи)

# TODO Добавить статусы к заданиям (запущен, выполнен, ошибка)
# TODO Добавить обновление конфига каждые несколько секунд


def change_task_status(tasks, task_name, status):
    task = list(filter(lambda x: x['name'] == task_name, tasks))
    task[0]['status'] = status


# Функция для выполнения команды
def run_task(command, args, task_name):
    logger.info(f"Запуск {task_name}: {command} {' '.join(args)}")
    result = subprocess.run(command, *args, capture_output=True)
    logger.info(f"stdout: {result.stdout.decode()} | stderr: {result.stderr.decode()}")


class Chrono:
    """Планировщик заданий"""

    def __init__(self, config_path, log_dir):
        self.config_path = config_path or 'config.json'
        self.log_dir = log_dir

        self.config_data = self.load_config(self.config_path)
        self.setup_logger(folder=log_dir)


    def run_checks(self):
        """Функция запуска проверок конфигурационного файла"""
        check_names_unique(tasks=CONFIG_DATA['tasks'])
    

    def setup_logger(self, folder:str='logs', log_name:str='scheduler.log'):
        """Настройка ведения логов"""
        if folder is None:
            return
        
        os.makedirs(folder, exist_ok=True)
        log_path = os.path.join(folder, log_name)
        # Настройка логирования
        logger.add(log_path, rotation="10 MB", retention="30 days", level="INFO")
    

    def load_config(self, path):
        """Чтение конфигурационного файла с задачами"""
        # Если файла конфига не существует
        if path is None or not os.path.exists(path):
            logger.info('Файла конфигурации не существует. Создаем...')
            return CONFIG_TEMPLATE
        # Файл конфига существует
        with open(path, 'r') as f:
            return json.load(f)
    

    def update_config(self):
        """Запись конфигурации в файл"""
        with open(self.config_path, "w") as file:
            json.dump(self.config_data, file, indent=2, ensure_ascii=False)
    

    def init_tasks(self, config):
        """Планирование выполнения задач с учетом дней недели"""
        # TODO сделать чтобы если задание пропущено почему то, то сразу запускать (вроде и так работает по умолчанию)
        
        if config is None:
            return

        for task in config['tasks']:
            days, task_time = parse_datetime(task['time'])  # days - список дней недели (monday-sunday), task_time - время 
            command = task['command']
            args = task['args']
            task_name = task['name']

            # TODO добавить просмотр статуса и если какой то статус стоит его обработать или если вообще нет
            
            if not days: # Если дни не указаны - ежедневно
                schedule.every().day.at(task_time).do(run_task, command, args, task_name)
                change_task_status(config['tasks'], task_name, 'running')
                continue
            
            for weekday in days:
                getattr(schedule.every(), weekday).at(task_time).do(
                    run_task, command, args, task_name
                )
                change_task_status(config['tasks'], task_name, 'running')
            # TODO сделать чтобы запуск running сменялся на другое когда был выход из программы
        self.update_config()


    async def run():
        """Запуск программы"""
        # TODO добавить асинхронность, чтобы можно было еще параллельно обновлять конфиг файл, вдруг что новое появится там
        while True:
            # Добавить обновление конфига
            schedule.run_pending()
            await asyncio.sleep(5)


@click.command()
@click.option('--config', type=str, default=None, help='Путь к конфигу.')
@click.option('--log', type=str, default=None, help='Директория для хранения логов.')
async def main(config, log):
    """Планировщик задач"""
    
    schedule = Chrono(
        config_path=config,
        log_dir=log
    )
    schedule.run_checks()
    await schedule.run()


if __name__ == '__main__':
    main()
