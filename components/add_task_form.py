import streamlit as st
from datetime import datetime
from models import Task, PRIORITIES


def render_add_task_form() -> Task | None:
    """Renderuje formularz dodawania zadania. Zwraca Task jeśli formularz został wysłany."""
    with st.form("add_task_form", clear_on_submit=True):
        st.subheader("Nowe zadanie")

        title = st.text_input("Tytuł", placeholder="Co trzeba zrobić?")

        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priorytet", PRIORITIES, index=1)
        with col2:
            deadline = st.date_input("Termin", value=None)

        description = st.text_area(
            "Opis (opcjonalnie)",
            placeholder="Dodaj szczegóły...",
            height=80,
        )

        submitted = st.form_submit_button(
            "➕ Dodaj zadanie",
            use_container_width=True,
            type="primary",
        )

        if submitted and title.strip():
            return Task(
                title=title.strip(),
                status="To Do",
                priority=priority,
                description=description.strip(),
                deadline=deadline,
                created_at=datetime.now().isoformat(),
            )
        elif submitted:
            st.warning("Tytuł zadania nie może być pusty.")

    return None


def render_board(tasks: list[Task], filters: dict) -> None:
    """Renderuje tablicę kanban z możliwością przesuwania zadań strzałkami."""
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
                    _render_task_card_with_actions(task, status, filtered)


def _render_task_card_with_actions(task: Task, current_status: str, all_tasks: list[Task]) -> None:
    """Renderuje kartę zadania z możliwością edycji i przesuwania."""
    priority_color = PRIORITY_COLORS.get(task.priority, "#9E9E9E")
    
    # Sprawdź czy można przesunąć w lewo/prawo
    current_idx = STATUSES.index(current_status)
    can_move_left = current_idx > 0
    can_move_right = current_idx < len(STATUSES) - 1
    
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

        # Przyciski przesuwania
        st.markdown("**Przenieś zadanie**")
        move_cols = st.columns([1, 1])
        
        with move_cols[0]:
            if can_move_left:
                new_status = STATUSES[current_idx - 1]
                if st.button(
                    f"⬅️ {new_status}",
                    key=f"left_{task.id}",
                    use_container_width=True,
                ):
                    db.update_task_status(task.id, new_status)
                    st.rerun()
            else:
                st.button(
                    "⬅️",
                    key=f"left_disabled_{task.id}",
                    disabled=True,
                    use_container_width=True,
                )
        
        with move_cols[1]:
            if can_move_right:
                new_status = STATUSES[current_idx + 1]
                if st.button(
                    f"{new_status} ➡️",
                    key=f"right_{task.id}",
                    use_container_width=True,
                ):
                    db.update_task_status(task.id, new_status)
                    st.rerun()
            else:
                st.button(
                    "➡️",
                    key=f"right_disabled_{task.id}",
                    disabled=True,
                    use_container_width=True,
                )

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