import os
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from datetime import date
import textwrap
import requests
import warnings

warnings.filterwarnings("ignore")

# --- Configuração da API Key (MUDANÇA AQUI!) ---
# A forma mais fácil é criar um arquivo .env na mesma pasta do seu projeto.
# Dentro do arquivo .env, adicione a linha: GOOGLE_API_KEY="SUA_CHAVE_AQUI"
# E DESCOMENTE (remova o '#') a linha abaixo para que ele consiga ler sua chave:
from dotenv import load_dotenv; load_dotenv() # <--- DESCOMENTE ESTA LINHA

# Não precisa mexer no código abaixo, ele vai tentar pegar a chave da variável de ambiente
try:
    os.environ["GOOGLE_API_KEY"]
except KeyError:
    raise Exception("Variável de ambiente GOOGLE_API_KEY não definida. Por favor, defina-a no seu arquivo .env ou no sistema.")
# Fim da Configuração da API Key

# Configura o cliente da SDK do Gemini
client = genai.Client()
MODEL_ID = "gemini-2.0-flash" # Mantenha o ID do seu modelo principal

# Função auxiliar que envia uma mensagem para um agente via Runner e retorna a resposta final
def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text
                    final_response += "\n"
    return final_response

# --- Definição dos 5 Agentes e suas funções (Com as instruções melhoradas e nomes antigos) ---
# MANTIVE OS NOMES DAS FUNÇÕES DE AGENTE ORIGINAIS DO SEU CÓDIGO
# PARA EVITAR QUE VOCÊ TENHA QUE MUDAR OUTRAS PARTES DO CÓDIGO.

# Agente 1: Buscador de Notícias
def agente_buscador(topico, data_de_hoje): # Nome da função original
    buscador = Agent(
        name="agente_buscador", # Nome interno do agente
        model="gemini-2.0-flash",
        description="Agente que busca notícias no Google sobre o tópico indicado",
        tools=[google_search],
        instruction="""
        Você é um assistente de pesquisa. A sua tarefa é usar a ferramenta de busca do google (google_search) para recuperar as últimas notícias de lançamentos muito relevantes sobre o tópico abaixo.
        Foque em no máximo 5 lançamentos relevantes, com base na quantidade e entusiasmo das notícias sobre ele.
        Se um tema tiver poucas notícias ou reações entusiasmadas, é possível que ele não seja tão relevante assim e pode ser substituído por outro que tenha mais.
        Esses lançamentos relevantes devem ser atuais, de no máximo um mês da data de hoje.
        APRESENTE os lançamentos como uma lista numerada, incluindo o nome do lançamento e uma breve descrição do porquê é relevante.
        """
    )
    entrada_do_agente_buscador = f"Tópico: {topico}\nData de hoje: {data_de_hoje}"
    lancamentos = call_agent(buscador, entrada_do_agente_buscador)
    return lancamentos

# Agente 2: Planejador de posts
def agente_planejador(topico, lancamentos_buscados): # Nome da função original
    planejador = Agent(
        name="agente_planejador", # Nome interno do agente
        model="gemini-2.0-flash",
        instruction="""
        Você é um planejador de conteúdo jurídico, especialista em redes sociais de um escritório de advocacia luso-brasileiro.
        Com base na lista de lançamentos mais recentes e relevantes buscados, você deve:
        1.  Analise cada lançamento: Avalie a relevância jurídica e o potencial de engajamento social de cada um.
        2.  Pesquise (google_search): Use a ferramenta de busca do Google (google_search) para aprofundar a pesquisa sobre o tema mais promissor e identificar os pontos legais mais relevantes que poderíamos abordar em um post.
        3.  Selecione o Tema Principal: Escolha o tema mais relevante e impactante para o público, justificando sua escolha.
        4.  Crie um Plano Detalhado: Retorne o tema escolhido, seus pontos mais relevantes para o contexto jurídico, e um plano com os assuntos a serem abordados no post.
        Lembre-se das regras de marketing jurídico para advogados, que não podem fazer propaganda direta, e garanta que o conteúdo seja informativo e de valor.
        FORMATO DE SAÍDA:
        Tema Escolhido: [Nome do Tema]
        Relevância: [Breve explicação da relevância]
        Pontos Principais para o Post:
        - [Ponto 1]
        - [Ponto 2]
        - [Ponto 3]
        Plano de Conteúdo:
        [Descrição detalhada do que deve ser abordado no post, tópicos, argumentos, etc.]
        """,
        description="Agente que planeja posts",
        tools=[google_search]
    )
    entrada_do_agente_planejador = f"Tópico:{topico}\nLançamentos buscados: {lancamentos_buscados}"
    plano_do_post = call_agent(planejador, entrada_do_agente_planejador)
    return plano_do_post

# NOVO AGENTE AQUI: Agente Criador de Reels Completo
def agente_reels_completo(topico, plano_de_post):
    reels_gerador = Agent(
        name="agente_reels_completo",
        model="gemini-2.0-flash", # Mantenha o modelo que você está usando
        instruction="""
        Você é um agente especialista na criação de Reels para um escritório de advocacia luso-brasileiro (CK Sasso).
        Seu objetivo é criar, a partir do tópico jurídico e do plano de post fornecidos, um **roteiro completo de vídeo no estilo Reels**, pronto para ser editado no Canva, CapCut ou InShot.
        O vídeo deve ser criado **sem que o advogado apareça**, utilizando apenas texto animado, imagens de fundo, ícones e trilha sonora suave.

        O vídeo deve ser dividido em slides animados (entre 6 e 8), com duração total de 30 a 45 segundos, utilizando linguagem clara, acessível, mas com credibilidade e sobriedade.
        **Cada slide deve conter OBRIGATORIAMENTE:**
        - Tempo sugerido (em segundos para o início e fim da cena/slide)
        - Texto a ser exibido
        - Sugestão de fundo (imagem, vídeo ou ícones simples do Canva)
        - Animação sugerida (fade, zoom, slide etc.)

        Ao final, gere também, no mesmo output e no formato especificado:
        - Uma **legenda** para o Reels (sem chamada de captação de cliente, com um máximo de 4 frases)
        - **Hashtags** relevantes para o tema (5 a 8 hashtags), respeitando as diretrizes éticas da OAB.
        - **Paleta de cores sóbria** (vinho, preto, dourado, branco ou variações)
        - **Sugestão de música** suave ou instrumental

        **Lembre-se:**
        - O conteúdo é jurídico-informativo, voltado para o público luso-brasileiro.
        - Deve ter clareza, simplicidade de execução e visual atrativo.
        - O tom é profissional, moderno e acessível.
        - O vídeo será executado por alguém leigo em design e edição, então use orientações simples e diretas.
        - **A FONTE RECOMENDADA DEVE SER SEMPRE:** Montserrat ou Playfair Display.

        **SEU OUTPUT DEVE SEGUIR RIGOROSAMENTE O FORMATO DO EXEMPLO ABAIXO. NENHUM TEXTO ADICIONAL DEVE SER INCLUÍDO ALÉM DO FORMATO ESPECIFICADO.**

        **EXEMPLO DE OUTPUT ESPERADO:**
        🎞️ Reels: Alterações na Lei da Nacionalidade Portuguesa (2025)
        Duração total: 40 segundos
        Estilo visual: moderno e sóbrio
        Paleta: vinho escuro, preto, dourado, branco
        Fonte recomendada: Montserrat ou Playfair Display
        🎬 Roteiro Slide a Slide
        Slide | Duração | Texto | Fundo sugerido | Animação sugerida
        ---|---|---|---|---
        1 | 0–5s | ⚠️ A Lei da Nacionalidade Portuguesa pode mudar em breve... | Torre de Belém ou mapa de Portugal com blur escuro | Texto com fade-in
        2 | 5–10s | Um novo projeto de lei propõe regras mais exigentes para quem deseja ser português. | Parlamento ou símbolo da justiça | Slide-in da esquerda
        3 | 10–15s | 📌 Tempo mínimo de residência: de 5 para 10 anos | Imagem de ampulheta ou calendário animado | Zoom-in no número “10”
        4 | 15–20s | 📚 Será exigido teste sobre cultura, história e valores portugueses | Livro aberto ou bandeira portuguesa | Fade com destaque em “teste”
        5 | 20–25s | ⚖️ É preciso comprovar boa conduta e ligação à comunidade | Ícone de balança ou comunidade | Slide com ícones aparecendo gradualmente
        6 | 25–30s | 🚫 Em certos casos, a nacionalidade poderá ser retirada | Fundo escuro com alerta discreto | Fade dramático no texto
        7 | 30–40s | Quem já reúne os critérios atuais pode ser afetado | Família caminhando, pessoa olhando horizonte | Texto central com fade e música suave
        8 | 40–45s | Informação jurídica com responsabilidade. (Logo discreto) | Fundo preto com logo em dourado | Fade no logo e encerramento da música

        ✍️ Legenda para o Reels
        📢 A proposta de alteração da Lei da Nacionalidade Portuguesa prevê mudanças importantes no acesso à cidadania por tempo de residência.
        Entre os pontos centrais estão o aumento do tempo mínimo de residência, exigência de teste de cultura portuguesa e regras de idoneidade cívica.
        Fique atento: o cenário legal está em movimento.
        Informação jurídica com responsabilidade.

        🏷️ Hashtags
        #NacionalidadePortuguesa #DireitoLusoBrasileiro #CidadaniaPortuguesa #MudancasNaLei #AdvocaciaResponsavel #ResidenciaLegal #Portugal2025

        🎨 Paleta de Cores
        Vinho escuro: #3E1F28
        Dourado: #D4AF37
        Preto: #000000
        Branco: #FFFFFF

        🎵 Música sugerida
        “Fado Instrumental”
        “Caminho (Instrumental)” de António Zambujo
        Sons ambiente portugueses suaves (disponíveis no Canva ou Reels)
        """,
        description="Agente que cria roteiros completos, legendas e sugestões visuais/musicais para Reels de Instagram."
    )
    entrada_do_agente_reels = f"Tópico: {topico}\nPlano de post: {plano_de_post}\n\nCrie um Reels completo com base no exemplo fornecido:"
    reels_completo = call_agent(reels_gerador, entrada_do_agente_reels)
    return reels_completo

# Agente 3: Redator do Post
def agente_redator(topico, plano_de_post): # Nome da função original
    redator = Agent(
        name="agente_redator", # Nome interno do agente
        model="gemini-2.0-flash",
        instruction="""
        Você é um Redator Criativo especializado em criar posts virais para redes sociais de um escritório de advocacia luso-brasileiro.
        Você escreve posts para o escritório CK Sasso, um escritório de advocacia luso-brasileiro.
        Utilize o tema fornecido no plano de post e os pontos mais relevantes fornecidos e, com base nisso,
        escreva um rascunho de post para Instagram sobre o tema indicado.
        É **ABSOLUTAMENTE ESSENCIAL** sempre seguir as regras do marketing jurídico para advogados, que **PROÍBEM VEEMENTEMENTE** propaganda direta.
        A propaganda deve ser feita de forma sutil e indireta. **NUNCA use expressões como 'agende uma consulta', 'entre em contato', 'ligue agora' ou qualquer outra chamada direta para ação.**
        **Prefira, e use exclusivamente, frases informativas ou sugestões como 'Consulte um advogado especializado para avaliar seu caso e iniciar o processo o quanto antes.', 'Para mais informações, procure um profissional do direito qualificado.', ou 'Busque orientação jurídica para entender seus direitos.'**
        O post deve ser engajador, informativo, com linguagem simples e incluir 2 a 4 hashtags no final.
        **Apresente o post com a seguinte estrutura:**
        **Título Sugerido:** [Seu Título]
        **Corpo do Post:** [Texto do Post]
        **Chamada Sutil para Ação:** [Frase informativa sutil]
        **Hashtags:** [Suas #hashtags]
        """,
        description="Agente redator de posts engajadores para Instagram"
    )
    entrada_do_agente_redator = f"Tópico: {topico}\nPlano de post: {plano_de_post}"
    rascunho = call_agent(redator, entrada_do_agente_redator)
    return rascunho

# Agente 4: Revisor de Qualidade
def agente_revisor(topico, rascunho_gerado): # Nome da função original
    revisor = Agent(
        name="agente_revisor", # Nome interno do agente
        model="gemini-2.0-flash",
        instruction="""
    	Você é um Editor e Revisor de Conteúdo meticuloso, especializado em posts para redes sociais de um escritório de advocacia luso-brasileiro, com foco no Instagram.
    	Use um tom de escrita adequado para um escritório de advocacia, mas também simples para que seja compreendido por uma pessoa leiga. Seja empático, simpático, bem disposto e educado.
    	Revise o rascunho de post de Instagram abaixo sobre o tópico indicado, verificando clareza, concisão, correção, tom e a aderência **rigorosa** às regras de marketing jurídico (sem propaganda direta).

    	**Sua tarefa é simples: FORNECER O TEXTO COMPLETO E FINAL DO POST JÁ REVISADO.**
    	Você deve pegar o rascunho fornecido, aplicar todas as melhorias (clareza, concisão, correção gramatical, ajuste de tom, correção de chamadas para ação direta para informativas sutis)
    	e **APRESENTAR APENAS o texto final do post, com suas próprias formatações de markdown (títulos, negritos, emojis, etc.)**.

    	**NÃO inclua o rascunho original novamente no seu output.**
    	**NÃO liste as sugestões separadamente; as sugestões devem ser incorporadas ao texto final.**

    	**É CRÍTICO E OBRIGATÓRIO**: No final do texto **COMPLETO E REVISADO** do post, adicione UMA ÚNICA pequena nota sobre as alterações, no formato EXATO:
    	'Post revisado e pronto para publicar! (Detalhes da revisão: [descreva brevemente as melhorias aplicadas, e.g., "ajuste de clareza", "correção de pontuação", "remoção de CA direta"])'
    	Se nenhuma alteração significativa foi necessária, a nota DEVE ser EXATAMENTE:
    	'Post revisado e pronto para publicar! (Detalhes da revisão: Sem alterações significativas)'

    	**EXEMPLO DE FORMATO DE SAÍDA FINAL (APENAS O TEXTO REVISADO E A NOTA):**
    	## Título Sugerido: Seus Direitos ao Arrematar Imóveis
    	Texto do post revisado, claro e conciso...
    	Chamada Sutil para Ação: Busque orientação jurídica.
    	Hashtags: #direitos #imoveis #advocacia

    	Post revisado e pronto para publicar! (Detalhes da revisão: Ajuste de tom, clareza e CTA sutil)
    	""",
    
        description="Agente revisor de post para redes sociais."
    )
    entrada_do_agente_revisor = f"Tópico: {topico}\nRascunho: {rascunho_gerado}"
    texto_revisado = call_agent(revisor, entrada_do_agente_revisor)
    return texto_revisado

# ... (código da função agente_revisor termina aqui) ...

# NOVO AGENTE AQUI: Agente de Legendas
def agente_legenda(topico, post_final_revisado):
    criador_legenda = Agent(
        name="agente_legenda", # Nome interno do agente
        model="gemini-2.0-flash", # Usando o modelo que você preferiu
        instruction="""
        Você é um Criador de Legendas MASTER para posts de redes sociais de um escritório de advocacia luso-brasileiro (CK Sasso), com foco no Instagram.
        Sua função é gerar uma **legenda completa e robusta**, mas também CURIOSA, ATRAENTE e OTIMIZADA para o Instagram, que sirva quase como um mini-post, com base no tópico e no post final revisado que você receberá.
        A legenda deve ser **altamente informativa, envolvente, profissional, mas de fácil compreensão para o público leigo.**, **totalmente otimizadas para serem copiadas e coladas diretamente**.

        **Estrutura OBRIGATÓRIA da Legenda:**
        1. **Corpo da Legenda:**
            * Mínimo de 3-4 frases, mas pode ser um parágrafo (até 6-7 linhas), explicando o tema principal de forma concisa e clara.
            * Deve conter informações valiosas e relevantes que complementam o post principal ou resumem seus pontos chave.
            * Use um tom simpático, informativo e profissional.
            * Inclua 1-3 emojis relevantes que enriqueçam o texto.
        2.  **Hashtags:**
            * No final da legenda, adicione um bloco de 5 a 6 hashtags relevantes e estratégicas para o tema jurídico e o público-alvo.
            * Exemplos: #DireitoDeFamilia #AdvocaciaPortugal #NacionalidadePortuguesa #DireitoDigital #LGPD
        3.  **Chamada para Ação (CTA) Sutil (Opcional, mas desejável):**
            * Se apropriado, inclua uma frase curta e engajadora que incentive o compartilhamento ou a reflexão (ex: "Conhece alguém que se encaixa nesse perfil? Compartilhe esta informação!"). **NUNCA use CTAs diretas para "agendar consulta" ou "ligar agora" ou "entre em contato".**
        4.  **Disclaimer (Obrigatório):**
            * **SEMPRE inclua a frase:** "Este post tem caráter informativo e não substitui uma consulta jurídica especializada."
            * Esta frase deve ser a ÚLTIMA linha da sua resposta.

        **É ABSOLUTAMENTE OBRIGATÓRIO que a sua resposta contenha SOMENTE a legenda no formato especificado, sem nenhuma introdução ("Aqui está sua legenda:") ou conclusão extra.**

        **EXEMPLO DE OUTPUT ESPERADO (APENAS A LEGENDA COMPLETA):**
        Muitos bisnetos de portugueses sonham com a cidadania europeia. Embora não haja um caminho direto, a nacionalidade pode ser alcançada através de um processo em "cascata": primeiro, o neto(a) do cidadão português original obtém a nacionalidade, e então, transmite esse direito ao filho(a) (o bisneto). É um processo que exige paciência, organização documental e estratégia.

        #NacionalidadePortuguesaParaBisnetos #BisnetoDePortugues #CidadaniaEmCascata #AdvogadoNacionalidadePortuguesa #PlanejamentoMigratorio #DireitoDeSangue #PortugalBrasil
        Este post tem caráter informativo e não substitui uma consulta jurídica especializada.
        """,
        description="Agente que gera legendas para posts de Instagram."
    )
    entrada_do_agente_legenda = f"Tópico: {topico}\nPost final revisado: {post_final_revisado}\n\nLegenda:" #Adiciona um "Legenda:" para guiar
    legenda_gerada = call_agent(criador_legenda, entrada_do_agente_legenda)
    return legenda_gerada

# Agente 5: Criador de Imagem
def agente_imagem(topico, texto_revisado): # Nome da função original
    criador = Agent(
        name="agente_imagem", # Nome interno do agente
        model="gemini-2.5-flash-preview-05-20", # Mantenha o modelo mais recente para imagem
        instruction="""
        Você é um Criador de Imagem, especializado em posts para redes sociais de um escritório de advocacia luso-brasileiro, com foco no Instagram.
        Veja o texto do post de Instagram criado sobre o tópico indicado e **crie APENAS a descrição detalhada e criativa (um prompt) para uma IA de geração de imagem.**
        Seja criativo, mas não fuja do tema e esteja atento sempre à formalidade esperada de um escritório de advocacia. A descrição deve ser clara e visualmente rica para que uma IA possa 	gerar uma imagem de alta qualidade.
        **A descrição da imagem deve incluir elementos como:** estilo (realista, ilustração, abstrato), cores predominantes, objetos, cenário, emoções, e qualquer outro detalhe relevante 	para a imagem do post jurídico.

        **Importante:** Sua resposta deve conter SOMENTE o prompt da imagem. NÃO adicione introduções como "Crie uma imagem que transmita...", "Aqui está a descrição detalhada para a IA:", 	nem conclusões como "Prompt pronto para a IA!". Comece e termine com o prompt da imagem.

        **Exemplo de Output esperado (APENAS o prompt da imagem):**
        Crie uma imagem profissional e sofisticada em um estilo realista ou render 3D limpo e de alta qualidade. A cena central deve focar na entrada de uma propriedade residencial moderna 	e atraente...
        """,
        description="Agente criador de imagem de post para redes sociais."
    )
    entrada_do_agente_imagem = f"Tópico: {topico}\nTexto Revisado: {texto_revisado}"
    imagem_gerada = call_agent(criador, entrada_do_agente_imagem)
    return imagem_gerada

# --- Função Principal que Orquestra os Agentes (NOVIDADE AQUI!) ---
def gerar_post_completo(topico_input: str) -> dict:
    """
    Orquestra a chamada dos 5 agentes para gerar um post de marketing jurídico completo.
    Retorna um dicionário com os resultados de cada etapa.
    """
    data_de_hoje = date.today().strftime("%d/%m/%Y")
    resultados = {}

    # 1. Agente Buscador
    if topico_input:
        lancamentos_buscados = agente_buscador(topico_input, data_de_hoje)
        resultados['lancamentos_buscados'] = lancamentos_buscados

        # 2. Agente Planejador
        plano_de_post = agente_planejador(topico_input, lancamentos_buscados)
        resultados['plano_de_post'] = plano_de_post

        # NOVO PASSO: Chamar Agente Criador de Reels COMPLETO
        reels_conteudo_completo = agente_reels_completo(topico_input, plano_de_post)
        resultados['reels_conteudo_completo'] = reels_conteudo_completo # Armazena todo o output do Reels

        # 3. Agente Redator
        rascunho_de_post = agente_redator(topico_input, plano_de_post)
        resultados['rascunho_de_post'] = rascunho_de_post

        # 4. Agente Revisor
        post_final = agente_revisor(topico_input, rascunho_de_post)
        resultados['post_final'] = post_final

        # NOVO PASSO: Chamar o Agente de Legendas
        legenda_post = agente_legenda(topico_input, post_final) # Chama a nova função
        resultados['legenda_post'] = legenda_post # Adiciona a legenda aos resultados

        # 5. Agente Criador de Imagem (gera o prompt para a imagem)
        imagem_gerada_prompt = agente_imagem(topico_input, post_final)
        resultados['imagem_gerada_prompt'] = imagem_gerada_prompt

        return resultados
    else:
        return {"erro": "Você esqueceu de digitar o tópico."}