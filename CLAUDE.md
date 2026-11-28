Siga as instruções de @AGENTS.md.

# Regras da AP2 (fork LeidySts/dsai-ap2-circuitcrash)

## Repositório
- Trabalhe só neste repositório (o fork `LeidySts/dsai-ap2-circuitcrash`, remoto `origin`).
- Nunca mexa no repositório `henriquelm-io`: nada de push, PR, issue ou comentário lá.

## Git
- Nunca use `git push --force` (nem `--force-with-lease`).
- Nunca commite direto na `main`: sempre crie uma branch e abra um PR.
- Todo commit termina com estas linhas de trailer:

  ```
  Agent: Claude Code
  Spec: SPEC/2026-11-26-painel-administracao.md
  Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
  ```

## TDD
- Escreva o teste primeiro, rode e mostre que ele falha. Só depois escreva o código.
- Os testes do repositório rodam na memória e no SQL (fixture `repo` em `tests/conftest.py`).

## Antes de cada commit
Rode os quatro, e todos precisam passar:

```
uv run ruff format
uv run ruff check
uv run mypy src
uv run pytest -q
```

## Explicações
- A autora é iniciante: explique em português simples o que foi feito, em poucas frases.
