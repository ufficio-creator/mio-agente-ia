import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# Configurazione della pagina
st.set_page_config(page_title="Il Mio Agente IA Universale", page_icon="🤖", layout="centered")

st.title("🤖 Il Mio Agente IA Universale")
st.write("Un assistente conversazionale capace di chattare, programmare e cercare sul web.")

# Barra laterale per inserire la chiave API
api_key = st.sidebar.text_input("Inserisci la tua Google Gemini API Key", type="password")

if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra a sinistra per iniziare.")
    st.stop()

# Configurazione di Gemini
genai.configure(api_key=api_key)

# Inizializzazione del modello con gemini-3.8-flash (modello aggiornato e supportato)
model = genai.GenerativeModel('models/gemini-3.8-flash')

# Funzione per cercare sul web in modo sicuro
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except Exception:
        return ""

# Gestione della cronologia della chat in Streamlit
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostra i messaggi precedenti
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dell'utente
if prompt := st.chat_input("Scrivi qualsiasi cosa (es. 'Come stai?', 'Crea una web app', ecc.):"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("L'agente sta rispondendo..."):
            try:
                # Controlliamo se la domanda richiede una ricerca web
                parole_chiave_web = ["notizie", "meteo", "ultime", "chi è", "cos'è", "cerca", "previsioni"]
                usa_web = any(parola in prompt.lower() for parola in parole_chiave_web)
                
                contesto_web = ""
                if usa_web:
                    risultati_web = search_web(prompt)
                    if risultati_web:
                        contesto_web = f"\nInformazioni fresche dal web:\n{risultati_web}\n"

                # Prompt finale per l'IA
                prompt_finale = f"""
                Sei un assistente IA esperto, amichevole e versatile, capace di risolvere problemi di qualsiasi tipo, programmare e conversare.
                {contesto_web}
                Domanda/Messaggio dell'utente: {prompt}
                """

                # Generazione della risposta
                response = model.generate_content(prompt_finale)
                answer = response.text

            except Exception as e:
                answer = f"⚠️ Si è verificato un piccolo problema tecnico con l'API: {e}. Controlla che la chiave API sia corretta."

            st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
