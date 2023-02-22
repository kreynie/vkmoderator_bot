from helpfuncs.jsonfunctions import JSONHandler
from .states import AIState


json_handler = JSONHandler("ai.json")


class AIHandler:
    def __init__(self):
        self.state = json_handler.get_data().get("state")

    @property
    async def ai_state(self):
        return self.state

    @ai_state.getter
    async def get(self) -> int:
        return self.state

    @ai_state.setter
    async def set(self, state: AIState) -> None:
        self.state = state.value
        json_handler.save_data({"state": self.state})

    async def switch(self) -> AIState:
        current_state = self.state
        next_status = (
            AIState.ACTIVE_STATE
            if current_state == AIState.DISABLED_STATE.value
            else AIState.DISABLED_STATE
        )
        self.state = next_status
        return self.state
