import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar cliente Groq
# O Groq SDK automaticamente busca a variável GROQ_API_KEY no ambiente
client = Groq()

# Configuração da página Streamlit
st.set_page_config(page_title="GMB Review Automator - MVP", page_icon="⭐", layout="wide")

st.title("GMB Review Automator - Simulador")
st.markdown("Protótipo interativo para teste de engine LLM e regras de triagem.")

# --- BARRA LATERAL: Configurações do Tenant ---
st.sidebar.header("⚙️ Configurações do Tenant")
tenant_name = st.sidebar.text_input("Nome da Empresa", value="Tech Burger")
tone_of_voice = st.sidebar.text_area(
    "Instrução de Tom de Voz",
    value="Seja amigável, moderno e descontraído. Use emojis ocasionalmente. Agradeça sempre a preferência."
)
model_choice = st.sidebar.selectbox(
    "Modelo Groq (LLM)",
    [
        "llama-3.1-8b-instant",  # Opção mais barata (Padrão)
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b"
    ]
)

# --- ÁREA PRINCIPAL: Entrada de Avaliação ---
st.header("📥 Nova Avaliação Recebida")

col1, col2 = st.columns([1, 2])
with col1:
    reviewer_name = st.text_input("Nome do Cliente", value="João Silva")
    star_rating = st.slider("Nota (Estrelas)", min_value=1, max_value=5, value=5)
with col2:
    comment = st.text_area("Comentário do Cliente", value="O lanche estava incrível, entrega super rápida!")

if st.button("Processar Avaliação", type="primary"):
    
    # Regra de Negócio: Triagem de Estrelas
    if star_rating <= 3:
        # Cenário Negativo/Neutro: Moderação Humana (Handoff)
        st.warning("⚠️ **Triagem Automática:** Avaliação de 3 estrelas ou menos detectada.")
        st.info("Ação do Sistema: **Moderação Humana (Handoff)**. Nenhuma resposta foi gerada ou publicada automaticamente. Registro marcado como 'Pendente de Aprovação'.")
    
    else:
        # Cenário Positivo: Automação Total
        st.success(f"✅ **Triagem Automática:** Avaliação de {star_rating} estrelas detectada. Iniciando geração de resposta...")
        
        # Estrutura do System Prompt baseada no PRD
        system_prompt = f"""Você é um assistente de IA sênior especializado em atendimento ao cliente e relações públicas da empresa {tenant_name}.
Sua tarefa é responder à avaliação de um cliente no Google Meu Negócio de forma extremamente humanizada.

Diretrizes Obrigatórias:
1. Mantenha o tom de voz alinhado com a seguinte instrução: {tone_of_voice}.
2. Use o nome do cliente ({reviewer_name}) de forma natural se disponível.
3. Se o cliente escreveu um comentário ({comment}), comente sobre os pontos específicos de forma breve.
4. Nunca mencione que você é uma IA ou um sistema automatizado.
5. Seja conciso, cordial e adote a norma culta da língua portuguesa.
Gere apenas o texto final da resposta, sem aspas ou introduções."""

        user_prompt = f"Gere a resposta para a avaliação de {star_rating} estrelas. Comentário do cliente: {comment}"

        try:
            with st.spinner('Processando com Groq...'):
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        }
                    ],
                    model=model_choice,
                    temperature=0.7, # Temperatura ajustada para criatividade controlada
                    max_tokens=256,
                )
                
                generated_response = chat_completion.choices[0].message.content
                
                st.subheader("🤖 Resposta Gerada pela IA")
                st.write(generated_response)
                
                st.caption("Ação do Sistema: **Automação Total**. Em um ambiente de produção, este texto seria enviado para a API do Google Business Profile.")

        except Exception as e:
            st.error(f"Erro ao comunicar com a API do Groq: {e}")