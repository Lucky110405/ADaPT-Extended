from ollama import chat
from ollama import ChatResponse

"""

exectuer module is responsible for executing the tasks. It takes the task as input and executes it. 
The execution for now is only a dummy, it just asks the LLM if the task is executed successfully or not. 
In future, we can replace this with actual execution code. 
The execute function returns True if the task is executed successfully, otherwise it returns False.

"""

def execute(task):

    task = task

    response: ChatResponse = chat(model='gemma3:1b', messages=[
    {
        'role': 'user',
        'content': f'''You are a exectuer agent that is responsible for executing the tasks. You will be given a task as input and you have to execute it.
        you will respond with "successful" if the task is executed successfully, otherwise you will respond with "failed".
        a task can be executed successfully if it is completly atomic that is it cannot be broken down into further subtasks.

        Instructions-

        Carefully analyze the given task.
        Decide whether the task is atomic or not.
        an atomic task is a task that cannot be broken down into further subtasks and can be executed directly.
        give the answer in a single word.
        if the task is atomic, respond with "successful".
        if the task is not atomic, respond with "failed".

        Task: {task}''',
    },
    ])
    execution_result = response['message']['content']

    if execution_result.strip().lower() == "successful":
        return True
    else:        
        return False
    
