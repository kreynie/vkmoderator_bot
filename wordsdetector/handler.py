from helpfuncs.jsonfunctions import JSONHandler
from .states import AIState


class AIHandler:
    def __init__(self):
        self.json_handler = JSONHandler("ai.json")

    async def get_ai_state(self) -> int:
        ai_state = await self.json_handler.get_data()
        return ai_state.get("state")

    async def set_ai_state(self, state: AIState) -> None:
        await self.json_handler.save_data("ai.json", {"state": state.value})

    async def switch_ai_state(self) -> AIState:
        current_state = await self.json_handler.get_ai_state()
        next_status = (
            AIState.ACTIVE_STATE
            if current_state == AIState.DISABLED_STATE.value
            else AIState.DISABLED_STATE
        )
        await self.set_ai_state(next_status)
        return next_status
