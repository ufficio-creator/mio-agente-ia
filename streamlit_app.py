import streamlit as st
from google import genai
from duckduckgo_search import DDGS

# Configurazione della pagina
st.set_page_config(page_title="Il Mio Agente IA Universale", page_icon="⚡", layout="centered")

st.title("⚡ Il Mio Agente IA Universale")
st.write("Assistente intelligente con sistema di protezione anti-sovraccarico.")

# Barra laterale per inserire la chiave API
api_key = st.sidebar.text_input("Inserisci la tua Google Gemini API Key", type="password")

if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra a sinistra per iniziare.")
    st.stop()

# Collegamento ufficiale con google-genai
client = genai.Client(api_key=api_key)

# Funzione rapida per la ricerca web intelligente
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=2)]
            return "\n".join(results)
    except Exception:
        return ""

# Memoria della chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Casella di input per l'utente
if prompt := st.chat_input("Scrivi qui il tuo messaggio..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Elaborazione in corso..."):
            answer = ""
            try:
                # Filtro intelligente per attivare la ricerca web solo se necessario
                parole_chiave_web = ["notizie", "meteo", "ultime", "chi è", "cos'è", "previsioni", "oggi"]
                serve_il_web = any(parola in prompt.lower() for parola in parole_chiave_web)
                
                contesto = prompt
                if serve_il_web:
                    web_results = search_web(prompt)
                    if web_results:
                        contesto = f"Informazioni recenti dal web:\n{web_results}\n\nDomanda dell'utente: {prompt}"

                # LISTA DI MODELLI DI RISERVA: se uno è sovraccarico o non disponibile, passa al successivo
                modelli_disponibili = ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']
                response = None
                
                for modello in modelli_disponibili:
                    try:
                        response = client.models.generate_content(
                            model=modello,
                            contents=contesto
                        )
                        break # Se la chiamata ha successo, esce dal ciclo
                    except Exception:
                        continue # Se un modello fallisce, prova il successivo in silenzio

                if response and hasattr(response, 'text'):
                    answer = response.text
                else:
                    answer = "⚠️ I server di Google sono momentaneamente sovraccarichi. Attendi qualche secondo e riprova a inviare il messaggio."

            except Exception as e:
                answer = f"⚠️ Errore imprevisto: {e}"

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        
