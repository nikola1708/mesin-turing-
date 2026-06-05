# traffic_gui.py
"""Tkinter based GUI for the traffic‑light Turing‑machine simulation.

The GUI displays three coloured circles (red, yellow, green). Only the circle
representing the current state is filled with its colour; the others are shown
as dark‑grey outlines. The simulation advances automatically using the
`TuringMachine` defined in `turing_machine.py`.
"""

import tkinter as tk
from typing import Dict

# Local import – the path will be resolved because both modules are in the same
# project directory.
from turing_machine import TuringMachine


class TrafficGUI:
    """Encapsulates the tkinter window and animation loop.

    The animation interval (in milliseconds) can be tweaked via the
    `interval_ms` argument. For a simple demo we use 1000 ms (1 s) per state.
    """

    def __init__(self, interval_ms: int = 1000):
        self.root = tk.Tk()
        self.root.title("Turing‑Machine Traffic Light")
        self.root.configure(bg="#2b2b2b")  # dark background for premium feel

        # Canvas size – enough room for three circles horizontally.
        self.canvas = tk.Canvas(self.root, width=300, height=120, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # Positions for the three lights.
        self.light_coords = {
            "red": (30, 30, 80, 80),
            "yellow": (110, 30, 160, 80),
            "green": (190, 30, 240, 80),
        }
        # Store canvas item IDs for later colour updates.
        self.light_items: Dict[str, int] = {}
        for colour, coords in self.light_coords.items():
            # Outline circles with a dark fill initially.
            item = self.canvas.create_oval(*coords, fill="#4f4f4f", outline="#111", width=2)
            self.light_items[colour] = item

        # Turing machine instance.
        self.tm = TuringMachine()
        self.interval_ms = interval_ms
        # Start the looping animation.
        self.root.after(0, self._update_light)

    def _update_light(self) -> None:
        """Refresh the GUI to reflect the current state and schedule the next step.
        The duration depends on the colour that is currently active.
        """
        # Determine which colour should be active.
        active_colour = self.tm.current_color()
        # Update fills.
        for colour, item_id in self.light_items.items():
            fill = colour if colour == active_colour else "#4f4f4f"
            self.canvas.itemconfig(item_id, fill=fill)
        # Define per‑state durations in milliseconds.
        duration_map = {"red": 4000, "yellow": 1000, "green": 4000}
        # Advance the Turing machine for the next cycle.
        self.tm.step()
        # Schedule next update using the duration of the colour we just displayed.
        next_interval = duration_map.get(active_colour, 1000)
        self.root.after(next_interval, self._update_light)

    def run(self) -> None:
        """Enter the tkinter main loop."""
        self.root.mainloop()


if __name__ == "__main__":
    # Quick demo when the file is executed directly.
    gui = TrafficGUI()
    gui.run()
