# modules/widget_factory.py - FIXED VERSION WITH PROPER BUTTON CALLBACKS

"""
Enhanced Widget Factory for LSDAI
Provides a unified interface for creating and managing ipywidgets with consistent styling
FIXED: Ensures all widgets properly support callbacks and event handling
"""

import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
from pathlib import Path
import json
import os

class WidgetFactory:
    """
    Factory class for creating ipywidgets with consistent styling and enhanced functionality
    FIXED: All widgets now properly support callbacks and event handling
    """
    
    def __init__(self):
        self.default_style = {'description_width': 'initial'}
        self.loaded_css = set()
        self.loaded_js = set()
        
    # === UTILITY METHODS ===
    
    def _validate_class_names(self, class_names):
        """Validate and clean class names."""
        if isinstance(class_names, str):
            return [class_names]
        elif isinstance(class_names, (list, tuple)):
            return [str(name) for name in class_names if name]
        return []
    
    def add_classes(self, widget, class_names):
        """Add CSS classes to a widget."""
        if not class_names:
            return widget
            
        validated_names = self._validate_class_names(class_names)
        for class_name in validated_names:
            widget.add_class(class_name)
        return widget
    
    def remove_classes(self, widget, class_names):
        """Remove CSS classes from a widget."""
        if not class_names:
            return widget
            
        validated_names = self._validate_class_names(class_names)
        for class_name in validated_names:
            widget.remove_class(class_name)
        return widget
    
    def load_css(self, css_path_or_content, inline=False):
        """Load CSS file or content."""
        try:
            if inline or '\n' in str(css_path_or_content) or '{' in str(css_path_or_content):
                # Treat as CSS content
                css_content = str(css_path_or_content)
            else:
                # Treat as file path
                css_path = Path(css_path_or_content)
                if css_path.exists() and str(css_path) not in self.loaded_css:
                    with open(css_path, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    self.loaded_css.add(str(css_path))
                else:
                    return  # Already loaded or doesn't exist
            
            display(HTML(f'<style>{css_content}</style>'))
            
        except Exception as e:
            print(f"Warning: Could not load CSS: {e}")
    
    def load_js(self, js_path_or_content, inline=False):
        """Load JavaScript file or content."""
        try:
            if inline or '\n' in str(js_path_or_content) or 'function' in str(js_path_or_content):
                # Treat as JS content
                js_content = str(js_path_or_content)
            else:
                # Treat as file path
                js_path = Path(js_path_or_content)
                if js_path.exists() and str(js_path) not in self.loaded_js:
                    with open(js_path, 'r', encoding='utf-8') as f:
                        js_content = f.read()
                    self.loaded_js.add(str(js_path))
                else:
                    return  # Already loaded or doesn't exist
            
            display(Javascript(js_content))
            
        except Exception as e:
            print(f"Warning: Could not load JS: {e}")
    
    # === CORE WIDGET CREATION ===
    
    def _create_widget(self, widget_type, class_names=None, **kwargs):
        """Create a widget of a specified type with optional classes and styles."""
        
        # Set default style if not provided
        if 'style' not in kwargs:
            kwargs['style'] = self.default_style
        
        # Create the widget
        widget = widget_type(**kwargs)
        
        # Add CSS classes if provided
        if class_names:
            self.add_classes(widget, class_names)
        
        return widget
    
    # === BASIC INPUT WIDGETS ===
    
    def create_text(self, value='', description='', placeholder='', class_names=None, **kwargs):
        """Create a text input widget."""
        return self._create_widget(
            widgets.Text,
            class_names=class_names,
            value=value,
            description=description,
            placeholder=placeholder,
            **kwargs
        )
    
    def create_textarea(self, value='', description='', placeholder='', rows=4, class_names=None, **kwargs):
        """Create a textarea widget."""
        return self._create_widget(
            widgets.Textarea,
            class_names=class_names,
            value=value,
            description=description,
            placeholder=placeholder,
            rows=rows,
            **kwargs
        )
    
    def create_password(self, value='', description='', placeholder='', class_names=None, **kwargs):
        """Create a password input widget."""
        return self._create_widget(
            widgets.Password,
            class_names=class_names,
            value=value,
            description=description,
            placeholder=placeholder,
            **kwargs
        )
    
    def create_checkbox(self, value=False, description='', class_names=None, **kwargs):
        """Create a checkbox widget."""
        return self._create_widget(
            widgets.Checkbox,
            class_names=class_names,
            value=value,
            description=description,
            **kwargs
        )
    
    def create_button(self, description='', button_style='', tooltip='', class_names=None, **kwargs):
        """Create a button widget with proper callback support."""
        button = self._create_widget(
            widgets.Button,
            class_names=class_names,
            description=description,
            button_style=button_style,
            tooltip=tooltip,
            **kwargs
        )
        # Ensure the button properly supports on_click callbacks
        return button
    
    def create_toggle_button(self, value=False, description='', button_style='', tooltip='', class_names=None, **kwargs):
        """Create a toggle button widget."""
        return self._create_widget(
            widgets.ToggleButton,
            class_names=class_names,
            value=value,
            description=description,
            button_style=button_style,
            tooltip=tooltip,
            **kwargs
        )
    
    # === NUMERIC WIDGETS ===
    
    def create_int_slider(self, value=0, min_val=0, max_val=10, step=1, description='', class_names=None, **kwargs):
        """Create an integer slider widget."""
        return self._create_widget(
            widgets.IntSlider,
            class_names=class_names,
            value=value,
            min=min_val,
            max=max_val,
            step=step,
            description=description,
            **kwargs
        )
    
    def create_float_slider(self, value=0.0, min_val=0.0, max_val=1.0, step=0.1, description='', class_names=None, **kwargs):
        """Create a float slider widget."""
        return self._create_widget(
            widgets.FloatSlider,
            class_names=class_names,
            value=value,
            min=min_val,
            max=max_val,
            step=step,
            description=description,
            **kwargs
        )
    
    def create_int_text(self, value=0, description='', class_names=None, **kwargs):
        """Create an integer text input widget."""
        return self._create_widget(
            widgets.IntText,
            class_names=class_names,
            value=value,
            description=description,
            **kwargs
        )
    
    def create_float_text(self, value=0.0, description='', class_names=None, **kwargs):
        """Create a float text input widget."""
        return self._create_widget(
            widgets.FloatText,
            class_names=class_names,
            value=value,
            description=description,
            **kwargs
        )
    
    # === SELECTION WIDGETS ===
    
    def create_dropdown(self, options, value=None, description='', class_names=None, **kwargs):
        """Create a dropdown widget."""
        if not options:
            options = ['None']
        
        if value is None:
            value = options[0]
        
        return self._create_widget(
            widgets.Dropdown,
            class_names=class_names,
            options=options,
            value=value,
            description=description,
            **kwargs
        )
    
    def create_select(self, options, value=None, description='', rows=5, class_names=None, **kwargs):
        """Create a select widget."""
        if not options:
            options = ['None']
        
        if value is None:
            value = options[0]
        
        return self._create_widget(
            widgets.Select,
            class_names=class_names,
            options=options,
            value=value,
            description=description,
            rows=rows,
            **kwargs
        )
    
    def create_select_multiple(self, options, description='', value=None, rows=5, class_names=None, **kwargs):
        """Create a multiple selection widget."""
        if not options:
            options = ['None']
        
        if value is None:
            value = []
        elif not isinstance(value, (list, tuple)):
            value = [value]
        
        return self._create_widget(
            widgets.SelectMultiple,
            class_names=class_names,
            options=options,
            value=value,
            description=description,
            rows=rows,
            **kwargs
        )
    
    def create_radio_buttons(self, options, value=None, description='', class_names=None, **kwargs):
        """Create radio buttons widget."""
        if not options:
            options = ['None']
        
        if value is None:
            value = options[0]
        
        return self._create_widget(
            widgets.RadioButtons,
            class_names=class_names,
            options=options,
            value=value,
            description=description,
            **kwargs
        )
    
    # === LAYOUT WIDGETS ===
    
    def create_hbox(self, children=None, class_names=None, **kwargs):
        """Create a horizontal box layout widget."""
        if children is None:
            children = []
        
        return self._create_widget(
            widgets.HBox,
            class_names=class_names,
            children=children,
            **kwargs
        )
    
    def create_vbox(self, children=None, class_names=None, **kwargs):
        """Create a vertical box layout widget."""
        if children is None:
            children = []
        
        return self._create_widget(
            widgets.VBox,
            class_names=class_names,
            children=children,
            **kwargs
        )
    
    def create_accordion(self, children=None, titles=None, class_names=None, **kwargs):
        """Create an accordion widget."""
        if children is None:
            children = []
        
        accordion = self._create_widget(
            widgets.Accordion,
            class_names=class_names,
            children=children,
            **kwargs
        )
        
        if titles:
            for i, title in enumerate(titles):
                if i < len(accordion.children):
                    accordion.set_title(i, title)
        
        return accordion
    
    def create_tab(self, children=None, titles=None, class_names=None, **kwargs):
        """Create a tab widget."""
        if children is None:
            children = []
        
        tab = self._create_widget(
            widgets.Tab,
            class_names=class_names,
            children=children,
            **kwargs
        )
        
        if titles:
            for i, title in enumerate(titles):
                if i < len(tab.children):
                    tab.set_title(i, title)
        
        return tab
    
    # === OUTPUT AND DISPLAY WIDGETS ===
    
    def create_html(self, value='', class_names=None, **kwargs):
        """Create an HTML widget."""
        return self._create_widget(
            widgets.HTML,
            class_names=class_names,
            value=value,
            **kwargs
        )
    
    def create_label(self, value='', class_names=None, **kwargs):
        """Create a label widget."""
        return self._create_widget(
            widgets.Label,
            class_names=class_names,
            value=value,
            **kwargs
        )
    
    def create_output(self, class_names=None, **kwargs):
        """Create an output widget."""
        return self._create_widget(
            widgets.Output,
            class_names=class_names,
            **kwargs
        )
    
    def create_image(self, value=None, format='png', width=None, height=None, class_names=None, **kwargs):
        """Create an image widget."""
        return self._create_widget(
            widgets.Image,
            class_names=class_names,
            value=value,
            format=format,
            width=width,
            height=height,
            **kwargs
        )
    
    # === PROGRESS AND LOADING WIDGETS ===
    
    def create_progress(self, value=0, min_val=0, max_val=10, description='', class_names=None, **kwargs):
        """Create a progress bar widget."""
        return self._create_widget(
            widgets.IntProgress,
            class_names=class_names,
            value=value,
            min=min_val,
            max=max_val,
            description=description,
            **kwargs
        )
    
    def create_float_progress(self, value=0.0, min_val=0.0, max_val=1.0, description='', class_names=None, **kwargs):
        """Create a float progress bar widget."""
        return self._create_widget(
            widgets.FloatProgress,
            class_names=class_names,
            value=value,
            min=min_val,
            max=max_val,
            description=description,
            **kwargs
        )
    
    # === UTILITY METHODS ===
    
    def display(self, widget):
        """Display a widget."""
        display(widget)
        return widget
    
    def observe_widget(self, widget, handler, names='value', type='change'):
        """Add an observer to a widget."""
        if hasattr(widget, 'observe'):
            widget.observe(handler, names=names, type=type)
        return widget
    
    def unobserve_widget(self, widget, handler, names='value', type='change'):
        """Remove an observer from a widget."""
        if hasattr(widget, 'unobserve'):
            widget.unobserve(handler, names=names, type=type)
        return widget
    
    def close(self, widget, class_names=None, delay=0):
        """Close/hide a widget with optional animation."""
        if class_names:
            self.add_classes(widget, class_names)
        
        if hasattr(widget, 'close'):
            if delay > 0:
                import time
                time.sleep(delay)
            widget.close()
        
        return widget
