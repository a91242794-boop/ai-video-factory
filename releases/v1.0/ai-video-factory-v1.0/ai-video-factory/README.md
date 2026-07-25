# AI Video Factory v1.0

这是一个面向 TikTok、Mercado Libre、Amazon 等平台的产品短视频故事板 Skill。

## 当前版本范围（Sprint 1）
- 产品资料标准化
- 导演脚本
- 16镜头故事板
- 一致性控制
- GPT Image 16宫格提示词
- JSON Schema 校验
- Minoxidil 示例

## 使用方式
1. 复制 `templates/product_brief.yaml`，填写产品资料。
2. 按 `workflow.yaml` 顺序执行各 Agent。
3. 将最终 `gpt_image_prompt.md` 连同产品参考图交给 GPT Image。
4. 生成故事板后，再进入 Flow/视频动画环节。

## 推荐命令
```bash
python validate.py examples/minoxidil/storyboard.json schemas/storyboard.schema.json
```

## 目录
- `agents/`：各阶段角色与规则
- `templates/`：可复用输入输出模板
- `schemas/`：结构校验
- `examples/`：产品实例
- `outputs/`：运行结果目录
