"""

RoiBox Custom Recognition

全屏识别目标，判断识别到的 box 是否在指定的 roi 范围内。

参数格式 (custom_recognition_param):
{
    "node": "NodeName",   // 要执行的识别节点名称
    "roi": [x, y, w, h],  // 目标区域，box 必须在此范围内才算成功
    "mode": "center"      // 可选: "center"(默认) | "full" | "any"
                          // center: box 中心点在 roi 内
                          // full: box 完全在 roi 内
                          // any: box 与 roi 有任意交集
}

Pipeline v2 使用示例:
{
    "DetectNode": {
        "recognition": {
            "type": "NeuralNetworkDetect",
            "model": "best.onnx",
            "expected": [0],
            "threshold": [0.5]
        }
    },
    "RoiBoxNode": {
        "recognition": {
            "type": "Custom",
            "param": {
                "custom_recognition": "RoiBox",
                "custom_recognition_param": {
                    "node": "DetectNode",
                    "roi": [100, 100, 500, 400],
                    "mode": "center"
                }
            }
        },
        "action": "Click",
        "next": ["NextNode"]
    }
}
"""

import json
from typing import List, Union

from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("RoiBox")
class RoiBox(CustomRecognition):
    """
    全屏检测，判断检测到的 box 是否在指定 roi 范围内。
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, None]:
        try:
            params = json.loads(argv.custom_recognition_param)
            # 获取要执行的识别节点名称
            node = params.get("node")
            if not node:
                return None

            # 获取目标 roi [x, y, w, h]
            roi = params.get("roi", [0, 0, 0, 0])
            if roi == [0, 0, 0, 0]:
                # 默认全屏，获取图像尺寸
                height, width = argv.image.shape[:2]
                roi = [0, 0, width, height]

            # 获取判断模式
            mode = params.get("mode", "center")

            # 执行识别节点
            try:
                reco_detail = context.run_recognition(node, argv.image)

            except Exception as e:
                import traceback

                return None

            if reco_detail and reco_detail.hit:
                # 获取检测到的 box
                box = list(reco_detail.box)

                # 判断 box 是否在 roi 范围内
                if self._is_box_in_roi(box, roi, mode):
                    return CustomRecognition.AnalyzeResult(
                        box=tuple(box),
                        detail={
                            "roi": roi,
                            "mode": mode,
                        },
                    )
                else:
                    return None
            else:
                return None

        except Exception as e:
            return None

    def _is_box_in_roi(self, box: List[int], roi: List[int], mode: str) -> bool:
        """
        判断 box 是否在 roi 范围内

        Args:
            box: 检测框 [x, y, w, h]
            roi: 目标区域 [x, y, w, h]
            mode: 判断模式
                - "center": box 中心点在 roi 内
                - "full": box 完全在 roi 内
                - "any": box 与 roi 有任意交集

        Returns:
            bool: 是否满足条件
        """
        box_x, box_y, box_w, box_h = box
        roi_x, roi_y, roi_w, roi_h = roi

        # 计算 box 的边界
        box_left = box_x
        box_top = box_y
        box_right = box_x + box_w
        box_bottom = box_y + box_h

        # 计算 roi 的边界
        roi_left = roi_x
        roi_top = roi_y
        roi_right = roi_x + roi_w
        roi_bottom = roi_y + roi_h

        if mode == "center":
            # box 中心点在 roi 内
            center_x = box_x + box_w / 2
            center_y = box_y + box_h / 2
            return (
                roi_left <= center_x <= roi_right and roi_top <= center_y <= roi_bottom
            )

        elif mode == "full":
            # box 完全在 roi 内
            return (
                box_left >= roi_left
                and box_top >= roi_top
                and box_right <= roi_right
                and box_bottom <= roi_bottom
            )

        elif mode == "any":
            # box 与 roi 有任意交集
            return not (
                box_right < roi_left
                or box_left > roi_right
                or box_bottom < roi_top
                or box_top > roi_bottom
            )

        else:
            return (
                roi_left <= center_x <= roi_right and roi_top <= center_y <= roi_bottom
            )