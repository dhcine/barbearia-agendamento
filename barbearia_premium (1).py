"""
Barbearia Premium - Sistema de Agendamento (Versão Comercial)
Execute: streamlit run barbearia_premium.py
"""

import streamlit as st
import sqlite3
from datetime import datetime, timedelta, date
import pandas as pd
from pathlib import Path
import yaml

# ==================== CAMINHOS ====================
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "barbearia.db"
CONFIG_PATH = BASE_DIR / "config.yaml"

# ==================== CONFIGURAÇÃO ====================
def carregar_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {
        "barbearia": {
            "nome": "Barbearia Premium",
            "slogan": "Estilo • Precisão • Experiência",
            "telefone": "",
            "endereco": "",
            "mensagem_boas_vindas": "Bem-vindo à nossa barbearia."
        },
        "whatsapp": {
            "numero_barbearia": "5511999999999",
            "enviar_para_cliente": True,
            "enviar_para_barbearia": True
        },
        "url_publica": "",
        "horario": {
            "abertura": "09:00",
            "fechamento": "19:00",
            "intervalo_minutos": 30,
            "dias_fechados": [6]
        },
        "admin": {"senha": "premium2026"},
        "tema": {
            "cor_principal": "#C9A227",
            "cor_secundaria": "#E8D48B",
            "cor_fundo": "#0D0D0D",
            "cor_card": "#1A1A1A"
        }
    }

CFG = carregar_config()
NOME = CFG["barbearia"]["nome"]
SLOGAN = CFG["barbearia"]["slogan"]
COR_PRINCIPAL = CFG["tema"]["cor_principal"]
COR_SECUNDARIA = CFG["tema"]["cor_secundaria"]
SENHA_ADMIN = CFG["admin"]["senha"]
HORA_ABERTURA = CFG["horario"]["abertura"]
HORA_FECHAMENTO = CFG["horario"]["fechamento"]
INTERVALO = CFG["horario"]["intervalo_minutos"]
DIAS_FECHADOS = CFG["horario"].get("dias_fechados", [6])
WA_CFG = CFG.get("whatsapp", {})
WA_NUMERO_BARBEARIA = WA_CFG.get("numero_barbearia", "")
WA_ENVIAR_CLIENTE = WA_CFG.get("enviar_para_cliente", True)
WA_ENVIAR_BARBEARIA = WA_CFG.get("enviar_para_barbearia", True)
URL_PUBLICA = (CFG.get("url_publica") or "").strip()

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title=f"{NOME} | Agendamento",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ====================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');
    
    .stApp {{
        background: linear-gradient(180deg, {CFG["tema"]["cor_fundo"]} 0%, #1A1510 100%);
        color: #F5F5F5;
        font-family: 'Inter', sans-serif;
    }}
    
    h1, h2, h3 {{
        font-family: 'Playfair Display', serif !important;
        color: {COR_PRINCIPAL} !important;
        letter-spacing: 0.5px;
    }}
    
    .main-header {{
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        border-bottom: 1px solid rgba(201, 162, 39, 0.3);
        margin-bottom: 2rem;
    }}
    
    .main-header h1 {{
        font-size: 2.6rem !important;
        margin-bottom: 0.2rem;
        background: linear-gradient(90deg, {COR_PRINCIPAL}, {COR_SECUNDARIA}, {COR_PRINCIPAL});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .subtitle {{
        color: #A0A0A0;
        font-size: 1.05rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }}
    
    .card {{
        background: {CFG["tema"]["cor_card"]};
        border: 1px solid rgba(201, 162, 39, 0.25);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }}
    
    .service-card {{
        background: linear-gradient(145deg, #1F1A14, #1A1A1A);
        border: 1px solid rgba(201, 162, 39, 0.3);
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        height: 100%;
    }}
    
    .service-price {{
        color: {COR_PRINCIPAL};
        font-size: 1.35rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }}
    
    .stButton > button {{
        background: linear-gradient(90deg, {COR_PRINCIPAL}, #A8841C) !important;
        color: #0D0D0D !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.4rem !important;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(90deg, {COR_SECUNDARIA}, {COR_PRINCIPAL}) !important;
        box-shadow: 0 4px 15px rgba(201, 162, 39, 0.4) !important;
    }}
    
    .stSelectbox > div > div, .stTextInput > div > div > input,
    .stDateInput > div > div > input, .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: #1A1A1A !important;
        border: 1px solid rgba(201, 162, 39, 0.3) !important;
        border-radius: 8px !important;
        color: #F5F5F5 !important;
    }}
    
    div[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #121212 0%, #1A1510 100%);
        border-right: 1px solid rgba(201, 162, 39, 0.2);
    }}
    
    .appointment-card {{
        background: #1A1A1A;
        border-left: 4px solid {COR_PRINCIPAL};
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-radius: 0 8px 8px 0;
    }}
    
    .status-confirmed {{ color: #28a745; font-weight: 600; }}
    .status-cancelled {{ color: #dc3545; font-weight: 600; }}
    
    .footer {{
        text-align: center;
        color: #A0A0A0;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(201, 162, 39, 0.2);
    }}
</style>
""", unsafe_allow_html=True)

# ==================== BANCO DE DADOS ====================
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            duracao_min INTEGER NOT NULL,
            preco REAL NOT NULL,
            ativo INTEGER DEFAULT 1
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS barbeiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especialidade TEXT,
            ativo INTEGER DEFAULT 1
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT NOT NULL,
            cliente_telefone TEXT NOT NULL,
            cliente_email TEXT,
            servico_id INTEGER NOT NULL,
            barbeiro_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            status TEXT DEFAULT 'confirmado',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (servico_id) REFERENCES servicos(id),
            FOREIGN KEY (barbeiro_id) REFERENCES barbeiros(id)
        )
    """)
    
    cur.execute("SELECT COUNT(*) FROM servicos")
    if cur.fetchone()[0] == 0:
        servicos = [
            ("Corte Clássico", "Corte tradicional com acabamento premium", 40, 80.00),
            ("Corte + Barba", "Corte completo + barba alinhada e hidratada", 60, 130.00),
            ("Barba Completa", "Aparar, alinhar e hidratar a barba", 30, 60.00),
            ("Premium Experience", "Corte + barba + sobrancelha + massagem facial", 90, 200.00),
            ("Corte Infantil", "Corte especial para crianças até 12 anos", 30, 50.00),
            ("Coloração / Luzes", "Coloração profissional ou luzes", 90, 180.00),
        ]
        cur.executemany(
            "INSERT INTO servicos (nome, descricao, duracao_min, preco) VALUES (?, ?, ?, ?)",
            servicos
        )
    
    cur.execute("SELECT COUNT(*) FROM barbeiros")
    if cur.fetchone()[0] == 0:
        barbeiros = [
            ("Carlos Mendes", "Cortes clássicos e degradê"),
            ("Ricardo Alves", "Barbas e bigodes"),
            ("Fernando Costa", "Cortes modernos e coloração"),
            ("Lucas Oliveira", "Atendimento infantil e premium"),
        ]
        cur.executemany(
            "INSERT INTO barbeiros (nome, especialidade) VALUES (?, ?)",
            barbeiros
        )
    
    conn.commit()
    conn.close()

def get_servicos(apenas_ativos=True):
    conn = get_connection()
    q = "SELECT * FROM servicos"
    if apenas_ativos:
        q += " WHERE ativo = 1"
    q += " ORDER BY preco"
    df = pd.read_sql_query(q, conn)
    conn.close()
    return df

def adicionar_servico(nome, descricao, duracao, preco):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO servicos (nome, descricao, duracao_min, preco) VALUES (?, ?, ?, ?)",
        (nome, descricao, duracao, preco)
    )
    conn.commit()
    conn.close()

def atualizar_servico(sid, nome, descricao, duracao, preco, ativo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE servicos SET nome=?, descricao=?, duracao_min=?, preco=?, ativo=? WHERE id=?",
        (nome, descricao, duracao, preco, ativo, sid)
    )
    conn.commit()
    conn.close()

def excluir_servico(sid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE servicos SET ativo = 0 WHERE id = ?", (sid,))
    conn.commit()
    conn.close()

def get_barbeiros(apenas_ativos=True):
    conn = get_connection()
    q = "SELECT * FROM barbeiros"
    if apenas_ativos:
        q += " WHERE ativo = 1"
    q += " ORDER BY nome"
    df = pd.read_sql_query(q, conn)
    conn.close()
    return df

def adicionar_barbeiro(nome, especialidade):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO barbeiros (nome, especialidade) VALUES (?, ?)",
        (nome, especialidade)
    )
    conn.commit()
    conn.close()

def atualizar_barbeiro(bid, nome, especialidade, ativo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE barbeiros SET nome=?, especialidade=?, ativo=? WHERE id=?",
        (nome, especialidade, ativo, bid)
    )
    conn.commit()
    conn.close()

def excluir_barbeiro(bid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE barbeiros SET ativo = 0 WHERE id = ?", (bid,))
    conn.commit()
    conn.close()

def get_agendamentos(filtro_data=None, status=None):
    conn = get_connection()
    query = """
        SELECT a.id, a.cliente_nome, a.cliente_telefone, a.cliente_email,
               s.nome as servico, s.preco, s.duracao_min,
               b.nome as barbeiro, a.data, a.horario, a.status, a.criado_em
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        JOIN barbeiros b ON a.barbeiro_id = b.id
        WHERE 1=1
    """
    params = []
    if filtro_data:
        query += " AND a.data = ?"
        params.append(filtro_data)
    if status:
        query += " AND a.status = ?"
        params.append(status)
    query += " ORDER BY a.data DESC, a.horario ASC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def slot_disponivel(barbeiro_id, data_str, horario_str, duracao_min):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.horario, s.duracao_min
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.barbeiro_id = ? AND a.data = ? AND a.status = 'confirmado'
    """, (barbeiro_id, data_str))
    existentes = cur.fetchall()
    conn.close()
    
    novo_inicio = datetime.strptime(f"{data_str} {horario_str}", "%Y-%m-%d %H:%M")
    novo_fim = novo_inicio + timedelta(minutes=duracao_min)
    
    for row in existentes:
        existente_inicio = datetime.strptime(f"{data_str} {row['horario']}", "%Y-%m-%d %H:%M")
        existente_fim = existente_inicio + timedelta(minutes=row['duracao_min'])
        if not (novo_fim <= existente_inicio or novo_inicio >= existente_fim):
            return False
    return True

def horarios_disponiveis(barbeiro_id, data_str, duracao_min):
    """Retorna apenas horários livres para o barbeiro na data, considerando a duração do serviço."""
    todos = gerar_horarios()
    livres = []
    for h in todos:
        if slot_disponivel(barbeiro_id, data_str, h, duracao_min):
            # Também garantir que o serviço termina antes do fechamento
            try:
                inicio = datetime.strptime(f"{data_str} {h}", "%Y-%m-%d %H:%M")
                fim = inicio + timedelta(minutes=duracao_min)
                limite = datetime.strptime(f"{data_str} {HORA_FECHAMENTO}", "%Y-%m-%d %H:%M")
                if fim <= limite:
                    livres.append(h)
            except Exception:
                livres.append(h)
    return livres

def criar_agendamento(cliente_nome, telefone, email, servico_id, barbeiro_id, data_str, horario_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO agendamentos 
        (cliente_nome, cliente_telefone, cliente_email, servico_id, barbeiro_id, data, horario)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cliente_nome, telefone, email, servico_id, barbeiro_id, data_str, horario_str))
    conn.commit()
    ag_id = cur.lastrowid
    conn.close()
    return ag_id

def cancelar_agendamento(agendamento_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE agendamentos SET status = 'cancelado' WHERE id = ?", (agendamento_id,))
    conn.commit()
    conn.close()


def limpar_telefone(telefone: str) -> str:
    """Remove tudo que não for dígito."""
    return "".join(c for c in telefone if c.isdigit())

def gerar_link_whatsapp(numero: str, mensagem: str) -> str:
    """Gera link wa.me com mensagem pré-preenchida."""
    numero_limpo = limpar_telefone(numero)
    if not numero_limpo.startswith("55") and len(numero_limpo) <= 11:
        numero_limpo = "55" + numero_limpo
    from urllib.parse import quote
    return f"https://wa.me/{numero_limpo}?text={quote(mensagem)}"

def montar_msg_cliente(nome, servico, barbeiro, data_fmt, horario, ag_id, nome_barbearia):
    return (
        f"Olá {nome}! ✅\n\n"
        f"Seu agendamento na *{nome_barbearia}* foi confirmado:\n\n"
        f"📋 Serviço: {servico}\n"
        f"👤 Profissional: {barbeiro}\n"
        f"📅 Data: {data_fmt}\n"
        f"🕐 Horário: {horario}\n"
        f"🔢 Protocolo: #{ag_id}\n\n"
        f"Obrigado pela preferência! Nos vemos em breve. ✂️"
    )

def montar_msg_barbearia(nome, telefone, servico, barbeiro, data_fmt, horario, ag_id):
    return (
        f"🆕 *Novo agendamento* #{ag_id}\n\n"
        f"Cliente: {nome}\n"
        f"Telefone: {telefone}\n"
        f"Serviço: {servico}\n"
        f"Barbeiro: {barbeiro}\n"
        f"Data: {data_fmt} às {horario}"
    )



def montar_msg_compartilhar(nome_barbearia, url):
    return (
        f"Olá! ✂️\n\n"
        f"Agende seu horário na *{nome_barbearia}* pelo link:\n\n"
        f"{url}\n\n"
        f"É rápido e fácil. Te esperamos!"
    )

def montar_msg_cancelamento_cliente(nome, servico, data_fmt, horario, ag_id, nome_barbearia):
    return (
        f"Olá {nome},\n\n"
        f"Seu agendamento na *{nome_barbearia}* foi *cancelado*:\n\n"
        f"📋 Serviço: {servico}\n"
        f"📅 Data: {data_fmt}\n"
        f"🕐 Horário: {horario}\n"
        f"🔢 Protocolo: #{ag_id}\n\n"
        f"Se quiser remarcar, é só entrar em contato. Até breve! ✂️"
    )

def montar_msg_cancelamento_barbearia(nome, telefone, servico, data_fmt, horario, ag_id):
    return (
        f"❌ *Agendamento cancelado* #{ag_id}\n\n"
        f"Cliente: {nome}\n"
        f"Telefone: {telefone}\n"
        f"Serviço: {servico}\n"
        f"Data: {data_fmt} às {horario}"
    )


def gerar_horarios():
    horarios = []
    h, m = map(int, HORA_ABERTURA.split(":"))
    fim_h, fim_m = map(int, HORA_FECHAMENTO.split(":"))
    atual = datetime(2000, 1, 1, h, m)
    limite = datetime(2000, 1, 1, fim_h, fim_m)
    while atual < limite:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=INTERVALO)
    return horarios

# ==================== INIT ====================
init_db()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown(f"### ✂️ {NOME}")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        ["🏠 Início", "📅 Agendar", "📋 Meus Agendamentos", "🔧 Administração"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    dias_nomes = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
    fechados = [dias_nomes.get(d, str(d)) for d in DIAS_FECHADOS]
    st.markdown(f"""
    <div style="font-size: 0.85rem; color: #A0A0A0; line-height: 1.7;">
        <strong style="color: {COR_PRINCIPAL};">Horário de funcionamento</strong><br>
        {HORA_ABERTURA} – {HORA_FECHAMENTO}<br>
        Fechado: {', '.join(fechados) if fechados else 'Nenhum'}
    </div>
    """, unsafe_allow_html=True)
    
    # Link para compartilhar com clientes
    st.markdown("---")
    st.markdown(f"**🔗 Link de agendamento**")
    if URL_PUBLICA:
        st.code(URL_PUBLICA, language=None)
        msg_share = montar_msg_compartilhar(NOME, URL_PUBLICA)
        # Usa número da barbearia só para abrir o WhatsApp; a mensagem vai para quem o usuário escolher
        link_share = gerar_link_whatsapp(WA_NUMERO_BARBEARIA or "5500000000000", msg_share)
        st.markdown(
            f'<a href="{link_share}" target="_blank" style="'
            f'display:inline-block;padding:0.55rem 0.9rem;margin-top:0.4rem;'
            f'background:#25D366;color:white;text-decoration:none;'
            f'border-radius:8px;font-weight:600;font-size:0.9rem;text-align:center;width:100%;">'
            f'📲 Compartilhar no WhatsApp</a>',
            unsafe_allow_html=True
        )
        st.caption("Abre o WhatsApp com o link pronto para enviar aos clientes.")
    else:
        st.caption("Configure `url_publica` no config.yaml após publicar o sistema online.")

# ==================== PÁGINAS ====================

if pagina == "🏠 Início":
    st.markdown(f"""
    <div class="main-header">
        <h1>{NOME}</h1>
        <p class="subtitle">{SLOGAN}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="card">
        <p style="font-size: 1.1rem; line-height: 1.7; color: #E0E0E0;">
            {CFG["barbearia"].get("mensagem_boas_vindas", "")}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Nossos Serviços")
    servicos = get_servicos()
    
    if servicos.empty:
        st.info("Nenhum serviço cadastrado ainda.")
    else:
        cols = st.columns(3)
        for idx, row in servicos.iterrows():
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="service-card">
                    <h3 style="color: {COR_SECUNDARIA}; font-size: 1.15rem; margin-bottom: 0.4rem;">{row['nome']}</h3>
                    <p style="color: #A0A0A0; font-size: 0.88rem; min-height: 42px;">{row['descricao'] or ''}</p>
                    <p style="color: #888; font-size: 0.85rem;">{row['duracao_min']} min</p>
                    <div class="service-price">R$ {row['preco']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👈 Use o menu lateral e clique em **Agendar** para marcar seu horário.")
    
    # Box de compartilhamento (visível quando há URL pública)
    if URL_PUBLICA:
        st.markdown("---")
        st.markdown("### 🔗 Compartilhar com seus clientes")
        st.markdown(f"""
        <div class="card">
            <p style="color:#E0E0E0; margin-bottom:0.8rem;">
                Envie este link no WhatsApp, Instagram ou Google para seus clientes agendarem sozinhos:
            </p>
            <p style="background:#111; padding:0.8rem 1rem; border-radius:8px; 
                      border:1px solid rgba(201,162,39,0.35); word-break:break-all; 
                      font-family:monospace; color:{COR_SECUNDARIA};">
                {URL_PUBLICA}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        msg_share = montar_msg_compartilhar(NOME, URL_PUBLICA)
        link_share = gerar_link_whatsapp(WA_NUMERO_BARBEARIA or "5500000000000", msg_share)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown(
                f'<a href="{link_share}" target="_blank" style="'
                f'display:inline-block;padding:0.75rem 1.4rem;'
                f'background:#25D366;color:white;text-decoration:none;'
                f'border-radius:8px;font-weight:600;text-align:center;width:100%;">'
                f'📲 Compartilhar link no WhatsApp</a>',
                unsafe_allow_html=True
            )

elif pagina == "📅 Agendar":
    st.markdown(f"""
    <div class="main-header">
        <h1>Agendar Horário</h1>
        <p class="subtitle">Reserve seu momento de cuidado</p>
    </div>
    """, unsafe_allow_html=True)
    
    servicos_df = get_servicos()
    barbeiros_df = get_barbeiros()
    
    if servicos_df.empty or barbeiros_df.empty:
        st.warning("Ainda não há serviços ou barbeiros cadastrados. Peça ao administrador para configurar.")
    else:
        # --- Seleções que atualizam os horários disponíveis (fora do form) ---
        st.markdown("#### ✂️ Serviço e Profissional")
        col1, col2 = st.columns(2)
        with col1:
            servico_opcoes = {
                f"{row['nome']} — R$ {row['preco']:.2f} ({row['duracao_min']} min)": row['id']
                for _, row in servicos_df.iterrows()
            }
            servico_sel = st.selectbox("Serviço *", list(servico_opcoes.keys()), key="ag_servico")
            servico_id = servico_opcoes[servico_sel]
            duracao = int(servicos_df.loc[servicos_df['id'] == servico_id, 'duracao_min'].values[0])
        
        with col2:
            barbeiro_opcoes = {
                f"{row['nome']} — {row['especialidade'] or 'Geral'}": row['id']
                for _, row in barbeiros_df.iterrows()
            }
            barbeiro_sel = st.selectbox("Barbeiro *", list(barbeiro_opcoes.keys()), key="ag_barbeiro")
            barbeiro_id = barbeiro_opcoes[barbeiro_sel]
        
        st.markdown("#### 📅 Data e Horário")
        col1, col2 = st.columns(2)
        with col1:
            hoje = date.today()
            data_agendamento = st.date_input(
                "Data *",
                min_value=hoje,
                max_value=hoje + timedelta(days=60),
                value=hoje + timedelta(days=1),
                key="ag_data"
            )
            dia_fechado = data_agendamento.weekday() in DIAS_FECHADOS
            if dia_fechado:
                st.warning("⚠️ Neste dia estamos fechados. Escolha outro dia.")
        
        data_str = data_agendamento.strftime("%Y-%m-%d")
        
        with col2:
            if dia_fechado:
                horarios = []
            else:
                horarios = horarios_disponiveis(barbeiro_id, data_str, duracao)
            
            if not dia_fechado and not horarios:
                st.warning("Nenhum horário disponível neste dia para este profissional/serviço.")
                horario_sel = None
            elif horarios:
                horario_sel = st.selectbox("Horário *", horarios, key="ag_horario")
            else:
                horario_sel = None
        
        # --- Dados do cliente + confirmação ---
        with st.form("form_agendamento"):
            st.markdown("#### 👤 Seus Dados")
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome completo *", placeholder="Seu nome")
                telefone = st.text_input("Telefone / WhatsApp *", placeholder="(11) 99999-9999")
            with col2:
                email = st.text_input("E-mail (opcional)", placeholder="seu@email.com")
            
            st.markdown("---")
            submitted = st.form_submit_button("✅ Confirmar Agendamento", use_container_width=True)
            
            if submitted:
                if not nome.strip() or not telefone.strip():
                    st.error("Por favor, preencha nome e telefone.")
                elif dia_fechado:
                    st.error("Não realizamos atendimentos neste dia.")
                elif not horario_sel:
                    st.error("Selecione um horário disponível.")
                else:
                    # Revalida no momento do envio (evita dois clientes pegarem o mesmo slot)
                    if not slot_disponivel(barbeiro_id, data_str, horario_sel, duracao):
                        st.error(
                            "⚠️ Este horário acabou de ser reservado. "
                            "Atualize a página e escolha outro horário."
                        )
                    else:
                        ag_id = criar_agendamento(
                            nome.strip(), telefone.strip(), email.strip() or None,
                            servico_id, barbeiro_id, data_str, horario_sel
                        )
                        data_fmt = data_agendamento.strftime('%d/%m/%Y')
                        servico_nome = servicos_df.loc[servicos_df['id'] == servico_id, 'nome'].values[0]
                        barbeiro_nome = barbeiros_df.loc[barbeiros_df['id'] == barbeiro_id, 'nome'].values[0]
                        
                        st.success(f"""
                        ✅ **Agendamento confirmado!**  
                        Número: **#{ag_id}**  
                        {nome} • {data_fmt} às {horario_sel}  
                        Guarde este número para consulta.
                        """)
                        st.balloons()
                        
                        st.markdown("### 📱 Enviar confirmação no WhatsApp")
                        
                        msg_cliente = montar_msg_cliente(
                            nome.strip(), servico_nome, barbeiro_nome,
                            data_fmt, horario_sel, ag_id, NOME
                        )
                        msg_barbearia = montar_msg_barbearia(
                            nome.strip(), telefone.strip(), servico_nome,
                            barbeiro_nome, data_fmt, horario_sel, ag_id
                        )
                        
                        col_wa1, col_wa2 = st.columns(2)
                        
                        if WA_ENVIAR_CLIENTE:
                            link_cliente = gerar_link_whatsapp(telefone.strip(), msg_cliente)
                            with col_wa1:
                                st.markdown(
                                    f'<a href="{link_cliente}" target="_blank" style="'
                                    f'display:inline-block;padding:0.7rem 1.2rem;'
                                    f'background:#25D366;color:white;text-decoration:none;'
                                    f'border-radius:8px;font-weight:600;text-align:center;width:100%;">'
                                    f'📲 Enviar para o Cliente</a>',
                                    unsafe_allow_html=True
                                )
                        
                        if WA_ENVIAR_BARBEARIA and WA_NUMERO_BARBEARIA:
                            link_barb = gerar_link_whatsapp(WA_NUMERO_BARBEARIA, msg_barbearia)
                            with col_wa2:
                                st.markdown(
                                    f'<a href="{link_barb}" target="_blank" style="'
                                    f'display:inline-block;padding:0.7rem 1.2rem;'
                                    f'background:#128C7E;color:white;text-decoration:none;'
                                    f'border-radius:8px;font-weight:600;text-align:center;width:100%;">'
                                    f'🏪 Avisar a Barbearia</a>',
                                    unsafe_allow_html=True
                                )
                        
                        st.caption("Os botões abrem o WhatsApp com a mensagem pronta. Basta clicar em Enviar.")
                        st.info("💡 Atualize a página ou escolha outra data/barbeiro para ver os horários atualizados.")


elif pagina == "📋 Meus Agendamentos":
    st.markdown(f"""
    <div class="main-header">
        <h1>Meus Agendamentos</h1>
        <p class="subtitle">Consulte ou cancele sua reserva</p>
    </div>
    """, unsafe_allow_html=True)
    
    telefone_busca = st.text_input("Digite seu telefone para localizar", placeholder="(11) 99999-9999")
    
    if telefone_busca.strip():
        conn = get_connection()
        df = pd.read_sql_query("""
            SELECT a.id, a.cliente_nome, s.nome as servico, b.nome as barbeiro,
                   a.data, a.horario, a.status, s.preco
            FROM agendamentos a
            JOIN servicos s ON a.servico_id = s.id
            JOIN barbeiros b ON a.barbeiro_id = b.id
            WHERE a.cliente_telefone LIKE ?
            ORDER BY a.data DESC, a.horario ASC
        """, conn, params=(f"%{telefone_busca.strip()}%",))
        conn.close()
        
        if df.empty:
            st.info("Nenhum agendamento encontrado com este telefone.")
        else:
            for _, row in df.iterrows():
                status_class = "status-confirmed" if row['status'] == 'confirmado' else "status-cancelled"
                data_fmt = datetime.strptime(row['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="appointment-card">
                        <strong>#{row['id']}</strong> — {row['cliente_nome']}<br>
                        <span style="color:{COR_PRINCIPAL}">{row['servico']}</span> com {row['barbeiro']}<br>
                        📅 {data_fmt} às {row['horario']} • R$ {row['preco']:.2f}<br>
                        Status: <span class="{status_class}">{row['status'].upper()}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if row['status'] == 'confirmado':
                        if st.button("Cancelar", key=f"cancel_{row['id']}"):
                            cancelar_agendamento(row['id'])
                            st.session_state['ultimo_cancelamento'] = {
                                'id': row['id'],
                                'nome': row['cliente_nome'],
                                'telefone': telefone_busca.strip(),
                                'servico': row['servico'],
                                'data': row['data'],
                                'horario': row['horario'],
                            }
                            st.success(f"Agendamento #{row['id']} cancelado.")
                            st.rerun()

    # Mostrar botões WhatsApp após cancelamento
    if 'ultimo_cancelamento' in st.session_state and st.session_state['ultimo_cancelamento']:
        c = st.session_state['ultimo_cancelamento']
        data_fmt = datetime.strptime(c['data'], "%Y-%m-%d").strftime("%d/%m/%Y") if isinstance(c['data'], str) and "-" in str(c['data']) else c['data']
        
        st.markdown("---")
        st.markdown("### 📱 Avisar sobre o cancelamento")
        
        msg_cli = montar_msg_cancelamento_cliente(
            c['nome'], c['servico'], data_fmt, c['horario'], c['id'], NOME
        )
        msg_barb = montar_msg_cancelamento_barbearia(
            c['nome'], c['telefone'], c['servico'], data_fmt, c['horario'], c['id']
        )
        
        col_c1, col_c2 = st.columns(2)
        if WA_ENVIAR_CLIENTE:
            link_c = gerar_link_whatsapp(c['telefone'], msg_cli)
            with col_c1:
                st.markdown(
                    f'<a href="{link_c}" target="_blank" style="'
                    f'display:inline-block;padding:0.7rem 1.2rem;'
                    f'background:#25D366;color:white;text-decoration:none;'
                    f'border-radius:8px;font-weight:600;text-align:center;width:100%;">'
                    f'📲 Avisar o Cliente</a>',
                    unsafe_allow_html=True
                )
        if WA_ENVIAR_BARBEARIA and WA_NUMERO_BARBEARIA:
            link_b = gerar_link_whatsapp(WA_NUMERO_BARBEARIA, msg_barb)
            with col_c2:
                st.markdown(
                    f'<a href="{link_b}" target="_blank" style="'
                    f'display:inline-block;padding:0.7rem 1.2rem;'
                    f'background:#128C7E;color:white;text-decoration:none;'
                    f'border-radius:8px;font-weight:600;text-align:center;width:100%;">'
                    f'🏪 Avisar a Barbearia</a>',
                    unsafe_allow_html=True
                )
        
        if st.button("Limpar aviso"):
            st.session_state['ultimo_cancelamento'] = None
            st.rerun()


    else:
        st.info("Digite o telefone usado no agendamento para visualizar suas reservas.")

elif pagina == "🔧 Administração":
    st.markdown(f"""
    <div class="main-header">
        <h1>Administração</h1>
        <p class="subtitle">Painel interno</p>
    </div>
    """, unsafe_allow_html=True)
    
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False
    
    if not st.session_state.admin_auth:
        senha = st.text_input("Senha de acesso", type="password", placeholder="Digite a senha")
        if st.button("Entrar"):
            if senha == SENHA_ADMIN:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    else:
        st.success("Acesso liberado ✓")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 Agenda do Dia", 
            "📊 Todos os Agendamentos", 
            "✂️ Serviços", 
            "👤 Barbeiros"
        ])
        
        with tab1:
            data_filtro = st.date_input("Selecione a data", value=date.today(), key="admin_data")
            df_dia = get_agendamentos(filtro_data=data_filtro.strftime("%Y-%m-%d"))
            
            if df_dia.empty:
                st.info("Nenhum agendamento nesta data.")
            else:
                df_display = df_dia[['id', 'horario', 'cliente_nome', 'cliente_telefone',
                                     'servico', 'barbeiro', 'status', 'preco']].copy()
                df_display.columns = ['ID', 'Horário', 'Cliente', 'Telefone',
                                      'Serviço', 'Barbeiro', 'Status', 'Valor']
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                st.markdown("#### Cancelar agendamento")
                ids_ok = df_dia[df_dia['status'] == 'confirmado']['id'].tolist()
                if ids_ok:
                    id_cancel = st.selectbox("Selecione o ID", ids_ok, key="cancel_dia")
                    if st.button("Confirmar cancelamento", key="btn_cancel_dia"):
                        # Buscar dados antes de cancelar
                        row_cancel = df_dia[df_dia['id'] == id_cancel].iloc[0]
                        cancelar_agendamento(id_cancel)
                        st.session_state['ultimo_cancelamento_admin'] = {
                            'id': int(id_cancel),
                            'nome': row_cancel['cliente_nome'],
                            'telefone': row_cancel['cliente_telefone'],
                            'servico': row_cancel['servico'],
                            'data': row_cancel['data'],
                            'horario': row_cancel['horario'],
                        }
                        st.success(f"Agendamento #{id_cancel} cancelado.")
                        st.rerun()
                
                # Botões WhatsApp após cancelamento no admin
                if 'ultimo_cancelamento_admin' in st.session_state and st.session_state['ultimo_cancelamento_admin']:
                    c = st.session_state['ultimo_cancelamento_admin']
                    data_fmt = datetime.strptime(str(c['data']), "%Y-%m-%d").strftime("%d/%m/%Y") if "-" in str(c['data']) else c['data']
                    st.markdown("### 📱 Avisar sobre o cancelamento")
                    msg_cli = montar_msg_cancelamento_cliente(c['nome'], c['servico'], data_fmt, c['horario'], c['id'], NOME)
                    msg_barb = montar_msg_cancelamento_barbearia(c['nome'], c['telefone'], c['servico'], data_fmt, c['horario'], c['id'])
                    col_a1, col_a2 = st.columns(2)
                    if WA_ENVIAR_CLIENTE:
                        with col_a1:
                            st.markdown(
                                f'<a href="{gerar_link_whatsapp(c["telefone"], msg_cli)}" target="_blank" style="'
                                f'display:inline-block;padding:0.7rem 1.2rem;background:#25D366;color:white;'
                                f'text-decoration:none;border-radius:8px;font-weight:600;text-align:center;width:100%;">'
                                f'📲 Avisar o Cliente</a>', unsafe_allow_html=True)
                    if WA_ENVIAR_BARBEARIA and WA_NUMERO_BARBEARIA:
                        with col_a2:
                            st.markdown(
                                f'<a href="{gerar_link_whatsapp(WA_NUMERO_BARBEARIA, msg_barb)}" target="_blank" style="'
                                f'display:inline-block;padding:0.7rem 1.2rem;background:#128C7E;color:white;'
                                f'text-decoration:none;border-radius:8px;font-weight:600;text-align:center;width:100%;">'
                                f'🏪 Avisar a Barbearia</a>', unsafe_allow_html=True)
                    if st.button("Limpar aviso", key="limpar_admin"):
                        st.session_state['ultimo_cancelamento_admin'] = None
                        st.rerun()
        
        with tab2:
            df_all = get_agendamentos()
            if df_all.empty:
                st.info("Ainda não há agendamentos.")
            else:
                df_show = df_all.copy()
                df_show['data'] = pd.to_datetime(df_show['data']).dt.strftime('%d/%m/%Y')
                st.dataframe(
                    df_show[['id', 'data', 'horario', 'cliente_nome', 'servico',
                             'barbeiro', 'status', 'preco']],
                    use_container_width=True, hide_index=True
                )
                
                st.markdown("#### Resumo")
                col1, col2, col3 = st.columns(3)
                confirmados = len(df_all[df_all['status'] == 'confirmado'])
                cancelados = len(df_all[df_all['status'] == 'cancelado'])
                receita = df_all[df_all['status'] == 'confirmado']['preco'].sum()
                col1.metric("Confirmados", confirmados)
                col2.metric("Cancelados", cancelados)
                col3.metric("Receita potencial", f"R$ {receita:,.2f}")
        
        with tab3:
            st.markdown("### Gerenciar Serviços")
            
            with st.expander("➕ Adicionar novo serviço", expanded=False):
                with st.form("form_novo_servico"):
                    ns_nome = st.text_input("Nome do serviço *")
                    ns_desc = st.text_area("Descrição")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        ns_duracao = st.number_input("Duração (minutos) *", min_value=15, max_value=240, value=40, step=5)
                    with col_b:
                        ns_preco = st.number_input("Preço (R$) *", min_value=0.0, value=80.0, step=5.0)
                    
                    if st.form_submit_button("Salvar serviço"):
                        if ns_nome.strip():
                            adicionar_servico(ns_nome.strip(), ns_desc.strip(), int(ns_duracao), float(ns_preco))
                            st.success("Serviço adicionado!")
                            st.rerun()
                        else:
                            st.error("Nome é obrigatório.")
            
            st.markdown("#### Serviços cadastrados")
            df_s = get_servicos(apenas_ativos=False)
            
            if not df_s.empty:
                for _, row in df_s.iterrows():
                    with st.expander(f"{'✅' if row['ativo'] else '❌'} {row['nome']} — R$ {row['preco']:.2f}"):
                        with st.form(f"edit_servico_{row['id']}"):
                            e_nome = st.text_input("Nome", value=row['nome'])
                            e_desc = st.text_area("Descrição", value=row['descricao'] or "")
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                e_duracao = st.number_input("Duração (min)", min_value=15, value=int(row['duracao_min']), key=f"dur_{row['id']}")
                            with c2:
                                e_preco = st.number_input("Preço", min_value=0.0, value=float(row['preco']), key=f"preco_{row['id']}")
                            with c3:
                                e_ativo = st.selectbox("Status", [1, 0], 
                                    format_func=lambda x: "Ativo" if x == 1 else "Inativo",
                                    index=0 if row['ativo'] else 1,
                                    key=f"ativo_{row['id']}")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("💾 Salvar alterações"):
                                    atualizar_servico(row['id'], e_nome, e_desc, int(e_duracao), float(e_preco), int(e_ativo))
                                    st.success("Atualizado!")
                                    st.rerun()
                            with col_btn2:
                                if st.form_submit_button("🗑️ Desativar"):
                                    excluir_servico(row['id'])
                                    st.success("Serviço desativado.")
                                    st.rerun()
        
        with tab4:
            st.markdown("### Gerenciar Barbeiros")
            
            with st.expander("➕ Adicionar novo barbeiro", expanded=False):
                with st.form("form_novo_barbeiro"):
                    nb_nome = st.text_input("Nome *")
                    nb_esp = st.text_input("Especialidade", placeholder="Ex: Cortes clássicos, barbas...")
                    
                    if st.form_submit_button("Salvar barbeiro"):
                        if nb_nome.strip():
                            adicionar_barbeiro(nb_nome.strip(), nb_esp.strip())
                            st.success("Barbeiro adicionado!")
                            st.rerun()
                        else:
                            st.error("Nome é obrigatório.")
            
            st.markdown("#### Barbeiros cadastrados")
            df_b = get_barbeiros(apenas_ativos=False)
            
            if not df_b.empty:
                for _, row in df_b.iterrows():
                    with st.expander(f"{'✅' if row['ativo'] else '❌'} {row['nome']}"):
                        with st.form(f"edit_barbeiro_{row['id']}"):
                            eb_nome = st.text_input("Nome", value=row['nome'])
                            eb_esp = st.text_input("Especialidade", value=row['especialidade'] or "")
                            eb_ativo = st.selectbox("Status", [1, 0],
                                format_func=lambda x: "Ativo" if x == 1 else "Inativo",
                                index=0 if row['ativo'] else 1,
                                key=f"bativo_{row['id']}")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("💾 Salvar alterações"):
                                    atualizar_barbeiro(row['id'], eb_nome, eb_esp, int(eb_ativo))
                                    st.success("Atualizado!")
                                    st.rerun()
                            with col_btn2:
                                if st.form_submit_button("🗑️ Desativar"):
                                    excluir_barbeiro(row['id'])
                                    st.success("Barbeiro desativado.")
                                    st.rerun()
        
        st.markdown("---")
        if st.button("Sair da Administração"):
            st.session_state.admin_auth = False
            st.rerun()

st.markdown(f"""
<div class="footer">
    {NOME} • Sistema de Agendamento<br>
    Desenvolvido com Python + Streamlit
</div>
""", unsafe_allow_html=True)
