"""
错误处理和重试机制
"""
import asyncio
import random
from typing import Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')


class RetryConfig:
    """重试配置"""
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """计算退避延迟（指数退避 + 抖动）"""
    delay = min(
        config.base_delay * (config.exponential_base ** attempt),
        config.max_delay
    )
    # 添加随机抖动，避免惊群效应
    jitter = random.uniform(0, delay * 0.1)
    return delay + jitter


async def retry_async(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    *args,
    **kwargs
) -> T:
    """
    异步函数重试包装器

    Args:
        func: 要执行的异步函数
        config: 重试配置
        *args, **kwargs: 传递给 func 的参数

    Returns:
        函数返回值

    Raises:
        最后一次异常
    """
    config = config or RetryConfig()
    last_exception = None

    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except config.retryable_exceptions as e:
            last_exception = e

            if attempt < config.max_retries:
                delay = calculate_delay(attempt, config)
                print(f"  ⚠️  Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}")
                print(f"     Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"  ❌ All {config.max_retries + 1} attempts failed")

    raise last_exception


class CircuitBreaker:
    """
    熔断器模式

    防止连续失败请求拖垮系统
    """
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        self.half_open_calls = 0

    def can_execute(self) -> bool:
        """检查是否可以执行请求"""
        if self.state == "closed":
            return True

        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
                self.half_open_calls = 0
                return True
            return False

        if self.state == "half_open":
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False

        return True

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试恢复"""
        if self.last_failure_time is None:
            return True

        import time
        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def record_success(self):
        """记录成功"""
        self.failures = 0
        self.state = "closed"
        self.half_open_calls = 0

    def record_failure(self):
        """记录失败"""
        import time
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            print(f"  🔴 Circuit breaker open: {self.failures} consecutive failures")


# API 特定的重试配置
EXA_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    retryable_exceptions=(
        asyncio.TimeoutError,
        ConnectionError,
        Exception  # aiohttp 异常
    )
)

BING_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    base_delay=0.5,
    retryable_exceptions=(
        asyncio.TimeoutError,
        ConnectionError,
    )
)
