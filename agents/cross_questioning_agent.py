from ollama import chat
from ollama import ChatResponse

"""

cross questioning agent:

if more context is deemed needed for complete understanding and execution of the task, then this agent will
ask clarifying questions to a LLM or if needed then from the user to get the full understanding of the task

"""

def answering(task, question):
    response: ChatResponse = chat(model='gemma3:1b', messages=[
    {
        'role': 'user',
        'content': f'''You are a clarification Question Answering Agent. you are given a task, 
        and more context is deemed necessary for the complete understanding or execution of a task, 
        so your work is to think and answer this clarification question if you can by yourself 
        or if you cannot then specify that human intervention is needed to answer it.
        if you think you need more information to answer the question, you should still specify that human intervention is needed, do NOT say "I need more information" and Do NOT add explanations.

        Instructions-
        1. If you can answer the clarifying question yourself, the write the response strictly in this format: "Q: [the question you are answering] , A: [your answer to that question]".
        2. If you cannot answer it, respond strictly only with "Human Intervention Needed."
        3. Do NOT provide any additional information other than the answer specified in the above formats.
        4. Do NOT say "I need more information" and Do NOT add explanations
        5. Use ONLY the two formats above and Nothing else

        Task: {task}
        Clarifying Question: {question}''',
    },
    ])
    answer = response['message']['content']

    if "human intervention needed." in answer.strip().lower():
        print(f"Q: {question}")
        user_answer = input("Your answer: ")
        return f"Q: {question} , A: {user_answer}"
    else:
        return answer

def cross_questioning(task, cross_questions):

    task = task
    cross_questions = cross_questions
    questions_list = cross_questions.split(" || ")
    extra_context = ""

    for question in questions_list:
        answer = answering(task, question)
        extra_context += f"\n{answer}"

    return extra_context

if __name__ == "__main__":
    task = "Plan a trip to Japan."
    cross_questions = "What is the duration of the trip? || What is your budget for the trip?"
    print(cross_questioning(task, cross_questions))