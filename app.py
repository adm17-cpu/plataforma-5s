import streamlit as st
import pandas as pd
import requests
import base64
import json
from datetime import datetime, date
import os
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from weasyprint import HTML

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
# 2. FUNÇÕES DE SUPORTE (IMGBB, BANCO JSON, PDF E E-MAIL)
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
        "acompanhamentos": [],
        "areas": ["Produção", "Escritório", "Almoxarifado", "Manutenção"]
    }

def salvar_dados(dados):
    """Salva a base de dados no arquivo JSON local."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def gerar_pdf_html(df_acompanhamentos, titulo_relatorio="Relatório de Acompanhamentos 5S"):
    """Gera um documento PDF estilizado a partir de dados de acompanhamentos usando WeasyPrint."""
    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    total_acompanhamentos = len(df_acompanhamentos)
    media_geral = df_acompanhamentos["pontuacao"].mean() if total_acompanhamentos > 0 else 0

    linhas_tabela = ""
    for idx, row in df_acompanhamentos.iterrows():
        foto_html = f'<a href="{row.get("foto_url")}" target="_blank">Ver Foto</a>' if row.get("foto_url") else 'Sem foto'
        
        nota = row['pontuacao']
        cor_badge = "#27ae60" if nota >= 80 else ("#f39c12" if nota >= 60 else "#e74c3c")
        
        linhas_tabela += f"""
        <tr>
            <td>#{row['id']}</td>
            <td>{row['data']}</td>
            <td><b>{row['area']}</b></td>
            <td>{row['responsavel']}</td>
            <td style="text-align: center;"><span style="background-color: {cor_badge}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{nota} / 100</span></td>
            <td>{row['observacoes'] if row['observacoes'] else '-'}</td>
            <td style="text-align: center;">{foto_html}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4 portrait;
                margin: 15mm 12mm;
                background-color: #faf8f5;
            }}
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                color: #2c3e50;
                margin: 0;
                padding: 0;
            }}
            .header {{
                background-color: #1e3a8a;
                color: white;
                padding: 20px;
                border-radius: 6px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                margin: 0 0 5px 0;
                font-size: 22pt;
            }}
            .header p {{
                margin: 0;
                font-size: 10pt;
                opacity: 0.85;
            }}
            .summary-box {{
                width: 100%;
                margin-bottom: 20px;
                border-collapse: collapse;
            }}
            .summary-card {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 12px;
                text-align: center;
            }}
            .summary-card .number {{
                font-size: 18pt;
                font-weight: bold;
                color: #1e3a8a;
            }}
            .summary-card .label {{
                font-size: 9pt;
                color: #64748b;
                text-transform: uppercase;
            }}
            table.data-table {{
                width: 100%;
                border-collapse: collapse;
                background-color: #ffffff;
                border-radius: 6px;
                overflow: hidden;
            }}
            table.data-table th {{
                background-color: #3b82f6;
                color: white;
                padding: 8px 10px;
                font-size: 9pt;
                text-align: left;
            }}
            table.data-table td {{
                padding: 8px 10px;
                font-size: 8.5pt;
                border-bottom: 1px solid #e2e8f0;
            }}
            table.data-table tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 8pt;
                color: #94a3b8;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{titulo_relatorio}</h1>
            <p>Gerado em: {data_geracao} | Sistema de Gestão de Acompanhamento 5S</p>
        </div>

        <table class="summary-box">
            <tr>
                <td style="padding-right: 10px;">
                    <div class="summary-card">
                        <div class="number">{total_acompanhamentos}</div>
                        <div class="label">Total de Acompanhamentos</div>
                    </div>
                </td>
                <td style="padding-left: 10px;">
                    <div class="summary-card">
                        <div class="number">{media_geral:.1f} pts</div>
                        <div class="label">Média Geral de Desempenho</div>
                    </div>
                </td>
            </tr>
        </table>

        <h3>Detalhamento dos Registros</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 5%;">ID</th>
                    <th style="width: 18%;">Data/Hora</th>
                    <th style="width: 15%;">Área</th>
                    <th style="width: 15%;">Responsável</th>
                    <th style="width: 12%;">Pontuação</th>
                    <th style="width: 25%;">Observações</th>
                    <th style="width: 10%;">Foto</th>
                </tr>
            </thead>
            <tbody>
                {linhas_tabela}
            </tbody>
        </table>

        <div class="footer">
            Relatório Oficial do Programa 5S • Documento gerado automaticamente pelo sistema.
        </div>
    </body>
    </html>
    """
    
    pdf_bytes = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes.getvalue()

def enviar_relatorio_email(destinatario, assunto, mensagem_texto, pdf_bytes, nome_arquivo_pdf="Relatorio_5S.pdf", smtp_config=None):
    """Envia o e-mail contendo o relatório em formato PDF anexado."""
    try:
        smtp_server = smtp_config.get("server") if smtp_config else "smtp.gmail.com"
        smtp_port = smtp_config.get("port") if smtp_config else 587
        smtp_user = smtp_config.get("user") if smtp_config else "seu_email@gmail.com"
        smtp_pass = smtp_config.get("password") if smtp_config else "sua_senha_de_app"

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = destinatario
        msg['Subject'] = assunto

        msg.attach(MIMEText(mensagem_texto, 'plain'))

        attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        attachment.add_header('Content-Disposition', 'attachment', filename=nome_arquivo_pdf)
        msg.attach(attachment)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True, "E-mail enviado com sucesso!"
    except Exception as e:
        return False, f"Falha no envio de e-mail: {e}"

# Carregamento e compatibilidade de dados
if "db" not in st.session_state:
    dados_carregados = carregar_dados()
    if "auditorias" in dados_carregados and "acompanhamentos" not in dados_carregados:
        dados_carregados["acompanhamentos"] = dados_carregados.pop("auditorias")
        for item in dados_carregados["acompanhamentos"]:
            if "auditor" in item:
                item["responsavel"] = item.pop("auditor")
    st.session_state.db = dados_carregados

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
        [
            "Dashboard",
            "Novo Acompanhamento / Registro",
            "Editar / Gerenciar Acompanhamentos",
            "Relatório Filtrado & Exportação PDF",
            "Relatório Geral 5S (Executivo)",
            "Enviar Relatório por E-mail",
            "Gestão de Áreas",
            "Assistente IA 5S"
        ]
    )

    # -----------------------------------------------------
    # ABA 1: DASHBOARD
    # -----------------------------------------------------
    if opcao == "Dashboard":
        st.title("📊 Dashboard de Indicadores 5S")
        acompanhamentos = st.session_state.db["acompanhamentos"]

        if not acompanhamentos:
            st.info("Nenhum acompanhamento registrado até o momento.")
            return

        df = pd.DataFrame(acompanhamentos)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Acompanhamentos", len(df))
        col2.metric("Média Geral das Notas", f"{df['pontuacao'].mean():.1f} / 100")
        col3.metric("Último Acompanhamento", df['data'].max())

        st.markdown("---")
        st.subheader("Pontuação Média por Área")
        grafico_area = df.groupby("area")["pontuacao"].mean().reset_index()
        st.bar_chart(grafico_area.set_index("area"))

    # -----------------------------------------------------
    # ABA 2: NOVO ACOMPANHAMENTO
    # -----------------------------------------------------
    elif opcao == "Novo Acompanhamento / Registro":
        st.title("📝 Novo Registro de Acompanhamento 5S")
        
        if not st.session_state.db["areas"]:
            st.warning("Nenhuma área cadastrada. Cadastre áreas na aba 'Gestão de Áreas' antes de continuar.")
            return

        with st.form("form_acompanhamento", clear_on_submit=True):
            area = st.selectbox("Selecione a Área:", st.session_state.db["areas"])
            responsavel = st.text_input("Responsável pelo Acompanhamento:", value=st.session_state.usuario_logado)
            
            st.subheader("Avaliação dos 5 Sensos (0 a 20 pontos cada)")
            seiri = st.slider("1. Seiri (Utilização)", 0, 20, 15)
            seiton = st.slider("2. Seiton (Organização)", 0, 20, 15)
            seiso = st.slider("3. Seiso (Limpeza)", 0, 20, 15)
            seiketsu = st.slider("4. Seiketsu (Padronização)", 0, 20, 15)
            shitsuke = st.slider("5. Shitsuke (Disciplina)", 0, 20, 15)

            observacoes = st.text_area("Observações / Pontos de Melhoria:")
            foto = st.file_uploader("Enviar Foto do Acompanhamento:", type=["png", "jpg", "jpeg"])

            submeter = st.form_submit_button("Salvar Registro")

        if submeter:
            pontuacao_total = seiri + seiton + seiso + seiketsu + shitsuke
            url_foto = None

            if foto is not None:
                with st.spinner("Enviando foto para a nuvem..."):
                    url_foto = enviar_foto_imgbb(foto.getvalue(), foto.name)

            registro = {
                "id": len(st.session_state.db["acompanhamentos"]) + 1,
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "area": area,
                "responsavel": responsavel,
                "seiri": seiri,
                "seiton": seiton,
                "seiso": seiso,
                "seiketsu": seiketsu,
                "shitsuke": shitsuke,
                "pontuacao": pontuacao_total,
                "observacoes": observacoes,
                "foto_url": url_foto
            }

            st.session_state.db["acompanhamentos"].append(registro)
            salvar_dados(st.session_state.db)
            st.success(f"Acompanhamento registrado com sucesso! Pontuação Final: {pontuacao_total}/100")

    # -----------------------------------------------------
    # ABA 3: EDITAR / GERENCIAR ACOMPANHAMENTOS
    # -----------------------------------------------------
    elif opcao == "Editar / Gerenciar Acompanhamentos":
        st.title("✏️ Edição e Exclusão de Acompanhamentos")
        acompanhamentos = st.session_state.db["acompanhamentos"]

        if not acompanhamentos:
            st.info("Nenhum acompanhamento cadastrado para edições.")
            return

        lista_opcoes = [f"ID #{item['id']} - Área: {item['area']} - Data: {item['data']}" for item in acompanhamentos]
        selecionado = st.selectbox("Selecione o Acompanhamento para Modificar:", lista_opcoes)

        idx_selecionado = lista_opcoes.index(selecionado)
        acompanhamento_atual = acompanhamentos[idx_selecionado]

        st.markdown("---")
        st.subheader(f"Editando Registro ID #{acompanhamento_atual['id']}")

        with st.form("form_edicao"):
            area = st.selectbox(
                "Área:", 
                st.session_state.db["areas"], 
                index=st.session_state.db["areas"].index(acompanhamento_atual["area"]) if acompanhamento_atual["area"] in st.session_state.db["areas"] else 0
            )
            responsavel = st.text_input("Responsável:", value=acompanhamento_atual.get("responsavel", acompanhamento_atual.get("auditor", "")))
            
            seiri = st.slider("1. Seiri (Utilização)", 0, 20, int(acompanhamento_atual.get("seiri", 15)))
            seiton = st.slider("2. Seiton (Organização)", 0, 20, int(acompanhamento_atual.get("seiton", 15)))
            seiso = st.slider("3. Seiso (Limpeza)", 0, 20, int(acompanhamento_atual.get("seiso", 15)))
            seiketsu = st.slider("4. Seiketsu (Padronização)", 0, 20, int(acompanhamento_atual.get("seiketsu", 15)))
            shitsuke = st.slider("5. Shitsuke (Disciplina)", 0, 20, int(acompanhamento_atual.get("shitsuke", 15)))

            observacoes = st.text_area("Observações:", value=acompanhamento_atual.get("observacoes", ""))
            
            st.write("Foto atual:")
            if acompanhamento_atual.get("foto_url"):
                st.image(acompanhamento_atual["foto_url"], width=200)
            else:
                st.write("Sem foto cadastrada.")

            nova_foto = st.file_uploader("Substituir Foto (opcional):", type=["png", "jpg", "jpeg"])

            col_btn1, col_btn2 = st.columns(2)
            btn_salvar = col_btn1.form_submit_button("💾 Salvar Alterações")
            btn_excluir = col_btn2.form_submit_button("🚨 Excluir Acompanhamento")

        if btn_salvar:
            nova_url_foto = acompanhamento_atual.get("foto_url")
            if nova_foto is not None:
                with st.spinner("Atualizando foto no ImgBB..."):
                    nova_url_foto = enviar_foto_imgbb(nova_foto.getvalue(), nova_foto.name)

            pontuacao_total = seiri + seiton + seiso + seiketsu + shitsuke
            
            st.session_state.db["acompanhamentos"][idx_selecionado]["area"] = area
            st.session_state.db["acompanhamentos"][idx_selecionado]["responsavel"] = responsavel
            st.session_state.db["acompanhamentos"][idx_selecionado]["seiri"] = seiri
            st.session_state.db["acompanhamentos"][idx_selecionado]["seiton"] = seiton
            st.session_state.db["acompanhamentos"][idx_selecionado]["seiso"] = seiso
            st.session_state.db["acompanhamentos"][idx_selecionado]["seiketsu"] = seiketsu
            st.session_state.db["acompanhamentos"][idx_selecionado]["shitsuke"] = shitsuke
            st.session_state.db["acompanhamentos"][idx_selecionado]["pontuacao"] = pontuacao_total
            st.session_state.db["acompanhamentos"][idx_selecionado]["observacoes"] = observacoes
            st.session_state.db["acompanhamentos"][idx_selecionado]["foto_url"] = nova_url_foto

            salvar_dados(st.session_state.db)
            st.success("Acompanhamento atualizado com sucesso!")
            st.rerun()

        if btn_excluir:
            st.session_state.db["acompanhamentos"].pop(idx_selecionado)
            salvar_dados(st.session_state.db)
            st.warning("Acompanhamento excluído com sucesso!")
            st.rerun()

    # -----------------------------------------------------
    # ABA 4: RELATÓRIO FILTRADO & EXPORTAÇÃO PDF
    # -----------------------------------------------------
    elif opcao == "Relatório Filtrado & Exportação PDF":
        st.title("🔍 Relatórios Filtrados & Gerador PDF")
        acompanhamentos = st.session_state.db["acompanhamentos"]

        if not acompanhamentos:
            st.info("Nenhum acompanhamento disponível para filtrar.")
            return

        df = pd.DataFrame(acompanhamentos)
        df['data_dt'] = pd.to_datetime(df['data'])

        st.subheader("Filtros de Pesquisa")
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            areas_disponiveis = ["Todas"] + list(df["area"].unique())
            filtro_area = st.selectbox("Área:", areas_disponiveis)

        with col_f2:
            responsaveis_disponiveis = ["Todos"] + list(df["responsavel"].unique())
            filtro_responsavel = st.selectbox("Responsável:", responsaveis_disponiveis)

        with col_f3:
            data_inicio = st.date_input("Data Inicial:", value=date(2025, 1, 1))
            data_fim = st.date_input("Data Final:", value=date.today())

        df_filtrado = df.copy()

        if filtro_area != "Todas":
            df_filtrado = df_filtrado[df_filtrado["area"] == filtro_area]

        if filtro_responsavel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["responsavel"] == filtro_responsavel]

        df_filtrado = df_filtrado[
            (df_filtrado['data_dt'].dt.date >= data_inicio) & 
            (df_filtrado['data_dt'].dt.date <= data_fim)
        ]

        st.markdown("---")
        st.subheader(f"Resultados Encontrados ({len(df_filtrado)} registros)")

        if df_filtrado.empty:
            st.warning("Nenhum acompanhamento encontrado para os filtros selecionados.")
        else:
            m1, m2 = st.columns(2)
            m1.metric("Média das Notas Filtradas", f"{df_filtrado['pontuacao'].mean():.1f} / 100")
            m2.metric("Maior Pontuação do Período", f"{df_filtrado['pontuacao'].max()} / 100")

            st.dataframe(
                df_filtrado[["id", "data", "area", "responsavel", "pontuacao", "observacoes"]], 
                use_container_width=True
            )

            col_exp1, col_exp2 = st.columns(2)

            with col_exp1:
                pdf_bytes = gerar_pdf_html(df_filtrado, f"Relatório de Acompanhamentos ({filtro_area})")
                st.download_button(
                    label="📄 Baixar Relatório Completo em PDF",
                    data=pdf_bytes,
                    file_name=f"relatorio_5s_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf"
                )

            with col_exp2:
                csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar Dados em CSV",
                    data=csv_data,
                    file_name=f"dados_5s_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

    # -----------------------------------------------------
    # ABA 5: RELATÓRIO GERAL DO 5S (EXECUTIVO)
    # -----------------------------------------------------
    elif opcao == "Relatório Geral 5S (Executivo)":
        st.title("📊 Relatório Geral Consolidado do Programa 5S")
        acompanhamentos = st.session_state.db["acompanhamentos"]

        if not acompanhamentos:
            st.info("Sem dados suficientes para gerar o relatório geral executivo.")
            return

        df = pd.DataFrame(acompanhamentos)

        st.markdown("""
        Este painel consolidado apresenta o **desempenho global do programa 5S**, discriminado por cada um dos 
        cinco sensos, identificando áreas de destaque e oportunidades de melhoria operacional.
        """)

        med_seiri = df["seiri"].fillna(15).mean() if "seiri" in df.columns else 15
        med_seiton = df["seiton"].fillna(15).mean() if "seiton" in df.columns else 15
        med_seiso = df["seiso"].fillna(15).mean() if "seiso" in df.columns else 15
        med_seiketsu = df["seiketsu"].fillna(15).mean() if "seiketsu" in df.columns else 15
        med_shitsuke = df["shitsuke"].fillna(15).mean() if "shitsuke" in df.columns else 15

        st.subheader("1. Desempenho por Senso (Média de 0 a 20 pontos)")
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        col_s1.metric("1. Seiri (Utilização)", f"{med_seiri:.1f}")
        col_s2.metric("2. Seiton (Organização)", f"{med_seiton:.1f}")
        col_s3.metric("3. Seiso (Limpeza)", f"{med_seiso:.1f}")
        col_s4.metric("4. Seiketsu (Padronização)", f"{med_seiketsu:.1f}")
        col_s5.metric("5. Shitsuke (Disciplina)", f"{med_shitsuke:.1f}")

        df_sensos = pd.DataFrame({
            "Senso": ["Seiri (Utilização)", "Seiton (Organização)", "Seiso (Limpeza)", "Seiketsu (Padronização)", "Shitsuke (Disciplina)"],
            "Média Geral": [med_seiri, med_seiton, med_seiso, med_seiketsu, med_shitsuke]
        })
        st.bar_chart(df_sensos.set_index("Senso"))

        st.markdown("---")
        st.subheader("2. Ranking Geral das Áreas")
        ranking = df.groupby("area")["pontuacao"].agg(["count", "mean", "min", "max"]).reset_index()
        ranking.columns = ["Área", "Total Acompanhamentos", "Média Nota", "Menor Nota", "Maior Nota"]
        ranking = ranking.sort_values(by="Média Nota", ascending=False)
        st.dataframe(ranking, use_container_width=True)

        pdf_geral = gerar_pdf_html(df, "Relatório Geral Consolidado 5S")
        st.download_button(
            label="📄 Baixar Relatório Geral Executivo (PDF)",
            data=pdf_geral,
            file_name="relatorio_geral_executivo_5s.pdf",
            mime="application/pdf"
        )

    # -----------------------------------------------------
    # ABA 6: ENVIAR RELATÓRIO POR E-MAIL
    # -----------------------------------------------------
    elif opcao == "Enviar Relatório por E-mail":
        st.title("✉️ Envio Automático de Relatórios por E-mail")
        acompanhamentos = st.session_state.db["acompanhamentos"]

        if not acompanhamentos:
            st.info("Nenhum acompanhamento disponível para envio de relatório.")
            return

        df = pd.DataFrame(acompanhamentos)

        st.write("Envie o relatório em PDF atualizado diretamente para a diretoria, gerentes de área ou responsáveis.")

        with st.form("form_email"):
            email_destino = st.text_input("E-mail do Destinatário:", placeholder="gerente@empresa.com")
            assunto = st.text_input("Assunto do E-mail:", value="Relatório Consolidado de Acompanhamentos 5S")
            mensagem = st.text_area("Mensagem:", value="Olá,\n\nSegue em anexo o relatório atualizado dos acompanhamentos 5S com os resultados e links de fotos.\n\nAtenciosamente,\nEquipe de Qualidade e 5S")

            st.subheader("Configuração de Envio (SMTP)")
            st.caption("Insira os dados do seu servidor SMTP (Ex: Gmail, Outlook ou servidor próprio):")

            col_s1, col_s2 = st.columns(2)
            smtp_server = col_s1.text_input("Servidor SMTP:", value="smtp.gmail.com")
            smtp_port = col_s2.number_input("Porta SMTP:", value=587)

            col_s3, col_s4 = st.columns(2)
            smtp_user = col_s3.text_input("E-mail Remetente:", value="seu_email@gmail.com")
            smtp_pass = col_s4.text_input("Senha de Aplicativo SMTP:", type="password")

            btn_enviar = st.form_submit_button("🚀 Enviar Relatório com PDF Anexo")

        if btn_enviar:
            if not email_destino or not smtp_user or not smtp_pass:
                st.warning("Preencha todos os campos obrigatórios (Destinatário, E-mail Remetente e Senha).")
            else:
                with st.spinner("Gerando PDF e enviando e-mail..."):
                    pdf_bytes = gerar_pdf_html(df, "Relatório de Acompanhamentos 5S")
                    
                    config_smtp = {
                        "server": smtp_server,
                        "port": smtp_port,
                        "user": smtp_user,
                        "password": smtp_pass
                    }

                    sucesso, msg_resultado = enviar_relatorio_email(
                        destinatario=email_destino,
                        assunto=assunto,
                        mensagem_texto=mensagem,
                        pdf_bytes=pdf_bytes,
                        nome_arquivo_pdf=f"Relatorio_5S_{datetime.now().strftime('%Y%m%d')}.pdf",
                        smtp_config=config_smtp
                    )

                    if sucesso:
                        st.success(msg_resultado)
                    else:
                        st.error(msg_resultado)

    # -----------------------------------------------------
    # ABA 7: GESTÃO COMPLETA DE ÁREAS (EXPANDIDA)
    # -----------------------------------------------------
    elif opcao == "Gestão de Áreas":
        st.title("🏢 Gestão de Áreas")
        
        tab_add, tab_edit, tab_del = st.tabs(["➕ Cadastrar Área", "✏️ Editar Área", "🗑️ Excluir Área"])

        # TAB CADASTRAR
        with tab_add:
            st.subheader("Adicionar Nova Área")
            nova_area = st.text_input("Nome da Nova Área:", key="input_nova_area")
            if st.button("Cadastrar Área"):
                nova_area_clean = nova_area.strip()
                if nova_area_clean:
                    if nova_area_clean not in st.session_state.db["areas"]:
                        st.session_state.db["areas"].append(nova_area_clean)
                        salvar_dados(st.session_state.db)
                        st.success(f"Área '{nova_area_clean}' cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Esta área já está cadastrada.")
                else:
                    st.warning("O nome da área não pode ser vazio.")

        # TAB EDITAR
        with tab_edit:
            st.subheader("Editar Nome de uma Área")
            if not st.session_state.db["areas"]:
                st.info("Nenhuma área disponível para edição.")
            else:
                area_selecionada = st.selectbox("Selecione a área para alterar:", st.session_state.db["areas"], key="select_edit_area")
                novo_nome_area = st.text_input("Novo Nome da Área:", value=area_selecionada, key="input_edit_area")
                
                if st.button("Salvar Alteração da Área"):
                    novo_nome_clean = novo_nome_area.strip()
                    if novo_nome_clean:
                        idx = st.session_state.db["areas"].index(area_selecionada)
                        st.session_state.db["areas"][idx] = novo_nome_clean
                        
                        # Atualiza histórico de acompanhamentos com o novo nome da área
                        for ac in st.session_state.db["acompanhamentos"]:
                            if ac.get("area") == area_selecionada:
                                ac["area"] = novo_nome_clean

                        salvar_dados(st.session_state.db)
                        st.success(f"Área atualizada para '{novo_nome_clean}'!")
                        st.rerun()
                    else:
                        st.warning("O novo nome da área não pode ser vazio.")

        # TAB EXCLUIR
        with tab_del:
            st.subheader("Remover uma Área")
            if not st.session_state.db["areas"]:
                st.info("Nenhuma área cadastrada.")
            else:
                area_para_remover = st.selectbox("Selecione a área para excluir:", st.session_state.db["areas"], key="select_del_area")
                st.caption("⚠️ Nota: Excluir uma área não apaga os acompanhamentos antigos salvos com ela.")
                
                if st.button("Remover Área", type="primary"):
                    st.session_state.db["areas"].remove(area_para_remover)
                    salvar_dados(st.session_state.db)
                    st.warning(f"Área '{area_para_remover}' removida com sucesso!")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Lista de Áreas Cadastradas Atualmente")
        if st.session_state.db["areas"]:
            df_areas = pd.DataFrame({"Áreas Cadastradas": st.session_state.db["areas"]})
            st.table(df_areas)
        else:
            st.info("Nenhuma área cadastrada no sistema.")

    # -----------------------------------------------------
    # ABA 8: CHAT COM ASSISTENTE IA 5S
    # -----------------------------------------------------
    elif opcao == "Assistente IA 5S":
        st.title("🤖 Assistente Virtual 5S")
        st.write("Tire dúvidas sobre padronização, acompanhamentos e melhorias do programa 5S.")

        if "mensagens_chat" not in st.session_state:
            st.session_state.mensagens_chat = [
                {"role": "assistant", "content": "Olá! Como posso ajudar na implementação e acompanhamento do 5S na sua empresa hoje?"}
            ]

        for msg in st.session_state.mensagens_chat:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Digite sua dúvida..."):
            st.session_state.mensagens_chat.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

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
