import streamlit as st
import pandas as pd
import datetime

# -----------------------------------------------------------------------------
# Configuração Inicial da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema 5S - Acompanhamento",
    page_icon="📋",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Gerenciamento de Estado Global (Banco de Dados Simulado)
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "areas" not in st.session_state:
    st.session_state.areas = [
        {"id": 1, "nome": "Almoxarifado", "responsavel": "João Silva"},
        {"id": 2, "nome": "Cozinha Industrial", "responsavel": "Maria Souza"},
        {"id": 3, "nome": "Escritório Central", "responsavel": "Carlos Lima"}
    ]

if "acomp" not in st.session_state:
    st.session_state.acomp = [
        {
            "id": 101, 
            "area": "Almoxarifado", 
            "nota": 88.0, 
            "data": "2026-03-01", 
            "status": "Concluído",
            "seiri": 90, "seiton": 85, "seiso": 90, "seiketsu": 85, "shitsuke": 90,
            "obs": "Organização do estoque OK.",
            "foto_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d"
        },
        {
            "id": 102, 
            "area": "Cozinha Industrial", 
            "nota": 94.0, 
            "data": "2026-03-05", 
            "status": "Concluído",
            "seiri": 95, "seiton": 90, "seiso": 95, "seiketsu": 95, "shitsuke": 95,
            "obs": "Higiene impecável.",
            "foto_url": ""
        }
    ]

# -----------------------------------------------------------------------------
# 🔐 Tela de Login
# -----------------------------------------------------------------------------
def render_login():
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso ao Sistema 5S</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            usuario = st.text_input("Usuário / E-mail")
            senha = st.text_input("Senha", type="password")
            btn_entrar = st.form_submit_button("Entrar", use_container_width=True)
            
            if btn_entrar:
                # Login simples de demonstração (Pode integrar com API/Banco)
                if usuario and senha:
                    st.session_state.logged_in = True
                    st.session_state.user = {"email": usuario}
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, preencha o usuário e a senha.")

# -----------------------------------------------------------------------------
# Cabeçalho da Aplicação
# -----------------------------------------------------------------------------
def render_header():
    col_logo, col_title, col_user = st.columns([1, 3, 2])
    
    with col_logo:
        st.image(
            "https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/691dbc22a1c65765d5d316b9/17393037c_LogoRedeCalabria_Horizontal_Branco.png",
            width=170
        )
        
    with col_title:
        st.title("Sistema 5S")
        st.caption("Gestão de Qualidade e Organização")

    with col_user:
        st.markdown(f"**Usuário:** `{st.session_state.user['email']}`")
        if st.button("Sair / Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    st.markdown("---")

# -----------------------------------------------------------------------------
# 📋 Seção 1: Novo Acompanhamento / Edição
# -----------------------------------------------------------------------------
def render_acomp_section(areas):
    st.subheader("📋 Acompanhamento 5S")
    
    if not areas:
        st.warning("Nenhuma área cadastrada. Vá até a aba 'Config' para adicionar uma área.")
        return

    modo = st.radio("Selecione a ação:", ["Novo Acompanhamento", "Editar Acompanhamento Existente"], horizontal=True)
    
    acomp_para_editar = None
    if modo == "Editar Acompanhamento Existente":
        if not st.session_state.acomp:
            st.info("Nenhum acompanhamento registrado para editar.")
            return
        
        opcoes = {f"ID #{a['id']} - {a['area']} ({a['data']})": a for a in st.session_state.acomp}
        escolha = st.selectbox("Escolha o acompanhamento para editar:", list(opcoes.keys()))
        acomp_para_editar = opcoes[escolha]

    # Valores padrão (Edição ou Novo)
    val_area = acomp_para_editar["area"] if acomp_para_editar else areas[0]["nome"]
    val_seiri = acomp_para_editar["seiri"] if acomp_para_editar else 80
    val_seiton = acomp_para_editar["seiton"] if acomp_para_editar else 80
    val_seiso = acomp_para_editar["seiso"] if acomp_para_editar else 80
    val_seiketsu = acomp_para_editar["seiketsu"] if acomp_para_editar else 80
    val_shitsuke = acomp_para_editar["shitsuke"] if acomp_para_editar else 80
    val_obs = acomp_para_editar["obs"] if acomp_para_editar else ""
    val_foto = acomp_para_editar["foto_url"] if acomp_para_editar else ""
    val_status = acomp_para_editar["status"] if acomp_para_editar else "Concluído"

    with st.form("form_acompanhamento"):
        st.markdown("### Dados Gerais")
        area_nome = st.selectbox("Área", options=[a["nome"] for a in areas], index=[a["nome"] for a in areas].index(val_area) if val_area in [a["nome"] for a in areas] else 0)
        status = st.selectbox("Status", ["Concluído", "Pendente", "Em Andamento"], index=["Concluído", "Pendente", "Em Andamento"].index(val_status))
        
        st.write("---")
        st.markdown("### Pontuação dos Sensos (0 a 100)")
        seiri = st.slider("1. Seiri (Utilização)", 0, 100, val_seiri)
        seiton = st.slider("2. Seiton (Organização)", 0, 100, val_seiton)
        seiso = st.slider("3. Seiso (Limpeza)", 0, 100, val_seiso)
        seiketsu = st.slider("4. Seiketsu (Padronização)", 0, 100, val_seiketsu)
        shitsuke = st.slider("5. Shitsuke (Disciplina)", 0, 100, val_shitsuke)
        
        st.write("---")
        st.markdown("### Evidências e Observações")
        foto_url = st.text_input("Link Externo da Fotografia (Drive, Cloud, etc.)", value=val_foto, help="Cole a URL da foto para não sobrecarregar a aplicação.")
        if foto_url:
            st.markdown(f"🔗 [Visualizar Imagem Externa]({foto_url})")
            
        observacoes = st.text_area("Observações / Planos de Ação", value=val_obs)
        
        btn_salvar = st.form_submit_button("Salvar Registro", use_container_width=True)
        
        if btn_salvar:
            nota_media = round((seiri + seiton + seiso + seiketsu + shitsuke) / 5, 1)
            
            dados = {
                "id": acomp_para_editar["id"] if acomp_para_editar else len(st.session_state.acomp) + 101,
                "area": area_nome,
                "nota": nota_media,
                "data": acomp_para_editar["data"] if acomp_para_editar else datetime.date.today().strftime("%Y-%m-%d"),
                "status": status,
                "seiri": seiri, "seiton": seiton, "seiso": seiso, "seiketsu": seiketsu, "shitsuke": shitsuke,
                "obs": observacoes,
                "foto_url": foto_url
            }
            
            if acomp_para_editar:
                # Atualizar existente
                idx = st.session_state.acomp.index(acomp_para_editar)
                st.session_state.acomp[idx] = dados
                st.success("Acompanhamento 5S atualizado com sucesso!")
            else:
                # Novo
                st.session_state.acomp.append(dados)
                st.success("Novo Acompanhamento 5S salvo com sucesso!")
            
            st.rerun()

# -----------------------------------------------------------------------------
# 📊 Seção 2: Dashboard
# -----------------------------------------------------------------------------
def render_dashboard_section(acomp):
    st.subheader("📊 Dashboard de Desempenho 5S")
    
    if not acomp:
        st.info("Nenhum acompanhamento realizado ainda.")
        return

    df = pd.DataFrame(acomp)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Acompanhamentos", len(df))
    c2.metric("Média Geral do 5S", f"{df['nota'].mean():.1f}%")
    c3.metric("Pendentes / Em Andamento", len(df[df['status'] != 'Concluído']))
    
    st.write("---")
    st.markdown("### Desempenho Médio por Área")
    df_area = df.groupby("area")["nota"].mean().reset_index()
    st.bar_chart(df_area, x="area", y="nota", color="#2563eb")

# -----------------------------------------------------------------------------
# 📄 Seção 3: Relatórios Filtrados, PDF, E-mail e Relatório Geral
# -----------------------------------------------------------------------------
def render_reports_section(acomp):
    st.subheader("📄 Relatórios de Acompanhamento 5S")
    
    if not acomp:
        st.info("Nenhum registro disponível para relatório.")
        return

    df = pd.DataFrame(acomp)

    # 🔍 Filtros de Relatório
    st.markdown("### 🔍 Filtros de Busca")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    areas_list = ["Todas"] + list(df["area"].unique())
    sel_area = f_col1.selectbox("Filtrar por Área", areas_list)
    
    status_list = ["Todos"] + list(df["status"].unique())
    sel_status = f_col2.selectbox("Filtrar por Status", status_list)
    
    sel_busca = f_col3.text_input("Buscar por termo (obs/área)")

    # Aplicação dos filtros
    df_filtered = df.copy()
    if sel_area != "Todas":
        df_filtered = df_filtered[df_filtered["area"] == sel_area]
    if sel_status != "Todos":
        df_filtered = df_filtered[df_filtered["status"] == sel_status]
    if sel_busca:
        df_filtered = df_filtered[df_filtered["obs"].str.contains(sel_busca, case=False, na=False) | df_filtered["area"].str.contains(sel_busca, case=False, na=False)]

    st.write("---")
    st.markdown(f"### 📋 Registros Encontrados ({len(df_filtered)})")
    
    # Exibição da tabela formatada
    col_exibicao = ["id", "area", "data", "nota", "status", "foto_url", "obs"]
    st.dataframe(
        df_filtered[col_exibicao], 
        column_config={
            "foto_url": st.column_config.LinkColumn("Fotografia (Link Externo)"),
            "nota": st.column_config.NumberColumn("Média %", format="%.1f%%")
        },
        use_container_width=True
    )

    st.write("---")
    
    # 🖨️ Ações do Relatório: PDF, CSV e E-mail
    st.markdown("### 🛠️ Ações e Exportação")
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    
    # Exportar CSV
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    exp_col1.download_button(
        "📥 Exportar para CSV",
        data=csv_data,
        file_name="relatorio_5s.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Gerar Relatório Geral / Impressão PDF
    if exp_col2.button("🖨️ Gerar PDF / Imprimir", use_container_width=True):
        st.info("Para salvar em PDF: Clique no botão abaixo para abrir a visualização limpa e use **Ctrl + P** (Imprimir) salvando como PDF.")
        
        # Gerando HTML limpo para impressão
        html_content = f"""
        <h2>Relatório Geral de Acompanhamento 5S</h2>
        <p><b>Data do Relatório:</b> {datetime.date.today().strftime('%d/%m/%Y')}</p>
        <hr/>
        {df_filtered.to_html(index=False)}
        """
        st.components.v1.html(html_content, height=300, scrolling=True)

    # Enviar por E-mail
    with exp_col3.popover("✉️ Enviar por E-mail", use_container_width=True):
        st.markdown("#### Enviar Relatório")
        email_destino = st.text_input("E-mail do Destinatário")
        mensagem_extra = st.text_area("Mensagem Adicional")
        
        if st.button("Enviar Relatório"):
            if email_destino:
                st.success(f"Relatório enviado com sucesso para **{email_destino}**!")
            else:
                st.error("Digite um e-mail válido.")

# -----------------------------------------------------------------------------
# ⚙️ Seção 4: Configurações
# -----------------------------------------------------------------------------
def render_config_section(areas):
    st.subheader("⚙️ Configurações das Áreas")
    
    st.markdown("### Áreas Cadastradas")
    for idx, area in enumerate(areas):
        c1, c2 = st.columns([4, 1])
        c1.write(f"• **{area['nome']}** — *Responsável: {area['responsavel']}*")
        if c2.button("Excluir", key=f"del_{idx}"):
            st.session_state.areas.pop(idx)
            st.toast(f"Área '{area['nome']}' removida com sucesso!")
            st.rerun()

    st.write("---")
    st.markdown("### Adicionar Nova Área")
    with st.form("form_add_area"):
        nome_area = st.text_input("Nome da Área")
        resp_area = st.text_input("Responsável pela Área")
        
        if st.form_submit_button("Cadastrar Área"):
            if nome_area and resp_area:
                nova_area = {"id": len(areas) + 1, "nome": nome_area, "responsavel": resp_area}
                st.session_state.areas.append(nova_area)
                st.success(f"Área '{nome_area}' cadastrada com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos.")

# -----------------------------------------------------------------------------
# 🤖 Seção 5: Consultor IA
# -----------------------------------------------------------------------------
def render_consultor_ia():
    st.subheader("🤖 Consultor IA - Sistema 5S")
    st.write("Tire dúvidas sobre os sensos 5S, planos de ação e padrões de acompanhamento.")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Olá! Sou seu Consultor 5S. Como posso ajudar com os acompanhamentos da sua unidade?"}
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Digite sua pergunta..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            resposta = f"**Consultor 5S:** Em relação a *'{user_input}'*, recomendo manter o padrão de verificação periódica e registrar fotos antes/depois no link externo do acompanhamento."
            st.write(resposta)
            st.session_state.chat_messages.append({"role": "assistant", "content": resposta})

# -----------------------------------------------------------------------------
# Execução Principal (Main)
# -----------------------------------------------------------------------------
def main():
    if not st.session_state.logged_in:
        render_login()
    else:
        render_header()
        
        areas = st.session_state.areas
        acomp = st.session_state.acomp
        
        # Abas da Aplicação
        tab_acomp, tab_dash, tab_reports, tab_config, tab_ia = st.tabs([
            "📋 Acompanhamento 5S", 
            "📊 Dashboard", 
            "📄 Relatórios", 
            "⚙️ Config", 
            "🤖 Consultor IA"
        ])
        
        with tab_acomp:
            render_acomp_section(areas)
            
        with tab_dash:
            render_dashboard_section(acomp)
            
        with tab_reports:
            render_reports_section(acomp)
            
        with tab_config:
            render_config_section(areas)
            
        with tab_ia:
            render_consultor_ia()

if __name__ == "__main__":
    main()
