# from transformers import pipeline

# task = "fix a air conditioner that is not cooling properly"
# labels=["complex task", "simple task"]

# classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-MiniLM2-L6-H768")     
# result = classifier(task, labels, multi_label=False)
# print(result)

# print(result['labels'][0])


def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b


# Augment the LLM with tools
tools = [add, multiply, divide]
tools_by_name = {tool: tool for tool in tools}

print(tools_by_name)