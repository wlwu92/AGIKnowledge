---
source: "https://github.com/musistudio/claude-code-router"
created: 2026-05-11
tags: [LLM, tooling, L4]
---

# claude-code-router

> 一个路由/代理层，将 Claude Code 连接到任意 LLM 提供商（DeepSeek、Gemini、Ollama 等），而非局限于 Anthropic 原生 API。

## 关键信息

- **Stars**: ~33k | **Forks**: ~3k
- **语言**: TypeScript (pnpm monorepo)
- **最新版**: 2.0.0 (npm)
- **启动时间**: 2025 年 6 月

## 核心功能

- LLM API 转换层 — 将 Claude Code 的协议翻译为其他模型提供商的格式
- 支持 DeepSeek、Gemini、Ollama、OpenAI 等多种模型
- 支持流式响应、工具调用、thinking mode
- 提供 CLI、Server、Web UI 多个交互方式
- Docker 部署支持

## 相关项目

- [musistudio/llms](https://github.com/musistudio/llms) — 通用 LLM API 转换服务器，最初为 claude-code-router 开发
- [@wangjibins/claude-code-router](https://www.npmjs.com/package/@wangjibins/claude-code-router) — 维护中的 fork（v2.1.2），增加模型别名、一键安装等

## 注意事项

- 项目维护力度堪忧：单个维护者，~769 open issues，102 个未合并 PR
- CVE-2025-57755: v1.0.34 之前存在 CORS 配置不当可能泄露 API Key
- 用户群正从"用廉价模型替代 Claude"转向严肃的多提供商生产部署

## 分类

- **L4**: LLM 应用 / AI 工具与工作流
