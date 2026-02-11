import streamlit as st
import os
import shutil
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
try:
    from langchain_community.chat_models import ChatOllama
except ImportError:
    # Fallback/Newer Import
    from langchain_community.chat_models import ChatOllama 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# --- CONFIGURATION ---
CHROMA_PATH = "chroma_db"
OLLAMA_MODEL = "mistral" # Or "llama3", make sure you 'ollama pull' it first
# ---------------------

st.set_page_config(page_title="Self-Hosted Grammar Expert", page_icon="🦉")

st.title("🦉 Grammar Expert AI")
st.caption(f"Powered by Local {OLLAMA_MODEL} & Custom Knowledge Base")

# Check if DB exists
if not os.path.exists(CHROMA_PATH):
    st.error(f"❌ Database not found at `{CHROMA_PATH}`.")
    st.info("⚠️ Please download `chroma_db.zip` from Colab, extract it here, and restart.")
    st.stop()

# --- INITIALIZE RESOURCES (Cached) ---
@st.cache_resource
def get_vector_db():
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'} # Local inference is usually CPU
    )
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    return db

@st.cache_resource
def get_llm():
    return ChatOllama(model=OLLAMA_MODEL)

try:
    db = get_vector_db()
    llm = get_llm()
except Exception as e:
    st.error(f"Error loading resources: {e}")
    st.stop()

# --- PROMPT TEMPLATE ---
template = """
You are an expert English Grammar Tutor. Your goal is to explain grammar concepts clearly and simply.

Answer the user's QUESTION based ONLY on the following CONTEXT from their study materials.
If the answer is not in the context, say "I couldn't find specific information about this in your study materials," then try to give a general explaination but explicitly state it is general knowledge.

CONTEXT:
{context}

QUESTION:
{question}

EXPLANATION:
"""
prompt = ChatPromptTemplate.from_template(template)

# --- APP LOGIC ---

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi! I'm ready to explain grammar using your documents. Ask me anything!"}]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"]).write(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

if prompt_input := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    st.chat_message("user").write(prompt_input)

    # Retrieval
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # RAG Chain
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
    )

    # Response Generation
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Stream response
        for chunk in chain.stream(prompt_input):
            full_response += chunk.content
            response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
