from ollama import chat
from ollama import ChatResponse
from transformers import pipeline

"""

check task type agent: check the type of task & Confidence Score

Understanding what the user is asking or wants the model to do?
and classifying if it can be responded to directly ie. is it a simple task or
a complex task where we might need more clarification on the task, and
what are the dependencies needed to complete the task ?

"""
classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-MiniLM2-L6-H768")     


def check_task_type(task):
    task_lower = task.lower()
    if any(word in task_lower for word in ["make", "build", "plan", "design", "develop"]):
        return "complex task"

    labels=["multi-step task or requiring planning", "single physical or actionable step"]
    result = classifier(task, labels, multi_label=False)
    print("module check_task_type_agent executed")
    if result["labels"][0] == "multi-step task or requiring planning":
        return "complex task"
    else:
        return "simple task"
    # return result['labels'][0]


# def check_task_type(task):
    task = task

    response: ChatResponse = chat(model='gemma3:1b', messages=[
    {
        'role': 'user',
        'content': f'''You are a Task Complexity Classifier. Your job is to analyze the given task and determine whether it is a Simple Task or a Complex Task.

        Definitions-

        Simple Task:
        A task that can be completed directly without breaking it into smaller subtasks. It involves a single clear action or straightforward execution.

        Complex Task:
        A task that requires decomposition into multiple subtasks, steps, or stages to be completed successfully. It may involve planning, dependencies, multiple objectives, or sequential actions.

        Instructions-

        Carefully analyze the given task.
        Decide whether the task is Simple or Complex based on the definitions.
        give the answer in a single word.
        Do NOT decompose the task — only classify it.

        Task: {task}''',
    },
    ])
    task_type = response['message']['content']
    return task_type

if __name__ == "__main__":
    task = input("Enter the task: ")
    task_type = check_task_type(task)
    print(f"Task Type: {task_type}")