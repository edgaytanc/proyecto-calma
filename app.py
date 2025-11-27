import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ==========================================
# CONFIGURACIÓN
# ==========================================

# 1. Configura tu API Key de Gemini aquí
# Se carga desde el archivo .env para mayor seguridad
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ Error: No se encontró la API Key de Google. Por favor configura el archivo .env.")
    st.stop()

# Configuración de la IA
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# ==========================================
# LÓGICA DE SEGURIDAD (MODO EMERGENCIA)
# ==========================================

def verificar_riesgo(texto):
    """
    Analiza el texto del usuario buscando patrones de riesgo inminente.
    Retorna (True, mensaje_emergencia) si hay riesgo, o (False, None) si es seguro.
    """
    # Palabras clave de riesgo alto (se puede ampliar con regex más complejos)
    palabras_riesgo = [
        "suicidio", "suicidarme", "matarme", "morirme", "no quiero vivir",
        "acabar con todo", "cortarme", "pastillas", "ahorcarme", "desaparecer"
    ]
    
    texto_lower = texto.lower()
    for palabra in palabras_riesgo:
        if palabra in texto_lower:
            return True, generar_alerta_guatemala()
            
    return False, None

def generar_alerta_guatemala():
    """Retorna el contenido HTML/Markdown para la alerta de emergencia en Guatemala."""
    return """
    ### ⚠️ ALERTA DE EMERGENCIA
    
    He detectado que estás pasando por un momento muy difícil y peligroso. 
    **Por favor, no estás solo/a.**
    
    Si estás en Guatemala, contacta a estos servicios gratuitos ahora mismo:
    
    * 🚑 **Bomberos Voluntarios:** Marca **122**
    * 🚑 **Bomberos Municipales:** Marca **123**
    * 🤝 **Liga Guatemalteca de Higiene Mental:** 2232-5325 / 2238-3739
    * 📞 **Teléfono de la Esperanza:** 2422-3000
    
    La IA se ha pausado para priorizar tu seguridad. Busca ayuda humana inmediata.
    """

# ==========================================
# PROMPT DEL SISTEMA (PERSONALIDAD)
# ==========================================

SYSTEM_INSTRUCTION = """
Eres "Calma", un asistente de apoyo emocional empático, cálido y sereno.
Tus objetivos son:
1. Validar las emociones del usuario (ej: "Es normal sentirse así...").
2. Ofrecer técnicas de respiración guiada si detectas ansiedad.
3. Sugerir ejercicios de journaling (escritura) para procesar pensamientos.
4. Dar rutinas pequeñas para manejar el estrés.

REGLAS ESTRICTAS:
- NO eres médico ni psicólogo. NO diagnostiques enfermedades ni recetes medicamentos.
- Si el usuario pregunta por síntomas físicos graves, dile que acuda a un médico.
- Mantén respuestas breves, amables y fáciles de leer.
- Usa un tono conversacional y cercano.
"""

# ==========================================
# INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Tu Guía Emocional", page_icon="🌿")

# Título y descripción
st.title("🌿 Tu Guía de Apoyo Emocional")
st.markdown("Este es un espacio seguro para desahogarte, respirar y encontrar calma. *Recuerda: No soy un psicólogo, soy una IA de acompañamiento.*")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensaje inicial del sistema (contexto para la IA, no se muestra al usuario)
    st.session_state.chat = model.start_chat(history=[
        {"role": "user", "parts": SYSTEM_INSTRUCTION},
        {"role": "model", "parts": "Entendido. Seré Calma, un asistente empático y seguro. Estoy listo para escuchar."}
    ])

# Mostrar mensajes anteriores en la interfaz
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura de entrada del usuario
if prompt := st.chat_input("Cuéntame, ¿cómo te sientes hoy?"):
    
    # 1. Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. VERIFICACIÓN DE SEGURIDAD (Capa 1)
    hay_riesgo, mensaje_emergencia = verificar_riesgo(prompt)

    if hay_riesgo:
        # Mostrar alerta de emergencia y detener flujo
        with st.chat_message("assistant"):
            st.error("Se ha detectado una situación de riesgo.")
            st.markdown(mensaje_emergencia)
        # No guardamos esto en el historial para no confundir a la IA, o guardamos un marcador
        st.session_state.messages.append({"role": "assistant", "content": mensaje_emergencia})
    
    else:
        # 3. Generación de respuesta con IA (Si es seguro)
        with st.chat_message("assistant"):
            with st.spinner("Escuchando..."):
                try:
                    response = st.session_state.chat.send_message(prompt)
                    texto_respuesta = response.text
                    st.markdown(texto_respuesta)
                    st.session_state.messages.append({"role": "assistant", "content": texto_respuesta})
                except Exception as e:
                    # Log del error para el administrador (en consola)
                    print(f"Error detallado: {e}")
                    st.error("Lo siento, hubo un problema técnico. Por favor intenta de nuevo en unos momentos.")

# Sidebar con recursos estáticos
with st.sidebar:
    st.header("Recursos Rápidos")
    st.info("**Técnica 4-7-8**\n\n1. Inhala en 4 seg\n2. Retén 7 seg\n3. Exhala en 8 seg")
    st.warning("En caso de crisis en Guatemala, marca al 123.")