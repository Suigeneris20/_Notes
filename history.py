# ui/screens/history.py
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Static, Button, DataTable, Input, Select
)
from textual.containers import Container, Horizontal, Vertical
from datetime import datetime, timedelta

# Import your database function
from db.operations import get_closed_sessions, get_session_statistics


class HistoryScreen(Screen):
    """Screen to view closed sessions history"""
    
    def __init__(self, user_context: dict):
        super().__init__()
        self.db_name = user_context["db_name"]
        self.user_id = user_context["user_id"]
        self.current_filter = "all"
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="history-container"):
            yield Static("Session History", classes="history-title")
            
            # Filter Panel
            with Container(classes="filter-panel"):
                yield Static("Filter Options", classes="panel-title")
                
                with Horizontal(classes="filter-row"):
                    yield Static("Time Period:", classes="filter-label")
                    yield Select(
                        [
                            ("Last 24 Hours", "24h"),
                            ("Last 7 Days", "7d"),
                            ("Last 30 Days", "30d"),
                            ("All Time", "all")
                        ],
                        value="all",
                        id="time-filter"
                    )
                    
                    yield Static("User:", classes="filter-label")
                    yield Input(
                        placeholder="User ID (leave empty for all)",
                        id="user-filter"
                    )
                    
                    yield Button(
                        "Apply Filter",
                        variant="primary",
                        id="filter-btn"
                    )
                    yield Button(
                        "Reset",
                        id="reset-btn"
                    )
            
            # Statistics Panel
            with Container(classes="stats-panel"):
                yield Static("Statistics", classes="panel-title")
                with Horizontal(classes="stats-row"):
                    with Vertical(classes="stat-box"):
                        yield Static("Total Sessions", classes="stat-label")
                        yield Static("0", id="total-sessions")
                    
                    with Vertical(classes="stat-box"):
                        yield Static("Total Slots Used", classes="stat-label")
                        yield Static("0", id="total-slots")
                    
                    with Vertical(classes="stat-box"):
                        yield Static("Avg Duration", classes="stat-label")
                        yield Static("0:00:00", id="avg-duration")
                    
                    with Vertical(classes="stat-box"):
                        yield Static("Total Duration", classes="stat-label")
                        yield Static("0:00:00", id="total-duration")
            
            # History Table
            with Container(classes="table-panel"):
                yield Static("Closed Sessions", classes="panel-title")
                yield DataTable(id="history-table")
                yield Static("", id="table-status")
            
            # Action Buttons
            with Horizontal(id="history-actions"):
                yield Button("Export CSV", variant="primary", id="export-btn")
                yield Button("Back to Dashboard", id="back-btn")
        
        yield Static(
            f"User: {self.user_id} | DB: {self.db_name}",
            id="status-bar"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize history view"""
        self.load_history()
    
    def load_history(
        self,
        time_period: str = "all",
        filter_user: str = None
    ) -> None:
        """Load closed sessions history"""
        table = self.query_one("#history-table", DataTable)
        table.clear(columns=True)
        status = self.query_one("#table-status", Static)
        
        try:
            # Get closed sessions from database
            sessions = get_closed_sessions(
                self.db_name,
                time_period=time_period,
                user_id=filter_user
            )
            
            if sessions:
                # Add columns
                table.add_columns(
                    "Session ID",
                    "User ID",
                    "Grid",
                    "App",
                    "Slots",
                    "Started",
                    "Closed",
                    "Duration",
                    "Closed By"
                )
                
                # Add rows
                for session in sessions:
                    table.add_row(
                        str(session.original_session_id),
                        session.user_id,
                        session.grid,
                        session.application,
                        str(session.slots_allocated),
                        self.format_datetime(session.created_at),
                        self.format_datetime(session.closed_at),
                        self.format_duration(session.duration_seconds),
                        session.closed_by or "Unknown"
                    )
                
                status.update(f"Showing {len(sessions)} sessions")
                status.remove_class("error-message")
                
                # Update statistics
                self.update_statistics(sessions)
            else:
                table.add_column("Status")
                table.add_row("No closed sessions found")
                status.update("No data available")
                
        except Exception as e:
            table.add_column("Error")
            table.add_row(f"Error loading history: {str(e)}")
            status.update(f"Error: {str(e)}")
            status.add_class("error-message")
    
    def update_statistics(self, sessions) -> None:
        """Update statistics panel"""
        total = len(sessions)
        total_slots = sum(s.slots_allocated for s in sessions)
        total_duration = sum(
            s.duration_seconds for s in sessions if s.duration_seconds
        )
        avg_duration = total_duration / total if total > 0 else 0
        
        self.query_one("#total-sessions", Static).update(str(total))
        self.query_one("#total-slots", Static).update(str(total_slots))
        self.query_one("#avg-duration", Static).update(
            self.format_duration(avg_duration)
        )
        self.query_one("#total-duration", Static).update(
            self.format_duration(total_duration)
        )
    
    def format_datetime(self, dt) -> str:
        """Format datetime for display"""
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def format_duration(self, seconds) -> str:
        """Format duration in seconds to HH:MM:SS"""
        if not seconds:
            return "0:00:00"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{secs:02d}"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "filter-btn":
            self.handle_filter()
        elif button_id == "reset-btn":
            self.handle_reset()
        elif button_id == "export-btn":
            self.handle_export()
        elif button_id == "back-btn":
            self.app.pop_screen()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Auto-apply when time filter changes"""
        if event.select.id == "time-filter":
            self.handle_filter()
    
    def handle_filter(self) -> None:
        """Apply filters"""
        time_filter = self.query_one("#time-filter", Select).value
        user_filter = self.query_one("#user-filter", Input).value.strip()
        
        filter_user = user_filter if user_filter else None
        self.load_history(time_period=time_filter, filter_user=filter_user)
    
    def handle_reset(self) -> None:
        """Reset all filters"""
        self.query_one("#time-filter", Select).value = "all"
        self.query_one("#user-filter", Input).value = ""
        self.load_history()
    
    def handle_export(self) -> None:
        """Export history to CSV"""
        import csv
        from datetime import datetime
        
        try:
            # Get current table data
            table = self.query_one("#history-table", DataTable)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_history_{timestamp}.csv"
            
            # Write CSV
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write headers
                headers = [col.label.plain for col in table.columns.values()]
                writer.writerow(headers)
                
                # Write rows
                for row_key in table.rows:
                    row = table.get_row(row_key)
                    writer.writerow(row)
            
            status = self.query_one("#table-status", Static)
            status.update(f"Exported to {filename}")
            status.remove_class("error-message")
            status.add_class("success-message")
            
        except Exception as e:
            status = self.query_one("#table-status", Static)
            status.update(f"Export failed: {str(e)}")
            status.add_class("error-message")


'''
/* History Screen Styles */
#history-container {
    padding: 2;
    height: 100%;
    overflow-y: auto;
}

.history-title {
    text-style: bold;
    color: $accent;
    text-align: center;
    margin-bottom: 2;
}

.filter-panel {
    background: $panel;
    border: solid $primary;
    padding: 2;
    margin-bottom: 1;
}

.filter-row {
    align: left middle;
    height: auto;
}

.filter-label {
    margin-right: 1;
    min-width: 10;
}

.filter-row Select {
    width: 20;
    margin-right: 2;
}

.filter-row Input {
    width: 30;
    margin-right: 2;
}

.stats-panel {
    background: $panel;
    border: solid $primary;
    padding: 2;
    margin-bottom: 1;
}

.stats-row {
    align: center middle;
    height: auto;
}

.stat-box {
    width: 1fr;
    align: center middle;
    padding: 1;
}

.stat-label {
    color: $text-muted;
    text-align: center;
    margin-bottom: 1;
}

.stat-box Static:not(.stat-label) {
    text-style: bold;
    color: $accent;
    text-align: center;
}

.table-panel {
    background: $panel;
    border: solid $primary;
    padding: 2;
    margin-bottom: 1;
    height: auto;
}

#history-table {
    height: 20;
    margin-bottom: 1;
}

#table-status {
    text-align: center;
    margin-top: 1;
}

#history-actions {
    align: center middle;
    height: auto;
}

#history-actions Button {
    margin: 0 1;
}
'''
