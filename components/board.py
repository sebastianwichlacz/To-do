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
    padding: 0;
    margin: 0 4px;
    flex: 1;  /* równa szerokość kolumn */
    min-width: 0;  /* pozwala na zmniejszanie */
}
.sortable-container-header {
    display: none;
}
.sortable-container-body {
    background-color: transparent;  /* zmień na przezroczyste */
    border-radius: 12px;
    min-height: 80px;
    padding: 8px;
    border: 2px dashed #424242;  /* ciemniejszy border dla dark mode */
}
.sortable-item, .sortable-item:hover {
    background-color: #2d2d3d;
    color: #e0e0e0;
    border: 1px solid #404050;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 4px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    transition: box-shadow 0.2s, transform 0.2s;
    line-height: 1.4;
    cursor: grab;
    width: calc(100% - 8px);  /* szerokość minus marginesy */
    box-sizing: border-box;
    word-wrap: break-word;  /* łamie długie słowa */
    overflow-wrap: break-word;
    hyphens: auto;
}
.sortable-item:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    transform: translateY(-1px);
    background-color: #353545;
}
.sortable-item:active {
    cursor: grabbing;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
"""

# STATUS_CONFIG = {
#     "To Do": {"color": "#6366f1", "icon": "📋", "bg": "#1e1b4b"},
#     "In Progress": {"color": "#f59e0b", "icon": "🔄", "bg": "#422006"},
#     "Done": {"color": "#10b981", "icon": "✅", "bg": "#064e3b"},
# }


STATUS_CONFIG = {
    "To Do": {"color": "#38bdf8", "icon": "📋", "bg": "linear-gradient(to right, #0c4a6e, #2d2d3d)"},
    "In Progress": {"color": "#fb923c", "icon": "🔄", "bg": "linear-gradient(to right, #7c2d12, #2d2d3d)"},
    "Done": {"color": "#4ade80", "icon": "✅", "bg": "linear-gradient(to right, #14532d, #2d2d3d)"},
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
    """Renderuje tablicę kanban z rozwijanymi kartami zadań."""
    filtered = _apply_filters(tasks, filters)

    # Nagłówki kolumn
    cols = st.columns(len(STATUSES))
    for col, status in zip(cols, STATUSES):
        cfg = STATUS_CONFIG[status]
        status_tasks = [t for t in filtered if t.status == status]
        count = len(status_tasks)
        
        with col:
            # Nagłówek kolumny
            st.markdown(
                f'''<div style="
                    background: {cfg["bg"]};
                    border-left: 4px solid {cfg["color"]};
                    color: {cfg["color"]};
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 0.95rem;
                    margin-bottom: 12px;
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
            
            # Zadania w tej kolumnie
            if not status_tasks:
                st.markdown(
                    '''<div style="
                        background: transparent;
                        border: 2px dashed #424242;
                        border-radius: 12px;
                        padding: 20px;
                        text-align: center;
                        color: #666;
                        font-size: 0.85rem;
                        min-height: 80px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">Brak zadań</div>''',
                    unsafe_allow_html=True,
                )
            else:
                for task in status_tasks:
                    _render_task_card(task, status)


def _render_task_card(task: Task, current_status: str) -> None:
    """Renderuje kartę zadania z możliwością rozwinięcia."""
    priority_color = PRIORITY_COLORS.get(task.priority, "#9E9E9E")
    
    # Sprawdź czy można przesunąć w lewo/prawo
    current_idx = STATUSES.index(current_status)
    can_move_left = current_idx > 0
    can_move_right = current_idx < len(STATUSES) - 1
    
    # Stan rozwinięcia (używamy session_state)
    toggle_key = f"expanded_{task.id}"
    if toggle_key not in st.session_state:
        st.session_state[toggle_key] = False
    
    # Główny kontener karty
    with st.container(border=True):
        # Górna część - zawsze widoczna
        top_cols = st.columns([1, 3, 1])
                # top_cols = st.columns([0.7, 3, 0.7, 1.2])
        
        # Strzałka lewo
        with top_cols[0]:
            if can_move_left:
                new_status = STATUSES[current_idx - 1]
                if st.button("⬅️", key=f"left_{task.id}", use_container_width=True):
                    db.update_task_status(task.id, new_status)
                    st.rerun()
        
        # Tytuł
        with top_cols[1]:
           st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    padding-top:6px;
                    font-weight:600;
                    font-size:0.95rem;
                ">
                    <span>{task.priority_icon} {task.title}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


        # # Priorytet badge
        # with top_cols[2]:
        #     st.markdown(
        #         f'<div style="text-align:right;padding-top:6px;"><span style="background:{priority_color};'
        #         f'color:white;padding:4px 10px;border-radius:12px;font-size:0.75rem;">'
        #         f'{task.priority}</span></div>',
        #         unsafe_allow_html=True,
        #     )
        
        # Strzałka prawo
        with top_cols[2]:
            if can_move_right:
                new_status = STATUSES[current_idx + 1]
                if st.button("➡️", key=f"right_{task.id}", use_container_width=True):
                    db.update_task_status(task.id, new_status)
                    st.rerun()
        

        
        # Deadline
        if task.deadline:
            dl = task.deadline.strftime("%d.%m.%Y")
            overdue_color = "#ef4444" if task.is_overdue else "#888"
            st.markdown(
                f'<div style="font-size:0.8rem;color:{overdue_color};margin-top:6px;">'
                f'📅 {dl}</div>',
                unsafe_allow_html=True,
            )
        
        # Przycisk do rozwinięcia/zwinięcia
        expand_icon = "🔽" if not st.session_state[toggle_key] else "🔼"
        expand_text = "Pokaż szczegóły" if not st.session_state[toggle_key] else "Ukryj szczegóły"
        
        if st.button(
            f"{expand_icon} {expand_text}",
            key=f"toggle_{task.id}",
            use_container_width=True,
        ):
            st.session_state[toggle_key] = not st.session_state[toggle_key]
            st.rerun()
        
        # Rozwinięta część
        if st.session_state[toggle_key]:
            st.divider()
            st.markdown("**Opis**")
            new_desc = st.text_area(
                "Opis",
                value=task.description,
                key=f"desc_{task.id}",
                label_visibility="collapsed",
                placeholder="Dodaj opis...",
                height=100,
            )
            
            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("💾 Zapisz", key=f"save_{task.id}", use_container_width=True):
                    if new_desc != task.description:
                        task.description = new_desc
                        db.update_task(task)
                        st.rerun()
            with col_del:
                if st.button("🗑️ Usuń", key=f"del_{task.id}", use_container_width=True, type="primary"):
                    db.delete_task(task.id)
                    st.rerun()
        # count = len([c for c in containers if c["header"] == status][0]["items"])
#         col.markdown(
#             f'''<div style="
#                 background: {cfg["bg"]};
#                 border-left: 4px solid {cfg["color"]};
#                 color: {cfg["color"]};
#                 padding: 12px 16px;
#                 border-radius: 8px;
#                 font-weight: 700;
#                 font-size: 0.95rem;
#                 margin-bottom: 4px;
#                 display: flex;
#                 justify-content: space-between;
#                 align-items: center;
#             ">
#                 <span>{cfg["icon"]} {status}</span>
#                 <span style="
#                     background: {cfg["color"]};
#                     color: white;
#                     border-radius: 12px;
#                     padding: 2px 10px;
#                     font-size: 0.8rem;
#                 ">{count}</span>
#             </div>''',
#             unsafe_allow_html=True,
#         )

#     # Drag & drop sortable
#     sorted_containers = sort_items(
#         containers,
#         multi_containers=True,
#         direction="vertical",
#         custom_style=SORTABLE_CSS,
#     )

#     # Wykryj zmiany statusu
#     if sorted_containers:
#         for i, status in enumerate(STATUSES):
#             for card_text in sorted_containers[i]["items"]:
#                 task = _find_task_by_card_text(tasks, card_text)
#                 if task and task.status != status:
#                     db.update_task_status(task.id, status)
#                     st.rerun()

#     # Akcje na zadaniach (edycja opisu, usuwanie) przez popovery
#     st.divider()
#     _render_task_actions(tasks, filters)


# def _render_task_actions(tasks: list[Task], filters: dict) -> None:
#     """Renderuje popovery z akcjami zadań pod tablicą, ułożone w 3 kolumny."""
#     filtered = _apply_filters(tasks, filters)

#     if not filtered:
#         st.caption("Brak zadań. Dodaj nowe zadanie w panelu bocznym.")
#         return

#     cols = st.columns(len(STATUSES))
#     for col, status in zip(cols, STATUSES):
#         with col:
#             status_tasks = [t for t in filtered if t.status == status]
#             for task in status_tasks:
#                 priority_color = PRIORITY_COLORS.get(task.priority, "#9E9E9E")
#                 with st.popover(
#                     f"{task.priority_icon} {task.title}",
#                     use_container_width=True,
#                 ):
#                     # Nagłówek
#                     st.markdown(f"### {task.title}")
#                     st.markdown(
#                         f'<span style="background:{priority_color};color:white;'
#                         f'padding:2px 10px;border-radius:12px;font-size:0.8rem;">'
#                         f'{task.priority}</span>',
#                         unsafe_allow_html=True,
#                     )

#                     # Info
#                     if task.deadline:
#                         dl = task.deadline.strftime("%d.%m.%Y")
#                         overdue = " :red[**Po terminie!**]" if task.is_overdue else ""
#                         st.markdown(f"📅 Termin: **{dl}**{overdue}")

#                     st.divider()

#                     # Edycja opisu
#                     st.markdown("**Opis**")
#                     new_desc = st.text_area(
#                         "Opis",
#                         value=task.description,
#                         key=f"desc_{task.id}",
#                         label_visibility="collapsed",
#                         placeholder="Dodaj opis zadania...",
#                         height=100,
#                     )

#                     col_save, col_del = st.columns(2)
#                     with col_save:
#                         if st.button(
#                             "💾 Zapisz",
#                             key=f"save_{task.id}",
#                             use_container_width=True,
#                         ):
#                             if new_desc != task.description:
#                                 task.description = new_desc
#                                 db.update_task(task)
#                                 st.rerun()
#                     with col_del:
#                         if st.button(
#                             "🗑️ Usuń",
#                             key=f"del_{task.id}",
#                             use_container_width=True,
#                             type="primary",
#                         ):
#                             db.delete_task(task.id)
#                             st.rerun()
