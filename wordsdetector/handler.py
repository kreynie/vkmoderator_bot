from helpfuncs import JSONHandler

from .states import AIState

json_handler = JSONHandler("ai.json")


class AIHandler:
    def __init__(self):
        self.state = json_handler.get_data().get("state")

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: AIState | int) -> None:
        if isinstance(state, int):
            state = AIState(state)
        self._state = state
        json_handler.save_data({"state": self.state.value})

    def switch(self) -> AIState:
        current_state = self.state
        next_status = (
            AIState.ACTIVE if current_state == AIState.DISABLED else AIState.DISABLED
        )
        self.state = next_status
        return self.state
