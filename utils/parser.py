from typing import Tuple, Union, List
import re


time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')


def is_valid_time(time_str: str) -> bool:
    return bool(time_pattern.fullmatch(time_str))


def parse_datetime(time_str: str) -> Tuple[Union[List[int], None], str]:
    """
    Парсит строку времени и возвращает дни недели и время.

    Поддерживаемые форматы:
    - "monday-friday 14:00"
    - "0-5 14:00" (0=понедельник, 6=воскресенье)
    - "10:00" (каждый день в это время)
    - "monday,wednesday,friday 09:00"
    - "1,3,5 15:30" (дни недели цифрами)

    :param time_str: Строка с временем и днями недели
    :return: Кортеж (список дней недели, время) Если дни не указаны - возвращает (None, str)
    """
    # Разделяем дни и время
    parts = re.split(r'\s+', time_str.strip(), maxsplit=1)
    if len(parts) == 1:
        # Только время (например "10:00")
        return None, _parse_time(parts[0])
    
    days_part, time_part = parts
    time_obj = _parse_time(time_part)
    
    # TODO переделать на конкретно один вид работы только с разделителем
    # Парсим дни недели
    if '-' in days_part:
        # Диапазон дней (monday-friday или 0-5)
        return _parse_day_range(days_part), time_obj
    elif ',' in days_part:
        # Список дней (monday,wednesday или 1,3,5)
        return _parse_day_list(days_part), time_obj
    else:
        # Один день
        return [_parse_single_day(days_part)], time_obj


def _parse_time(time_str: str) -> str:
    """Парсит строку времени в формате HH:MM"""
    if not is_valid_time(time_str):
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM")
    return time_str


def _parse_day_range(day_range: str) -> List[int]:
    """Парсит диапазон дней (monday-friday или 0-5)"""
    start, end = day_range.split('-')
    start_day = _parse_single_day(start.strip())
    end_day = _parse_single_day(end.strip())
    
    if start_day > end_day:
        raise ValueError(f"Invalid day range: {day_range}. Start day must be before end day")
    
    return list(range(start_day, end_day + 1))


def _parse_day_list(day_list: str) -> List[int]:
    """Парсит список дней (monday,wednesday или 1,3,5)"""
    return [_parse_single_day(day.strip()) for day in day_list.split(',')]


def _parse_single_day(day: str) -> int:
    """Парсит один день (название или цифра) и возвращает номер дня (0-6)"""
    day = day.lower()
    # Пробуем распарсить как число
    if day.isdigit():
        day_num = int(day)
        if 0 <= day_num <= 6:
            return day_num
        raise ValueError(f"Invalid day number: {day}. Must be 0-6 (0=Monday)")
    
    # Пробуем распарсить как название дня
    day_mapping = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }
    if day in day_mapping:
        return day_mapping[day]
    
    raise ValueError(f"Invalid day name: {day}. Expected weekday name (monday-friday) or number (0-6)")


if __name__ == "__main__":
    # Примеры использования
    print(parse_datetime("monday-friday 14:00"))  # ([0, 1, 2, 3, 4], 14:00)
    print(parse_datetime("0-5 14:00"))           # ([0, 1, 2, 3, 4, 5], 14:00)
    print(parse_datetime("10:00"))               # (None, 10:00)
    print(parse_datetime("monday,wednesday,friday 09:00"))  # ([0, 2, 4], 09:00)
    print(parse_datetime("1,3,5 15:30"))         # ([1, 3, 5], 15:30)