from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Table, Enum, Boolean, Date, Text
from sqlalchemy.orm import relationship, declarative_base, declared_attr
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

Base = declarative_base()

# --- Mixins and Base Patterns ---

class BaseModel:
    """Industry standard base model with UUIDs, soft delete, and audit fields."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True) # User ID or name
    updated_by = Column(String(100), nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

# --- Enums for Brazilian Context ---

class Turno(enum.Enum):
    MATUTINO = "Matutino"
    VESPERTINO = "Vespertino"
    NOTURNO = "Noturno"
    INTEGRAL = "Integral"

class StatusMatricula(enum.Enum):
    ATIVA = "Ativa"
    TRANCADA = "Trancada"
    CONCLUIDA = "Concluída"
    TRANSFERIDA = "Transferida"
    EVADIDO = "Evadido"

class Escolaridade(enum.Enum):
    FUNDAMENTAL_INCOMPLETO = "Fundamental Incompleto"
    FUNDAMENTAL_COMPLETO = "Fundamental Completo"
    MEDIO_INCOMPLETO = "Médio Incompleto"
    MEDIO_COMPLETO = "Médio Completo"
    SUPERIOR_COMPLETO = "Superior Completo"
    POS_GRADUACAO = "Pós-Graduação"

# --- Domain Models ---

class Endereco(Base, BaseModel):
    __tablename__ = "enderecos"
    logradouro = Column(String(255), nullable=False)
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False) # UF
    cep = Column(String(8), nullable=False)

class Pessoa(BaseModel):
    """Abstract-like mixin for shared person attributes."""
    nome_completo = Column(String(255), nullable=False)
    nome_social = Column(String(255))
    cpf = Column(String(11), unique=True, nullable=True)
    rg = Column(String(20))
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(255))
    telefone = Column(String(20))
    sexo = Column(String(1)) # M, F, O

class Aluno(Base, Pessoa):
    __tablename__ = "alunos"
    nis_pbf = Column(String(11)) # Para programas sociais (Bolsa Família)
    codigo_inep = Column(String(12), unique=True) # Registro MEC
    
    # Relationships
    endereco_id = Column(UUID(as_uuid=True), ForeignKey("enderecos.id"))
    endereco = relationship("Endereco")
    
    matriculas = relationship("Matricula", back_populates="aluno")
    responsaveis = relationship("ResponsavelAluno", back_populates="aluno")

class Responsavel(Base, Pessoa):
    __tablename__ = "responsaveis"
    parentesco = Column(String(50))
    
    alunos = relationship("ResponsavelAluno", back_populates="responsavel")

class ResponsavelAluno(Base, BaseModel):
    __tablename__ = "responsavel_aluno"
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("alunos.id"), nullable=False)
    responsavel_id = Column(UUID(as_uuid=True), ForeignKey("responsaveis.id"), nullable=False)
    principal = Column(Boolean, default=False)
    
    aluno = relationship("Aluno", back_populates="responsaveis")
    responsavel = relationship("Responsavel", back_populates="alunos")

class Professor(Base, Pessoa):
    __tablename__ = "professores"
    formacao = Column(Enum(Escolaridade))
    data_admissao = Column(Date)
    
    turmas = relationship("Turma", back_populates="professor")

class Disciplina(Base, BaseModel):
    __tablename__ = "disciplinas"
    nome = Column(String(100), nullable=False, unique=True)
    codigo = Column(String(20), unique=True)
    descricao = Column(Text)
    carga_horaria_anual = Column(Integer)
    
    turmas = relationship("Turma", back_populates="disciplina")

class AnoLetivo(Base, BaseModel):
    __tablename__ = "anos_letivos"
    ano = Column(Integer, unique=True, nullable=False)
    data_inicio = Column(Date)
    data_fim = Column(Date)
    aberto = Column(Boolean, default=True)

class Turma(Base, BaseModel):
    __tablename__ = "turmas"
    nome = Column(String(50), nullable=False) # Ex: 1ª Série A
    etapa_ensino = Column(String(100)) # Fundamental, Médio
    turno = Column(Enum(Turno), nullable=False)
    vagas = Column(Integer, default=40)
    
    ano_letivo_id = Column(UUID(as_uuid=True), ForeignKey("anos_letivos.id"))
    professor_id = Column(UUID(as_uuid=True), ForeignKey("professores.id"))
    disciplina_id = Column(UUID(as_uuid=True), ForeignKey("disciplinas.id"))
    
    ano_letivo = relationship("AnoLetivo")
    professor = relationship("Professor", back_populates="turmas")
    disciplina = relationship("Disciplina", back_populates="turmas")
    matriculas = relationship("Matricula", back_populates="turma")

class Matricula(Base, BaseModel):
    __tablename__ = "matriculas"
    numero_matricula = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(StatusMatricula), default=StatusMatricula.ATIVA)
    
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("alunos.id"), nullable=False)
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turmas.id"), nullable=False)
    
    aluno = relationship("Aluno", back_populates="matriculas")
    turma = relationship("Turma", back_populates="matriculas")
    avaliacoes = relationship("Avaliacao", back_populates="matricula")
    frequencias = relationship("Frequencia", back_populates="matricula")

class Avaliacao(Base, BaseModel):
    __tablename__ = "avaliacoes"
    matricula_id = Column(UUID(as_uuid=True), ForeignKey("matriculas.id"), nullable=False)
    bimestre = Column(Integer, nullable=False) # 1, 2, 3, 4
    nota = Column(Float)
    faltas = Column(Integer, default=0)
    observacao = Column(Text)
    
    matricula = relationship("Matricula", back_populates="avaliacoes")

class Frequencia(Base, BaseModel):
    __tablename__ = "frequencias"
    matricula_id = Column(UUID(as_uuid=True), ForeignKey("matriculas.id"), nullable=False)
    data = Column(Date, nullable=False, server_default=func.now())
    presente = Column(Boolean, default=True)
    justificativa = Column(String(255))
    
    matricula = relationship("Matricula", back_populates="frequencias")
