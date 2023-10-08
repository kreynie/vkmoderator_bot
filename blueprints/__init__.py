from .admin import admin_labeler
from .common import common_labeler
from .help import help_labeler
from .lead import lead_labeler
from .legal import lt_labeler
from .legal_extended import ltl_labeler
from .mailing import mailing_labeler
from .moderator import moderator_labeler
from .moderator_extended import moderator_extended_labeler

labelers = [
    admin_labeler,
    lead_labeler,
    moderator_extended_labeler,
    moderator_labeler,
    help_labeler,
    mailing_labeler,
    lt_labeler,
    ltl_labeler,
    common_labeler,
]

__all__ = [*labelers]
