
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Static, Button, Input, TabbedContent, TabPane
)
from textual.containers import Container, Vertical, Horizontal
from textual.validation import Length, Integer

# Import your CRUD functions
from db.operations import (
    add_user,
    add_group,
    remove_user_all,
    remove_user
)


class AdminScreen(Screen):
    """Admin screen for CRUD operations"""
    
    def __init__(self, user_context: dict):
        super().__init__()
        self.db_name = user_context["db_name"]
        self.admin_user_id = user_context["user_id"]
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="admin-container"):
            yield Static("Admin Panel", classes="admin-title")
            yield Static(
                f"Database: {self.db_name}",
                classes="admin-subtitle"
            )
            
            with TabbedContent(initial="add-user-tab"):
                # Add User Tab
                with TabPane("Add User", id="add-user-tab"):
                    with Vertical(classes="form-container"):
                        yield Static("User ID:", classes="field-label")
                        yield Input(
                            placeholder="Enter user ID",
                            id="add-user-id",
                            validators=[Length(minimum=1)]
                        )
                        
                        yield Static("Grid:", classes="field-label")
                        yield Input(
                            placeholder="Enter grid",
                            id="add-user-grid",
                            validators=[Length(minimum=1)]
                        )
                        
                        yield Static(
                            "Applications (comma-separated):",
                            classes="field-label"
                        )
                        yield Input(
                            placeholder="app1, app2, app3",
                            id="add-user-apps"
                        )
                        
                        yield Static(
                            "Number of Slots:",
                            classes="field-label"
                        )
                        yield Input(
                            placeholder="Enter number of slots",
                            id="add-user-slots",
                            validators=[Integer(minimum=1)]
                        )
                        
                        yield Button(
                            "Add User",
                            variant="success",
                            id="add-user-btn"
                        )
                        yield Static("", id="add-user-message")
                
                # Add Group Tab
                with TabPane("Add Group", id="add-group-tab"):
                    with Vertical(classes="form-container"):
                        yield Static("Group Name:", classes="field-label")
                        yield Input(
                            placeholder="Enter group name",
                            id="add-group-name",
                            validators=[Length(minimum=1)]
                        )
                        
                        yield Static("Grid:", classes="field-label")
                        yield Input(
                            placeholder="Enter grid",
                            id="add-group-grid",
                            validators=[Length(minimum=1)]
                        )
                        
                        yield Static(
                            "Applications (comma-separated):",
                            classes="field-label"
                        )
                        yield Input(
                            placeholder="app1, app2, app3",
                            id="add-group-apps"
                        )
                        
                        yield Static(
                            "Number of Slots:",
                            classes="field-label"
                        )
                        yield Input(
                            placeholder="Enter number of slots",
                            id="add-group-slots",
                            validators=[Integer(minimum=1)]
                        )
                        
                        yield Button(
                            "Add Group",
                            variant="success",
                            id="add-group-btn"
                        )
                        yield Static("", id="add-group-message")
                
                # Remove User Tab
                with TabPane("Remove User", id="remove-user-tab"):
                    with Vertical(classes="form-container"):
                        yield Static(
                            "Remove All User Instances",
                            classes="section-title"
                        )
                        
                        yield Static("User ID:", classes="field-label")
                        yield Input(
                            placeholder="Enter user ID to remove",
                            id="remove-user-all-id",
                            validators=[Length(minimum=1)]
                        )
                        
                        yield Button(
                            "Remove All Instances",
                            variant="error",
                            id="remove-user-all-btn"
                        )
                        yield Static("", id="remove-all-message")
                        
                        yield Static("", classes="spacer")
                        
                        yield Static(
                            "Remove Specific User Instance",
                            classes="section-title"
                        )
                        
                        yield Static("User ID:", classes="field-label")
                        yield Input(
                            placeholder="Enter user ID",
                            id="remove-user-id",
                            validators=[Length(minimum=1)]
                        )
                        
                        yield Static("Grid:", classes="field-label")
                        yield Input(
                            placeholder="Enter grid",
                            id="remove-user-grid",
                            validators=[Length(minimum=1)]
                        )
                        
                        yield Static("Application:", classes="field-label")
                        yield Input(
                            placeholder="Enter application",
                            id="remove-user-app",
                            validators=[Length(minimum=1)]
                        )
                        
                        yield Button(
                            "Remove Specific Instance",
                            variant="error",
                            id="remove-user-btn"
                        )
                        yield Static("", id="remove-specific-message")
            
            # Bottom action buttons
            with Horizontal(id="admin-actions"):
                yield Button("Back to Dashboard", id="back-btn")
        
        yield Static(
            f"Admin: {self.admin_user_id} | DB: {self.db_name}",
            id="status-bar"
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "add-user-btn":
            self.handle_add_user()
        elif button_id == "add-group-btn":
            self.handle_add_group()
        elif button_id == "remove-user-all-btn":
            self.handle_remove_user_all()
        elif button_id == "remove-user-btn":
            self.handle_remove_user()
        elif button_id == "back-btn":
            self.app.pop_screen()
    
    def handle_add_user(self) -> None:
        """Add a new user"""
        user_id = self.query_one("#add-user-id", Input).value.strip()
        grid = self.query_one("#add-user-grid", Input).value.strip()
        apps_input = self.query_one("#add-user-apps", Input).value.strip()
        slots_input = self.query_one("#add-user-slots", Input).value.strip()
        message = self.query_one("#add-user-message", Static)
        
        # Validate inputs
        if not all([user_id, grid, apps_input, slots_input]):
            message.update("Please fill in all fields")
            message.add_class("error-message")
            return
        
        try:
            # Parse applications list
            applications = [app.strip() for app in apps_input.split(",")]
            num_slots = int(slots_input)
            
            # Call add_user function
            success = add_user(
                self.db_name,
                user_id,
                grid,
                applications,
                num_slots
            )
            
            if success:
                message.update(f"User '{user_id}' added successfully!")
                message.remove_class("error-message")
                message.add_class("success-message")
                
                # Clear inputs
                self.query_one("#add-user-id", Input).value = ""
                self.query_one("#add-user-grid", Input).value = ""
                self.query_one("#add-user-apps", Input).value = ""
                self.query_one("#add-user-slots", Input).value = ""
            else:
                message.update("Failed to add user")
                message.add_class("error-message")
                
        except ValueError:
            message.update("Invalid number of slots")
            message.add_class("error-message")
        except Exception as e:
            message.update(f"Error: {str(e)}")
            message.add_class("error-message")
    
    def handle_add_group(self) -> None:
        """Add a new group"""
        group_name = self.query_one("#add-group-name", Input).value.strip()
        grid = self.query_one("#add-group-grid", Input).value.strip()
        apps_input = self.query_one("#add-group-apps", Input).value.strip()
        slots_input = self.query_one("#add-group-slots", Input).value.strip()
        message = self.query_one("#add-group-message", Static)
        
        # Validate inputs
        if not all([group_name, grid, apps_input, slots_input]):
            message.update("Please fill in all fields")
            message.add_class("error-message")
            return
        
        try:
            # Parse applications list
            applications = [app.strip() for app in apps_input.split(",")]
            num_slots = int(slots_input)
            
            # Call add_group function
            success = add_group(
                self.db_name,
                group_name,
                grid,
                applications,
                num_slots
            )
            
            if success:
                message.update(f"Group '{group_name}' added successfully!")
                message.remove_class("error-message")
                message.add_class("success-message")
                
                # Clear inputs
                self.query_one("#add-group-name", Input).value = ""
                self.query_one("#add-group-grid", Input).value = ""
                self.query_one("#add-group-apps", Input).value = ""
                self.query_one("#add-group-slots", Input).value = ""
            else:
                message.update("Failed to add group")
                message.add_class("error-message")
                
        except ValueError:
            message.update("Invalid number of slots")
            message.add_class("error-message")
        except Exception as e:
            message.update(f"Error: {str(e)}")
            message.add_class("error-message")
    
    def handle_remove_user_all(self) -> None:
        """Remove all instances of a user"""
        user_id = self.query_one(
            "#remove-user-all-id",
            Input
        ).value.strip()
        message = self.query_one("#remove-all-message", Static)
        
        if not user_id:
            message.update("Please enter a user ID")
            message.add_class("error-message")
            return
        
        try:
            # Call remove_user_all function
            success = remove_user_all(self.db_name, user_id)
            
            if success:
                message.update(
                    f"All instances of user '{user_id}' removed"
                )
                message.remove_class("error-message")
                message.add_class("success-message")
                
                # Clear input
                self.query_one("#remove-user-all-id", Input).value = ""
            else:
                message.update(f"User '{user_id}' not found")
                message.add_class("error-message")
                
        except Exception as e:
            message.update(f"Error: {str(e)}")
            message.add_class("error-message")
    
    def handle_remove_user(self) -> None:
        """Remove specific user instance"""
        user_id = self.query_one("#remove-user-id", Input).value.strip()
        grid = self.query_one("#remove-user-grid", Input).value.strip()
        application = self.query_one(
            "#remove-user-app",
            Input
        ).value.strip()
        message = self.query_one("#remove-specific-message", Static)
        
        if not all([user_id, grid, application]):
            message.update("Please fill in all fields")
            message.add_class("error-message")
            return
        
        try:
            # Call remove_user function
            success = remove_user(
                self.db_name,
                user_id,
                grid,
                application
            )
            
            if success:
                message.update(
                    f"User '{user_id}' removed from {grid}/{application}"
                )
                message.remove_class("error-message")
                message.add_class("success-message")
                
                # Clear inputs
                self.query_one("#remove-user-id", Input).value = ""
                self.query_one("#remove-user-grid", Input).value = ""
                self.query_one("#remove-user-app", Input).value = ""
            else:
                message.update("User instance not found")
                message.add_class("error-message")
                
        except Exception as e:
            message.update(f"Error: {str(e)}")
            message.add_class("error-message")
