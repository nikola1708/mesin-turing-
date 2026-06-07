# Traffic‑Light Simulation via Turing Machine

## 📖 Overview
This tiny project demonstrates how a **Turing‑machine** can model an automatic traffic‑light system. Three states represent the lights:
- `q0` – Red (`M`)
- `q1` – Yellow (`K`)
- `q2` – Green (`H`)

The transition function cycles the machine forever: **Red → Yellow → Green → Red**. A **Tkinter** GUI visualises the current state with coloured circles.

---
## 🤖 Instructions for AI Assistants
- **Extending the automaton**: Add new states/symbols to `TRANSITIONS` in `turing_machine.py` and update `current_color` mapping. Adjust the GUI if new colours are needed.
- **Custom timing**: Pass a different `interval_ms` value when constructing `TrafficGUI` in `run.py` (e.g., `TrafficGUI(interval_ms=1500)`).
- **Testing**: Import `TuringMachine` in a test suite and assert the state sequence after a number of `step()` calls.
- **Packaging**: To turn this into a pip‑installable package, create `setup.cfg` and expose `run:main` as a console script.

---
## 👩‍💻 Human Setup & Usage
### Prerequisites
- Python **3.10+** (standard library only)
- No external dependencies

### Installation
```bash
# Clone the repository (or copy the files into a folder)
git clone <repo‑url>  # if hosted
cd <repo‑folder>
# (Optional) create a virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Run the simulation
```bash
python run.py
```
A window will appear with three circles; the active light glows while the others stay dim. The colours change automatically every second.

### Customising the interval
Edit `run.py` or launch manually:
```python
from traffic_gui import TrafficGUI
gui = TrafficGUI(interval_ms=2000)  # 2 seconds per state
gui.run()
```

### Quick sanity check
```bash
python -m turing_machine
```
You should see a printed sequence of states and colours.

