import os
import json
import logging
import re
from typing import Dict, Tuple, List
from models.schemas import SimulationInput, GraphNode, GraphEdge, GraphUpdate
from config.prompts import AGENT_ACTION_PROMPT
from utils.retry_handler import gemini_retry
import time
import urllib.request

logger = logging.getLogger(__name__)

class SimulationEngine:
    """
    模块 B: 核心推演引擎 (HaruFishing Simulation Engine)
    """
    def __init__(self, simulation_input: SimulationInput, agent_prompts: Dict[str, str], max_rounds: int = 2):
        self.simulation_input = simulation_input
        self.agent_prompts = agent_prompts
        self.max_rounds = max_rounds
        self.interaction_logs = []
        self.all_nodes = []
        self.all_edges = []
        
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ 未检测到 GEMINI_API_KEY 环境变量！请在运行前设置。")

    @gemini_retry
    def _call_agent(self, char_name: str, prompt: str, system_instruction: str) -> str:
        if not self.api_key:
            raise ValueError("API Key 缺失")
            
        model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        logger.info(f"    -> 正在向云端发送 {char_name} 的行动请求...")
        start_time = time.time()
        
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                result_data = json.loads(response.read().decode('utf-8'))
                
            logger.info(f"    -> ✅ 请求成功，耗时: {time.time() - start_time:.2f} 秒")
            return result_data['candidates'][0]['content']['parts'][0]['text'].strip()
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logger.error(f"❌ HTTP 报错 {e.code}: {error_body}")
            raise
        except Exception as e:
            logger.error(f"❌ 原生网络请求失败或超时: {e}")
            raise

    def run_simulation(self, on_step_complete=None) -> Tuple[str, List[GraphNode], List[GraphEdge]]:
        logger.info("🎬 HaruFishing 推演引擎启动...")
        
        # 初始中心节点
        self.all_nodes.append(GraphNode(id=self.simulation_input.trigger_event, label="触发事件", group="Event"))
        
        blackboard_context = f"初始触发事件：{self.simulation_input.trigger_event}\n"
        self.interaction_logs.append(blackboard_context)
        
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"--- 🔄 第 {round_num} 轮推演 ---")
            round_log = f"\n[第 {round_num} 轮]\n"
            
            for char in self.simulation_input.characters:
                char_name = char.name
                logger.info(f"等待 {char_name} 做出反应...")
                
                action_prompt = AGENT_ACTION_PROMPT.format(
                    context=blackboard_context,
                    name=char_name
                )
                system_prompt = self.agent_prompts[char_name]
                
                try:
                    reaction = self._call_agent(char_name, action_prompt, system_prompt)
                    
                    # 从回答中提取 JSON 增量图谱更新
                    json_match = re.search(r'```json(.*?)```', reaction, re.DOTALL)
                    clean_reaction = reaction
                    if json_match:
                        json_str = json_match.group(1).strip()
                        try:
                            update_data = json.loads(json_str)
                            graph_update = GraphUpdate(**update_data)
                            self.all_nodes.extend(graph_update.nodes)
                            self.all_edges.extend(graph_update.edges)
                        except Exception as json_e:
                            logger.warning(f"⚠️ 解析 {char_name} 的增量图谱 JSON 失败: {json_e}")
                        
                        # 从文本中剔除 JSON 块，保持黑板干净
                        clean_reaction = reaction[:json_match.start()].strip() + "\n" + reaction[json_match.end():].strip()
                    
                    log_entry = f"【{char_name} 的反应】:\n{clean_reaction.strip()}\n\n"
                    
                    round_log += log_entry
                    blackboard_context += log_entry
                    
                    if on_step_complete:
                        unique_nodes = []
                        seen_node_ids = set()
                        for node in self.all_nodes:
                            if node.id not in seen_node_ids:
                                seen_node_ids.add(node.id)
                                unique_nodes.append(node)
                        on_step_complete(unique_nodes, self.all_edges)
                        
                except Exception as e:
                    logger.error(f"❌ {char_name} 推演失败: {e}")
                    round_log += f"【{char_name}】 (被不可抗力沉默，无响应)\n\n"
            
            self.interaction_logs.append(round_log)
            
        logger.info("🛑 推演循环结束。")
        
        # 简单去重 Nodes
        unique_nodes = []
        seen_node_ids = set()
        for node in self.all_nodes:
            if node.id not in seen_node_ids:
                seen_node_ids.add(node.id)
                unique_nodes.append(node)
                
        return "".join(self.interaction_logs), unique_nodes, self.all_edges

