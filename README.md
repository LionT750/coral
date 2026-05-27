# Coral - Sistema de Gestão Escolar (Protótipo)

Este projeto é um painel de indicadores (dashboard) para gestão escolar de redes públicas, desenvolvido com **Streamlit**, **SQLAlchemy** e **PostgreSQL**. Ele permite visualizar o desempenho de alunos, turmas e docentes, além de identificar alunos em situação de risco escolar com base em critérios do MEC.

## 🚀 Como Executar o Projeto

A forma mais simples de rodar o projeto é utilizando o **Docker**, que já configura o banco de dados e a aplicação automaticamente.

### 📋 Pré-requisitos

Certifique-se de ter instalado em sua máquina:
1. **Docker**: [Guia de Instalação do Docker](https://docs.docker.com/get-docker/)
2. **Docker Compose**: Geralmente já vem incluído na instalação do Docker Desktop.

---

### 🛠️ Passo a Passo para Instalação

#### 1. Clonar o Repositório
Abra seu terminal e clone este repositório:
```bash
git clone <url-do-repositorio>
cd coral
```

#### 2. Subir o Ambiente com Docker
Execute o comando abaixo para construir a imagem da aplicação e iniciar os containers (banco de dados e app):
```bash
docker-compose up -d --build
```
*O parâmetro `-d` roda os containers em segundo plano.*

#### 3. Criar e Popular o Banco de Dados
Com os containers rodando, você precisa criar as tabelas e inserir os dados iniciais (seed). Execute o comando:
```bash
docker exec -it coral-app-1 python seed_data.py
```
*Nota: Se o nome do seu container for diferente (verifique com `docker ps`), ajuste `coral-app-1` para o nome correto.*

#### 4. Acessar a Aplicação
Após o processo acima, o sistema estará disponível no seu navegador:
🔗 **[http://localhost:8501](http://localhost:8501)**

---

## 📊 Funcionalidades do Dashboard

- **Dashboard Geral**: Estatísticas globais (total de alunos, média e evasão).
- **Alertas de Risco**: Identificação automática de alunos com média < 5.0 ou frequência < 75%.
- **Relatório de Aluno**: Busca detalhada por CPF/INEP e histórico acadêmico.
- **Gestão de Turmas**: Comparativo de desempenho entre diferentes classes.
- **Desempenho Docente**: Métricas de aproveitamento por professor.
- **Diagrama do Banco**: Visualização técnica do modelo de dados (ER).

---

## 🗄️ Estrutura do Projeto

- `app.py`: Interface principal do Streamlit.
- `logic.py`: Camada de lógica de negócio e consultas SQL (queries).
- `models.py`: Definição das tabelas do banco de dados (SQLAlchemy ORM).
- `seed_data.py`: Script para geração de dados fictícios realistas.
- `docker-compose.yml`: Orquestração dos containers Docker.

---

## 🔧 Manutenção e Comandos Úteis

**Ver logs da aplicação:**
```bash
docker-compose logs -f app
```

**Parar o sistema:**
```bash
docker-compose down
```

**Resetar banco de dados (limpar tudo):**
Basta rodar o comando do Passo 3 novamente. O script `seed_data.py` está configurado para apagar e recriar as tabelas.

---

