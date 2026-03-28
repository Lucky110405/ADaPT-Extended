from ollama import chat
from ollama import ChatResponse
from agents.cross_questioning_agent import cross_questioning

"""

External Help Requirement Check Agent:

To check if more cross questioning is needed or any tool like google search is needed to solve task.
and get the required info from them.

"""

def external_help_check(task):

    task = task

    response: ChatResponse = chat(model='gemma3:1b', messages=[
    {
        'role': 'user',
        'content': f'''You are an External Help Requirement Check Agent. Your task is to analyze the given task and determine if it requires external help, such as asking clarifying questions, or using google search for some information.

        Instructions-
        1. Carefully analyze the given task.
        2. Determine if the task is clear and can be completed directly, or if it requires external help (e.g., asking clarifying questions to the user).
        3. If the task is clear and can be completed directly, respond with "no questions".
        4. If the task requires external help, or more context is deemed necessary for complete understanding and execution of the task, respond with a string which lists the clarifying questions that should be asked to the user to better understand the task.
        5. the response for the cross questions should be in this format '"first question" || "second question" || ...' and so on for each question.

        Task: {task}''',
    },
    ])
    cross_questions = response['message']['content']
    print(f"Cross Questions: {cross_questions}")

    if "no questions" in cross_questions.strip().lower():
        return ""
    else:
        return cross_questioning(task, cross_questions)