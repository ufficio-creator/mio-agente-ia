import streamlit as st
from google import genai
from duckduckgo_search import DDGS

# Configurazione della pagina
st.set_page_config(page_title="Il Mio Agente IA Privato", page_icon="🤖", layout="centered")

st.title("🤖 Il Mio Agente IA con Ricerca Web")
st.write("Agente privato, gratuito e in grado di cercare informazioni aggiornate sul web.")

# Barra laterale per inserire la chiave API
api_key = st.sidebar.text_input("Inserisci la tua Google Gemini API Key", type="password")

if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra a sinistra per iniziare.")
    st.stop()

# Collegamento a Gemini
client = genai.Client(api_key=api_key)

# Funzione che cerca su DuckDuckGo
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except Exception as e:
        return f"Errore durante la ricerca web: {e}"

# Memoria della chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Casella per scrivere all'agente
if prompt := st.chat_input("Chiedimi qualcosa o cercalo sul web..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Cerco sul web ed elaboro la risposta..."):
            web_results = search_web(prompt)
            
            context_prompt = f"""
            Sei un assistente intelligente. Usa queste informazioni appena trovate sul web per rispondere in modo preciso e aggiornato:
            {web_results}
            
            Domanda dell'utente: {prompt}
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=context_prompt
            )
            answer = response.text
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
