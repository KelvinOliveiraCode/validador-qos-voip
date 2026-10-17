# Validador de QoS VoIP / VoIP QoS Validator

## PT-BR

### Descrição

Validador determinístico de QoS para tráfego VoIP, em Python. Mede latência, jitter e perda de pacotes por simulação — não depende de rede real e aceita injeção de resultados — e valida a medição contra os limiares VoIP, emitindo veredito PASS ou FAIL.

Limiares padrão: latência < 150 ms, jitter < 30 ms, perda < 1%.

### Como usar

Requisito: Python 3.10 ou superior.

Instale o pacote em modo editável:

```
cd validador-qos-voip
pip install -e .
```

Execute a simulação:

```
python -m validador_qos_voip --count 100 --seed 1 --loss-rate 0.0
```

Exemplo de saída (PASS):

```
Validador de QoS VoIP — resultado: PASS
  latência média : 40.12 ms (limiar < 150 ms)
  jitter         : 4.87 ms (limiar < 30 ms)
  perda          : 0.0% (limiar < 1%)
```

O programa termina com código 0 em PASS e 1 em FAIL, o que permite usá-lo em scripts e CI.

Opções da CLI:

| Opção | Padrão | Significado |
|-------|--------|-------------|
| `--count` | 100 | número de pacotes simulados |
| `--base-latency-ms` | 40.0 | latência base em ms |
| `--jitter-factor-ms` | 5.0 | desvio padrão da latência em ms |
| `--loss-rate` | 0.0 | taxa de perda de pacotes, de 0.0 a 1.0 |
| `--seed` | 0 | semente do gerador aleatório |
| `--max-latency-ms` | 150.0 | limiar de latência em ms |
| `--max-jitter-ms` | 30.0 | limiar de jitter em ms |
| `--max-loss-pct` | 1.0 | limiar de perda percentual |

### Injeção de resultados

Não quer simular? Inje direto um `QoSMeasurement`:

```python
from validador_qos_voip import QoSMeasurement, evaluate

medicao = QoSMeasurement(latency_ms=80.0, jitter_ms=12.0, loss_pct=0.2)
veredito = evaluate(medicao)
print(veredito.passed)  # True
print(veredito.failures)  # []
```

### Testes

```
python -m pytest -q
```

Resultado: 19 aprovados. Lint: `python -m ruff check .` passa sem avisos.

### Licença

MIT.

Autor: Kelvin Oliveira.

## EN

### Description

Deterministic VoIP QoS validator written in Python. Measures latency, jitter, and packet loss through simulation — no real network required, and results can be injected directly — then validates the measurement against VoIP thresholds, emitting a PASS or FAIL verdict.

Default thresholds: latency < 150 ms, jitter < 30 ms, loss < 1%.

### Usage

Requirement: Python 3.10 or newer.

Install the package in editable mode:

```
cd validador-qos-voip
pip install -e .
```

Run the simulation:

```
python -m validador_qos_voip --count 100 --seed 1 --loss-rate 0.0
```

Example output (PASS):

```
Validador de QoS VoIP — resultado: PASS
  latência média : 40.12 ms (limiar < 150 ms)
  jitter         : 4.87 ms (limiar < 30 ms)
  perda          : 0.0% (limiar < 1%)
```

The program exits with code 0 on PASS and 1 on FAIL, so it can be used in scripts and CI.

CLI options:

| Option | Default | Meaning |
|--------|---------|---------|
| `--count` | 100 | number of simulated packets |
| `--base-latency-ms` | 40.0 | base latency in ms |
| `--jitter-factor-ms` | 5.0 | latency standard deviation in ms |
| `--loss-rate` | 0.0 | packet loss rate, from 0.0 to 1.0 |
| `--seed` | 0 | random generator seed |
| `--max-latency-ms` | 150.0 | latency threshold in ms |
| `--max-jitter-ms` | 30.0 | jitter threshold in ms |
| `--max-loss-pct` | 1.0 | packet loss percentage threshold |

### Result injection

Prefer not to simulate? Inject a `QoSMeasurement` directly:

```python
from validador_qos_voip import QoSMeasurement, evaluate

measurement = QoSMeasurement(latency_ms=80.0, jitter_ms=12.0, loss_pct=0.2)
verdict = evaluate(measurement)
print(verdict.passed)  # True
print(verdict.failures)  # []
```

### Tests

```
python -m pytest -q
```

Result: 19 passed. Lint: `python -m ruff check .` passes with no warnings.

### License

MIT.

Author: Kelvin Oliveira.
