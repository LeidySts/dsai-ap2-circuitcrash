# Plano Técnico: Missões e Conquistas

## Arquitetura
- **Domínio (`src/circuitcrash/domain/missoes.py`)**: Criar as classes e regras de negócio para validar se uma missão foi cumprida, calcular recompensas e limites diários.
- **Dados (`src/circuitcrash/dados/sql.py`)**: Atualizar o repositório de banco de dados para ler e gravar o progresso real nas tabelas `progresso_missoes` e `progresso_conquistas`.
- **Web (`src/circuitcrash/app.py`)**: Atualizar a rota do perfil para buscar os dados reais do banco em vez de usar os dados de exemplo (`carga.py`).

## Tecnologias
- Python 3.12
- SQLAlchemy (para os repositórios)
- Jinja2 (para renderizar o perfil com os dados reais)
