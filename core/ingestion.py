import json
import os
import logging
from typing import Dict
from models.schemas import SimulationInput
from config.prompts import AGENT_SYSTEM_PROMPT, EXTRACTOR_PROMPT
from utils.retry_handler import gemini_retry
import time
import urllib.request

logger = logging.getLogger(__name__)

class IngestionModule:
    """
    模块 A: 剧本解析器 (Context & Profile Ingestion)
    """
    
    @staticmethod
    def load_simulation_data(file_path: str) -> SimulationInput:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"剧本文件未找到: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            
        return SimulationInput(**data)

    @staticmethod
    @gemini_retry
    def extract_from_document(document_text: str) -> SimulationInput:
        logger.info("🧠 正在利用大模型对文档进行全自动角色与事件提取...")
        
        max_chars = 40000 
        if len(document_text) > max_chars:
            logger.warning(f"⚠️ 文档过长 ({len(document_text)}字)，进行安全截断...")
            document_text = document_text[:max_chars]

        prompt = EXTRACTOR_PROMPT.format(document_text=document_text)
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 未找到！")
            
        model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        
        logger.info(f"发送提取请求中，Prompt长度: {len(prompt)}...")
        start_time = time.time()
        
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                result_data = json.loads(response.read().decode('utf-8'))
                
            logger.info(f"✅ 原生 HTTP 请求完成，耗时: {time.time() - start_time:.2f} 秒")
            
            result_json = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            if result_json.startswith('```json'):
                result_json = result_json.replace('```json', '', 1)
            if result_json.endswith('```'):
                result_json = result_json[::-1].replace('```'[::-1], '', 1)[::-1]
            result_json = result_json.strip()
            
            return SimulationInput.model_validate_json(result_json)
            
        except Exception as e:
            logger.error(f"❌ 剧本提炼失败: {e}")
            raise

    @staticmethod
    def build_agent_prompts(simulation_input: SimulationInput) -> Dict[str, str]:
        agent_prompts = {}
        for char in simulation_input.characters:
            rel_text = "\n".join([f"- 对待 {name}: {desc}" for name, desc in char.relationships.items()])
            if not rel_text:
                rel_text = "- 无特殊人物关系"
                
            prompt = AGENT_SYSTEM_PROMPT.format(
                name=char.name,
                identity=char.identity,
                relationships=rel_text
            )
            agent_prompts[char.name] = prompt
            
        return agent_prompts
