/* ~ enhanced-widgets.css | by ANXETY ~ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

:root {
    --bg-color: linear-gradient(145deg, #330000 0%, #000000 100%);
    --primary-widget-bg: #2a2a2a;
    --secondary-widget-bg: #202020;
    --border-color: #444;
    --trim-color: #FFD700; /* Golden Yellow */
    --text-color: #f0f0f0;
    --text-color-secondary: #aaa;
    --accent-color: #9370DB; /* Medium Purple */
    --accent-hover: #a388ee;
    --container-shadow: 0 4px 12px rgba(0,0,0,0.4);
    --font-family: 'Inter', sans-serif;
}

/* --- Main Container --- */
.main-ui-container {
    font-family: var(--font-family);
    background: var(--bg-color);
    padding: 16px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    box-shadow: var(--container-shadow);
    color: var(--text-color);
}

/* --- Golden Trim --- */
.trimmed-box {
    border: 2px solid var(--trim-color);
    box-shadow: 0 0 8px -2px var(--trim-color);
}

/* --- Header Controls --- */
.header-controls {
    padding: 10px;
    background-color: var(--secondary-widget-bg);
    border-radius: 8px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between; /* Changed for new layout */
    flex-wrap: wrap;
    gap: 10px;
}
.header-controls .widget-dropdown,
.header-controls .widget-checkbox,
.header-controls .jupyter-button {
    margin: 0;
}
.header-controls .widget-checkbox label {
    font-size: 13px;
}
.header-left-group, .header-right-group {
    display: flex;
    gap: 15px;
    align-items: center;
}
.header-center-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
}
.header-center-group .widget-dropdown {
    min-width: 200px;
}

/* --- Tab Widget Styling --- */
.p-TabBar .p-TabBar-tab {
    background: var(--secondary-widget-bg);
    color: var(--text-color-secondary);
    border: 1px solid var(--border-color);
    border-bottom: none;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
}
.p-TabBar .p-TabBar-tab.p-mod-current {
    background: var(--primary-widget-bg);
    color: var(--text-color);
    border-color: var(--trim-color);
    border-bottom: 1px solid var(--primary-widget-bg);
    transform: translateY(2px);
}
.p-TabPanel {
    background: var(--primary-widget-bg);
    border: 1px solid var(--border-color);
    border-top: none;
    padding: 16px;
    border-radius: 0 0 8px 8px;
}

/* --- Checkbox Selection List --- */
.checkbox-group {
    background-color: var(--secondary-widget-bg);
    border-radius: 8px;
    padding: 10px;
    height: 300px; /* Increased height */
    overflow-y: auto;
    border: 1px solid var(--border-color);
}
.checkbox-group .widget-checkbox {
    padding: 4px 8px;
    border-radius: 4px;
    transition: background-color 0.2s ease;
}
.checkbox-group .widget-checkbox:hover {
    background-color: rgba(255, 255, 255, 0.05);
}
.checkbox-group .widget-checkbox label {
    font-size: 13px;
    white-space: normal; /* Allow text wrapping */
    overflow: visible;
    text-overflow: clip;
    max-width: 100%;
    display: block; /* Ensure label takes full width */
}

/* --- Accordion Styling --- */
.p-Accordion .p-Accordion-header {
    background: var(--secondary-widget-bg);
    color: var(--text-color);
    border: 1px solid var(--border-color);
    margin-top: 10px;
    padding: 10px;
    font-weight: 500;
}
.p-Accordion .p-Accordion-header.p-mod-selected {
    background: var(--accent-color);
}
.p-Accordion .p-Accordion-child {
    padding: 16px;
    background: var(--primary-widget-bg);
    border: 1px solid var(--border-color);
    border-top: none;
}

/* --- General Widget Styling --- */
.widget-text input, .widget-dropdown select, .widget-textarea textarea, .jupyter-button {
    background-color: var(--secondary-widget-bg);
    color: var(--text-color);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 8px;
}
.widget-text input:focus, .widget-dropdown select:focus, .widget-textarea textarea:focus {
    border-color: var(--accent-color);
    outline: none;
}
.widget-label {
    font-size: 13px;
    color: var(--text-color-secondary);
}
.jupyter-button {
    font-size: 12px;
}

/* --- Save Button --- */
.button_save {
    width: 100%;
    margin-top: 16px;
    background-color: var(--accent-color);
    color: white;
    font-weight: 600;
    transition: background-color 0.2s ease;
}
.button_save:hover {
    background-color: var(--accent-hover);
}

/* --- Hide Animation --- */
.main-ui-container.hide {
    transition: opacity 0.5s, transform 0.5s;
    opacity: 0;
    transform: scale(0.95);
}
