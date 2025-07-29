// ~ enhanced-widgets.js | by ANXETY ~

// This script handles the client-side logic for the enhanced widget UI,
// primarily the tab switching functionality.

function setupEnhancedWidgets() {
    // Find all tab buttons and tab panels
    const tabButtons = document.querySelectorAll('.p-TabBar-tab');
    const tabPanels = document.querySelectorAll('.p-TabPanel > .widget-vbox');

    if (tabButtons.length === 0 || tabPanels.length === 0) {
        // Fallback or log error if tabs aren't found
        // This can happen if the ipywidgets structure changes
        return;
    }

    // Hide all tab panels initially
    tabPanels.forEach(panel => {
        panel.style.display = 'none';
    });

    // Show the first tab panel by default
    if (tabPanels.length > 0) {
        tabPanels[0].style.display = 'block';
    }
    
    // Add click event listeners to tab buttons
    tabButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            // Hide all panels
            tabPanels.forEach(panel => {
                panel.style.display = 'none';
            });

            // Deactivate all buttons
            tabButtons.forEach(btn => {
                btn.classList.remove('p-mod-current');
            });

            // Show the clicked panel
            if (tabPanels[index]) {
                tabPanels[index].style.display = 'block';
            }

            // Activate the clicked button
            button.classList.add('p-mod-current');
        });
    });
}

// The ipywidgets library renders elements dynamically, so we need to
// wait for them to be available in the DOM. A simple timeout is often
// the most reliable way to do this in a Colab/Jupyter environment.
setTimeout(setupEnhancedWidgets, 500);
