import tkinter as tk
from typing import Dict

from logic.turing_machine import TuringMachine


class TrafficGUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Turing Machine Traffic Light")
        self.root.configure(bg="#2b2b2b")

        # ==========================
        # Canvas Lampu
        # ==========================

        self.canvas = tk.Canvas(
            self.root,
            width=320,
            height=140,
            bg="#2b2b2b",
            highlightthickness=0
        )

        self.canvas.pack(pady=20)

        self.light_coords = {
            "red": (30, 30, 90, 90),
            "yellow": (130, 30, 190, 90),
            "green": (230, 30, 290, 90),
        }

        self.light_items: Dict[str, int] = {}

        for colour, coords in self.light_coords.items():

            item = self.canvas.create_oval(
                *coords,
                fill="#4f4f4f",
                outline="#111",
                width=2
            )

            self.light_items[colour] = item

        # ==========================
        # Label State
        # ==========================

        self.state_label = tk.Label(
            self.root,
            text="",
            font=("Consolas", 12, "bold"),
            fg="white",
            bg="#2b2b2b"
        )

        self.state_label.pack()

        # ==========================
        # Label Tape
        # ==========================

        self.tape_label = tk.Label(
            self.root,
            text="",
            font=("Consolas", 16),
            fg="cyan",
            bg="#2b2b2b"
        )

        self.tape_label.pack(pady=10)

        # ==========================
        # TM
        # ==========================

        self.tm = TuringMachine()

        self.root.after(0, self._update_light)

    def _update_light(self):

        active_colour = self.tm.current_color()

        # Lampu aktif
        for colour, item_id in self.light_items.items():

            fill = colour if colour == active_colour else "#4f4f4f"

            self.canvas.itemconfig(
                item_id,
                fill=fill
            )

        # ==========================
        # State
        # ==========================

        self.state_label.config(
            text=f"Current State : {self.tm.state}"
        )

        # ==========================
        # Tape + Head
        # ==========================

        tape = self.tm.tape_content()

        head = self.tm.head_position()

        visual = ""

        for i, symbol in enumerate(tape):

            if i == head:
                visual += f"[{symbol}]"

            else:
                visual += f" {symbol} "

        if head >= len(tape):
            visual += " [END]"

        self.tape_label.config(
            text=f"Tape : {visual}"
        )

        # Jalankan TM
        self.tm.step()

        # 1 detik sekali
        self.root.after(
            1000,
            self._update_light
        )

    def run(self):

        self.root.mainloop()


if __name__ == "__main__":

    gui = TrafficGUI()
    gui.run()