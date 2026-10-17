"""Suíte de testes do validador de QoS VoIP.

Cobre: validação contra limiares (pass/fail), simulador determinístico
de ping (sem rede real), injeção de resultados e função de conveniência.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from validador_qos_voip import (
    PingSimulator,
    QoSMeasurement,
    QoSThresholds,
    QoSValidator,
    evaluate,
)

SRC = Path(__file__).resolve().parents[1] / "src"


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "validador_qos_voip", *args],
        check=False,
        cwd=SRC,
        capture_output=True,
        text=True,
    )


def test_validate_pass_quando_todas_as_metricas_abaixo_dos_limiares() -> None:
    """Tudo dentro dos limiares VoIP => PASS."""
    medicao = QoSMeasurement(latency_ms=40.0, jitter_ms=5.0, loss_pct=0.1)
    veredito = QoSValidator().validate(medicao)

    assert veredito.passed is True
    assert veredito.failures == []
    assert veredito.measurement == medicao


def test_validate_falha_latencia_no_limiar() -> None:
    """Limiar é estrito: latência == 150 ms falha (< 150 ms é exigido)."""
    medicao = QoSMeasurement(latency_ms=150.0, jitter_ms=5.0, loss_pct=0.1)
    veredito = QoSValidator().validate(medicao)

    assert veredito.passed is False
    assert len(veredito.failures) == 1
    assert "latência" in veredito.failures[0]


def test_validate_passa_latencia_abaixo_do_limiar() -> None:
    medicao = QoSMeasurement(latency_ms=149.9, jitter_ms=5.0, loss_pct=0.1)
    veredito = QoSValidator().validate(medicao)

    assert veredito.passed is True


def test_validate_falha_jitter_no_limiar() -> None:
    medicao = QoSMeasurement(latency_ms=40.0, jitter_ms=30.0, loss_pct=0.1)
    veredito = QoSValidator().validate(medicao)

    assert veredito.passed is False
    assert any("jitter" in f for f in veredito.failures)


def test_validate_passa_jitter_abaixo_do_limiar() -> None:
    medicao = QoSMeasurement(latency_ms=40.0, jitter_ms=29.9, loss_pct=0.1)
    veredito = QoSValidator().validate(medicao)

    assert veredito.passed is True


def test_validate_falha_perda_no_limiar() -> None:
    medicao = QoSMeasurement(latency_ms=40.0, jitter_ms=5.0, loss_pct=1.0)
    veredito = QoSValidator().validate(medicao)

    assert veredito.passed is False
    assert any("perda" in f for f in veredito.failures)


def test_validate_passa_perda_abaixo_do_limiar() -> None:
    medicao = QoSMeasurement(latency_ms=40.0, jitter_ms=5.0, loss_pct=0.99)
    veredito = QoSValidator().validate(medicao)

    assert veredito.passed is True


def test_validate_acumula_todas_as_falhas() -> None:
    """Três métricas acima => três falhas, não encerra na primeira."""
    medicao = QoSMeasurement(latency_ms=200.0, jitter_ms=50.0, loss_pct=5.0)
    veredito = QoSValidator().validate(medicao)

    assert veredito.passed is False
    assert len(veredito.failures) == 3
    assert any("latência" in f for f in veredito.failures)
    assert any("jitter" in f for f in veredito.failures)
    assert any("perda" in f for f in veredito.failures)


def test_validate_com_limiares_personalizados() -> None:
    thresholds = QoSThresholds(max_latency_ms=50.0, max_jitter_ms=10.0, max_loss_pct=0.5)
    medicao = QoSMeasurement(latency_ms=40.0, jitter_ms=5.0, loss_pct=0.1)
    veredito = QoSValidator(thresholds).validate(medicao)

    assert veredito.passed is True
    assert veredito.thresholds.max_latency_ms == 50.0

    ruim = QoSMeasurement(latency_ms=60.0, jitter_ms=5.0, loss_pct=0.1)
    assert QoSValidator(thresholds).validate(ruim).passed is False


def test_ping_simulator_e_deterministico() -> None:
    """Mesma semente e parâmetros => mesmo resultado."""
    resultado_a = PingSimulator(seed=7).measure(count=50, loss_rate=0.02)
    resultado_b = PingSimulator(seed=7).measure(count=50, loss_rate=0.02)

    assert resultado_a == resultado_b


def test_ping_simulator_semente_diferente_resultado_diferente() -> None:
    resultado_a = PingSimulator(seed=1).measure(count=200, loss_rate=0.1)
    resultado_b = PingSimulator(seed=2).measure(count=200, loss_rate=0.1)

    assert resultado_a != resultado_b


def test_ping_simulator_injeta_perda_total() -> None:
    """loss_rate = 1.0 => 100% de perda, sem latência nem jitter."""
    resultado = PingSimulator(seed=3).measure(count=100, loss_rate=1.0)

    assert resultado.loss_pct == 100.0
    assert resultado.latency_ms == 0.0
    assert resultado.jitter_ms == 0.0


def test_ping_simulator_sem_perda() -> None:
    """loss_rate = 0.0 => 0% de perda."""
    resultado = PingSimulator(seed=3).measure(count=100, loss_rate=0.0)

    assert resultado.loss_pct == 0.0


def test_ping_simulator_contagem_invalida_erro() -> None:
    for count in (0, -1):
        try:
            PingSimulator(seed=1).measure(count=count)
        except ValueError:
            break
    else:
        raise AssertionError("esperava ValueError para count invalido")


def test_ping_simulator_taxa_perda_invalida_erro() -> None:
    for loss_rate in (-0.1, 1.1):
        try:
            PingSimulator(seed=1).measure(count=10, loss_rate=loss_rate)
        except ValueError:
            break
    else:
        raise AssertionError("esperava ValueError para loss_rate invalido")


def test_evaluate_equivalente_a_validator() -> None:
    medicao = QoSMeasurement(latency_ms=100.0, jitter_ms=20.0, loss_pct=0.5)
    assert evaluate(medicao) == QoSValidator().validate(medicao)


def test_veredito_contem_dados_da_medicao_e_limiares() -> None:
    medicao = QoSMeasurement(latency_ms=10.0, jitter_ms=2.0, loss_pct=0.01)
    thresholds = QoSThresholds()
    veredito = QoSValidator(thresholds).validate(medicao)

    assert veredito.measurement is medicao
    assert veredito.thresholds is thresholds


def test_cli_saida_pass_saida_zero() -> None:
    resultado = _run_cli("--count", "100", "--seed", "1", "--loss-rate", "0.0")

    assert resultado.returncode == 0
    assert "resultado: PASS" in resultado.stdout


def test_cli_saida_fail_saida_nao_zero() -> None:
    resultado = _run_cli(
        "--count", "200", "--seed", "2",
        "--base-latency-ms", "200.0",
    )

    assert resultado.returncode == 1
    assert "resultado: FAIL" in resultado.stdout
    assert "latência" in resultado.stdout
