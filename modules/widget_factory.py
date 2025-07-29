"""
Widget Factory Module | by ANXETY
Provides standardized widget creation with consistent styling and functionality
"""

from IPython.display import display, HTML
import ipywidgets as widgets
from pathlib import Path
import time

class WidgetFactory:
    """Factory class for creating standardized widgets with consistent styling"""
    
    def __init__(self):
        self.default_style = {'description_width': 'initial'}
        self.default_layout = widgets.Layout()

    def _validate_class_names(self, class_names):
        """Validate and normalize class names."""
        if class_names is None:
            return []

        if isinstance(class_names, str):
            return [class_names.strip()]

        if isinstance(class_names, list):
            return [cls.strip() for cls in class_names if cls.strip()]

        print(f"Warning: Invalid class_names type: {type(class_names).__name__}")
        return []

    def add_classes(self, widget, class_names):
        """Add CSS classes to a widget."""
        classes = self._validate_class_names(class_names)
        for cls in classes:
            widget.add_class(cls)

    # === HTML AND STYLING ===
    
    def load_css(self, css_path):
        """Load CSS from a file and display it in the notebook."""
        try:
            css_path = Path(css_path)
            if css_path.exists():
                with open(css_path, 'r') as file:
                    data = file.read()
                    display(HTML(f"<style>{data}</style>"))
            else:
                print(f"Warning: CSS file not found: {css_path}")
        except Exception as e:
            print(f"Error loading CSS: {e}")

    def load_js(self, js_path):
        """Load JavaScript from a file and display it in the notebook."""
        try:
            js_path = Path(js_path)
            if js_path.exists():
                with open(js_path, 'r') as file:
                    data = file.read()
                    display(HTML(f"<script>{data}</script>"))
            else:
                print(f"Warning: JavaScript file not found: {js_path}")
        except Exception as e:
            print(f"Error loading JavaScript: {e}")

    def create_html(self, content, class_names=None):
        """Create an HTML widget with optional CSS classes."""
        html_widget = widgets.HTML(content)
        if class_names:
            self.add_classes(html_widget, class_names)
        return html_widget

    def create_header(self, name, class_names=None):
        """Create a header HTML widget."""
        if class_names is None:
            class_names = ['header']
        
        class_names_str = ' '.join(self._validate_class_names(class_names))
        header_html = f'<div class="{class_names_str}">{name}</div>'
        return self.create_html(header_html)

    # === BASIC WIDGETS ===
    
    def _apply_layouts(self, children, layouts):
        """Apply layouts to children widgets."""
        n_layouts = len(layouts)

        if n_layouts == 1:
            # Apply the single layout to all children
            for child in children:
                child.layout = layouts[0]
        else:
            for child, layout in zip(children, layouts):
                child.layout = layout

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
        """Create a button widget."""
        return self._create_widget(
            widgets.Button,
            class_names=class_names,
            description=description,
            button_style=button_style,
            tooltip=tooltip,
            **kwargs
        )

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

    def create_dropdown_multiple(self, options, value=None, description='', class_names=None, **kwargs):
        """Create a multiple selection dropdown widget."""
        if not options:
            options = ['None']
        
        if value is None:
            value = [options[0]]
        elif not isinstance(value, (list, tuple)):
            value = [value]
        
        return self._create_widget(
            widgets.SelectMultiple,
            class_names=class_names,
            options=options,
            value=value,
            description=description,
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

    def create_toggle_buttons(self, options, value=None, description='', class_names=None, **kwargs):
        """Create toggle buttons widget."""
        if not options:
            options = ['None']
        
        return self._create_widget(
            widgets.ToggleButtons,
            class_names=class_names,
            options=options,
            value=value,
            description=description,
            **kwargs
        )

    # === CONTAINER WIDGETS ===

    def create_hbox(self, children=None, class_names=None, layouts=None, **kwargs):
        """Create a horizontal box container."""
        if children is None:
            children = []
        
        if layouts:
            self._apply_layouts(children, layouts)
        
        return self._create_widget(
            widgets.HBox,
            class_names=class_names,
            children=children,
            **kwargs
        )

    def create_vbox(self, children=None, class_names=None, layouts=None, **kwargs):
        """Create a vertical box container."""
        if children is None:
            children = []
        
        if layouts:
            self._apply_layouts(children, layouts)
        
        return self._create_widget(
            widgets.VBox,
            class_names=class_names,
            children=children,
            **kwargs
        )

    def create_grid(self, children=None, n_rows=None, n_columns=None, class_names=None, **kwargs):
        """Create a grid container."""
        if children is None:
            children = []
        
        return self._create_widget(
            widgets.GridBox,
            class_names=class_names,
            children=children,
            **kwargs
        )

    def create_accordion(self, children=None, titles=None, class_names=None, **kwargs):
        """Create an accordion container."""
        if children is None:
            children = []
        
        accordion = self._create_widget(
            widgets.Accordion,
            class_names=class_names,
            children=children,
            **kwargs
        )
        
        if titles and len(titles) == len(children):
            for i, title in enumerate(titles):
                accordion.set_title(i, title)
        
        return accordion

    def create_tab(self, children=None, titles=None, class_names=None, **kwargs):
        """Create a tab container."""
        if children is None:
            children = []
        
        tab = self._create_widget(
            widgets.Tab,
            class_names=class_names,
            children=children,
            **kwargs
        )
        
        if titles and len(titles) == len(children):
            for i, title in enumerate(titles):
                tab.set_title(i, title)
        
        return tab

    # === PROGRESS AND OUTPUT ===

    def create_progress_bar(self, value=0, min_val=0, max_val=100, description='', class_names=None, **kwargs):
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

    def create_output(self, class_names=None, **kwargs):
        """Create an output widget."""
        return self._create_widget(
            widgets.Output,
            class_names=class_names,
            **kwargs
        )

    # === LAYOUT UTILITIES ===

    def create_layout(self, width=None, height=None, margin=None, padding=None, **kwargs):
        """Create a layout object with specified properties."""
        layout_kwargs = {}
        
        if width:
            layout_kwargs['width'] = width
        if height:
            layout_kwargs['height'] = height
        if margin:
            layout_kwargs['margin'] = margin
        if padding:
            layout_kwargs['padding'] = padding
        
        layout_kwargs.update(kwargs)
        
        return widgets.Layout(**layout_kwargs)

    def create_style(self, **kwargs):
        """Create a style object with specified properties."""
        return kwargs

    # === SPECIALIZED WIDGETS ===

    def create_file_upload(self, accept='', multiple=False, description='Upload', class_names=None, **kwargs):
        """Create a file upload widget."""
        return self._create_widget(
            widgets.FileUpload,
            class_names=class_names,
            accept=accept,
            multiple=multiple,
            description=description,
            **kwargs
        )

    def create_color_picker(self, value='#000000', description='Color', class_names=None, **kwargs):
        """Create a color picker widget."""
        return self._create_widget(
            widgets.ColorPicker,
            class_names=class_names,
            value=value,
            description=description,
            **kwargs
        )

    def create_date_picker(self, value=None, description='Date', class_names=None, **kwargs):
        """Create a date picker widget."""
        return self._create_widget(
            widgets.DatePicker,
            class_names=class_names,
            value=value,
            description=description,
            **kwargs
        )

    # === INTERACTIVE WIDGETS ===

    def create_interactive_widget(self, func, **kwargs):
        """Create an interactive widget using ipywidgets.interact."""
        return widgets.interact(func, **kwargs)

    def create_interactive_output(self, func, controls, class_names=None):
        """Create an interactive output widget."""
        output_widget = widgets.interactive_output(func, controls)
        if class_names:
            self.add_classes(output_widget, class_names)
        return output_widget

    # === NOTIFICATION AND ALERT WIDGETS ===

    def create_alert(self, message, alert_type='info', class_names=None):
        """Create an alert/notification widget."""
        
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        colors = {
            'info': '#d1ecf1',
            'success': '#d4edda',
            'warning': '#fff3cd',
            'error': '#f8d7da'
        }
        
        icon = icons.get(alert_type, 'ℹ️')
        color = colors.get(alert_type, '#d1ecf1')
        
        alert_html = f"""
        <div style="
            background-color: {color};
            border: 1px solid #bee5eb;
            border-radius: 0.25rem;
            padding: 0.75rem 1.25rem;
            margin: 0.5rem 0;
            color: #0c5460;
        ">
            <span style="margin-right: 0.5rem;">{icon}</span>
            {message}
        </div>
        """
        
        return self.create_html(alert_html, class_names)

    def create_loading_indicator(self, message='Loading...', class_names=None):
        """Create a loading indicator widget."""
        
        loading_html = f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 1rem;
            font-family: monospace;
        ">
            <div style="
                border: 2px solid #f3f3f3;
                border-top: 2px solid #3498db;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            "></div>
            {message}
        </div>
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        """
        
        return self.create_html(loading_html, class_names)

    # === UTILITY FUNCTIONS ===

    def link_widgets(self, source_widget, target_widget, source_trait='value', target_trait='value'):
        """Link two widgets so changes in one affect the other."""
        return widgets.link((source_widget, source_trait), (target_widget, target_trait))

    def observe_widget(self, widget, callback, trait='value'):
        """Observe a widget for changes."""
        widget.observe(callback, names=trait)

    def display_widgets(self, *widget_list):
        """Display multiple widgets."""
        for widget in widget_list:
            display(widget)

    def clear_output(self, output_widget):
        """Clear the content of an output widget."""
        if hasattr(output_widget, 'clear_output'):
            output_widget.clear_output()

    def capture_output(self, output_widget):
        """Return a context manager for capturing output to an output widget."""
        return output_widget

    # === LAYOUT HELPERS ===

    def create_form_layout(self, field_configs, submit_callback=None, class_names=None):
        """Create a form layout with multiple fields and optional submit button."""
        
        form_widgets = {}
        form_elements = []
        
        for config in field_configs:
            field_type = config.get('type', 'text')
            field_name = config.get('name', f'field_{len(form_widgets)}')
            field_label = config.get('label', field_name.replace('_', ' ').title())
            field_value = config.get('value', '')
            field_options = config.get('options', [])
            
            if field_type == 'text':
                widget = self.create_text(value=field_value, description=field_label)
            elif field_type == 'textarea':
                widget = self.create_textarea(value=field_value, description=field_label)
            elif field_type == 'password':
                widget = self.create_password(value=field_value, description=field_label)
            elif field_type == 'checkbox':
                widget = self.create_checkbox(value=bool(field_value), description=field_label)
            elif field_type == 'dropdown':
                widget = self.create_dropdown(options=field_options, value=field_value, description=field_label)
            elif field_type == 'slider':
                min_val = config.get('min', 0)
                max_val = config.get('max', 100)
                widget = self.create_int_slider(value=field_value, min_val=min_val, max_val=max_val, description=field_label)
            else:
                widget = self.create_text(value=field_value, description=field_label)
            
            form_widgets[field_name] = widget
            form_elements.append(widget)
        
        if submit_callback:
            submit_button = self.create_button('Submit', button_style='success')
            
            def on_submit(button):
                form_data = {name: widget.value for name, widget in form_widgets.items()}
                submit_callback(form_data)
            
            submit_button.on_click(on_submit)
            form_elements.append(submit_button)
        
        form_container = self.create_vbox(form_elements, class_names=class_names)
        
        return form_container, form_widgets

# Export the main class
__all__ = ['WidgetFactory']
