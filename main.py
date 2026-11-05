
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv

from algorithms import (
    find_best_slot,
    dijkstra,
    linear_search,
    sort_slots_by_distance
)

from database import (
    initialize_database,
    get_slots,
    allocate_parking,
    release_parking,
    get_records
)


# =====================================================
# PARKSMART - INTELLIGENT PARKING OPTIMIZATION SYSTEM
# =====================================================

BG = "#101827"
SIDEBAR = "#172438"
CARD = "#1E2D42"
CARD_LIGHT = "#26374D"
ACCENT = "#13B8A6"
WHITE = "#F4F7FB"
MUTED = "#A8B5C7"
GREEN = "#24C78A"
RED = "#F16D75"
YELLOW = "#F0B84B"
BORDER = "#304258"


# =====================================================
# PARKING ROUTE GRAPH
# =====================================================

GRAPH = {
    "Entrance": {"A": 5, "B": 10},
    "A": {"Entrance": 5, "A1": 5, "A2": 10, "A3": 15},
    "B": {"Entrance": 10, "B1": 5, "B2": 10, "B3": 15, "C": 10},
    "C": {"B": 10, "C1": 5, "C2": 10},
    "A1": {"A": 5},
    "A2": {"A": 10},
    "A3": {"A": 15},
    "B1": {"B": 5},
    "B2": {"B": 10},
    "B3": {"B": 15},
    "C1": {"C": 5},
    "C2": {"C": 10}
}


class ParkSmart:

    # =================================================
    # INITIALIZATION
    # =================================================

    def __init__(self, root):

        self.root = root

        self.root.title(
            "ParkSmart | Intelligent Parking Optimization"
        )

        self.root.geometry("1250x820")
        self.root.minsize(1000, 680)
        self.root.configure(bg=BG)

        initialize_database()

        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    # =================================================
    # STYLES
    # =================================================

    def setup_styles(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=CARD,
            foreground=WHITE,
            fieldbackground=CARD,
            rowheight=36,
            borderwidth=0,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=SIDEBAR,
            foreground=ACCENT,
            font=("Segoe UI", 10, "bold"),
            padding=10
        )

        style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", WHITE)]
        )

        style.configure(
            "Park.Horizontal.TProgressbar",
            troughcolor=BORDER,
            background=ACCENT,
            thickness=14,
            bordercolor=CARD,
            lightcolor=ACCENT,
            darkcolor=ACCENT
        )

        style.configure(
            "Park.TCombobox",
            fieldbackground=CARD_LIGHT,
            background=CARD_LIGHT,
            foreground=WHITE,
            arrowcolor=ACCENT
        )

    # =================================================
    # MAIN WINDOW LAYOUT
    # =================================================

    def create_layout(self):

        # Sidebar
        self.sidebar = tk.Frame(
            self.root,
            bg=SIDEBAR,
            width=235
        )

        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="PARKSMART",
            font=("Segoe UI", 21, "bold"),
            fg=ACCENT,
            bg=SIDEBAR
        ).pack(pady=(28, 4))

        tk.Label(
            self.sidebar,
            text="INTELLIGENT PARKING SYSTEM",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=SIDEBAR
        ).pack(pady=(0, 30))

        tk.Label(
            self.sidebar,
            text="MAIN MENU",
            font=("Segoe UI", 8, "bold"),
            fg="#71849D",
            bg=SIDEBAR
        ).pack(anchor="w", padx=22, pady=(0, 8))

        menu = [
            ("Dashboard", self.show_dashboard),
            ("Smart Parking", self.show_parking),
            ("Shortest Route", self.show_route),
            ("Search Slot", self.show_search),
            ("Search Vehicle", self.show_vehicle_search),
            ("Vehicle Exit", self.show_exit),
            ("Parking Records", self.show_records),
            ("Algorithm Analysis", self.show_analysis)
        ]

        self.menu_buttons = []

        for name, command in menu:
            self.make_menu_button(name, command)

        tk.Frame(
            self.sidebar,
            bg=BORDER,
            height=1
        ).pack(fill="x", padx=18, pady=15)

        self.make_menu_button(
            "Export Records",
            self.export_csv
        )

        tk.Label(
            self.sidebar,
            text="MCA DAA MINI PROJECT\nPython Desktop Application",
            bg=SIDEBAR,
            fg=MUTED,
            font=("Segoe UI", 9),
            justify="left"
        ).pack(side="bottom", pady=25)

        # Main content area
        main_area = tk.Frame(self.root, bg=BG)
        main_area.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Scrollable content
        self.canvas = tk.Canvas(
            main_area,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            main_area,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.content = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_content
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.mouse_scroll
        )

        self.content.pack_propagate(True)

    def update_scroll_region(self, event=None):

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def resize_content(self, event):

        self.canvas.itemconfigure(
            self.canvas_window,
            width=event.width
        )

    def mouse_scroll(self, event):

        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # =================================================
    # REUSABLE UI FUNCTIONS
    # =================================================

    def make_menu_button(self, name, command):

        button = tk.Button(
            self.sidebar,
            text="   " + name,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=SIDEBAR,
            fg=WHITE,
            activebackground=ACCENT,
            activeforeground=WHITE,
            bd=0,
            relief="flat",
            anchor="w",
            padx=15,
            pady=12,
            cursor="hand2"
        )

        button.pack(
            fill="x",
            padx=12,
            pady=2
        )

        self.menu_buttons.append(button)

        return button

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

        self.canvas.yview_moveto(0)

    def heading(self, title, subtitle):

        tk.Label(
            self.content,
            text=title,
            font=("Segoe UI", 24, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(
            anchor="w",
            padx=28,
            pady=(25, 3)
        )

        tk.Label(
            self.content,
            text=subtitle,
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=BG
        ).pack(
            anchor="w",
            padx=30,
            pady=(0, 22)
        )

    def section_title(self, parent, text):

        tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            fg=WHITE,
            bg=parent.cget("bg")
        ).pack(
            anchor="w",
            pady=(12, 10)
        )

    def make_button(self, parent, text, command):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=ACCENT,
            fg=WHITE,
            activebackground="#0D9689",
            activeforeground=WHITE,
            font=("Segoe UI", 10, "bold"),
            padx=17,
            pady=10,
            bd=0,
            cursor="hand2",
            relief="flat"
        )

        button.bind(
            "<Enter>",
            lambda event: button.config(bg="#0D9689")
        )

        button.bind(
            "<Leave>",
            lambda event: button.config(bg=ACCENT)
        )

        return button

    def make_entry(self, parent, placeholder=""):

        entry = tk.Entry(
            parent,
            font=("Segoe UI", 12),
            bg=CARD_LIGHT,
            fg=WHITE,
            insertbackground=WHITE,
            bd=0,
            relief="flat"
        )

        entry.pack(
            fill="x",
            ipady=12,
            pady=10
        )

        return entry

    def make_stat_card(
        self,
        parent,
        title,
        value,
        color,
        description,
        command
    ):

        card = tk.Frame(
            parent,
            bg=CARD,
            padx=16,
            pady=17,
            highlightbackground=BORDER,
            highlightthickness=1,
            cursor="hand2"
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        title_label = tk.Label(
            card,
            text=title,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )

        title_label.pack(anchor="w")

        value_label = tk.Label(
            card,
            text=str(value),
            bg=CARD,
            fg=color,
            font=("Segoe UI", 25, "bold"),
            cursor="hand2"
        )

        value_label.pack(anchor="w", pady=5)

        desc_label = tk.Label(
            card,
            text=description,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 8),
            cursor="hand2"
        )

        desc_label.pack(anchor="w")

        for widget in (card, title_label, value_label, desc_label):
            widget.bind(
                "<Button-1>",
                lambda event: command()
            )

        card.bind(
            "<Enter>",
            lambda event: card.config(bg=CARD_LIGHT)
        )

        card.bind(
            "<Leave>",
            lambda event: card.config(bg=CARD)
        )

        return card

    def get_duration(self, entry_time, exit_time=""):

        try:
            start = datetime.strptime(
                entry_time,
                "%d-%m-%Y %I:%M:%S %p"
            )

            if exit_time:
                end = datetime.strptime(
                    exit_time,
                    "%d-%m-%Y %I:%M:%S %p"
                )
            else:
                end = datetime.now()

            seconds = max(
                0,
                int((end - start).total_seconds())
            )

            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            return (
                f"{hours} hr {minutes} min"
            )

        except (ValueError, TypeError):
            return "Not available"

    # =================================================
    # DASHBOARD
    # =================================================

    def show_dashboard(self):

        self.clear_content()

        # Header
        header = tk.Frame(
            self.content,
            bg=BG
        )

        header.pack(
            fill="x",
            padx=28,
            pady=(25, 18)
        )

        header_left = tk.Frame(header, bg=BG)
        header_left.pack(side="left")

        tk.Label(
            header_left,
            text="Welcome to ParkSmart",
            font=("Segoe UI", 24, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            header_left,
            text="Your intelligent parking management dashboard",
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=BG
        ).pack(anchor="w", pady=4)

        clock_label = tk.Label(
            header,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg=ACCENT,
            bg=BG
        )

        clock_label.pack(side="right", anchor="n")

        def update_clock():

            if clock_label.winfo_exists():

                clock_label.config(
                    text=datetime.now().strftime(
                        "%d %b %Y\n%I:%M:%S %p"
                    )
                )

                self.root.after(1000, update_clock)

        update_clock()

        # Statistics
        slots = get_slots()
        records = get_records()

        total = len(slots)

        available = sum(
            1 for slot in slots
            if slot["status"] == "Available"
        )

        occupied = total - available

        occupancy = (
            occupied / total * 100
            if total else 0
        )

        self.section_title(
            self.content,
            "PARKING STATISTICS"
        )

        stats_frame = tk.Frame(
            self.content,
            bg=BG
        )

        stats_frame.pack(
            fill="x",
            padx=28
        )

        self.make_stat_card(
            stats_frame,
            "TOTAL SLOTS",
            total,
            ACCENT,
            "View all parking spaces",
            self.show_search
        )

        self.make_stat_card(
            stats_frame,
            "AVAILABLE",
            available,
            GREEN,
            "Find an empty space",
            self.show_parking
        )

        self.make_stat_card(
            stats_frame,
            "OCCUPIED",
            occupied,
            RED,
            "View active vehicles",
            self.show_records
        )

        self.make_stat_card(
            stats_frame,
            "OCCUPANCY",
            f"{occupancy:.1f}%",
            YELLOW,
            "Parking utilization",
            self.show_analysis
        )

        # Capacity bar
        progress_card = tk.Frame(
            self.content,
            bg=CARD,
            padx=20,
            pady=17,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        progress_card.pack(
            fill="x",
            padx=28,
            pady=20
        )

        progress_header = tk.Frame(
            progress_card,
            bg=CARD
        )

        progress_header.pack(fill="x")

        tk.Label(
            progress_header,
            text="PARKING CAPACITY",
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 11, "bold")
        ).pack(side="left")

        tk.Label(
            progress_header,
            text=f"{occupied} / {total} occupied",
            bg=CARD,
            fg=ACCENT,
            font=("Segoe UI", 10, "bold")
        ).pack(side="right")

        progress = ttk.Progressbar(
            progress_card,
            style="Park.Horizontal.TProgressbar",
            maximum=100,
            value=occupancy
        )

        progress.pack(
            fill="x",
            pady=13
        )

        tk.Label(
            progress_card,
            text=f"{occupancy:.1f}% of parking capacity is currently in use",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        # Slot layout
        self.section_title(
            self.content,
            "INTERACTIVE PARKING SPACE OVERVIEW"
        )

        slot_grid = tk.Frame(
            self.content,
            bg=BG
        )

        slot_grid.pack(
            fill="x",
            padx=28
        )

        for i, slot in enumerate(slots):

            available_slot = (
                slot["status"] == "Available"
            )

            color = GREEN if available_slot else RED

            status = (
                "AVAILABLE"
                if available_slot
                else "OCCUPIED"
            )

            slot_button = tk.Button(
                slot_grid,
                text=(
                    f"{slot['slot_number']}\n"
                    f"{status}\n"
                    f"{slot['distance']} metres"
                ),
                command=lambda s=slot: self.show_slot_details(s),
                bg=CARD,
                fg=color,
                activebackground=CARD_LIGHT,
                activeforeground=WHITE,
                font=("Segoe UI", 10, "bold"),
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=15,
                highlightbackground=BORDER,
                highlightthickness=1
            )

            slot_button.grid(
                row=i // 4,
                column=i % 4,
                padx=5,
                pady=5,
                sticky="nsew"
            )

            slot_button.bind(
                "<Enter>",
                lambda event, b=slot_button:
                b.config(bg=CARD_LIGHT)
            )

            slot_button.bind(
                "<Leave>",
                lambda event, b=slot_button:
                b.config(bg=CARD)
            )

        for col in range(4):
            slot_grid.grid_columnconfigure(
                col,
                weight=1
            )

        # Recent activity
        self.section_title(
            self.content,
            "RECENT PARKING ACTIVITY"
        )

        recent_frame = tk.Frame(
            self.content,
            bg=CARD
        )

        recent_frame.pack(
            fill="x",
            padx=28
        )

        columns = (
            "Vehicle",
            "Slot",
            "Entry Time",
            "Status"
        )

        recent_table = ttk.Treeview(
            recent_frame,
            columns=columns,
            show="headings",
            height=5
        )

        for col in columns:

            recent_table.heading(
                col,
                text=col
            )

            recent_table.column(
                col,
                width=150,
                anchor="center"
            )

        recent_table.pack(
            fill="x",
            padx=5,
            pady=5
        )

        for record in records[:5]:

            recent_table.insert(
                "",
                "end",
                values=(
                    record[1],
                    record[2],
                    record[3],
                    record[5]
                )
            )

        if not records:

            recent_table.insert(
                "",
                "end",
                values=(
                    "No records",
                    "-",
                    "-",
                    "-"
                )
            )

        # Quick actions
        self.section_title(
            self.content,
            "QUICK ACTIONS"
        )

        actions = tk.Frame(
            self.content,
            bg=BG
        )

        actions.pack(
            fill="x",
            padx=28,
            pady=(0, 30)
        )

        self.make_button(
            actions,
            "+ New Parking",
            self.show_parking
        ).pack(side="left", padx=(0, 8))

        self.make_button(
            actions,
            "Vehicle Exit",
            self.show_exit
        ).pack(side="left", padx=8)

        self.make_button(
            actions,
            "Search Vehicle",
            self.show_vehicle_search
        ).pack(side="left", padx=8)

        self.make_button(
            actions,
            "Refresh",
            self.show_dashboard
        ).pack(side="right")

    # =================================================
    # CLICKABLE PARKING SLOT DETAILS
    # =================================================

    def show_slot_details(self, slot):

        status_color = (
            GREEN
            if slot["status"] == "Available"
            else RED
        )

        window = tk.Toplevel(self.root)

        window.title("Parking Slot Details")
        window.geometry("360x300")
        window.configure(bg=BG)
        window.resizable(False, False)

        tk.Label(
            window,
            text=slot["slot_number"],
            font=("Segoe UI", 28, "bold"),
            fg=ACCENT,
            bg=BG
        ).pack(pady=(25, 10))

        tk.Label(
            window,
            text=slot["status"].upper(),
            font=("Segoe UI", 14, "bold"),
            fg=status_color,
            bg=BG
        ).pack(pady=5)

        tk.Label(
            window,
            text=f"Distance from entrance: {slot['distance']} metres",
            font=("Segoe UI", 10),
            fg=WHITE,
            bg=BG
        ).pack(pady=10)

        if slot["status"] == "Available":

            self.make_button(
                window,
                "Allocate This Slot",
                lambda: self.allocate_selected_slot(
                    slot["slot_number"],
                    window
                )
            ).pack(pady=15)

        self.make_button(
            window,
            "Find Shortest Route",
            lambda: self.open_route_for_slot(
                slot["slot_number"],
                window
            )
        ).pack(pady=5)

    def allocate_selected_slot(self, slot_number, window):

        window.destroy()
        self.show_parking()

        messagebox.showinfo(
            "Selected Slot",
            f"You selected {slot_number}.\n"
            "Enter the vehicle number and use the Greedy allocation button "
            "to allocate the nearest available slot."
        )

    def open_route_for_slot(self, slot_number, window):

        window.destroy()
        self.show_route(slot_number)

    # =================================================
    # SMART PARKING ALLOCATION
    # =================================================

    def show_parking(self):

        self.clear_content()

        self.heading(
            "Smart Parking Allocation",
            "Greedy Algorithm automatically finds the nearest available parking space"
        )

        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=25,
            pady=25,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        form.pack(
            fill="x",
            padx=28
        )

        tk.Label(
            form,
            text="VEHICLE REGISTRATION NUMBER",
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        vehicle_entry = self.make_entry(form)

        output = tk.Frame(
            self.content,
            bg=BG
        )

        output.pack(
            fill="x",
            padx=28,
            pady=20
        )

        result_label = tk.Label(
            output,
            text="Enter a vehicle number to find the best parking space.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
            padx=20,
            pady=25,
            justify="left"
        )

        result_label.pack(fill="x")

        def allocate():

            vehicle = vehicle_entry.get().strip().upper()

            if not vehicle:

                messagebox.showwarning(
                    "Input Required",
                    "Please enter a vehicle registration number."
                )

                return

            records = get_records()

            if any(
                str(r[1]).upper() == vehicle
                and r[5] == "Parked"
                for r in records
            ):

                messagebox.showwarning(
                    "Already Parked",
                    "This vehicle already has an active parking slot."
                )

                return

            best, elapsed = find_best_slot(
                get_slots()
            )

            if best is None:

                result_label.config(
                    text="No parking spaces are currently available.",
                    fg=RED
                )

                return

            success = allocate_parking(
                vehicle,
                best["slot_number"]
            )

            if success:

                result_label.config(
                    text=(
                        "PARKING SUCCESSFULLY CONFIRMED\n\n"
                        f"Vehicle Number: {vehicle}\n"
                        f"Allocated Slot: {best['slot_number']}\n"
                        f"Distance: {best['distance']} metres\n\n"
                        "Algorithm Used: Greedy Algorithm\n"
                        f"Execution Time: {elapsed:.6f} ms"
                    ),
                    fg=GREEN
                )

                messagebox.showinfo(
                    "Parking Confirmed",
                    f"Vehicle {vehicle} allocated to "
                    f"slot {best['slot_number']}."
                )

            else:

                result_label.config(
                    text="Unable to allocate the selected parking slot.",
                    fg=RED
                )

        self.make_button(
            form,
            "Find & Allocate Best Slot",
            allocate
        ).pack(anchor="w", pady=(5, 0))

        self.make_button(
            self.content,
            "View Updated Dashboard",
            self.show_dashboard
        ).pack(
            anchor="w",
            padx=28,
            pady=5
        )

    # =================================================
    # SHORTEST ROUTE
    # =================================================

    def show_route(self, selected_slot=None):

        self.clear_content()

        self.heading(
            "Shortest Route Finder",
            "Dijkstra's Algorithm calculates the minimum-distance route from the entrance"
        )

        slots = get_slots()

        slot_names = [
            slot["slot_number"]
            for slot in slots
        ]

        if not slot_names:
            return

        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=25,
            pady=25
        )

        form.pack(
            fill="x",
            padx=28
        )

        tk.Label(
            form,
            text="SELECT DESTINATION PARKING SLOT",
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        selected = tk.StringVar(
            value=selected_slot or slot_names[0]
        )

        combo = ttk.Combobox(
            form,
            textvariable=selected,
            values=slot_names,
            state="readonly",
            font=("Segoe UI", 11)
        )

        combo.pack(
            fill="x",
            pady=12,
            ipady=5
        )

        result_card = tk.Frame(
            self.content,
            bg=CARD,
            padx=25,
            pady=25
        )

        result_card.pack(
            fill="x",
            padx=28,
            pady=20
        )

        output = tk.Label(
            result_card,
            text="Choose a destination and calculate your route.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
            justify="left",
            wraplength=750
        )

        output.pack(anchor="w")

        def calculate():

            destination = selected.get()

            path, distance, elapsed = dijkstra(
                GRAPH,
                "Entrance",
                destination
            )

            if not path:

                output.config(
                    text="No route found.",
                    fg=RED
                )

                return

            route_text = "   →   ".join(path)

            output.config(
                text=(
                    "OPTIMAL ROUTE\n\n"
                    f"{route_text}\n\n"
                    f"Destination: {destination}\n"
                    f"Total Distance: {distance} metres\n"
                    f"Execution Time: {elapsed:.6f} ms\n\n"
                    "Algorithm: Dijkstra's Shortest Path"
                ),
                fg=ACCENT
            )

        self.make_button(
            form,
            "Calculate Shortest Route",
            calculate
        ).pack(anchor="w")

        calculate()

    # =================================================
    # SEARCH PARKING SLOT
    # =================================================

    def show_search(self):

        self.clear_content()

        self.heading(
            "Search Parking Slot",
            "Use Linear Search to find a specific parking space"
        )

        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=25,
            pady=25
        )

        form.pack(
            fill="x",
            padx=28
        )

        tk.Label(
            form,
            text="ENTER SLOT NUMBER",
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        entry = self.make_entry(form)

        output = tk.Label(
            self.content,
            text="Search results will appear here.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
            padx=20,
            pady=25,
            justify="left"
        )

        output.pack(
            fill="x",
            padx=28,
            pady=20
        )

        def search():

            name = entry.get().strip()

            if not name:

                messagebox.showwarning(
                    "Input Required",
                    "Enter a parking slot number."
                )

                return

            result, elapsed = linear_search(
                get_slots(),
                name
            )

            if result:

                color = (
                    GREEN
                    if result["status"] == "Available"
                    else RED
                )

                output.config(
                    text=(
                        f"PARKING SLOT FOUND\n\n"
                        f"Slot: {result['slot_number']}\n"
                        f"Status: {result['status']}\n"
                        f"Distance: {result['distance']} metres\n\n"
                        f"Algorithm: Linear Search\n"
                        f"Execution Time: {elapsed:.6f} ms"
                    ),
                    fg=color
                )

            else:

                output.config(
                    text="No matching parking slot was found.",
                    fg=RED
                )

        buttons = tk.Frame(
            form,
            bg=CARD
        )

        buttons.pack(anchor="w")

        self.make_button(
            buttons,
            "Search Slot",
            search
        ).pack(side="left", padx=(0, 10))

        self.make_button(
            buttons,
            "Sort by Distance",
            self.show_sorted_slots
        ).pack(side="left")

        entry.bind(
            "<Return>",
            lambda event: search()
        )

    def show_sorted_slots(self):

        sorted_slots = sort_slots_by_distance(
            get_slots()
        )

        window = tk.Toplevel(self.root)

        window.title("Sorted Parking Spaces")
        window.geometry("500x450")
        window.configure(bg=BG)

        tk.Label(
            window,
            text="PARKING SPACES BY DISTANCE",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=20)

        columns = (
            "Slot",
            "Distance",
            "Status"
        )

        table = ttk.Treeview(
            window,
            columns=columns,
            show="headings",
            height=10
        )

        for col in columns:

            table.heading(col, text=col)
            table.column(
                col,
                width=130,
                anchor="center"
            )

        table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        for slot in sorted_slots:

            table.insert(
                "",
                "end",
                values=(
                    slot["slot_number"],
                    f"{slot['distance']} metres",
                    slot["status"]
                )
            )

        tk.Label(
            window,
            text="Sorting Algorithm: Selection Sort",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(pady=10)

    # =================================================
    # SEARCH VEHICLE
    # =================================================

    def show_vehicle_search(self):

        self.clear_content()

        self.heading(
            "Vehicle Search",
            "Find the latest parking record and current parking status of a vehicle"
        )

        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=25,
            pady=25
        )

        form.pack(
            fill="x",
            padx=28
        )

        tk.Label(
            form,
            text="VEHICLE REGISTRATION NUMBER",
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        entry = self.make_entry(form)

        output = tk.Label(
            self.content,
            text="Enter a vehicle number to view its record.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
            padx=20,
            pady=25,
            justify="left"
        )

        output.pack(
            fill="x",
            padx=28,
            pady=20
        )

        def search():

            vehicle = entry.get().strip().upper()

            if not vehicle:

                messagebox.showwarning(
                    "Input Required",
                    "Enter a vehicle number."
                )

                return

            matches = [
                record for record in get_records()
                if str(record[1]).upper() == vehicle
            ]

            if not matches:

                output.config(
                    text="No records found for this vehicle.",
                    fg=RED
                )

                return

            record = matches[0]

            duration = self.get_duration(
                record[3],
                record[4]
            )

            output.config(
                text=(
                    "VEHICLE RECORD FOUND\n\n"
                    f"Vehicle Number: {record[1]}\n"
                    f"Parking Slot: {record[2]}\n"
                    f"Entry Time: {record[3]}\n"
                    f"Exit Time: {record[4] or 'Not exited yet'}\n"
                    f"Status: {record[5]}\n"
                    f"Parking Duration: {duration}"
                ),
                fg=GREEN if record[5] == "Parked" else WHITE
            )

        self.make_button(
            form,
            "Search Vehicle",
            search
        ).pack(anchor="w")

        entry.bind(
            "<Return>",
            lambda event: search()
        )

    # =================================================
    # VEHICLE EXIT
    # =================================================

    def show_exit(self):

        self.clear_content()

        self.heading(
            "Vehicle Exit Management",
            "Release an occupied parking slot when a vehicle leaves"
        )

        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=25,
            pady=25
        )

        form.pack(
            fill="x",
            padx=28
        )

        tk.Label(
            form,
            text="VEHICLE REGISTRATION NUMBER",
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        entry = self.make_entry(form)

        output = tk.Label(
            self.content,
            text="Enter the vehicle number to process its exit.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
            padx=20,
            pady=25,
            justify="left"
        )

        output.pack(
            fill="x",
            padx=28,
            pady=20
        )

        def release():

            vehicle = entry.get().strip().upper()

            if not vehicle:

                messagebox.showwarning(
                    "Input Required",
                    "Enter a vehicle number."
                )

                return

            slot = release_parking(vehicle)

            if slot:

                output.config(
                    text=(
                        "VEHICLE EXIT SUCCESSFUL\n\n"
                        f"Vehicle: {vehicle}\n"
                        f"Released Slot: {slot}\n"
                        "Parking status: Available"
                    ),
                    fg=GREEN
                )

                messagebox.showinfo(
                    "Exit Successful",
                    f"Vehicle {vehicle} has exited.\n"
                    f"Slot {slot} is now available."
                )

                entry.delete(0, tk.END)

            else:

                output.config(
                    text="No active parking record found for this vehicle.",
                    fg=RED
                )

                messagebox.showerror(
                    "Vehicle Not Found",
                    "No active parking record was found."
                )

        self.make_button(
            form,
            "Confirm Vehicle Exit",
            release
        ).pack(anchor="w")

        entry.bind(
            "<Return>",
            lambda event: release()
        )

        self.make_button(
            self.content,
            "Refresh Dashboard",
            self.show_dashboard
        ).pack(
            anchor="w",
            padx=28,
            pady=5
        )

    # =================================================
    # PARKING RECORDS
    # =================================================

    def show_records(self):

        self.clear_content()

        self.heading(
            "Parking Records & History",
            "View, filter, sort and export vehicle parking records"
        )

        controls = tk.Frame(
            self.content,
            bg=BG
        )

        controls.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        tk.Label(
            controls,
            text="Search:",
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        search_entry = tk.Entry(
            controls,
            font=("Segoe UI", 10),
            bg=CARD_LIGHT,
            fg=WHITE,
            insertbackground=WHITE,
            bd=0,
            width=20
        )

        search_entry.pack(
            side="left",
            ipady=8,
            padx=(0, 15)
        )

        sort_option = tk.StringVar(
            value="Latest First"
        )

        sort_combo = ttk.Combobox(
            controls,
            textvariable=sort_option,
            values=[
                "Latest First",
                "Oldest First",
                "Vehicle Number",
                "Slot Number"
            ],
            state="readonly",
            width=17,
            font=("Segoe UI", 10)
        )

        sort_combo.pack(
            side="left",
            padx=5
        )

        status_option = tk.StringVar(
            value="All Records"
        )

        status_combo = ttk.Combobox(
            controls,
            textvariable=status_option,
            values=[
                "All Records",
                "Parked",
                "Exited"
            ],
            state="readonly",
            width=13,
            font=("Segoe UI", 10)
        )

        status_combo.pack(
            side="left",
            padx=5
        )

        columns = (
            "ID",
            "Vehicle",
            "Slot",
            "Entry Time",
            "Exit Time",
            "Duration",
            "Status"
        )

        table_frame = tk.Frame(
            self.content,
            bg=CARD
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=10
        )

        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        widths = [
            45, 110, 65, 155, 155, 100, 80
        ]

        for col, width in zip(columns, widths):

            table.heading(
                col,
                text=col
            )

            table.column(
                col,
                width=width,
                anchor="center"
            )

        y_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=table.yview
        )

        table.configure(
            yscrollcommand=y_scroll.set
        )

        table.pack(
            side="left",
            fill="both",
            expand=True
        )

        y_scroll.pack(
            side="right",
            fill="y"
        )

        def parse_entry_time(value):

            try:
                return datetime.strptime(
                    value,
                    "%d-%m-%Y %I:%M:%S %p"
                )

            except (ValueError, TypeError):
                return datetime.min

        def load_records():

            records = list(get_records())

            query = search_entry.get().strip().upper()
            status = status_option.get()
            sorting = sort_option.get()

            # Search by vehicle or slot
            if query:

                records = [
                    r for r in records
                    if query in str(r[1]).upper()
                    or query in str(r[2]).upper()
                ]

            # Filter by parking status
            if status != "All Records":

                records = [
                    r for r in records
                    if r[5] == status
                ]

            # Sort records
            if sorting == "Latest First":

                records.sort(
                    key=lambda r: parse_entry_time(r[3]),
                    reverse=True
                )

            elif sorting == "Oldest First":

                records.sort(
                    key=lambda r: parse_entry_time(r[3])
                )

            elif sorting == "Vehicle Number":

                records.sort(
                    key=lambda r: str(r[1]).upper()
                )

            elif sorting == "Slot Number":

                records.sort(
                    key=lambda r: str(r[2]).upper()
                )

            # Clear existing rows
            for item in table.get_children():
                table.delete(item)

            # Insert filtered rows
            for record in records:

                duration = self.get_duration(
                    record[3],
                    record[4]
                )

                table.insert(
                    "",
                    "end",
                    values=(
                        record[0],
                        record[1],
                        record[2],
                        record[3],
                        record[4] or "-",
                        duration,
                        record[5]
                    )
                )

            count_label.config(
                text=f"{len(records)} records found"
            )

        count_label = tk.Label(
            self.content,
            text="",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 10, "bold")
        )

        count_label.pack(
            anchor="w",
            padx=28,
            pady=5
        )

        buttons = tk.Frame(
            self.content,
            bg=BG
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(5, 25)
        )

        self.make_button(
            buttons,
            "Apply Filters",
            load_records
        ).pack(side="left", padx=(0, 10))

        self.make_button(
            buttons,
            "Refresh",
            self.show_records
        ).pack(side="left", padx=10)

        self.make_button(
            buttons,
            "Export CSV",
            self.export_csv
        ).pack(side="right")

        search_entry.bind(
            "<Return>",
            lambda event: load_records()
        )

        sort_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: load_records()
        )

        status_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: load_records()
        )

        load_records()

    # =================================================
    # EXPORT RECORDS TO CSV
    # =================================================

    def export_csv(self):

        records = get_records()

        if not records:

            messagebox.showwarning(
                "No Records",
                "There are no parking records to export."
            )

            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ],
            initialfile="ParkSmart_Parking_Records.csv"
        )

        if not file_path:
            return

        try:

            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "ID",
                    "Vehicle Number",
                    "Parking Slot",
                    "Entry Time",
                    "Exit Time",
                    "Status"
                ])

                writer.writerows(records)

            messagebox.showinfo(
                "Export Successful",
                f"Parking records exported successfully.\n\n{file_path}"
            )

        except OSError as error:

            messagebox.showerror(
                "Export Error",
                str(error)
            )

    # =================================================
    # ALGORITHM ANALYSIS
    # =================================================

    def show_analysis(self):

        self.clear_content()

        self.heading(
            "Algorithm Analysis",
            "Design and Analysis of Algorithms - Performance and Complexity"
        )

        columns = (
            "Algorithm",
            "Application",
            "Time Complexity",
            "Space Complexity"
        )

        table = ttk.Treeview(
            self.content,
            columns=columns,
            show="headings",
            height=5
        )

        for col in columns:

            table.heading(
                col,
                text=col
            )

            table.column(
                col,
                width=180,
                anchor="center"
            )

        data = [
            (
                "Greedy Algorithm",
                "Parking allocation",
                "O(n)",
                "O(n)"
            ),
            (
                "Dijkstra",
                "Shortest route",
                "O((V+E) log V)",
                "O(V+E)"
            ),
            (
                "Linear Search",
                "Slot searching",
                "O(n)",
                "O(1)"
            ),
            (
                "Selection Sort",
                "Distance sorting",
                "O(n²)",
                "O(n)"
            )
        ]

        for row in data:
            table.insert(
                "",
                "end",
                values=row
            )

        table.pack(
            fill="x",
            padx=28,
            pady=15
        )

        # Performance explanation
        info = tk.Frame(
            self.content,
            bg=CARD,
            padx=22,
            pady=22
        )

        info.pack(
            fill="x",
            padx=28,
            pady=15
        )

        tk.Label(
            info,
            text="PERFORMANCE MEASUREMENT",
            bg=CARD,
            fg=ACCENT,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 12))

        explanation = (
            "ParkSmart uses different algorithms to improve parking "
            "management.\n\n"
            "1. Greedy Algorithm: Selects the nearest available parking slot.\n\n"
            "2. Dijkstra's Algorithm: Calculates the shortest route from "
            "the entrance to a parking destination.\n\n"
            "3. Linear Search: Checks parking slots one by one to find "
            "a requested slot.\n\n"
            "4. Selection Sort: Arranges parking slots in increasing "
            "order of distance.\n\n"
            "Execution time is measured using Python's time.perf_counter().\n\n"
            "n = Number of parking slots\n"
            "V = Number of graph vertices\n"
            "E = Number of graph edges"
        )

        tk.Label(
            info,
            text=explanation,
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 10),
            justify="left",
            wraplength=800
        ).pack(anchor="w")

        self.make_button(
            self.content,
            "Back to Dashboard",
            self.show_dashboard
        ).pack(
            anchor="w",
            padx=28,
            pady=15
        )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    initialize_database()

    root = tk.Tk()

    app = ParkSmart(root)

    root.mainloop()
