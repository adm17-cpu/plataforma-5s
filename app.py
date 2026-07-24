import streamlit as st
import pandas as pd
import requests
import base64
import json
from datetime import datetime
import os

# =========================================================
# 1. CONFIGURAÇÕES E CONSTANTES
# =========================================================
st.set_page_config(
    page_title="Sistema de Acompanhamento 5S",
    page_icon="🔍",
    layout="wide"
)

IMGBB_API_KEY = "96c2d6fa3d4537d7af2d3d7f39eb3031"
DB_FILE = "dados_5s.json"

# =========================================================
# 2. FUNÇÕES DE ARMAZENAMENTO E API (IMGBB)
# =========================================================
def enviar_foto_imgbb(file_bytes, filename):
    """Envia a imagem para o ImgBB e retorna a URL pública direta."""
    try:
        base64_image = base64.b64encode(file_bytes).decode('utf-8')
        payload = {
            "key": IMGBB_API_KEY,
            "image": base64_image,
            "name": filename
        }
        response = requests.post("https://api.imgbb.com/1/upload", data=payload)
        data = response.json()
        if data.get("success"):
            return data["data"]["url"]
        else:
            st.error(f"Erro no ImgBB: {data.get('error', {}).get('message')}")
            return None
    except Exception as e:
        st.error(f"Falha na conexão com o servidor de imagens: {e}")
        return None

def carregar_dados():
    """Carrega a base de dados do arquivo JSON local."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "usuarios": {"admin": "1234"},
        "auditorias": [],
        "areas": ["Produção", "Escritório", "Almoxarifado", "Manutenção"]
    }

def salvar_dados(dados):
    """Salva a base de dados no arquivo JSON local."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Inicialização do estado dos dados na sessão do Streamlit
if "db" not in st.session_state:
    st.session_state.db = carregar_dados()

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# =========================================================
# 3. MÓDULO DE AUTENTICAÇÃO E LOGIN
# =========================================================
def tela_login():
    st.title("🔐 Sistema 5S - Autenticação")
    tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])

    with tab1:
        st.subheader("Login")
        usuario = st.text_input("Usuário", key="login_user")
        senha = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Acessar Sistema"):
            usuarios = st.session_state.db["usuarios"]
            if usuario in usuarios and usuarios[usuario] == senha:
                st.session_state.usuario_logado = usuario
                st.success(f"Bem-vindo, {usuario}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with tab2:
        st.subheader("Cadastrar Novo Usuário")
        novo_usuario = st.text_input("Novo Usuário", key="new_user")
        nova_senha = st.text_input("Nova Senha", type="password", key="new_pass")
        if st.button("Cadastrar"):
            if novo_usuario and nova_senha:
                if novo_usuario in st.session_state.db["usuarios"]:
                    st.warning("Usuário já existente!")
                else:
                    st.session_state.db["usuarios"][novo_usuario] = nova_senha
                    salvar_dados(st.session_state.db)
                    st.success("Conta criada com sucesso! Faça login na aba ao lado.")
            else:
                st.warning("Preencha todos os campos.")

# =========================================================
# 4. PAINEL PRINCIPAL DA APLICAÇÃO
# =========================================================
def tela_principal():
    st.sidebar.title(f"👤 {st.session_state.usuario_logado}")
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.rerun()

    st.sidebar.markdown("---")
    opcao = st.sidebar.radio(
        "Navegação",
        ["Dashboard", "Nova Auditoria / Registro", "Histórico de Auditorias", "Gestão de Áreas", "Assistente IA 5S"]
    )

    # -----------------------------------------------------
    # ABA: DASHBOARD
    # -----------------------------------------------------
    if opcao == "Dashboard":
        st.title("📊 Dashboard de Indicadores 5S")
        auditorias = st.session_state.db["auditorias"]

        if not auditorias:
            st.info("Nenhuma auditoria registrada até o momento.")
            return

        df = pd.DataFrame(auditorias)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Auditorias", len(df))
        col2.metric("Média Geral das Notas", f"{df['pontuacao'].mean():.1f} / 100")
        col3.metric("Última Auditoria", df['data'].max())

        st.markdown("---")
        st.subheader("Pontuação por Área")
        grafico_area = df.groupby("area")["pontuacao"].mean().reset_index()
        st.bar_chart(grafico_area.set_index("area"))

    # -----------------------------------------------------
    # ABA: NOVA AUDITORIA (COM UPLOAD IMGBB)
    # -----------------------------------------------------
    elif opcao == "Nova Auditoria / Registro":
        st.title("📝 Nova Auditoria de Acompanhamento 5S")
        
        with st.form("form_auditoria", clear_on_submit=True):
            area = st.selectbox("Selecione a Área:", st.session_state.db["areas"])
            auditor = st.text_input("Auditor Responsável:", value=st.session_state.usuario_logado)
            
            st.subheader("Avaliação dos 5 Sensos (0 a 20 pontos cada)")
            seiri = st.slider("1. Seiri (Utilização)", 0, 20, 15)
            seiton = st.slider("2. Seiton (Organização)", 0, 20, 15)
            seiso = st.slider("3. Seiso (Limpeza)", 0, 20, 15)
            seiketsu = st.slider("4. Seiketsu (Padronização)", 0, 20, 15)
            shitsuke = st.slider("5. Shitsuke (Disciplina)", 0, 20, 15)

            observacoes = st.text_area("Observações / Pontos de Melhoria:")
            foto = st.file_uploader("Enviar Foto da Auditoria:", type=["png", "jpg", "jpeg"])

            submeter = st.form_submit_button("Salvar Registro")

        if submeter:
            pontuacao_total = seiri + seiton + seiso + seiketsu + shitsuke
            url_foto = None

            if foto is not None:
                with st.spinner("Enviando foto para a nuvem..."):
                    url_foto = enviar_foto_imgbb(foto.getvalue(), foto.name)

            registro = {
                "id": len(st.session_state.db["auditorias"]) + 1,
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "area": area,
                "auditor": auditor,
                "pontuacao": pontuacao_total,
                "observacoes": observacoes,
                "foto_url": url_foto
            }

            st.session_state.db["auditorias"].append(registro)
            salvar_dados(st.session_state.db)
            st.success(f"Auditoria registrada com sucesso! Pontuação Final: {pontuacao_total}/100")

    # -----------------------------------------------------
    # ABA: HISTÓRICO DE AUDITORIAS (VER FOTOS E EXPORTAR)
    # -----------------------------------------------------
    elif opcao == "Histórico de Auditorias":
        st.title("📋 Histórico de Auditorias e Fotos")
        auditorias = st.session_state.db["auditorias"]

        if not auditorias:
            st.info("Nenhum registro encontrado.")
            return

        df = pd.DataFrame(auditorias)
        st.dataframe(df[["id", "data", "area", "auditor", "pontuacao", "observacoes"]], use_container_width=True)

        st.subheader("📷 Galeria e Detalhes")
        for item in reversed(auditorias):
            with st.expander(f"Auditoria #{item['id']} - Área: {item['area']} ({item['data']})"):
                st.write(f"**Auditor:** {item['auditor']}")
                st.write(f"**Nota Total:** {item['pontuacao']}/100")
                st.write(f"**Observações:** {item['observacoes']}")
                
                if item.get("foto_url"):
                    st.image(item["foto_url"], caption="Foto da Auditoria", width=350)
                    st.link_button("🌐 Abrir Foto em Tela Cheia no Navegador", item["foto_url"])
                else:
                    st.write(" *Nenhuma foto anexada.*")

        st.markdown("---")
        # Exportação CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Relatório em CSV",
            data=csv,
            file_name=f"relatorio_5s_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )

    # -----------------------------------------------------
    # ABA: GESTÃO DE ÁREAS
    # -----------------------------------------------------
    elif opcao == "Gestão de Áreas":
        st.title("🏢 Gerenciamento de Áreas")
        
        nova_area = st.text_input("Cadastrar Nova Área:")
        if st.button("Adicionar Área"):
            if nova_area and nova_area not in st.session_state.db["areas"]:
                st.session_state.db["areas"].append(nova_area)
                salvar_dados(st.session_state.db)
                st.success(f"Área '{nova_area}' cadastrada!")
                st.rerun()
            else:
                st.warning("Área inválida ou já cadastrada.")

        st.subheader("Áreas Atuais:")
        for area in st.session_state.db["areas"]:
            st.write(f"- {area}")

    # -----------------------------------------------------
    # ABA: CHAT COM ASSISTENTE IA 5S
    # -----------------------------------------------------
    elif opcao == "Assistente IA 5S":
        st.title("🤖 Assistente Virtual 5S")
        st.write("Tire dúvidas sobre padronização, auditorias e melhorias do programa 5S.")

        if "mensagens_chat" not in st.session_state:
            st.session_state.mensagens_chat = [
                {"role": "assistant", "content": "Olá! Como posso ajudar na implementação e auditoria do 5S na sua empresa hoje?"}
            ]

        for msg in st.session_state.mensagens_chat:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Digite sua dúvida..."):
            st.session_state.mensagens_chat.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            # Resposta simples de demonstração (pode ser conectada com API da OpenAI/Gemini)
            resposta = f"Em relação ao 5S: Para a dúvida '{prompt}', a recomendação principal é focar no senso de Padronização (Seiketsu), mantendo regras visuais claras para toda a equipe."
            
            st.session_state.mensagens_chat.append({"role": "assistant", "content": resposta})
            st.chat_message("assistant").write(resposta)

# =========================================================
# 5. EXECUÇÃO DO APLICATIVO
# =========================================================
if st.session_state.usuario_logado is None:
    tela_login()
else:
    tela_principal()
