import customtkinter as ctk
from tkinter import ttk, scrolledtext, messagebox
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import seaborn as sns
import os
import platform
import matplotlib.dates as mdates

# Set appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ProfessionalLogAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sonbati Academy - Professional Log Analyzer")

        # Set window size based on platform
        if platform.system() == "Windows":
            self.root.state("zoomed")  # Maximize window on Windows
        else:
            # For Linux, use a large size instead of zoomed
            self.root.geometry("1600x1000")

        # Application data
        self.log_data = []
        self.functions = {}
        self.filtered_data = []
        self.log_file_path = (
            "/media/elsonbaty/My/Projects/Sonbati_Academey/Execute_time.log"
        )

        # Create UI
        self.create_widgets()

        # Load data automatically
        self.load_log_file()

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Clean up any resources and close properly
        self.root.quit()
        self.root.destroy()

    def create_widgets(self):
        # Create main container with sidebar and main content
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create sidebar for filters
        self.sidebar = ctk.CTkFrame(self.main_container, width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10), pady=10)
        self.sidebar.pack_propagate(False)

        # Create main content area
        self.main_content = ctk.CTkFrame(self.main_container)
        self.main_content.pack(side="right", fill="both", expand=True, pady=10)

        # Build sidebar filters
        self.build_sidebar_filters()

        # Create notebook for main content
        self.notebook = ctk.CTkTabview(self.main_content)
        self.notebook.pack(fill="both", expand=True)

        # Add tabs
        self.notebook.add("Dashboard")
        self.notebook.add("Raw Data")
        self.notebook.add("Detailed Analysis")
        self.notebook.add("Advanced Visualizations")
        self.notebook.add("Performance Metrics")

        # Build each tab
        self.build_dashboard_tab()
        self.build_raw_data_tab()
        self.build_detailed_analysis_tab()
        self.build_advanced_visualizations_tab()
        self.build_performance_metrics_tab()

    def build_sidebar_filters(self):
        # Sidebar title
        ctk.CTkLabel(
            self.sidebar, text="FILTERS", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)

        # Function filter
        ctk.CTkLabel(self.sidebar, text="Function:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.function_filter_var = ctk.StringVar(value="All Functions")
        self.function_combo = ctk.CTkComboBox(
            self.sidebar, variable=self.function_filter_var, state="readonly"
        )
        self.function_combo.pack(fill="x", padx=10, pady=(0, 10))
        self.function_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Duration range filter
        ctk.CTkLabel(self.sidebar, text="Duration Range (seconds):").pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        duration_frame = ctk.CTkFrame(self.sidebar)
        duration_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.min_duration_var = ctk.StringVar(value="0")
        self.max_duration_var = ctk.StringVar(value="1000")

        ctk.CTkLabel(duration_frame, text="Min:").pack(side="left", padx=(0, 5))
        min_entry = ctk.CTkEntry(
            duration_frame, textvariable=self.min_duration_var, width=60
        )
        min_entry.pack(side="left", padx=(0, 10))
        min_entry.bind("<Return>", lambda e: self.apply_filters())

        ctk.CTkLabel(duration_frame, text="Max:").pack(side="left", padx=(0, 5))
        max_entry = ctk.CTkEntry(
            duration_frame, textvariable=self.max_duration_var, width=60
        )
        max_entry.pack(side="left")
        max_entry.bind("<Return>", lambda e: self.apply_filters())

        # Time range filter
        ctk.CTkLabel(self.sidebar, text="Time Range:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        time_frame = ctk.CTkFrame(self.sidebar)
        time_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.start_time_var = ctk.StringVar(value="00:00:00")
        self.end_time_var = ctk.StringVar(value="23:59:59")

        ctk.CTkLabel(time_frame, text="From:").pack(side="left", padx=(0, 5))
        start_entry = ctk.CTkEntry(
            time_frame, textvariable=self.start_time_var, width=70
        )
        start_entry.pack(side="left", padx=(0, 10))
        start_entry.bind("<Return>", lambda e: self.apply_filters())

        ctk.CTkLabel(time_frame, text="To:").pack(side="left", padx=(0, 5))
        end_entry = ctk.CTkEntry(time_frame, textvariable=self.end_time_var, width=70)
        end_entry.pack(side="left")
        end_entry.bind("<Return>", lambda e: self.apply_filters())

        # Operation type filter
        ctk.CTkLabel(self.sidebar, text="Operation Type:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.operation_type_var = ctk.StringVar(value="All Operations")
        operation_combo = ctk.CTkComboBox(
            self.sidebar,
            variable=self.operation_type_var,
            values=["All Operations", "Table Creation", "Data Insertion", "Other"],
        )
        operation_combo.pack(fill="x", padx=10, pady=(0, 10))
        operation_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Apply filters button
        ctk.CTkButton(
            self.sidebar, text="Apply Filters", command=self.apply_filters
        ).pack(pady=20)

        # Reset filters button
        ctk.CTkButton(
            self.sidebar,
            text="Reset Filters",
            command=self.reset_filters,
            fg_color="gray",
        ).pack(pady=5)

        # Quick stats
        ctk.CTkLabel(
            self.sidebar, text="QUICK STATS", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(30, 10))

        self.stats_frame = ctk.CTkFrame(self.sidebar)
        self.stats_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.total_ops_label = ctk.CTkLabel(
            self.stats_frame, text="Total Operations: 0"
        )
        self.total_ops_label.pack(anchor="w", pady=2)

        self.avg_duration_label = ctk.CTkLabel(
            self.stats_frame, text="Avg Duration: 0.000s"
        )
        self.avg_duration_label.pack(anchor="w", pady=2)

        self.filtered_ops_label = ctk.CTkLabel(self.stats_frame, text="Filtered: 0")
        self.filtered_ops_label.pack(anchor="w", pady=2)

    def build_dashboard_tab(self):
        tab = self.notebook.tab("Dashboard")

        # Create a grid layout for dashboard widgets
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        # Summary KPI frame
        kpi_frame = ctk.CTkFrame(tab)
        kpi_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Add KPI widgets
        self.create_kpi_widgets(kpi_frame)

        # Duration distribution chart
        duration_frame = ctk.CTkFrame(tab)
        duration_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            duration_frame,
            text="Duration Distribution",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=10)
        self.duration_chart_frame = ctk.CTkFrame(duration_frame)
        self.duration_chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Function performance chart
        perf_frame = ctk.CTkFrame(tab)
        perf_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            perf_frame, text="Function Performance", font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        self.perf_chart_frame = ctk.CTkFrame(perf_frame)
        self.perf_chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Timeline chart
        timeline_frame = ctk.CTkFrame(tab)
        timeline_frame.grid(
            row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )
        ctk.CTkLabel(
            timeline_frame, text="Execution Timeline", font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        self.timeline_chart_frame = ctk.CTkFrame(timeline_frame)
        self.timeline_chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def create_kpi_widgets(self, parent):
        # Create a grid for KPIs
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)
        parent.grid_columnconfigure(3, weight=1)

        # Total operations KPI
        total_frame = ctk.CTkFrame(parent, height=100)
        total_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            total_frame, text="Total Operations", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        self.total_ops_kpi = ctk.CTkLabel(
            total_frame, text="0", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.total_ops_kpi.pack(pady=5)

        # Average duration KPI
        avg_frame = ctk.CTkFrame(parent, height=100)
        avg_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            avg_frame, text="Avg Duration", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        self.avg_duration_kpi = ctk.CTkLabel(
            avg_frame, text="0.000s", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.avg_duration_kpi.pack(pady=5)

        # Max duration KPI
        max_frame = ctk.CTkFrame(parent, height=100)
        max_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            max_frame, text="Max Duration", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        self.max_duration_kpi = ctk.CTkLabel(
            max_frame, text="0.000s", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.max_duration_kpi.pack(pady=5)

        # Functions count KPI
        func_frame = ctk.CTkFrame(parent, height=100)
        func_frame.grid(row=0, column=3, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            func_frame, text="Unique Functions", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        self.func_count_kpi = ctk.CTkLabel(
            func_frame, text="0", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.func_count_kpi.pack(pady=5)

    def build_raw_data_tab(self):
        tab = self.notebook.tab("Raw Data")

        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            control_frame, text="Refresh Data", command=self.load_log_file
        ).pack(side="right", padx=5)
        ctk.CTkButton(control_frame, text="Export Data", command=self.export_data).pack(
            side="right", padx=5
        )

        # Search frame
        search_frame = ctk.CTkFrame(control_frame)
        search_frame.pack(side="left", padx=5)

        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame, textvariable=self.search_var, width=200
        )
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<Return>", lambda e: self.apply_filters())

        # Raw data display
        self.raw_text = scrolledtext.ScrolledText(
            tab, wrap="word", width=100, height=30
        )
        self.raw_text.pack(fill="both", expand=True, padx=10, pady=10)

    def build_detailed_analysis_tab(self):
        tab = self.notebook.tab("Detailed Analysis")

        # Treeview for detailed data
        columns = (
            "Timestamp",
            "Function",
            "Start Time",
            "End Time",
            "Duration",
            "Details",
        )
        self.analysis_tree = ttk.Treeview(
            tab, columns=columns, show="headings", height=25
        )

        column_widths = {
            "Timestamp": 150,
            "Function": 120,
            "Start Time": 150,
            "End Time": 150,
            "Duration": 100,
            "Details": 300,
        }

        for col in columns:
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=column_widths.get(col, 100))

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tab, orient="vertical", command=self.analysis_tree.yview
        )
        self.analysis_tree.configure(yscroll=scrollbar.set)

        self.analysis_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def build_advanced_visualizations_tab(self):
        tab = self.notebook.tab("Advanced Visualizations")

        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(control_frame, text="Chart Type:").pack(side="left", padx=5)
        self.chart_type_var = ctk.StringVar(value="Duration Distribution")
        chart_types = [
            "Duration Distribution",
            "Function Performance",
            "Timeline Analysis",
            "Correlation Heatmap",
            "Box Plot Analysis",
            "Cumulative Duration",
        ]
        chart_type_combo = ctk.CTkComboBox(
            control_frame, variable=self.chart_type_var, values=chart_types
        )
        chart_type_combo.pack(side="left", padx=5)

        ctk.CTkButton(
            control_frame, text="Generate Chart", command=self.update_advanced_charts
        ).pack(side="left", padx=5)

        # Chart frame
        self.advanced_chart_frame = ctk.CTkFrame(tab)
        self.advanced_chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def build_performance_metrics_tab(self):
        tab = self.notebook.tab("Performance Metrics")

        # Create a grid for metrics
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Function statistics
        func_stats_frame = ctk.CTkFrame(tab)
        func_stats_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            func_stats_frame,
            text="Function Statistics",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=10)

        columns = ("Function", "Count", "Min", "Max", "Average", "Std Dev", "Total")
        self.stats_tree = ttk.Treeview(
            func_stats_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=80)

        scrollbar = ttk.Scrollbar(
            func_stats_frame, orient="vertical", command=self.stats_tree.yview
        )
        self.stats_tree.configure(yscroll=scrollbar.set)

        self.stats_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Performance metrics
        metrics_frame = ctk.CTkFrame(tab)
        metrics_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            metrics_frame, text="Performance Metrics", font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)

        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame, wrap="word", height=20
        )
        self.metrics_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Timeline metrics
        timeline_metrics_frame = ctk.CTkFrame(tab)
        timeline_metrics_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            timeline_metrics_frame,
            text="Timeline Analysis",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=10)

        self.timeline_text = scrolledtext.ScrolledText(
            timeline_metrics_frame, wrap="word", height=10
        )
        self.timeline_text.pack(fill="both", expand=True, padx=10, pady=10)

    def load_log_file(self):
        try:
            with open(self.log_file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.raw_text.delete(1.0, "end")
                self.raw_text.insert(1.0, content)

                # Parse data
                self.parse_log_data(content)

                # Update UI
                self.apply_filters()
                self.update_dashboard()

                messagebox.showinfo("Success", "Data loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")

    def parse_log_data(self, content):
        self.log_data = []
        self.functions = {}

        # Regex pattern to extract data
        pattern = r"\[(.*?)\] Function: (.*?)\n.*?Start Time \(datetime\): (.*?)\n.*?End Time \(datetime\): (.*?)\n.*?Duration \(datetime\): (.*?)\n.*?Operation Details: (.*?)\n-{80}"

        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            timestamp, function, start_time, end_time, duration, details = match

            # Convert duration to seconds for calculations
            duration_seconds = self.parse_duration(duration)

            # Format times for display
            formatted_start = self.format_datetime(start_time.strip())
            formatted_end = self.format_datetime(end_time.strip())
            formatted_duration = self.format_duration(duration.strip())

            # Add to data list
            self.log_data.append(
                {
                    "timestamp": timestamp,
                    "function": function,
                    "start_time": start_time.strip(),
                    "end_time": end_time.strip(),
                    "duration": duration.strip(),
                    "duration_seconds": duration_seconds,
                    "details": details.strip(),
                    "formatted_start": formatted_start,
                    "formatted_end": formatted_end,
                    "formatted_duration": formatted_duration,
                }
            )

            # Group by function
            if function not in self.functions:
                self.functions[function] = {
                    "count": 0,
                    "durations": [],
                    "min_duration": float("inf"),
                    "max_duration": 0,
                    "total_duration": 0,
                    "durations_list": [],
                }

            self.functions[function]["count"] += 1
            self.functions[function]["durations_list"].append(duration_seconds)
            self.functions[function]["min_duration"] = min(
                self.functions[function]["min_duration"], duration_seconds
            )
            self.functions[function]["max_duration"] = max(
                self.functions[function]["max_duration"], duration_seconds
            )
            self.functions[function]["total_duration"] += duration_seconds

        # Calculate statistics for each function
        for function, stats in self.functions.items():
            if stats["count"] > 0:
                stats["average_duration"] = stats["total_duration"] / stats["count"]
                if len(stats["durations_list"]) > 1:
                    stats["std_dev"] = np.std(stats["durations_list"])
                else:
                    stats["std_dev"] = 0

        # Update filter combos
        function_names = ["All Functions"] + list(self.functions.keys())
        self.function_combo.configure(values=function_names)
        self.function_filter_var.set("All Functions")

    def format_datetime(self, datetime_str):
        """Format datetime string to HH:MM:SS.mmm format"""
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
            return dt.strftime("%H:%M:%S.%f")[:-3]  # Truncate to milliseconds
        except:
            return datetime_str

    def format_duration(self, duration_str):
        """Format duration string to HH:MM:SS.mmm format"""
        try:
            if "." in duration_str:
                time_part, millis_part = duration_str.split(".")
                millis = millis_part[:3]  # Take only 3 digits for milliseconds
            else:
                time_part = duration_str
                millis = "000"

            # Ensure time part has 3 components (HH:MM:SS)
            time_parts = time_part.split(":")
            if len(time_parts) == 2:
                time_parts = ["00"] + time_parts  # Add hours if missing
            elif len(time_parts) == 1:
                time_parts = [
                    "00",
                    "00",
                ] + time_parts  # Add hours and minutes if missing

            # Format with leading zeros
            formatted_time = ":".join([part.zfill(2) for part in time_parts])
            return f"{formatted_time}.{millis}"
        except:
            return duration_str

    def parse_duration(self, duration_str):
        try:
            if "." in duration_str:
                time_part, millis_part = duration_str.split(".")
                millis = float("0." + millis_part)
            else:
                time_part = duration_str
                millis = 0

            parts = time_part.split(":")
            if len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
            elif len(parts) == 2:  # MM:SS
                hours = 0
                minutes, seconds = map(int, parts)
            else:  # SS
                hours, minutes, seconds = 0, 0, int(parts[0])

            total_seconds = hours * 3600 + minutes * 60 + seconds + millis
            return total_seconds
        except:
            return 0

    def apply_filters(self):
        # Apply all filters to the data
        self.filtered_data = self.log_data.copy()

        # Function filter
        selected_function = self.function_filter_var.get()
        if selected_function != "All Functions":
            self.filtered_data = [
                d for d in self.filtered_data if d["function"] == selected_function
            ]

        # Duration filter
        try:
            min_duration = float(self.min_duration_var.get())
            max_duration = float(self.max_duration_var.get())
            self.filtered_data = [
                d
                for d in self.filtered_data
                if min_duration <= d["duration_seconds"] <= max_duration
            ]
        except:
            pass  # Ignore invalid duration values

        # Time filter
        try:
            start_time = self.start_time_var.get()
            end_time = self.end_time_var.get()

            self.filtered_data = [
                d
                for d in self.filtered_data
                if self.time_in_range(start_time, end_time, d["start_time"])
            ]
        except:
            pass  # Ignore invalid time values

        # Operation type filter
        op_type = self.operation_type_var.get()
        if op_type != "All Operations":
            if op_type == "Table Creation":
                self.filtered_data = [
                    d for d in self.filtered_data if "create_tables" in d["function"]
                ]
            elif op_type == "Data Insertion":
                self.filtered_data = [
                    d for d in self.filtered_data if "create_base_data" in d["function"]
                ]

        # Search filter
        search_text = self.search_var.get().lower()
        if search_text:
            self.filtered_data = [
                d
                for d in self.filtered_data
                if search_text in d["function"].lower()
                or search_text in d["details"].lower()
            ]

        # Update UI with filtered data
        self.update_analysis_tab()
        self.update_stats_tab()
        self.update_quick_stats()
        self.update_dashboard_charts()

    def time_in_range(self, start, end, time_str):
        """Check if time_str is between start and end times"""
        try:
            # Extract time part from datetime string
            time_part = time_str.split(" ")[1] if " " in time_str else time_str

            # Convert to comparable format
            current_time = datetime.strptime(time_part, "%H:%M:%S.%f").time()
            start_time = datetime.strptime(start, "%H:%M:%S").time()
            end_time = datetime.strptime(end, "%H:%M:%S").time()

            return start_time <= current_time <= end_time
        except:
            return True  # If parsing fails, include the record

    def reset_filters(self):
        # Reset all filter values
        self.function_filter_var.set("All Functions")
        self.min_duration_var.set("0")
        self.max_duration_var.set("1000")
        self.start_time_var.set("00:00:00")
        self.end_time_var.set("23:59:59")
        self.operation_type_var.set("All Operations")
        self.search_var.set("")

        # Reapply filters (which will show all data)
        self.apply_filters()

    def update_analysis_tab(self):
        # Clear old data
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)

        # Add filtered data
        for data in self.filtered_data:
            self.analysis_tree.insert(
                "",
                "end",
                values=(
                    data["timestamp"],
                    data["function"],
                    data["formatted_start"],
                    data["formatted_end"],
                    data["formatted_duration"],
                    data["details"],
                ),
            )

    def update_stats_tab(self):
        # Clear old data
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        # Calculate statistics for filtered data
        func_stats = {}
        for data in self.filtered_data:
            function = data["function"]
            duration = data["duration_seconds"]

            if function not in func_stats:
                func_stats[function] = {
                    "count": 0,
                    "durations": [],
                    "min": float("inf"),
                    "max": 0,
                    "total": 0,
                }

            func_stats[function]["count"] += 1
            func_stats[function]["durations"].append(duration)
            func_stats[function]["min"] = min(func_stats[function]["min"], duration)
            func_stats[function]["max"] = max(func_stats[function]["max"], duration)
            func_stats[function]["total"] += duration

        # Add statistics to treeview
        for function, stats in func_stats.items():
            avg = stats["total"] / stats["count"] if stats["count"] > 0 else 0
            if len(stats["durations"]) > 1:
                std_dev = np.std(stats["durations"])
            else:
                std_dev = 0

            self.stats_tree.insert(
                "",
                "end",
                values=(
                    function,
                    stats["count"],
                    f"{stats['min']:.3f}",
                    f"{stats['max']:.3f}",
                    f"{avg:.3f}",
                    f"{std_dev:.3f}",
                    f"{stats['total']:.3f}",
                ),
            )

        # Update performance metrics
        self.update_performance_metrics()

    def update_quick_stats(self):
        total_ops = len(self.log_data)
        filtered_ops = len(self.filtered_data)

        if filtered_ops > 0:
            avg_duration = (
                sum([d["duration_seconds"] for d in self.filtered_data]) / filtered_ops
            )
        else:
            avg_duration = 0

        self.total_ops_label.configure(text=f"Total Operations: {total_ops}")
        self.avg_duration_label.configure(text=f"Avg Duration: {avg_duration:.3f}s")
        self.filtered_ops_label.configure(text=f"Filtered: {filtered_ops}")

    def update_dashboard(self):
        # Update KPI widgets
        total_ops = len(self.log_data)
        self.total_ops_kpi.configure(text=str(total_ops))

        if total_ops > 0:
            avg_duration = (
                sum([d["duration_seconds"] for d in self.log_data]) / total_ops
            )
            max_duration = max([d["duration_seconds"] for d in self.log_data])
        else:
            avg_duration = 0
            max_duration = 0

        self.avg_duration_kpi.configure(text=f"{avg_duration:.3f}s")
        self.max_duration_kpi.configure(text=f"{max_duration:.3f}s")
        self.func_count_kpi.configure(text=str(len(self.functions)))

        # Update charts
        self.update_dashboard_charts()

    def update_dashboard_charts(self):
        # Update duration distribution chart
        self.update_duration_chart()

        # Update function performance chart
        self.update_performance_chart()

        # Update timeline chart
        self.update_timeline_chart()

    def update_duration_chart(self):
        for widget in self.duration_chart_frame.winfo_children():
            widget.destroy()

        if not self.filtered_data:
            no_data_label = ctk.CTkLabel(
                self.duration_chart_frame, text="No data to display"
            )
            no_data_label.pack(expand=True)
            return

        durations = [d["duration_seconds"] for d in self.filtered_data]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(durations, bins=20, alpha=0.7, edgecolor="black")
        ax.set_title("Duration Distribution")
        ax.set_xlabel("Duration (seconds)")
        ax.set_ylabel("Frequency")
        ax.grid(True, alpha=0.3)

        # Add statistics lines
        avg_duration = np.mean(durations)
        min_duration = np.min(durations)
        max_duration = np.max(durations)

        ax.axvline(
            avg_duration,
            color="r",
            linestyle="--",
            label=f"Average: {avg_duration:.3f}s",
        )
        ax.axvline(
            min_duration, color="g", linestyle="--", label=f"Min: {min_duration:.3f}s"
        )
        ax.axvline(
            max_duration, color="b", linestyle="--", label=f"Max: {max_duration:.3f}s"
        )
        ax.legend()

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.duration_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_performance_chart(self):
        for widget in self.perf_chart_frame.winfo_children():
            widget.destroy()

        if not self.filtered_data:
            no_data_label = ctk.CTkLabel(
                self.perf_chart_frame, text="No data to display"
            )
            no_data_label.pack(expand=True)
            return

        # Group by function
        func_durations = {}
        for data in self.filtered_data:
            function = data["function"]
            duration = data["duration_seconds"]

            if function not in func_durations:
                func_durations[function] = []

            func_durations[function].append(duration)

        # Calculate average duration per function
        functions = list(func_durations.keys())
        avg_durations = [np.mean(func_durations[f]) for f in functions]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(functions, avg_durations)
        ax.set_title("Average Duration by Function")
        ax.set_ylabel("Duration (seconds)")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.001,
                f"{height:.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.perf_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_timeline_chart(self):
        for widget in self.timeline_chart_frame.winfo_children():
            widget.destroy()

        if not self.filtered_data:
            no_data_label = ctk.CTkLabel(
                self.timeline_chart_frame, text="No data to display"
            )
            no_data_label.pack(expand=True)
            return

        # Extract times and durations
        times = [
            datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            for data in self.filtered_data
        ]
        durations = [data["duration_seconds"] for data in self.filtered_data]

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(times, durations, "o-", alpha=0.7)
        ax.set_title("Execution Timeline")
        ax.set_xlabel("Time")
        ax.set_ylabel("Duration (seconds)")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)

        # Format x-axis to show time properly
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.timeline_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_advanced_charts(self):
        for widget in self.advanced_chart_frame.winfo_children():
            widget.destroy()

        if not self.filtered_data:
            no_data_label = ctk.CTkLabel(
                self.advanced_chart_frame, text="No data to display"
            )
            no_data_label.pack(expand=True)
            return

        chart_type = self.chart_type_var.get()

        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == "Duration Distribution":
            durations = [d["duration_seconds"] for d in self.filtered_data]
            ax.hist(durations, bins=20, alpha=0.7, edgecolor="black")
            ax.set_title("Duration Distribution")
            ax.set_xlabel("Duration (seconds)")
            ax.set_ylabel("Frequency")

        elif chart_type == "Function Performance":
            func_durations = {}
            for data in self.filtered_data:
                function = data["function"]
                duration = data["duration_seconds"]

                if function not in func_durations:
                    func_durations[function] = []

                func_durations[function].append(duration)

            functions = list(func_durations.keys())
            avg_durations = [np.mean(func_durations[f]) for f in functions]

            bars = ax.bar(functions, avg_durations)
            ax.set_title("Average Duration by Function")
            ax.set_ylabel("Duration (seconds)")
            ax.tick_params(axis="x", rotation=45)

            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.001,
                    f"{height:.3f}",
                    ha="center",
                    va="bottom",
                )

        elif chart_type == "Timeline Analysis":
            times = [
                datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                for data in self.filtered_data
            ]
            durations = [data["duration_seconds"] for data in self.filtered_data]

            ax.plot(times, durations, "o-")
            ax.set_title("Execution Timeline")
            ax.set_xlabel("Time")
            ax.set_ylabel("Duration (seconds)")
            ax.tick_params(axis="x", rotation=45)

        elif chart_type == "Correlation Heatmap":
            # Create correlation matrix between functions
            func_data = {}
            for data in self.filtered_data:
                function = data["function"]
                duration = data["duration_seconds"]

                if function not in func_data:
                    func_data[function] = []

                func_data[function].append(duration)

            # Create DataFrame and calculate correlation
            max_len = max(len(v) for v in func_data.values())
            for func in func_data:
                if len(func_data[func]) < max_len:
                    func_data[func] += [np.nan] * (max_len - len(func_data[func]))

            df = pd.DataFrame(func_data)
            corr_matrix = df.corr()

            im = ax.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)
            ax.set_title("Function Correlation Heatmap")
            ax.set_xticks(range(len(corr_matrix.columns)))
            ax.set_yticks(range(len(corr_matrix.columns)))
            ax.set_xticklabels(corr_matrix.columns, rotation=45, ha="right")
            ax.set_yticklabels(corr_matrix.columns)

            # Add values to cells
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    text = ax.text(
                        j,
                        i,
                        f"{corr_matrix.iloc[i, j]:.2f}",
                        ha="center",
                        va="center",
                        color="white",
                    )

            plt.colorbar(im, ax=ax)

        elif chart_type == "Box Plot Analysis":
            func_durations = {}
            for data in self.filtered_data:
                function = data["function"]
                duration = data["duration_seconds"]

                if function not in func_durations:
                    func_durations[function] = []

                func_durations[function].append(duration)

            data = [func_durations[f] for f in func_durations.keys()]
            ax.boxplot(data)
            ax.set_title("Duration Distribution by Function (Box Plot)")
            ax.set_ylabel("Duration (seconds)")
            ax.set_xticklabels(func_durations.keys(), rotation=45)

        elif chart_type == "Cumulative Duration":
            times = [
                datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                for data in self.filtered_data
            ]
            durations = [data["duration_seconds"] for data in self.filtered_data]
            cumulative_duration = np.cumsum(durations)

            ax.plot(times, cumulative_duration, "b-")
            ax.set_title("Cumulative Execution Time")
            ax.set_xlabel("Time")
            ax.set_ylabel("Cumulative Duration (seconds)")
            ax.tick_params(axis="x", rotation=45)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.advanced_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_performance_metrics(self):
        self.metrics_text.delete(1.0, "end")
        self.timeline_text.delete(1.0, "end")

        if not self.filtered_data:
            return

        # Calculate performance metrics
        durations = [d["duration_seconds"] for d in self.filtered_data]
        total_duration = sum(durations)
        avg_duration = np.mean(durations)
        std_duration = np.std(durations)
        min_duration = np.min(durations)
        max_duration = np.max(durations)

        metrics_text = f"""
        PERFORMANCE METRICS:
        ====================
        Total Operations: {len(self.filtered_data)}
        Total Duration: {total_duration:.3f} seconds
        Average Duration: {avg_duration:.3f} seconds
        Standard Deviation: {std_duration:.3f} seconds
        Minimum Duration: {min_duration:.3f} seconds
        Maximum Duration: {max_duration:.3f} seconds
        Operations per Second: {len(self.filtered_data) / total_duration:.3f} (when running)
        
        PERCENTILES:
        ===========
        25th Percentile: {np.percentile(durations, 25):.3f} seconds
        50th Percentile (Median): {np.percentile(durations, 50):.3f} seconds
        75th Percentile: {np.percentile(durations, 75):.3f} seconds
        90th Percentile: {np.percentile(durations, 90):.3f} seconds
        95th Percentile: {np.percentile(durations, 95):.3f} seconds
        99th Percentile: {np.percentile(durations, 99):.3f} seconds
        """

        self.metrics_text.insert(1.0, metrics_text)

        # Timeline analysis
        if len(self.filtered_data) > 1:
            times = [
                datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                for d in self.filtered_data
            ]
            time_diffs = [
                (times[i] - times[i - 1]).total_seconds() for i in range(1, len(times))
            ]

            avg_interval = np.mean(time_diffs)
            std_interval = np.std(time_diffs)

            timeline_text = f"""
            TIMELINE ANALYSIS:
            =================
            Time Range: {times[0].strftime('%H:%M:%S')} to {times[-1].strftime('%H:%M:%S')}
            Total Time Span: {(times[-1] - times[0]).total_seconds():.3f} seconds
            Average Interval Between Operations: {avg_interval:.3f} seconds
            Interval Standard Deviation: {std_interval:.3f} seconds
            
            OPERATION DENSITY:
            =================
            Operations per Minute: {len(self.filtered_data) / ((times[-1] - times[0]).total_seconds() / 60):.2f}
            """

            self.timeline_text.insert(1.0, timeline_text)

    def export_data(self):
        try:
            # Create DataFrame from filtered data
            data = []
            for item in self.filtered_data:
                data.append(
                    {
                        "Timestamp": item["timestamp"],
                        "Function": item["function"],
                        "Start Time": item["formatted_start"],
                        "End Time": item["formatted_end"],
                        "Duration (s)": item["duration_seconds"],
                        "Formatted Duration": item["formatted_duration"],
                        "Details": item["details"],
                    }
                )

            df = pd.DataFrame(data)

            # Save to Excel
            with pd.ExcelWriter(
                "log_analysis_export.xlsx", engine="openpyxl"
            ) as writer:
                df.to_excel(writer, sheet_name="Raw Data", index=False)

                # Add statistics sheet
                stats_data = []
                for function, stats in self.functions.items():
                    stats_data.append(
                        {
                            "Function": function,
                            "Count": stats["count"],
                            "Min Duration (s)": stats["min_duration"],
                            "Max Duration (s)": stats["max_duration"],
                            "Average Duration (s)": stats["average_duration"],
                            "Std Dev": stats["std_dev"],
                            "Total Duration (s)": stats["total_duration"],
                        }
                    )

                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name="Statistics", index=False)

            messagebox.showinfo("Success", "Data exported to Excel successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = ProfessionalLogAnalyzer(root)
    root.mainloop()
