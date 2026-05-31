# logs/

任务级编排日志目录。每个任务的 codex 复审内循环各写一份：

```
<YYYY-MM-DD>_<feature>_task<N>.md
```

格式见 `../assets/task-loop-log-template.md`。日志用于追溯每个任务"实现 → codex 复审 → 修复"的轮次与放行依据，便于问题排查与流程审计。
