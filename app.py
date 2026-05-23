import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Aluno, Turma, Professor
from logic import SchoolLogic
import os
import pandas as pd

# --- Config ---
st.set_page_config(page_title="Gestão Escolar Pro", layout="wide", page_icon="🏫")

db_url = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/dbname")
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

# --- Navigation ---
st.sidebar.title("🧭 Navegação")
page = st.sidebar.selectbox(
    "Ir para:", 
    ["Dashboard", "Alertas de Risco", "Relatório de Aluno", "Gestão de Turmas", "Desempenho Docente", "Diagrama do Banco", "Configurações"]
)

# --- Logic Injection ---
session = SessionLocal()
logic = SchoolLogic(session)

# --- Pages ---

if page == "Dashboard":
    st.title("📊 Painel de Indicadores")
    stats = logic.get_general_stats()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Alunos", stats["total_alunos"])
    c2.metric("Média Global", f"{stats['avg_grade_global']:.2f}")
    c3.metric("Taxa de Evasão", f"{stats['evasao_rate']:.1f}%")

    st.divider()
    st.subheader("Distribuição de Notas")
    st.info("Painel de visualização agregada. Use as outras abas para detalhes individuais.")

elif page == "Alertas de Risco":
    st.title("🚨 Alertas de Desempenho (Risco Escolar)")
    st.markdown("Filtro: Alunos com média < 5.0 ou frequência < 75% (Critérios MEC)")
    df_risk = logic.get_students_at_risk()
    if not df_risk.empty:
        st.dataframe(df_risk, use_container_width=True)
    else:
        st.success("Nenhum aluno em situação de risco imediato.")

elif page == "Relatório de Aluno":
    st.title("📄 Histórico e Desempenho do Aluno")
    alunos = session.query(Aluno).order_by(Aluno.nome_completo).all()
    aluno_map = {a.nome_completo: a.id for a in alunos}
    selected_name = st.selectbox("Selecione o Aluno:", list(aluno_map.keys()))
    
    if selected_name:
        report = logic.get_student_report(aluno_map[selected_name])
        if report:
            al = report["info"]
            st.markdown(f"### {al.nome_completo}")
            col_a, col_b = st.columns(2)
            col_a.write(f"**CPF:** {al.cpf}")
            col_a.write(f"**INEP:** {al.codigo_inep}")
            col_b.write(f"**Data Nasc:** {al.data_nascimento}")
            col_b.write(f"**Sexo:** {al.sexo}")
            
            st.dataframe(report["academic"], use_container_width=True)

elif page == "Gestão de Turmas":
    st.title("👥 Desempenho por Turma")
    turmas = session.query(Turma).all()
    turma_map = {f"{t.nome} - {t.disciplina.nome}": t.id for t in turmas}
    selected_turma = st.selectbox("Selecione a Turma:", list(turma_map.keys()))
    
    if selected_turma:
        df_turma = logic.get_class_performance(turma_map[selected_turma])
        st.dataframe(df_turma, use_container_width=True)

elif page == "Desempenho Docente":
    st.title("👨‍🏫 Estatísticas do Corpo Docente")
    df_prof = logic.get_teacher_stats()
    st.dataframe(df_prof, use_container_width=True)

elif page == "Diagrama do Banco":
    st.title("🗺️ Estrutura de Dados (Diagrama ER)")
    st.markdown("Visualização das entidades e relacionamentos do sistema escolar.")
    
    from eralchemy2 import render_er
    output_path = "schema_diagram.png"
    
    try:
        with st.spinner("Gerando diagrama..."):
            render_er(Base, output_path)
            st.image(output_path, use_container_width=True)
            with open(output_path, "rb") as file:
                st.download_button("Baixar Diagrama (PNG)", file, "escola_schema.png", "image/png")
    except Exception as e:
        st.error(f"Erro ao gerar diagrama: {e}")
        st.info("O sistema requer Graphviz instalado para renderizar o diagrama.")

elif page == "Configurações":
    st.title("⚙️ Sistema")
    st.write("Banco de Dados: Postgres 18")
    if st.button("Resetar e Re-popular Banco"):
        st.error("Funcionalidade protegida. Execute via terminal: 'docker exec coral-app-1 python3 seed_data.py'")

session.close()
