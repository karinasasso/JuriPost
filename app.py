# -*- coding: utf-8 -*-

import streamlit as st
from chatbot_core import gerar_post_completo
import streamlit.components.v1 as components

# --- Funções Auxiliares para Copiar (JavaScript - VERSÃO FINAL DE LIMPEZA) ---
def copy_button_js(text_to_copy, button_label, key_suffix=""):
    # Lógica aprimorada para limpar o texto antes de copiar
    # 1. Manter quebras de linha visíveis (para posts)
    # 2. Remover marcadores Markdown (negrito, itálico, título)
    # 3. Remover frases de subtítulo que o LLM pode ter gerado (ex: "Título Sugerido:")

    cleaned_text_lines = []
    lines = text_to_copy.splitlines() # Divide o texto em linhas

    for line in lines:
        temp_line = line.strip() # Remove espaços em branco do início/fim da linha

        # Remover marcadores de Markdown
        temp_line = temp_line.replace('**', '').replace('*', '') # Remove negrito e itálico
        temp_line = temp_line.lstrip('# ') # Remove '#' e espaço se for um título
        
        # Remover frases de subtítulo que o LLM pode ter incluído
        if temp_line.startswith("Título Sugerido:"):
            temp_line = temp_line.replace("Título Sugerido:", "").strip()
        if temp_line.startswith("Corpo do Post:"):
            temp_line = temp_line.replace("Corpo do Post:", "").strip()
        if temp_line.startswith("Chamada Sutil para Ação:"):
            temp_line = temp_line.replace("Chamada Sutil para Ação:", "").strip()
        if temp_line.startswith("Hashtags:"):
            temp_line = temp_line.replace("Hashtags:", "").strip()
        if temp_line.startswith("Assunto:"): # Se o agente imagem ainda colocar isso
            temp_line = temp_line.replace("Assunto:", "").strip()
        
        # Adiciona a linha limpa, mas apenas se não for uma linha vazia após a limpeza
        if temp_line: # Garante que não adicione linhas vazias extras
            cleaned_text_lines.append(temp_line)
    
    # Junta as linhas de volta com quebras de linha
    final_cleaned_text = '\n'.join(cleaned_text_lines).strip()
    
    # Garante que o texto seja seguro para JS (escapa aspas duplas)
    safe_text = final_cleaned_text.replace('"', '\\"')

    # Cria um ID único para o text area temporário e para o botão
    unique_id = f"text_to_copy_{hash(safe_text)}_{key_suffix}"
    button_id = f"copy_btn_{unique_id}"

    # HTML para criar um text area oculto e o botão
    js_code = f"""
    <textarea id="{unique_id}" style="position: absolute; left: -9999px;">{safe_text}</textarea>
    <button id="{button_id}" style="
        background-color: #4CAF50; /* Verde */
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition-duration: 0.4s;
    " onmouseover="this.style.backgroundColor='#45a049'" onmouseout="this.style.backgroundColor='#4CAF50'">
        {button_label}
    </button>
    <script>
        document.getElementById('{button_id}').onclick = function() {{
            var copyText = document.getElementById('{unique_id}');
            copyText.select();
            copyText.setSelectionRange(0, 99999); /* Para dispositivos móveis */
            try {{
                document.execCommand("copy");
                var originalText = this.innerText;
                this.innerText = "Copiado!";
                setTimeout(() => {{
                    this.innerText = originalText;
                }}, 1500);
            }} catch (err) {{
                console.error('Erro ao copiar: ', err);
                alert('Erro ao copiar o texto. Por favor, copie manualmente.');
            }}
        }};
    </script>
    """
    # Renderiza o HTML e JS no Streamlit
    components.html(js_code, height=50) # Altura para o botão aparecer

# --- NOVA FUNÇÃO AUXILIAR PARA GERAR O POST ---
def executar_geracao_post():
    if st.session_state['topico_usuario']:
        with st.spinner("🧠 Nossos especialistas em IA estão trabalhando para criar seu post..."):
            try:
                st.session_state['resultados_chatbot'] = None
                st.session_state['resultados_chatbot'] = gerar_post_completo(st.session_state['topico_usuario'])
            except Exception as e:
                st.session_state['resultados_chatbot'] = {"erro": f"Ocorreu um erro inesperado: {e}. Por favor, verifique sua chave de API e tente novamente."}
    else:
        st.warning("Por favor, digite o tópico do post para que eu possa começar.")
        st.session_state['resultados_chatbot'] = None

# --- Configurações da Página ---
st.set_page_config(
    page_title="JuriPost - Gerador de Conteúdo Jurídico",
    page_icon=":scales:", # Usando o shortcode para o emoji da balança
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Título e Descrição da Aplicação ---
st.title("⚖️ JuriPost: Seu Assistente de Marketing Jurídico com IA")
st.markdown(
    """
    Bem-vindo ao JuriPost! Sou seu assistente de IA especializado em criar posts
    para marketing jurídico do escritório CK Sasso.
    Basta me dizer o tema que você deseja para o post e eu cuidarei de todo o processo,
    desde a pesquisa de tendências até o rascunho final e a sugestão de imagem!
    """
)
st.markdown("---")

# Usando st.session_state para manter o tema e os resultados entre reruns
if 'topico_usuario' not in st.session_state:
    st.session_state['topico_usuario'] = ""
if 'resultados_chatbot' not in st.session_state:
    st.session_state['resultados_chatbot'] = None
if 'gerar_novamente' not in st.session_state:
    st.session_state['gerar_novamente'] = False

# --- Entrada do Usuário ---
st.header("Qual tópico jurídico você gostaria de explorar para o post?")
st.session_state['topico_usuario'] = st.text_input(
    "Ex: 'As últimas tendências em LGPD para pequenas empresas', 'Novidades sobre direito do consumidor e compras online'",
    value=st.session_state['topico_usuario'],
    key="topico_input",
    label_visibility="collapsed"
)

# --- Botão para Gerar o Post ---
gerar_botao = st.button("🚀 Gerar Post Completo")

# Lógica para ativar a geração
# Ativa a geração se o botão principal foi clicado OU se a flag de 'gerar_novamente' está True
if gerar_botao or st.session_state['gerar_novamente']:
    st.session_state['gerar_novamente'] = False # Reseta a flag
    executar_geracao_post() # Chama a nova função

# Exibir resultados somente se houverem resultados gerados (ou carregados da sessão)
if st.session_state['resultados_chatbot']:
    resultados_chatbot = st.session_state['resultados_chatbot']

    if "erro" in resultados_chatbot:
        st.error(resultados_chatbot["erro"])
        st.warning("Algo deu errado. Por favor, tente novamente ou verifique as configurações da API.")
    else:
        st.success("🎉 Seu Post está pronto!")
        st.markdown("---")

        # Exibe os resultados de cada agente em seções expander
        with st.expander("🔍 Pesquisa de Tendências (Agente Pesquisador Jurídico)", expanded=False):
            st.markdown(resultados_chatbot.get('lancamentos_buscados', 'Nenhum lançamento encontrado.'))

        with st.expander("💡 Plano de Conteúdo (Agente Estrategista de Conteúdo)", expanded=False):
            st.markdown(resultados_chatbot.get('plano_de_post', 'Nenhum plano gerado.'))
        
        # NOVO BLOCO AQUI: Conteúdo para Reels COMPLETO
        st.subheader("🎬 Conteúdo para Reels")

        with st.expander("🎥 Roteiro e Detalhes do Reels Completo", expanded=True):
            reels_conteudo_completo = resultados_chatbot.get('reels_conteudo_completo', 'Nenhum conteúdo para Reels gerado.')
            if reels_conteudo_completo and reels_conteudo_completo.strip(): # Verifica se há conteúdo real
                st.markdown(reels_conteudo_completo) # Usar st.markdown para renderizar a formatação do Reels
                # O botão de copiar já usará a função copy_button_js que limpa o texto
                copy_button_js(reels_conteudo_completo, "📋 Copiar Conteúdo Completo do Reels", key_suffix="reels_completo_button")
            else:
                st.write("Conteúdo para Reels não gerado.")

        with st.expander("📝 Rascunho do Post (Agente Redator Legal)", expanded=False):
            st.markdown(resultados_chatbot.get('rascunho_de_post', 'Nenhum rascunho gerado.'))

        # Agente Revisor - Sempre aberto, e exibe o post final JÁ REVISADO
        with st.expander("✅ Revisão Final (Agente Revisor Final)", expanded=True):
            post_revisado_completo = resultados_chatbot.get('post_final', 'Nenhuma revisão realizada.')
            texto_do_post_para_exibir = post_revisado_completo # O texto bruto do LLM
            nota_da_revisao = ""

            # Tenta separar a nota de revisão do corpo do post
            if 'Post revisado e pronto para publicar!' in post_revisado_completo:
                partes = post_revisado_completo.rsplit('Post revisado e pronto para publicar!', 1) 
                texto_do_post_para_exibir = partes[0].strip()
                nota_da_revisao = 'Post revisado e pronto para publicar!' + partes[1].strip()
            else:
                st.warning("O revisor não seguiu o formato esperado para a nota final. Exibindo o texto completo da revisão.")
                st.markdown(post_revisado_completo) # Exibe o que veio do revisor como markdown

            # Exibe o post final formatado
            if texto_do_post_para_exibir and texto_do_post_para_exibir != 'Nenhuma revisão realizada.':
                st.subheader("Post Final Revisado:")
                st.markdown(texto_do_post_para_exibir)
            
            # Exibe a nota da revisão se ela existir
            if nota_da_revisao:
                st.markdown(f"*{nota_da_revisao}*")
            
            # Botão de copiar Post Final usando a nova função JS
            if texto_do_post_para_exibir and texto_do_post_para_exibir != 'Nenhuma revisão realizada.':
                copy_button_js(texto_do_post_para_exibir, "📋 Copiar Post Final para Publicação", key_suffix="final_post_display")

        # NOVO BLOCO AQUI: Agente de Legenda
        with st.expander("💬 Legenda do Post (Agente Criador de Legendas)", expanded=True): # Pode ser expandido por padrão se quiser
            legenda_post = resultados_chatbot.get('legenda_post', '').strip() #Pega a legenda e remove espaços extras
            st.info("Copie a legenda abaixo para usar em suas redes sociais:")
            # Usar text_area para facilitar a cópia
            if legenda_post: #Apenas verifica se a string não está vazia após strip()
                st.text_area("Legenda gerada:", value=legenda_post, height=80, key="legenda_display", help="Legenda concisa e atraente para o 			post.")
                copy_button_js(legenda_post, "📋 Copiar Legenda", key_suffix="legenda_button")
            else:
                st.write("Legenda não gerada.")

        # Agente Gerador Visual - Sempre aberto
        with st.expander("🖼️ Sugestão de Imagem (Agente Gerador Visual)", expanded=True):
            st.info("Use o prompt abaixo em sua ferramenta de IA preferida (Ex: Google Gemini Advanced, Midjourney, DALL-E):")

            imagem_prompt = resultados_chatbot.get('imagem_gerada_prompt', 'Nenhum prompt gerado.')
            
            # Exibir o prompt da imagem em um text_area para visualização e cópia fácil
            if imagem_prompt != 'Nenhum prompt gerado.':
                st.text_area("Prompt gerado para IA de Imagem:", value=imagem_prompt, height=200, key="image_prompt_display", help="Copie este prompt completo para a sua IA geradora de imagens.")
                copy_button_js(imagem_prompt, "📋 Copiar Prompt da Imagem", key_suffix="image_prompt_button")
            else:
                st.write("Prompt da imagem não gerado.")


        st.markdown("---")
        st.write("✨ Pronto para a próxima publicação!")

        # Botões de Ação Final
        col_actions1, col_actions2 = st.columns(2)
        with col_actions1:
            if st.button("🔄 Gerar Novo Post"):
                st.session_state['topico_usuario'] = ""
                st.session_state['resultados_chatbot'] = None
                st.rerun() 
        with col_actions2:
            if st.button("🔁 Refazer com Mesmo Tema"):
                # Mantém o tópico, limpa resultados e seta a flag para gerar novamente
                st.session_state['resultados_chatbot'] = None
                st.session_state['gerar_novamente'] = True
                st.rerun()

# --- Seção para Dicas na Barra Lateral ---
st.sidebar.header("Dicas Rápidas")
st.sidebar.info(
    """
    * Seja específico com o tema para melhores resultados.
    * O JuriPost vai gerar um prompt para você usar em uma ferramenta de IA de imagem.
    * Lembre-se sempre de revisar o conteúdo gerado antes de publicar!
    """
)

st.sidebar.markdown("---")
st.sidebar.header("Configurações de Exibição")
st.sidebar.write("Você pode alternar entre os temas claro e escuro clicando no ícone de configurações no canto superior direito da tela.")