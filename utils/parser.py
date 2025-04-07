from typing import Tuple, Union, List
import re


day_mapping = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday'
}
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
    
    # Парсим дни недели
    if '-' in days_part:
        # Диапазон дней (monday-friday или 0-5)
        return _parse_day(days_part, divider='-'), time_obj
    elif ',' in days_part:
        # Список дней (monday,wednesday или 1,3,5)
        return _parse_day(days_part, divider=','), time_obj
    else:
        # Один день
        return [_parse_day(days_part)], time_obj


def _parse_time(time_str: str) -> str:
    """Парсит строку времени в формате HH:MM"""
    if not is_valid_time(time_str):
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM")
    return time_str


def _parse_day(data, divider=None) -> Union[List[str], None]:
    """Парсит диапазон дней (monday-friday или 0-5)"""
    if divider:
        data = data.split(divider)
    raw_days = [_parse_single_day(single_day.strip()) for single_day in data]
    
    days = list(day_mapping.values())

    if divider == '-':
        start_day_index = days.index(raw_days[0])
        end_day_index = days.index(raw_days[-1])

        if start_day_index > end_day_index:
            raise ValueError(f"Invalid day range: {data}. Start day must be before end day")
        return days[start_day_index:end_day_index+1]
    
    elif divider == ',':
        if raw_days[0].isdigit():
            return [days[int(day)] for day in raw_days]
    return raw_days


def _parse_single_day(day: str) -> str:
    """Парсит один день (название или цифра) и возвращает название дня"""
    day = day.lower()
    # Пробуем распарсить как число
    if day.isdigit():
        day_num = int(day)
        if 0 <= day_num <= 6:
            return day_mapping[day_num]
        raise ValueError(f"Invalid day number: {day}. Must be 0-6 (0=Monday)")
    
    # Пробуем распарсить как название дня
    if day in list(day_mapping.values()):
        return day
    
    raise ValueError(f"Invalid day name: {day}. Expected weekday name (monday-friday) or number (0-6)")


if __name__ == "__main__":
    # Примеры использования
    assert parse_datetime("monday-friday 14:00") == (['monday', 'tuesday', 'wednesday', 'thursday', 'friday'], '14:00')
    assert parse_datetime("0-5 14:00") == (['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'], '14:00')
    assert parse_datetime("10:00") == (None, '10:00')
    assert parse_datetime("monday,wednesday,friday 09:00") == (['monday', 'wednesday', 'friday'], '09:00')
    assert parse_datetime("1,3,5 15:30") == (['tuesday', 'thursday', 'saturday'], '15:30')