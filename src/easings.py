import math


def ease_out_expo(x: float) -> float:
    """指数缓动 - 快速开始，逐渐减速"""
    if x == 1:
        return 1
    return 1 - math.pow(2, -10 * x)


def ease_in_out_quad(x: float) -> float:
    """二次缓动 - 开始和结束都缓慢，中间快速"""
    if x < 0.5:
        return 2 * x * x
    return -1 + (4 - 2 * x) * x


def ease_in_cubic(x: float) -> float:
    """三次缓动 - 开始缓慢，逐渐加速"""
    return x * x * x


def ease_out_cubic(x: float) -> float:
    """三次缓动 - 快速开始，逐渐减速"""
    x = x - 1
    return x * x * x + 1


def ease_in_sine(x: float) -> float:
    """正弦缓动 - 开始缓慢"""
    return 1 - math.cos((x * math.pi) / 2)


def ease_out_sine(x: float) -> float:
    """正弦缓动 - 结束缓慢"""
    return math.sin((x * math.pi) / 2)
