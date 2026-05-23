import random
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Base, Aluno, Professor, Disciplina, Turma, Matricula, 
    Avaliacao, Frequencia, AnoLetivo, Endereco, Responsavel, 
    ResponsavelAluno, Turno, StatusMatricula, Escolaridade
)
import os
import uuid

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/dbname")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# Realistic Data Constants
NAMES_M = ["João", "José", "Francisco", "Luiz", "Paulo", "Ricardo", "Fernando", "Roberto", "Lucas", "Marcelo", "Gabriel", "Rafael", "Gustavo", "Bruno", "Tiago"]
NAMES_F = ["Maria", "Ana", "Adriana", "Antonia", "Marcia", "Sandra", "Camila", "Beatriz", "Juliana", "Letícia", "Amanda", "Larissa", "Fernanda", "Patricia", "Vanessa"]
SURNAMES = ["Silva", "Oliveira", "Santos", "Souza", "Lima", "Costa", "Ferreira", "Rodrigues", "Almeida", "Nascimento"]

DISCIPLINAS_DATA = [
    ("Língua Portuguesa", "LP", 160), ("Matemática", "MAT", 160), 
    ("História", "HIS", 80), ("Geografia", "GEO", 80), 
    ("Ciências", "CIE", 80), ("Artes", "ART", 40), 
    ("Educação Física", "EDF", 80), ("Inglês", "ING", 40),
    ("Física", "FIS", 80), ("Química", "QUI", 80),
    ("Biologia", "BIO", 80), ("Sociologia", "SOC", 40),
    ("Filosofia", "FIL", 40), ("Ensino Religioso", "ER", 40)
]

GRADES = ["6º Ano", "7º Ano", "8º Ano", "9º Ano"]
SECTIONS = ["A", "B", "C"]

def generate_cpf():
    return "".join([str(random.randint(0, 9)) for _ in range(11)])

def get_random_person():
    if random.random() > 0.5:
        return f"{random.choice(NAMES_M)} {random.choice(SURNAMES)} {random.choice(SURNAMES)}", "M"
    else:
        return f"{random.choice(NAMES_F)} {random.choice(SURNAMES)} {random.choice(SURNAMES)}", "F"

def seed():
    session = Session()
    try:
        print("🛑 Resetting Database...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        print("📅 Creating Ano Letivo 2024...")
        ano_2024 = AnoLetivo(ano=2024, data_inicio=date(2024, 2, 5), data_fim=date(2024, 12, 15), aberto=True)
        session.add(ano_2024)
        session.flush()

        print("📚 Creating Disciplinas...")
        disciplinas = []
        for nome, cod, ch in DISCIPLINAS_DATA:
            d = Disciplina(nome=nome, codigo=cod, carga_horaria_anual=ch)
            session.add(d)
            disciplinas.append(d)
        session.flush()

        print("👨‍🏫 Creating 30 Professores...")
        professores = []
        for _ in range(30):
            nome, sexo = get_random_person()
            p = Professor(
                nome_completo=nome,
                sexo=sexo,
                cpf=generate_cpf(),
                data_nascimento=date(1970 + random.randint(0, 25), 1, 1),
                formacao=random.choice(list(Escolaridade))
            )
            session.add(p)
            professores.append(p)
        session.flush()

        print(f"🏫 Creating Turmas for each Subject (10+ per student)...")
        turmas_dict = {} 
        for grade in GRADES:
            for section in SECTIONS:
                for disc in disciplinas:
                    t = Turma(
                        nome=f"{grade} {section}",
                        etapa_ensino="Ensino Fundamental/Médio",
                        turno=random.choice([Turno.MATUTINO, Turno.VESPERTINO]),
                        ano_letivo_id=ano_2024.id,
                        professor_id=random.choice(professores).id,
                        disciplina_id=disc.id
                    )
                    session.add(t)
                    turmas_dict[(grade, section, disc.id)] = t
        session.flush()

        print(f"👥 Creating Alunos and Matrículas (14 Disciplinas each)...")
        for grade in GRADES:
            for section in SECTIONS:
                for i in range(20):
                    is_at_risk = random.random() < 0.35
                    
                    nome, sexo = get_random_person()
                    al = Aluno(
                        nome_completo=nome,
                        sexo=sexo,
                        cpf=generate_cpf(),
                        data_nascimento=date(2010, 1, 1),
                        codigo_inep=f"INEP{uuid.uuid4().hex[:8].upper()}"
                    )
                    session.add(al)
                    session.flush()

                    for disc in disciplinas:
                        t = turmas_dict[(grade, section, disc.id)]
                        m = Matricula(
                            numero_matricula=f"MAT-{uuid.uuid4().hex[:12].upper()}",
                            aluno_id=al.id,
                            turma_id=t.id,
                            status=StatusMatricula.ATIVA
                        )
                        session.add(m)
                        session.flush()

                        for b in range(1, 5):
                            if is_at_risk:
                                nota = random.uniform(2.0, 5.5) if random.random() > 0.5 else random.uniform(4.0, 8.0)
                                faltas = random.randint(3, 8) if random.random() > 0.5 else 0
                            else:
                                nota = random.uniform(6.5, 10.0)
                                faltas = 0
                            
                            av = Avaliacao(matricula_id=m.id, bimestre=b, nota=round(nota, 1), faltas=faltas)
                            session.add(av)
                        
                        for d in range(10):
                            presente = True
                            if is_at_risk and random.random() < 0.3:
                                presente = False
                            
                            f = Frequencia(matricula_id=m.id, data=date(2024, 3, 1) + timedelta(days=d), presente=presente)
                            session.add(f)

        print("💾 Finalizing Seeding...")
        session.commit()
        print("✅ Seed complete with Name/Gender synchronization!")

    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed()
