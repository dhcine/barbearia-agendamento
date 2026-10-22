# ✂️ Sistema de Agendamento - Barbearia Premium

Versão comercial pronta para personalização e venda.

## Instalação rápida

```bash
pip install -r requirements.txt
streamlit run barbearia_premium.py
```

Acesse: http://localhost:8501

## Personalização (importante)

Edite o arquivo **config.yaml** para alterar:

- Nome da barbearia
- Slogan
- Mensagem de boas-vindas
- Horário de funcionamento
- Dias fechados
- **Senha do painel admin**
- Cores do tema

Exemplo de alteração de senha:

```yaml
admin:
  senha: "sua_senha_segura_aqui"
```

## Funcionalidades

### Cliente
- Visualizar serviços e preços
- Agendar horário (com verificação de conflito)
- Consultar e cancelar agendamentos pelo telefone

### Administração (senha no config.yaml)
- Agenda do dia
- Todos os agendamentos + estatísticas de receita
- **CRUD completo de Serviços** (adicionar, editar, desativar)
- **CRUD completo de Barbeiros** (adicionar, editar, desativar)

## Arquivos do projeto

| Arquivo | Descrição |
|---------|-----------|
| `barbearia_premium.py` | Aplicação principal |
| `config.yaml` | Configurações personalizáveis |
| `requirements.txt` | Dependências |
| `barbearia.db` | Banco de dados (criado automaticamente) |

## Senha padrão do admin

```
premium2026
```

**Altere antes de entregar ao cliente.**

## Requisitos

- Python 3.9 ou superior
- Windows, macOS ou Linux

## Suporte à personalização

Para white-label (colocar a marca do cliente):

1. Altere `config.yaml`
2. (Opcional) Troque as cores no mesmo arquivo
3. Entregue os arquivos + este README

## Notificação WhatsApp

Após cada agendamento aparecem botões para:

1. **Enviar para o Cliente** — abre o WhatsApp do cliente com a confirmação pronta
2. **Avisar a Barbearia** — envia o aviso para o número configurado

Configure no `config.yaml`:

```yaml
whatsapp:
  numero_barbearia: "5511999999999"   # DDI 55 + DDD + número
  enviar_para_cliente: true
  enviar_para_barbearia: true
```

Não precisa de API paga. O sistema gera um link `wa.me` e o WhatsApp Web/App abre com a mensagem preenchida.

## Link para os clientes

1. Publique o sistema na nuvem (Streamlit Cloud, Railway, Render, etc.)
2. Copie a URL pública (ex: `https://sua-barbearia.streamlit.app`)
3. Cole no `config.yaml`:

```yaml
url_publica: "https://sua-barbearia.streamlit.app"
```

4. Reinicie o app

Na tela inicial e na barra lateral aparecerá o botão **Compartilhar no WhatsApp**, com a mensagem e o link prontos para enviar aos clientes.
