---
name: maa代码补全
description: 基于 MaaFramework 任务流水线协议，对 Pipeline 节点进行识别算法类型推断与代码补全（不新增参数）。
---

# MaaFramework Pipeline 补全

当用户请求“补全代码”时使用本技能。

## 约束

- 仅根据用户已提供的节点参数推断识别算法类型并补全必要字段
- 默认添加 "focus": {"Node.Recognition.Succeeded": "{name}"}
- 不得新增任何其他参数；不得凭空补齐任何算法/动作参数
- 严格遵循任务流水线协议：[任务流水线协议.md]
- 补全节点代码后根据文件中其他节点的前缀为补全的节点添加名称前缀

## 算法类型推断规则

在节点未显式给出识别算法类型时，按以下优先级判断（命中即停止）：

1. `all_of` 存在：`And`
2. `any_of` 存在：`Or`
3. `custom_recognition` 存在：`Custom`
4. `lower` 与 `upper` 同时存在：`ColorMatch`
5. `model` / `onnx` 存在：
   - 路径包含 `model/detect`：`NeuralNetworkDetect`
   - 路径包含 `model/classify`：`NeuralNetworkClassify`
6. `template` / `png` 存在：
   - 存在 `detector` / `ratio` / `count`：`FeatureMatch`
   - 其余默认：`TemplateMatch`
   - 默认添加："green_mask": true
7. 以上都不满足：`OCR`

在节点未显式给出识别算法类型时，默认为`Click`

## 输出要求

- 仅补全 `recognition`（v1）或 `recognition.type`（v2）中缺失的算法类型
- 默认使用Pipeline v2协议
- 不移动、不合并、不拆分用户已给出的其他字段

## 参考文件

- 任务流水线协议.md