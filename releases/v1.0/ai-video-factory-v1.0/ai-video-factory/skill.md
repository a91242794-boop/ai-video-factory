---
name: ai-video-factory
version: 1.0.0
description: 将产品资料转化为短视频导演脚本、16镜头故事板、统一一致性规范和GPT Image故事板提示词。
---

# AI Video Factory

## 目标
把产品图片、卖点、平台、市场与受众，转换为可直接用于 GPT Image 生成16宫格故事板的标准化生产资料。

## 触发条件
当用户提出以下任务时使用本 Skill：
- 产品短视频脚本
- TikTok / Mercado Libre / Amazon 故事板
- 9/16/24宫格分镜
- GPT Image 故事板提示词
- 视频人物、产品、环境一致性控制
- 批量生成短视频素材

## 输入
优先读取 `templates/product_brief.yaml` 格式。资料不足时，只补充会影响结果的关键字段；其余字段采用明确默认值。

## 工作流
1. 读取 Product Brief。
2. 执行 Director Agent，生成故事主线、钩子、情绪曲线、CTA 与镜头结构。
3. 执行 Storyboard Agent，将结构扩展为16个可视化镜头。
4. 执行 Consistency Agent，冻结人物、产品、环境、灯光、镜头和品牌规范。
5. 执行 GPT Image Agent，生成：
   - 一条完整16宫格故事板提示词；
   - 每格独立提示词；
   - 负面约束；
   - 画幅和排版要求。
6. 使用 `schemas/` 校验输出结构。
7. 输出到 `outputs/`，不得覆盖用户原始资料。

## 核心原则
- 产品外观、包装、颜色、Logo、比例必须以参考图为准。
- 同一视频内人物、服装、环境、时间、光线保持连续。
- 镜头必须服务于：停留、理解、信任、转化。
- 禁止未经依据的医疗功效、绝对化承诺和虚假前后对比。
- 默认无文字故事板；字幕、价格、CTA在后期单独叠加。
- 生成前先检查产品尺寸与人物/场景比例。

## 标准输出文件
- `director.yaml`
- `storyboard.yaml`
- `consistency.yaml`
- `gpt_image_prompt.md`
- `storyboard.json`
- `qa_report.md`

## 默认镜头结构（16镜头）
1. 强钩子
2. 痛点识别
3. 痛点放大
4. 情绪反应
5. 产品首次出现
6. 包装/结构展示
7. 产品质感
8. 第一步使用
9. 核心使用动作
10. 功能机理视觉化
11. 关键卖点证明
12. 使用体验
13. 场景收益
14. 情绪逆转
15. 产品英雄镜头
16. CTA结尾镜头

## 模型适配
本 Skill 以 GPT Image 为主要故事板生成器。后续视频模型只读取已冻结的 Storyboard 与 Consistency，不重新解释产品。
