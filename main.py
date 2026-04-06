from importlib.resources import path
from agents.check_task_type_agent import check_task_type
from agents.external_help_check_agent import cross_questioning, external_help_check, online_search
from agents.planner_and_decomposition_agent import planner_and_decomposition
from executer import execute
import json
import os
from typing import Any
from langchain.tools import tool
from langgraph.func import entrypoint, task
from langchain_ollama import ChatOllama
from logger import log_event


llm = ChatOllama(model="gemma3:1b", temperature=0)


def get_ai_content(resp: Any) -> str:
    """Safely extract the AI text/content from a langgraph/langchain response.

    Handles:
    - lists/tuples of messages (takes last)
    - objects with a `content` attribute (e.g., `AIMessage`/`BaseMessage`)
    - dict-shaped responses (OpenAI-like `choices`/`message`/`content`)
    - falls back to stringifying the object
    """
    if isinstance(resp, (list, tuple)):
        msg = resp[-1]
    else:
        msg = resp

    if hasattr(msg, "content"):
        return getattr(msg, "content")

    if isinstance(msg, dict):
        if "content" in msg:
            return msg["content"]
        if "message" in msg and isinstance(msg["message"], dict) and "content" in msg["message"]:
            return msg["message"]["content"]
        choices = msg.get("choices")
        if choices and isinstance(choices, (list, tuple)):
            first = choices[0]
            m = first.get("message") if isinstance(first, dict) else first
            return get_ai_content(m)

    return str(msg)


def add_subtasks(tree, parent, subtasks):
    if parent not in tree:
        tree[parent] = {}

    for sub in subtasks:
        tree[parent][sub] = {}

def save_task_tree(new_tree):
    existing_tree = load_task_tree()

    merged_tree = {**existing_tree, **new_tree}

    with open("task_tree.json", "w") as f:
        json.dump(merged_tree, f, indent=2)

def load_task_tree():
    if os.path.exists("task_tree.json"):
        with open("task_tree.json", "r") as f:
            return json.load(f)
    return {}
    
def print_tree(tree, indent=0):
    for task, subtasks in tree.items():
        print("  " * indent + f"- {task}")
        print_tree(subtasks, indent + 1)

@task
def complex_task_handler(given_task, memory):
    log_event("process", f"Handling complex task and checking for external help: {given_task}")
    resp = external_help_check(given_task, memory).result()
    log_event("result", "External help check completed", {"task": given_task, "response": resp})
    extra_context = get_ai_content(resp)
    print(f"Extra context: {extra_context}")
    print("Plan for executing the task:")
    log_event("process", f"Planning and decomposing task: {given_task} with extra context: {extra_context}")
    plan_text = planner_and_decomposition(given_task, extra_context, memory).strip('[]')
    # subtasks = [task.strip() for task in subtasks.split(',') if task.strip()]
    lines = plan_text.split("\n")
    subtasks = []
    for line in lines:
        line = line.strip()
        if line.startswith("-"):
            subtasks.append(line[1:].strip())

    print(f"Subtasks: {subtasks}")
    log_event("result", "Subtasks generated", {"task": given_task, "subtasks": subtasks})
    return subtasks


@entrypoint()
def main_agent(given_task):
    task_tree = {}
    visited = set()
    memory = {}
    queue = [(given_task, 0)]

    while queue:

        current_task, depth = queue.pop(0)
        if current_task in visited:
            print(f"Already visited task: {current_task}, skipping to avoid cycles.")
            log_event("process", f"Skipping task: {current_task}")
            continue
        visited.add(current_task)
        print(f"Received task: {current_task} at depth {depth}")
        log_event("process", f"Processing task: {current_task}")
        task_type = check_task_type(current_task)
        print(f"Task Type: {task_type}")
        log_event("result", "Task type determined", {"task": current_task, "type": task_type})
        print(type(task_type))

        if depth > 3:
            print("⚠️ Max depth reached → forcing execution")
            log_event("process", f"Max depth reached for task: {current_task}, forcing execution")
            execute(current_task)
            continue
        if task_type == "simple task":
            print("The task is simple and can be executed directly.")
            # print("Task executed successfully.")
            # return
            result = execute(current_task)
            if result:
                print("Task executed successfully.")
                log_event("result", "Task executed successfully", {"task": current_task, "result": result})
            else:
                print("Task execution failed.")
                print("The task must be complex and requires decomposition into subtasks.")
                log_event("result", "Task execution failed, treating as complex task", {"task": current_task})
                log_event("process", f"Processing task: {current_task}")
                subtasks = complex_task_handler(current_task, memory).result()
                if not subtasks:
                    print("No subtasks → executing directly")
                    log_event("process", f"No subtasks found for task: {current_task}, so executing directly")
                    execute(current_task)
                    continue
                add_subtasks(task_tree, current_task, subtasks)
                for subtask in subtasks:
                    queue.append((subtask, depth + 1))

        elif task_type == "complex task":
            print("The task is complex and requires decomposition into subtasks.")
            log_event("process", f"Processing task: {current_task}")
            subtasks = complex_task_handler(current_task, memory).result()
            if not subtasks:
                print("No subtasks → executing directly")
                log_event("process", f"No subtasks found for task: {current_task}, so executing directly")
                execute(current_task)
                continue
            add_subtasks(task_tree, current_task, subtasks)
            for subtask in subtasks:
                queue.append((subtask, depth + 1))

    save_task_tree(task_tree)
    print("Final Task Tree:")
    print_tree(task_tree)
    print(memory)

    return True
    

if __name__ == "__main__":
    given_task = input("Enter the task: ")
    main_agent.invoke(given_task)
    print(f"The {given_task} is successfully completed, and all its subtasks are also executed successfully.")
