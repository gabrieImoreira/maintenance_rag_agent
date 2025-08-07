# 🛠️ Assistente Técnico de Manutenção com RAG, ChromaDB e GPT-4o

Este projeto implementa um assistente inteligente para diagnósticos técnicos de manutenção com base em um histórico real de Ordens de Serviço (OS). Ele utiliza busca vetorial para encontrar casos semelhantes, e responde com sugestões técnicas fundamentadas nas ocorrências anteriores, por meio de uma arquitetura RAG (Retrieval-Augmented Generation).

## 🎥 Demonstração

<p align="center">
  <a href="https://raw.githubusercontent.com/gabrieImoreira/maintenance_rag_agent/main/data/demo.gif">
    <img src="https://raw.githubusercontent.com/gabrieImoreira/maintenance_rag_agent/main/data/demo.gif" alt="Demonstração do Assistente">
  </a>
</p>

### Tecnologias Utilizadas

- Python
- LangChain & LangGraph
- OpenAI (GPT-4o e text-embedding-3-large)
- ChromaDB (Persistência vetorial)
- Streamlit (Interface)
- TinyDB (Armazenamento do histórico de conversas)
- Pandas

---

## 🗂️ Estrutura do Projeto

```
📂 app/                        # Scripts principais da aplicação
  ├── app_os.py               # Interface com Streamlit
  └── rag_pipe_os.py          # Pipeline RAG com LangChain
📂 chroma_db_reparos/         # Banco vetorial persistente
📂 data/                      # Dados CSV e histórico de conversas
📄 conversas_reparos_db.json  # Histórico de conversas (TinyDB)
📄 Dockerfile / docker-compose.yml  # Configuração de container (opcional)
📄 Pipfile / Pipfile.lock     # Gerenciador de dependências
```

---

## 📋 Etapas Técnicas do Projeto

### 1. Higienização dos Dados

- Remoção de colunas irrelevantes.
- Filtro de OS sem horário de início e fim (mantendo ~51k registros).
- Eliminação de registros duplicados (mesmo equipamento, falha e solução).
- Geração de base final com ~12.7k OS únicas, via script `higienizacao_base.py`.

### 2. Indexação com ChromaDB

- Cada linha da base final foi convertida em um `Document` do LangChain.
- Aplicação de embeddings com o modelo `text-embedding-3-large` da OpenAI.
- Persistência em um banco vetorial local com `Chroma`.

### 3. Prompt Especializado

- O agente responde como um técnico sênior de manutenção.
- Restrições de alucinação: só responde com base no histórico.
- Respostas técnicas, claras e objetivas.

### 4. Pipeline RAG com LangGraph

- Arquitetura baseada em dois nós:
  - `retrieve`: busca por similaridade no histórico vetorizado.
  - `generate`: gera uma resposta com base nos documentos e no histórico do chat.
- Reranking para priorizar os documentos mais relevantes (top 4).

### 5. Frontend com Streamlit

- Entrada via campos: Equipamento + Descrição da Falha.
- Histórico de conversas salvo automaticamente com TinyDB.
- Interface com histórico lateral de diagnósticos anteriores.
- Feedback visual e UX amigável.

## 💡 Funcionalidades

- Busca vetorial com base em histórico técnico real
- IA especializada com GPT-4o e prompt restritivo
- Interface interativa com histórico de chat
- Diagnósticos técnicos otimizados por reranking

---

## 📌 Observação Importante sobre a Base de Dados

Inicialmente, a base fornecida para este projeto continha mais de **500.000 registros** de Ordens de Serviço (OS). No entanto, após um processo rigoroso de higienização e análise de qualidade dos dados, apenas **cerca de 12.700 registros únicos** foram utilizados na construção do banco vetorial.

Essa redução drástica foi necessária devido a diversos fatores, como:
- Presença de colunas com informações ausentes ou irrelevantes;
- Dados duplicados ou inconsistentes;
- Registros sem horário de início e fim;
- Equipamentos e falhas repetidas com resoluções idênticas.

Essa filtragem teve como objetivo garantir **alta assertividade** nas respostas do agente inteligente. No entanto, é importante ressaltar que este projeto foi desenvolvido como um **protótipo funcional** para **demonstração técnica**. 

Para um uso em escala profissional e confiável, será fundamental:
- Reavaliar e enriquecer a base de dados original;
- Alimentar o sistema apenas com dados completos, relevantes e estruturados;
- Conduzir experimentos com conjuntos maiores e mais bem curados de OS;
- Rankeamento da base das respostas duplicadas, para ter maior assertividade e ter a base das respostas mais relevantes/repetidas.

Esse projeto prova o potencial da abordagem RAG em manutenção técnica, mas **a qualidade da base de dados é determinante para a eficácia real da solução**.


---

## ▶️ Como Executar o Projeto

Este projeto pode ser executado de duas formas: via Docker (recomendado para ambientes isolados) ou via Pipenv (modo local de desenvolvimento).

### 🔹 Opção 1: Usando Docker (Recomendado)

1.   Acesse a pasta raiz do projeto, vá até o arquivo .env na raiz do projeto e insira sua chave de API da OpenAI.

2.  Após isso, na raizraiz do projeto (com o Docker instalado) e execute:

```bash
docker-compose up --build
```

3. Acesse a aplicação no navegador: [http://localhost:8501](http://localhost:8501)


### 🔹 Opção 2: Executando Localmente com Pipenv

4. Clone o repositório e acesse a pasta:

```bash
git clone https://github.com/gabrieImoreira/maintenance_rag_agent.git
cd maintenance_rag_agent
```

5. Instale as dependências:

```bash
pip install pipenv
pipenv install
```

6. Execute o app:

```bash
pipenv run python streamlit run app/app_os.py
```

7. Acesse: [http://localhost:8501](http://localhost:8501)
