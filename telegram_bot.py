#!/usr/bin/env python3
"""Telegram command listener for Market Kline Radar."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import requests

from scanner import (
    DEFAULT_EXCLUDED_BASES,
    Candidate,
    compact_money,
    fetch_klines,
    format_caption,
    load_dotenv,
    render_candles,
    send_telegram_photo,
    tickers,
    utc_stamp,
)


TELEGRAM_API = "https://api.telegram.org"
ALLOWED_INTERVALS = {"5m", "15m", "1h"}


def telegram_request(token: str, method: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> Any:
    response = requests.post(
        f"{TELEGRAM_API}/bot{token}/{method}",
        json=payload or {},
        timeout=timeout,
        headers={"User-Agent": "market-kline-radar-bot/0.1"},
    )
    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(f"Telegram non-JSON response: {response.text[:300]}") from exc
    if not response.ok or not data.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: HTTP {response.status_code} {data}")
    return data.get("result")


def send_message(token: str, chat_id: str, text: str) -> None:
    telegram_request(
        token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        },
    )


def set_commands(token: str) -> None:
    telegram_request(
        token,
        "setMyCommands",
        {
            "commands": [
                {"command": "top10", "description": "发送当前24h涨幅榜Top10 K线图"},
                {"command": "help", "description": "查看可用指令"},
            ]
        },
    )


def parse_top10_args(text: str, default_interval: str) -> str:
    parts = text.split()
    if len(parts) < 2:
        return default_interval
    interval = parts[1].strip().lower()
    if interval not in ALLOWED_INTERVALS:
        raise ValueError("周期只支持 5m、15m、1h，例如：/top10 15m")
    return interval


def top_gainer_candidates(exchange: str, top_n: int, excluded_bases: set[str]) -> list[Candidate]:
    rows = tickers(exchange, excluded_bases)
    volume_rank = {
        item.symbol: rank
        for rank, item in enumerate(sorted(rows, key=lambda item: item.quote_volume, reverse=True), start=1)
    }
    gainers = sorted(rows, key=lambda item: item.price_change_pct, reverse=True)[:top_n]
    return [
        Candidate(
            symbol=item.symbol,
            reason="gainer",
            rank=rank,
            volume_rank=volume_rank.get(item.symbol),
            gainer_rank=rank,
            quote_volume=item.quote_volume,
            price_change_pct=item.price_change_pct,
        )
        for rank, item in enumerate(gainers, start=1)
    ]


def send_top10(token: str, chat_id: str, args: argparse.Namespace, interval: str) -> None:
    excluded_bases = {item.strip().upper() for item in args.exclude_bases.split(",") if item.strip()}
    candidates = top_gainer_candidates(args.exchange, args.top_n, excluded_bases)
    send_message(
        token,
        chat_id,
        f"开始发送24h涨幅榜Top{len(candidates)} K线图\n周期：{interval}\n时间：{utc_stamp()}",
    )
    chart_dir = Path(args.chart_dir)
    for candidate in candidates:
        candles = fetch_klines(args.exchange, candidate.symbol, interval, args.chart_limit)
        image_path = render_candles(candidate.symbol, candles, interval, chart_dir, args.candle_width_scale)
        send_telegram_photo(token, chat_id, image_path, format_caption(candidate))
        print(
            f"[sent] {candidate.symbol} 涨幅榜 #{candidate.gainer_rank} "
            f"24h={candidate.price_change_pct:+.2f}% volume={compact_money(candidate.quote_volume)}"
        )
        time.sleep(args.sleep)


def help_text() -> str:
    return "\n".join(
        [
            "可用指令：",
            "/top10 - 发送当前24h涨幅榜Top10的K线图",
            "/top10 5m - 使用5m K线",
            "/top10 15m - 使用15m K线",
            "/top10 1h - 使用1h K线",
        ]
    )


def handle_message(token: str, allowed_chat_id: str, args: argparse.Namespace, message: dict[str, Any]) -> None:
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id") or "")
    text = str(message.get("text") or "").strip()
    if not chat_id or not text:
        return
    if chat_id != allowed_chat_id:
        send_message(token, chat_id, "这个 bot 只响应授权 chat。")
        print(f"[ignored] unauthorized chat_id={chat_id}", file=sys.stderr)
        return

    command = text.split()[0].split("@", 1)[0].lower()
    try:
        if command == "/top10":
            interval = parse_top10_args(text, args.interval)
            send_top10(token, chat_id, args, interval)
        elif command == "/help" or command == "/start":
            send_message(token, chat_id, help_text())
    except Exception as exc:  # noqa: BLE001 - report command failures to chat.
        send_message(token, chat_id, f"指令执行失败：{exc}")
        print(f"[error] command failed: {exc}", file=sys.stderr)


def poll(token: str, allowed_chat_id: str, args: argparse.Namespace) -> None:
    offset = None
    print(f"[{utc_stamp()}] Telegram command listener started.")
    while True:
        try:
            result = telegram_request(
                token,
                "getUpdates",
                {
                    "offset": offset,
                    "timeout": 30,
                    "allowed_updates": ["message"],
                },
                timeout=40,
            )
            for update in result:
                offset = int(update["update_id"]) + 1
                message = update.get("message")
                if isinstance(message, dict):
                    handle_message(token, allowed_chat_id, args, message)
        except KeyboardInterrupt:
            print("Stopped.")
            return
        except Exception as exc:  # noqa: BLE001 - keep listener alive.
            print(f"[warn] polling failed: {exc}", file=sys.stderr)
            time.sleep(5)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Listen for Telegram bot commands.")
    parser.add_argument("--register-only", action="store_true", help="Set Telegram bot commands and exit.")
    parser.add_argument("--exchange", choices=["bybit-linear", "binance-futures"], default="bybit-linear")
    parser.add_argument("--interval", choices=sorted(ALLOWED_INTERVALS), default="15m")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top gainers to send.")
    parser.add_argument("--chart-limit", type=int, default=180)
    parser.add_argument("--candle-width-scale", type=float, default=0.48)
    parser.add_argument("--chart-dir", default="charts")
    parser.add_argument("--sleep", type=float, default=0.4)
    parser.add_argument(
        "--exclude-bases",
        default=",".join(sorted(DEFAULT_EXCLUDED_BASES)),
        help="Comma-separated base assets to exclude.",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    load_dotenv(Path(__file__).resolve().with_name(".env"))
    load_dotenv(Path.cwd() / ".env")
    args = parse_args(argv)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env first.")
    set_commands(token)
    print("[ok] Telegram bot commands registered.")
    if args.register_only:
        return 0
    poll(token, chat_id, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
