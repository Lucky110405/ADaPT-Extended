from ollama import chat
from ollama import ChatResponse

"""Cross-questioning helper agent.

Provides `cross_questioning(task, cross_questions)` and `answering(task, question)`.

This module prefers asking the user interactively when run in a terminal.
"""

def answering(task, question):
    """Attempt to answer a clarifying question.

    This implementation prompts the user for an answer. If the user leaves
    the input blank, it returns the sentinel string indicating human
    intervention is needed.
    """
    prompt = f"Clarifying Question: {question}\nProvide an answer (leave blank if you cannot answer): "
    try:
        user_answer = input(prompt).strip()
    except Exception:
        # Non-interactive environment: indicate human intervention
        return "Human Intervention Needed."

    if not user_answer:
        return "Human Intervention Needed."
    return f"Q: {question} , A: {user_answer}"


def cross_questioning(task, cross_questions):
    """Run cross-questioning for a task.

    `cross_questions` is expected as a string with questions separated by
    " || ". Returns a joined string of answers (one per question).
    """
    if not cross_questions:
        return ""
    questions = [q.strip() for q in cross_questions.split("||") if q.strip()]
    answers = []
    for q in questions:
        ans = answering(task, q)
        answers.append(ans)
    return "\n".join(answers)


if __name__ == "__main__":
    task = "Plan a trip to Japan."
    cross_questions = "What is the duration of the trip? || What is your budget for the trip?"
    print(cross_questioning(task, cross_questions))


if __name__ == "__main__":
    task = "Plan a trip to Japan."
    cross_questions = "What is the duration of the trip? || What is your budget for the trip?"
    print(cross_questioning(task, cross_questions))