import asyncio
from asyncio import subprocess
from loguru import logger
import click
import json
import os
import schedule
from watchfiles import awatch

from utils.parser import parse_datetime
from utils.validators import check_names_unique


CONFIG_TEMPLATE = {'tasks': []}

# TODO сделать запуск каждое какое то время (рекуррентные задачи)
# TODO Добавить статусы к заданиям (ожидание, выполнена, запущена, ошибка). Реализовать их смену.

class Chrono:
    """Планировщик заданий"""


    def __init__(self, config_path, log_dir):
        self.config_path = config_path or 'config.json'
        self.log_dir = log_dir

        self.config_data = self.load_config()
        self.setup_logger(folder=log_dir)


    async def watch_config(self):
        """Асинхронно следим за изменением именно этого файла"""
        async for changes in awatch(self.config_path):
            logger.info(f"Конфиг изменился: {self.config_path}")
            # Удаляем все старые записи (если записываем 2 задачи одинаковые но из за разного времени обновления, то обе выполнятся)
            schedule.clear()
            self.config_data = self.load_config()
            self.init_tasks()


    def run_checks(self):
        """Функция запуска проверок конфигурационного файла"""
        check_names_unique(tasks=self.config_data['tasks'])


    def setup_logger(self, folder:str='logs', log_name:str='scheduler.log'):
        """Настройка ведения логов"""
        if folder is None:
            return
        
        os.makedirs(folder, exist_ok=True)
        log_path = os.path.join(folder, log_name)
        # Настройка логирования
        logger.add(log_path, rotation="10 MB", retention="30 days", level="INFO")


    def load_config(self):
        """Чтение конфигурационного файла с задачами"""
        # Если файла конфига не существует
        if self.config_path is None or not os.path.exists(self.config_path):
            logger.info('Файла конфигурации не существует. Создаем...')
            return CONFIG_TEMPLATE
        # Файл конфига существует
        with open(self.config_path, 'r') as f:
            return json.load(f)


    def change_task_status(self, tasks, task_name, status):
        for task in tasks:
            if task['name'] == task_name:
                task['status'] = status
                break
        self.update_config()


    def update_config(self):
        """Запись конфигурации в файл"""
        with open(self.config_path, "w") as file:
            json.dump(self.config_data, file, indent=4, ensure_ascii=False)


    def run_task(self, command, args, task_name):
        """Обертка для запуска асинхронной задачи"""
        # TODO сделать возможность запуска задачи не асинхронно
        asyncio.create_task(self.run_task_async(command, args, task_name))

    def run_task_non_async(self, command, args, task_name):
        full_command = list(map(str, command.split() + args))
        
        logger.info(f"Запуск {task_name} с параметрами {full_command}")
        result = subprocess.run(full_command, capture_output=True)
        
        if result.stdout.decode():
            logger.info(f"{task_name} - Результат: {result.stdout.decode()}")
        if result.stderr.decode():
            logger.error(f'{task_name} - Ошибка: {result.stderr.decode()}')
            self.change_task_status(self.config_data['tasks'], task_name, f'Error: {result.stderr.decode()}')
    
    async def run_task_async(self, command, args, task_name):
        """Асинхронный запуск задачи"""
        full = list(map(str, command.split() + args))
        logger.info(f"[ASYNC] запуск {task_name}: {full}")
        # создаём асинхронный процесс
        proc = await asyncio.create_subprocess_exec(
            *full,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()
        if out:
            logger.info(f"{task_name} → {out.decode().strip()}")
        if err:
            logger.error(f"{task_name} Ошибка → {err.decode().strip()}")
            self.change_task_status(self.config_data['tasks'], task_name, f"Error: {err.decode().strip()}")


    def init_tasks(self):
        """Планирование выполнения задач с учетом времени и дней недели"""
        
        if self.config_data is None:
            return
                
        for task in self.config_data['tasks']:
            days, task_time = parse_datetime(task['time'])  # days - список дней недели (monday-sunday), task_time - время 
            command = task['command']
            args = task['args']
            task_name = task['name']
            
            logger.info(f'Установка задачи: {task_name}')
            
            if not days: # Если дни не указаны - ежедневно
                schedule.every().day.at(task_time).do(self.run_task, command, args, task_name)
                # self.change_task_status(self.config_data['tasks'], task_name, 'running')
                continue
            
            for weekday in days:
                getattr(schedule.every(), weekday).at(task_time).do(
                    self.run_task, command, args, task_name
                )


    async def step(self, sleep_sec):
        schedule.run_pending()
        await asyncio.sleep(sleep_sec)


    async def run(self):
        """Запуск программы"""
        
        logger.info("Планировщик запущен!")
        # стартуем watcher, он сам вызовет init_tasks() по изменению
        asyncio.create_task(self.watch_config())
        
        logger.info(f'Первичный конфиг загружен: {self.config_data}')
        schedule.clear()
        self.init_tasks()
        
        while True:
            try:
                # Добавить обновление конфига
                conf_tmp = self.config_data
                self.config_data = self.load_config()
                
                if self.config_data != conf_tmp:
                    logger.info(f'Конфиг обновлен: {self.config_data}')
                    schedule.clear()
                    self.init_tasks()
                
                await self.step(sleep_sec=1)
            except Exception as e:
                logger.error(f'Ошибка: {e}')
                await self.step(sleep_sec=1)


async def main(config, log):
    scheduler_ = Chrono(
        config_path=config,
        log_dir=log
    )
    scheduler_.run_checks()
    await scheduler_.run()


@click.command()
@click.option('--config', type=str, required=True, help='Путь к конфигу.')
@click.option('--log', type=str, default='logs', help='Директория для хранения логов.')
def cli(config, log):
    """Планировщик задач"""
    asyncio.run(main(config, log))


if __name__ == '__main__':
    cli()