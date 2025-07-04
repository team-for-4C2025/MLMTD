from pydantic import BaseModel


class HistoryRequest(BaseModel):
    """
    请求以往的恶意流浪攻击数据
    请求可能是 'min', 'hour', 'day'
    """
    dtype: str
