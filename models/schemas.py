from pydantic import BaseModel, Field
from typing import List, Dict

class Character(BaseModel):
    name: str = Field(description="角色名称")
    identity: str = Field(description="性格、弱点、背景")
    relationships: Dict[str, str] = Field(default_factory=dict, description="关系字典")

class SimulationInput(BaseModel):
    trigger_event: str = Field(description="触发核心事件")
    characters: List[Character] = Field(description="人物列表")

class GraphNode(BaseModel):
    id: str = Field(description="节点唯一ID，例如：张三")
    label: str = Field(description="节点显示名称")
    group: str = Field(description="节点类型(Person/Event/Action/Emotion)")

class GraphEdge(BaseModel):
    source: str = Field(description="起始节点ID")
    target: str = Field(description="目标节点ID")
    label: str = Field(description="动作描述")

class GraphUpdate(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list, description="新增节点")
    edges: List[GraphEdge] = Field(default_factory=list, description="新增连线")

class Prediction(BaseModel):
    scenario: str = Field(description="预测结果场景")
    probability: str = Field(description="概率")
    reasoning_chain: str = Field(description="逻辑链条")

class SimulationOutput(BaseModel):
    predictions: List[Prediction] = Field(description="预测结果")
