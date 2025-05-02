import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- Configuração da Página (DEVE SER O PRIMEIRO COMANDO STREAMLIT) ---
st.set_page_config(page_title="Painel de Metas de Vendas", layout="wide")

# --- CSS Personalizado (Cartões Flutuantes Quadrados) --- 
st.markdown("""
<style>
    /* Estilo base para os cartões FLUTUANTES */
    .card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0; /* Borda mais suave */
        padding: 20px; /* Um pouco mais de padding */
        border-radius: 8px; /* Menos arredondado, mais quadrado */
        margin-bottom: 20px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); /* Sombra mais pronunciada para flutuar */
        transition: box-shadow 0.3s ease-in-out, transform 0.3s ease-in-out;
        height: 100%; /* Tenta fazer os cards na mesma linha terem a mesma altura */
        display: flex; /* Usar flexbox para alinhar conteúdo interno */
        flex-direction: column; /* Empilhar conteúdo verticalmente */
    }
    .card:hover {
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        transform: translateY(-3px); /* Leve elevação no hover */
    }

    /* Títulos dentro dos cartões */
    .card h2 {
        border-bottom: 2px solid #4CAF50;
        color: #333;
        padding-bottom: 8px;
        margin-top: 0;
        margin-bottom: 18px;
        font-size: 1.5rem;
    }

    /* Barras de progresso - Mantendo grossas */
    .stProgress > div > div > div > div {
        height: 28px;
        border-radius: 14px;
    }

    /* Estilo para métricas */
    .card div[data-testid="metric-container"] {
        background-color: #f9f9f9;
        border: none;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 5px;
        box-shadow: none;
    }
    .card div[data-testid="metric-container"] label {
        font-weight: bold;
        font-size: 0.95rem;
    }
     .card div[data-testid="metric-container"] div {
        font-size: 1.15rem;
    }

    /* Título principal e subtítulo */
    h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; font-size: 2.2rem; }
    h3 { color: #555; text-align: center; margin-bottom: 30px; font-size: 1.3rem; }
    hr { display: none; }
    .stVerticalBlock, .stHorizontalBlock { gap: 1rem; } /* Ajustar gap entre colunas/elementos */

    /* Conteúdo do card semanal */
    .card p { margin-bottom: 0.6rem; font-size: 1rem; }
    .card .stMarkdown p { margin-bottom: 0.6rem; font-size: 1rem; }
    .card .stMarkdown hr { display: none; } /* Remover hr interno */

    /* Forçar altura igual para colunas principais */
    div[data-testid="stHorizontalBlock"] > div[data-testid^="stVerticalBlock"] {
        height: 100%;
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
        # Garante que colunas de data sejam lidas como string inicialmente
        date_cols = [col for col in df.columns if "Data" in col or "Semana" in col]
        df = pd.read_csv(csv_url, dtype={col: str for col in date_cols})
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

        # Conversões de tipo (CORREÇÃO DEFINITIVA - errors=\'coerce\')
        # Tentar formatos diferentes se o padrão falhar
        date_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"] # Adicione outros formatos se necessário
        for fmt in date_formats:
            try:
                metas_df["Inicio_Semana"] = pd.to_datetime(metas_df["Inicio_Semana"], format=fmt, errors=\'raise\')
                metas_df["Fim_Semana"] = pd.to_datetime(metas_df["Fim_Semana"], format=fmt, errors=\'raise\')
                vendas_df["Data"] = pd.to_datetime(vendas_df["Data"], format=fmt, errors=\'raise\')
                break # Sai do loop se a conversão for bem-sucedida
            except (ValueError, TypeError):
                continue # Tenta o próximo formato
        else: # Executa se o loop terminar sem break
             # Se nenhum formato funcionou, tenta com dayfirst=True e coerce
             metas_df["Inicio_Semana"] = pd.to_datetime(metas_df["Inicio_Semana"], dayfirst=True, errors=\'coerce\')
             metas_df["Fim_Semana"] = pd.to_datetime(metas_df["Fim_Semana"], dayfirst=True, errors=\'coerce\')
             vendas_df["Data"] = pd.to_datetime(vendas_df["Data"], dayfirst=True, errors=\'coerce\')

        metas_df.dropna(subset=["Inicio_Semana", "Fim_Semana"], inplace=True)
        vendas_df.dropna(subset=["Data"], inplace=True)

        cols_numericas_metas = ["Meta_Mensal", "Bonus_Mensal", "Meta_Semanal", "Bonus_Semanal"]
        for col in cols_numericas_metas:
            if metas_df[col].dtype == "object":
                 metas_df[col] = metas_df[col].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).str.strip()
            metas_df[col] = pd.to_numeric(metas_df[col], errors=\'coerce\').fillna(0)
            
        cols_numericas_vendas = ["Valor"]
        for col in cols_numericas_vendas:
             if vendas_df[col].dtype == "object":
                 vendas_df[col] = vendas_df[col].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).str.strip()
             vendas_df[col] = pd.to_numeric(vendas_df[col], errors=\'coerce\').fillna(0)

        metas_df["Ano"] = pd.to_numeric(metas_df["Ano"], errors=\'coerce\').fillna(0).astype(int)
        metas_df["Mês"] = pd.to_numeric(metas_df["Mês"], errors=\'coerce\').fillna(0).astype(int)
        metas_df["Semana"] = pd.to_numeric(metas_df["Semana"], errors=\'coerce\').fillna(0).astype(int)

    except Exception as e:
        st.error(f"Erro durante o pré-processamento dos dados: {e}")
        st.exception(e) # Mostra traceback completo para depuração
        st.stop()

    # --- Lógica Principal --- 
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year

    st.subheader(f"Vendedora: {DEFAULT_VENDEDOR} — {hoje.strftime(\'%B de %Y\')}")

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
        # --- Layout Principal em Colunas (3 Colunas: Mensal | Atual | Bônus) ---
        col_main1, col_main2, col_main3 = st.columns(3)

        # --- Cálculo dos dados (fora dos cards para reutilização) ---
        meta_mensal_valor = metas_mes_atual["Meta_Mensal"].iloc[0]
        bonus_mensal_valor = metas_mes_atual["Bonus_Mensal"].iloc[0]
        total_vendido_mes = vendas_mes_atual["Valor"].sum()
        progresso_mensal = (total_vendido_mes / meta_mensal_valor) * 100 if meta_mensal_valor > 0 else 0
        bonus_mensal_atingido = total_vendido_mes >= meta_mensal_valor
        bonus_mensal_ganho = bonus_mensal_valor if bonus_mensal_atingido else 0

        semana_atual_df = metas_mes_atual[
            (metas_mes_atual["Inicio_Semana"] <= hoje) &
            (metas_mes_atual["Fim_Semana"] + pd.Timedelta(days=1) > hoje)
        ]
        
        total_bonus_semanal_ganho = 0
        for index, semana_info_calc in metas_mes_atual.iterrows():
            vendas_na_semana_calc = vendas_mes_atual[
                (vendas_mes_atual["Data"] >= semana_info_calc["Inicio_Semana"]) &
                (vendas_mes_atual["Data"] <= semana_info_calc["Fim_Semana"])
            ]
            total_vendido_sem_calc = vendas_na_semana_calc["Valor"].sum()
            meta_sem_valor_calc = semana_info_calc["Meta_Semanal"]
            bonus_sem_valor_calc = semana_info_calc["Bonus_Semanal"]
            if meta_sem_valor_calc > 0 and total_vendido_sem_calc >= meta_sem_valor_calc:
                total_bonus_semanal_ganho += bonus_sem_valor_calc
        
        total_bonus = total_bonus_semanal_ganho + bonus_mensal_ganho

        # --- Coluna 1: Meta Mensal ---
        with col_main1:
            with st.container():
                st.markdown("<div class=\'card\'>", unsafe_allow_html=True)
                st.markdown("## 🎯 Meta Mensal")
                st.metric("Total vendido", f"R$ {total_vendido_mes:,.2f}".replace(",", "."))
                st.metric("Meta", f"R$ {meta_mensal_valor:,.2f}".replace(",", "."))
                st.metric("Progresso", f"{progresso_mensal:.1f}%")
                st.progress(min(progresso_mensal / 100, 1.0))
                bonus_txt = f"✅ R$ {bonus_mensal_valor:,.2f}".replace(",", ".") if bonus_mensal_atingido else f"❌ R$ {bonus_mensal_valor:,.2f}".replace(",", ".")
                st.metric("Bonificação Mensal", bonus_txt)
                st.markdown("</div>", unsafe_allow_html=True)

        # --- Coluna 2: Semana Atual ---
        with col_main2:
            with st.container():
                st.markdown("<div class=\'card\'>", unsafe_allow_html=True)
                st.markdown("## 🟢 Semana Atual")
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
                    st.metric("Vendido na Semana", f"R$ {total_vendido_sem:,.2f}".replace(",", "."))
                    st.metric("Meta Semanal", f"R$ {meta_sem_valor:,.2f}".replace(",", "."))
                    st.metric("Progresso", f"{progresso_sem:.1f}%")
                    st.progress(min(progresso_sem / 100, 1.0))
                    bonus_sem_txt = f"✅ R$ {bonus_sem_valor:,.2f}".replace(",", ".") if bonus_sem_atingido else f"❌ R$ {bonus_sem_valor:,.2f}".replace(",", ".")
                    st.metric("Bonificação Semanal", bonus_sem_txt)
                else:
                    st.info("Não há informações de meta para a semana atual.")
                st.markdown("</div>", unsafe_allow_html=True)

        # --- Coluna 3: Resumo Bonificações ---
        with col_main3:
             with st.container():
                st.markdown("<div class=\'card\'>", unsafe_allow_html=True)
                st.markdown("## 💰 Resumo Bônus")
                st.metric("Total Bônus Semanais", f"R$ {total_bonus_semanal_ganho:,.2f}".replace(",", "."))
                st.metric("Bônus Mensal", f"R$ {bonus_mensal_ganho:,.2f}".replace(",", "."))
                st.metric("**TOTAL BÔNUS MÊS**", f"**R$ {total_bonus:,.2f}**".replace(",", "."))
                # Adicionar um elemento visual ou espaço se necessário para altura
                st.write(" ") 
                st.write(" ")
                st.markdown("</div>", unsafe_allow_html=True)

        # --- Card: Todas as Metas Semanais (Abaixo das colunas principais) ---
        with st.container():
            st.markdown("<div class=\'card\'>", unsafe_allow_html=True)
            st.markdown(f"## 🗓️ Detalhe Semanal - {hoje.strftime(\'%B\')}")
            
            # Usar colunas para organizar as semanas lado a lado (4 colunas)
            num_cols_semanais = 4 # Mais colunas para visualização lado a lado
            cols_semanas = st.columns(num_cols_semanais)
            col_idx = 0

            for index, semana_info in metas_mes_atual.sort_values(by="Semana").iterrows():
                with cols_semanas[col_idx % num_cols_semanais]: # Alterna entre as colunas
                    # Mini-card interno para cada semana
                    st.markdown("<div style=\"border: 1px solid #eee; padding: 10px; border-radius: 5px; margin-bottom: 10px; height: 100%;\">", unsafe_allow_html=True)
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
                    
                    st.write(f"**Sem {num_semana}** ({inicio_sem}-{fim_sem})")
                    st.metric("Vendido", f"R$ {total_vendido_sem:,.2f}".replace(",", "."), f"{progresso_sem:.1f}% vs Meta R$ {meta_sem_valor:,.2f}".replace(",","."), delta_color="off")
                    bonus_sem_txt = f"✅ R$ {bonus_sem_valor:,.2f}".replace(",", ".") if bonus_sem_atingido else f"❌ R$ {bonus_sem_valor:,.2f}".replace(",", ".")
                    st.write(f"Bônus: {bonus_sem_txt}")
                    st.progress(min(progresso_sem / 100, 1.0))
                    st.markdown("</div>", unsafe_allow_html=True)
                col_idx += 1
            # Preencher colunas vazias se houver menos de 4 semanas
            while col_idx % num_cols_semanais != 0:
                 with cols_semanas[col_idx % num_cols_semanais]:
                     st.write("") # Adiciona espaço vazio para alinhar
                 col_idx += 1
            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.error("Não foi possível carregar os dados de uma ou ambas as abas da planilha (Metas, Vendas). Verifique as mensagens de erro acima, o compartilhamento da planilha e os nomes das abas.")

# --- Rodapé ---
st.caption("Desenvolvido por Manus (vFinal Flutuante - Testado)")

