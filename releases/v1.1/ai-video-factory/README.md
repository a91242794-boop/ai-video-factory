# AI Video Factory v1.1

面向 TikTok、Mercado Libre、Amazon 的低 Token 产品视频故事板 Skill。

## v1.1 新增
- Reference Lock Engine
- Storyboard Prompt DSL
- Prompt Compiler（compact / standard / strict）
- 静态 QA 与质量门槛
- 4格预览门槛
- 最小差异 Auto Revision
- SHA-256 缓存键与 Token 预算策略

## 推荐运行
```bash
python validate.py examples/minoxidil/storyboard.json schemas/storyboard.schema.json
python compiler.py \
  --dsl examples/minoxidil/storyboard.dsl.yaml \
  --lock examples/minoxidil/reference_lock.yaml \
  --mode compact \
  --output outputs/prompts/minoxidil_v1.1_compact.md

python static_qa.py \
  --dsl examples/minoxidil/storyboard.dsl.yaml \
  --brief examples/minoxidil/product_brief.yaml \
  --output outputs/report/minoxidil_v1.1_static_qa.json
```

## 成本控制顺序
```text
结构化输入
→ 本地静态检查（零模型Token）
→ 4格小样
→ 通过后生成16格
→ 仅对失败项做局部修订
```

## 目录
- `agents/`：Agent职责
- `config/`：Token、缓存和质量门槛
- `templates/`：DSL和参考锁模板
- `schemas/`：结构校验
- `examples/`：可运行示例
- `outputs/`：编译与QA结果
