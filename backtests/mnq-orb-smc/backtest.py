"""
MNQ ORB backtester — baseline vs improved.

Runs locally on an OHLCV CSV you export from your broker / TradingView.
Models ONLY the ORB leg (the SMC leg depends on TradingView's tvta volume
delta which isn't reproducible outside TV). If you want SMC modeled too,
swap in your own up/down-volume series in the CSV.

USAGE
-----
    python3 backtest.py --csv mnq_5m.csv

CSV FORMAT
----------
Required columns (case-insensitive, any order):
    datetime,open,high,low,close,volume

`datetime` must parse as a timezone-aware or US/Eastern-local timestamp.
If your CSV is UTC, pass --tz-in UTC. Market-session logic runs in
America/New_York.

OUTPUT
------
Prints a before/after table and writes equity curves to equity_*.csv.
"""
from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass, field
from datetime import datetime, time as dtime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


NY = ZoneInfo("America/New_York")


# --- Config --------------------------------------------------------------

@dataclass
class Config:
    # Session
    orb_start: dtime = dtime(9, 30)
    orb_end: dtime = dtime(9, 35)      # baseline 5-min; improved will override
    sess_end: dtime = dtime(11, 0)

    # Trade rules (percent of ORB range)
    tp1_pct: float = 50.0
    tp2_pct: float = 75.0
    sl_pct: float = 100.0
    min_orb_pct: float = 0.0
    max_orb_pct: float = 0.5

    # Sizing / risk
    contracts: int = 2                 # total; split 1/1 between TP1/TP2
    dollar_per_point: float = 2.0      # MNQ = $2 / point / contract
    max_loss_dollars: float = 300.0

    # Trade days (Mon=0..Fri=4)
    trade_days: tuple = (0, 1, 2, 3, 4)

    # Filters
    use_volume_filter: bool = True
    volume_ma_len: int = 20
    volume_mult: float = 1.2

    # Improvements (off in baseline)
    use_regime_filter: bool = False
    use_kill_switch: bool = False
    use_atr_floor: bool = False

    # Misc
    slippage_points: float = 0.5       # one-way, per contract leg
    commission_per_contract: float = 0.0


# Canonical baseline and improved configs.
def baseline_cfg() -> Config:
    return Config()

def improved_cfg() -> Config:
    return Config(
        orb_end=dtime(9, 45),   # 15-min ORB
        tp1_pct=100.0,
        tp2_pct=150.0,
        sl_pct=100.0,
        use_regime_filter=True,
        use_kill_switch=True,
        use_atr_floor=True,
    )


# --- Data loading --------------------------------------------------------

def load_csv(path: Path, tz_in: str | None) -> pd.DataFrame:
    """
    Accepts:
      - TradingView native export (columns: time, open, high, low, close, Volume, ...)
        `time` can be Unix seconds or ISO 8601.
      - Generic OHLCV (datetime, open, high, low, close, volume).
    Extra columns (Volume MA, indicators, etc.) are ignored.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    # Normalize timestamp column
    ts_col = next((c for c in ("datetime", "time", "date") if c in df.columns), None)
    if ts_col is None:
        raise SystemExit(f"CSV missing timestamp column (expected 'datetime' or 'time'). Got {list(df.columns)}")
    if ts_col != "datetime":
        df = df.rename(columns={ts_col: "datetime"})

    need = {"datetime", "open", "high", "low", "close"}
    missing = need - set(df.columns)
    if missing:
        raise SystemExit(f"CSV missing columns: {missing}. Got {list(df.columns)}")
    if "volume" not in df.columns:
        print("WARNING: 'volume' column missing from CSV — volume filter will be disabled for this run.")
        df["volume"] = 0.0

    # Parse timestamps: Unix epoch (int/float) or ISO string
    s = df["datetime"]
    try:
        as_num = pd.to_numeric(s, errors="raise")
        # TradingView epoch exports are seconds. Heuristic: > 10^12 is ms, > 10^10 is s.
        unit = "s" if as_num.max() < 1e12 else "ms"
        df["datetime"] = pd.to_datetime(as_num, unit=unit, utc=True)
    except Exception:
        df["datetime"] = pd.to_datetime(s, utc=(tz_in == "UTC"), errors="coerce")

    if df["datetime"].dt.tz is None:
        # Naive string parse: localize per --tz-in or default NY
        df["datetime"] = df["datetime"].dt.tz_localize(tz_in or str(NY))
    elif tz_in and tz_in != "UTC" and "utc" in str(df["datetime"].dt.tz).lower():
        # Caller insists on a specific TZ for a naive-looking stamp that parsed as UTC
        df["datetime"] = df["datetime"].dt.tz_convert(tz_in)

    df["datetime"] = df["datetime"].dt.tz_convert(NY)
    df = df.sort_values("datetime").reset_index(drop=True)
    for c in ("open", "high", "low", "close", "volume"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["datetime", "open", "high", "low", "close", "volume"]).reset_index(drop=True)
    return df


# --- Indicators ----------------------------------------------------------

def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()

def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h - l).abs(), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(length).mean()


# --- Trade model ---------------------------------------------------------

@dataclass
class Trade:
    entry_dt: datetime
    side: str                 # "long" | "short"
    entry_px: float
    stop_px: float
    tp1_px: float
    tp2_px: float
    contracts: int
    exit_dt: datetime | None = None
    exit_px_tp1: float | None = None
    exit_px_tp2: float | None = None
    exit_reason: str = ""     # TP1, TP2, SL, SESSION_FLAT, or mixed "TP1+SL"
    pnl_dollars: float = 0.0


# --- Backtest engine -----------------------------------------------------

def backtest(df: pd.DataFrame, cfg: Config) -> tuple[list[Trade], pd.DataFrame]:
    # Precompute indicators
    df = df.copy()
    # Auto-disable volume filter if the CSV has no usable volume data
    if cfg.use_volume_filter and (df["volume"].fillna(0).max() <= 0):
        cfg = Config(**{**cfg.__dict__, "use_volume_filter": False})
    df["vol_ma"] = df["volume"].shift(1).rolling(cfg.volume_ma_len).mean()
    df["atr14"] = atr(df, 14)
    # 15-min HTF EMA20 — resample close to 15m, EMA, forward-fill back to 5m
    close_15 = df.set_index("datetime")["close"].resample("15min").last().dropna()
    ema15 = ema(close_15, 20)
    df["htf_ema20"] = df["datetime"].map(ema15.reindex(df["datetime"], method="ffill"))

    df["date"] = df["datetime"].dt.date
    df["t"] = df["datetime"].dt.time
    df["dow"] = df["datetime"].dt.dayofweek

    trades: list[Trade] = []
    equity = []
    cum_pnl = 0.0

    # Group by trading day
    for date, day in df.groupby("date", sort=True):
        day = day.reset_index(drop=True)
        if day["dow"].iloc[0] not in cfg.trade_days:
            continue

        # ORB window
        orb_mask = (day["t"] >= cfg.orb_start) & (day["t"] < cfg.orb_end)
        orb_bars = day[orb_mask]
        if len(orb_bars) == 0:
            continue
        orb_high = orb_bars["high"].max()
        orb_low = orb_bars["low"].min()
        orb_size = orb_high - orb_low
        if orb_low <= 0 or orb_size <= 0:
            continue
        orb_pct = orb_size / orb_low * 100.0
        if orb_pct < cfg.min_orb_pct or orb_pct > cfg.max_orb_pct:
            continue

        # Post-ORB session bars
        sess_mask = (day["t"] >= cfg.orb_end) & (day["t"] < cfg.sess_end)
        sess = day[sess_mask].reset_index(drop=True)
        if len(sess) == 0:
            continue

        traded = False
        open_trade: Trade | None = None
        tp1_hit = False
        day_losses = 0
        day_pnl = 0.0
        kill = False

        prev_close = None  # close of previous bar (for breakout confirmation)
        for i, bar in sess.iterrows():
            # Try to fill open trade on this bar
            if open_trade is not None:
                filled = _advance_open(open_trade, bar, tp1_hit, cfg)
                if filled is not None:
                    tp1_hit, closed = filled
                    if closed:
                        trades.append(open_trade)
                        pnl = open_trade.pnl_dollars
                        cum_pnl += pnl
                        day_pnl += pnl
                        if pnl < 0:
                            day_losses += 1
                        if cfg.use_kill_switch and (day_losses >= 2 or day_pnl <= -2 * cfg.max_loss_dollars):
                            kill = True
                        open_trade = None
                        tp1_hit = False

            # Look for a new entry only if flat and not already traded today and not killed
            if open_trade is None and not traded and not kill:
                # Volume filter
                vol_ok = True
                if cfg.use_volume_filter and not pd.isna(bar["vol_ma"]):
                    vol_ok = bar["volume"] > bar["vol_ma"] * cfg.volume_mult

                # Regime filter
                long_regime_ok = True
                short_regime_ok = True
                if cfg.use_regime_filter and not pd.isna(bar["htf_ema20"]):
                    long_regime_ok = bar["close"] > bar["htf_ema20"]
                    short_regime_ok = bar["close"] < bar["htf_ema20"]

                # Breakout triggers on close crossing ORB, with prior close on the other side
                long_trig = (bar["close"] > orb_high and prev_close is not None and prev_close <= orb_high)
                short_trig = (bar["close"] < orb_low and prev_close is not None and prev_close >= orb_low)

                side = None
                if long_trig and vol_ok and long_regime_ok:
                    side = "long"
                elif short_trig and vol_ok and short_regime_ok:
                    side = "short"

                if side is not None:
                    # Stop distance
                    stop_raw = orb_size * cfg.sl_pct / 100.0
                    if cfg.use_atr_floor and not pd.isna(bar["atr14"]):
                        stop_raw = max(stop_raw, 0.5 * bar["atr14"])
                    max_stop = cfg.max_loss_dollars / (cfg.contracts * cfg.dollar_per_point)
                    stop_d = min(stop_raw, max_stop)

                    entry_px = bar["close"]
                    if side == "long":
                        stop_px = entry_px - stop_d
                        tp1_px = entry_px + orb_size * cfg.tp1_pct / 100.0
                        tp2_px = entry_px + orb_size * cfg.tp2_pct / 100.0
                    else:
                        stop_px = entry_px + stop_d
                        tp1_px = entry_px - orb_size * cfg.tp1_pct / 100.0
                        tp2_px = entry_px - orb_size * cfg.tp2_pct / 100.0

                    # Apply entry slippage
                    slip = cfg.slippage_points * (1 if side == "long" else -1)
                    entry_fill = entry_px + slip
                    open_trade = Trade(
                        entry_dt=bar["datetime"], side=side, entry_px=entry_fill,
                        stop_px=stop_px, tp1_px=tp1_px, tp2_px=tp2_px,
                        contracts=cfg.contracts,
                    )
                    traded = True
                    tp1_hit = False

            prev_close = bar["close"]

        # End-of-session flat
        if open_trade is not None:
            last_bar = sess.iloc[-1]
            _close_at_market(open_trade, last_bar["close"], tp1_hit, cfg, reason="SESSION_FLAT")
            trades.append(open_trade)
            cum_pnl += open_trade.pnl_dollars

        equity.append({"date": date, "cum_pnl": cum_pnl})

    equity_df = pd.DataFrame(equity)
    return trades, equity_df


def _advance_open(tr: Trade, bar, tp1_hit: bool, cfg: Config) -> tuple[bool, bool] | None:
    """
    Mutate `tr` with any fills that happen inside `bar`. Returns (tp1_hit_new, closed).
    Pessimistic tie-break: if a bar's range spans both TP and SL, SL fills first.
    """
    h, l = bar["high"], bar["low"]
    slip = cfg.slippage_points
    if tr.side == "long":
        sl_hit = l <= tr.stop_px
        tp1_h = h >= tr.tp1_px
        tp2_h = h >= tr.tp2_px

        if tp1_h and sl_hit:
            # worst case: SL first on the unfilled half, TP1 on the other
            # if TP1 already hit in a prior bar we only have 1 contract left
            if not tp1_hit:
                _book_leg(tr, 1, tr.tp1_px - slip, "TP1")
                _book_leg(tr, 1, tr.stop_px - slip, "SL")
                return (True, True)
            else:
                _book_leg(tr, 1, tr.stop_px - slip, "SL")
                tr.exit_reason = (tr.exit_reason + "+SL").strip("+")
                tr.exit_dt = bar["datetime"]
                return (True, True)
        if sl_hit:
            remaining = tr.contracts - (1 if tp1_hit else 0)
            _book_leg(tr, remaining, tr.stop_px - slip, "SL")
            tr.exit_dt = bar["datetime"]
            return (tp1_hit, True)
        if tp2_h and tp1_hit:
            _book_leg(tr, 1, tr.tp2_px - slip, "TP2")
            tr.exit_dt = bar["datetime"]
            return (True, True)
        if tp1_h and not tp1_hit:
            _book_leg(tr, 1, tr.tp1_px - slip, "TP1")
            # breakeven stop on remaining runner
            tr.stop_px = max(tr.stop_px, tr.entry_px)
            return (True, False)
    else:
        sl_hit = h >= tr.stop_px
        tp1_h = l <= tr.tp1_px
        tp2_h = l <= tr.tp2_px

        if tp1_h and sl_hit:
            if not tp1_hit:
                _book_leg(tr, 1, tr.tp1_px + slip, "TP1")
                _book_leg(tr, 1, tr.stop_px + slip, "SL")
                return (True, True)
            else:
                _book_leg(tr, 1, tr.stop_px + slip, "SL")
                tr.exit_reason = (tr.exit_reason + "+SL").strip("+")
                tr.exit_dt = bar["datetime"]
                return (True, True)
        if sl_hit:
            remaining = tr.contracts - (1 if tp1_hit else 0)
            _book_leg(tr, remaining, tr.stop_px + slip, "SL")
            tr.exit_dt = bar["datetime"]
            return (tp1_hit, True)
        if tp2_h and tp1_hit:
            _book_leg(tr, 1, tr.tp2_px + slip, "TP2")
            tr.exit_dt = bar["datetime"]
            return (True, True)
        if tp1_h and not tp1_hit:
            _book_leg(tr, 1, tr.tp1_px + slip, "TP1")
            tr.stop_px = min(tr.stop_px, tr.entry_px)
            return (True, False)
    return (tp1_hit, False)


def _close_at_market(tr: Trade, px: float, tp1_hit: bool, cfg: Config, reason: str) -> None:
    slip = cfg.slippage_points
    remaining = tr.contracts - (1 if tp1_hit else 0)
    if tr.side == "long":
        _book_leg(tr, remaining, px - slip, reason)
    else:
        _book_leg(tr, remaining, px + slip, reason)
    tr.exit_reason = (tr.exit_reason + "+" + reason).strip("+") if tr.exit_reason else reason


def _book_leg(tr: Trade, qty: int, exit_px: float, tag: str) -> None:
    if qty <= 0:
        return
    if tr.side == "long":
        pnl_pts = exit_px - tr.entry_px
    else:
        pnl_pts = tr.entry_px - exit_px
    tr.pnl_dollars += pnl_pts * qty * 2.0  # MNQ $2/point
    tr.pnl_dollars -= qty * 0.0            # commission hook
    tr.exit_reason = (tr.exit_reason + "+" + tag).strip("+") if tr.exit_reason else tag


# --- Reporting -----------------------------------------------------------

def metrics(trades: list[Trade], equity: pd.DataFrame) -> dict:
    if not trades:
        return {"trades": 0, "net_pnl": 0, "win_rate": 0, "profit_factor": 0,
                "avg_win": 0, "avg_loss": 0, "max_dd": 0, "expectancy": 0, "sharpe": 0}
    pnls = [t.pnl_dollars for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    net = sum(pnls)
    pf = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else float("inf")
    win_rate = 100 * len(wins) / len(pnls)
    avg_w = sum(wins) / len(wins) if wins else 0
    avg_l = sum(losses) / len(losses) if losses else 0
    exp = sum(pnls) / len(pnls)

    # Drawdown on cumulative
    cum = equity["cum_pnl"].to_numpy() if not equity.empty else []
    max_dd = 0.0
    peak = -1e18
    for v in cum:
        peak = max(peak, v)
        dd = peak - v
        if dd > max_dd:
            max_dd = dd

    # Daily returns (crude Sharpe)
    if not equity.empty and len(equity) > 1:
        daily = equity["cum_pnl"].diff().dropna()
        mean = daily.mean()
        std = daily.std(ddof=1)
        sharpe = (mean / std * math.sqrt(252)) if std > 0 else 0.0
    else:
        sharpe = 0.0

    return {"trades": len(pnls), "net_pnl": net, "win_rate": win_rate,
            "profit_factor": pf, "avg_win": avg_w, "avg_loss": avg_l,
            "max_dd": max_dd, "expectancy": exp, "sharpe": sharpe}


def fmt(m: dict) -> str:
    return (f"  trades         {m['trades']:>8}\n"
            f"  net P/L $      {m['net_pnl']:>8.2f}\n"
            f"  win rate       {m['win_rate']:>7.1f}%\n"
            f"  profit factor  {m['profit_factor']:>8.2f}\n"
            f"  expectancy/tr  {m['expectancy']:>8.2f}\n"
            f"  avg win $      {m['avg_win']:>8.2f}\n"
            f"  avg loss $     {m['avg_loss']:>8.2f}\n"
            f"  max DD $       {m['max_dd']:>8.2f}\n"
            f"  sharpe (daily) {m['sharpe']:>8.2f}\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="OHLCV 5-min CSV")
    ap.add_argument("--tz-in", default=None, help="Source timezone (e.g. UTC). Omit if already NY.")
    ap.add_argument("--out-dir", default=".", help="Where to write equity curves")
    args = ap.parse_args()

    df = load_csv(Path(args.csv), args.tz_in)
    print(f"Loaded {len(df)} rows, {df['datetime'].iloc[0]} → {df['datetime'].iloc[-1]}")

    base = baseline_cfg()
    impr = improved_cfg()

    print("\n=== BASELINE (original defaults) ===")
    t_b, eq_b = backtest(df, base)
    m_b = metrics(t_b, eq_b)
    print(fmt(m_b))

    print("=== IMPROVED (TP1=100%, TP2=150%, ORB=15m, pyramiding=1, regime+kill+ATR) ===")
    t_i, eq_i = backtest(df, impr)
    m_i = metrics(t_i, eq_i)
    print(fmt(m_i))

    print("=== DELTA (improved − baseline) ===")
    print(f"  net P/L        {m_i['net_pnl'] - m_b['net_pnl']:+.2f}")
    print(f"  trades         {m_i['trades'] - m_b['trades']:+d}")
    print(f"  win rate       {m_i['win_rate'] - m_b['win_rate']:+.1f}%")
    print(f"  profit factor  {m_i['profit_factor'] - m_b['profit_factor']:+.2f}")
    print(f"  max DD         {m_i['max_dd'] - m_b['max_dd']:+.2f}")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    eq_b.to_csv(out / "equity_baseline.csv", index=False)
    eq_i.to_csv(out / "equity_improved.csv", index=False)
    _dump_trades(t_b, out / "trades_baseline.csv")
    _dump_trades(t_i, out / "trades_improved.csv")
    print(f"\nWrote equity curves and trade logs to {out.resolve()}")


def _dump_trades(trades: list[Trade], path: Path) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entry_dt", "side", "entry_px", "stop_px", "tp1_px", "tp2_px",
                    "exit_dt", "exit_reason", "pnl_dollars"])
        for t in trades:
            w.writerow([t.entry_dt, t.side, t.entry_px, t.stop_px, t.tp1_px, t.tp2_px,
                        t.exit_dt, t.exit_reason, round(t.pnl_dollars, 2)])


if __name__ == "__main__":
    main()
