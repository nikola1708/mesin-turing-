import time
import tkinter as tk
from typing import Dict, Optional, Tuple

from logic.turing_machine import TuringMachine


class TrafficGUI:
    BG = "#101114"
    PANEL = "#181b20"
    PANEL_ALT = "#20242b"
    BORDER = "#343a43"
    TEXT = "#f3f4f6"
    MUTED = "#a8b0bb"
    SOFT = "#747d8a"
    RED = "#f05252"
    YELLOW = "#f5c542"
    GREEN = "#34d399"
    CYAN = "#4cc9f0"
    ROAD = "#5d636b"
    ROAD_EDGE = "#858c96"
    LANE_MARK = "#e5e7eb"

    ROAD_NAMES = ["A", "B", "C"]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Turing Traffic Light")
        self.root.geometry("840x790")
        self.root.minsize(840, 790)
        self.root.configure(bg=self.BG)

        self.tm = TuringMachine()

        self.visible_colors: Dict[str, str] = {"A": "red", "B": "red", "C": "red"}
        self.visible_counts = [0, 0, 0]
        self.visible_order = [0, 1, 2]
        self.visible_state = "q0"
        self.visible_head_token = 0
        self.visible_duration_ms = 1
        self.visible_started_at = time.perf_counter()
        self.hovered_road: Optional[str] = None

        self.road_items: Dict[str, Dict[str, object]] = {}
        self.road_hit_boxes: Dict[str, Tuple[int, int, int, int]] = {}
        self.map_light_items: Dict[str, Dict[str, object]] = {}
        self.map_count_labels: Dict[str, int] = {}
        self.map_route_lines: Dict[str, int] = {}
        self.map_cars: Dict[str, list] = {}
        self.map_queue_points: Dict[str, list] = {}
        self.map_motion_paths: Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]] = {}
        self.state_nodes: Dict[str, int] = {}
        self.state_texts: Dict[str, int] = {}
        self.state_road_labels: Dict[str, int] = {}

        self._build_layout()

        self.root.after(0, self._update)
        self.root.after(80, self._animate_progress)

    def _build_layout(self):
        shell = tk.Frame(self.root, bg=self.BG)
        shell.pack(fill="both", expand=True, padx=18, pady=16)

        header = tk.Frame(shell, bg=self.BG)
        header.pack(fill="x", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        title_block = tk.Frame(header, bg=self.BG)
        title_block.grid(row=0, column=0, sticky="w")

        tk.Label(
            title_block,
            text="Smart Turing Traffic Light",
            fg=self.TEXT,
            bg=self.BG,
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_block,
            text="Simulasi persimpangan A | B | C berbasis state machine",
            fg=self.MUTED,
            bg=self.BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(3, 0))

        status = tk.Frame(header, bg=self.PANEL, highlightbackground=self.BORDER, highlightthickness=1)
        status.grid(row=0, column=1, sticky="e")

        self.state_label = tk.Label(
            status,
            text="Current State: q0",
            fg=self.TEXT,
            bg=self.PANEL,
            font=("Consolas", 12, "bold"),
            padx=16,
            pady=8,
        )
        self.state_label.pack(anchor="e")

        self.duration_label = tk.Label(
            status,
            text="0.0s",
            fg=self.MUTED,
            bg=self.PANEL,
            font=("Segoe UI", 9),
            padx=16,
        )
        self.duration_label.pack(anchor="e", pady=(0, 7))

        self.progress = tk.Canvas(status, width=188, height=9, bg=self.PANEL, highlightthickness=0)
        self.progress.pack(padx=16, pady=(0, 12))
        self.progress_track = self.progress.create_rectangle(0, 2, 188, 7, fill="#2b3037", outline="")
        self.progress_fill = self.progress.create_rectangle(0, 2, 0, 7, fill=self.CYAN, outline="")

        self.canvas = tk.Canvas(shell, width=790, height=515, bg=self.PANEL, highlightthickness=0)
        self.canvas.pack(fill="x")
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Leave>", self._on_canvas_leave)

        self._draw_main_canvas()

        footer = tk.Frame(shell, bg=self.BG)
        footer.pack(fill="x", pady=(12, 0))

        self.info_label = tk.Label(
            footer,
            text="Arah layanan akan mengikuti jumlah kendaraan terbanyak.",
            fg=self.MUTED,
            bg=self.BG,
            font=("Segoe UI", 10),
        )
        self.info_label.pack(anchor="w", pady=(0, 8))

        self.tape_canvas = tk.Canvas(footer, width=790, height=112, bg=self.PANEL, highlightthickness=0)
        self.tape_canvas.pack(fill="x")

    def _draw_main_canvas(self):
        self.canvas.create_rectangle(0, 0, 790, 515, fill=self.PANEL, outline="")

        self.canvas.create_text(
            28,
            24,
            anchor="w",
            text="Peta Persimpangan",
            fill=self.TEXT,
            font=("Segoe UI", 14, "bold"),
        )
        self.canvas.create_text(
            28,
            46,
            anchor="w",
            text="Tiga lampu di peta ini bergerak mengikuti state machine yang sama.",
            fill=self.MUTED,
            font=("Segoe UI", 9),
        )

        self._draw_intersection_map()

        card_tops = {"A": 76, "B": 170, "C": 264}
        for road, top in card_tops.items():
            self._draw_compact_road_card(road, 662, top, 188, 76)

        self.canvas.create_line(34, 383, 756, 383, fill="#2a2f37", width=1)
        self.canvas.create_text(
            28,
            399,
            anchor="w",
            text="State Diagram",
            fill=self.TEXT,
            font=("Segoe UI", 13, "bold"),
        )
        self._draw_state_diagram()

    def _draw_intersection_map(self):
        left, top, right, bottom = 36, 76, 540, 358
        center_x, center_y = 288, 212

        self._round_rect(self.canvas, left, top, right, bottom, 8, fill="#1d2229", outline=self.BORDER, width=1)
        self.canvas.create_text(
            left + 18,
            top + 18,
            anchor="w",
            text="Persimpangan Tiga Arah",
            fill=self.TEXT,
            font=("Segoe UI", 11, "bold"),
        )
        self.canvas.create_text(
            right - 18,
            top + 18,
            anchor="e",
            text="1 lampu hijau aktif",
            fill=self.MUTED,
            font=("Segoe UI", 9),
        )

        road_left, road_right = left + 26, right - 26
        road_bottom = bottom - 18
        road_half = 48

        self.canvas.create_rectangle(
            road_left,
            center_y - road_half,
            road_right,
            center_y + road_half,
            fill=self.ROAD,
            outline=self.ROAD_EDGE,
            width=2,
        )
        self.canvas.create_rectangle(
            center_x - road_half,
            center_y - 2,
            center_x + road_half,
            road_bottom,
            fill=self.ROAD,
            outline=self.ROAD_EDGE,
            width=2,
        )
        self.canvas.create_rectangle(
            center_x - road_half,
            center_y - road_half,
            center_x + road_half,
            center_y + road_half,
            fill=self.ROAD,
            outline="",
        )

        self.canvas.create_line(
            road_left + 8,
            center_y,
            road_right - 8,
            center_y,
            fill=self.LANE_MARK,
            width=2,
            dash=(12, 10),
        )
        self.canvas.create_line(
            center_x,
            center_y + 34,
            center_x,
            road_bottom - 8,
            fill=self.LANE_MARK,
            width=2,
            dash=(12, 10),
        )
        self.canvas.create_line(center_x - 66, center_y - road_half + 8, center_x - 66, center_y + road_half - 8, fill="#f8fafc", width=3)
        self.canvas.create_line(center_x + 66, center_y - road_half + 8, center_x + 66, center_y + road_half - 8, fill="#f8fafc", width=3)
        self.canvas.create_line(center_x - road_half + 8, center_y + 66, center_x + road_half - 8, center_y + 66, fill="#f8fafc", width=3)

        self.map_route_lines["A"] = self.canvas.create_line(
            center_x,
            road_bottom - 30,
            center_x,
            center_y + 26,
            fill=self.GREEN,
            width=4,
            arrow="last",
            dash=(10, 8),
            state="hidden",
        )
        self.map_route_lines["B"] = self.canvas.create_line(
            center_x - 90,
            center_y + 24,
            center_x - 52,
            center_y + 24,
            fill=self.GREEN,
            width=4,
            arrow="last",
            dash=(10, 8),
            state="hidden",
        )
        self.map_route_lines["C"] = self.canvas.create_line(
            center_x + 90,
            center_y - 24,
            center_x + 52,
            center_y - 24,
            fill=self.GREEN,
            width=4,
            arrow="last",
            dash=(10, 8),
            state="hidden",
        )

        self.canvas.create_line(center_x, road_bottom - 22, center_x, center_y + 78, fill="#111827", width=2, dash=(4, 7), arrow="last")
        self.canvas.create_line(road_left + 32, center_y + 20, center_x - 84, center_y + 20, fill="#111827", width=2, dash=(4, 7), arrow="last")
        self.canvas.create_line(road_right - 32, center_y - 20, center_x + 84, center_y - 20, fill="#111827", width=2, dash=(4, 7), arrow="last")

        self.canvas.create_text(center_x, road_bottom - 10, text="Jalan A", fill=self.TEXT, font=("Segoe UI", 10, "bold"))
        self.canvas.create_text(road_left + 56, center_y - 62, text="Jalan B", fill=self.TEXT, font=("Segoe UI", 10, "bold"))
        self.canvas.create_text(road_right - 56, center_y - 62, text="Jalan C", fill=self.TEXT, font=("Segoe UI", 10, "bold"))

        self.map_count_labels["A"] = self.canvas.create_text(center_x + 86, road_bottom - 22, text="0 kendaraan", fill=self.MUTED, font=("Consolas", 9, "bold"))
        self.map_count_labels["B"] = self.canvas.create_text(road_left + 82, center_y + 56, text="0 kendaraan", fill=self.MUTED, font=("Consolas", 9, "bold"))
        self.map_count_labels["C"] = self.canvas.create_text(road_right - 82, center_y + 56, text="0 kendaraan", fill=self.MUTED, font=("Consolas", 9, "bold"))

        self._draw_map_traffic_light("A", center_x - 86, center_y + 64)
        self._draw_map_traffic_light("B", center_x - 122, center_y - 92)
        self._draw_map_traffic_light("C", center_x + 94, center_y - 92)
        self._draw_map_cars(center_x, center_y, road_left, road_right, road_bottom)

    def _draw_map_traffic_light(self, road: str, x: int, y: int):
        self._round_rect(self.canvas, x, y, x + 31, y + 72, 5, fill="#111318", outline="#2f3742", width=1)
        self.canvas.create_text(x + 15, y - 9, text=f"L{road}", fill=self.MUTED, font=("Segoe UI", 8, "bold"))

        lights: Dict[str, int] = {}
        halos: Dict[str, int] = {}
        rows = [("red", y + 14), ("yellow", y + 36), ("green", y + 58)]
        for color_name, cy in rows:
            halos[color_name] = self.canvas.create_oval(x + 3, cy - 12, x + 27, cy + 12, fill="#1d2229", outline="", state="hidden")
            lights[color_name] = self.canvas.create_oval(x + 8, cy - 7, x + 22, cy + 7, fill="#303741", outline="#687180", width=1)

        self.map_light_items[road] = {"lights": lights, "halos": halos}

    def _draw_map_cars(self, center_x: int, center_y: int, road_left: int, road_right: int, road_bottom: int):
        car_colors = ["#60a5fa", "#f97316", "#a78bfa", "#22c55e", "#f43f5e"]
        self.map_queue_points = {
            "A": [
                (center_x, road_bottom - 30),
                (center_x - 22, road_bottom - 14),
                (center_x + 22, road_bottom - 14),
                (center_x - 22, road_bottom - 38),
                (center_x + 22, road_bottom - 38),
            ],
            "B": [
                (center_x - 90, center_y + 24),
                (center_x - 130, center_y + 24),
                (center_x - 170, center_y + 24),
                (center_x - 210, center_y + 24),
                (center_x - 250, center_y + 24),
            ],
            "C": [
                (center_x + 90, center_y - 24),
                (center_x + 130, center_y - 24),
                (center_x + 170, center_y - 24),
                (center_x + 210, center_y - 24),
                (center_x + 250, center_y - 24),
            ],
        }
        self.map_motion_paths = {
            "A": ((center_x, road_bottom - 30), (center_x, center_y + 26)),
            "B": ((center_x - 90, center_y + 24), (center_x - 52, center_y + 24)),
            "C": ((center_x + 90, center_y - 24), (center_x + 52, center_y - 24)),
        }

        for road, positions in self.map_queue_points.items():
            self.map_cars[road] = []
            for idx, (x, y) in enumerate(positions):
                car_id = self._create_map_car(road, x, y, car_colors[idx])
                self.map_cars[road].append(car_id)

    def _create_map_car(self, road: str, x: int, y: int, fill: str):
        if road == "A":
            points = self._rounded_rect_points(x - 7, y - 11, x + 7, y + 11, 4)
        else:
            points = self._rounded_rect_points(x - 14, y - 7, x + 14, y + 7, 4)
        return self.canvas.create_polygon(points, smooth=True, splinesteps=8, fill=fill, outline="#111827", width=1, state="hidden")

    def _place_map_car(self, road: str, car_id: int, x: float, y: float, active: bool):
        x = int(x)
        y = int(y)
        if road == "A":
            points = self._rounded_rect_points(x - 7, y - 11, x + 7, y + 11, 4)
        else:
            points = self._rounded_rect_points(x - 14, y - 7, x + 14, y + 7, 4)
        self.canvas.coords(car_id, *points)
        self.canvas.itemconfig(car_id, outline="#f8fafc" if active else "#111827", width=2 if active else 1)

    def _draw_compact_road_card(self, road: str, center_x: int, top: int, width: int, height: int):
        left = center_x - width // 2
        right = center_x + width // 2
        bottom = top + height
        self.road_hit_boxes[road] = (left, top, right, bottom)

        shadow = self._round_rect(self.canvas, left + 4, top + 4, right + 4, bottom + 4, 8, fill="#0c0d10", outline="")
        card = self._round_rect(self.canvas, left, top, right, bottom, 8, fill=self.PANEL_ALT, outline=self.BORDER, width=1)
        self.canvas.create_text(left + 16, top + 17, anchor="w", text=f"Jalan {road}", fill=self.TEXT, font=("Segoe UI", 11, "bold"))

        halos: Dict[str, int] = {}
        lights: Dict[str, int] = {}
        x = right - 30
        rows = [("red", top + 17), ("yellow", top + 37), ("green", top + 57)]
        for color_name, cy in rows:
            halos[color_name] = self.canvas.create_oval(x - 12, cy - 12, x + 12, cy + 12, fill=self.PANEL_ALT, outline="", state="hidden")
            lights[color_name] = self.canvas.create_oval(x - 7, cy - 7, x + 7, cy + 7, fill="#2e333a", outline="#59616e", width=1)

        status = self.canvas.create_text(left + 16, top + 39, anchor="w", text="MERAH", fill=self.RED, font=("Segoe UI", 9, "bold"))
        count = self.canvas.create_text(left + 78, top + 39, anchor="w", text=f"{road}: 0 kendaraan", fill=self.MUTED, font=("Consolas", 9, "bold"))
        bar_bg = self._round_rect(self.canvas, left + 16, bottom - 14, right - 56, bottom - 7, 4, fill="#2c3138", outline="")
        bar = self._round_rect(self.canvas, left + 16, bottom - 14, left + 16, bottom - 7, 4, fill=self.GREEN, outline="")

        self.road_items[road] = {
            "shadow": shadow,
            "card": card,
            "status": status,
            "halos": halos,
            "lights": lights,
            "count": count,
            "bar_bg": bar_bg,
            "bar": bar,
            "bar_left": left + 16,
            "bar_right": right - 56,
            "bar_top": bottom - 14,
            "bar_bottom": bottom - 7,
        }

    def _draw_road_card(self, road: str, center_x: int, top: int, width: int, height: int):
        left = center_x - width // 2
        right = center_x + width // 2
        bottom = top + height
        self.road_hit_boxes[road] = (left, top, right, bottom)

        shadow = self._round_rect(self.canvas, left + 4, top + 5, right + 4, bottom + 5, 8, fill="#0c0d10", outline="")
        card = self._round_rect(self.canvas, left, top, right, bottom, 8, fill=self.PANEL_ALT, outline=self.BORDER, width=1)

        self.canvas.create_text(
            center_x,
            top + 24,
            text=f"Jalan {road}",
            fill=self.TEXT,
            font=("Segoe UI", 13, "bold"),
        )
        status = self.canvas.create_text(
            center_x,
            top + 47,
            text="MERAH",
            fill=self.RED,
            font=("Segoe UI", 9, "bold"),
        )

        housing = self._round_rect(
            self.canvas,
            center_x - 31,
            top + 66,
            center_x + 31,
            top + 157,
            8,
            fill="#111318",
            outline="#3d434c",
            width=1,
        )

        halos: Dict[str, int] = {}
        lights: Dict[str, int] = {}
        light_rows = [("red", top + 86), ("yellow", top + 111), ("green", top + 136)]
        for color_name, y in light_rows:
            halos[color_name] = self.canvas.create_oval(
                center_x - 21,
                y - 21,
                center_x + 21,
                y + 21,
                fill=self.PANEL_ALT,
                outline="",
                state="hidden",
            )
            lights[color_name] = self.canvas.create_oval(
                center_x - 12,
                y - 12,
                center_x + 12,
                y + 12,
                fill="#2e333a",
                outline="#5a6270",
                width=1,
            )

        count = self.canvas.create_text(
            center_x,
            bottom - 42,
            text=f"{road}: 0 kendaraan",
            fill=self.TEXT,
            font=("Consolas", 12, "bold"),
        )

        bar_bg = self._round_rect(
            self.canvas,
            left + 30,
            bottom - 24,
            right - 30,
            bottom - 14,
            5,
            fill="#2c3138",
            outline="",
        )
        bar = self._round_rect(
            self.canvas,
            left + 30,
            bottom - 24,
            left + 30,
            bottom - 14,
            5,
            fill=self.GREEN,
            outline="",
        )

        self.road_items[road] = {
            "shadow": shadow,
            "card": card,
            "status": status,
            "housing": housing,
            "halos": halos,
            "lights": lights,
            "count": count,
            "bar_bg": bar_bg,
            "bar": bar,
            "bar_left": left + 30,
            "bar_right": right - 30,
            "bar_top": bottom - 24,
            "bar_bottom": bottom - 14,
        }

    def _draw_state_diagram(self):
        xs = [78, 184, 290, 396, 502, 608, 714]
        y = 466
        r = 19
        states = ["q0", "q1", "q2", "q3", "q4", "q5", "q6"]

        for i in range(len(xs) - 1):
            self.canvas.create_line(xs[i] + r, y, xs[i + 1] - r, y, fill="#48515c", width=2, arrow="last")

        self.canvas.create_line(
            xs[-1],
            y - r,
            xs[-1],
            y - 52,
            xs[0],
            y - 52,
            xs[0],
            y - r,
            fill="#48515c",
            width=2,
            arrow="last",
            smooth=True,
        )

        for i, st in enumerate(states):
            x = xs[i]
            cid = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#222832", outline="#515b68", width=1)
            tid = self.canvas.create_text(x, y, text=st, fill=self.MUTED, font=("Consolas", 10, "bold"))
            rlab = self.canvas.create_text(x, y + 30, text="", fill=self.SOFT, font=("Consolas", 9))
            self.state_nodes[st] = cid
            self.state_texts[st] = tid
            self.state_road_labels[st] = rlab

    def _rounded_rect_points(self, x1: int, y1: int, x2: int, y2: int, radius: int):
        return [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]

    def _round_rect(self, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, radius: int, **kwargs):
        points = self._rounded_rect_points(x1, y1, x2, y2, radius)
        return canvas.create_polygon(points, smooth=True, splinesteps=8, **kwargs)

    def _set_light_fill(self, road: str, color_name: str):
        mapping = {
            "red": (self.RED, "#4a2022", "MERAH"),
            "yellow": (self.YELLOW, "#4d3b17", "KUNING"),
            "green": (self.GREEN, "#153f31", "HIJAU"),
            "off": ("#2e333a", self.PANEL_ALT, "OFF"),
        }
        active_fill, halo_fill, status_text = mapping.get(color_name, mapping["off"])
        items = self.road_items[road]
        lights = items["lights"]
        halos = items["halos"]

        for key, light_id in lights.items():
            if key == color_name:
                self.canvas.itemconfig(light_id, fill=active_fill, outline="#f8fafc", width=2)
                self.canvas.itemconfig(halos[key], fill=halo_fill, state="normal")
            else:
                self.canvas.itemconfig(light_id, fill="#2e333a", outline="#59616e", width=1)
                self.canvas.itemconfig(halos[key], state="hidden")

        self.canvas.itemconfig(items["status"], text=status_text, fill=active_fill)

    def _set_map_light_fill(self, road: str, color_name: str):
        mapping = {
            "red": (self.RED, "#4a2022"),
            "yellow": (self.YELLOW, "#4d3b17"),
            "green": (self.GREEN, "#153f31"),
            "off": ("#303741", "#1d2229"),
        }
        active_fill, halo_fill = mapping.get(color_name, mapping["off"])
        items = self.map_light_items[road]
        lights = items["lights"]
        halos = items["halos"]

        for key, light_id in lights.items():
            if key == color_name:
                self.canvas.itemconfig(light_id, fill=active_fill, outline="#f8fafc", width=2)
                self.canvas.itemconfig(halos[key], fill=halo_fill, state="normal")
            else:
                self.canvas.itemconfig(light_id, fill="#303741", outline="#687180", width=1)
                self.canvas.itemconfig(halos[key], state="hidden")

    def _update_intersection_map(self):
        route_colors = {"green": self.GREEN, "yellow": self.YELLOW}

        for i, road in enumerate(self.ROAD_NAMES):
            token_count = self.visible_counts[i]
            colour = self.visible_colors[road]
            self._set_map_light_fill(road, colour)
            self.canvas.itemconfig(self.map_count_labels[road], text=f"{token_count} kendaraan")

            route_id = self.map_route_lines[road]
            if colour in route_colors:
                self.canvas.itemconfig(route_id, fill=route_colors[colour], state="normal")
            else:
                self.canvas.itemconfig(route_id, state="hidden")

        self._animate_map_cars()

    def _animate_map_cars(self):
        if not self.map_cars:
            return

        elapsed_ms = (time.perf_counter() - self.visible_started_at) * 1000
        cycle_ms = 1650
        phase = (elapsed_ms % cycle_ms) / cycle_ms

        for i, road in enumerate(self.ROAD_NAMES):
            token_count = self.visible_counts[i]
            colour = self.visible_colors.get(road, "red")
            active = colour in ("green", "yellow")
            visible_cars = min(4, max(1, (token_count + 4) // 5))
            moving_cars = 1 if active and visible_cars > 0 else 0
            path_start, path_end = self.map_motion_paths[road]

            for idx, car_id in enumerate(self.map_cars[road]):
                if idx >= visible_cars:
                    self.canvas.itemconfig(car_id, state="hidden")
                    continue

                if idx < moving_cars:
                    eased = phase * phase * (3 - 2 * phase)
                    x = path_start[0] + (path_end[0] - path_start[0]) * eased
                    y = path_start[1] + (path_end[1] - path_start[1]) * eased
                    self._place_map_car(road, car_id, x, y, active=True)
                else:
                    queue_x, queue_y = self.map_queue_points[road][idx]
                    self._place_map_car(road, car_id, queue_x, queue_y, active=False)

                self.canvas.itemconfig(car_id, state="normal")

    def _update_road_cards(self):
        for i, road in enumerate(self.ROAD_NAMES):
            token_count = self.visible_counts[i]
            colour = self.visible_colors[road]
            items = self.road_items[road]

            self.canvas.itemconfig(items["count"], text=f"{road}: {token_count} kendaraan")
            self._set_light_fill(road, colour)

            fraction = min(max(token_count / 20, 0), 1)
            bar_left = items["bar_left"]
            bar_right = items["bar_right"]
            bar_top = items["bar_top"]
            bar_bottom = items["bar_bottom"]
            new_right = bar_left + int((bar_right - bar_left) * fraction)
            self.canvas.coords(
                items["bar"],
                bar_left + 5,
                bar_top,
                new_right,
                bar_top,
                new_right,
                bar_top,
                new_right,
                bar_top + 5,
                new_right,
                bar_bottom - 5,
                new_right,
                bar_bottom,
                new_right,
                bar_bottom,
                bar_left + 5,
                bar_bottom,
                bar_left,
                bar_bottom,
                bar_left,
                bar_bottom - 5,
                bar_left,
                bar_top + 5,
                bar_left,
                bar_top,
            )

            if token_count > 14:
                bar_color = self.RED
            elif token_count > 8:
                bar_color = self.YELLOW
            else:
                bar_color = self.GREEN
            self.canvas.itemconfig(items["bar"], fill=bar_color)

        self._update_intersection_map()
        self._update_hover_visuals()

    def _highlight_state_node(self, active_state: str):
        for st, cid in self.state_nodes.items():
            if st == active_state:
                self.canvas.itemconfig(cid, fill=self.CYAN, outline="#dff7ff", width=2)
                self.canvas.itemconfig(self.state_texts[st], fill="#06151a")
            else:
                self.canvas.itemconfig(cid, fill="#222832", outline="#515b68", width=1)
                self.canvas.itemconfig(self.state_texts[st], fill=self.MUTED)
        self._update_state_road_labels()

    def _update_state_road_labels(self):
        order = self.visible_order
        mapping = {
            "q1": self.ROAD_NAMES[order[0]],
            "q2": self.ROAD_NAMES[order[0]],
            "q3": self.ROAD_NAMES[order[1]],
            "q4": self.ROAD_NAMES[order[1]],
            "q5": self.ROAD_NAMES[order[2]],
            "q6": self.ROAD_NAMES[order[2]],
            "q0": "GEN",
        }
        for st, label_id in self.state_road_labels.items():
            txt = mapping.get(st, "")
            if txt in self.ROAD_NAMES:
                idx = self.ROAD_NAMES.index(txt)
                txt = f"{txt}:{self.visible_counts[idx]}"
            self.canvas.itemconfig(label_id, text=txt)

    def _draw_tape(self):
        self.tape_canvas.delete("all")
        self.tape_canvas.create_rectangle(0, 0, 790, 112, fill=self.PANEL, outline="")
        self.tape_canvas.create_text(
            22,
            22,
            anchor="w",
            text="Tape Visual",
            fill=self.TEXT,
            font=("Segoe UI", 12, "bold"),
        )
        self.tape_canvas.create_text(
            768,
            22,
            anchor="e",
            text=f"head-> token:{self.visible_head_token}",
            fill=self.MUTED,
            font=("Consolas", 10),
        )

        start_x = 200
        y = 62
        box_w = 76
        gap = 42
        for i, road in enumerate(self.ROAD_NAMES):
            x1 = start_x + i * (box_w + gap)
            x2 = x1 + box_w
            is_head = i == self.visible_head_token
            outline = self.CYAN if is_head else self.BORDER
            fill = "#263241" if is_head else self.PANEL_ALT
            self._round_rect(self.tape_canvas, x1, y - 24, x2, y + 24, 8, fill=fill, outline=outline, width=2 if is_head else 1)
            self.tape_canvas.create_text(
                (x1 + x2) // 2,
                y - 8,
                text=road,
                fill=self.MUTED,
                font=("Segoe UI", 8, "bold"),
            )
            self.tape_canvas.create_text(
                (x1 + x2) // 2,
                y + 8,
                text=str(self.visible_counts[i]),
                fill=self.TEXT,
                font=("Consolas", 15, "bold"),
            )
            if i < 2:
                self.tape_canvas.create_text(
                    x2 + gap // 2,
                    y,
                    text="|",
                    fill=self.SOFT,
                    font=("Consolas", 18, "bold"),
                )

    def _road_message(self, road: Optional[str] = None):
        order_names = [self.ROAD_NAMES[i] for i in self.visible_order]
        if road is None:
            return "Urutan layanan saat ini: " + " -> ".join(order_names)

        idx = self.ROAD_NAMES.index(road)
        rank = order_names.index(road) + 1
        color = self.visible_colors.get(road, "red")
        label = {"red": "merah", "yellow": "kuning", "green": "hijau"}.get(color, color)
        return f"Jalan {road}: {self.visible_counts[idx]} kendaraan, lampu {label}, prioritas #{rank}"

    def _update_hover_visuals(self):
        active_outline = {"red": self.RED, "yellow": self.YELLOW, "green": self.GREEN}
        for road, items in self.road_items.items():
            color = self.visible_colors.get(road, "red")
            is_active = color in ("green", "yellow")
            is_hovered = road == self.hovered_road
            outline = active_outline.get(color, self.BORDER) if is_active else self.BORDER
            width = 2 if is_active else 1
            fill = self.PANEL_ALT

            if is_hovered:
                outline = "#f8fafc"
                width = 2
                fill = "#262b33"

            self.canvas.itemconfig(items["card"], fill=fill, outline=outline, width=width)

        self.info_label.config(text=self._road_message(self.hovered_road))

    def _on_canvas_motion(self, event):
        hovered = None
        for road, (x1, y1, x2, y2) in self.road_hit_boxes.items():
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                hovered = road
                break

        if hovered != self.hovered_road:
            self.hovered_road = hovered
            self.canvas.config(cursor="hand2" if hovered else "")
            self._update_hover_visuals()

    def _on_canvas_leave(self, _event):
        if self.hovered_road is not None:
            self.hovered_road = None
            self.canvas.config(cursor="")
            self._update_hover_visuals()

    def _animate_progress(self):
        elapsed_ms = (time.perf_counter() - self.visible_started_at) * 1000
        fraction = min(max(elapsed_ms / max(self.visible_duration_ms, 1), 0), 1)
        self.progress.coords(self.progress_fill, 0, 2, int(188 * fraction), 7)
        self._animate_map_cars()
        self.root.after(80, self._animate_progress)

    def _update(self):
        state = self.tm.state
        colors = self.tm.current_color_map()
        duration_ms = self.tm.current_duration_ms()

        self.visible_state = state
        self.visible_colors = colors
        self.visible_counts = list(self.tm.vehicles)
        self.visible_order = list(self.tm.order)
        self.visible_head_token = min(max(0, self.tm.head // 2), 2)
        self.visible_duration_ms = duration_ms
        self.visible_started_at = time.perf_counter()

        self.state_label.config(text=f"Current State: {state}")
        self.duration_label.config(text=f"{duration_ms / 1000:.1f}s display window")

        self._update_road_cards()
        self._highlight_state_node(state)
        self._draw_tape()

        self.tm.step()

        self.root.after(duration_ms, self._update)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = TrafficGUI()
    gui.run()
