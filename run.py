# run.py
"""Entry point to start the Turing‑machine traffic‑light simulation.

Run with:
    python run.py
"""

from traffic_gui import TrafficGUI

if __name__ == "__main__":
    gui = TrafficGUI()
    gui.run()
