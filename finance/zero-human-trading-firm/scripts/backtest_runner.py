#!/usr/bin/env python3
"""
Backtest Runner

Minimal but hygienic backtester for vetting new strategy ideas fast.
Supports a handful of canonical strategies. Enforces strict causality,
realistic fees and slippage, and an out-of-sample split by default.

This is a first-pass filter, not a production engine. Strategies that
survive here should be re-implemented against a battle-tested library
(vectorbt, zipline, backtrader, qlib) before paper trading.

Input CSV format (header required):
    timestamp,open,high,low,close,volume

Usage:
    python backtest_runner.py --csv prices.csv --strategy sma_cross \
        --fast 20 --slow 50 --fee-bps 10 --slippage-bps 5

    python backtest_runner.py --csv prices.csv --strategy ema_cross \
        --fast 12 --slow 26 --oos-split 0.3

    python backtest_runner.py --csv prices.csv --strategy mean_revert \
        --lookback 20 --zscore 2.0
"""

import argparse
import csv
import json
import math
import statistics
import sys
from typing import Any, Dict, List, Optional, Tuple


def load_csv(path: str) -> List[Dict[str, float]]:
    rows: List[Dict[str, float]] = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "timestamp": r["timestamp"],
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r.get("volume", 0) or 0),
            })
    return rows


def sma(values: List[float], window: int) -> List[Optional[float]]:
    out: List[Optional[float]] = [None] * len(values)
    if window <= 0:
        return out
    running = 0.0
    for i, v in enumerate(values):
        running += v
        if i >= window:
            running -= values[i - window]
        if i >= window - 1:
            out[i] = running / window
    return out


def ema(values: List[float], window: int) -> List[Optional[float]]:
    out: List[Optional[float]] = [None] * len(values)
    if window <= 0 or not values:
        return out
    alpha = 2.0 / (window + 1.0)
    ema_val = values[0]
    out[0] = ema_val
    for i in range(1, len(values)):
        ema_val = alpha * values[i] + (1 - alpha) * ema_val
        out[i] = ema_val
    return out


def rolling_zscore(values: List[float], window: int) -> List[Optional[float]]:
    out: List[Optional[float]] = [None] * len(values)
    for i in range(len(values)):
        if i < window - 1:
            continue
        window_vals = values[i - window + 1: i + 1]
        mu = statistics.fmean(window_vals)
        sd = statistics.pstdev(window_vals)
        if sd == 0:
            out[i] = 0.0
        else:
            out[i] = (values[i] - mu) / sd
    return out


def signals_sma_cross(closes: List[float], fast: int, slow: int) -> List[int]:
    """+1 long, -1 short, 0 flat. Signal at bar i uses data through bar i; entry at i+1."""
    f = sma(closes, fast)
    s = sma(closes, slow)
    sig: List[int] = [0] * len(closes)
    for i in range(len(closes)):
        if f[i] is None or s[i] is None:
            continue
        sig[i] = 1 if f[i] > s[i] else -1
    return sig


def signals_ema_cross(closes: List[float], fast: int, slow: int) -> List[int]:
    f = ema(closes, fast)
    s = ema(closes, slow)
    sig: List[int] = [0] * len(closes)
    for i in range(len(closes)):
        if f[i] is None or s[i] is None:
            continue
        sig[i] = 1 if f[i] > s[i] else -1
    return sig


def signals_mean_revert(closes: List[float], lookback: int, zscore: float) -> List[int]:
    z = rolling_zscore(closes, lookback)
    sig: List[int] = [0] * len(closes)
    for i in range(len(closes)):
        if z[i] is None:
            continue
        if z[i] <= -zscore:
            sig[i] = 1
        elif z[i] >= zscore:
            sig[i] = -1
        else:
            sig[i] = 0
    return sig


def backtest(
    rows: List[Dict[str, float]],
    signals: List[int],
    fee_bps: float,
    slippage_bps: float,
) -> Dict[str, Any]:
    """Bar-on-close execution at next bar's open. Signal at bar i -> entry at bar i+1 open."""
    closes = [r["close"] for r in rows]
    opens = [r["open"] for r in rows]
    position = 0
    entry_price = 0.0
    equity = 1.0
    equity_curve = [equity]
    trade_returns: List[float] = []
    wins = 0
    losses = 0
    total_fee_cost = 0.0

    cost_per_fill = (fee_bps + slippage_bps) / 10000.0

    for i in range(len(rows) - 1):
        target = signals[i]
        exec_price = opens[i + 1]
        if target != position:
            if position != 0:
                gross_return = (exec_price - entry_price) / entry_price * position
                net_return = gross_return - cost_per_fill
                total_fee_cost += cost_per_fill
                equity *= (1 + net_return)
                trade_returns.append(net_return)
                if net_return > 0:
                    wins += 1
                else:
                    losses += 1
            if target != 0:
                entry_price = exec_price
                total_fee_cost += cost_per_fill
                equity *= (1 - cost_per_fill)
            position = target
        equity_curve.append(equity)

    if position != 0 and len(rows) >= 2:
        exec_price = closes[-1]
        gross_return = (exec_price - entry_price) / entry_price * position
        net_return = gross_return - cost_per_fill
        total_fee_cost += cost_per_fill
        equity *= (1 + net_return)
        trade_returns.append(net_return)
        if net_return > 0:
            wins += 1
        else:
            losses += 1
        equity_curve[-1] = equity

    total_return = equity - 1.0
    num_trades = len(trade_returns)
    win_rate = wins / num_trades if num_trades else 0.0

    if num_trades >= 2:
        mean_r = statistics.fmean(trade_returns)
        sd_r = statistics.pstdev(trade_returns)
        sharpe_per_trade = (mean_r / sd_r) if sd_r > 0 else 0.0
        # Annualized sharpe is overloaded without bar frequency; expose per-trade as the honest number
    else:
        mean_r = trade_returns[0] if trade_returns else 0.0
        sharpe_per_trade = 0.0

    peak = equity_curve[0]
    max_dd = 0.0
    for e in equity_curve:
        if e > peak:
            peak = e
        dd = (peak - e) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd

    return {
        "bars": len(rows),
        "trades": num_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_return": total_return,
        "ending_equity": equity,
        "sharpe_per_trade": sharpe_per_trade,
        "max_drawdown": max_dd,
        "total_fee_cost": total_fee_cost,
    }


def split_oos(rows: List[Dict[str, float]], oos_frac: float) -> Tuple[List[Dict[str, float]], List[Dict[str, float]]]:
    if oos_frac <= 0 or oos_frac >= 1:
        return rows, []
    cut = int(len(rows) * (1.0 - oos_frac))
    return rows[:cut], rows[cut:]


def run(args: argparse.Namespace) -> Dict[str, Any]:
    rows = load_csv(args.csv)
    if len(rows) < 50:
        raise SystemExit("ERROR: need at least 50 bars for a meaningful backtest")

    is_rows, oos_rows = split_oos(rows, args.oos_split)

    def run_one(subset: List[Dict[str, float]]) -> Dict[str, Any]:
        closes = [r["close"] for r in subset]
        if args.strategy == "sma_cross":
            sig = signals_sma_cross(closes, args.fast, args.slow)
        elif args.strategy == "ema_cross":
            sig = signals_ema_cross(closes, args.fast, args.slow)
        elif args.strategy == "mean_revert":
            sig = signals_mean_revert(closes, args.lookback, args.zscore)
        else:
            raise SystemExit(f"unknown strategy: {args.strategy}")
        return backtest(subset, sig, args.fee_bps, args.slippage_bps)

    report: Dict[str, Any] = {
        "strategy": args.strategy,
        "params": {
            "fast": args.fast,
            "slow": args.slow,
            "lookback": args.lookback,
            "zscore": args.zscore,
            "fee_bps": args.fee_bps,
            "slippage_bps": args.slippage_bps,
            "oos_split": args.oos_split,
        },
        "in_sample": run_one(is_rows),
    }
    if oos_rows:
        report["out_of_sample"] = run_one(oos_rows)
    return report


def format_report(report: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"Strategy: {report['strategy']}")
    lines.append(f"Params: {report['params']}")
    for section in ("in_sample", "out_of_sample"):
        if section not in report:
            continue
        r = report[section]
        lines.append("")
        lines.append(f"--- {section.upper()} ---")
        lines.append(f"  bars:              {r['bars']}")
        lines.append(f"  trades:            {r['trades']} (W {r['wins']} / L {r['losses']})")
        lines.append(f"  win rate:          {r['win_rate']:.2%}")
        lines.append(f"  total return:      {r['total_return']:+.2%}")
        lines.append(f"  ending equity:     {r['ending_equity']:.4f}")
        lines.append(f"  sharpe per trade:  {r['sharpe_per_trade']:.3f}")
        lines.append(f"  max drawdown:      {r['max_drawdown']:.2%}")
        lines.append(f"  total fee drag:    {r['total_fee_cost']:.4f}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Minimal causal backtester")
    p.add_argument("--csv", required=True, help="OHLCV csv path")
    p.add_argument("--strategy", required=True, choices=["sma_cross", "ema_cross", "mean_revert"])
    p.add_argument("--fast", type=int, default=20, help="fast window (sma/ema_cross)")
    p.add_argument("--slow", type=int, default=50, help="slow window (sma/ema_cross)")
    p.add_argument("--lookback", type=int, default=20, help="lookback window (mean_revert)")
    p.add_argument("--zscore", type=float, default=2.0, help="entry threshold (mean_revert)")
    p.add_argument("--fee-bps", type=float, default=10.0, help="fee in basis points per fill")
    p.add_argument("--slippage-bps", type=float, default=5.0, help="slippage in basis points per fill")
    p.add_argument("--oos-split", type=float, default=0.3, help="fraction reserved for out-of-sample (0 to disable)")
    p.add_argument("--format", default="text", choices=["text", "json"])
    args = p.parse_args()

    report = run(args)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
