from .admin import admin_labeler
from .help import help_labeler
from .lead import lead_labeler
from .mailing import mailing_labeler
from .moderator import moderator_labeler
from .moderator_extended import supmoder_labeler

from .autoai import ai_labeler


labelers = [
    admin_labeler,
    lead_labeler,
    supmoder_labeler,
    moderator_labeler,
    help_labeler,
    mailing_labeler,
    ai_labeler,
]

__all__ = [*labelers]
