import json
import os


def check_plan():
    """this function checks if the file plan.md exists, if it doesn't exist it gets created"""

    current_working_directory = os.getcwd()
    workdir = os.path.join(
        current_working_directory, "autogpt", "auto_gpt_workspace", "plan.md"
    )

    file_name = workdir

    if not os.path.exists(file_name):
        with open(file_name, "w") as file:
            file.write(
                """
                # 任务清单和状态:
                - [ ] 为当前计划和目标创建详细的清单
                - [ ] 最后,检查每项新任务是否完成
                ## 备注:
                - 频繁使用run_planning_cycle命令以保持此计划最新。
                        """
            )
        print(f"{file_name} created.")

    with open(file_name, "r") as file:
        return file.read()


def update_plan():
    """this function checks if the file plan.md exists, if it doesn't exist it gets created"""

    current_working_directory = os.getcwd()
    workdir = os.path.join(
        current_working_directory, "autogpt", "auto_gpt_workspace", "plan.md"
    )

    file_name = workdir

    with open(file_name, "r") as file:
        data = file.read()

    response = generate_improved_plan(data)

    with open(file_name, "w") as file:
        file.write(response)
    print(f"{file_name} updated.")

    return response


def generate_improved_plan(prompt: str) -> str:
    """Generate an improved plan using OpenAI's ChatCompletion functionality"""

    import openai

    tasks = load_tasks()

    model = os.getenv("PLANNER_MODEL", os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo"))
    max_tokens = os.getenv("PLANNER_TOKEN_LIMIT", os.getenv("FAST_TOKEN_LIMIT", 1500))
    temperature = os.getenv("PLANNER_TEMPERATURE", os.getenv("TEMPERATURE", 0.5))

    # Call the OpenAI API for chat completion
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个助手,可以改进并添加关键点到.md格式的计划中。",
            },
            {
                "role": "user",
                "content": f"根据以下任务状态更新以下计划,保持.md格式:\n{prompt}\n"
                f"在优化后的计划中包含当前任务,注意任务状态并用清单跟踪:\n{tasks}\n "
                f"修订版本应遵循当前任务的要求。 ",
            },
        ],
        max_tokens=int(max_tokens),
        n=1,
        temperature=float(temperature),
    )

    # Extract the improved plan from the response
    improved_plan = response.choices[0].message.content.strip()
    return improved_plan


def create_task(task_id=None, task_description: str = None, status=False):
    task = {"description": task_description, "completed": status}
    tasks = load_tasks()
    tasks[str(task_id)] = task

    current_working_directory = os.getcwd()
    workdir = os.path.join(
        current_working_directory, "autogpt", "auto_gpt_workspace", "tasks.json"
    )
    file_name = workdir

    with open(file_name, "w") as f:
        json.dump(tasks, f)

    return tasks


def load_tasks() -> dict:
    current_working_directory = os.getcwd()
    workdir = os.path.join(
        current_working_directory, "autogpt", "auto_gpt_workspace", "tasks.json"
    )
    file_name = workdir

    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write("{}")

    with open(file_name) as f:
        try:
            tasks = json.load(f)
            if isinstance(tasks, list):
                tasks = {}
        except json.JSONDecodeError:
            tasks = {}

    return tasks


def update_task_status(task_id):
    tasks = load_tasks()

    if str(task_id) not in tasks:
        print(f"Task with ID {task_id} not found.")
        return

    tasks[str(task_id)]["completed"] = True

    current_working_directory = os.getcwd()
    workdir = os.path.join(
        current_working_directory, "autogpt", "auto_gpt_workspace", "tasks.json"
    )
    file_name = workdir

    with open(file_name, "w") as f:
        json.dump(tasks, f)

    return f"Task with ID {task_id} has been marked as completed."
