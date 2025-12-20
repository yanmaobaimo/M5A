from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("my_reco_222")
class MyRecongition(CustomRecognition):
    """
    自定义识别类示例
    
    该类演示了如何使用MaaFramework进行自定义图像识别，包括：
    1. 执行OCR识别任务
    2. 临时覆盖识别配置
    3. 全局覆盖流水线配置
    4. 克隆上下文进行独立配置
    5. 执行点击操作
    6. 覆盖后续任务流程
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        """
        执行自定义识别逻辑
        
        Args:
            context: 运行上下文，包含任务状态和配置
            argv: 识别参数，包含当前帧图像等信息
            
        Returns:
            识别结果，包含边界框和详细信息
        """
        
        # 1. 执行OCR识别任务，临时覆盖ROI配置
        # 这里使用"MyCustomOCR"作为识别任务名称，可根据实际需求修改
        # ROI参数格式：[x1, y1, x2, y2]，表示识别区域的左上角和右下角坐标
        reco_detail = context.run_recognition(
            "MyCustomOCR",
            argv.image,
            pipeline_override={"MyCustomOCR": {"roi": [100, 100, 200, 300]}},
        )

        # 2. 全局覆盖流水线配置，对后续所有识别任务生效
        # 这里将ROI设置为[1, 1, 114, 514]，可根据实际需求调整
        context.override_pipeline({"MyCustomOCR": {"roi": [1, 1, 114, 514]}})
        # context.run_recognition ...  # 可继续执行其他识别任务

        # 3. 克隆上下文，创建独立的上下文实例
        # 克隆后的上下文可以独立配置，不会影响全局上下文
        new_context = context.clone()
        new_context.override_pipeline({"MyCustomOCR": {"roi": [100, 200, 300, 400]}})
        reco_detail = new_context.run_recognition("MyCustomOCR", argv.image)

        # 4. 执行独立的点击操作
        # 点击坐标(10, 20)，可根据实际需求修改
        click_job = context.tasker.controller.post_click(10, 20)
        click_job.wait()  # 等待点击操作完成

        # 5. 覆盖当前节点的后续任务列表
        # 将后续任务设置为["TaskA", "TaskB"]，可根据实际需求修改
        context.override_next(argv.node_name, ["TaskA", "TaskB"])

        # 6. 返回识别结果
        # box参数表示识别到的目标边界框，detail参数为详细信息
        return CustomRecognition.AnalyzeResult(
            box=(0, 0, 100, 100), detail="识别完成"
        )
