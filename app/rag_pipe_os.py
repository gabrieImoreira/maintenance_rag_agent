import os
import pandas as pd
from typing import List, Dict
from typing_extensions import TypedDict

# Importações do LangChain e LangGraph
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E SETUP DO BACKEND (PIPELINE RAG)
# ==============================================================================

# -- CONFIGURAÇÃO DO PIPELINE --
persist_directory = "./chroma_db_reparos"
collection_name = "reparos_historico"
csv_path = "./data/resultado_sem_duplicatas.csv"

def get_rag_graph():
    """
    Função principal que configura e retorna o pipeline RAG compilado (grafo).
    Esta função encapsula toda a lógica do backend.
    """
    print("Executando setup do Pipeline RAG...")

    # LLM e Embeddings
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # Vetorização e Indexação do CSV
    if os.path.exists(persist_directory):
        print("🔁 Carregando banco de dados vetorial de reparos existente...")
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )
    else:
        print(f"📚 Indexando dados do arquivo CSV: {csv_path}...")
        if not os.path.exists(os.path.dirname(csv_path)):
            raise FileNotFoundError(f"ERRO: O diretório 'data' não foi encontrado.")
        
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"ERRO: O arquivo {csv_path} não foi encontrado.")

        documents = []
        for index, row in df.iterrows():
            content = (
                f"Registro de Manutenção OS {row.get('OS', 'N/A')}:\n"
                f"- Tipo do Equipamento: {row.get('TIPO EQUIPAMENTO', 'N/A')}\n"
                f"- Equipamento: {row.get('EQUIPAMENTO', 'N/A')}\n"
                f"- Tipo de Manutenção: {row.get('TIPO', 'N/A')}\n"
                f"- Marca: {row.get('MARCA', 'N/A')}\n"
                f"- Tempo da manutenção: {row.get('TEMPO', 'N/A')}\n"
                f"- Tipo de Serviço: {row.get('TIPO DE SERVIÇO', 'N/A')}\n"
                f"- Complemento: {row.get('COMPLEMENTO', 'N/A')}\n"
                f"- Solução Aplicada: {row.get('RESOLUÇÃO', 'N/A')}"
            )
            doc = Document(
                page_content=content,
                metadata={
                    "os_number": str(row.get('OS', '')),
                    "equipment": str(row.get('EQUIPAMENTO', '')),
                    "type": str(row.get('TIPO', '')),
                    "brand": str(row.get('MARCA', '')),
                }
            )
            documents.append(doc)

        vector_store = Chroma.from_documents(
            documents=documents, embedding=embeddings,
            collection_name=collection_name, persist_directory=persist_directory
        )
        print("✅ Banco de dados vetorial criado e salvo com sucesso!")

    # Definição do Agente (Grafo com LangGraph)
    prompt = ChatPromptTemplate.from_template("""
    Você é um assistente sênior de manutenção técnica, treinado com base em um histórico de Ordens de Serviço (OS). 
    Sua função é analisar problemas relatados e oferecer suporte com sugestões úteis, claras e técnicas.

    <restricoes>
    - Não invente soluções ou causas que não estejam relacionadas ao histórico fornecido.
    - Se não encontrar informações relevantes no contexto, responda educadamente que **não foi possível encontrar uma solução com base nos dados disponíveis**.
    - Seja técnico, claro e objetivo.
    </restricoes>

    <permissoes>
    - Você pode analisar a descrição de um problema e buscar casos semelhantes no histórico de OS.
    - Você pode sugerir causas prováveis, soluções e procedimentos técnicos usados em casos semelhantes.
    - Você pode informar o tempo estimado de execução com base nos registros anteriores.
    - Você deve sempre indicar que as sugestões são baseadas em histórico e não substituem diagnóstico técnico presencial.
    </permissoes>

    ---
    - Equipamento informado: {equipamento}
    - Histórico da conversa: {history}
    - Descrição do problema: {question}
    - Contexto extraído do histórico de OS: {context}
    - Resposta:
    """)

    class State(TypedDict):
        question: str
        equipamento: str
        context: List[Document]
        chat_history: List[Dict[str, str]]
        answer: str

    def retrieve(state: State):
        search_query = f"Falha no equipamento {state['equipamento']}: {state['question']}"
        docs_with_scores = vector_store.similarity_search_with_score(search_query, k=10)

        # Reranking: ordenar pelos scores mais baixos (mais similares)
        docs_sorted = sorted(docs_with_scores, key=lambda x: x[1])
        top_docs = [doc for doc, _ in docs_sorted[:4]]  # pega os 4 melhores

        state['context'] = top_docs
        return state

    def generate(state: State):
        history_text = "\n".join(
            f"{'Usuário' if msg['role'] == 'user' else 'Assistente'}: {msg['content']}" 
            for msg in state.get("chat_history", [])
        )
        docs_text = "\n\n---\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({
            "question": state["question"],
            "equipamento": state["equipamento"],
            "context": docs_text,
            "history": history_text
        })
        response = llm.invoke(messages)
        state['answer'] = response.content
        return state

    graph_builder = StateGraph(State)
    graph_builder.add_node("retrieve", retrieve)
    graph_builder.add_node("generate", generate)
    graph_builder.add_edge(START, "retrieve")
    graph_builder.add_edge("retrieve", "generate")
    
    return graph_builder.compile()