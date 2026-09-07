"""
Today's Work — Employee Task Dashboard

"""

import json
import os
import webbrowser
import tkinter as tk
from datetime import datetime
from tkinter import Tk, StringVar, messagebox, filedialog
from tkinter import ttk
# Setup
DATA_FILE = "tasks.json"
APP_TITLE = "Today's Work — Employee Task Dashboard"

COLOR_BG = "whitesmoke"
COLOR_HEADER_BG = "midnightblue"
COLOR_HEADER_FG = "white"
COLOR_CARD_BG = "white"
COLOR_ACCENT = "royalblue"
COLOR_SUCCESS = "green"
COLOR_PENDING = "darkorange"
COLOR_TEXT = "darkslategray"
COLOR_MUTED = "gray"

FONT_FAMILY = "Segoe UI"
# Data
# so this part can be tested or explained completely on its own
def load_all_data():
    """Load saved tasks."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def save_all_data(all_data):
    """Save tasks to JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

def get_today_key():
    """Get today's date."""
    return datetime.now().strftime("%Y-%m-%d")

def get_next_id(tasks):
    """Get the next task id."""
    return max((t["id"] for t in tasks), default=0) + 1
# Setup
class TaskDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x640")
        self.root.minsize(900, 560)
        self.root.configure(bg=COLOR_BG)
        self.all_data = load_all_data()
        self.date_key = get_today_key()
        self.tasks = self.all_data.get(self.date_key, [])

        self._configure_styles()
        self._build_header()
        self._build_input_row()
        self._build_body()
        self._build_footer()

        self.refresh_all()
# Styles
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview", background=COLOR_CARD_BG, fieldbackground=COLOR_CARD_BG,
                        foreground=COLOR_TEXT, rowheight=28, font=(FONT_FAMILY, 10))
        style.configure("Treeview.Heading", background="lightgray", foreground=COLOR_TEXT,
                        font=(FONT_FAMILY, 10, "bold"))
        style.map("Treeview", background=[("selected", COLOR_ACCENT)],
                  foreground=[("selected", "white")])

        style.configure("Accent.TButton", background=COLOR_ACCENT, foreground="white",
                        font=(FONT_FAMILY, 10, "bold"), padding=6)
        style.map("Accent.TButton", background=[("active", "blue")])

        style.configure("Success.TButton", background=COLOR_SUCCESS, foreground="white",
                        font=(FONT_FAMILY, 10, "bold"), padding=6)
        style.map("Success.TButton", background=[("active", "darkgreen")])

        style.configure("Danger.TButton", background="red", foreground="white",
                        font=(FONT_FAMILY, 10, "bold"), padding=6)
        style.map("Danger.TButton", background=[("active", "darkred")])

        style.configure("Green.Horizontal.TProgressbar", troughcolor="lightgray",
                        background=COLOR_SUCCESS, thickness=18)
# Header
    def _build_header(self):
        bar = tk.Frame(self.root, bg=COLOR_HEADER_BG, height=70)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(bar, text="Today's Work", bg=COLOR_HEADER_BG, fg=COLOR_HEADER_FG,
                 font=(FONT_FAMILY, 18, "bold")).pack(side="left", padx=20)
        tk.Label(bar, text="Employee Task Dashboard", bg=COLOR_HEADER_BG, fg="lightskyblue",
                 font=(FONT_FAMILY, 11)).pack(side="left", pady=(20, 0))

        self.date_lbl = tk.Label(bar, text=self._pretty_date(), bg=COLOR_HEADER_BG,
                                  fg="lightsteelblue", font=(FONT_FAMILY, 11))
        self.date_lbl.pack(side="right", padx=20)

    def _pretty_date(self):
        return datetime.now().strftime("%A, %d %B %Y")
# Task input
    def _build_input_row(self):
        row = tk.Frame(self.root, bg=COLOR_BG)
        row.pack(fill="x", padx=20, pady=(16, 8))

        self.task_input = StringVar()
        entry = ttk.Entry(row, textvariable=self.task_input, font=(FONT_FAMILY, 11))
        entry.pack(side="left", fill="x", expand=True, ipady=5)
        entry.bind("<Return>", lambda e: self.add_task())
        entry.focus()

        ttk.Button(row, text="+ Add Task", style="Accent.TButton",
                   command=self.add_task).pack(side="left", padx=(10, 0))
# Main area
    def _build_body(self):
        body = tk.Frame(self.root, bg=COLOR_BG)
        body.pack(fill="both", expand=True, padx=20, pady=8)
        left = tk.Frame(body, bg=COLOR_CARD_BG, highlightbackground="lightgray",
                        highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        columns = ("status", "task", "time")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("status", text="Status")
        self.tree.heading("task", text="Task")
        self.tree.heading("time", text="Added / Completed")
        self.tree.column("status", width=90, anchor="center", stretch=False)
        self.tree.column("task", width=320, anchor="w", stretch=True)
        self.tree.column("time", width=170, anchor="center", stretch=False)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", lambda e: self.toggle_complete())   # double-click toggles done/pending
        self.tree.bind("<Delete>", lambda e: self.delete_task())          # Delete key removes the task

        btn_row = tk.Frame(left, bg=COLOR_CARD_BG)
        btn_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(btn_row, text="Mark Complete / Pending", style="Success.TButton",
                   command=self.toggle_complete).pack(side="left")
        ttk.Button(btn_row, text="Delete Task", style="Danger.TButton",
                   command=self.delete_task).pack(side="left", padx=8)
        right = tk.Frame(body, bg=COLOR_CARD_BG, width=280,
                         highlightbackground="lightgray", highlightthickness=1)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="Progress", bg=COLOR_CARD_BG, fg=COLOR_TEXT,
                 font=(FONT_FAMILY, 12, "bold")).pack(anchor="w", padx=14, pady=(14, 4))

        self.progress_bar = ttk.Progressbar(right, style="Green.Horizontal.TProgressbar",
                                            orient="horizontal", mode="determinate", length=240)
        self.progress_bar.pack(padx=14, pady=4)

        self.progress_lbl = tk.Label(right, text="0% complete", bg=COLOR_CARD_BG,
                                     fg=COLOR_MUTED, font=(FONT_FAMILY, 10))
        self.progress_lbl.pack(anchor="w", padx=14)

        self.counts_lbl = tk.Label(right, text="", bg=COLOR_CARD_BG, fg=COLOR_TEXT,
                                   font=(FONT_FAMILY, 10), justify="left")
        self.counts_lbl.pack(anchor="w", padx=14, pady=(8, 14))

        sep = tk.Frame(right, bg="lightgray", height=1)
        sep.pack(fill="x", padx=14)

        tk.Label(right, text="Key Accomplishments", bg=COLOR_CARD_BG, fg=COLOR_TEXT,
                 font=(FONT_FAMILY, 12, "bold")).pack(anchor="w", padx=14, pady=(14, 4))
        self.accomplishments_box = tk.Text(right, bg="snow", fg=COLOR_TEXT,
                                           relief="flat", font=(FONT_FAMILY, 10),
                                           highlightthickness=0, wrap="word",
                                           state="disabled", padx=4, pady=2)
        self.accomplishments_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))
# Footer
    def _build_footer(self):
        footer = tk.Frame(self.root, bg=COLOR_BG)
        footer.pack(fill="x", padx=20, pady=(0, 16))

        ttk.Button(footer, text="Export Today's Report (HTML)", style="Accent.TButton",
                   command=self.export_html_report).pack(side="right")

        tk.Label(footer, text=f"Data file: {DATA_FILE}", bg=COLOR_BG,
                 fg=COLOR_MUTED, font=(FONT_FAMILY, 9)).pack(side="left")
# Add task
    def add_task(self):
        text = self.task_input.get().strip()
        if not text:
            messagebox.showwarning("Empty Task", "Please type a task before adding it.")
            return

        new_task = {
            "id": get_next_id(self.tasks),
            "text": text,
            "status": "pending",
            "created_at": datetime.now().strftime("%I:%M %p"),
            "completed_at": None,
        }
        self.tasks.append(new_task)
        self.task_input.set("")
        self.save_and_refresh()
# Complete or pending
    def toggle_complete(self):
        task = self._get_selected_task()
        if task is None:
            messagebox.showinfo("No Task Selected", "Select a task first.")
            return

        if task["status"] == "pending":
            task["status"] = "completed"
            task["completed_at"] = datetime.now().strftime("%I:%M %p")
        else:
            task["status"] = "pending"
            task["completed_at"] = None

        self.save_and_refresh()
# Delete task
    def delete_task(self):
        task = self._get_selected_task()
        if task is None:
            messagebox.showinfo("No Task Selected", "Select a task first.")
            return

        confirm = messagebox.askyesno("Delete Task", f'Delete this task?\n\n"{task["text"]}"')
        if confirm:
            self.tasks.remove(task)
            self.save_and_refresh()

    def _get_selected_task(self):
        """Get the selected task."""
        selection = self.tree.selection()
        if not selection:
            return None
        task_id = int(selection[0])  # the task's id is used as the Treeview row id
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
# Save changes
    def save_and_refresh(self):
        self.all_data[self.date_key] = self.tasks
        save_all_data(self.all_data)
        self.refresh_all()

    def refresh_all(self):
        self.refresh_tree()
        self.refresh_progress()
        self.refresh_accomplishments()
# Show tasks
    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            if task["status"] == "completed":
                status_display = "Done"
                time_display = f"Done {task['completed_at']}"
            else:
                status_display = "Pending"
                time_display = f"Added {task['created_at']}"

            self.tree.insert("", "end", iid=str(task["id"]),
                             values=(status_display, task["text"], time_display))
# Show progress
    def refresh_progress(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["status"] == "completed")
        pending = total - completed
        percent = round((completed / total) * 100) if total else 0

        self.progress_bar["value"] = percent
        self.progress_lbl.config(text=f"{percent}% complete")
        self.counts_lbl.config(
            text=f"Total tasks: {total}\nCompleted: {completed}\nPending: {pending}"
        )
# Show accomplishments
    def refresh_accomplishments(self):
        completed_tasks = [t for t in self.tasks if t["status"] == "completed"]

        self.accomplishments_box.config(state="normal")   # unlock for editing
        self.accomplishments_box.delete("1.0", "end")
        if not completed_tasks:
            self.accomplishments_box.insert("end", "No tasks completed yet today.")
        else:
            for task in completed_tasks:
                self.accomplishments_box.insert("end", f"\u2022 {task['text']}\n")
        self.accomplishments_box.config(state="disabled")  # lock again (read-only)
# Export report
    def export_html_report(self):
        if not self.tasks:
            messagebox.showinfo("Nothing to Export", "Add some tasks first.")
            return

        default_name = f"daily_report_{self.date_key}.html"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=default_name,
            filetypes=[("HTML file", "*.html")],
            title="Save Today's Report",
        )
        if not filepath:
            return  # user cancelled the dialog

        html_content = self._build_html_report()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        if messagebox.askyesno("Report Exported", "Report saved successfully.\nOpen it now?"):
            webbrowser.open(f"file://{os.path.abspath(filepath)}")

    def _build_html_report(self):
        """Create the HTML report."""
        total = len(self.tasks)
        completed = [t for t in self.tasks if t["status"] == "completed"]
        pending = [t for t in self.tasks if t["status"] == "pending"]
        percent = round((len(completed) / total) * 100) if total else 0

        completed_items = "".join(
            f'<li><span class="tick">DONE</span> {self._escape(t["text"])} '
            f'<span class="time">({t["completed_at"]})</span></li>'
            for t in completed
        ) or "<li class='empty'>No tasks completed today.</li>"

        pending_items = "".join(
            f'<li><span class="dot">-</span> {self._escape(t["text"])} '
            f'<span class="time">(added {t["created_at"]})</span></li>'
            for t in pending
        ) or "<li class='empty'>No pending tasks — great job!</li>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Daily Report — {self.date_key}</title>
<style>
    :root {{
        --accent: {COLOR_ACCENT};
        --success: {COLOR_SUCCESS};
        --pending: {COLOR_PENDING};
        --text: {COLOR_TEXT};
        --muted: {COLOR_MUTED};
    }}
    * {{ box-sizing: border-box; }}
    body {{
        font-family: 'Segoe UI', Arial, sans-serif;
        background: whitesmoke;
        color: var(--text);
        margin: 0;
        padding: 40px 20px;
    }}
    .container {{
        max-width: 720px;
        margin: 0 auto;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        overflow: hidden;
    }}
    .header {{
        background: midnightblue;
        color: white;
        padding: 28px 32px;
    }}
    .header h1 {{
        margin: 0 0 4px 0;
        font-size: 24px;
    }}
    .header p {{
        margin: 0;
        color: lightskyblue;
        font-size: 14px;
    }}
    .stats {{
        display: flex;
        justify-content: space-between;
        padding: 24px 32px;
        border-bottom: 1px solid lightgray;
    }}
    .stat {{
        text-align: center;
    }}
    .stat .value {{
        font-size: 26px;
        font-weight: bold;
    }}
    .stat .label {{
        font-size: 12px;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .progress-wrap {{
        padding: 20px 32px;
    }}
    .progress-bar-bg {{
        background: lightgray;
        border-radius: 8px;
        height: 16px;
        overflow: hidden;
    }}
    .progress-bar-fill {{
        background: var(--success);
        height: 100%;
        width: {percent}%;
        border-radius: 8px 0 0 8px;
    }}
    .section {{
        padding: 20px 32px;
    }}
    .section h2 {{
        font-size: 16px;
        margin-bottom: 10px;
        border-left: 4px solid var(--accent);
        padding-left: 10px;
    }}
    ul {{
        list-style: none;
        margin: 0;
        padding: 0;
    }}
    li {{
        padding: 8px 0;
        border-bottom: 1px dashed lightgray;
        font-size: 14px;
    }}
    li:last-child {{ border-bottom: none; }}
    .tick {{ color: var(--success); font-weight: bold; margin-right: 6px; }}
    .dot {{ color: var(--pending); font-weight: bold; margin-right: 6px; }}
    .time {{ color: var(--muted); font-size: 12px; }}
    .empty {{ color: var(--muted); font-style: italic; }}
    .footer {{
        padding: 16px 32px;
        text-align: center;
        color: var(--muted);
        font-size: 12px;
    }}
</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Today's Work — Daily Report</h1>
            <p>{self._pretty_date()}</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="value">{total}</div>
                <div class="label">Total Tasks</div>
            </div>
            <div class="stat">
                <div class="value" style="color: var(--success);">{len(completed)}</div>
                <div class="label">Completed</div>
            </div>
            <div class="stat">
                <div class="value" style="color: var(--pending);">{len(pending)}</div>
                <div class="label">Pending</div>
            </div>
            <div class="stat">
                <div class="value" style="color: var(--accent);">{percent}%</div>
                <div class="label">Progress</div>
            </div>
        </div>

        <div class="progress-wrap">
            <div class="progress-bar-bg">
                <div class="progress-bar-fill"></div>
            </div>
        </div>

        <div class="section">
            <h2>Key Accomplishments</h2>
            <ul>{completed_items}</ul>
        </div>

        <div class="section">
            <h2>Pending / Carried Over</h2>
            <ul>{pending_items}</ul>
        </div>

        <div class="footer">
            Generated automatically by Today's Work — Employee Task Dashboard
        </div>
    </div>
</body>
</html>"""

    @staticmethod
    def _escape(text):
        """Escape text before putting it in HTML."""
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
        )
# Start app
def main():
    root = Tk()
    TaskDashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
