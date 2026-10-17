"""Interface de linha de comando do validador de QoS VoIP."""

from __future__ import annotations

import argparse
import sys

from .qos import PingSimulator, QoSThresholds, evaluate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validador-qos-voip",
        description="Valida QoS de VoIP por simulação determinística (sem rede real).",
    )
    parser.add_argument("--count", type=int, default=100, help="número de pacotes simulados")
    parser.add_argument(
        "--base-latency-ms", type=float, default=40.0, help="latência base em ms"
    )
    parser.add_argument(
        "--jitter-factor-ms", type=float, default=5.0, help="fator de jitter em ms"
    )
    parser.add_argument(
        "--loss-rate", type=float, default=0.0, help="taxa de perda de pacotes de 0.0 a 1.0"
    )
    parser.add_argument("--seed", type=int, default=0, help="semente do gerador aleatório")
    parser.add_argument(
        "--max-latency-ms", type=float, default=150.0, help="limiar de latência em ms"
    )
    parser.add_argument(
        "--max-jitter-ms", type=float, default=30.0, help="limiar de jitter em ms"
    )
    parser.add_argument(
        "--max-loss-pct", type=float, default=1.0, help="limiar de perda percentual"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    thresholds = QoSThresholds(
        max_latency_ms=args.max_latency_ms,
        max_jitter_ms=args.max_jitter_ms,
        max_loss_pct=args.max_loss_pct,
    )

    simulator = PingSimulator(seed=args.seed)
    measurement = simulator.measure(
        count=args.count,
        base_latency_ms=args.base_latency_ms,
        jitter_factor_ms=args.jitter_factor_ms,
        loss_rate=args.loss_rate,
    )

    verdict = evaluate(measurement, thresholds)

    status = "PASS" if verdict.passed else "FAIL"
    print(f"Validador de QoS VoIP — resultado: {status}")
    print(
        f"  latência média : {measurement.latency_ms} ms "
        f"(limiar < {thresholds.max_latency_ms} ms)"
    )
    print(
        f"  jitter         : {measurement.jitter_ms} ms "
        f"(limiar < {thresholds.max_jitter_ms} ms)"
    )
    print(
        f"  perda          : {measurement.loss_pct}% "
        f"(limiar < {thresholds.max_loss_pct}%)"
    )
    if verdict.failures:
        print("  falhas:")
        for failure in verdict.failures:
            print(f"    - {failure}")
    return 0 if verdict.passed else 1


if __name__ == "__main__":
    sys.exit(main())
