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

