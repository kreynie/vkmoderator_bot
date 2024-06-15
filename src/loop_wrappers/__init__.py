__all__ = (
    "loop_wrappers",
    "vk_loop_wrapper",
)

from .hot_issues_checkout import vk_loop_wrapper as hot_issues_checkout_wrapper
from .infinite_online import vk_loop_wrapper as infinite_online_wrapper
from .loop_wrapper import vk_loop_wrapper

loop_wrappers = [
    hot_issues_checkout_wrapper,
    infinite_online_wrapper,
]
