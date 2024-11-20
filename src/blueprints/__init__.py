__all__ = (
    "labelers",
)

from .admin import labeler as admin_labeler
from .chat_actions import chat_actions_labeler
from .common import labeler as common_labeler
from .help import labeler as help_labeler
from .moderator import labeler as moderator_labeler
from .moderator_extended import labeler as moderator_ext_labeler
from .rules import CheckPermissions

# Initializing changes in base labeler behavior and applying them.
# All imported labelers are added to set to exclude repeats
labelers = {
    admin_labeler,
    chat_actions_labeler,
    moderator_ext_labeler,
    moderator_labeler,
    help_labeler,
    common_labeler,
}
