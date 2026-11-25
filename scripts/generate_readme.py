
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
README_FILE = ROOT_DIR / "README.md"

GITHUB_USERNAME = "manasranjanmohanta"
TIMEZONE = ZoneInfo("Asia/Kolkata")


# --------------------------------------------------
# DATA LOADER
# --------------------------------------------------

def load_json(filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Missing data file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(filename, data):
    file_path = DATA_DIR / filename

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def prepare_daily_tasks():
    today = datetime.now(TIMEZONE).date().isoformat()

    tasks_data = load_json("tasks.json")

    history_file = DATA_DIR / "task_history.json"

    if history_file.exists():
        history_data = load_json("task_history.json")
    else:
        history_data = {"history": []}

    stored_date = tasks_data.get("date")

    # First-time initialization
    if not stored_date:
        tasks_data["date"] = today
        save_json("tasks.json", tasks_data)
        save_json("task_history.json", history_data)

        return tasks_data, history_data

    # No rollover required
    if stored_date == today:
        return tasks_data, history_data

    # Archive the previous day's progress
    previous_day = {
        "date": stored_date,
        "focus": tasks_data.get("focus", []),
        "tasks": tasks_data.get("tasks", [])
    }

    history = history_data.get("history", [])

    # Avoid duplicate history entries
    if not any(item.get("date") == stored_date for item in history):
        history.append(previous_day)

    # Reset checklist for the new day
    for task in tasks_data.get("tasks", []):
        task["completed"] = False

    tasks_data["date"] = today

    history_data["history"] = history

    save_json("tasks.json", tasks_data)
    save_json("task_history.json", history_data)

    print(f"Archived tasks for {stored_date}")
    print(f"Started fresh checklist for {today}")

    return tasks_data, history_data



# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def escape_markdown(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def generate_progress_bar(percentage, length=20):
    completed = round(percentage / 100 * length)
    remaining = length - completed

    return "█" * completed + "░" * remaining


def get_status_badge(status):
    colors = {
        "In Progress": "orange",
        "Completed": "brightgreen",
        "Exploring": "blue",
        "On Hold": "lightgrey"
    }

    color = colors.get(status, "lightgrey")
    return (
        f"![{status}]"
        f"(https://img.shields.io/badge/{status.replace(' ', '%20')}-{color})"
    )


# --------------------------------------------------
# TODAY'S TASKS
# --------------------------------------------------

def generate_tasks_section(data):
    tasks = data.get("tasks", [])

    total = len(tasks)
    completed = sum(
        1 for task in tasks if task.get("completed", False)
    )

    percentage = round((completed / total) * 100) if total else 0

    lines = [
        "## 📅 Today's Dashboard",
        "",
        f"**{datetime.now(TIMEZONE).strftime('%A, %d %B %Y')}**",
        "",
        "### 🎯 Today's Tasks",
        "",
        f"**Progress: {completed}/{total} tasks ({percentage}%)**",
        "",
        f"`{generate_progress_bar(percentage)}`",
        "",
    ]

    for task in tasks:
        checkbox = "x" if task.get("completed", False) else " "
        title = escape_markdown(task.get("title", "Untitled task"))
        category = escape_markdown(task.get("category", "General"))

        lines.append(f"- [{checkbox}] **{title}** · `{category}`")

    focus = data.get("focus", [])

    if focus:
        lines.extend([
            "",
            "### 🔥 Today's Focus",
            "",
            " · ".join(f"`{escape_markdown(item)}`" for item in focus)
        ])

    return "\n".join(lines)


def generate_task_history_section(data):
    history = data.get("history", [])

    # Show the latest 7 archived days
    recent_history = sorted(
        history,
        key=lambda item: item["date"],
        reverse=True
    )[:7]

    lines = [
        "## 📈 Daily Productivity History",
        "",
        "| Date | Completed | Progress |",
        "|---|---:|---:|"
    ]

    if not recent_history:
        lines.append("| No history yet | - | - |")

    for day in recent_history:
        tasks = day.get("tasks", [])

        total = len(tasks)
        completed = sum(
            1 for task in tasks
            if task.get("completed", False)
        )

        percentage = round(
            completed / total * 100
        ) if total else 0

        lines.append(
            f"| {day['date']} | {completed}/{total} "
            f"| {percentage}% |"
        )

    return "\n".join(lines)



# --------------------------------------------------
# PROJECTS
# --------------------------------------------------

def generate_projects_section(data):
    projects = data.get("projects", [])

    lines = [
        "## 🚀 What I'm Working On",
        "",
        "| Project | Description | Technologies | Status |",
        "|---|---|---|---|"
    ]

    for project in projects:
        name = escape_markdown(project.get("name", "Untitled"))
        description = escape_markdown(
            project.get("description", "")
        )

        technologies = ", ".join(
            escape_markdown(tech)
            for tech in project.get("tech", [])
        )

        status = project.get("status", "Exploring")
        badge = get_status_badge(status)

        url = project.get("url", "").strip()

        if url:
            name = f"[{name}]({url})"

        icon = project.get("icon", "💻")

        lines.append(
            f"| {icon} **{name}** | {description} "
            f"| {technologies} | {badge} |"
        )

    return "\n".join(lines)


# --------------------------------------------------
# COMPLETED MILESTONES
# --------------------------------------------------

def generate_milestones_section(data):
    milestones = data.get("milestones", [])

    completed = [
        milestone for milestone in milestones
        if milestone.get("completed", False)
    ]

    lines = [
        "## ✅ Completed Milestones",
        "",
        f"**{len(completed)} achievements recorded**",
        ""
    ]

    if not completed:
        lines.append("_No completed milestones yet._")

    for milestone in completed:
        title = escape_markdown(milestone.get("title", "Milestone"))
        description = escape_markdown(
            milestone.get("description", "")
        )

        category = escape_markdown(
            milestone.get("category", "Development")
        )

        lines.append(
            f"- [x] **{title}** — {description} "
            f"`{category}`"
        )

    return "\n".join(lines)


# --------------------------------------------------
# TECH STACK
# --------------------------------------------------

def generate_tech_stack():
    return """
## 🛠️ Tech Stack

### Languages
![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

### Backend
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=springboot&logoColor=white)
![Spring Security](https://img.shields.io/badge/Spring_Security-6DB33F?style=for-the-badge&logo=springsecurity&logoColor=white)
![Hibernate](https://img.shields.io/badge/Hibernate-59666C?style=for-the-badge&logo=hibernate&logoColor=white)
![Maven](https://img.shields.io/badge/Maven-C71A36?style=for-the-badge&logo=apachemaven&logoColor=white)

### Database & Cache
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Oracle](https://img.shields.io/badge/Oracle-F80000?style=for-the-badge&logo=oracle&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

### DevOps & Tools
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![IntelliJ IDEA](https://img.shields.io/badge/IntelliJ_IDEA-000000?style=for-the-badge&logo=intellijidea&logoColor=white)
"""


# --------------------------------------------------
# GITHUB STATISTICS
# --------------------------------------------------

def generate_github_stats():
    username = GITHUB_USERNAME

    return f"""
## 📊 GitHub Statistics

<p align="center">
  <img width="49%"
       src="https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme=tokyonight&hide_border=true&rank_icon=github"
       alt="GitHub Stats" />
  <img width="49%"
       src="https://github-readme-stats.vercel.app/api/top-langs/?username={username}&layout=compact&theme=tokyonight&hide_border=true"
       alt="Top Languages" />
</p>

<p align="center">
  <img width="75%"
       src="https://streak-stats.demolab.com?user={username}&theme=tokyonight&hide_border=true"
       alt="GitHub Streak" />
</p>
"""


# --------------------------------------------------
# FINAL README GENERATOR
# --------------------------------------------------

def generate_readme():
    tasks, task_history = prepare_daily_tasks()
    projects = load_json("projects.json")
    milestones = load_json("milestones.json")

    now = datetime.now(TIMEZONE)

    sections = [
        f"""<div align="center">

# MANAS.DEV

### Code. Create. Repeat.

**Java Backend Engineer | Software Developer | Tech Explorer**

Building scalable backend systems, exploring new technologies
and turning ideas into real-world applications.

![Profile Views](https://komarev.com/ghpvc/?username={GITHUB_USERNAME}&color=blueviolet&style=flat)
![GitHub followers](https://img.shields.io/github/followers/{GITHUB_USERNAME}?style=social)

</div>

---

> Welcome to my developer command center.
> A snapshot of what I'm building, learning and accomplishing.

""",
        generate_tasks_section(tasks),
        "",
        generate_task_history_section(task_history),
        "",
        generate_projects_section(projects),
        "",
        generate_milestones_section(milestones),
        "",
        generate_tech_stack(),
        generate_github_stats(),
        """
## 📖 Currently Learning

- Advanced Microservices Architecture
- Spring Boot 4 and Spring Cloud
- Kafka and Event-Driven Architecture
- Advanced Database Optimization
- System Design and Design Patterns
- Cloud-Native Development
- AI Agents and Workflow Automation

---

## 💡 Developer Philosophy

> Don't just make it work. Understand why it works,
> make it better, and build it to scale.

---

## 🤝 Let's Connect

- 💻 [GitHub](https://github.com/manasranjanmohanta)
- 💼 [LinkedIn](https://www.linkedin.com/)

---

<div align="center">

**BUILDING · LEARNING · IMPROVING · EVERY SINGLE DAY 🚀**

<sub>Last generated: """
        + now.strftime("%d %B %Y, %I:%M %p IST")
        + """</sub>

</div>
"""
    ]

    README_FILE.write_text(
        "\n".join(sections),
        encoding="utf-8"
    )

    print("======================================")
    print("       MANAS.DEV DASHBOARD")
    print("======================================")
    print("README generated successfully!")
    print(f"Location: {README_FILE}")

    total = len(tasks.get("tasks", []))
    completed = sum(
        1 for task in tasks.get("tasks", [])
        if task.get("completed", False)
    )

    print(f"Today's tasks: {completed}/{total} completed")
    print(f"Projects: {len(projects.get('projects', []))}")
    print(
        "Completed milestones: "
        + str(sum(
            1 for item in milestones.get("milestones", [])
            if item.get("completed", False)
        ))
    )


if __name__ == "__main__":
    generate_readme()
