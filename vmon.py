#!/usr/bin/env python3

"""
VMON - Simple TUI System Monitor
Python implementation using only standard libraries
Shows CPU and Memory usage as ASCII line charts
"""

import curses
import subprocess
import time
from datetime import datetime

# Configuration
MAX_POINTS = 60
UPDATE_INTERVAL = 1
CHART_WIDTH = 60
CHART_HEIGHT = 10


class SystemMonitor:
    def __init__(self):
        self.cpu_history = [0] * MAX_POINTS
        self.mem_history = [0] * MAX_POINTS
        self.timestamps = [0] * MAX_POINTS

    def get_cpu_usage(self):
        """Get overall CPU usage percentage"""
        try:
            with open("/proc/stat", "r") as f:
                # Read current CPU stats
                cpu_line = None
                for line in f:
                    if line.startswith("cpu "):
                        cpu_line = line
                        break

                if not cpu_line:
                    return 0

                # Parse CPU stats
                parts = cpu_line.split()
                user = int(parts[1])
                nice = int(parts[2])
                system = int(parts[3])
                idle = int(parts[4])
                iowait = int(parts[5])
                irq = int(parts[6])
                softirq = int(parts[7])
                steal = int(parts[8])

                total1 = user + nice + system + idle + iowait + irq + softirq + steal
                idle1 = idle + iowait

                # Sleep briefly to get delta
                time.sleep(0.1)

                # Read again
                with open("/proc/stat", "r") as f:
                    for line in f:
                        if line.startswith("cpu "):
                            cpu_line = line
                            break

                if not cpu_line:
                    return 0

                parts = cpu_line.split()
                user = int(parts[1])
                nice = int(parts[2])
                system = int(parts[3])
                idle = int(parts[4])
                iowait = int(parts[5])
                irq = int(parts[6])
                softirq = int(parts[7])
                steal = int(parts[8])

                total2 = user + nice + system + idle + iowait + irq + softirq + steal
                idle2 = idle + iowait

                total_diff = total2 - total1
                idle_diff = idle2 - idle1

                if total_diff > 0:
                    usage = int(100 * (total_diff - idle_diff) / total_diff)
                    return usage
                else:
                    return 0

        except Exception:
            return 0

    def get_mem_usage(self):
        """Get memory usage percentage"""
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = f.read()

            # Extract memory values
            memtotal = self._extract_mem_value(meminfo, "MemTotal")
            memfree = self._extract_mem_value(meminfo, "MemFree")
            buffers = self._extract_mem_value(meminfo, "Buffers")
            cached = self._extract_mem_value(meminfo, "Cached")

            if memtotal > 0:
                memused = memtotal - memfree - buffers - cached
                usage = int(100 * memused / memtotal)
                return usage
            else:
                return 0

        except Exception:
            return 0

    def _extract_mem_value(self, meminfo, key):
        """Extract memory value from meminfo"""
        for line in meminfo.split("\n"):
            if line.startswith(key):
                parts = line.split()
                if len(parts) >= 2:
                    return int(parts[1])
        return 0

    def add_data_point(self, cpu, mem):
        """Add data point to history (circular buffer)"""
        self.cpu_history.pop(0)
        self.mem_history.pop(0)
        self.timestamps.pop(0)

        self.cpu_history.append(cpu)
        self.mem_history.append(mem)
        self.timestamps.append(int(time.time()))

    def draw_line_chart(self, data, title, height, width):
        """Draw a single line chart"""
        lines = []

        # Draw title (centered)
        title_padding = max(0, (width - len(title)) // 2)
        title_line = " " * title_padding + title
        lines.append(title_line)

        # Draw chart area
        for y in range(height, -1, -1):
            line = []

            # Draw y-axis label
            if y % 2 == 0:
                label = f"{y * 100 // height}%"
                line.append(f"{label:>4} |")
            else:
                line.append("     |")

            # Draw data points
            for x in range(len(data)):
                value = data[x]
                y_pos = height * value // 100

                if y_pos == y:
                    line.append("▄")
                elif y_pos > y:
                    line.append(" ")
                else:
                    line.append(" ")

            line.append("|")
            lines.append("".join(line))

        # Draw x-axis
        x_axis = "     +" + "-" * width + "+"
        lines.append(x_axis)

        # Draw x-axis labels
        x_labels = "      " + "0s"
        x_labels += " " * (width - 4)
        x_labels += f"{MAX_POINTS}s"
        lines.append(x_labels)

        return lines

    def draw_screen(self, stdscr):
        """Draw the complete screen"""
        stdscr.clear()

        # Draw CPU chart
        cpu_chart = self.draw_line_chart(
            self.cpu_history,
            f"CPU Usage (Last {MAX_POINTS}s)",
            CHART_HEIGHT,
            CHART_WIDTH,
        )

        # Draw Memory chart
        mem_chart = self.draw_line_chart(
            self.mem_history,
            f"Memory Usage (Last {MAX_POINTS}s)",
            CHART_HEIGHT,
            CHART_WIDTH,
        )

        # Combine all lines
        all_lines = cpu_chart + [""] + mem_chart

        # Add current values and controls
        current_cpu = self.cpu_history[-1]
        current_mem = self.mem_history[-1]
        all_lines.append(f"Current: CPU {current_cpu}%  Memory {current_mem}%")
        all_lines.append("Controls: q=quit, s=save current view")

        # Draw all lines
        for i, line in enumerate(all_lines):
            if i < curses.LINES - 1:
                stdscr.addstr(i, 0, line)

        stdscr.refresh()

    def save_chart(self, filename=None):
        """Save current view to file"""
        if filename is None:
            filename = f"vmon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filename, "w") as f:
                f.write("VMON - System Monitor Snapshot\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(f"System: {subprocess.getoutput('uname -a')}\n")
                f.write(f"Uptime: {subprocess.getoutput('uptime')}\n")
                f.write("\n")

                # Generate ASCII chart
                cpu_chart = self.draw_line_chart(
                    self.cpu_history,
                    f"CPU Usage (Last {MAX_POINTS}s)",
                    CHART_HEIGHT,
                    CHART_WIDTH,
                )
                mem_chart = self.draw_line_chart(
                    self.mem_history,
                    f"Memory Usage (Last {MAX_POINTS}s)",
                    CHART_HEIGHT,
                    CHART_WIDTH,
                )

                for line in cpu_chart:
                    f.write(line + "\n")
                f.write("\n")
                for line in mem_chart:
                    f.write(line + "\n")

                current_cpu = self.cpu_history[-1]
                current_mem = self.mem_history[-1]
                f.write(f"Current: CPU {current_cpu}%  Memory {current_mem}%\n")

            return filename

        except Exception as e:
            return None


def main():
    """Main function"""
    monitor = SystemMonitor()

    # Initialize curses
    stdscr = curses.initscr()
    curses.curs_set(0)  # Hide cursor
    curses.noecho()  # Don't echo keypresses
    curses.cbreak()  # Disable line buffering
    stdscr.keypad(1)  # Enable special keys
    stdscr.nodelay(1)  # Non-blocking input

    try:
        # Main loop
        while True:
            # Collect data
            cpu = monitor.get_cpu_usage()
            mem = monitor.get_mem_usage()

            # Update history
            monitor.add_data_point(cpu, mem)

            # Draw screen
            monitor.draw_screen(stdscr)

            # Handle input (non-blocking)
            key = stdscr.getch()
            if key == ord("q"):
                break
            elif key == ord("s"):
                # Save chart
                filename = monitor.save_chart()
                if filename:
                    # Show confirmation
                    confirmation = f"Chart saved to {filename}"
                    stdscr.addstr(curses.LINES - 1, 0, confirmation)
                    stdscr.refresh()
                    time.sleep(1)  # Show confirmation for 1 second

            # Update interval
            time.sleep(UPDATE_INTERVAL)

    finally:
        # Cleanup
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        print("VMON exited")


if __name__ == "__main__":
    main()
