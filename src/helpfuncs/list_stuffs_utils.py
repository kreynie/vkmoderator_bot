from typing import Iterable, Literal

from src.schemas import Stuff
from src.services import StuffsService
from src.utils.enums import StuffGroups
from src.utils.unitofwork import IUnitOfWork


async def list_stuff_groups(
        uow: IUnitOfWork,
        stuff_group: StuffGroups,
        group_name: str,
        service: StuffsService
) -> str:
    leads = await service.get_stuffs(uow, group_id=stuff_group, allowance=3)
    others = await service.get_stuffs(uow, group_id=stuff_group, allowance__ne=3)
    result = ""
    if leads:
        result += get_stuffs_list(leads) + "\n\n"
    if others:
        result += get_stuffs_list(others)
    return f"{group_name} с правами у бота:\n{result if result else 'Ни у кого нет прав'}"


def get_stuffs_list(stuffs: Iterable[Stuff]) -> str:
    """
    Make list of strings with stuffs' info from Stuff objects

    :param stuffs: Iterable of Stuff
    :return: @id<stuff.user.id> (<stuff.user.full_name>) (<prefix><stuff.key>)
    """
    r = []
    sorted_by_key_stuffs = sorted(stuffs, key=lambda s: s.key)
    for stuff in sorted_by_key_stuffs:
        if stuff.key > 0:
            prefix = get_stuff_prefix(stuff.allowance, "МВ")
            r.append(
                f"@id{stuff.user.id}"
                f"({stuff.user.full_name}) "
                f"({prefix}{stuff.key})"
            )

    return "\n".join(r)


def get_stuff_prefix(allowance: int, prefix_base: Literal["МВ"]) -> str:
    return "S" + prefix_base if allowance == 3 else prefix_base
