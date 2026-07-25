---
name: ai-video-factory
version: 1.1.0
description: 以低Token消耗将产品资料编译为短视频导演脚本、结构化故事板、参考锁、GPT Image故事板提示词及自动修订指令。
---

# AI Video Factory v1.1

## 目标
把产品资料转换为可复用、可校验、低冗余的短视频生产资产，并通过“静态检查 → 小样 → 完整生成 → 定向修订”控制 Token 与图片生成成本。

## 触发条件
用于产品短视频脚本、TikTok/Mercado Libre/Amazon故事板、9/16/24宫格分镜、GPT Image提示词、连续性控制、批量视频素材。

## 标准工作流
1. Intake：标准化 Product Brief，只保留影响创意和合规的字段。
2. Director：输出简洁商业叙事，不写绘图长提示词。
3. Storyboard DSL：镜头只引用固定 ID，避免重复人物、场景、灯光描述。
4. Reference Lock：冻结产品、人物、环境、品牌和禁止项。
5. Static QA：先用规则检查结构、重复、产品出现时点和禁用表述，不调用模型。
6. Prompt Compiler：仅在真正生成图片前，将 DSL + Reference Lock 编译为最终提示词。
7. Preview Gate：默认先生成4格关键小样；通过后再生成16格完整版。
8. Visual QA：只描述失败项，不重复完整上下文。
9. Auto Revision：生成最小差异修订提示词，只修改失败项。

## Token效率原则
- **一次定义，多处引用**：人物、产品、环境、摄影统一放入 `reference_lock.yaml`，镜头中只写 ID。
- **分级提示词**：默认 `compact`；只有首次失败才升级 `standard`，再次失败才使用 `strict`。
- **先规则后模型**：Schema、禁词、镜头数量、重复镜头等由本地脚本完成。
- **先小样后全量**：4格小样用于人物、包装、色调锁定，避免直接浪费一次16格生成。
- **差异修订**：修图提示词只包含“保留项 + 错误项 + 修改项”，不重发整个故事板。
- **缓存复用**：输入内容哈希不变时，复用已编译 Prompt 和 QA 结果。
- **按需输出**：除非用户要求，不同时生成长脚本、逐镜头长Prompt和多语言文案。

## 核心约束
- 产品参考图是包装、颜色、结构、比例的唯一视觉来源。
- 默认故事板无字幕、无标题、无编号、无水印。
- 禁止未经证实的医疗功效、绝对承诺和虚假前后对比。
- 同一角色、服装、环境、时间、灯光必须连续。
- 每格必须能独立裁切为竖屏关键帧。

## 标准输出
- `director.yaml`
- `storyboard.dsl.yaml`
- `reference_lock.yaml`
- `compiled_prompt.md`
- `preview_prompt.md`
- `qa_static.json`
- `revision_prompt.md`（仅失败时）
