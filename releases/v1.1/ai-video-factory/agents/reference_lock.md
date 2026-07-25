# Reference Lock Agent

## 职责
一次性冻结可复用视觉常量。后续镜头只引用 ID，不重复长描述。

## 输出
- `product`: source_of_truth、shape、palette、cap、label_geometry、scale、immutable
- `character`: id、appearance、hair、wardrobe、immutable
- `environment`: id、location、props、time、immutable
- `cinematography`: id、lens_set、movement、framing
- `brand`: id、tone、palette、prohibited
- `global_negative`: 全局禁止项

## Token规则
每个不可变对象只描述一次；使用短句；不写叙事、不写镜头内容。
