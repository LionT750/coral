from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Aluno, Matricula, Avaliacao, Frequencia, Turma, Disciplina, Professor
from typing import List, Dict
import pandas as pd

class SchoolLogic:
    def __init__(self, session: Session):
        self.session = session

    def get_student_report(self, aluno_id) -> Dict:
        """Generates a complete academic report for a student."""
        aluno = self.session.query(Aluno).filter(Aluno.id == aluno_id).first()
        if not aluno:
            return None

        matriculas = self.session.query(Matricula).filter(Matricula.aluno_id == aluno_id).all()
        
        results = []
        for m in matriculas:
            # Average grade
            grades = [a.nota for a in m.avaliacoes if a.nota is not None]
            avg_grade = sum(grades) / len(grades) if grades else 0
            
            # Attendance rate
            total_days = self.session.query(Frequencia).filter(Frequencia.matricula_id == m.id).count()
            presences = self.session.query(Frequencia).filter(Frequencia.matricula_id == m.id, Frequencia.presente == True).count()
            attendance_pct = (presences / total_days * 100) if total_days > 0 else 100

            results.append({
                "Disciplina": m.turma.disciplina.nome,
                "Turma": m.turma.nome,
                "Média": round(avg_grade, 2),
                "Frequência %": round(attendance_pct, 1),
                "Status": "Aprovado" if avg_grade >= 6 and attendance_pct >= 75 else "Em curso/Reprovado"
            })

        return {
            "info": aluno,
            "academic": pd.DataFrame(results)
        }

    def get_class_performance(self, turma_id) -> pd.DataFrame:
        """Aggregates performance data for an entire class."""
        matriculas = self.session.query(Matricula).filter(Matricula.turma_id == turma_id).all()
        data = []
        for m in matriculas:
            grades = [a.nota for a in m.avaliacoes if a.nota is not None]
            avg = sum(grades) / len(grades) if grades else 0
            data.append({
                "Aluno": m.aluno.nome_completo,
                "Média Final": round(avg, 2),
                "Status": m.status.value
            })
        return pd.DataFrame(data)

    def get_general_stats(self):
        """Dashboard metrics."""
        return {
            "total_alunos": self.session.query(Aluno).count(),
            "avg_grade_global": self.session.query(func.avg(Avaliacao.nota)).scalar() or 0,
            "evasao_rate": (self.session.query(Matricula).filter(Matricula.status == "EVADIDO").count() / 
                            max(self.session.query(Matricula).count(), 1)) * 100
        }

    def get_students_at_risk(self) -> pd.DataFrame:
        """Identifies students at risk based on overall GPA or average attendance across all subjects."""
        alunos = self.session.query(Aluno).all()
        risk_list = []
        
        for al in alunos:
            matriculas = al.matriculas
            if not matriculas:
                continue
                
            total_gpa = 0
            total_attendance_pct = 0
            count = len(matriculas)
            
            for m in matriculas:
                # Subject GPA
                grades = [a.nota for a in m.avaliacoes if a.nota is not None]
                avg = sum(grades) / len(grades) if grades else 0
                total_gpa += avg
                
                # Subject Attendance
                total_days = self.session.query(Frequencia).filter(Frequencia.matricula_id == m.id).count()
                presences = self.session.query(Frequencia).filter(Frequencia.matricula_id == m.id, Frequencia.presente == True).count()
                total_attendance_pct += (presences / total_days * 100) if total_days > 0 else 100
            
            overall_gpa = total_gpa / count
            overall_attendance = total_attendance_pct / count
            
            if overall_gpa < 5.0 or overall_attendance < 75:
                risk_list.append({
                    "Aluno": al.nome_completo,
                    "Disciplinas": count,
                    "Média Geral": round(overall_gpa, 2),
                    "Frequência Média %": round(overall_attendance, 1),
                    "Motivo": "Desempenho Global Insuficiente" if overall_gpa < 5.0 else "Absenteísmo Crítico"
                })
                
        return pd.DataFrame(risk_list)

    def get_teacher_stats(self) -> pd.DataFrame:
        """Calculates performance and load metrics per teacher."""
        professores = self.session.query(Professor).all()
        stats = []
        for p in professores:
            turmas_count = len(p.turmas)
            alunos_count = self.session.query(Matricula).join(Turma).filter(Turma.professor_id == p.id).count()
            
            # Average grade of all students under this teacher
            avg_grade = self.session.query(func.avg(Avaliacao.nota))\
                .join(Matricula).join(Turma)\
                .filter(Turma.professor_id == p.id).scalar() or 0
                
            stats.append({
                "Professor": p.nome_completo,
                "Turmas": turmas_count,
                "Total Alunos": alunos_count,
                "Média das Turmas": round(avg_grade, 2)
            })
        return pd.DataFrame(stats)

    def check_recovery_eligibility(self, matricula_id) -> Dict:
        """Determines if a student needs 'Recuperação Paralela'."""
        grades = self.session.query(Avaliacao).filter(Avaliacao.matricula_id == matricula_id).all()
        # Brazilian standard: if any bimestre grade is below threshold, recovery is offered
        low_grades = [g.bimestre for g in grades if g.nota < 6.0]
        return {
            "needs_recovery": len(low_grades) > 0,
            "bimestres_criticos": low_grades
        }
