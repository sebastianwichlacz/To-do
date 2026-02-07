from models import Task


def render_task_card(task: Task) -> str:
    """Zwraca tekst karty zadania dla sortable container."""
    parts = [f"{task.priority_icon} {task.title}"]

    if task.deadline:
        dl_str = task.deadline.strftime("%d.%m")
        if task.is_overdue:
            parts.append(f"-- {dl_str} !")
        else:
            parts.append(f"-- {dl_str}")

    # ID gwarantuje unikalność tekstu (potrzebne dla drag & drop matching)
    parts.append(f"#{task.id}")

    return "  ".join(parts)
