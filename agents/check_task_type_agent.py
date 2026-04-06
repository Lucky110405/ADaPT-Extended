from transformers import pipeline
from logger import log_event

"""
check task type agent: check the type of task & Confidence Score

Understanding what the user is asking or wants the model to do?
and classifying if it can be responded to directly ie. is it a simple task or
a complex task where we might need more clarification on the task, and
what are the dependencies needed to complete the task ?
"""

try:
    classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-MiniLM2-L6-H768")
except Exception as e:
    print(f"Warning: Failed to load transformer model: {e}")
    print("Falling back to keyword-based classification")
    classifier = None


def check_task_type(task):
    """Classify task as simple or complex."""
    task_lower = task.lower()
    
    # Rule-based heuristic for obvious complex tasks
    complex_keywords = ["make", "build", "plan", "design", "develop", "create", "construct"]
    if any(word in task_lower for word in complex_keywords):
        log_event("process", "Task classified as complex (keyword match)")
        return "complex task"

    # Try ML-based classification if model is available
    if classifier is not None:
        try:
            labels = ["multi-step task or requiring planning", "single physical or actionable step"]
            result = classifier(task, labels, multi_label=False)
            log_event("process", "Task classified by transformer model")
            if result["labels"][0] == "multi-step task or requiring planning":
                return "complex task"
            else:
                return "simple task"
        except Exception as e:
            print(f"Error in transformer classification: {e}")
            # Fall back to simple heuristic
            return "simple task"
    
    return "simple task"


if __name__ == "__main__":
    task = input("Enter the task: ")
    task_type = check_task_type(task)
    print(f"Task Type: {task_type}")