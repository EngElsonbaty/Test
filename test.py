import customtkinter as ctk
from tkinter import ttk, scrolledtext, messagebox
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import font_manager as fm

# Set appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AdvancedLogAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sonbati Academy - Advanced Log Analyzer")
        self.root.geometry("1600x1000")

        # Application data
        self.log_data = []
        self.functions = {}
        self.log_file_path = (
            "/media/elsonbaty/My/Projects/Sonbati_Academey/Execute_time.log"
        )

        # Create UI
        self.create_widgets()

        # Load data automatically
        self.load_log_file()

    def create_widgets(self):
        # Create main frames
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create notebook (tabs)
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Add tabs
        self.notebook.add("Raw Data")
        self.notebook.add("Data Analysis")
        self.notebook.add("Statistics")
        self.notebook.add("Visualizations")
        self.notebook.add("Advanced Charts")

        # Build each tab
        self.build_raw_data_tab()
        self.build_analysis_tab()
        self.build_stats_tab()
        self.build_visualizations_tab()
        self.build_advanced_charts_tab()

    def build_raw_data_tab(self):
        tab = self.notebook.tab("Raw Data")

        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(control_frame, text="Load Data", command=self.load_log_file).pack(
            side="right", padx=5
        )
        ctk.CTkButton(control_frame, text="Export Data", command=self.export_data).pack(
            side="right", padx=5
        )
        ctk.CTkButton(control_frame, text="Refresh", command=self.refresh_data).pack(
            side="right", padx=5
        )

        # Raw data display
        self.raw_text = scrolledtext.ScrolledText(
            tab, wrap="word", width=100, height=30
        )
        self.raw_text.pack(fill="both", expand=True, padx=10, pady=10)

    def build_analysis_tab(self):
        tab = self.notebook.tab("Data Analysis")

        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(control_frame, text="Select Function:").pack(side="left", padx=5)
        self.function_var = ctk.StringVar()
        self.function_combo = ctk.CTkComboBox(
            control_frame, variable=self.function_var, state="readonly"
        )
        self.function_combo.pack(side="left", padx=5)
        self.function_combo.bind("<<ComboboxSelected>>", self.on_function_select)

        ctk.CTkLabel(control_frame, text="Filter by Duration:").pack(
            side="left", padx=5
        )
        self.duration_filter_var = ctk.StringVar(value="All")
        duration_combo = ctk.CTkComboBox(
            control_frame,
            variable=self.duration_filter_var,
            values=["All", "Fast (<0.1s)", "Medium (0.1-0.5s)", "Slow (>0.5s)"],
        )
        duration_combo.pack(side="left", padx=5)
        duration_combo.bind("<<ComboboxSelected>>", self.on_filter_select)

        # Treeview for data
        columns = ("Function", "Start Time", "End Time", "Duration (s)", "Details")
        self.analysis_tree = ttk.Treeview(
            tab, columns=columns, show="headings", height=20
        )

        for col in columns:
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=120)

        self.analysis_tree.column("Details", width=300)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tab, orient="vertical", command=self.analysis_tree.yview
        )
        self.analysis_tree.configure(yscroll=scrollbar.set)

        self.analysis_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def build_stats_tab(self):
        tab = self.notebook.tab("Statistics")

        # Statistics container
        stats_container = ctk.CTkFrame(tab)
        stats_container.pack(fill="both", expand=True, padx=10, pady=10)

        # General statistics
        general_frame = ctk.CTkFrame(stats_container)
        general_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            general_frame,
            text="General Statistics",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=10)

        self.general_stats_text = scrolledtext.ScrolledText(
            general_frame, wrap="word", width=100, height=8
        )
        self.general_stats_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Function statistics
        functions_frame = ctk.CTkFrame(stats_container)
        functions_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            functions_frame,
            text="Function Statistics",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=10)

        columns = (
            "Function",
            "Count",
            "Min (s)",
            "Max (s)",
            "Average (s)",
            "Std Dev",
            "Total (s)",
        )
        self.stats_tree = ttk.Treeview(
            functions_frame, columns=columns, show="headings", height=12
        )

        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(
            functions_frame, orient="vertical", command=self.stats_tree.yview
        )
        self.stats_tree.configure(yscroll=scrollbar.set)

        self.stats_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def build_visualizations_tab(self):
        tab = self.notebook.tab("Visualizations")

        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(control_frame, text="Chart Type:").pack(side="left", padx=5)
        self.chart_type_var = ctk.StringVar(value="Function Duration")
        chart_types = [
            "Function Duration",
            "Operation Count",
            "Function Comparison",
            "Duration Distribution",
            "Time Series",
            "Box Plot",
            "Pie Chart",
            "Heatmap",
        ]
        chart_type_combo = ctk.CTkComboBox(
            control_frame, variable=self.chart_type_var, values=chart_types
        )
        chart_type_combo.pack(side="left", padx=5)

        ctk.CTkLabel(control_frame, text="Function:").pack(side="left", padx=5)
        self.viz_function_var = ctk.StringVar()
        self.viz_function_combo = ctk.CTkComboBox(
            control_frame, variable=self.viz_function_var, state="readonly"
        )
        self.viz_function_combo.pack(side="left", padx=5)

        ctk.CTkButton(
            control_frame, text="Generate Chart", command=self.update_chart
        ).pack(side="left", padx=5)

        # Chart frame
        self.chart_frame = ctk.CTkFrame(tab)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def build_advanced_charts_tab(self):
        tab = self.notebook.tab("Advanced Charts")

        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(control_frame, text="Advanced Chart:").pack(side="left", padx=5)
        self.advanced_chart_var = ctk.StringVar(value="Performance Trend")
        advanced_charts = [
            "Performance Trend",
            "Cumulative Duration",
            "Statistical Summary",
            "Correlation Matrix",
        ]
        advanced_chart_combo = ctk.CTkComboBox(
            control_frame, variable=self.advanced_chart_var, values=advanced_charts
        )
        advanced_chart_combo.pack(side="left", padx=5)

        ctk.CTkButton(
            control_frame,
            text="Generate Advanced Chart",
            command=self.update_advanced_chart,
        ).pack(side="left", padx=5)

        # Advanced chart frame
        self.advanced_chart_frame = ctk.CTkFrame(tab)
        self.advanced_chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Statistics summary frame
        self.stats_summary_frame = ctk.CTkFrame(tab)
        self.stats_summary_frame.pack(fill="x", padx=10, pady=10)

        self.stats_summary_text = scrolledtext.ScrolledText(
            self.stats_summary_frame, wrap="word", width=100, height=8
        )
        self.stats_summary_text.pack(fill="both", expand=True, padx=10, pady=10)

    def load_log_file(self):
        try:
            with open(self.log_file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.raw_text.delete(1.0, "end")
                self.raw_text.insert(1.0, content)

                # Parse data
                self.parse_log_data(content)

                # Update UI
                self.update_analysis_tab()
                self.update_stats_tab()
                self.update_chart()

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

            # Convert duration to seconds
            duration_seconds = self.parse_duration(duration)

            # Add to data list
            self.log_data.append(
                {
                    "timestamp": timestamp,
                    "function": function,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "duration_seconds": duration_seconds,
                    "details": details.strip(),
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
            self.functions[function]["durations"].append(duration_seconds)

        # Calculate statistics for each function
        for function, stats in self.functions.items():
            if stats["count"] > 0:
                stats["average_duration"] = stats["total_duration"] / stats["count"]
                stats["std_dev"] = (
                    np.std(stats["durations_list"])
                    if len(stats["durations_list"]) > 1
                    else 0
                )

        # Update combo boxes
        self.function_combo.configure(values=list(self.functions.keys()))
        self.viz_function_combo.configure(values=list(self.functions.keys()))
        if self.functions:
            self.function_var.set(list(self.functions.keys())[0])
            self.viz_function_var.set(list(self.functions.keys())[0])

    def parse_duration(self, duration_str):
        try:
            # Handle different duration formats
            if "." in duration_str:
                time_part, millis_part = duration_str.split(".")
                millis = float("0." + millis_part)
            else:
                time_part = duration_str
                millis = 0

            # Handle different time formats
            if ":" in time_part:
                parts = time_part.split(":")
                if len(parts) == 3:  # HH:MM:SS
                    hours, minutes, seconds = map(int, parts)
                elif len(parts) == 2:  # MM:SS
                    hours = 0
                    minutes, seconds = map(int, parts)
                else:
                    hours, minutes, seconds = 0, 0, 0
            else:
                hours, minutes, seconds = 0, 0, 0

            total_seconds = hours * 3600 + minutes * 60 + seconds + millis
            return total_seconds
        except:
            return 0

    def update_analysis_tab(self):
        # Clear old data
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)

        # Add new data
        for data in self.log_data:
            self.analysis_tree.insert(
                "",
                "end",
                values=(
                    data["function"],
                    data["start_time"],
                    data["end_time"],
                    f"{data['duration_seconds']:.3f}",
                    data["details"],
                ),
            )

    def update_stats_tab(self):
        # Update general statistics
        total_operations = len(self.log_data)
        total_functions = len(self.functions)
        total_duration = sum([d["duration_seconds"] for d in self.log_data])
        avg_duration = total_duration / total_operations if total_operations > 0 else 0

        # Find fastest and slowest operations
        fastest_op = (
            min(self.log_data, key=lambda x: x["duration_seconds"])
            if self.log_data
            else None
        )
        slowest_op = (
            max(self.log_data, key=lambda x: x["duration_seconds"])
            if self.log_data
            else None
        )

        general_stats = f"""
        GENERAL STATISTICS:
        - Total Operations: {total_operations}
        - Unique Functions: {total_functions}
        - Total Duration: {total_duration:.3f} seconds
        - Average Duration: {avg_duration:.3f} seconds
        - Fastest Operation: {fastest_op['duration_seconds']:.3f}s ({fastest_op['function'] if fastest_op else 'N/A'})
        - Slowest Operation: {slowest_op['duration_seconds']:.3f}s ({slowest_op['function'] if slowest_op else 'N/A'})
        """

        self.general_stats_text.delete(1.0, "end")
        self.general_stats_text.insert(1.0, general_stats)

        # Clear old data in function statistics tree
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        # Add function statistics
        for function, stats in self.functions.items():
            self.stats_tree.insert(
                "",
                "end",
                values=(
                    function,
                    stats["count"],
                    f"{stats['min_duration']:.3f}",
                    f"{stats['max_duration']:.3f}",
                    f"{stats['average_duration']:.3f}",
                    f"{stats['std_dev']:.3f}",
                    f"{stats['total_duration']:.3f}",
                ),
            )

    def update_chart(self):
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not self.functions:
            return

        chart_type = self.chart_type_var.get()
        selected_function = self.viz_function_var.get()

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == "Function Duration":
            # Bar chart of average duration per function
            functions = list(self.functions.keys())
            avg_durations = [self.functions[f]["average_duration"] for f in functions]

            bars = ax.bar(functions, avg_durations)
            ax.set_title("Average Execution Time by Function")
            ax.set_ylabel("Duration (seconds)")
            ax.tick_params(axis="x", rotation=45)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.001,
                    f"{height:.3f}",
                    ha="center",
                    va="bottom",
                )

        elif chart_type == "Operation Count":
            # Bar chart of operation count per function
            functions = list(self.functions.keys())
            counts = [self.functions[f]["count"] for f in functions]

            bars = ax.bar(functions, counts)
            ax.set_title("Number of Operations by Function")
            ax.set_ylabel("Count")
            ax.tick_params(axis="x", rotation=45)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.1,
                    f"{height}",
                    ha="center",
                    va="bottom",
                )

        elif chart_type == "Function Comparison":
            # Comparison of count vs duration
            functions = list(self.functions.keys())
            counts = [self.functions[f]["count"] for f in functions]
            avg_durations = [self.functions[f]["average_duration"] for f in functions]

            # Normalize for comparison
            max_count = max(counts)
            max_duration = max(avg_durations)

            normalized_counts = [c / max_count for c in counts]
            normalized_durations = [d / max_duration for d in avg_durations]

            width = 0.35
            x = np.arange(len(functions))

            ax.bar(x - width / 2, normalized_counts, width, label="Count (normalized)")
            ax.bar(
                x + width / 2,
                normalized_durations,
                width,
                label="Duration (normalized)",
            )

            ax.set_title("Function Comparison (Count vs Duration)")
            ax.set_ylabel("Normalized Value")
            ax.set_xticks(x)
            ax.set_xticklabels(functions, rotation=45)
            ax.legend()

        elif (
            chart_type == "Duration Distribution"
            and selected_function in self.functions
        ):
            # Histogram of duration distribution for selected function
            durations = self.functions[selected_function]["durations_list"]

            ax.hist(durations, bins=20, alpha=0.7, edgecolor="black")
            ax.set_title(f"Duration Distribution for {selected_function}")
            ax.set_xlabel("Duration (seconds)")
            ax.set_ylabel("Frequency")

            # Add statistics lines
            avg_duration = self.functions[selected_function]["average_duration"]
            min_duration = self.functions[selected_function]["min_duration"]
            max_duration = self.functions[selected_function]["max_duration"]

            ax.axvline(
                avg_duration,
                color="r",
                linestyle="--",
                label=f"Average: {avg_duration:.3f}s",
            )
            ax.axvline(
                min_duration,
                color="g",
                linestyle="--",
                label=f"Min: {min_duration:.3f}s",
            )
            ax.axvline(
                max_duration,
                color="b",
                linestyle="--",
                label=f"Max: {max_duration:.3f}s",
            )
            ax.legend()

        elif chart_type == "Time Series":
            # Time series of operations
            times = [
                datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                for data in self.log_data
            ]
            durations = [data["duration_seconds"] for data in self.log_data]

            ax.plot(times, durations, "o-")
            ax.set_title("Operation Duration Over Time")
            ax.set_xlabel("Time")
            ax.set_ylabel("Duration (seconds)")
            ax.tick_params(axis="x", rotation=45)

        elif chart_type == "Box Plot":
            # Box plot of durations by function
            data = [self.functions[f]["durations_list"] for f in self.functions.keys()]

            ax.boxplot(data)
            ax.set_title("Duration Distribution by Function (Box Plot)")
            ax.set_ylabel("Duration (seconds)")
            ax.set_xticklabels(list(self.functions.keys()), rotation=45)

        elif chart_type == "Pie Chart":
            # Pie chart of total duration by function
            functions = list(self.functions.keys())
            total_durations = [self.functions[f]["total_duration"] for f in functions]

            ax.pie(total_durations, labels=functions, autopct="%1.1f%%")
            ax.set_title("Total Duration by Function")

        elif chart_type == "Heatmap":
            # Prepare data for heatmap (function vs time of day)
            function_times = {}
            for data in self.log_data:
                function = data["function"]
                time = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                hour = time.hour

                if function not in function_times:
                    function_times[function] = [0] * 24

                function_times[function][hour] += data["duration_seconds"]

            # Create heatmap data
            functions = list(function_times.keys())
            heatmap_data = [function_times[f] for f in functions]

            im = ax.imshow(heatmap_data, cmap="viridis", aspect="auto")
            ax.set_title("Execution Time Heatmap (Function vs Hour of Day)")
            ax.set_xlabel("Hour of Day")
            ax.set_ylabel("Function")
            ax.set_xticks(range(24))
            ax.set_yticks(range(len(functions)))
            ax.set_yticklabels(functions)

            # Add colorbar
            plt.colorbar(im, ax=ax, label="Total Duration (seconds)")

        plt.tight_layout()

        # Embed chart in CustomTkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_advanced_chart(self):
        # Clear previous chart
        for widget in self.advanced_chart_frame.winfo_children():
            widget.destroy()

        for widget in self.stats_summary_frame.winfo_children():
            widget.destroy()

        if not self.functions:
            return

        chart_type = self.advanced_chart_var.get()

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 7))

        if chart_type == "Performance Trend":
            # Performance trend over time
            times = [
                datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                for data in self.log_data
            ]
            durations = [data["duration_seconds"] for data in self.log_data]

            # Calculate moving average
            window_size = min(10, len(durations))
            moving_avg = pd.Series(durations).rolling(window=window_size).mean()

            ax.plot(times, durations, "o", alpha=0.5, label="Individual Operations")
            ax.plot(
                times,
                moving_avg,
                "r-",
                linewidth=2,
                label=f"Moving Average (window={window_size})",
            )
            ax.set_title("Performance Trend Over Time")
            ax.set_xlabel("Time")
            ax.set_ylabel("Duration (seconds)")
            ax.tick_params(axis="x", rotation=45)
            ax.legend()
            ax.grid(True)

            # Statistics summary
            summary_text = f"""
            PERFORMANCE TREND ANALYSIS:
            - Total Data Points: {len(durations)}
            - Trend Direction: {'Improving' if moving_avg.iloc[-1] < moving_avg.iloc[0] else 'Worsening'}
            - Average Duration: {np.mean(durations):.3f}s
            - Duration Std Dev: {np.std(durations):.3f}s
            - Minimum Duration: {np.min(durations):.3f}s
            - Maximum Duration: {np.max(durations):.3f}s
            """

            self.stats_summary_text = scrolledtext.ScrolledText(
                self.stats_summary_frame, wrap="word", width=100, height=8
            )
            self.stats_summary_text.pack(fill="both", expand=True, padx=10, pady=10)
            self.stats_summary_text.insert(1.0, summary_text)

        elif chart_type == "Cumulative Duration":
            # Cumulative duration over time
            times = [
                datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                for data in self.log_data
            ]
            durations = [data["duration_seconds"] for data in self.log_data]
            cumulative_duration = np.cumsum(durations)

            ax.plot(times, cumulative_duration, "b-")
            ax.set_title("Cumulative Execution Time Over Time")
            ax.set_xlabel("Time")
            ax.set_ylabel("Cumulative Duration (seconds)")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(True)

            # Statistics summary
            summary_text = f"""
            CUMULATIVE DURATION ANALYSIS:
            - Total Operations: {len(durations)}
            - Total Duration: {cumulative_duration[-1]:.3f}s
            - Average Duration: {np.mean(durations):.3f}s
            - Operations per Second: {len(durations) / cumulative_duration[-1]:.3f}
            """

            self.stats_summary_text = scrolledtext.ScrolledText(
                self.stats_summary_frame, wrap="word", width=100, height=8
            )
            self.stats_summary_text.pack(fill="both", expand=True, padx=10, pady=10)
            self.stats_summary_text.insert(1.0, summary_text)

        elif chart_type == "Statistical Summary":
            # Statistical summary with violin plot
            data = [self.functions[f]["durations_list"] for f in self.functions.keys()]

            ax.violinplot(data, showmeans=True, showmedians=True)
            ax.set_title("Statistical Summary of Function Durations (Violin Plot)")
            ax.set_ylabel("Duration (seconds)")
            ax.set_xticks(range(1, len(self.functions) + 1))
            ax.set_xticklabels(list(self.functions.keys()), rotation=45)
            ax.grid(True)

            # Statistics summary
            summary_text = "STATISTICAL SUMMARY:\n\n"
            for function in self.functions.keys():
                stats = self.functions[function]
                summary_text += f"{function}:\n"
                summary_text += f"  - Count: {stats['count']}\n"
                summary_text += f"  - Min: {stats['min_duration']:.3f}s\n"
                summary_text += f"  - Max: {stats['max_duration']:.3f}s\n"
                summary_text += f"  - Average: {stats['average_duration']:.3f}s\n"
                summary_text += f"  - Std Dev: {stats['std_dev']:.3f}s\n"
                summary_text += f"  - Total: {stats['total_duration']:.3f}s\n\n"

            self.stats_summary_text = scrolledtext.ScrolledText(
                self.stats_summary_frame, wrap="word", width=100, height=8
            )
            self.stats_summary_text.pack(fill="both", expand=True, padx=10, pady=10)
            self.stats_summary_text.insert(1.0, summary_text)

        elif chart_type == "Correlation Matrix":
            # Create correlation matrix between functions
            # First, create a DataFrame with function durations over time
            time_series_data = {}

            for data in self.log_data:
                time_key = data["timestamp"][:16]  # Group by minute
                function = data["function"]

                if time_key not in time_series_data:
                    time_series_data[time_key] = {}

                if function not in time_series_data[time_key]:
                    time_series_data[time_key][function] = []

                time_series_data[time_key][function].append(data["duration_seconds"])

            # Create DataFrame with average durations per time period
            df_data = {}
            for time_key, functions in time_series_data.items():
                for function, durations in functions.items():
                    if function not in df_data:
                        df_data[function] = []
                    df_data[function].append(np.mean(durations))

            # Ensure all arrays have the same length
            max_length = max(len(v) for v in df_data.values())
            for function in df_data:
                if len(df_data[function]) < max_length:
                    df_data[function] += [np.nan] * (
                        max_length - len(df_data[function])
                    )

            df = pd.DataFrame(df_data)

            # Calculate correlation matrix
            corr_matrix = df.corr()

            # Plot heatmap
            im = ax.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
            ax.set_title("Correlation Matrix Between Functions")
            ax.set_xticks(range(len(corr_matrix.columns)))
            ax.set_yticks(range(len(corr_matrix.columns)))
            ax.set_xticklabels(corr_matrix.columns, rotation=45, ha="right")
            ax.set_yticklabels(corr_matrix.columns)

            # Add correlation values to cells
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    text = ax.text(
                        j,
                        i,
                        f"{corr_matrix.iloc[i, j]:.2f}",
                        ha="center",
                        va="center",
                        color="w",
                    )

            # Add colorbar
            plt.colorbar(im, ax=ax, label="Correlation Coefficient")

            # Statistics summary
            summary_text = "CORRELATION ANALYSIS:\n\n"
            summary_text += "Strong Positive Correlations (>0.7):\n"
            for i, col1 in enumerate(corr_matrix.columns):
                for j, col2 in enumerate(corr_matrix.columns):
                    if i < j and corr_matrix.iloc[i, j] > 0.7:
                        summary_text += (
                            f"  - {col1} & {col2}: {corr_matrix.iloc[i, j]:.3f}\n"
                        )

            summary_text += "\nStrong Negative Correlations (< -0.7):\n"
            for i, col1 in enumerate(corr_matrix.columns):
                for j, col2 in enumerate(corr_matrix.columns):
                    if i < j and corr_matrix.iloc[i, j] < -0.7:
                        summary_text += (
                            f"  - {col1} & {col2}: {corr_matrix.iloc[i, j]:.3f}\n"
                        )

            self.stats_summary_text = scrolledtext.ScrolledText(
                self.stats_summary_frame, wrap="word", width=100, height=8
            )
            self.stats_summary_text.pack(fill="both", expand=True, padx=10, pady=10)
            self.stats_summary_text.insert(1.0, summary_text)

        plt.tight_layout()

        # Embed chart in CustomTkinter
        canvas = FigureCanvasTkAgg(fig, self.advanced_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def on_function_select(self, event):
        selected_function = self.function_var.get()

        # Clear old data
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)

        # Add data for selected function only
        for data in self.log_data:
            if data["function"] == selected_function:
                self.analysis_tree.insert(
                    "",
                    "end",
                    values=(
                        data["function"],
                        data["start_time"],
                        data["end_time"],
                        f"{data['duration_seconds']:.3f}",
                        data["details"],
                    ),
                )

    def on_filter_select(self, event):
        filter_type = self.duration_filter_var.get()

        # Clear old data
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)

        # Add filtered data
        for data in self.log_data:
            duration = data["duration_seconds"]
            include = False

            if filter_type == "All":
                include = True
            elif filter_type == "Fast (<0.1s)" and duration < 0.1:
                include = True
            elif filter_type == "Medium (0.1-0.5s)" and 0.1 <= duration <= 0.5:
                include = True
            elif filter_type == "Slow (>0.5s)" and duration > 0.5:
                include = True

            if include:
                self.analysis_tree.insert(
                    "",
                    "end",
                    values=(
                        data["function"],
                        data["start_time"],
                        data["end_time"],
                        f"{duration:.3f}",
                        data["details"],
                    ),
                )

    def export_data(self):
        try:
            # Create DataFrame from data
            data = []
            for item in self.log_data:
                data.append(
                    {
                        "Function": item["function"],
                        "Start Time": item["start_time"],
                        "End Time": item["end_time"],
                        "Duration (s)": item["duration_seconds"],
                        "Details": item["details"],
                    }
                )

            df = pd.DataFrame(data)

            # Save to Excel
            df.to_excel("execution_time_analysis.xlsx", index=False, engine="openpyxl")

            # Also save statistics
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
            with pd.ExcelWriter(
                "execution_time_analysis.xlsx", engine="openpyxl", mode="a"
            ) as writer:
                stats_df.to_excel(writer, sheet_name="Statistics", index=False)

            messagebox.showinfo("Success", "Data exported to Excel successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")

    def refresh_data(self):
        self.load_log_file()


if __name__ == "__main__":
    root = ctk.CTk()
    app = AdvancedLogAnalyzer(root)
    root.mainloop()
