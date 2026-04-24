from ollama import chat
from ollama import ChatResponse

"""

Planner and Decomposition Agent:

Once the model gets a full understanding of the task it can then start to plan the next steps: 
Based on the task and the extra given context, the model decomposes the task into various interconnected and dependent heirarchial subtasks.
Plans the sequence of execution of these subtasks, and how they are dependent of each other (AND/OR/NEXT/IF-THEN).

"""

def planner_and_decomposition(task, extra_context, memory):  

    response: ChatResponse = chat(model='gemma3:1b', messages=[
    {
        'role': 'user',
        'content': f''' You are a planner agent, and your work is to plan and decompose the given task into dependent heirarchial subtasks or steps, such that the result of the execution of all these subtasks will lead to the successful execution of the given orignal task.

        Your job is to break down a given task into a list of smaller, clear, actionable subtasks.

        Return output in JSON format:

        {{
        "subtasks": ["subtask 1", "subtask 2"]
        }}

        Rules:
        - Give only up to 4 subtasks
        - Each subtask must be a short string
        - Maintain the logical order between the subtasks
        - Do NOT include explanations
        - Do NOT include numbering
        - Do NOT include anything except the list
        - Ensure the output can be directly parsed using Python

        Task: {task}
        Extra Context: {extra_context}
        known info from memory: {memory}''',
    },
    ])
    subtasks = response['message']['content']
    return subtasks

if __name__ == "__main__":
    plan = planner_and_decomposition("build a house", "", {})
    print("plan:", plan)
    lines = plan.split("\n")
    subtasks = []
    for line in lines:
        line = line.strip()
        if line.startswith("-"):
            subtasks.append(line[1:].strip())

    print(f"Subtasks: {subtasks}")