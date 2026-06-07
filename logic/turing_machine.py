# turing_machine.py
"""Turing Machine implementation for traffic‑light simulation.

The machine is defined as a 7‑tuple:
    M = (Q, Σ, Γ, δ, q0, B, F)
where
    Q   = {q0, q1, q2}                # states (Red, Yellow, Green)
    Σ   = {"M", "K", "H"}           # input alphabet (red, yellow, green)
    Γ   = {"M", "K", "H", "B"}    # tape alphabet (includes blank)
    δ   = transition function (see TRANSITIONS dict)
    q0  = "q0" (initial state – Red)
    B   = "B"  (blank symbol – unused in this simple simulation)
    F   = set()   (no final state – it loops forever)

The transition table (δ) mirrors the traffic‑light cycle:
    q0 (Red) reads "M" → write "K", move right, next state q1 (Yellow)
    q1 (Yellow) reads "K" → write "H", move right, next state q2 (Green)
    q2 (Green) reads "H" → write "M", move right, next state q0 (Red)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple

State = str
Symbol = str

# Transition mapping: (current_state, read_symbol) -> (next_state, write_symbol, move)
# move is "L", "R" or "S" (stay). For this demo we always move right.
TRANSITIONS: Dict[Tuple[State, Symbol], Tuple[State, Symbol, str]] = {
    ("q0", "M"): ("q1", "K", "R"),
    ("q1", "K"): ("q2", "H", "R"),
    ("q2", "H"): ("q0", "M", "R"),
}

@dataclass
class TuringMachine:
    """Minimal Turing‑machine for the traffic‑light automaton.

    The machine maintains only the current state because the tape is not needed
    for the visual simulation – the tape symbols correspond exactly to the
    colour of the current light.
    """

    state: State = "q0"  # start at Red

    def step(self) -> State:
        """Perform one transition and return the new state.

        The method looks up the transition based on the current state and the
        symbol that represents that state (M, K, H). It then updates the internal
        state and returns it.
        """
        # Map internal state to the symbol it "writes" on the tape.
        symbol_map = {"q0": "M", "q1": "K", "q2": "H"}
        current_symbol = symbol_map[self.state]
        key = (self.state, current_symbol)
        if key not in TRANSITIONS:
            raise RuntimeError(f"No transition defined for {key}")
        next_state, _write_symbol, _move = TRANSITIONS[key]
        self.state = next_state
        return self.state

    def current_color(self) -> str:
        """Return the colour name associated with the current state.

        Returns one of "red", "yellow", "green" – convenient for the GUI.
        """
        return {"q0": "red", "q1": "yellow", "q2": "green"}[self.state]

if __name__ == "__main__":
    # Simple sanity test when the file is executed directly.
    tm = TuringMachine()
    for _ in range(6):
        print(f"State: {tm.state}, colour: {tm.current_color()}")
        tm.step()

