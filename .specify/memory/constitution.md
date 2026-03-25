# anti-slop-writer Constitution

## Core Principles / 核心原则

### I. 质量优先
输出质量是本项目的核心价值。改写结果必须比原文更自然、AI味明显降低。
当质量与速度冲突时，优先保质量。

### II. 库优先设计 (Library-First)
核心能力先设计成可调用模块，再由 CLI 封装。
支持未来 HTTP API 封装和第三方复用。

### III. 模块边界清晰
Core/CLI/Providers/Language Packs 各司其职，依赖方向严格限制。
详见 AGENTS.md Module Boundaries 部分。

## Security Constraints / 安全约束

### IV. API Key 安全
API Key 仅通过环境变量或配置文件提供，禁止硬编码到代码中。
相关配置文件不纳入版本控制。

### V. 数据隐私
用户文本仅在内存中处理，不持久化存储到本地或云端。
不记录用户文本内容，不收集遥测数据。

## Boundary Rules / 边界规则

### VI. Core 不依赖 CLI
Core 模块不依赖 CLI，保持可独立调用。
这确保核心能力可被其他应用复用。

### VII. Provider 可切换
Provider 抽象设计为可切换，不绑定单一 LLM 服务商。
当前 MVP 使用 OpenAI-compatible 协议，支持智谱 GLM 等服务商。

## Governance / 治理规则

1. Constitution 是项目的上位约束，所有 spec/plan/tasks/analyze 必须遵守
2. Constitution 修订需要明确记录修订原因和影响范围
3. 当 Constitution 与其他规则冲突时，以 Constitution 为准
4. 复杂度必须被证明必要，YAGNI 原则适用

---

**Version**: 1.0.0 | **Ratified**: 2025-03-19 | **Last Amended**: 2025-03-19
