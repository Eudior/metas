import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- Configuração da Página (DEVE SER O PRIMEIRO COMANDO STREAMLIT) ---
st.set_page_config(page_title="Painel de Metas de Vendas", layout="wide")

# --- CSS Personalizado para Melhorias Visuais (Cards COMPACTOS e Barras Grossas) --- 
st.markdown("""
<style>
    /* Estilo base para os cards COMPACTOS */
    .card {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 15px; /* Reduzido */
        border-radius: 10px; /* Levemente reduzido */
        margin-bottom: 15px; /* Reduzido */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); /* Sombra mais sutil */
        transition: box-shadow 0.3s ease-in-out;
    }
    .card:hover {
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.12);
    }

    /* Títulos dentro dos cards COMPACTOS */
    .card h2 {
        border-bottom: 2px solid #4CAF50; /* Linha mais fina */
        color: #333;
        padding-bottom: 5px; /* Reduzido */
        margin-top: 0;
        margin-bottom: 15px; /* Reduzido */
        font-size: 1.4rem; /* Reduzido */
    }

    /* Barra de progresso principal (Meta Mensal) - Grossa mas ajustada */
    .card:has(h2:contains("Meta Mensal")) .stProgress > div > div > div > div {
        height: 30px; /* Ajustado */
        border-radius: 15px;
    }
    /* Barras de progresso menores (Semanais) - Grossa mas ajustada */
    .card:not(:has(h2:contains("Meta Mensal"))) .stProgress > div > div > div > div {
         height: 25px; /* Ajustado */
         border-radius: 12px;
    }

    /* Estilo para métricas dentro dos cards COMPACTOS */
    .card div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: none;
        padding: 8px; /* Reduzido */
        border-radius: 6px; /* Reduzido */
        margin-bottom: 3px; /* Reduzido */
        box-shadow: none;
    }
    .card div[data-testid="metric-container"] label {
        font-weight: bold;
        font-size: 0.9rem; /* Reduzido */
    }
     .card div[data-testid="metric-container"] div {
        font-size: 1.1rem; /* Reduzido valor da métrica */
    }

    /* Título principal da página */
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 25px; /* Reduzido */
        font-size: 2rem; /* Reduzido */
    }
    /* Subtítulo (Vendedora) */
    h3 {
        color: #555;
        text-align: center;
        margin-bottom: 25px; /* Reduzido */
        font-size: 1.2rem; /* Reduzido */
    }
    /* Remove divisores padrão */
    hr {
        display: none;
    }
    /* Reduzir espaço extra de containers/blocos */
    .stVerticalBlock, .stHorizontalBlock {
        gap: 0.5rem; /* Tenta reduzir o gap entre elementos */
    }
    /* Reduzir espaço de st.write("") */
    div[data-testid="stText"] p {
        margin-bottom: 0.1rem; /* Tenta reduzir margem de parágrafos vazios */
        line-height: 0.5; /* Tenta reduzir altura da linha */
    }
    /* Estilo para texto de semana/bonificação no card semanal */
    .card p {
         margin-bottom: 0.5rem; /* Reduz espaço abaixo dos parágrafos */
         font-size: 0.95rem;
    }
    .card .stMarkdown p {
         margin-bottom: 0.5rem; /* Reduz espaço abaixo dos parágrafos em markdown */
         font-size: 0.95rem;
    }
    .card .stMarkdown hr {
        display: block; /* Reabilita hr dentro do card semanal */
        margin-top: 10px !important; /* Reduzido */
        margin-bottom: 10px !important; /* Reduzido */
        border-top: 1px solid #eee !important;
    }

</style>
""", unsafe_allow_html=True)

# --- Título Principal ---
st.title("📊 Painel de Metas de Vendas")

# --- Constantes e Configurações ---
GOOGLE_SHEET_URL_PROVIDED = "https://docs.google.com/spreadsheets/d/1bnqOqnJ3C9SXpJZ6txLtOu-pI7NYb6Yy/"
try:
    sheet_id = GOOGLE_SHEET_URL_PROVIDED.split("/d/")[1].split("/")[0]
except IndexError:
    st.error("Não foi possível extrair o ID da planilha da URL fornecida.")
    st.stop()

BASE_CSV_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="
DEFAULT_VENDEDOR = "Sarah"

# --- Carregamento de Dados via URL CSV (CACHE REMOVIDO) --- 
def load_data_from_csv(sheet_name):
    """Carrega dados de uma aba específica da planilha Google via URL CSV."""
    try:
        csv_url = BASE_CSV_URL + urllib.parse.quote(sheet_name)
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da aba {sheet_name} via URL CSV: {e}. Verifique se a planilha está compartilhada como \"Qualquer pessoa com o link pode visualizar\" e se o nome da aba está correto.")
        return pd.DataFrame()

metas_df_raw = load_data_from_csv("Metas")
vendas_df_raw = load_data_from_csv("Vendas")

# --- Pré-processamento e Lógica Principal --- 
if not metas_df_raw.empty and not vendas_df_raw.empty:
    metas_df = metas_df_raw.copy()
    vendas_df = vendas_df_raw.copy()
    try:
        # --- Pré-processamento --- 
        metas_df.columns = [col.strip() for col in metas_df.columns]
        vendas_df.columns = [col.strip() for col in vendas_df.columns]
        
        required_metas_cols = {"Ano", "Mês", "Vendedor", "Meta_Mensal", "Bonus_Mensal", "Semana", "Inicio_Semana", "Fim_Semana", "Meta_Semanal", "Bonus_Semanal"}
        required_vendas_cols = {"Data", "Vendedor", "Valor"}
        
        if not required_metas_cols.issubset(metas_df.columns):
            st.error(f"Colunas faltando na aba \"Metas\". Necessário: {required_metas_cols}. Encontrado: {set(metas_df.columns)}")
            st.stop()
        if not required_vendas_cols.issubset(vendas_df.columns):
            st.error(f"Colunas faltando na aba \"Vendas\". Necessário: {required_vendas_cols}. Encontrado: {set(vendas_df.columns)}")
            st.stop()

        # Conversões de tipo (CORREÇÃO DEFINITIVA - errors='coerce')
        metas_df["Inicio_Semana"] = pd.to_datetime(metas_df["Inicio_Semana"], dayfirst=True, errors='coerce')
        metas_df["Fim_Semana"] = pd.to_datetime(metas_df["Fim_Semana"], dayfirst=True, errors='coerce')
        vendas_df["Data"] = pd.to_datetime(vendas_df["Data"], dayfirst=True, errors='coerce')
        
        metas_df.dropna(subset=["Inicio_Semana", "Fim_Semana"], inplace=True)
        vendas_df.dropna(subset=["Data"], inplace=True)

        cols_numericas_metas = ["Meta_Mensal", "Bonus_Mensal", "Meta_Semanal", "Bonus_Semanal"]
        for col in cols_numericas_metas:
            if metas_df[col].dtype == "object":
                 metas_df[col] = metas_df[col].astype(str).str.replace(",", ".", regex=False)
            metas_df[col] = pd.to_numeric(metas_df[col], errors='coerce').fillna(0)
            
        cols_numericas_vendas = ["Valor"]
        for col in cols_numericas_vendas:
             if vendas_df[col].dtype == "object":
                 vendas_df[col] = vendas_df[col].astype(str).str.replace(",", ".", regex=False)
             vendas_df[col] = pd.to_numeric(vendas_df[col], errors='coerce').fillna(0)

        metas_df["Ano"] = pd.to_numeric(metas_df["Ano"], errors='coerce').fillna(0).astype(int)
        metas_df["Mês"] = pd.to_numeric(metas_df["Mês"], errors='coerce').fillna(0).astype(int)
        metas_df["Semana"] = pd.to_numeric(metas_df["Semana"], errors='coerce').fillna(0).astype(int)

    except Exception as e:
        st.error(f"Erro durante o pré-processamento dos dados: {e}")
        st.stop()

    # --- Lógica Principal --- 
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year

    st.subheader(f"Vendedora: {DEFAULT_VENDEDOR} — {hoje.strftime('%B de %Y')}") # Corrigido strftime

    metas_mes_atual = metas_df[
        (metas_df["Ano"] == ano_atual) &
        (metas_df["Mês"] == mes_atual) &
        (metas_df["Vendedor"] == DEFAULT_VENDEDOR)
    ].copy()
    
    vendas_mes_atual = vendas_df[
        (vendas_df["Data"].dt.year == ano_atual) &
        (vendas_df["Data"].dt.month == mes_atual) &
        (vendas_df["Vendedor"] == DEFAULT_VENDEDOR)
    ].copy()

    if metas_mes_atual.empty:
        st.warning(f"Nenhuma meta encontrada para {DEFAULT_VENDEDOR} em {mes_atual}/{ano_atual}.")
    else:
        # --- Layout Principal em Colunas (Meta Mensal | Semana Atual) ---
        col_main1, col_main2 = st.columns(2)

        with col_main1:
            # --- Card: Meta Mensal ---
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("## 🎯 Meta Mensal")
                meta_mensal_valor = metas_mes_atual["Meta_Mensal"].iloc[0]
                bonus_mensal_valor = metas_mes_atual["Bonus_Mensal"].iloc[0]
                total_vendido_mes = vendas_mes_atual["Valor"].sum()
                progresso_mensal = (total_vendido_mes / meta_mensal_valor) * 100 if meta_mensal_valor > 0 else 0
                bonus_mensal_atingido = total_vendido_mes >= meta_mensal_valor

                # Colunas internas para métricas e barra
                col1_int, col2_int = st.columns([3, 2]) # Ajuste proporção se necessário
                with col1_int:
                    st.metric("Total vendido", f"R$ {total_vendido_mes:,.2f}".replace(",", "."))
                    st.metric("Meta", f"R$ {meta_mensal_valor:,.2f}".replace(",", "."))
                    bonus_txt = f"✅ R$ {bonus_mensal_valor:,.2f}".replace(",", ".") if bonus_mensal_atingido else f"❌ R$ {bonus_mensal_valor:,.2f}".replace(",", ".")
                    st.metric("Bonificação", bonus_txt)
                with col2_int:
                    st.metric("Progresso", f"{progresso_mensal:.1f}%")
                    st.progress(min(progresso_mensal / 100, 1.0))
                st.markdown("</div>", unsafe_allow_html=True)

        with col_main2:
            # --- Card: Semana Atual ---
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("## 🟢 Semana Atual")
                semana_atual_df = metas_mes_atual[
                    (metas_mes_atual["Inicio_Semana"] <= hoje) &
                    (metas_mes_atual["Fim_Semana"] + pd.Timedelta(days=1) > hoje)
                ]

                if not semana_atual_df.empty:
                    semana_atual_info = semana_atual_df.iloc[0]
                    inicio_sem = semana_atual_info["Inicio_Semana"].strftime("%d/%m")
                    fim_sem = semana_atual_info["Fim_Semana"].strftime("%d/%m")
                    meta_sem_valor = semana_atual_info["Meta_Semanal"]
                    bonus_sem_valor = semana_atual_info["Bonus_Semanal"]
                    num_semana = semana_atual_info["Semana"]

                    vendas_semana_atual = vendas_mes_atual[
                        (vendas_mes_atual["Data"] >= semana_atual_info["Inicio_Semana"]) &
                        (vendas_mes_atual["Data"] <= semana_atual_info["Fim_Semana"])
                    ]
                    total_vendido_sem = vendas_semana_atual["Valor"].sum()
                    progresso_sem = (total_vendido_sem / meta_sem_valor) * 100 if meta_sem_valor > 0 else 0
                    bonus_sem_atingido = total_vendido_sem >= meta_sem_valor

                    st.write(f"**Semana {num_semana} ({inicio_sem} a {fim_sem})**")
                    # Colunas internas
                    col1_sem_int, col2_sem_int = st.columns([3, 2])
                    with col1_sem_int:
                        st.metric("Vendido na Semana", f"R$ {total_vendido_sem:,.2f}".replace(",", "."))
                        st.metric("Meta Semanal", f"R$ {meta_sem_valor:,.2f}".replace(",", "."))
                        bonus_sem_txt = f"✅ R$ {bonus_sem_valor:,.2f}".replace(",", ".") if bonus_sem_atingido else f"❌ R$ {bonus_sem_valor:,.2f}".replace(",", ".")
                        st.metric("Bonificação Semanal", bonus_sem_txt)
                    with col2_sem_int:
                        st.metric("Progresso", f"{progresso_sem:.1f}%")
                        st.progress(min(progresso_sem / 100, 1.0))
                else:
                    st.info("Não há informações de meta para a semana atual.")
                st.markdown("</div>", unsafe_allow_html=True)

        # --- Card: Todas as Metas Semanais (Abaixo das colunas principais) ---
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"## 🗓️ Todas as Metas Semanais de {hoje.strftime('%B')}") # Corrigido strftime
            total_bonus_semanal_ganho = 0

            # Usar colunas para organizar as semanas lado a lado (ex: 3 ou 4 colunas para mais compactação)
            num_cols_semanais = 3 # Ajuste conforme necessário (2, 3 ou 4)
            cols_semanas = st.columns(num_cols_semanais)
            col_idx = 0

            for index, semana_info in metas_mes_atual.sort_values(by="Semana").iterrows():
                with cols_semanas[col_idx % num_cols_semanais]: # Alterna entre as colunas
                    with st.container(): # Container para cada semana dentro da coluna
                        inicio_sem = semana_info["Inicio_Semana"].strftime("%d/%m")
                        fim_sem = semana_info["Fim_Semana"].strftime("%d/%m")
                        meta_sem_valor = semana_info["Meta_Semanal"]
                        bonus_sem_valor = semana_info["Bonus_Semanal"]
                        num_semana = semana_info["Semana"]

                        vendas_na_semana = vendas_mes_atual[
                            (vendas_mes_atual["Data"] >= semana_info["Inicio_Semana"]) &
                            (vendas_mes_atual["Data"] <= semana_info["Fim_Semana"])
                        ]
                        total_vendido_sem = vendas_na_semana["Valor"].sum()
                        progresso_sem = (total_vendido_sem / meta_sem_valor) * 100 if meta_sem_valor > 0 else 0
                        bonus_sem_atingido = total_vendido_sem >= meta_sem_valor
                        if bonus_sem_atingido:
                            total_bonus_semanal_ganho += bonus_sem_valor

                        st.write(f"**Sem {num_semana} ({inicio_sem}-{fim_sem})**") # Mais compacto
                        st.metric("Progresso", f"R$ {total_vendido_sem:,.2f} / R$ {meta_sem_valor:,.2f}".replace(",", "."), f"{progresso_sem:.1f}%", delta_color="off")
                        bonus_sem_txt = f"✅ R$ {bonus_sem_valor:,.2f}".replace(",", ".") if bonus_sem_atingido else f"❌ R$ {bonus_sem_valor:,.2f}".replace(",", ".")
                        st.write(f"Bônus: {bonus_sem_txt}") # Mais compacto
                        st.progress(min(progresso_sem / 100, 1.0))
                        # Remover o <hr> para mais compactação
                        # st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
                col_idx += 1
            st.markdown("</div>", unsafe_allow_html=True)

        # --- Card: Resumo Bonificações (Abaixo) ---
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("## 💰 Resumo Bonificações do Mês")
            bonus_mensal_ganho = bonus_mensal_valor if bonus_mensal_atingido else 0
            total_bonus = total_bonus_semanal_ganho + bonus_mensal_ganho

            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.metric("Total Bônus Semanais", f"R$ {total_bonus_semanal_ganho:,.2f}".replace(",", "."))
            with col_res2:
                st.metric("Bônus Mensal", f"R$ {bonus_mensal_ganho:,.2f}".replace(",", "."))
            with col_res3:
                st.metric("**TOTAL BÔNUS**", f"**R$ {total_bonus:,.2f}**".replace(",", "."))
            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.error("Não foi possível carregar os dados de uma ou ambas as abas da planilha (Metas, Vendas). Verifique as mensagens de erro acima, o compartilhamento da planilha e os nomes das abas.")

# --- Rodapé ---
st.caption("Desenvolvido por Manus (vFinal Cards Compactos - CORRIGIDO)")



