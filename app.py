"""
app.py - Streamlit Web UI for ADaPT-Extended Agent (reworked)

This file provides a resilient Streamlit UI for the project. Key features:
- Demo mode (no external LLM calls) for quick local testing
- Lazy-import of agent modules to avoid blocking the UI on import
- Non-blocking execution with a configurable timeout for LLM calls
- Safe error handling and a JSON download of results

Launch with: streamlit run app.py
"""

import json
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import streamlit as st


st.set_page_config(page_title="ADaPT-Extended Agent", page_icon="🤖", layout="wide")


def fake_decompose(task: str, context: str, max_depth: int):
    """Return a deterministic demo decomposition for offline testing."""
    start = time.time()
    plan = {
        "task": task,
        "max_depth": max_depth,
        "subtasks": [
            "Gather requirements",
            "Create design",
            "Estimate costs",
            "Execute build",
            "Review and close",
        ],
    }
    trace = [
        {"step": "classification", "result": "complex"},
        {"step": "decomposition", "items": plan["subtasks"]},
    ]
    elapsed = time.time() - start
    return {
        "status": "completed",
        "elapsed_seconds": elapsed,
        "total_llm_calls": 0,
        "used_cached_skill": False,
        "skill_cached": False,
        "final_output": "\n\n".join(plan["subtasks"]),
        "execution_trace": trace,
        "plan": plan,
    }


# def run_agent_with_timeout(task, context, max_depth, timeout_seconds=30):
#     """Lazy-import and run the OrchestratorAgent with a timeout.

#     Returns a dict-like response or raises an exception.
#     """
#     try:
#         from agents.orchestrator import OrchestratorAgent
#     except Exception as e:
#         raise RuntimeError(
#             "Could not import OrchestratorAgent. Ensure agents are available and importable."
#         ) from e

#     agent = OrchestratorAgent(max_depth=max_depth, interactive=False, use_skill_cache=True)

#     def call():
#         # agent.run is expected to return an object-like response
#         return agent.run(task=task, extra_context=context)

#     with ThreadPoolExecutor(max_workers=1) as ex:
#         fut = ex.submit(call)
#         try:
#             return fut.result(timeout=timeout_seconds)
#         except TimeoutError as te:
#             fut.cancel()
#             raise TimeoutError(f"LLM call timed out after {timeout_seconds}s") from te


def main():
    # Sidebar config
    with st.sidebar:
        st.title("⚙️ Agent Config")
        max_depth = st.number_input("Max Decomposition Depth", min_value=1, max_value=6, value=3)
        use_cache = st.checkbox("Use Skill Cache", value=True)
        interactive = st.checkbox("Interactive Clarification", value=False)
        demo_mode = st.checkbox("Demo Mode (no external LLM)", value=False)
        timeout_seconds = st.number_input("LLM timeout (s)", min_value=5, max_value=300, value=30)
        st.markdown("---")
        st.markdown("Based on ADaPT: As-Needed Decomposition and Planning with LLMs")

    st.title("🤖 ADaPT-Extended: Multi-Agent Task Decomposition")
    st.caption("Enter a task and optionally run in demo mode for offline testing.")

    col1, col2 = st.columns([3, 1])
    with col1:
        task_input = st.text_area("Enter your task:", height=140, placeholder="E.g. Build a small house")
        context_input = st.text_input("Additional context (optional):")
        run_btn = st.button("🚀 Run Agent")

    with col2:
        st.markdown("**Example Tasks**")
        for ex in [
            "Organize a 2-day tech conference for 200 people",
            "Plan a product launch for a mobile app",
            "Create a market research report on EVs",
        ]:
            if st.button(ex, key=ex):
                st.session_state.example = ex

    if "example" in st.session_state and not task_input:
        task_input = st.session_state.example

    # Results placeholders
    result_holder = st.empty()

    if run_btn:
        if not task_input:
            st.warning("Please enter a task first.")
        else:
            with st.spinner("Running..."):
                try:
                    if demo_mode:
                        response = fake_decompose(task_input, context_input, max_depth)
                    else:
                        response = run_agent_with_timeout(
                            task_input, context_input, max_depth, timeout_seconds=timeout_seconds
                        )

                    # Coerce response into a dict for UI (handle object-like responses)
                    if not isinstance(response, dict):
                        try:
                            response_dict = {
                                "status": getattr(response, "status", "completed"),
                                "elapsed_seconds": getattr(response, "elapsed_seconds", 0),
                                "total_llm_calls": getattr(response, "total_llm_calls", 0),
                                "used_cached_skill": getattr(response, "used_cached_skill", False),
                                "skill_cached": getattr(response, "skill_cached", False),
                                "final_output": getattr(response, "final_output", ""),
                                "execution_trace": getattr(response, "execution_trace", []),
                                "plan": getattr(response, "plan", {}),
                            }
                        except Exception:
                            response_dict = {"final_output": str(response)}
                    else:
                        response_dict = response

                    # Display results
                    if response_dict.get("status") == "completed":
                        st.success(f"✅ Task completed in {response_dict.get('elapsed_seconds',0):.2f}s")
                    else:
                        st.info("Task returned a non-completed status")

                    meta_cols = st.columns(4)
                    meta_cols[0].metric("LLM Calls", response_dict.get("total_llm_calls", 0))
                    meta_cols[1].metric("Time (s)", f"{response_dict.get('elapsed_seconds',0):.1f}")
                    meta_cols[2].metric("Cache Hit", "✅" if response_dict.get("used_cached_skill") else "❌")
                    meta_cols[3].metric("Skill Saved", "✅" if response_dict.get("skill_cached") else "❌")

                    st.subheader("📋 Final Output")
                    st.markdown(response_dict.get("final_output", "(no output)"))

                    with st.expander("🔍 Execution Trace", expanded=False):
                        st.json(response_dict.get("execution_trace", []))

                    with st.expander("📐 Decomposition Plan", expanded=False):
                        st.json(response_dict.get("plan", {}))

                    # Download button
                    payload = json.dumps(response_dict, indent=2)
                    st.download_button("📥 Download JSON", payload, file_name="agent_result.json")

                except TimeoutError as te:
                    st.error(str(te))
                except Exception as e:
                    st.error("Agent error: see details below.")
                    st.text(traceback.format_exc())


if __name__ == "__main__":
    main()

