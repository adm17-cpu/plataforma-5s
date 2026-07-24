import streamlit as st
import pandas as pd
import datetime

# -----------------------------------------------------------------------------
# Configuração da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema 5S - Gestão de Qualidade",
    page_icon="📋",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Simulação de APIs / Banco de Dados (Substitua pela sua integração Base44/API)
# -----------------------------------------------------------------------------
def fetch_user():
    return {"email": "usuario@calabria.org.br", "nome": "Auditor 5S"}

def fetch_areas():
    if "areas" not in st.session_state:
        st.session_state.areas = [
            {"id": 1, "nome": "Almoxarifado", "responsavel": "João Silva"},
            {"id": 2, "nome": "Cozinha Industrial", "responsavel": "Maria Souza"},
            {"id": 3, "nome": "Escritório Central", "responsavel": "Carlos Lima"}
        ]
    return st.session_state.areas

def fetch_audits():
    if "audits" not in st.session_state:
        st.session_state.audits = [
            {"id": 101, "area": "Almoxarifado", "nota": 88, "data": "2026-03-01", "status": "Concluída"},
            {"id": 102, "area": "Cozinha Industrial", "nota": 94, "data": "2026-03-05", "status": "Concluída"},
            {"id": 103, "area": "Escritório Central", "nota": 72, "data": "2026-03-10", "status": "Pendente"}
        ]
    return st.session_state.audits

# -----------------------------------------------------------------------------
# Cabeçalho da Aplicação (Header)
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
        user = fetch_user()
        st.markdown(f"**Usuário:** `{user['email']}`")

    st.markdown("---")

# -----------------------------------------------------------------------------
# Seções da Aplicação (Abas)
# -----------------------------------------------------------------------------
def render_audit_section(areas):
    st.subheader("📋 Nova Auditoria 5S")
    
    if not areas:
        st.warning("Nenhuma área cadastrada. Vá até a aba 'Config' para adicionar uma área.")
        return

    with st.form("form_auditoria"):
        area_nome = st.selectbox("Selecione a Área", options=[a["nome"] for a in areas])
        
        st.write("---")
        st.markdown("### Pontuação dos Sensos (0 a 100)")
        
        seiri = st.slider("1. Seiri (Utilização)", 0, 100, 80)
        seiton = st.slider("2. Seiton (Organização)", 0, 100, 80)
        seiso = st.slider("3. Seiso (Limpeza)", 0, 100, 80)
        seiketsu = st.slider("4. Seiketsu (Padronização)", 0, 100, 80)
        shitsuke = st.slider("5. Shitsuke (Disciplina)", 0, 100, 80)
        
        observacoes = st.text_area("Observações / Oportunidades de Melhoria")
        
        submitted = st.form_submit_button("Salvar Auditoria", use_container_width=True)
        if submitted:
            nota_media = round((seiri + seiton + seiso + seiketsu + shitsuke) / 5, 1)
            
            nova_auditoria = {
                "id": len(st.session_state.audits) + 1,
                "area": area_nome,
                "nota": nota_media,
                "data": datetime.date.today().strftime("%Y-%m-%d"),
                "status": "Concluída"
            }
            st.session_state.audits.append(nova_auditoria)
            st.success(f"Auditoria para **{area_nome}** salva com sucesso! Média Final: **{nota_media}%**")

def render_dashboard_section(audits):
    st.subheader("📊 Dashboard de Desempenho")
    
    if not audits:
        st.info("Nenhuma auditoria realizada ainda.")
        return

    df = pd.DataFrame(audits)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Auditorias", len(df))
    col2.metric("Média Geral de Qualidade", f"{df['nota'].mean():.1f}%")
    col3.metric("Auditorias Pendentes", len(df[df['status'] == 'Pendente']))
    
    st.write("---")
    st.markdown("### Desempenho por Área (Nota %)")
    st.bar_chart(df, x="area", y="nota", color="#2563eb")

def render_reports_section(audits):
    st.subheader("📄 Relatórios de Auditorias")
    
    if not audits:
        st.info("Nenhum dado disponível para relatório.")
        return

    df = pd.DataFrame(audits)
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Relatório em CSV",
        data=csv,
        file_name='relatorio_auditorias_5s.csv',
        mime='text/csv',
        use_container_width=True
    )

def render_config_section(areas):
    st.subheader("⚙️ Configurações do Sistema")
    
    st.markdown("### Áreas Cadastradas")
    for idx, area in enumerate(areas):
        c1, c2 = st.columns([4, 1])
        c1.write(f"• **{area['nome']}** — *Resp: {area['responsavel']}*")
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

def render_consultor_ia():
    st.subheader("🤖 Consultor IA - Sistema 5S")
    st.write("Tire dúvidas sobre padronização, auditorias e plano de ação 5S.")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Olá! Sou seu assistente virtual de 5S. Como posso ajudar com a organização da sua unidade?"}
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Digite sua pergunta... Ex: Como implantar o Seiton na cozinha?"):
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            resposta = f"**Consultor 5S:** Em relação a *'{user_input}'*, a recomendação padrão é realizar a identificação visual clara, delimitando locais específicos e descartando itens obsoletos."
            st.write(resposta)
            st.session_state.chat_messages.append({"role": "assistant", "content": resposta})

# -----------------------------------------------------------------------------
# Execução Principal (Main)
# -----------------------------------------------------------------------------
def main():
    render_header()
    
    areas = fetch_areas()
    audits = fetch_audits()
    
    # Navegação por Abas
    tab_audit, tab_dash, tab_reports, tab_config, tab_ia = st.tabs([
        "📋 Auditoria", 
        "📊 Dashboard", 
        "📄 Relatórios", 
        "⚙️ Config", 
        "🤖 Consultor IA"
    ])
    
    with tab_audit:
        render_audit_section(areas)
        
    with tab_dash:
        render_dashboard_section(audits)
        
    with tab_reports:
        render_reports_section(audits)
        
    with tab_config:
        render_config_section(areas)
        
    with tab_ia:
        render_consultor_ia()

if __name__ == "__main__":
    main()
