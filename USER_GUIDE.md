# Task Status and Category Guide

This guide explains how to label tasks in `data/tasks.json`. Use a **status** to show where a task is in its workflow, and a **category** to describe the kind of work it involves.

## Statuses

Use one status per task:

| Status | Use it when |
|---|---|
| `Not Started` | You have not begun the task. |
| `In Progress` | You are actively working on it. |
| `Blocked` | You cannot continue until a dependency or issue is resolved. |
| `On Hold` | You have intentionally paused the task and may return to it later. |
| `Completed` | The task is finished. |

For a simple daily checklist, most tasks will move from `Not Started` to `In Progress` to `Completed`. Use `Blocked` and `On Hold` only when they explain the task's current state.

## Categories

Choose the category that best describes the task's main purpose:

| Category | Use it for | Examples |
|---|---|---|
| `Development` | Building or changing software. | Implementing a bookstore feature; adding PDF generation. |
| `Learning` | Studying a subject, tool, or technology. | Learning Spring AI or Antigravity. |
| `Practice` | Repeated exercises that build a skill. | Solving daily SQL problems. |
| `Research` | Investigating a question or evaluating options. | Researching how IRCTC handles high traffic. |
| `Maintenance` | Reviewing, fixing, or keeping existing work healthy. | Reviewing code; updating dependencies. |
| `Personal` | Personal errands or goals outside software work and learning. | Personal appointments or household tasks. |

Choose one primary category when a task could fit more than one. Keep the category broad; put specific tools, topics, or outcomes in the task title.

## Example task record

```json
{
  "title": "Solve 2 SQL problems",
  "category": "Practice",
  "status": "In Progress"
}
```

Task records also keep a `completed` boolean for the checklist and progress count. Keep it consistent with the status: use `true` with `Completed`, and `false` for every other status. Daily rollover resets both to `false` and `Not Started`. Keep category names consistent across tasks; the JSON files do not currently enforce an allowed list.
