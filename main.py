import re
import json
import time
import random
import threading
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from IPython.display import display, HTML, clear_output
    import matplotlib.pyplot as plt
    import numpy as np
    COLAB_MODE = True
except ImportError:
    COLAB_MODE = False

class TaskType(Enum):
    FILE_OPERATION = "file_operation"
    BROWSER_ACTION = "browser_action"
    SYSTEM_COMMAND = "system_command"
    APPLICATION_TASK = "application_task"
    WORKFLOW = "workflow"

@dataclass
class Task:
    id: str
    type: TaskType
    command: str
    status: str = "pending"
    result: str = ""
    timestamp: str = ""
    execution_time: float = 0.0

class VirtualDesktop:
    def __init__(self):
        self.applications = {
            "browser": {"status": "closed", "tabs": [], "current_url": ""},
            "file_manager": {"status": "closed", "current_path": "/home/user"},
            "text_editor": {"status": "closed", "current_file": "", "content": ""},
            "email": {"status": "closed", "unread": 3, "inbox": []},
            "terminal": {"status": "closed", "history": []}
        }

        self.file_system = {
                "/home/user/": {
                "documents/": {
                    "report.txt": "Important quarterly report content...",
                    "notes.md": "# Meeting Notes\n- Project update\n- Budget review"
                },
                "downloads/": {
                    "data.csv": "name,age,city\nJohn,25,NYC\nJane,30,LA",
                    "image.jpg": "[Binary image data]"
                },
                "desktop/": {}
            }
        }
        self.screen_state = {
            "active_window": None,
            "mouse_position": (0, 0),
            "clipboard": ""
        }

    def get_system_info(self) -> Dict:
        return {
            "cpu_usage": random.randint(5, 25),
            "memory_usage": random.randint(30, 60),
            "disk_space": random.randint(60, 90),
            "network_status": "connected",
            "uptime": "2 hours 15 minutes"
        }

class NLPProcessor:
    """Processes natural language commands and extracts intents"""

    def __init__(self):
        self.intent_patterns = {
            TaskType.BROWSER_ACTION: [
                r"(open|visit|go to|navigate)\s+.*\.(com|org|net)",
                r"(search|google|find)\s+.*",
                r"(click|press|select)\s+(button|link)",
                r"(fill|enter|type)\s+.*"
            ],
            TaskType.FILE_OPERATION: [
                r"(open|create|delete|copy|move|find|save|edit|write|list|show|download|upload)\s+.*"
            ],
            TaskType.SYSTEM_COMMAND: [
                r"(check|show)\s+(system|cpu|memory|disk)",
                r"(run|execute|start)\s+program",
                r"(restart|shutdown|sleep)",
                r"(install|update|configure)\s+.*"
            ],
            TaskType.APPLICATION_TASK: [
                r"(open|start|launch)\s+(browser|editor|email|terminal)",
                r"(close|quit|exit)\s+.*",
                r"(send|compose|reply)\s+(email|message)",
                r"(edit|modify|change)\s+.*"
            ],
            TaskType.WORKFLOW: [
                r"(automate|batch|bulk)\s+.*",
                r"(combine|merge|join)\s+.*",
                r"(schedule|remind|notify)\s+.*",
                r"(backup|sync|export)\s+.*"
            ]
        }
    def extract_intent(self, command: str) -> Tuple[TaskType, float]:
        """Extract task type and confidence from natural language command"""
        command_lower = command.lower()
        best_match = TaskType.SYSTEM_COMMAND
        best_confidence = 0.0

        for task_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command_lower):
                    confidence = len(re.findall(pattern, command_lower)) * 0.3
                    if confidence > best_confidence:
                        best_match = task_type
                        best_confidence = confidence

        return best_match, min(best_confidence, 1.0)

    def extract_parameters(self, command: str, task_type: TaskType) -> Dict[str, str]:
        """Extract parameters from command based on task type"""
        params = {}
        command_lower = command.lower()

        if task_type == TaskType.FILE_OPERATION:
            file_match = re.search(r'[\w/.-]+\.\w+', command)
            if file_match:
                params['filename'] = file_match.group()

            path_match = re.search(r'/[\w/.-]+', command)
            if path_match:
                params['path'] = path_match.group()

        elif task_type == TaskType.BROWSER_ACTION:
            url_match = re.search(r'https?://[\w.-]+|[\w.-]+\.(com|org|net|edu)', command)
            if url_match:
                params['url'] = url_match.group()

            search_match = re.search(r'(?:search|find|google) for ["\']?([^"\']+)["\']?', command_lower)
            if search_match:
                params['query'] = search_match.group(1)

        elif task_type == TaskType.APPLICATION_TASK:
            app_match = re.search(r'(browser|editor|email|terminal|calculator)', command_lower)
            if app_match:
                params['application'] = app_match.group(1)

        return params

class TaskExecutor:
    """Executes tasks on the virtual desktop"""

    def __init__(self, desktop: VirtualDesktop):
        self.desktop = desktop
        self.execution_log = []

    def execute_file_operation(self, params: Dict[str, str], command: str) -> str:
        """Simulate file operations"""
        if "open" in command.lower():
            filename = params.get('filename', 'unknown.txt')
            return f" Opened file: {filename}\n File contents loaded in text editor"

        elif "create" in command.lower():
            filename = params.get('filename', 'new_file.txt')
            return f" Created new file: {filename}\n File ready for editing"

        elif "list" in command.lower():
            files = list(self.desktop.file_system["/home/user/documents/"].keys())
            return f" Files found:\n" + "\n".join([f"  - {f}" for f in files])

        return " File operation completed successfully"

    def execute_browser_action(self, params: Dict[str, str], command: str) -> str:
        """Simulate browser actions"""
        if "open" in command.lower() or "visit" in command.lower():
            url = params.get('url', 'example.com')
            self.desktop.applications["browser"]["current_url"] = url
            self.desktop.applications["browser"]["status"] = "open"
            return f" Navigated to: {url}\n Page loaded successfully"

        elif "search" in command.lower():
            query = params.get('query', 'search term')
            return f" Searching for: '{query}'\n Found 1,247 results"

        return " Browser action completed"

    def execute_system_command(self, params: Dict[str, str], command: str) -> str:
        """Simulate system commands"""
        if "check" in command.lower() or "show" in command.lower():
            info = self.desktop.get_system_info()
            return f" System Status:\n" + \
                   f"  CPU: {info['cpu_usage']}%\n" + \
                   f"  Memory: {info['memory_usage']}%\n" + \
                   f"  Disk: {info['disk_space']}% used\n" + \
                   f"  Network: {info['network_status']}"

        return " System command executed"

    def execute_application_task(self, params: Dict[str, str], command: str) -> str:
        """Simulate application tasks"""
        app = params.get('application', 'unknown')

        if "open" in command.lower():
            self.desktop.applications[app]["status"] = "open"
            return f" Launched {app.title()}\n Application ready for use"

        elif "close" in command.lower():
            if app in self.desktop.applications:
                self.desktop.applications[app]["status"] = "closed"
                return f" Closed {app.title()}"

        return f" {app.title()} task completed"

    def execute_workflow(self, params: Dict[str, str], command: str) -> str:
        """Simulate complex workflow execution"""
        steps = [
            "Analyzing workflow requirements...",
            "Preparing automation steps...",
            "Executing batch operations...",
            "Validating results...",
            "Generating report..."
        ]

        result = " Workflow Execution:\n"
        for i, step in enumerate(steps, 1):
            result += f"  {i}. {step} Y\n"
            if COLAB_MODE:
                time.sleep(0.1)

        return result + " Workflow completed successfully!"

class DesktopAgent:
    """Main desktop automation agent class - coordinates all components"""

    def __init__(self):
        self.desktop = VirtualDesktop()
        self.nlp = NLPProcessor()
        self.executor = TaskExecutor(self.desktop)
        self.task_history = []
        self.active = True
        self.stats = {
            "tasks_completed": 0,
            "success_rate": 100.0,
            "average_execution_time": 0.0
        }

    def process_command(self, command: str) -> Task:
        """Process a natural language command and execute it"""
        start_time = time.time()

        task_id = f"task_{len(self.task_history) + 1:04d}"
        task_type, confidence = self.nlp.extract_intent(command)

        task = Task(
            id=task_id,
            type=task_type,
            command=command,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )

        try:
            params = self.nlp.extract_parameters(command, task_type)

            if task_type == TaskType.FILE_OPERATION:
                result = self.executor.execute_file_operation(params, command)
            elif task_type == TaskType.BROWSER_ACTION:
                result = self.executor.execute_browser_action(params, command)
            elif task_type == TaskType.SYSTEM_COMMAND:
                result = self.executor.execute_system_command(params, command)
            elif task_type == TaskType.APPLICATION_TASK:
                result = self.executor.execute_application_task(params, command)
            elif task_type == TaskType.WORKFLOW:
                result = self.executor.execute_workflow(params, command)
            else:
                result = " Command type not recognized"

            task.status = "completed"
            task.result = result
            self.stats["tasks_completed"] += 1

        except Exception as e:
            task.status = "failed"
            task.result = f" Error: {str(e)}"

        task.execution_time = round(time.time() - start_time, 3)
        self.task_history.append(task)
        self.update_stats()

        return task

    def update_stats(self):
        """Update agent statistics"""
        if self.task_history:
            successful_tasks = sum(1 for t in self.task_history if t.status == "completed")
            self.stats["success_rate"] = round((successful_tasks / len(self.task_history)) * 100, 1)

            total_time = sum(t.execution_time for t in self.task_history)
            self.stats["average_execution_time"] = round(total_time / len(self.task_history), 3)

    def get_status_dashboard(self) -> str:
        """Generate a status dashboard"""
        recent_tasks = self.task_history[-5:] if self.task_history else []

        dashboard = f"""
+----------------------------------------------------------------------------------------------------------------+
|                AI DESKTOP AGENT STATUS            |
+------------------------------------------------------+
| Statistics:                                       |
|   * Tasks Completed: {self.stats['tasks_completed']:<10}                |
|   * Success Rate:    {self.stats['success_rate']:<10}%               |
|   * Avg Exec Time:   {self.stats['average_execution_time']:<10}s               |
+------------------------------------------------------+
|   Desktop Applications:                            |
"""

        for app, info in self.desktop.applications.items():
            status_icon = "[+]" if info["status"] == "open" else "[-]"
            dashboard += f"|   {status_icon} {app.title():<12} ({info['status']:<6})              |\n"

        dashboard += "+------------------------------------------------------+\n"
        dashboard += "|  Recent Tasks:                                    |\n"

        if recent_tasks:
            for task in recent_tasks:
                status_icon = "[Y]" if task.status == "completed" else "[N]"
                dashboard += f"| {status_icon} {task.timestamp} - {task.type.value:<15} |\n"
        else:
            dashboard += "|   No tasks executed yet                              |\n"

        dashboard += "+----------------------------------------------------------------------------------------------------------------+"

        return dashboard

def run_advanced_demo():
    """Run an advanced interactive demo of the AI Desktop Agent"""

    print("Initializing Advanced AI Desktop Automation Agent...")
    time.sleep(1)

    agent = DesktopAgent()

    print("\n" + "="*60)
    print("AI DESKTOP AUTOMATION AGENT - ADVANCED TUTORIAL")
    print("="*60)
    print("A sophisticated AI agent that understands natural language")
    print("commands and automates desktop tasks in a simulated environment.")
    print("\nTry these example commands:")
    print("  • 'open the browser and go to github.com'")
    print("  • 'create a new file called report.txt'")
    print("  • 'check system performance'")
    print("  • 'show me the files in documents folder'")
    print("  • 'automate email processing workflow'")

    demo_commands = [
        "check system status and show CPU usage",
        "open browser and navigate to github.com",
        "create a new file called meeting_notes.txt",
        "list all files in the documents directory",
        "launch text editor application",
        "automate data backup workflow"
    ]

    print(f"\nRunning {len(demo_commands)} demonstration commands...\n")

    for i, command in enumerate(demo_commands, 1):
        print(f"[{i}/{len(demo_commands)}] Command: '{command}'")
        print("-" * 50)

        task = agent.process_command(command)

        print(f"Task ID: {task.id}")
        print(f"Type: {task.type.value}")
        print(f"Status: {task.status}")
        print(f"Execution Time: {task.execution_time}s")
        print(f"Result:\n{task.result}")
        print()

        if COLAB_MODE:
            time.sleep(0.5)

    print("\n" + "="*60)
    print("FINAL AGENT STATUS")
    print("="*60)
    print(agent.get_status_dashboard())

    return agent

def interactive_mode(agent):
    """Run interactive mode for user input"""
    print("\nINTERACTIVE MODE ACTIVATED")
    print("Type your commands below (type 'quit' to exit, 'status' for dashboard):")
    print("-" * 60)

    while True:
        try:
            user_input = input("\nAgent> ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("AI Agent shutting down. Goodbye!")
                break

            elif user_input.lower() in ['status', 'dashboard']:
                print(agent.get_status_dashboard())
                continue

            elif user_input.lower() in ['help', '?']:
                print("Available commands:")
                print("  • Any natural language command")
                print("  • 'status' - Show agent dashboard")
                print("  • 'help' - Show this help")
                print("  • 'quit' - Exit AI Agent")
                continue

            elif not user_input:
                continue

            print(f"Processing: '{user_input}'...")
            task = agent.process_command(user_input)

            print(f"\n Task {task.id} [{task.type.value}] - {task.status}")
            print(task.result)

        except KeyboardInterrupt:
            print("\n\n AI Agent interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


try:
    import tkinter as tk
    from tkinter import scrolledtext, Entry, Button, Label, Frame
    TINTER_AVAILABLE = True
except ImportError:
    TINTER_AVAILABLE = False


def run_gui_mode(agent):
    """Run the agent in GUI mode"""

    if not TINTER_AVAILABLE:
        print("tkinter is not available. Cannot run in GUI mode.")
        return

    window = tk.Tk()
    window.title("AI Desktop Agent")

    main_frame = Frame(window)
    main_frame.pack(padx=10, pady=10)

    output_box = scrolledtext.ScrolledText(main_frame, width=80, height=20)
    output_box.pack(pady=5)

    input_frame = Frame(main_frame)
    input_frame.pack(pady=5)

    input_label = Label(input_frame, text="Command:")
    input_label.pack(side=tk.LEFT, padx=5)

    input_box = Entry(input_frame, width=60)
    input_box.pack(side=tk.LEFT)

    def execute_command():
        command = input_box.get()
        if command:
            task = agent.process_command(command)
            output_box.insert(tk.END, f">> {command}\n")
            output_box.insert(tk.END, f"{task.result}\n\n")
            input_box.delete(0, tk.END)
            output_box.see(tk.END)

    execute_button = Button(input_frame, text="Execute", command=execute_command)
    execute_button.pack(side=tk.LEFT, padx=5)

    def on_closing():
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()


if __name__ == "__main__":
    agent = run_advanced_demo()

    if COLAB_MODE:
        print("\nTo continue with interactive mode, run:")
        print("interactive_mode(agent)")
    else:
        # Add a command line argument to choose mode
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--gui":
            run_gui_mode(agent)
        else:
            interactive_mode(agent)