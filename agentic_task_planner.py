import ollama
import json
import os
import re

# Function to interact with the LLM
def get_llm_response(prompt):
    response = ollama.generate(
        model="llama3.1",
        prompt=prompt,
        options={"temperature": 0.5}  # Lower temperature for deterministic output
    )
    raw_response = response['response'].strip()
    print(f"Raw LLM response: {raw_response}")  # Debug print
    # Extract JSON (list or object) from code blocks or standalone
    json_match = re.search(r'(\[.*?\]|\{.*?\})', raw_response, re.DOTALL)
    if json_match:
        extracted_json = json_match.group(0)
        print(f"Extracted JSON: {extracted_json}")  # Debug print
        return extracted_json
    print("No JSON found, returning raw response")
    return raw_response  # Fallback to raw if no JSON found

# Agentic decision-making: Prioritize tasks
def prioritize_tasks(tasks, goal):
    prioritized = []
    for task in tasks:
        priority = 1
        if "urgent" in task.lower() or any(word in task.lower() for word in goal.lower().split()):
            priority = 0
        prioritized.append((task, priority))
    return [task for task, _ in sorted(prioritized, key=lambda x: x[1])]

# Main agent function
def task_planner(goal):
    # Generate tasks
    prompt = f"""
    You are a task planning assistant. Given the goal: "{goal}",
    break it down into 3-5 specific tasks. Each task must be a short sentence.
    Return *only* a valid JSON list, e.g., ["Task 1", "Task 2", "Task 3"].
    Do not include any extra text, explanations, comments, or code blocks (e.g., ```json).
    Example: ["Study math for 2 hours", "Read history chapters", "Practice coding"]
    """
    try:
        tasks_json = get_llm_response(prompt)
        tasks = json.loads(tasks_json)
    except json.JSONDecodeError as e:
        print(f"Error: LLM did not return valid JSON: {e}. Using fallback tasks.")
        tasks = ["Review goal", "Create plan", "Execute tasks"]

    # Prioritize tasks
    prioritized_tasks = prioritize_tasks(tasks, goal)

    # Generate schedule
    schedule_prompt = f"""
    You are a scheduling assistant. Given the prioritized tasks: {prioritized_tasks},
    create a simple weekly schedule. Assign tasks to days (Monday to Sunday).
    Return *only* a valid JSON object, e.g., {{"Monday": ["Task 1"], "Tuesday": ["Task 2"], "Wednesday": [], "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []}}.
    Do not include any extra text, explanations, comments, or code blocks (e.g., ```json
    Example: {{"Monday": ["Study math"], "Tuesday": ["Read history"], "Wednesday": [], "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []}}
    """
    try:
        schedule_json = get_llm_response(schedule_prompt)
        schedule = json.loads(schedule_json)
    except json.JSONDecodeError as e:
        print(f"Error: LLM did not return valid JSON: {e}. Using fallback schedule.")
        schedule = {"Monday": prioritized_tasks[:2], "Tuesday": prioritized_tasks[2:], "Wednesday": [], "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []}

    # Save to file
    output = {
        "goal": goal,
        "tasks": prioritized_tasks,
        "schedule": schedule
    }
    with open("task_plan.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Plan saved to task_plan.json")

    return output

# Run the agent
if __name__ == "__main__":
    user_goal = input("Enter your goal (e.g., Plan a study schedule for this week): ")
    plan = task_planner(user_goal)
    print("\nGenerated Plan:")
    print(json.dumps(plan, indent=2))