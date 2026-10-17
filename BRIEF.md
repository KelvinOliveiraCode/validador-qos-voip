# BRIEF — validador-qos-voip

Projeto: validador determinístico de QoS para VoIP (área Redes).
Stack: Python 3.10+, sem dependências externas (stdlib only).
Dono da validação: workflow manager (este subagent).

## Entregas (arquivos criados)

| Caminho | Conteúdo |
|---------|----------|
| `pyproject.toml` | Projeto setuptools, scripts CLI, pytest `pythonpath = ["src"]` |
| `src/validador_qos_voip/__init__.py` | Exporta API pública |
| `src/validador_qos_voip/qos.py` | `QoSThresholds`, `QoSMeasurement`, `QoSVerdict`, `QoSValidator`, `PingSimulator`, `evaluate` |
| `src/validador_qos_voip/__main__.py` | CLI `python -m validador_qos_voip` (PASS/FAIL, exit 0/1) |
| `tests/test_qos.py` | 19 testes (limiares estritos, acumulado de falhas, determinismo do simulador, injeção de perda, CLI) |
| `README.md` | Bilíngue PT-BR + EN: título, descrição, como usar, limiares, injeção de resultados, testes, licença MIT, autor Kelvin Oliveira |
| `BRIEF.md` | Este arquivo |

## Comportamento (MVP)

- Mede latência, jitter e perda via `PingSimulator` — simulação determinística com semente; não usa rede real.
- Permite injeção de resultados direta com `QoSMeasurement` + `evaluate(...)`.
- Valida contra limiares VoIP (padrão): latência < 150 ms, jitter < 30 ms, perda < 1% (comparação estrita: valor igual ao limiar já falha).
- Emite veredito PASS/FAIL com lista de falhas; CLI termina com código 0 (PASS) ou 1 (FAIL).

## Como verificar

Na pasta do projeto:

```
cd C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\validador-qos-voip
python -m ruff check .
python -m pytest -q
```

Resultado esperado:
- `ruff check .`: All checks passed!
- `pytest -q`: 19 passed

Clique de exemplo (PASS):

```
python -m validador_qos_voip --count 100 --seed 1 --loss-rate 0.0
```

Clique de exemplo (FAIL, saída 1):

```
python -m validador_qos_voip --count 200 --seed 2 --base-latency-ms 200.0
```

## Caminhos

- README: `...\projects\validador-qos-voip\README.md`
- BRIEF: `...\projects\validador-qos-voip\BRIEF.md`
- Testes: `...\projects\validador-qos-voip\tests\test_qos.py`

Autor: Kelvin Oliveira. Licença: MIT.
