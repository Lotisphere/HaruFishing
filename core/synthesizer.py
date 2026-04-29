import json
import re
import os
import logging
import urllib.request
import time
from models.schemas import SimulationOutput
from config.prompts import OBSERVER_PROMPT
from utils.retry_handler import gemini_retry

logger = logging.getLogger(__name__)

class Synthesizer:
    """
    模块 C: 裁判与综合生成器 (The Observer)
    """
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ 未检测到 GEMINI_API_KEY！")

    def _truncate_logs(self, logs: str, max_length: int = 30000) -> str:
        if len(logs) <= max_length:
            return logs
        logger.warning(f"⚠️ 日志字数 ({len(logs)}) 超过安全阈值，进行截断保护...")
        half = max_length // 2
        return logs[:half] + "\n\n...[由于 Token 限制，中间对话已折叠]...\n\n" + logs[-half:]

    @gemini_retry
    def generate_report(self, trigger_event: str, interaction_logs: str) -> SimulationOutput:
        logger.info("⚖️ 裁判 (The Observer) 开始俯瞰整个事件，正在汇总推演结果...")
        
        safe_logs = self._truncate_logs(interaction_logs)
        prompt = OBSERVER_PROMPT.format(
            trigger_event=trigger_event,
            interaction_logs=safe_logs
        )
        
        model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        
        logger.info(f"    -> 正在向云端请求裁判报告...")
        start_time = time.time()
        
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=300) as response:
                result_data = json.loads(response.read().decode('utf-8'))
                
            logger.info(f"    -> ✅ 裁判请求成功，耗时: {time.time() - start_time:.2f} 秒")
            
            result_json = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            if result_json.startswith('```json'):
                result_json = result_json.replace('```json', '', 1)
            if result_json.endswith('```'):
                result_json = result_json[::-1].replace('```'[::-1], '', 1)[::-1]
            result_json = result_json.strip()
            
            report = SimulationOutput.model_validate_json(result_json)
            return report
            
        except Exception as e:
            logger.error(f"❌ 裁判生成器解析失败: {e}")
            raise


