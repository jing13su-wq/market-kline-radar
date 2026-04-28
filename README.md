# Market Kline Radar

交易所短线扫盘器：只使用价格、涨幅和成交额数据，筛选有热度的 USDT 永续币种，生成纯 K 线图并推送到 Telegram bot。

默认数据源是 Bybit USDT 永续，因为 GitHub-hosted runner 访问 Binance Futures 可能返回 HTTP 451。脚本仍保留 `--exchange binance-futures`，方便你本地使用。

## 信号逻辑

1. 成交额榜新进币
   - 当前进入 24h 成交额前 `--volume-top-n`
   - 上一次扫描不在这个榜单里
   - 24h 成交额不低于 `--min-volume-quote`

2. 有成交额支撑的涨幅榜币
   - 24h 涨幅不低于 `--min-gain-pct`
   - 24h 成交额不低于 `--min-gainer-volume-quote`
   - 取涨幅榜前 `--gainer-top-n`

推送内容默认只有 K 线图和极简标题，不包含 OI、费率、均线、RSI、MACD 等任何指标。

## 本地测试

```powershell
cd D:\eepic\market-kline-radar
python .\scanner.py --once --dry-run --exchange bybit-linear
```

首次运行时，成交额榜新进币需要先建立上一轮成交额榜基线，所以通常只会看到涨幅榜候选。想让首次运行也对当前成交额榜出图，可以加：

```powershell
python .\scanner.py --once --dry-run --bootstrap-volume-alerts
```

测试 Telegram 图片链路：

```powershell
$env:TELEGRAM_BOT_TOKEN="123456789:your_bot_token"
$env:TELEGRAM_CHAT_ID="your_chat_id"
python .\scanner.py --once --test-symbol SOLUSDT
```

连续运行：

```powershell
python .\scanner.py --loop --interval-minutes 5
```

## GitHub Actions

仓库包含 `.github/workflows/market-kline-radar.yml`，默认每 5 分钟运行一次。

需要在 GitHub 仓库里配置两个 Actions secrets：

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

手动测试建议参数：

- `dry_run`: `false`
- `reset_state`: `true`
- `bootstrap_volume_alerts`: `true`
- `exchange`: `bybit-linear`
- `interval`: `15m`
- `chart_limit`: `180`
- `test_symbol`: `SOLUSDT`

测试通过后，正式运行时把 `test_symbol` 留空。

## 常用参数

- `--exchange`: `bybit-linear` 或 `binance-futures`，默认 `bybit-linear`
- `--interval`: K 线周期，默认 `15m`
- `--chart-limit`: K 线根数，默认 `180`
- `--candle-width-scale`: K 线实体宽度，默认 `0.48`；想更密可降到 `0.35`
- `--volume-top-n`: 成交额榜前 N，默认 `40`
- `--gainer-top-n`: 涨幅榜前 N，默认 `25`
- `--min-volume-quote`: 成交额榜信号的最低 24h 成交额，默认 `50000000`
- `--min-gainer-volume-quote`: 涨幅榜信号的最低 24h 成交额，默认 `20000000`
- `--min-gain-pct`: 涨幅榜最低 24h 涨幅，默认 `12`
- `--seen-ttl-hours`: 同一币种同一触发类型的重复推送抑制时间，默认 `6`
- `--max-alerts`: 每轮最多推送图片数，默认 `8`

## 项目边界

这个仓库只做交易所短线 K 线扫盘和 Telegram 推图。链上叙事看板与 DEX Screener 监控保留在 `on-chain-narrative-radar` 项目里。
