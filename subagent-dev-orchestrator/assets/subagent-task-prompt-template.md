# 子 agent 任务实现提示词模板

> 主会话用 Agent 工具新建子 agent（subagent_type 见 config.orchestration.subagent_type）时填充。

```
你负责实现单个开发任务，按下列规范直接编码。完成后只汇报改动，不要自行扩大范围。

【任务】
- 编号：T<N>
- 目标：<摘自 tasks.md>
- 验收标准：<摘自 tasks.md 验收标准>

【设计契约】（模式 A 摘自 design.md；模式 B 摘自 tasks.md 口述契约 + 需求描述原文）
- API 契约：<请求/响应字段、错误码、路径、方法>
- 数据模型：<表/字段/索引/约束>
- 模块边界：<本任务涉及的类/文件/分层>

【工程上下文】（来自 config.json）
- 代码库路径：<backend_path / frontend_path>
- 技术栈：<backend_framework / frontend_framework>
- 编码规范：<coding_standards_path>
- 坑点文档：<backend_gotchas_path / frontend_gotchas_path>
- 项目结构：<project_structure_path>

【硬约束】
1. 只实现本任务 T<N>，不改动其他任务的范围。
2. 严格遵循 design.md 的 API 契约与数据模型，不擅自改字段/错误码。
3. 遵循编码规范与坑点文档。
4. 数据库事实以 config.database 指定的 MCP（<mcp_server> / <database_name>）为准校验。

【完成后汇报】（一两段即可）
- 改动的文件清单
- 关键实现决策（幂等/事务/校验/边界处理等）
- 自测情况（如能编译/跑通）
```

> 记下该子 agent 的 ID/名称——后续 codex 复审发现的问题用 SendMessage 回传给**同一会话**修复。
