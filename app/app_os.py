# app.py

import streamlit as st
from tinydb import TinyDB, Query
# Importa a função de setup do nosso módulo de backend
from rag_pipe_os import get_rag_graph

# ==============================================================================
# 1. CONFIGURAÇÃO DA INTERFACE E CARREGAMENTO DO BACKEND
# ==============================================================================

# -- CONFIGURAÇÃO DA PÁGINA E CSS --
st.set_page_config(page_title="Assistente de Reparos", layout="wide")
st.markdown("""
<style>
    .stButton>button {
        width: 100%; text-align: left !important; border-radius: 8px;
        transition: background-color 0.2s, color 0.2s;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stButton>button:hover { background-color: #4A4A4A; color: white; }
    .main .block-container { max-width: 900px; padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# -- CARREGAMENTO DO PIPELINE RAG --
# Usamos @st.cache_resource para garantir que o pipeline seja carregado apenas uma vez.
# Envolvemos a chamada em um try-except para lidar com erros de inicialização (ex: arquivo não encontrado).
@st.cache_resource
def load_rag_graph():
    try:
        return get_rag_graph()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado durante a inicialização: {e}")
        st.stop()

graph = load_rag_graph()


# -- BANCO DE DADOS E ESTADO DA SESSÃO --
db = TinyDB("./data/conversas_reparos_db.json")
Conversa = Query()
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None


# -- FUNÇÕES AUXILIARES DA INTERFACE --
def listar_conversas():
    return sorted(db.all(), key=lambda x: x.doc_id, reverse=True)

def carregar_conversa(chat_id):
    st.session_state.chat_id = chat_id

def salvar_conversa(nome, mensagens):
    if st.session_state.chat_id:
        db.update({"nome": nome, "mensagens": mensagens}, doc_ids=[st.session_state.chat_id])
    else:
        st.session_state.chat_id = db.insert({"nome": nome, "mensagens": mensagens})

def nova_conversa():
    st.session_state.chat_id = None


# ==============================================================================
# 2. LAYOUT DA APLICAÇÃO STREAMLIT
# ==============================================================================

# -- SIDEBAR COM HISTÓRICO --
with st.sidebar:
    st.markdown("### 🛠️ Histórico de Reparos")
    if st.button("➕ Novo Diagnóstico", use_container_width=True, type="primary"):
        nova_conversa()
    st.markdown("---")
    for c in listar_conversas():
        if st.button(f"📄 {c['nome']}", key=f"btn_{c.doc_id}", use_container_width=True):
            carregar_conversa(c.doc_id)

# -- TÍTULO E CABEÇALHO --
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/128/3208/3208636.png", width=70)
with col2:
    st.markdown("<h2 style='vertical-align: middle; margin-bottom: 0px;'>Assistente Técnico de Manutenção</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6E6E6E; margin-top: 0px;'>Descreva a falha de um equipamento para obter sugestões baseadas no histórico.</p>", unsafe_allow_html=True)
st.markdown("---")


# -- CARREGAMENTO E EXIBIÇÃO DAS MENSAGENS --
mensagens = db.get(doc_id=st.session_state.chat_id).get("mensagens", []) if st.session_state.chat_id else []
for msg in mensagens:
    with st.chat_message(msg["role"]):
        st.container(border=True).markdown(msg["content"])


# -- FORMULÁRIO DE INPUT --
with st.form(key="input_form", clear_on_submit=True):
    equipamento_input = st.text_input("Equipamento", placeholder="Ex: Esteira Kikos KX9000")
    falha_input = st.text_area("Descrição da Falha", placeholder="Ex: Painel apaga durante o uso e motor não responde.")
    submit_button = st.form_submit_button(label="Obter Sugestão")

if submit_button and equipamento_input and falha_input:
    user_message_content = f"**Equipamento:** {equipamento_input}\n\n**Falha Descrita:** {falha_input}"
    mensagens.append({"role": "user", "content": user_message_content})
    
    with st.chat_message("user"):
        st.container(border=True).markdown(user_message_content)

    with st.chat_message("assistant"):
        with st.spinner("Analisando histórico de reparos..."):
            response = graph.invoke({
                "question": falha_input,
                "equipamento": equipamento_input,
                "chat_history": mensagens
            })
            answer = response["answer"]
            st.container(border=True).markdown(answer)
            mensagens.append({"role": "assistant", "content": answer})

    nome_conversa = f"{equipamento_input[:30]}..."
    salvar_conversa(nome_conversa, mensagens)
    st.rerun()