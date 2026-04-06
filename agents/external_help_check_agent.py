from langchain.tools import tool
from langgraph.func import entrypoint, task
from langchain_ollama import ChatOllama
from langgraph.graph import add_messages
from langchain.messages import (
    SystemMessage,
    HumanMessage,
    ToolCall,
)
from langchain_core.messages import BaseMessage
import requests
import json
import os
from dotenv import load_dotenv
from logger import log_event
import streamlit as st

load_dotenv()

api_key = os.getenv("LANGSEARCH_API_KEY")

"""

External Help Requirement Check Agent:

To check if more cross questioning is needed or any tool like google search is needed to solve task.
and get the required info from them.

"""


llm = ChatOllama(model="gpt-oss:20b-cloud", temperature=0)

@tool
def online_search(task, memory):
    """Perform an online search to find relevant information or context regarding the task, so that the task can be completed effectively."""

    url = "https://api.langsearch.com/v1/web-search"

    payload = json.dumps({
    "query": task,
    "freshness": "noLimit",
    "summary": True,
    "count": 2
    })
    headers = {
    'Authorization': api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    log_event("tool", "Search tool used", {"query": task})
    search_result = response.text
    memory[task] = search_result
    log_event("result", "Search result", search_result)
    return search_result

@tool
def cross_questioning(task, memory):
    """ cross questioning agent: 
    if more context is deemed needed for complete understanding and execution of the task, then this agent will ask clarifying questions to a LLM or if needed then from the user to get the full understanding of the task
    """

    cross_questions = generate_cross_questions(task, memory)
    if "no questions" in cross_questions.lower():
        return "no extra context needed"
    extra_context = answering(task, cross_questions, memory)
    memory[cross_questions] = extra_context
    log_event("tool", "Cross-questioning tool used", {"task": task, "questions": cross_questions, "context": extra_context})
    return extra_context


tools = [online_search, cross_questioning]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = llm.bind_tools(tools)


def generate_cross_questions(task, memory):
    messages = [
        {
            'role': 'user',
            'content': f"""You are a cross-question generation agent. you are given a task, and more context is deemed necessary for the complete understanding or execution of a task, so your task is to generate clarifying questions that can be asked to the user to get more context about the task.
            if you think you need more information to generate the clarifying questions, you should still generate the clarifying questions, do NOT say "I need more information" and Do NOT add explanations.

            Instructions-
            1. If you can generate clarifying questions yourself, then write the response strictly in this format: "first question" || "second question" for each question.
            2. ask only one question at most that you think are the most important to clarify the task and get more context about it.
            3. If you cannot generate it, respond strictly only with "no questions".
            4. Do NOT provide any additional information other than the answer specified in the above formats.
            5. Do NOT say "I need more information" and Do NOT add explanations.
            6. Use ONLY the two formats above and Nothing else.

            Task: {task}
            Known Information from Memory: {memory}""",
        }
    ]
    cross_questions = llm.invoke(messages).content.strip()
    print(f"Cross Questions: {cross_questions}")
    log_event("question", "Cross question asked", {"task": task, "questions": cross_questions})
    return cross_questions

def answering(task, questions, memory):
    messages = [
        {
            'role': 'user',
            'content': f"""You are a clarification Question Answering Agent. you are given a task, and some cross questions on it since more context is deemed necessary for the complete understanding or execution of the task, so your work is to think and answer these clarification cross questions by yourself if you can or if you cannot then specify that human intervention is needed to answer it.
            
            if you think you need more information to answer the question, you should still specify that human intervention is needed, do NOT say \"I need more information\" and Do NOT add explanations.

            Instructions-
            1. If you can answer the clarifying question yourself, then write the response strictly in this format: "Q: [the question you are answering] , A: [your answer to that question]".
            2. If you cannot answer it, respond strictly only with "Human Intervention Needed."
            3. Do NOT provide any additional information other than the answer specified in the above formats.
            4. Do NOT say "I need more information" and Do NOT add explanations
            5. Use ONLY the two formats above and Nothing else.

            Task: {task}
            Clarifying Question: {questions}""",
        }
    ]

    resp = llm.invoke([HumanMessage(content=messages[0]['content'])])

    # normalize response text
    text = getattr(resp, 'content', None)
    if text is None:
        text = str(resp)
    text = text.strip()

    # If model explicitly requests human intervention, ask the user for an answer
    if "human intervention needed." in text.lower():
        print(f"Model requests human intervention for question(s): {questions}")
        log_event("question", "Model requests human intervention", {"task": task, "questions": questions})
        st.session_state.pending_question = questions
        st.stop()  # pause execution
        # user_answer = input("Please provide the answer: ")
        user_answer = st.session_state.get("answers", {})
        return f"Q: {questions} , A: {user_answer}"

    # Human-in-the-loop review: show model's proposed answer and allow accept/override
    print("Model's proposed answer:\n", text)
    log_event("answer", "Model's proposed answer:", {"task": task, "questions": questions, "proposed_answer": text})
    st.write("Model's proposed answer:\n" + text)
    st.session_state.pending_question = "Do you accept the model's proposed answer? (Y/N)"
    st.stop()  # pause execution
    # review = input("Accept model answer? (y/N): ").strip().lower()
    review = st.session_state.get("answers", {}).get(st.session_state.pending_question, "").strip().lower()
    if review in ("y", "yes"):
        # ensure returned format matches expected "Q: ..., A: ..." when possible
        if text.lower().startswith("q:"):
            return text
        return f"Q: {questions} , A: {text}"
    # If user rejects, collect their answer
    # user_answer = input("Please provide the correct answer: ")
    st.session_state.pending_question = questions
    st.stop()
    user_answer = st.session_state.get("answers", {}).get(st.session_state.pending_question, "")

    log_event("answer", "User answered", {"task": task, "answer": user_answer})
    return f"Q: {questions} , A: {user_answer}"


@task
def call_tool(tool_call: ToolCall):
    """Performs the tool call"""
    tool = tools_by_name[tool_call["name"]]
    return tool.invoke(tool_call)

@task
def call_llm(messages: list[BaseMessage]):
    """LLM decides whether to call a tool or not for extra context for a given task, and if it needs to call a tool then it calls the appropriate tool and gets the required info from it."""

    return model_with_tools.invoke(
        [
            SystemMessage(
                content="You are a helpful assistant tasked with deciding which tool to call for extra context for a given task."
            )
        ]
        + messages
    )

@task
def external_help_check(task, memory):
    
    messages = [HumanMessage(content=f"""
                             You are an External Help Requirement Check Agent. Your task is to analyze the given task and determine if it requires external help, such as asking clarifying questions, or using google search for some information.

                            Instructions-
                            1. Carefully analyze the given task.
                            2. Determine if the task is clear and can be completed directly, or if it requires external help (e.g., asking clarifying questions to the user).
                            3. If the task is clear and can be completed directly, respond with "no extra context needed".
                            4. otherwise if the task requires external help, or more context is deemed necessary for complete understanding and execution of the task, call the appropriate tool.
                            5. Use the tools effectively to gather the necessary information or context to complete the task, and respond with the gathered extra context.
                            6. Provide the gathered information as the output.

                            Task: {task}
                            known info from memory: {memory}
                            """
    )]
    
    model_response = call_llm(messages).result()

    while True:
        if not model_response.tool_calls:
            break

        # Execute tools
        tool_result_futures = [
            call_tool(tool_call) for tool_call in model_response.tool_calls
        ]
        tool_results = [fut.result() for fut in tool_result_futures]
        messages = add_messages(messages, [model_response, *tool_results])
        model_response = call_llm(messages).result()

    messages = add_messages(messages, model_response)
    return messages
    
