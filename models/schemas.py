from pydantic import BaseModel, Field
from typing import List, Dict

class CharacterMetrics(BaseModel):
    degree_centrality: float = Field(default=0.0, description="Degree Centrality 0.0-1.0")
    betweenness_centrality: float = Field(default=0.0, description="Betweenness Centrality 0.0-1.0")
    eigenvector_centrality: float = Field(default=0.0, description="Eigenvector Centrality 0.0-1.0")

class Character(BaseModel):
    name: str = Field(description="角色名称")
    identity: str = Field(description="性格、弱点、背景")
    relationships: Dict[str, str] = Field(default_factory=dict, description="关系字典")
    initial_metrics: CharacterMetrics = Field(default_factory=CharacterMetrics, description="初始设定的节点价值指标")

class SimulationInput(BaseModel):
    trigger_event: str = Field(description="触发核心事件")
    characters: List[Character] = Field(description="人物列表")

class GraphNode(BaseModel):
    id: str = Field(description="节点唯一ID，例如：张三")
    label: str = Field(description="节点显示名称")
    group: str = Field(description="节点类型(Person/Event/Action/Emotion)")
    impact: float = Field(default=5.0, description="影响力指数 0.0-10.0")
    probability: str = Field(default="100%", description="发生概率 0%-100%")
    sentiment: float = Field(default=0.0, description="情绪极性 -1.0(负面) 到 1.0(正面)")

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

class FinalCharacterEval(BaseModel):
    name: str = Field(description="角色名称")
    effective_propagation_rate: str = Field(description="有效传播率 (Effective Propagation Rate) 及计算结果")
    diffusion_radius: str = Field(description="扩散半径换算 (Diffusion Radius) 及计算结果")
    social_marketing_score: str = Field(description="具体的社交营销得分 (Social Marketing Score) 及计算结果")

class SimulationOutput(BaseModel):
    predictions: List[Prediction] = Field(description="预测结果")
    evaluations: List[FinalCharacterEval] = Field(default_factory=list, description="各个角色的最终审判指标")
