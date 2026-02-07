import streamlit as st
from streamlit_sortables import sort_items

from models import Task, STATUSES, PRIORITY_COLORS
from components.task_card import render_task_card
import database as db


# Custom CSS dla sortable komponentu
SORTABLE_CSS = """
.sortable-component {
    border: none;
    padding: 0;
}
.sortable-container {
    background-color: transparent;
    padding: 4px 0;
}
.sortable-container-header {
    display: none;
}
.sortable-container-body {
    background-color: #f8f9fa;
    border-radius: 12px;
    min-height: 80px;
    padding: 8px;
    border: 2px dashed #e0e0e0;
}
.sortable-item, .sortable-item:hover {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 4px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    transition: box-shadow 0.2s, transform 0.2s;
    line-height: 1.4;
    cursor: grab;
}
.sortable-item:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    transform: translateY(-1px);
}
.sortable-item:active {
    cursor: grabbing;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
"""

STATUS_CONFIG = {
    "To Do": {"color": "#6366f1", "icon": "📋", "bg": "#eef2ff"},
    "In Progress": {"color": "#f59e0b", "icon": "🔄", "bg": "#fffbeb"},
    "Done": {"color": "#10b981", "icon": "✅", "bg": "#ecfdf5"},
}


def _apply_filters(tasks: list[Task], filters: dict) -> list[Task]:
    """Stosuje filtry do listy zadań."""
    filtered = tasks

    if filters.get("priority"):
        filtered = [t for t in filtered if t.priority in filters["priority"]]

    if filters.get("hide_done"):
        filtered = [t for t in filtered if t.status != "Done"]

    return filtered


def _build_sortable_items(tasks: list[Task], filters: dict) -> list[dict]:
    """Buduje strukturę danych dla sort_items (multi-container)."""
    filtered = _apply_filters(tasks, filters)

    containers = []
    for status in STATUSES:
        status_tasks = [t for t in filtered if t.status == status]
        items = [render_task_card(t) for t in status_tasks]
        containers.append({"header": status, "items": items})

    return containers


def _find_task_by_card_text(tasks: list[Task], card_text: str) -> Task | None:
    """Znajduje zadanie na podstawie tekstu karty."""
    for t in tasks:
        if render_task_card(t) == card_text:
            return t
    return None


def render_board(tasks: list[Task], filters: dict) -> None:
    """Renderuje tablicę kanban z drag & drop."""
    containers = _build_sortable_items(tasks, filters)

    # Nagłówki kolumn
    cols = st.columns(len(STATUSES))
    for col, status in zip(cols, STATUSES):
        cfg = STATUS_CONFIG[status]
        count = len([c for c in containers if c["header"] == status][0]["items"])
        col.markdown(
            f'''<div style="
                background: {cfg["bg"]};
                border-left: 4px solid {cfg["color"]};
                color: {cfg["color"]};
                padding: 12px 16px;
                border-radius: 8px;
                font-weight: 700;
                font-size: 0.95rem;
                margin-bottom: 4px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <span>{cfg["icon"]} {status}</span>
                <span style="
                    background: {cfg["color"]};
                    color: white;
                    border-radius: 12px;
                    padding: 2px 10px;
                    font-size: 0.8rem;
                ">{count}</span>
            </div>''',
            unsafe_allow_html=True,
        )

    # Drag & drop sortable
    sorted_containers = sort_items(
        containers,
        multi_containers=True,
        direction="vertical",
        custom_style=SORTABLE_CSS,
    )

    # Wykryj zmiany statusu
    if sorted_containers:
        for i, status in enumerate(STATUSES):
            for card_text in sorted_containers[i]["items"]:
                task = _find_task_by_card_text(tasks, card_text)
                if task and task.status != status:
                    db.update_task_status(task.id, status)
                    st.rerun()

    # Akcje na zadaniach (edycja opisu, usuwanie) przez popovery
    st.divider()
    _render_task_actions(tasks, filters)


def _render_task_actions(tasks: list[Task], filters: dict) -> None:
    """Renderuje popovery z akcjami zadań pod tablicą, ułożone w 3 kolumny."""
    filtered = _apply_filters(tasks, filters)

    if not filtered:
        st.caption("Brak zadań. Dodaj nowe zadanie w panelu bocznym.")
        return

    cols = st.columns(len(STATUSES))
    for col, status in zip(cols, STATUSES):
        with col:
            status_tasks = [t for t in filtered if t.status == status]
            for task in status_tasks:
                priority_color = PRIORITY_COLORS.get(task.priority, "#9E9E9E")
                with st.popover(
                    f"{task.priority_icon} {task.title}",
                    use_container_width=True,
                ):
                    # Nagłówek
                    st.markdown(f"### {task.title}")
                    st.markdown(
                        f'<span style="background:{priority_color};color:white;'
                        f'padding:2px 10px;border-radius:12px;font-size:0.8rem;">'
                        f'{task.priority}</span>',
                        unsafe_allow_html=True,
                    )

                    # Info
                    if task.deadline:
                        dl = task.deadline.strftime("%d.%m.%Y")
                        overdue = " :red[**Po terminie!**]" if task.is_overdue else ""
                        st.markdown(f"📅 Termin: **{dl}**{overdue}")

                    st.divider()

                    # Edycja opisu
                    st.markdown("**Opis**")
                    new_desc = st.text_area(
                        "Opis",
                        value=task.description,
                        key=f"desc_{task.id}",
                        label_visibility="collapsed",
                        placeholder="Dodaj opis zadania...",
                        height=100,
                    )

                    col_save, col_del = st.columns(2)
                    with col_save:
                        if st.button(
                            "💾 Zapisz",
                            key=f"save_{task.id}",
                            use_container_width=True,
                        ):
                            if new_desc != task.description:
                                task.description = new_desc
                                db.update_task(task)
                                st.rerun()
                    with col_del:
                        if st.button(
                            "🗑️ Usuń",
                            key=f"del_{task.id}",
                            use_container_width=True,
                            type="primary",
                        ):
                            db.delete_task(task.id)
                            st.rerun()
