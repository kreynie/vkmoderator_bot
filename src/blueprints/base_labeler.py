from vkbottle.user import UserLabeler
from .rules import CheckPermissions

labeler = UserLabeler()
labeler.vbml_ignore_case = True
labeler.custom_rules["access"] = CheckPermissions
