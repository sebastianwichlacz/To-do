import streamlit as st
import pandas as pd
import plotly.express as px

from models import Task, PRIORITIES, STATUSES
import database as db
from components.add_task_form import render_add_task_form


def render_sidebar(tasks: list[Task]) -> dict:
    """Renderuje sidebar z formularzem, filtrami i statystykami. Zwraca filtry."""
    with st.sidebar:
        st.markdown(
            '<h1 style="text-align:center;margin-bottom:0;">📌 Kanban</h1>',
            unsafe_allow_html=True,
        )
        st.divider()

        # Formularz dodawania
        new_task = render_add_task_form()
        if new_task:
            db.add_task(new_task)
            st.rerun()

        st.divider()

        # Filtry
        st.subheader("🔍 Filtry")

        selected_priorities = st.multiselect(
            "Priorytet",
            PRIORITIES,
            default=[],
            placeholder="Wszystkie",
        )

        hide_done = st.checkbox("Ukryj ukończone")

        filters = {
            "priority": selected_priorities,
            "hide_done": hide_done,
        }

        st.divider()

        # Statystyki
        _render_stats(tasks)

    return filters


def _render_stats(tasks: list[Task]) -> None:
    """Renderuje statystyki w sidebarze."""
    st.subheader("📊 Statystyki")

    if not tasks:
        st.caption("Brak zadań.")
        return

    total = len(tasks)
    done = len([t for t in tasks if t.status == "Done"])
    in_progress = len([t for t in tasks if t.status == "In Progress"])
    overdue = len([t for t in tasks if t.is_overdue])

    col1, col2 = st.columns(2)
    col1.metric("Wszystkie", total)
    col2.metric("Ukończone", done)

    col3, col4 = st.columns(2)
    col3.metric("W trakcie", in_progress)
    col4.metric("Po terminie", overdue)

    if total > 0:
        progress = done / total
        st.progress(progress, text=f"Postęp: {progress:.0%}")

    # Wykres statusów
    status_counts = {s: len([t for t in tasks if t.status == s]) for s in STATUSES}
    df_status = pd.DataFrame(
        {"Status": status_counts.keys(), "Liczba": status_counts.values()}
    )

    if df_status["Liczba"].sum() > 0:
        colors = {"To Do": "#6366f1", "In Progress": "#f59e0b", "Done": "#10b981"}
        fig = px.pie(
            df_status,
            values="Liczba",
            names="Status",
            color="Status",
            color_discrete_map=colors,
            hole=0.45,
        )
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=180,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=11),
        )
        fig.update_traces(
            textinfo="label+value",
            textfont_size=11,
            marker=dict(line=dict(color="#1a1a2e", width=2)),
        )
        st.plotly_chart(fig, use_container_width=True)