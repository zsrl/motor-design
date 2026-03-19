"""
RMxprt电机设计模块
基于实际的RMxprt参数结构，提供完整的电机设计功能
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from ansys.aedt.core import Rmxprt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RMxprtDesigner:
    """RMxprt电机设计器"""
    
    def __init__(self, solution_type: str = "ASSM", project: str = "DefaultProject", design: str = "Motor_2D_Design"):
        """
        初始化RMxprt设计器
        
        Args:
            solution_type: 解决方案类型，默认为"ASSM"（调速同步电机）
        """
        self.solution_type = solution_type
        self.project = project
        self.design = design
        self.app = None
        self.design_params = {}
        self.setup_params = {}
        
    def initialize(self, timestamp: Optional[str] = None):
        """初始化RMxprt应用
        
        Args:
            timestamp: 时间戳，用于动态生成项目名
        """
        try:
            logger.info(f"初始化RMxprt应用，解决方案类型: {self.solution_type}")
            
            # 如果提供了时间戳，使用时间戳动态生成项目名
            if timestamp:
                project_name = f"project_{timestamp}"
            else:
                project_name = self.project
            
            self.app = Rmxprt(
                # version="2025.2",  # 固定版本
                project=project_name,  # 动态生成的项目名
                # design=self.design,  # 固定设计名
                # new_desktop=True,  # 创建新桌面
                # remove_lock=True,  # 移除锁文件
                solution_type=self.solution_type
            )
            logger.info(f"RMxprt应用初始化成功，项目名: {project_name}")
            return True
        except Exception as e:
            logger.error(f"RMxprt应用初始化失败: {e}")
            return False
    
    def load_parameters(self, params_file: str) -> bool:
        """
        从JSON文件加载参数
        
        Args:
            params_file: 参数文件路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            with open(params_file, 'r', encoding='utf-8') as f:
                self.design_params = json.load(f)
            logger.info(f"从 {params_file} 加载参数成功")
            return True
        except Exception as e:
            logger.error(f"加载参数文件失败: {e}")
            return False
    
    def apply_parameters(self) -> bool:
        """
        应用参数到RMxprt设计
        
        Returns:
            bool: 是否成功应用
        """
        if not self.app:
            logger.error("RMxprt应用未初始化")
            return False
        
        if not self.design_params:
            logger.error("未加载设计参数")
            return False
        
        try:
            logger.info("开始应用参数到RMxprt设计")
            
            # 应用通用参数
            if "General" in self.design_params:
                self._apply_component_parameters(self.app.general, self.design_params["General"], "General")
            
            # 应用定子参数
            if "Stator" in self.design_params:
                self._apply_component_parameters(self.app.stator, self.design_params["Stator"], "Stator")
            
            # 应用转子参数
            if "Rotor" in self.design_params:
                self._apply_component_parameters(self.app.rotor, self.design_params["Rotor"], "Rotor")
            
            # 应用轴参数
            if "Shaft" in self.design_params:
                self._apply_component_parameters(self.app.shaft, self.design_params["Shaft"], "Shaft")
            
            # 应用电路参数
            if "Circuit" in self.design_params:
                self._apply_component_parameters(self.app.circuit, self.design_params["Circuit"], "Circuit")
            
            # 应用Setup参数（保存到实例变量中，供create_setup使用）
            if "Setup" in self.design_params:
                self.setup_params = self.design_params["Setup"]
                logger.info(f"加载Setup参数: {self.setup_params}")
            else:
                self.setup_params = {}
            
            #应用子组件参数（Slot, Winding, Pole等）
            self._apply_subcomponent_parameters()
            
            logger.info("参数应用完成")
            return True
            
        except Exception as e:
            logger.error(f"应用参数失败: {e}")
            return False
    
    def _apply_component_parameters(self, component, params: Dict[str, Any], component_name: str):
        """应用组件参数"""
        # 定义已知的只读属性列表（根据警告信息）
        read_only_properties = {
            "Slot": [],  # 槽相关只读属性
            "Pole": [],  # 磁极相关只读属性
            "General": [],  # 通用参数
            "Stator": [],   # 定子参数
            "Rotor": [],    # 转子参数
            "Shaft": [],    # 轴参数
            "Circuit": []   # 电路参数
        }
        
        for param_name, param_value in params.items():
            try:
                # 跳过Choices后缀的参数
                if param_name.endswith("/Choices"):
                    continue
                
                # 检查是否为只读属性
                component_read_only = read_only_properties.get(component_name, [])
                if param_name in component_read_only:
                    logger.debug(f"跳过只读属性 {component_name}.{param_name}")
                    continue
                
                # 设置参数值
                component[param_name] = param_value
                logger.debug(f"设置 {component_name}.{param_name} = {param_value}")
                
            except Exception as e:
                # 检查错误信息中是否包含"read-only"
                error_msg = str(e).lower()
                if "read-only" in error_msg or "readonly" in error_msg:
                    logger.debug(f"跳过只读属性 {component_name}.{param_name}: {e}")
                else:
                    logger.warning(f"设置参数 {component_name}.{param_name} 失败: {e}")
    
    def _apply_subcomponent_parameters(self):
        """应用子组件参数"""
        # 获取定子子组件
        stator_node = self.app.stator.properties
        if stator_node is not False and hasattr(stator_node, 'children'):
            stator_children = stator_node.children
            
            # 应用槽参数
            if "Slot" in self.design_params and "Slot" in stator_children:
                slot_params = self.design_params["Slot"]
                slot_node = stator_children["Slot"]
                self._apply_child_parameters(slot_node, slot_params, "Slot")
            
            # 应用绕组参数
            if "Winding" in self.design_params and "Winding" in stator_children:
                winding_params = self.design_params["Winding"]
                winding_node = stator_children["Winding"]
                self._apply_child_parameters(winding_node, winding_params, "Winding")
        
        # 获取转子子组件
        rotor_node = self.app.rotor.properties
        if rotor_node is not False and hasattr(rotor_node, 'children'):
            rotor_children = rotor_node.children
            
            # 应用极参数
            if "Pole" in self.design_params and "Pole" in rotor_children:
                pole_params = self.design_params["Pole"]
                pole_node = rotor_children["Pole"]
                self._apply_child_parameters(pole_node, pole_params, "Pole")
    
    def _apply_child_parameters(self, child_node, params: Dict[str, Any], child_name: str):
        """应用子组件参数"""
        # 定义已知的只读属性列表（根据警告信息）
        read_only_properties = {
            "Slot": [],  # 槽相关只读属性
            "Pole": [],  # 磁极相关只读属性
            "Winding": []  # 绕组参数
        }
        
        for param_name, param_value in params.items():
            try:
                # 跳过Choices后缀的参数
                if param_name.endswith("/Choices"):
                    continue
                
                # 检查是否为只读属性
                component_read_only = read_only_properties.get(child_name, [])
                if param_name in component_read_only:
                    logger.debug(f"跳过只读属性 {child_name}.{param_name}")
                    continue
                
                # 设置参数值
                if hasattr(child_node, 'properties'):
                    child_node.properties[param_name] = param_value
                    logger.debug(f"设置 {child_name}.{param_name} = {param_value}")
                
            except Exception as e:
                # 检查错误信息中是否包含"read-only"
                error_msg = str(e).lower()
                if "read-only" in error_msg or "readonly" in error_msg:
                    logger.debug(f"跳过只读属性 {child_name}.{param_name}: {e}")
                else:
                    logger.warning(f"设置子组件参数 {child_name}.{param_name} 失败: {e}")
    
    def create_setup(self, setup_name: str = "MySetupAuto", **kwargs) -> bool:
        """
        创建分析设置
        
        Args:
            setup_name: 设置名称
            **kwargs: 其他设置参数（将覆盖从JSON加载的Setup参数）
            
        Returns:
            bool: 是否成功创建
        """
        try:
            logger.info(f"创建分析设置: {setup_name}")
            
            # 合并Setup参数：优先使用kwargs，其次使用从JSON加载的参数
            setup_kwargs = {}
            
            # 首先添加从JSON加载的Setup参数
            if hasattr(self, 'setup_params') and self.setup_params:
                for key, value in self.setup_params.items():
                    setup_kwargs[key] = value
                    logger.debug(f"从JSON加载Setup参数: {key} = {value}")
            
            # 然后添加传入的kwargs参数（覆盖JSON参数）
            setup_kwargs.update(kwargs)
            
            # 如果Enabled为False，则不创建Setup
            if 'Enabled' in setup_kwargs and not setup_kwargs['Enabled']:
                logger.info(f"Setup {setup_name} 被禁用，跳过创建")
                return True
            
            logger.info(f"使用参数创建Setup: {setup_kwargs}")
            setup = self.app.create_setup(name=setup_name, **setup_kwargs)
            setup.analyze()
            m2d = self.app.create_maxwell_design(setup_name)
            if m2d:
                logger.info(f"Maxwell设计创建成功: {setup_name}")
                return True
            else:
                logger.warning(f"Maxwell设计创建失败: {setup_name}")
                return False
        except Exception as e:
            logger.error(f"创建分析设置失败: {e}")
            return False
    

    
    def analyze(self) -> bool:
        """
        执行分析
        
        Returns:
            bool: 是否成功分析
        """
        try:
            logger.info("开始执行分析...")
            # 使用analyze方法而不是analyze_all
            self.app.analyze()
            logger.info("分析执行完成")

            return True
        except Exception as e:
            logger.error(f"分析执行失败: {e}")
            return False
    
    def save_project(self, project_name: Optional[str] = None, timestamp: Optional[str] = None) -> bool:
        """
        保存项目
        
        Args:
            project_name: 项目名称，如果为None则使用默认名称
            timestamp: 时间戳，用于构建文件名
            
        Returns:
            bool: 是否成功保存
        """
        try:
            if project_name:
                save_path = f"{project_name}.aedt"
            elif timestamp:
                save_path = f"rmxprt_design_{timestamp}.aedt"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"rmxprt_design_{timestamp}.aedt"
            
            # 这里需要根据实际API实现保存逻辑
            self.app.save_project()
            logger.info(f"项目保存到: {save_path}")
            return True
        except Exception as e:
            logger.error(f"保存项目失败: {e}")
            return False
    
    def close(self):
        """关闭RMxprt应用"""
        if self.app:
            try:
                # 释放桌面会话
                self.app.release_desktop()
                logger.info("RMxprt应用已关闭")
            except Exception as e:
                logger.error(f"关闭RMxprt应用时出错: {e}")
    
    def get_design_summary(self) -> Dict[str, Any]:
        """
        获取设计摘要
        
        Returns:
            Dict[str, Any]: 设计摘要信息
        """
        summary = {
            "solution_type": self.solution_type,
            "parameters_loaded": bool(self.design_params),
            "components": []
        }
        
        if self.app:
            # 获取各组件信息
            components = ["general", "stator", "rotor", "shaft", "circuit"]
            for comp_name in components:
                component = getattr(self.app, comp_name, None)
                if component:
                    node = component.properties
                    if node is not False:
                        summary["components"].append({
                            "name": comp_name.capitalize(),
                            "parameters_count": len(node.properties) if hasattr(node, 'properties') else 0
                        })
        
        return summary


def create_rmxprt_design(timestamp: str, output_dir: str = "output") -> Dict[str, Any]:
    """
    创建RMxprt设计的便捷函数
    
    Args:
        timestamp: 时间戳，用于构建参数文件路径
        output_dir: 输出目录
        
    Returns:
        Dict[str, Any]: 执行结果
    """
    result = {
        "success": False,
        "message": "",
        "output_files": [],
        "design_summary": {}
    }
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 根据timestamp构建参数文件路径
    params_file = f"rmxprt_params_{timestamp}.json"
    
    designer = RMxprtDesigner()
    
    try:
        # 1. 初始化
        if not designer.initialize(timestamp=timestamp):
            result["message"] = "RMxprt初始化失败"
            return result
        
        # 2. 加载参数
        if not designer.load_parameters(params_file):
            result["message"] = "参数加载失败"
            return result
        
        # 3. 应用参数
        if not designer.apply_parameters():
            result["message"] = "参数应用失败"
            return result
        
        # 5. 创建分析设置
        if not designer.create_setup("Setup1"):
            result["message"] = "创建分析设置失败"
            return result
        
        # 7. 保存项目
        designer.save_project()
        
        # 8. 获取设计摘要
        result["design_summary"] = designer.get_design_summary()
        
        # 所有步骤成功完成，设置success为True
        result["success"] = True
        
    except Exception as e:
        result["message"] = f"创建RMxprt设计时出错: {str(e)}"
        logger.error(result["message"])
    
    finally:
        # 关闭设计器
        pass
        # designer.close()
    
    return result


if __name__ == "__main__":
    # 示例用法
    import sys
    
    if len(sys.argv) > 1:
        timestamp = sys.argv[1]
        result = create_rmxprt_design(timestamp)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("用法: python rmxprt_design.py <timestamp>")
        print("示例: python rmxprt_design.py 20250318141853")