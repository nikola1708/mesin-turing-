from dataclasses import dataclass
"""turing_machine.py

Smart Turing‑machine model for a 3‑way traffic intersection. The machine
explicitly exposes usual TM primitives: state, tape, head, BLANK, read,
write, move_right, move_left and a transition function.

States (logical):
  q0 = Generate Traffic Data
  q1 = Jalan A Hijau
  q2 = Jalan A Kuning
  q3 = Jalan B Hijau
  q4 = Jalan B Kuning
  q5 = Jalan C Hijau
  q6 = Jalan C Kuning

The tape stores vehicle counts as tokens: e.g. ["12","|","5","|","18"].
Head points to a token index. read()/write() operate on tokens. move_right/
move_left shift the head between tokens. Each time the machine enters q0 it
generates new random traffic counts for A,B,C.
"""

from dataclasses import dataclass, field
from typing import List
import random


BLANK = "B"


@dataclass
class TuringMachine:
    state: str = "q0"
    tape: List[str] = field(default_factory=list)
    head: int = 0
    vehicles: List[int] = field(default_factory=lambda: [0, 0, 0])
    # fixed green duration (seconds) for all roads when green
    green_seconds: int = 4
    # order of roads to serve this cycle (list of indices 0=A,1=B,2=C)
    order: List[int] = field(default_factory=lambda: [0, 1, 2])

    def __post_init__(self):
        # initialise with generated traffic so UI shows values immediately
        self._generate_traffic()

    # -------------------- Turing primitives --------------------
    def read(self):
        """Return the token under the head."""
        if 0 <= self.head < len(self.tape):
            return self.tape[self.head]
        return BLANK

    def write(self, symbol: str):
        """Write a token at the head position."""
        if 0 <= self.head < len(self.tape):
            self.tape[self.head] = symbol
        else:
            # extend tape if head is out of bounds
            # keep behaviour simple: append symbol
            self.tape.append(symbol)

    def move_right(self):
        """Move the head to the right (token index)."""
        if self.head < len(self.tape) - 1:
            self.head += 1

    def move_left(self):
        """Move the head to the left (token index)."""
        if self.head > 0:
            self.head -= 1

    def scan_tape(self):
        """
        Simulasi operasi Turing Machine:
        read, write, move_right, move_left
        """

        self.head = 0

        # Read Jalur A
        a = int(self.read())

        self.move_right()
        self.move_right()

        # Read Jalur B
        b = int(self.read())

        self.move_right()
        self.move_right()

        # Read Jalur C
        c = int(self.read())

        # Write (menulis ulang simbol yang sedang dibaca)
        current = self.read()
        self.write(current)

        # Kembali ke awal tape
        while self.head > 0:
            self.move_left()

        # Tentukan prioritas
        self.order = sorted(
            [0, 1, 2],
            key=lambda i: [a, b, c][i],
            reverse=True
        )


    # -------------------- Tape / traffic helpers --------------------
    def _generate_traffic(self):
        """Create random vehicle counts and rebuild the tape tokens."""
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        c = random.randint(1, 20)
        self.vehicles = [a, b, c]
        # tape tokens: ["A","|","B","|","C"] where A/B/C are counts
        self.tape = [str(a), "|", str(b), "|", str(c)]
        # position head at start (A)
        self.head = 0
        # Menentukan prioritas melalui proses TM
        self.scan_tape()



    def get_tape_str(self) -> str:
        return "".join(self.tape)

    def head_char_index(self) -> int:
        """Return character index (for display) of the start of the token
        currently under the head."""
        idx = 0
        for i in range(self.head):
            idx += len(self.tape[i])
        return idx

    # -------------------- State logic / transitions --------------------
    def current_color_map(self):
        """Return per-road color mapping for the current state.

        Returns a dict: {"A":"red|yellow|green", "B":..., "C":...}
        """
        # map states to which ordered road they represent
        # q1/q2 -> first in order, q3/q4 -> second, q5/q6 -> third
        mapping = {"A": "red", "B": "red", "C": "red"}
        if self.state in ("q1", "q2"):
            idx = self.order[0]
            road = ["A", "B", "C"][idx]
            mapping[road] = "green" if self.state == "q1" else "yellow"
            return mapping
        if self.state in ("q3", "q4"):
            idx = self.order[1]
            road = ["A", "B", "C"][idx]
            mapping[road] = "green" if self.state == "q3" else "yellow"
            return mapping
        if self.state in ("q5", "q6"):
            idx = self.order[2]
            road = ["A", "B", "C"][idx]
            mapping[road] = "green" if self.state == "q5" else "yellow"
            return mapping
        # q0: generating — treat as all red for safety
        return mapping

    def current_duration_ms(self) -> int:
        """Return how long (ms) the current state should be displayed.

        Green durations depend on the vehicle count for the road being
        served: >10 vehicles -> 8s, otherwise 5s. Yellow states are 1s.
        q0 remains a short pause (800ms).
        """
        if self.state in ("q1", "q3", "q5"):

            if self.state == "q1":
                road_idx = self.order[0]

            elif self.state == "q3":
                road_idx = self.order[1]

            else:
                road_idx = self.order[2]

            vehicle_count = self.vehicles[road_idx]

            if vehicle_count > 10:
                return 8000
            else:
                return 5000

        if self.state in ("q2", "q4", "q6"):
            return 1000

        return 800

    def step(self) -> str:
        """Advance the TM to the next logical state. When entering q0 the
        machine generates new random traffic counts (tape is rebuilt).

        Returns the new state.
        """
        if self.state == "q0":
            # generate traffic and compute serving order when q0 is entered
            self._generate_traffic()
            # after generating, go to the first green state (q1)
            self.state = "q1"
            # set head to the token index for the first served road
            first_idx = self.order[0]
            self.head = first_idx * 2
        elif self.state == "q1":
            self.state = "q2"
            # keep head on same token (yellow for first road)
            first_idx = self.order[0]
            self.head = first_idx * 2
        elif self.state == "q2":
            self.state = "q3"
            # move head to second road start
            second_idx = self.order[1]
            self.head = second_idx * 2
        elif self.state == "q3":
            self.state = "q4"
            # keep head on second road (yellow)
            second_idx = self.order[1]
            self.head = second_idx * 2
        elif self.state == "q4":
            self.state = "q5"
            # move head to third road
            third_idx = self.order[2]
            self.head = third_idx * 2
        elif self.state == "q5":
            self.state = "q6"
            # keep head on third road (yellow)
            third_idx = self.order[2]
            self.head = third_idx * 2
        else:
            # q6 -> q0
            self.state = "q0"
            # reset head to start (will be repositioned when q0 generates new traffic)
            self.head = 0
        return self.state


if __name__ == "__main__":
    tm = TuringMachine()
    # quick simulation printout
    for _ in range(10):
        print(f"State={tm.state} | Tape={tm.get_tape_str()} | Head={tm.head} | Vehicles={tm.vehicles}")
        # show duration and color map
        print("Colors:", tm.current_color_map(), "Duration_ms:", tm.current_duration_ms())
        tm.step()
    for i in range(15):

        print(
            f"State={tm.state} | "
            f"Tape={tm.get_tape_str()} | "
            f"Head={tm.head} | "
        )

        tm.step()