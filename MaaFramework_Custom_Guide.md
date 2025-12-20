# MaaFramework Custom用法与Python API调用指南

## 1. 概述

### 1.1 MaaFramework简介
MaaFramework是基于图像识别技术的自动化黑盒测试框架，具备低代码、高扩展性的特点。它能够帮助开发者轻松编写出高质量的黑盒测试程序，广泛应用于自动化测试、游戏辅助、UI自动化等领域。

### 1.2 Custom功能的作用和优势
Custom功能是MaaFramework的核心扩展机制，允许开发者通过Python编写自定义的识别逻辑和动作，实现框架本身不支持的复杂功能。

**优势：**
- 高度灵活：可根据需求实现任意识别和动作逻辑
- 易于集成：与现有Python生态无缝对接
- 强大的上下文管理：支持复杂的状态维护和任务调度
- 良好的性能：基于MaaFramework的高性能识别引擎

### 1.3 适用场景
- 复杂的图像识别需求
- 需要调用外部API或服务的场景
- 自定义的交互逻辑
- 特殊的UI操作
- 复杂的状态管理

## 2. 核心概念

### 2.1 自定义识别（CustomRecognition）
自定义识别是MaaFramework中用于实现图像识别逻辑的扩展机制。开发者可以通过继承`CustomRecognition`基类，实现自己的识别算法，或者结合框架提供的识别能力实现复杂的识别逻辑。

### 2.2 自定义动作（CustomAction）
自定义动作是MaaFramework中用于实现交互逻辑的扩展机制。开发者可以通过继承`CustomAction`基类，实现自定义的动作，如点击、滑动、输入等，或者调用外部服务。

### 2.3 上下文管理（Context）
上下文是贯穿整个任务执行过程的状态管理器，包含了任务的配置、识别结果、控制器等信息。开发者可以通过上下文访问和修改任务状态，实现复杂的逻辑控制。

### 2.4 代理服务（AgentServer）
代理服务是MaaFramework中连接Python代码和核心框架的桥梁，负责处理两者之间的通信。开发者需要通过代理服务注册自定义组件，并启动服务。

## 3. Python API基础

### 3.1 环境搭建

#### 3.1.1 安装MaaFramework Python包
```bash
# 通过pip安装MaaFramework Python包
pip install maa-framework
```

#### 3.1.2 配置依赖项
MaaFramework依赖以下库：
- opencv-python
- numpy
- protobuf

可以通过以下命令安装：
```bash
pip install opencv-python numpy protobuf
```

### 3.2 核心模块导入

```python
# 导入核心模块
from maa.agent.agent_server import AgentServer  # 代理服务器，用于与MAA主程序通信
from maa.custom_recognition import CustomRecognition  # 自定义识别基类
from maa.custom_action import CustomAction  # 自定义动作基类
from maa.context import Context  # 上下文管理类
from maa.toolkit import Toolkit  # 工具类，用于初始化和配置
```

## 4. Custom语法用法详解

### 4.1 自定义识别（CustomRecognition）

#### 4.1.1 类定义与装饰器

```python
@AgentServer.custom_recognition("MyCustomRecognition")
class MyCustomRecognition(CustomRecognition):
    """自定义识别类，实现图像识别逻辑"""
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # 识别逻辑实现
        pass
```

**参数说明：**
- `@AgentServer.custom_recognition(name)`：装饰器，用于注册自定义识别组件，`name`为组件名称，在JSON配置中使用。
- `context`：上下文对象，包含任务状态和配置。
- `argv`：识别参数，包含当前帧图像等信息。
- `return`：返回识别结果，包含边界框和详细信息。

#### 4.1.2 analyze方法参数详解

- `context: Context`：
  - 提供任务执行的上下文环境
  - 包含识别器、控制器等核心组件
  - 支持覆盖流水线配置和后续任务

- `argv: CustomRecognition.AnalyzeArg`：
  - `image`：当前帧图像，格式为numpy数组
  - `node_name`：当前节点名称
  - 其他识别相关参数

#### 4.1.3 识别结果处理

```python
# 执行识别任务
reco_detail = context.run_recognition(
    "MyCustomOCR",  # 识别任务名称
    argv.image,  # 当前帧图像
    pipeline_override={"MyCustomOCR": {"roi": [100, 100, 200, 300]}}  # 临时覆盖ROI配置
)

if reco_detail and reco_detail.hit:
    # 识别成功，处理结果
    box = reco_detail.best_result.box  # 获取最佳识别结果的边界框
    score = reco_detail.best_result.score  # 获取识别置信度
    detail = reco_detail.best_result.detail  # 获取识别详细信息
    
    # 执行后续操作
    context.tasker.controller.post_click(box[0], box[1]).wait()  # 点击识别到的位置
```

#### 4.1.4 上下文操作

```python
# 覆盖流水线配置（全局生效）
context.override_pipeline({
    "MyCustomOCR": {
        "roi": [1, 1, 114, 514],
        "other_param": "value"
    }
})

# 覆盖当前节点的后续任务
context.override_next(argv.node_name, ["TaskA", "TaskB"])

# 克隆上下文（局部生效）
new_context = context.clone()
new_context.override_pipeline({
    "MyCustomOCR": {"roi": [100, 200, 300, 400]}
})

# 使用克隆的上下文执行识别
reco_detail = new_context.run_recognition("MyCustomOCR", argv.image)
```

### 4.2 自定义动作（CustomAction）

#### 4.2.1 类定义与装饰器

```python
@AgentServer.custom_action("MyCustomAction")
class MyCustomAction(CustomAction):
    """自定义动作类，实现交互逻辑"""
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        # 动作逻辑实现
        return True
```

**参数说明：**
- `@AgentServer.custom_action(name)`：装饰器，用于注册自定义动作组件，`name`为组件名称，在JSON配置中使用。
- `context`：上下文对象，包含任务状态和配置。
- `argv`：动作参数，包含当前任务状态等信息。
- `return`：返回动作执行结果，`True`表示成功，`False`表示失败。

#### 4.2.2 run方法参数详解

- `context: Context`：
  - 提供任务执行的上下文环境
  - 包含识别器、控制器等核心组件
  - 支持覆盖流水线配置和后续任务

- `argv: CustomAction.RunArg`：
  - `node_name`：当前节点名称
  - 其他动作相关参数

#### 4.2.3 动作执行逻辑

```python
def run(
    self,
    context: Context,
    argv: CustomAction.RunArg,
) -> bool:
    print(f"[MyCustomAction] 执行动作，节点名称：{argv.node_name}")
    
    # 执行点击操作
    click_job = context.tasker.controller.post_click(100, 200)
    click_job.wait()  # 等待点击完成
    
    # 执行滑动操作
    swipe_job = context.tasker.controller.post_swipe(100, 200, 300, 400, 500)  # 500ms滑动时间
    swipe_job.wait()  # 等待滑动完成
    
    # 调用外部API
    import requests
    response = requests.get("https://api.example.com/data")
    if response.status_code == 200:
        data = response.json()
        print(f"[MyCustomAction] 获取外部数据成功：{data}")
    
    # 返回执行结果
    return True
```

## 5. 代理服务启动与管理

### 5.1 代理服务启动

```python
import sys
from maa.toolkit import Toolkit
from maa.agent.agent_server import AgentServer


def main():
    # 初始化工具包，加载配置
    Toolkit.init_option("./")
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("Usage: python agent_main.py <socket_id>")
        print("socket_id 由 AgentIdentifier 提供")
        exit(1)
    
    # 获取socket_id
    socket_id = sys.argv[-1]
    
    # 启动代理服务
    AgentServer.start_up(socket_id)
    
    # 等待服务结束
    AgentServer.join()
    
    # 关闭服务
    AgentServer.shut_down()


if __name__ == "__main__":
    main()
```

### 5.2 代理服务工作流程

1. 初始化工具包，加载配置
2. 获取socket_id，用于与MAA主程序通信
3. 启动代理服务，注册自定义组件
4. 等待主程序连接，处理识别和动作请求
5. 服务结束，释放资源

## 6. 实例教程

### 6.1 基础示例：简单的自定义识别

```python
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("SimpleRecognition")
class SimpleRecognition(CustomRecognition):
    """简单的自定义识别示例"""
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # 执行OCR识别
        reco_detail = context.run_recognition(
            "MyOCR",  # OCR识别任务名称
            argv.image,  # 当前帧图像
            pipeline_override={"MyOCR": {"roi": [50, 50, 300, 100]}}  # OCR区域
        )
        
        if reco_detail and reco_detail.hit:
            # 识别成功，返回结果
            box = reco_detail.best_result.box
            text = reco_detail.best_result.detail
            
            print(f"[SimpleRecognition] OCR识别成功：{text}，位置：{box}")
            
            return CustomRecognition.AnalyzeResult(
                box=box,
                detail=f"识别到文本：{text}"
            )
        else:
            # 识别失败
            print("[SimpleRecognition] OCR识别失败")
            
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail="未识别到文本"
            )
```

### 6.2 基础示例：简单的自定义动作

```python
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context


@AgentServer.custom_action("SimpleAction")
class SimpleAction(CustomAction):
    """简单的自定义动作示例"""
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        print(f"[SimpleAction] 执行自定义动作，节点：{argv.node_name}")
        
        # 执行一系列点击操作
        click_positions = [(100, 200), (300, 400), (500, 600)]
        
        for x, y in click_positions:
            print(f"[SimpleAction] 点击位置：({x}, {y})")
            context.tasker.controller.post_click(x, y).wait()
        
        # 执行滑动操作
        print("[SimpleAction] 执行滑动操作")
        context.tasker.controller.post_swipe(100, 200, 500, 200, 1000).wait()
        
        print("[SimpleAction] 动作执行完成")
        return True
```

### 6.3 进阶示例：复杂的上下文管理

```python
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("ComplexRecognition")
class ComplexRecognition(CustomRecognition):
    """复杂的自定义识别示例，结合上下文管理"""
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # 1. 第一次识别：查找目标按钮
        button_reco = context.run_recognition(
            "ButtonOCR",
            argv.image,
            pipeline_override={"ButtonOCR": {"roi": [0, 0, 100, 100]}}
        )
        
        if button_reco and button_reco.hit:
            button_box = button_reco.best_result.box
            print(f"[ComplexRecognition] 找到目标按钮：{button_box}")
            
            # 2. 点击目标按钮
            context.tasker.controller.post_click(button_box[0], button_box[1]).wait()
            
            # 3. 第二次识别：验证操作结果
            result_reco = context.run_recognition(
                "ResultOCR",
                argv.image,
                pipeline_override={"ResultOCR": {"roi": [200, 200, 300, 100]}}
            )
            
            if result_reco and result_reco.hit:
                print(f"[ComplexRecognition] 操作成功，结果：{result_reco.best_result.detail}")
                
                # 4. 覆盖后续任务，跳转到成功节点
                context.override_next(argv.node_name, ["SuccessNode"])
                
                return CustomRecognition.AnalyzeResult(
                    box=button_box,
                    detail="操作成功"
                )
            else:
                print("[ComplexRecognition] 操作失败，未找到结果")
                
                # 5. 覆盖后续任务，跳转到失败节点
                context.override_next(argv.node_name, ["FailureNode"])
                
                return CustomRecognition.AnalyzeResult(
                    box=button_box,
                    detail="操作失败"
                )
        else:
            print("[ComplexRecognition] 未找到目标按钮")
            
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail="未找到目标按钮"
            )
```

### 6.4 示例：使用TemplateMatch找图识别

```python
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("TemplateMatchRecognition")
class TemplateMatchRecognition(CustomRecognition):
    """使用TemplateMatch进行找图识别的示例"""
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # 定义TemplateMatch找图配置
        template_match_config = {
            "TemplateMatch": {
                "type": "TemplateMatch",
                "param": {
                    "template": "target_image.png",  # 模板图片名称
                    "threshold": 0.8,  # 匹配阈值，0-1之间，值越大匹配越严格
                    "roi": [0, 0, 1280, 720]  # 搜索区域，格式：[x, y, width, height]
                }
            }
        }
        
        # 执行找图识别
        reco_detail = context.run_recognition(
            "TemplateMatch",  # 识别任务名称
            argv.image,  # 当前帧图像
            pipeline_override=template_match_config  # 覆盖模板匹配配置
        )
        
        if reco_detail and reco_detail.hit:
            # 识别成功，获取匹配结果
            box = reco_detail.best_result.box  # 匹配到的区域坐标
            score = reco_detail.best_result.score  # 匹配得分
            
            print(f"[TemplateMatchRecognition] 找到目标图像，位置：{box}，得分：{score}")
            
            # 点击匹配到的位置（点击区域中心）
            click_x = box[0] + box[2] // 2
            click_y = box[1] + box[3] // 2
            context.tasker.controller.post_click(click_x, click_y).wait()
            
            return CustomRecognition.AnalyzeResult(
                box=box,
                detail=f"找到目标图像，得分：{score}"
            )
        else:
            print("[TemplateMatchRecognition] 未找到目标图像")
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail="未找到目标图像"
            )
```

### 6.5 示例：使用NeuralNetworkDetect深度识别

```python
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("NNDetectRecognition")
class NNDetectRecognition(CustomRecognition):
    """使用NeuralNetworkDetect进行深度识别的示例"""
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # 定义NeuralNetworkDetect深度识别配置
        nn_detect_config = {
            "NeuralNetworkDetect": {
                "type": "NeuralNetworkDetect",
                "param": {
                    "model": "object_detection_model.onnx",  # 深度模型文件路径
                    "threshold": 0.7,  # 检测阈值
                    "roi": [0, 0, 1280, 720],  # 检测区域
                    "labels": ["target_object", "other_object"]  # 模型输出标签
                }
            }
        }
        
        # 执行深度识别
        reco_detail = context.run_recognition(
            "NeuralNetworkDetect",  # 识别任务名称
            argv.image,  # 当前帧图像
            pipeline_override=nn_detect_config  # 覆盖深度识别配置
        )
        
        if reco_detail and reco_detail.hit:
            # 识别成功，处理检测结果
            best_result = reco_detail.best_result
            box = best_result.box  # 检测到的目标框
            label = best_result.detail  # 检测到的目标标签
            score = best_result.score  # 检测置信度
            
            print(f"[NNDetectRecognition] 检测到目标：{label}，位置：{box}，置信度：{score}")
            
            # 只处理特定标签的目标
            if label == "target_object":
                # 点击目标中心
                click_x = box[0] + box[2] // 2
                click_y = box[1] + box[3] // 2
                context.tasker.controller.post_click(click_x, click_y).wait()
                
                return CustomRecognition.AnalyzeResult(
                    box=box,
                    detail=f"检测到目标：{label}，置信度：{score}"
                )
            else:
                print(f"[NNDetectRecognition] 检测到非目标物体：{label}，跳过")
                return CustomRecognition.AnalyzeResult(
                    box=None,
                    detail=f"检测到非目标物体：{label}"
                )
        else:
            print("[NNDetectRecognition] 未检测到目标")
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail="未检测到目标"
            )
```

### 6.6 示例：结合多种识别方式的综合识别

```python
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("MultiRecognition")
class MultiRecognition(CustomRecognition):
    """结合TemplateMatch和NeuralNetworkDetect的综合识别示例"""
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        print("[MultiRecognition] 开始综合识别...")
        
        # 1. 首先使用TemplateMatch找图
        template_config = {
            "TemplateMatch": {
                "type": "TemplateMatch",
                "param": {
                    "template": "reference.png",
                    "threshold": 0.85,
                    "roi": [0, 0, 1280, 720]
                }
            }
        }
        
        template_reco = context.run_recognition(
            "TemplateMatch",
            argv.image,
            pipeline_override=template_config
        )
        
        if template_reco and template_reco.hit:
            print(f"[MultiRecognition] TemplateMatch成功：{template_reco.best_result.box}")
            
            # 2. 如果找图成功，再使用深度识别进行精确检测
            nn_config = {
                "NeuralNetworkDetect": {
                    "type": "NeuralNetworkDetect",
                    "param": {
                        "model": "precision_model.onnx",
                        "threshold": 0.75,
                        "labels": ["precise_target"]
                    }
                }
            }
            
            nn_reco = context.run_recognition(
                "NeuralNetworkDetect",
                argv.image,
                pipeline_override=nn_config
            )
            
            if nn_reco and nn_reco.hit:
                best_result = nn_reco.best_result
                print(f"[MultiRecognition] 深度识别成功：{best_result.box}，标签：{best_result.detail}")
                
                return CustomRecognition.AnalyzeResult(
                    box=best_result.box,
                    detail=f"综合识别成功，标签：{best_result.detail}"
                )
            else:
                print("[MultiRecognition] 深度识别失败，使用找图结果")
                return CustomRecognition.AnalyzeResult(
                    box=template_reco.best_result.box,
                    detail="深度识别失败，使用找图结果"
                )
        else:
            print("[MultiRecognition] 找图失败")
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail="综合识别失败"
            )
```

## 7. 最佳实践

### 7.1 代码结构建议

- **模块化设计**：将不同功能的自定义组件放在不同的模块中
- **清晰的命名规范**：使用有意义的类名和方法名
- **详细的文档字符串**：为类和方法添加详细的文档字符串
- **适当的日志输出**：使用print或logging模块输出关键信息，便于调试

### 7.2 性能优化

- **减少识别次数**：避免不必要的识别操作
- **合理设置ROI**：只在必要的区域进行识别
- **异步操作**：对于非阻塞操作，考虑使用异步方式执行
- **资源管理**：及时释放不再使用的资源

### 7.3 调试技巧

- **日志输出**：在关键位置添加日志输出，便于跟踪执行流程
- **结果验证**：对识别结果进行验证，确保准确性
- **分步调试**：将复杂逻辑分解为多个步骤，逐步调试
- **可视化调试**：保存识别过程中的图像，便于分析问题

### 7.4 错误处理

- **异常捕获**：对可能出现的异常进行捕获和处理
- **合理的返回值**：根据实际情况返回适当的结果
- **错误日志**：记录详细的错误信息，便于定位问题

## 8. 常见问题与解决方案

### 8.1 识别失败问题

**问题**：自定义识别总是返回未命中
**解决方案**：
- 检查ROI设置是否正确
- 验证识别任务名称是否正确
- 检查识别模型是否正确加载
- 确保图像质量良好

### 8.2 动作执行异常

**问题**：自定义动作执行失败
**解决方案**：
- 检查控制器是否正常工作
- 验证坐标是否在屏幕范围内
- 确保动作参数设置正确
- 检查外部依赖是否正常

### 8.3 上下文管理问题

**问题**：上下文覆盖不生效
**解决方案**：
- 检查节点名称是否正确
- 确保覆盖操作在正确的时机执行
- 验证覆盖的配置格式是否正确

### 8.4 代理服务启动失败

**问题**：代理服务无法启动
**解决方案**：
- 检查命令行参数是否正确
- 确保socket_id有效
- 验证MAA主程序是否正在运行
- 检查配置文件是否正确

## 9. 完整示例代码

```python
import sys
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction
from maa.context import Context
from maa.toolkit import Toolkit


@AgentServer.custom_recognition("MyRecognition")
class MyRecognition(CustomRecognition):
    """自定义识别类示例"""
    
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        print(f"[MyRecognition] 执行识别，节点：{argv.node_name}")
        
        # 执行OCR识别
        reco_detail = context.run_recognition(
            "MyOCR",
            argv.image,
            pipeline_override={"MyOCR": {"roi": [100, 100, 200, 300]}}
        )
        
        if reco_detail and reco_detail.hit:
            box = reco_detail.best_result.box
            text = reco_detail.best_result.detail
            
            print(f"[MyRecognition] 识别成功：{text}，位置：{box}")
            
            # 点击识别到的位置
            context.tasker.controller.post_click(box[0], box[1]).wait()
            
            # 覆盖后续任务
            context.override_next(argv.node_name, ["MyCustomAction"])
            
            return CustomRecognition.AnalyzeResult(
                box=box,
                detail=f"识别到文本：{text}"
            )
        else:
            print("[MyRecognition] 识别失败")
            
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail="未识别到文本"
            )


@AgentServer.custom_action("MyCustomAction")
class MyCustomAction(CustomAction):
    """自定义动作类示例"""
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        print(f"[MyCustomAction] 执行动作，节点：{argv.node_name}")
        
        # 执行一系列操作
        context.tasker.controller.post_click(100, 200).wait()
        context.tasker.controller.post_swipe(100, 200, 300, 400, 500).wait()
        
        print("[MyCustomAction] 动作执行完成")
        return True



def main():
    # 初始化工具包
    Toolkit.init_option("./")
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("Usage: python agent_main.py <socket_id>")
        print("socket_id 由 AgentIdentifier 提供")
        exit(1)
    
    # 获取socket_id
    socket_id = sys.argv[-1]
    
    # 启动代理服务
    AgentServer.start_up(socket_id)
    AgentServer.join()
    AgentServer.shut_down()


if __name__ == "__main__":
    main()
```

## 10. 参考资源

- [MaaFramework GitHub仓库](https://github.com/MaaXYZ/MaaFramework)
- [MaaFramework官方文档](https://maafw.xyz/)
- [MaaFramework集成接口一览](https://maafw.xyz/docs/2.2-IntegratedInterfaceOverview)
- [MaaAssistantArknights项目](https://github.com/MaaAssistantArknights/MaaAssistantArknights)
- [Python官方文档](https://docs.python.org/3/)

## 11. 结语

本指南详细介绍了MaaFramework中Custom功能的语法用法和Python API调用方法，涵盖了自定义识别、自定义动作、上下文管理和代理服务等核心内容。通过本指南，开发者可以快速掌握MaaFramework的扩展机制，实现复杂的自动化测试逻辑。

MaaFramework是一个功能强大、易于扩展的自动化测试框架，具有广阔的应用前景。希望本指南能够帮助开发者更好地利用MaaFramework的功能，编写出高质量的自动化测试程序。

如果您在使用过程中遇到问题，欢迎查阅官方文档或参与社区讨论，共同推动MaaFramework的发展。