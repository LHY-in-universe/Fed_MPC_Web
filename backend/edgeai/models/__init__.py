"""
EdgeAI数据模型
"""

from .project import EdgeAIProject
from .edge_node import EdgeNode
from .control_node import ControlNode
from .training_task import TrainingTask
from .node_connection import NodeConnection

__all__ = [
    'EdgeAIProject',
    'EdgeNode', 
    'ControlNode',
    'TrainingTask',
    'NodeConnection'
]