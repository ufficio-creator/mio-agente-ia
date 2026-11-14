import streamlit as st
from google import genai
from duckduckgo_search import DDGS

# Configurazione della pagina
st.set_page_config(
    page_title="Agente IA Universale", 
    page_icon="⚡", 
    layout="centered"
)

st.title("⚡ Agente IA Universale")
st.markdown("Assistente intelligente con supporto chat e ricerca web.")

# Barra laterale per configurazioni
with st.sidebar:
    st.header("⚙️ Configurazione")
    api_key = st.text_input("Google Gemini API Key", type="password", help="Inserisci la tua chiave API di Google AI Studio.")
    
    st.divider()
    
    modello_scelto = st.selectbox(
        "Modello",
        ["gemini-2.0-flash", "gemini-1.5-flash"],
        help="Scegli il modello da utilizzare."
    )
    
    st.divider()
    
    if st.button("🗑️ Pulisci Cronologia Chat", use_container_width=True):
        st.session_state.messages = []
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()

if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra a sinistra per iniziare.")
    st.stop()

# Inizializzazione del client ufficiale google-genai
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Errore nell'inizializzazione del client: {e}")
    st.stop()

# Inizializzazione della sessione di chat nello stato di Streamlit
if "chat_session" not in st.session_state:
    try:
        st.session_state.chat_session = client.chats.create(model=modello_scelto)
    except Exception as e:
        st.error(f"Errore nella creazione della sessione chat: {e}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Visualizzazione dei messaggi precedenti
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Funzione di ricerca web sicura
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r.get('body', '') for r in ddgs.text(query, max_results=2)]
            return "\n".join([r for r in results if r])
    except Exception:
        return ""

# Input utente
if prompt := st.chat_input("Scrivi qui il tuo messaggio..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Elaborazione in corso..."):
            try:
                # Eventuale integrazione ricerca web
                parole_chiave_web = ["notizie", "meteo", "ultime", "chi è", "cos'è", "previsioni", "oggi", "2026"]
                if any(p in prompt.lower() for p in parole_chiave_web):
                    web_results = search_web(prompt)
                    if web_results:
                        prompt_inviato = f"[Informazioni web recenti]:\n{web_results}\n\nDomanda: {prompt}"
                    else:
                        prompt_inviato = prompt
                else:
                    prompt_inviato = prompt

                # Invio del messaggio tramite la sessione ufficiale
                response = st.session_state.chat_session.send_message(prompt_inviato)
                answer = response.text if response and hasattr(response, 'text') else "Risposta vuota ricevuta dal modello."

            except Exception as e:
                answer = f"⚠️ Errore durante la generazione della risposta: {e}"

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
