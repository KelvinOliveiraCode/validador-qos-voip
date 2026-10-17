"""Validador determinístico de QoS para VoIP.

Mede latência, jitter e perda de pacotes por simulação determinística
(sem dependência de rede real) e valida o resultado contra limiares
VoIP, emitindo veredito pass/fail. Resultados podem ser injetados
diretamente, sem passar pelo simulador.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class QoSThresholds:
    """Limiares de aceitação para tráfego VoIP (ms / %)."""

    max_latency_ms: float = 150.0
    max_jitter_ms: float = 30.0
    max_loss_pct: float = 1.0


@dataclass(frozen=True)
class QoSMeasurement:
    """Resultado agregado de uma medição de QoS."""

    latency_ms: float
    jitter_ms: float
    loss_pct: float


@dataclass(frozen=True)
class QoSVerdict:
    """Veredito de validação contra os limiares configurados."""

    passed: bool
    measurement: QoSMeasurement
    thresholds: QoSThresholds
    failures: list[str]


class PingSimulator:
    """Simulador determinístico de ping. Não usa rede real.

    Gera latências de pacotes a partir de uma semente, com injeção de
    taxa de perda e fator de jitter. Mesmos parâmetros => mesmo resultado.
    """

    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)

    def measure(
        self,
        count: int = 100,
        base_latency_ms: float = 40.0,
        jitter_factor_ms: float = 5.0,
        loss_rate: float = 0.0,
    ) -> QoSMeasurement:
        """Simula ``count`` pacotes e retorna a métrica agregada.

        Args:
            count: número de pacotes simulados.
            base_latency_ms: latência base em ms.
            jitter_factor_ms: desvio padrão da latência em ms.
            loss_rate: taxa de perda de pacotes entre 0.0 e 1.0.

        Returns:
            QoSMeasurement com latência média, jitter e perda em %.
        """
        if count <= 0:
            raise ValueError("count deve ser maior que zero")
        if not 0.0 <= loss_rate <= 1.0:
            raise ValueError("loss_rate deve estar entre 0.0 e 1.0")

        latencies: list[float] = []
        lost = 0
        for _ in range(count):
            if self._rng.random() < loss_rate:
                lost += 1
                continue
            latencies.append(base_latency_ms + self._rng.gauss(0.0, jitter_factor_ms))

        if latencies:
            latency_ms = sum(latencies) / len(latencies)
            jitter_ms = sum(abs(x - latency_ms) for x in latencies) / len(latencies)
        else:
            latency_ms = 0.0
            jitter_ms = 0.0

        loss_pct = (lost / count) * 100.0
        return QoSMeasurement(
            latency_ms=round(latency_ms, 4),
            jitter_ms=round(jitter_ms, 4),
            loss_pct=round(loss_pct, 4),
        )


class QoSValidator:
    """Valida uma medição de QoS contra os limiares VoIP."""

    def __init__(self, thresholds: QoSThresholds | None = None) -> None:
        self.thresholds = thresholds or QoSThresholds()

    def validate(self, measurement: QoSMeasurement) -> QoSVerdict:
        """Retorna veredito pass/fail para a medição informada.

        Cada limiar é estrito: o valor medido deve ser estritamente
        menor que o limiar para passar.
        """
        failures: list[str] = []
        if measurement.latency_ms >= self.thresholds.max_latency_ms:
            failures.append(
                f"latência {measurement.latency_ms} ms >= limiar "
                f"{self.thresholds.max_latency_ms} ms"
            )
        if measurement.jitter_ms >= self.thresholds.max_jitter_ms:
            failures.append(
                f"jitter {measurement.jitter_ms} ms >= limiar "
                f"{self.thresholds.max_jitter_ms} ms"
            )
        if measurement.loss_pct >= self.thresholds.max_loss_pct:
            failures.append(
                f"perda {measurement.loss_pct}% >= limiar "
                f"{self.thresholds.max_loss_pct}%"
            )
        return QoSVerdict(
            passed=len(failures) == 0,
            measurement=measurement,
            thresholds=self.thresholds,
            failures=failures,
        )


def evaluate(
    measurement: QoSMeasurement,
    thresholds: QoSThresholds | None = None,
) -> QoSVerdict:
    """Função de conveniência: valida medição contra limiares (padrão VoIP)."""
    return QoSValidator(thresholds).validate(measurement)
