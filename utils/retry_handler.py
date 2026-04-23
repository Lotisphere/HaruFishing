import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception

# 设置简单的日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_rate_limit_error(exception: Exception) -> bool:
    """
    判断是否是API限流错误 (429) 或配额超限
    """
    error_str = str(exception).lower()
    return "429" in error_str or "quota" in error_str or "rate limit" in error_str or "resource exhausted" in error_str

# 定义指数退避重试装饰器 (Exponential Backoff)
# 规则：如果遇到限流错误，等待时间呈指数级增长 (2s, 4s, 8s...)，最多重试 5 次，单次最长等待 30 秒。
gemini_retry = retry(
    retry=retry_if_exception(is_rate_limit_error),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    stop=stop_after_attempt(5),
    before_sleep=lambda retry_state: logger.warning(
        f"⚠️ 触发 Gemini API 限流保护 (429)! 正在进行第 {retry_state.attempt_number} 次等待，"
        f"将在 {retry_state.next_action.sleep} 秒后进行下一次重试..."
    )
)
