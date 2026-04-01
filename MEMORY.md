# MEMORY.md - Long-term notes

Updated: 2026-03-28

Preferences
- Communication style: 话多（verbose progress updates）
  - For any action >10s: send “开始/进度/完成” updates
  - For multi-step ops: ack each step (config write, restart, verify)
  - If blocked awaiting approval/input: notify immediately

System state (2026-03-28)
- OpenClaw version alignment: 2026.3.13 schema; removed 3.24-only keys
- Gateway: running on 127.0.0.1:18789; Dashboard/Control UI disabled
- Default model: custom-160-202-238-108-3000/gpt-5
- Telegram: groupPolicy=allowlist (empty) → groups dropped; DM OK
- memorySearch: disabled (to silence embedding warnings)

Next planned work
- QQ integration via Webhook relay (方案B) when requested
