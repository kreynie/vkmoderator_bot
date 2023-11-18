__all__ = (
    "BannerInfo",
    "BanRegistrationInfo",
    "LegalBanRegistrationInfo",
    "Stuff",
    "User",
    "VKObjectInfo",
)


from .object_validators import BannerInfo, VKObjectInfo
from .registration import BanRegistrationInfo, LegalBanRegistrationInfo
from .stuff import Stuff
from .user import User
