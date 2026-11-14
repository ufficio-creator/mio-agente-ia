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
st.markdown("Assistente intelligente potenziato con ricerca web e gestione errori avanzata.")

# Barra laterale per configurazioni
with st.sidebar:
    st.header("⚙️ Configurazione")
    api_key = st.text_input("Google Gemini API Key", type="password", help="Inserisci la tua chiave API di Google AI Studio.")
    
    st.divider()
    
    # Selezione opzionale del modello principale
    modello_scelto = st.selectbox(
        "Modello preferito",
        ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"],
        help="Scegli il modello principale da interrogare."
    )
    
    st.divider()
    
    # Pulsante per resettare la chat
    if st.button("🗑️ Pulisci Cronologia Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra a sinistra per iniziare.")
    st.stop()

# Inizializzazione del client ufficiale google-genai
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Errore nell'inizializzazione del client Gemini: {e}")
    st.stop()

# Funzione per la ricerca web intelligente
def search_web(query):
    try:
        with DDGS() as ddgs:
            # Estrae fino a 3 risultati rilevanti
            results = [r.get('body', '') for r in ddgs.text(query, max_results=3)]
            results_puliti = [r for r in results if r]
            return "\n".join(results_puliti)
    except Exception as e:
        print(f"Errore ricerca web: {e}")
        return ""

# Inizializzazione della memoria della chat nello stato di sessione
if "messages" not in st.session_state:
    st.session_state.messages = []

# Visualizzazione della cronologia dei messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Casella di input per l'utente
if prompt := st.chat_input("Scrivi qui il tuo messaggio..."):
    # Aggiunge il messaggio dell'utente allo stato
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Area di risposta dell'assistente
    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer = ""
        
        with st.spinner("Elaborazione in corso..."):
            try:
                # Filtro intelligente per attivare la ricerca web
                parole_chiave_web = ["notizie", "meteo", "ultime", "chi è", "cos'è", "previsioni", "oggi", "2026", "quotazione", "prezzo"]
                serve_il_web = any(parola in prompt.lower() for parola in parole_chiave_web)
                
                contesto_prompt = prompt
                if serve_il_web:
                    with st.spinner("🔍 Ricerca in corso sul web..."):
                        web_results = search_web(prompt)
                        if web_results:
                            contesto_prompt = f"[Informazioni fresche dal web]:\n{web_results}\n\n[Richiesta dell'utente]: {prompt}"

                # Lista di fallback ordinata per affidabilità e velocità
                modelli_disponibili = [modello_scelto, 'gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-2.5-pro']
                # Rimuove eventuali duplicati mantenendo l'ordine
                modelli_disponibili = list(dict.fromkeys(modelli_disponibili))
                
                response = None
                successo = False
                
                # Costruisce la cronologia formattata per Gemini (ultimi 10 messaggi per evitare sovraccarico di contesto)
                cronologia_recente = []
                for m in st.session_state.messages[-10:-1]: # Esclude l'ultimo prompt appena inserito
                    role = "user" if m["role"] == "user" else "model"
                    cronologia_recente.append({"role": role, "parts": [{"text": m["content"]}]})

                for modello in modelli_disponibili:
                    try:
                        # Se abbiamo la cronologia, possiamo usare chat session o passare i contents completi
                        # Per semplicità e robustezza usiamo generate_content includendo il contesto corrente
                        chat_contents = []
                        for h in cronologia_recente:
                            chat_contents.append(h)
                        chat_contents.append({"role": "user", "parts": [{"text": contesto_prompt}]})

                        response = client.models.generate_content(
                            model=modello,
                            contents=chat_contents
                        )
                        if response and hasattr(response, 'text') and response.text:
                            answer = response.text
                            successo = True
                            break 
                    except Exception as err:
                        # Passa silenziosamente al modello successivo in caso di errore/sovraccarico
                        continue 

                if not successo:
                    answer = "⚠️ I server di Google sono momentaneamente sovraccarichi o la richiesta ha incontrato un limite. Attendi qualche secondo e riprova."

            except Exception as e:
                answer = f"⚠️ Errore imprevisto durante l'esecuzione: {e}"

        placeholder.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
