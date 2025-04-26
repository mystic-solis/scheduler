# Scheduler

## Запуск
```sh
uv run scheduler.py --config config.json
```

```sh
uv pip install --editable .  # Установка скрипта
```



> !!! Проект можно использовать как стороннюю библиотеку


## Git Subtree: Интеграция внешнего репозитория в ваш проект

Git Subtree — это альтернатива подмодулям, позволяющая интегрировать один репозиторий в другой без необходимости отслеживания подмодулей.

### Создание поддерева
Чтобы добавить внешний репозиторий как поддерево, выполните команду:

```bash
git subtree add --prefix=путь/к/папке https://github.com/ваш_пользователь/scheduler.git main --squash
```

### Обновление поддерева
```bash
git subtree pull --prefix=путь/к/папке https://github.com/ваш_пользователь/scheduler.git main --squash
```

### Отправка изменений в поддерево
```bash
git subtree push --prefix=путь/к/папке https://github.com/ваш_пользователь/scheduler.git main
```

## Пример использования подмодуля
1. Добавление репозитория как поддерево
```bash
git subtree add --prefix=scheduler https://github.com/ваш_пользователь/scheduler.git main --squash
```

2. Обновление поддерева
```bash
git subtree pull --prefix=scheduler https://github.com/ваш_пользователь/scheduler.git main --squash
```

3. Отправка изменений в внешний репозиторий
```bash
git subtree push --prefix=scheduler https://github.com/ваш_пользователь/scheduler.git main
```




