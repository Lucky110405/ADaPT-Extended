from importlib.resources import path

from agents.check_task_type_agent import check_task_type
from agents.external_help_check_agent import external_help_check
from agents.planner_and_decomposition_agent import planner_and_decomposition
from executer import execute
# from persistent_memory import PersistentMemory
import json

# pm = PersistentMemory()


task = input("Enter the task: ")
# pm.add_task_path([task]) 

def complex_task_handler(task):
    extra_context = external_help_check(task)
    print(f"Extra context: {extra_context}")
    print("Plan for executing the task:")
    subtasks = planner_and_decomposition(task, extra_context).strip('[]')
    subtasks = [task.strip() for task in subtasks.split(',') if task.strip()]
    print(f"Subtasks: {subtasks}")
    for subtask in subtasks:
        # pm.add_task_path([task, subtask.strip('"').strip("'")])
        main(subtask.strip('"').strip("'"))

def main(task):
    print(f"Received task: {task}")
    task_type = check_task_type(task)
    print(f"Task Type: {task_type}")
    print(type(task_type))


    if task_type == "simple task":
        print("The task is simple and can be executed directly.")
        # print("Task executed successfully.")
        # return
        result = execute(task)
        if result:
            print("Task executed successfully.")
            return
        else:
            print("Task execution failed.")
            print("The task must be complex and requires decomposition into subtasks.")
            complex_task_handler(task)

    elif task_type == "complex task":
        print("The task is complex and requires decomposition into subtasks.")
        complex_task_handler(task)

    # path = "persistent_memory.json"
    # with open(path, "w") as f:
    #     json.dump(pm.get_map(), f)
    # print(json.dumps(pm.get_map(), indent=2))

if __name__ == "__main__":    
    main(task)
