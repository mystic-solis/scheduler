def check_names_unique(tasks):
    tasks_set = {task['name'] for task in tasks}
    tasks_list = [task['name'] for task in tasks]

    tasks_set_len = len(tasks_set)
    tasks_list_len = len(tasks_list)
    
    if tasks_set_len != tasks_list_len:
        raise Exception('Имена задач должны быть уникальными.')