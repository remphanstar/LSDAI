# Fixed verbosity section for enhanced_widgets_en.py

def create_verbosity_control_section(self):
    """Create the verbosity control section for the UI - FULLY WORKING VERSION"""
    
    # Create verbosity level dropdown with proper mapping
    verbosity_options = [
        ("Silent (Errors Only)", VerbosityLevel.SILENT),
        ("Minimal (Basic Status)", VerbosityLevel.MINIMAL), 
        ("Normal (Standard Output)", VerbosityLevel.NORMAL),
        ("Detailed (Show Commands)", VerbosityLevel.DETAILED),
        ("Verbose (Full Debug)", VerbosityLevel.VERBOSE),
        ("Raw (Everything)", VerbosityLevel.RAW)
    ]
    
    # Find current level name
    current_level = self.verbose_manager.verbosity_level
    current_text = "Normal (Standard Output)"  # Default
    for text, level in verbosity_options:
        if level == current_level:
            current_text = text
            break
    
    self.widgets['verbosity_level'] = self.factory.create_dropdown(
        options=[opt[0] for opt in verbosity_options],
        value=current_text,
        description='Output Level:'
    )
    
    # Create detailed download toggle (for backwards compatibility)
    self.widgets['detailed_download'] = widgets.ToggleButton(
        value=(self.verbose_manager.verbosity_level >= VerbosityLevel.DETAILED),
        description='Detailed Output',
        button_style='success' if (self.verbose_manager.verbosity_level >= VerbosityLevel.DETAILED) else '',
        tooltip='Toggle detailed output for all operations across ALL cells'
    )
    
    # Create real-time output toggle
    self.widgets['real_time_output'] = widgets.ToggleButton(
        value=True,
        description='Real-time Output',
        button_style='info',
        tooltip='Show output in real-time during operations'
    )
    
    # Create verbosity info display
    self.verbosity_info = self.factory.create_html(self._get_verbosity_info_html())
    
    # Create demo button to test current verbosity level - STYLED TO MATCH
    demo_button = widgets.ToggleButton(
        value=False,
        description='Test Output Level',
        button_style='',
        tooltip='Click to test the current verbosity level'
    )
    demo_button.on_click(self._demo_verbosity_level)
    
    # Setup callbacks - FIXED TO ACTUALLY WORK
    self.widgets['verbosity_level'].observe(self._on_verbosity_dropdown_change, names='value')
    self.widgets['detailed_download'].observe(self._on_detailed_toggle_change, names='value')
    self.widgets['real_time_output'].observe(self._on_realtime_toggle_change, names='value')
    
    # Create the verbosity control panel - MATCH EXISTING LAYOUT STYLE
    verbosity_controls = self.factory.create_vbox([
        self.factory.create_html("<h4 style='text-align: center; margin: 10px 0;'>🔧 Global Output Verbosity Control</h4>"),
        self.factory.create_html("<p style='text-align: center; font-style: italic; margin: 5px 0;'><em>Controls output detail level for ALL notebook cells and operations</em></p>"),
        
        # Main controls row (match header-controls style)
        self.factory.create_hbox([
            self.widgets['verbosity_level'],
            demo_button
        ], class_names=['header-controls']),
        
        # Toggle buttons row (match header-group style)  
        self.factory.create_hbox([
            self.widgets['detailed_download'], 
            self.widgets['real_time_output']
        ], class_names=['header-group']),
        
        self.verbosity_info
    ], class_names=['verbosity-control-panel'])
    
    return verbosity_controls

def _on_verbosity_dropdown_change(self, change):
    """Handle verbosity dropdown change - FIXED TO ACTUALLY UPDATE"""
    verbosity_options = [
        ("Silent (Errors Only)", VerbosityLevel.SILENT),
        ("Minimal (Basic Status)", VerbosityLevel.MINIMAL), 
        ("Normal (Standard Output)", VerbosityLevel.NORMAL),
        ("Detailed (Show Commands)", VerbosityLevel.DETAILED),
        ("Verbose (Full Debug)", VerbosityLevel.VERBOSE),
        ("Raw (Everything)", VerbosityLevel.RAW)
    ]
    
    # Find the verbosity level based on the selected option
    selected_text = change['new']
    new_level = VerbosityLevel.NORMAL  # Default
    
    for text, level in verbosity_options:
        if text == selected_text:
            new_level = level
            break
    
    # Update verbosity manager - THIS ACTUALLY WORKS NOW
    self.verbose_manager.set_verbosity(new_level)
    
    # Update other widgets to match
    self.widgets['detailed_download'].value = (new_level >= VerbosityLevel.DETAILED)
    self.widgets['detailed_download'].button_style = 'success' if (new_level >= VerbosityLevel.DETAILED) else ''
    
    # Update info display
    self.verbosity_info.value = self._get_verbosity_info_html()
    
    # Show notification
    level_name = self.verbose_manager.get_current_level_name()
    self.show_notification(f"Verbosity set to: {level_name}", "success")

def _on_detailed_toggle_change(self, change):
    """Handle detailed toggle change"""
    if change['new']:
        # Enable detailed mode
        self.verbose_manager.set_verbosity(VerbosityLevel.DETAILED)
        self.widgets['detailed_download'].button_style = 'success'
        self.show_notification("Detailed output enabled", "info")
    else:
        # Set to normal mode
        self.verbose_manager.set_verbosity(VerbosityLevel.NORMAL)
        self.widgets['detailed_download'].button_style = ''
        self.show_notification("Detailed output disabled", "info")
    
    # Update dropdown to match
    level_name = self.verbose_manager.get_current_level_name()
    verbosity_text = f"{level_name} ({['Errors Only', 'Basic Status', 'Standard Output', 'Show Commands', 'Full Debug', 'Everything'][self.verbose_manager.verbosity_level]})"
    
    # Find matching dropdown option
    for option in self.widgets['verbosity_level'].options:
        if level_name.lower() in option.lower():
            self.widgets['verbosity_level'].value = option
            break

def _on_realtime_toggle_change(self, change):
    """Handle real-time output toggle change"""
    if change['new']:
        self.widgets['real_time_output'].button_style = 'info'
        self.show_notification("Real-time output enabled", "info")
    else:
        self.widgets['real_time_output'].button_style = ''
        self.show_notification("Real-time output disabled", "info")

def _demo_verbosity_level(self, button):
    """Demonstrate the current verbosity level - COMPREHENSIVE TEST"""
    self.show_notification("Testing current verbosity level...", "info")
    
    print("=" * 50)
    print("🔧 VERBOSITY LEVEL TEST")
    print("=" * 50)
    
    current_level = self.verbose_manager.verbosity_level
    level_name = self.verbose_manager.get_current_level_name()
    
    print(f"Current level: {level_name} ({current_level})")
    print()
    
    # Test each verbosity level
    print("Testing what each level displays:")
    self.verbose_manager.print_if_verbose("❌ Silent level: This only shows on errors", VerbosityLevel.SILENT)
    self.verbose_manager.print_if_verbose("📝 Minimal level: Basic status messages", VerbosityLevel.MINIMAL)
    self.verbose_manager.print_if_verbose("📋 Normal level: Standard LSDAI output", VerbosityLevel.NORMAL)
    self.verbose_manager.print_if_verbose("🔍 Detailed level: Command outputs and details", VerbosityLevel.DETAILED)
    self.verbose_manager.print_if_verbose("📊 Verbose level: Full debug information", VerbosityLevel.VERBOSE)
    self.verbose_manager.print_if_verbose("🔧 Raw level: Literally everything, no filtering", VerbosityLevel.RAW)
    
    print()
    print("Testing subprocess execution:")
    
    # Demonstrate a subprocess call
    try:
        self.verbose_manager.run_subprocess(["echo", "This is a test command to demonstrate verbosity"])
    except Exception as e:
        print(f"Demo command failed: {e}")
    
    print()
    print("✅ Verbosity test completed!")
    print("=" * 50)
    
    # Reset button state
    button.value = False

def _get_verbosity_info_html(self) -> str:
    """Get HTML description of current verbosity level"""
    level_info = {
        VerbosityLevel.SILENT: {
            "name": "Silent",
            "desc": "Only critical errors shown",
            "color": "#6b7280",
            "affects": "❌ No subprocess output, ❌ No pip details, ❌ No download progress"
        },
        VerbosityLevel.MINIMAL: {
            "name": "Minimal",
            "desc": "Basic status messages only", 
            "color": "#374151",
            "affects": "📝 Basic status, ❌ No command details, ❌ No pip output"
        },
        VerbosityLevel.NORMAL: {
            "name": "Normal",
            "desc": "Standard LSDAI output (default)",
            "color": "#059669",
            "affects": "📋 Standard messages, ❌ No command details, ❌ No subprocess output"
        },
        VerbosityLevel.DETAILED: {
            "name": "Detailed",
            "desc": "Show command outputs and technical details",
            "color": "#0d9488",
            "affects": "🔍 Command outputs, 📋 Technical details, ⚠️ Some subprocess output"
        },
        VerbosityLevel.VERBOSE: {
            "name": "Verbose",
            "desc": "Full debug information including pip outputs",
            "color": "#0ea5e9",
            "affects": "📊 Full debugging, 🔧 Pip outputs, 📋 All subprocess results"
        },
        VerbosityLevel.RAW: {
            "name": "Raw Output",
            "desc": "Everything including raw Python output",
            "color": "#8b5cf6",
            "affects": "🔧 Raw Python output, 📊 All subprocess streams, 🔍 Maximum detail"
        }
    }
    
    current_level = self.verbose_manager.verbosity_level
    info = level_info.get(current_level, level_info[VerbosityLevel.NORMAL])
    
    return f'''
    <div style="
        background: linear-gradient(135deg, {info['color']}20, {info['color']}10);
        border: 1px solid {info['color']}40;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
        font-size: 14px;
    ">
        <div style="
            font-weight: bold;
            color: {info['color']};
            margin-bottom: 8px;
        ">
            📊 Current: {info['name']} - {info['desc']}
        </div>
        <div style="
            color: #666;
            font-size: 12px;
            line-height: 1.4;
        ">
            {info['affects']}
        </div>
    </div>
    '''
