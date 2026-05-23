# 🏫 Protótipo de Esquema de Banco de Dados: Escola Pública Brasileira

Este projeto é uma demonstração técnica de uma modelagem de dados (ORM) projetada para representar a estrutura complexa de uma instituição de ensino pública no Brasil, seguindo padrões e nomenclaturas do Censo Escolar (MEC).

## 🎯 Objetivo do Projeto
O foco central deste trabalho é a **arquitetura de dados**. Ele serve como uma prova de conceito de como entidades educacionais (Alunos, Professores, Matrículas, Turmas, Disciplinas) podem ser relacionadas de forma robusta e escalável, utilizando padrões modernos de indústria (como UUIDs e trilhas de auditoria).

## 🏗️ Estrutura do Esquema (Modelagem)
A modelagem abrange as seguintes áreas do domínio escolar:
*   **Identificação:** Pessoas (Alunos, Professores, Responsáveis) com validação de documentos (CPF, RG, INEP).
*   **Acadêmico:** Organização por Anos Letivos, Disciplinas e Turmas (com suporte a diferentes turnos).
*   **Vida Escolar:** Fluxo completo de Matrícula, Registro de Frequência Diária e Avaliações Bimestrais.
*   **Infraestrutura:** Gestão de Endereços vinculados a múltiplas entidades.

## 🛠️ Padrões Implementados
*   **UUID v4:** Identificadores únicos universais para todas as tabelas.
*   **Soft Delete:** Registro lógico de exclusão para preservação de integridade histórica.
*   **Audit Fields:** Carimbos de data/hora (`created_at`, `updated_at`) automáticos em todos os registros.
*   **Relacionamentos Fortes:** Chaves estrangeiras e integridade referencial rigorosa.

## 📊 Visualização
Embora o foco seja o banco de dados, o projeto inclui uma interface Streamlit para:
1.  **Visualizar o Diagrama ER:** Gerar e exportar graficamente o mapa de relações entre as tabelas.
2.  **Validar o Esquema:** Demonstrar como os dados populados (mock data) se comportam na estrutura proposta através de relatórios e indicadores.

---
*Este é um projeto técnico de demonstração de modelagem de dados, sem fins de produto comercial final.*
