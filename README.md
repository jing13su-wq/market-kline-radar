# Market Kline Radar

交易所短线扫盘器：只使用价格、涨幅和成交额数据，筛选有热度的 USDT 永续币种，生成纯 K 线图并推送到 Telegram bot。

默认数据源是 Bybit USDT 永续。GitHub-hosted runner 可能被交易所拒绝，所以更推荐本地电脑或 VPS 运行。

## 准备环境

```powershell
cd D:\eepic\market-kline-radar
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

编辑 `.env`：

```text
TELEGRAM_BOT_TOKEN=123456789:your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

脚本会自动读取项目根目录的 `.env`，不需要每次手动设置 `$env:`。

## 本地测试

只生成图，不推送：

```powershell
python .\scanner.py --once --dry-run --exchange bybit-linear --test-symbol SOLUSDT
```

测试 Telegram 推图：

```powershell
.\scripts\run_test.ps1
```

跑一轮正式扫描：

```powershell
.\scripts\run_once.ps1
```

前台持续循环：

```powershell
.\scripts\run_loop.ps1
```

## Windows 定时任务

如果你希望电脑开着时后台每 5 分钟扫一次：

```powershell
.\scripts\register_windows_task.ps1
```

取消定时任务：

```powershell
.\scripts\unregister_windows_task.ps1
```

注意：Windows 定时任务不能在电脑关机时运行。想不依赖本机开机，需要放到 VPS 或 GitHub self-hosted runner。

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

## 常用参数

- `--exchange`: `bybit-linear` 或 `binance-futures`，默认 `bybit-linear`
- `--interval`: K 线周期，默认 `15m`
- `--chart-limit`: K 线根数，默认 `180`
- `--candle-width-scale`: K 线实体宽度，默认 `0.48`
- `--volume-top-n`: 成交额榜前 N，默认 `40`
- `--gainer-top-n`: 涨幅榜前 N，默认 `25`
- `--min-volume-quote`: 成交额榜信号的最低 24h 成交额，默认 `50000000`
- `--min-gainer-volume-quote`: 涨幅榜信号的最低 24h 成交额，默认 `20000000`
- `--min-gain-pct`: 涨幅榜最低 24h 涨幅，默认 `12`
- `--seen-ttl-hours`: 同一币种同一触发类型的重复推送抑制时间，默认 `6`
- `--max-alerts`: 每轮最多推送图片数，默认 `8`

## GitHub Actions

仓库仍保留 `.github/workflows/market-kline-radar.yml`，但普通 GitHub-hosted runner 可能因为出口 IP 被交易所返回 403/451。要在 GitHub Actions 稳定运行，建议使用 self-hosted runner。
