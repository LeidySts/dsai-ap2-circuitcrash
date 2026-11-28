import re
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from starlette.testclient import TestClient

from circuitcrash.app import criar_app
from circuitcrash.dados.repositorio import Repositorio
from circuitcrash.dados.sql import RepositorioSQL
from conftest import HOJE, criar_repo_sql, url_sqlite


@pytest.fixture
def cliente() -> TestClient:
    return TestClient(criar_app())


@pytest.mark.parametrize("rota", ["/", "/partida", "/perfil", "/loja", "/loja?raridade=raro", "/ranking", "/regras"])
def test_paginas_abrem(cliente: TestClient, rota: str) -> None:
    resposta = cliente.get(rota)
    assert resposta.status_code == 200
    assert "CIRCUIT" in resposta.text


def test_health(cliente: TestClient) -> None:
    assert cliente.get("/health").json() == {"status": "ok"}


def test_jogada_via_htmx_devolve_so_o_jogo(cliente: TestClient) -> None:
    cliente.get("/partida")
    resposta = cliente.post("/partida/jogar", data={"linha": "2", "coluna": "3"}, headers={"HX-Request": "true"})
    assert resposta.status_code == 200
    assert resposta.text.lstrip().startswith('<div id="jogo"') or 'id="jogo"' in resposta.text[:400]
    assert "<html" not in resposta.text
    assert "capturou Bateria" in resposta.text


def test_jogada_sem_htmx_redireciona(cliente: TestClient) -> None:
    resposta = cliente.post("/partida/passar", follow_redirects=False)
    assert resposta.status_code == 303


def test_trocar_para_novato_mostra_sem_avatar(cliente: TestClient) -> None:
    cliente.post("/jogador", data={"jogador_id": "novato"})
    resposta = cliente.get("/perfil")
    assert "Sem avatar ainda" in resposta.text


def test_comprar_avatar_mostra_aviso(cliente: TestClient) -> None:
    resposta = cliente.post("/loja/comprar", data={"avatar_id": "onda"})
    assert resposta.status_code == 200
    assert "Onda é seu" in resposta.text


# ---------- com o banco (spec 002) ----------


@pytest.fixture
def cliente_sql(tmp_path: Path) -> Iterator[TestClient]:
    repo = criar_repo_sql(tmp_path)
    yield TestClient(criar_app(repo))
    repo.fechar()


@pytest.mark.parametrize("rota", ["/", "/perfil", "/loja", "/loja?raridade=raro", "/ranking", "/regras"])
def test_paginas_com_banco_iguais_as_da_memoria(cliente: TestClient, cliente_sql: TestClient, rota: str) -> None:
    resposta = cliente_sql.get(rota)
    assert resposta.status_code == 200
    assert resposta.text == cliente.get(rota).text


def test_paginas_do_novato_com_banco(cliente: TestClient, cliente_sql: TestClient) -> None:
    for c in (cliente, cliente_sql):
        c.post("/jogador", data={"jogador_id": "novato"})
    assert cliente_sql.get("/perfil").text == cliente.get("/perfil").text


def test_compra_com_banco_aparece_no_perfil(cliente_sql: TestClient) -> None:
    resposta = cliente_sql.post("/loja/comprar", data={"avatar_id": "onda"})
    assert "Onda é seu" in resposta.text
    assert "Onda" in cliente_sql.get("/perfil").text


# ---------- partida gravada no fim (spec 006) ----------


def _jogar_ate_o_fim(cliente: TestClient, htmx: bool = False) -> Any:
    """A partida de demonstração começa na rodada 6; passar 7 vezes a encerra."""
    cliente.get("/partida")
    for _ in range(6):
        cliente.post("/partida/passar")
    headers = {"HX-Request": "true"} if htmx else {}
    return cliente.post("/partida/passar", headers=headers, follow_redirects=not htmx)


def _fagulhas_no_cabecalho(html: str) -> int:
    achado = re.search(r"Fagulhas: </span>(\d+)", html)
    assert achado is not None
    return int(achado.group(1))


def test_fim_de_partida_grava_e_mostra_o_resultado(cliente: TestClient) -> None:
    # Passando sempre, "Você" fica em 3º com 4 pontos: +15 Fagulhas e rating 1482 -> 1466.
    resposta = _jogar_ate_o_fim(cliente)
    assert "Seu resultado" in resposta.text
    assert "+15 Fagulhas" in resposta.text
    assert "1482 → 1466" in resposta.text
    assert _fagulhas_no_cabecalho(resposta.text) == 320 + 15


def test_fim_de_partida_grava_uma_vez_so(cliente: TestClient) -> None:
    _jogar_ate_o_fim(cliente)
    cliente.post("/partida/passar")
    resposta = cliente.get("/partida")
    assert _fagulhas_no_cabecalho(resposta.text) == 335
    perfil = cliente.get("/perfil").text
    assert perfil.count("+15</td>") == 2  # a partida nova e a de exemplo de "hoje"


def test_fim_de_partida_via_htmx_pede_para_recarregar(cliente: TestClient) -> None:
    resposta = _jogar_ate_o_fim(cliente, htmx=True)
    assert resposta.headers.get("HX-Refresh") == "true"
    assert "Seu resultado" in resposta.text
    seguinte = cliente.post("/partida/passar", headers={"HX-Request": "true"})
    assert "HX-Refresh" not in seguinte.headers


def test_partida_gravada_aparece_no_perfil(cliente: TestClient) -> None:
    _jogar_ate_o_fim(cliente)
    perfil = cliente.get("/perfil").text
    corpo = perfil[perfil.index("<tbody>", perfil.index("Partidas recentes")) :]
    primeira = corpo[: corpo.index("</tr>")]
    assert "3º" in primeira and "-16" in primeira and "+15" in primeira and "hoje" in primeira


def test_jogar_de_novo_grava_outra_partida(cliente: TestClient) -> None:
    _jogar_ate_o_fim(cliente)
    cliente.post("/partida/nova")
    resposta = _jogar_ate_o_fim(cliente)
    assert _fagulhas_no_cabecalho(resposta.text) == 320 + 15 + 15


def test_partida_nao_terminada_nao_grava(cliente: TestClient) -> None:
    cliente.get("/partida")
    cliente.post("/partida/passar")
    resposta = cliente.get("/partida")
    assert "Seu resultado" not in resposta.text
    assert _fagulhas_no_cabecalho(resposta.text) == 320


def test_partida_do_novato_usa_k_provisorio(cliente: TestClient) -> None:
    cliente.post("/jogador", data={"jogador_id": "novato"})
    resposta = _jogar_ate_o_fim(cliente)
    # Rating igual ao dos adversários: 3º lugar = 48/3 * (0 + 0 + 1 - 1.5) = -8.
    assert "1200 → 1192" in resposta.text
    assert _fagulhas_no_cabecalho(resposta.text) == 60 + 15


def test_fim_de_partida_com_banco_persiste(cliente_sql: TestClient, tmp_path: Path) -> None:
    _jogar_ate_o_fim(cliente_sql)
    reaberto = RepositorioSQL(url_sqlite(tmp_path), hoje=lambda: HOJE)
    veterano = reaberto.obter_jogador("veterano")
    assert veterano is not None
    assert (veterano.fagulhas, veterano.rating, veterano.partidas) == (335, 1466, 49)
    assert reaberto.partidas_recentes("veterano")[0].quando == "hoje"
    reaberto.fechar()


def test_carta_isolante_pela_rota(cliente: TestClient) -> None:
    dados = {"carta": "isolante", "linha": "2", "coluna": "0"}
    resposta = cliente.post("/partida/carta", data=dados)
    assert resposta.status_code == 200
    assert "Isolante usado" in resposta.text


def test_carta_desconhecida_mostra_erro(cliente: TestClient) -> None:
    resposta = cliente.post("/partida/carta", data={"carta": "xyz"})
    assert resposta.status_code == 200
    assert "Carta desconhecida" in resposta.text


def test_partida_mostra_formulario_de_cartas(cliente: TestClient) -> None:
    resposta = cliente.get("/partida")
    assert resposta.status_code == 200
    assert "Usar carta" in resposta.text


def test_formulario_de_cartas_tem_classe_propria(cliente: TestClient) -> None:
    resposta = cliente.get("/partida")
    assert 'class="cartas"' in resposta.text
    assert "Cartas especiais" in resposta.text


def test_carta_usada_some_da_lista(cliente: TestClient) -> None:
    dados = {"carta": "isolante", "linha": "2", "coluna": "0"}
    cliente.post("/partida/carta", data=dados)
    resposta = cliente.get("/partida")
    assert '<option value="isolante">' not in resposta.text
    assert '<option value="curto">' in resposta.text


# ---------- painel de administração (spec 015, T006) ----------

# Apelido do jogador "novato". A rota /jogador só troca para os dois perfis de demonstração
# (veterano e novato); o visitante padrão (veterano, voltz_br) é um jogador comum.
ADMIN = "luma_dev"


@pytest.fixture
def cliente_admin(repo: Repositorio, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Cliente com ADMIN_USUARIO configurado, rodando na memória e no SQL."""
    monkeypatch.setenv("ADMIN_USUARIO", ADMIN)
    return TestClient(criar_app(repo))


def _entrar_como_admin(cliente: TestClient) -> None:
    cliente.post("/jogador", data={"jogador_id": "novato"})


def _secao(html: str, secao_id: str) -> str:
    """Trecho da página entre <section id="..."> e o </section> seguinte."""
    inicio = html.index(f'id="{secao_id}"')
    return html[inicio : html.index("</section>", inicio)]


def test_admin_jogador_comum_ve_acesso_restrito(cliente_admin: TestClient) -> None:
    resposta = cliente_admin.get("/admin")
    assert resposta.status_code == 403
    assert "Acesso restrito" in resposta.text
    assert 'id="admin-resumo"' not in resposta.text
    assert 'id="admin-jogadores"' not in resposta.text
    assert 'id="admin-acoes"' not in resposta.text


def test_admin_sem_admin_configurado_ninguem_entra(repo: Repositorio, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ADMIN_USUARIO", raising=False)
    cliente = TestClient(criar_app(repo))
    _entrar_como_admin(cliente)
    resposta = cliente.get("/admin")
    assert resposta.status_code == 403
    assert "Acesso restrito" in resposta.text


def test_admin_ve_os_numeros_do_jogo(cliente_admin: TestClient) -> None:
    _entrar_como_admin(cliente_admin)
    resposta = cliente_admin.get("/admin")
    assert resposta.status_code == 200
    assert "Acesso restrito" not in resposta.text
    resumo = _secao(resposta.text, "admin-resumo")
    assert "Jogadores" in resumo and ">6<" in resumo
    assert "Partidas" in resumo and ">7<" in resumo
    assert "Fagulhas em circulação" in resumo and ">3030<" in resumo


def test_admin_lista_jogadores_do_maior_rating_para_o_menor(cliente_admin: TestClient) -> None:
    _entrar_como_admin(cliente_admin)
    lista = _secao(cliente_admin.get("/admin").text, "admin-jogadores")
    ordem = ["ninacircuit", "lia.ohm", "voltz_br", "brunovolt", "kai_k", "luma_dev"]
    posicoes = [lista.index(apelido) for apelido in ordem]
    assert posicoes == sorted(posicoes)
    # Nome, rating e saldo de Fagulhas de cada jogador (aqui, a primeira).
    linha_nina = lista[posicoes[0] : posicoes[1]]
    assert "1611" in linha_nina and "1500" in linha_nina


def test_admin_mostra_as_acoes_de_ajuste(cliente_admin: TestClient, repo: Repositorio) -> None:
    repo.ajustar_fagulhas(ADMIN, "kai", 50, datetime(2026, 11, 27, 12, 0))
    _entrar_como_admin(cliente_admin)
    acoes = _secao(cliente_admin.get("/admin").text, "admin-acoes")
    assert ADMIN in acoes
    assert "kai" in acoes
    assert "+50" in acoes
    assert "27/11/2026 12:00" in acoes


def test_admin_sem_acoes_avisa_que_a_lista_esta_vazia(cliente_admin: TestClient) -> None:
    _entrar_como_admin(cliente_admin)
    acoes = _secao(cliente_admin.get("/admin").text, "admin-acoes")
    assert "Nenhum ajuste ainda" in acoes


# ---------- ajuste de saldo pelo painel (spec 015, T007) ----------


def _aviso(html: str) -> str:
    """Texto do aviso de sucesso ou erro mostrado no topo da página."""
    inicio = html.index('class="aviso')
    return html[inicio : html.index("</div>", inicio)]


def _saldo(repo: Repositorio, jogador_id: str) -> int:
    jogador = repo.obter_jogador(jogador_id)
    assert jogador is not None
    return jogador.fagulhas


def test_admin_tem_formulario_de_ajuste(cliente_admin: TestClient) -> None:
    _entrar_como_admin(cliente_admin)
    formulario = _secao(cliente_admin.get("/admin").text, "admin-ajuste")
    assert 'method="post"' in formulario
    assert 'action="/admin/ajuste"' in formulario
    assert 'name="jogador_id"' in formulario
    assert '<option value="kai">' in formulario
    assert 'name="valor"' in formulario


def test_admin_ajuste_soma_ao_saldo_e_registra_a_acao(cliente_admin: TestClient, repo: Repositorio) -> None:
    _entrar_como_admin(cliente_admin)
    resposta = cliente_admin.post("/admin/ajuste", data={"jogador_id": "kai", "valor": "50"}, follow_redirects=False)
    assert resposta.status_code == 303
    assert resposta.headers["location"] == "/admin"
    assert _saldo(repo, "kai") == 90
    acao = repo.acoes_admin()[0]
    assert (acao.admin, acao.jogador, acao.valor) == (ADMIN, "kai", 50)


def test_admin_ajuste_mostra_mensagem_de_sucesso(cliente_admin: TestClient) -> None:
    _entrar_como_admin(cliente_admin)
    resposta = cliente_admin.post("/admin/ajuste", data={"jogador_id": "kai", "valor": "50"})
    assert resposta.status_code == 200
    aviso = _aviso(resposta.text)
    assert "erro" not in aviso
    assert "kai_k" in aviso and "+50" in aviso and "90" in aviso
    assert "+50" in _secao(resposta.text, "admin-acoes")


def test_admin_ajuste_negativo_que_cabe_no_saldo(cliente_admin: TestClient, repo: Repositorio) -> None:
    _entrar_como_admin(cliente_admin)
    cliente_admin.post("/admin/ajuste", data={"jogador_id": "kai", "valor": "-40"})
    assert _saldo(repo, "kai") == 0


def test_admin_ajuste_que_deixaria_saldo_negativo_e_recusado(cliente_admin: TestClient, repo: Repositorio) -> None:
    _entrar_como_admin(cliente_admin)
    resposta = cliente_admin.post("/admin/ajuste", data={"jogador_id": "kai", "valor": "-41"})
    aviso = _aviso(resposta.text)
    assert "erro" in aviso
    assert "O saldo não pode ficar negativo." in aviso
    assert _saldo(repo, "kai") == 40
    assert repo.acoes_admin() == []


@pytest.mark.parametrize("valor", ["", "abc", "1.5"])
def test_admin_ajuste_com_valor_que_nao_e_inteiro_e_recusado(
    cliente_admin: TestClient, repo: Repositorio, valor: str
) -> None:
    _entrar_como_admin(cliente_admin)
    resposta = cliente_admin.post("/admin/ajuste", data={"jogador_id": "kai", "valor": valor})
    aviso = _aviso(resposta.text)
    assert "erro" in aviso
    assert "Informe um número inteiro" in aviso
    assert _saldo(repo, "kai") == 40
    assert repo.acoes_admin() == []


def test_admin_ajuste_de_valor_zero_e_recusado(cliente_admin: TestClient, repo: Repositorio) -> None:
    _entrar_como_admin(cliente_admin)
    resposta = cliente_admin.post("/admin/ajuste", data={"jogador_id": "kai", "valor": "0"})
    aviso = _aviso(resposta.text)
    assert "erro" in aviso
    assert "O valor do ajuste não pode ser zero." in aviso
    assert _saldo(repo, "kai") == 40
    assert repo.acoes_admin() == []


def test_admin_ajuste_de_jogador_inexistente_e_recusado(cliente_admin: TestClient, repo: Repositorio) -> None:
    _entrar_como_admin(cliente_admin)
    resposta = cliente_admin.post("/admin/ajuste", data={"jogador_id": "nao-existe", "valor": "10"})
    aviso = _aviso(resposta.text)
    assert "erro" in aviso
    assert "Jogador não encontrado" in aviso
    assert repo.acoes_admin() == []


def test_admin_ajuste_por_jogador_comum_e_proibido(cliente_admin: TestClient, repo: Repositorio) -> None:
    resposta = cliente_admin.post("/admin/ajuste", data={"jogador_id": "kai", "valor": "50"}, follow_redirects=False)
    assert resposta.status_code == 403
    assert "Acesso restrito" in resposta.text
    assert _saldo(repo, "kai") == 40
    assert repo.acoes_admin() == []
