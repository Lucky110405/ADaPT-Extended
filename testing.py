
# from langchain_ollama import ChatOllama

# llm = ChatOllama(
#     model="gemma3:1b",
#     temperature=0,
# )


# def generate_cross_questions(task):
#     messages = [
#         {
#             'role': 'user',
#             'content': f"""You are a cross-question generation agent. you are given a task, and more context is deemed necessary for the complete understanding or execution of a task, so your task is to generate clarifying questions that can be asked to the user to get more context about the task.
#             if you think you need more information to generate the clarifying questions, you should still generate the clarifying questions, do NOT say "I need more information" and Do NOT add explanations.

#             Instructions-
#             1. If you can generate clarifying questions yourself, then write the response strictly in this format: "first question" || "second question" for each question.
#             2. ask only two question at most that you think are the most important to clarify the task and get more context about it.
#             3. If you cannot generate it, respond strictly only with "no questions".
#             4. Do NOT provide any additional information other than the answer specified in the above formats.
#             5. Do NOT say "I need more information" and Do NOT add explanations.
#             6. Use ONLY the two formats above and Nothing else.

#             Task: {task}""",
#         }
#     ]
#     cross_questions = llm.invoke(messages).content
#     print(f"Cross Questions: {cross_questions}")
#     return cross_questions


# # # Augment the LLM with tools
# # tools = [add, multiply, divide]
# # tools_by_name = {tool: tool for tool in tools}

# # print(tools_by_name)

# res = generate_cross_questions("write a python function to calculate the factorial of a number") 
# print(type(res))

from transformers import pipeline

def check_task_type(task):
    task = task
    labels=["complex task", "simple task"]
    classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-MiniLM2-L6-H768")     
    result = classifier(task, labels, multi_label=False)
    print("module check_task_type_agent executed")
    # if result["labels"][0] == "complex task" and result["scores"][0] > 0.51:
    #     return "complex task"
    # else:
    #     return "simple task"
    return result

print(check_task_type("make me some pancakes"))