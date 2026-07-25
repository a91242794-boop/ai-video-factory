# AVF Checkpoint Snapshot

更新时间：2026-07-26

## 当前项目状态

- 工作分支：`sprint/avf-mini-mvp`
- 远端状态：与 `origin/sprint/avf-mini-mvp` 同步
- 工作树：checkpoint 创建前干净
- 当前 HEAD：`d671b78820ea3b204eba1393b66390f63242038f`

## 当前架构

AVF 当前采用分层、可替换的模块化架构：

1. Contracts：Director、Image、Video、QA 及 Runtime Module Contract。
2. Registry：CapabilityRegistry、AdapterRegistry、ModuleRegistry。
3. Router/Optimizer：根据能力、成本、质量和历史性能选择 Provider。
4. Execution：Adapter 执行、重试、Fallback、指标记录和性能持久化。
5. Runtime：ModuleMetadata、ModuleDependency、ExecutionContext、ModuleRuntime。
6. Runtime IO：Artifact、ModuleInput、ModuleOutput、ArtifactStore、ModuleExecutor。
7. Stub 层：本地零成本 Stub Module/Adapter，用于验证流程，不调用真实模型。

当前 Pipeline Binding 流程为：

```text
ModuleRegistry
  -> ModuleRuntime.execute
  -> ModuleExecutor
  -> ModuleInput
  -> Module execution
  -> ModuleOutput
  -> ArtifactStore
```

## 已完成 Sprint

- Sprint 1：Mini MVP pipeline、项目加载、六镜头 storyboard、Prompt Compiler、静态 QA。
- Sprint 1.x：稳定性、成本策略、Provider Contract、Capability、Adapter、Execution、Fault Tolerance、Quality Intelligence、Router/Optimizer。
- Sprint 2.9：ProviderPerformanceStore 持久化，JSON 存储、版本校验和 atomic rename。
- Sprint 3.0 第一阶段：Module Contract、Module Metadata、Module Registry、Stub Module 生命周期。
- Sprint 3.0 第二阶段：ModuleRuntime、ModuleDependency、ExecutionContext、依赖拓扑和生命周期编排。
- Sprint 3.1：Artifact、ModuleInput、ModuleOutput 及运行时类型校验。
- Sprint 3.2：ModuleExecutor、ArtifactStore、ModuleRuntime Pipeline Binding 和 Stub IO 输出。

## 关键 Commit 列表

- `5f2f838` — `feat: add persistent provider performance storage`
- `13afa6b` — `feat: add modular runtime foundation`
- `5cad487` — `feat: add module runtime container`
- `4551626` — `feat: add module io contracts`
- `d671b78` — `feat: bind module runtime pipeline IO`

## 测试结果

最后一次完整验证命令：

```bash
python -m pytest -v
```

结果：`200 passed`。

## 当前 PR 状态

- PR：[Draft PR #1](https://github.com/a91242794-boop/ai-video-factory/pull/1)
- 状态：OPEN、Draft
- Base：`main`
- Head：`sprint/avf-mini-mvp`
- 当前策略：持续更新 Draft PR，不合并 `main`。

## 下一步 Sprint 3.3 计划

Sprint 3.3 尚未开始，计划包括：

- 明确模块输出到下游模块的 Artifact 选择和命名规则。
- 增加 Pipeline execution trace，记录模块状态、输入输出和失败原因。
- 将预算与质量目标接入模块执行前检查。
- 为模块执行失败增加更细粒度的错误分类和恢复策略。
- 在不绑定具体 Provider 的前提下扩展可替换执行器。

## 开发原则

- 模块化：通过清晰 Contract、Registry 和 Container 隔离职责。
- 低成本：默认 `cost=0`，优先使用本地 Stub，禁止未授权真实模型调用。
- Provider 可替换：Runtime、Provider、Adapter 和持久化边界保持松耦合。
- 兼容优先：扩展现有接口时保留既有调用路径和行为。
- 可验证：每个增量先写失败测试，再实现并运行完整回归。
