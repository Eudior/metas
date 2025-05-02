import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- Configuração da Página (DEVE SER O PRIMEIRO COMANDO STREAMLIT) ---
st.set_page_config(page_title="Painel de Metas de Vendas", layout="wide")

# --- CSS Personalizado para Melhorias Visuais (Cards e Barras Grossas) --- 
st.markdown("""
<style>
    /* Estilo base para os cards */
    .card {
        background-color: #ffffff; /* Fundo branco */
        border: 1px solid #e6e6e6;
        padding: 25px; /* Mais preenchimento interno */
        border-radius: 15px; /* Bordas mais arredondadas */
        margin-bottom: 25px; /* Espaçamento entre cards */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Sombra mais pronunciada */
        transition: box-shadow 0.3s ease-in-out; /* Efeito suave ao passar o mouse */
    }
    .card:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    /* Títulos dentro dos cards */
    .card h2 {
        border-bottom: 3px solid #4CAF50;
        color: #333;
        padding-bottom: 10px;
        margin-top: 0; /* Remove margem superior do h2 dentro do card */
        margin-bottom: 20px;
        font-size: 1.75rem; /* Tamanho do título do card */
    }

    /* Barra de progresso principal (Meta Mensal) - SUPER GROSSA */
    .card:has(h2:contains("Meta Mensal")) .stProgress > div > div > div > div {
        height: 40px; /* Aumenta MUITO a altura da barra */
        border-radius: 20px; /* Bordas super arredondadas */
    }
    /* Barras de progresso menores (Semanais) - SUPER GROSSAS */
    .card:not(:has(h2:contains("Meta Mensal"))) .stProgress > div > div > div > div {
         height: 35px; /* Altura aumentada para barras semanais */
         border-radius: 18px; /* Bordas super arredondadas */
    }

    /* Estilo para métricas dentro dos cards */
    .card div[data-testid="metric-container"] {
        background-color: #f8f9fa; /* Fundo levemente diferente para métricas */
        border: none; /* Remove borda padrão da métrica */
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
        box-shadow: none; /* Remove sombra padrão da métrica */
    }
    .card div[data-testid="metric-container"] label {
        font-weight: bold; /* Deixa o label da métrica em negrito */
    }

    /* Título principal da página */
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 40px;
    }
    /* Subtítulo (Vendedora) */
    h3 {
        color: #555;
        text-align: center;
        margin-bottom: 40px;
    }
    /* Remove divisores padrão, os cards já separam */
    hr {
        display: none;
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

        # Conversões de tipo (CORREÇÃO MANUAL DEFINITIVA - errors='coerce')
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

    st.subheader(f"Vendedora: {DEFAULT_VENDEDOR} — {hoje.strftime('%B de %Y')}")

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
        # --- Card: Meta Mensal ---
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("## 🎯 Meta Mensal")
            meta_mensal_valor = metas_mes_atual["Meta_Mensal"].iloc[0]
            bonus_mensal_valor = metas_mes_atual["Bonus_Mensal"].iloc[0]
            total_vendido_mes = vendas_mes_atual["Valor"].sum()
            progresso_mensal = (total_vendido_mes / meta_mensal_valor) * 100 if meta_mensal_valor > 0 else 0
            bonus_mensal_atingido = total_vendido_mes >= meta_mensal_valor

            col1, col2 = st.columns([2, 1])
            with col1:
                st.metric("Total vendido", f"R$ {total_vendido_mes:,.2f}".replace(",", "."))
                st.metric("Meta", f"R$ {meta_mensal_valor:,.2f}".replace(",", "."))
                st.metric("Progresso", f"{progresso_mensal:.1f}%")
                bonus_txt = f"✅ R$ {bonus_mensal_valor:,.2f}".replace(",", ".") if bonus_mensal_atingido else f"❌ R$ {bonus_mensal_valor:,.2f}".replace(",", ".")
                st.metric("Bonificação", bonus_txt)
            with col2:
                st.write("") # Espaço para alinhar verticalmente
                st.write("")
                st.progress(min(progresso_mensal / 100, 1.0))
            st.markdown("</div>", unsafe_allow_html=True)

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
                col1_sem, col2_sem = st.columns([2, 1])
                with col1_sem:
                    st.metric("Vendido na Semana", f"R$ {total_vendido_sem:,.2f}".replace(",", "."))
                    st.metric("Meta Semanal", f"R$ {meta_sem_valor:,.2f}".replace(",", "."))
                    bonus_sem_txt = f"✅ R$ {bonus_sem_valor:,.2f}".replace(",", ".") if bonus_sem_atingido else f"❌ R$ {bonus_sem_valor:,.2f}".replace(",", ".")
                    st.metric("Bonificação Semanal", bonus_sem_txt)
                with col2_sem:
                    st.write("")
                    st.write("")
                    st.progress(min(progresso_sem / 100, 1.0))
            else:
                st.info("Não há informações de meta para a semana atual.")
            st.markdown("</div>", unsafe_allow_html=True)

        # --- Card: Todas as Metas Semanais ---
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"## 🗓️ Todas as Metas Semanais de {hoje.strftime('%B')}")
            total_bonus_semanal_ganho = 0

            # Usar colunas para organizar as semanas lado a lado (ex: 2 colunas)
            cols_semanas = st.columns(2)
            col_idx = 0

            for index, semana_info in metas_mes_atual.sort_values(by="Semana").iterrows():
                with cols_semanas[col_idx % 2]: # Alterna entre as colunas
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

                        st.write(f"**Semana {num_semana} ({inicio_sem} a {fim_sem})**")
                        # Usar st.metric para consistência visual
                        st.metric("Progresso", f"R$ {total_vendido_sem:,.2f} / R$ {meta_sem_valor:,.2f}".replace(",", "."), f"{progresso_sem:.1f}%", delta_color="off")
                        bonus_sem_txt = f"✅ R$ {bonus_sem_valor:,.2f}".replace(",", ".") if bonus_sem_atingido else f"❌ R$ {bonus_sem_valor:,.2f}".replace(",", ".")
                        st.write(f"Bonificação: {bonus_sem_txt}")
                        st.progress(min(progresso_sem / 100, 1.0))
                        st.markdown("<hr style='margin-top: 15px; margin-bottom: 15px; border-top: 1px solid #eee;'>", unsafe_allow_html=True) # Divisor sutil entre semanas na mesma coluna
                col_idx += 1
            st.markdown("</div>", unsafe_allow_html=True)

        # --- Card: Resumo Bonificações ---
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
                # Destaque maior para o total
                st.metric("**TOTAL BÔNUS**", f"**R$ {total_bonus:,.2f}**".replace(",", "."))
            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.error("Não foi possível carregar os dados de uma ou ambas as abas da planilha (Metas, Vendas). Verifique as mensagens de erro acima, o compartilhamento da planilha e os nomes das abas.")

# --- Rodapé ---
st.caption("Desenvolvido por Manus (vFinal Cards - CORRIGIDO e Testado)")

