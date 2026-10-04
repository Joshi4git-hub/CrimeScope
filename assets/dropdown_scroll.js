// Intercepts Radix UI dropdown auto-scrolling to force options menu to scroll to top (1st option) first
(function() {
    let lastOpenTime = 0;

    function resetContainers() {
        const containers = document.querySelectorAll(
            '.dash-dropdown-content, div[class*="-menu"], div[class*="-MenuList"], [role="listbox"], [data-radix-select-viewport]'
        );
        containers.forEach(function(c) {
            c.scrollTop = 0;
        });
    }

    // Intercept native scroll events on dropdown viewports during the first 600ms of opening
    document.addEventListener('scroll', function(e) {
        if (Date.now() - lastOpenTime < 600) {
            if (e.target && (
                (e.target.classList && e.target.classList.contains('dash-dropdown-content')) ||
                (e.target.matches && e.target.matches('div[class*="-menu"], [role="listbox"], [data-radix-select-viewport]'))
            )) {
                e.target.scrollTop = 0;
            }
        }
    }, true);

    function triggerOpen() {
        lastOpenTime = Date.now();
        resetContainers();
        requestAnimationFrame(resetContainers);
        setTimeout(resetContainers, 10);
        setTimeout(resetContainers, 30);
        setTimeout(resetContainers, 80);
        setTimeout(resetContainers, 150);
        setTimeout(resetContainers, 300);
    }

    document.addEventListener('pointerdown', function(e) {
        if (e.target.closest('.dash-dropdown, [class*="dash-dropdown"], [role="combobox"], div[class*="-control"], button.dash-dropdown')) {
            triggerOpen();
        }
    }, true);

    document.addEventListener('click', function(e) {
        if (e.target.closest('.dash-dropdown, [class*="dash-dropdown"], [role="combobox"], div[class*="-control"], button.dash-dropdown')) {
            triggerOpen();
        }
    }, true);

    document.addEventListener('focusin', function(e) {
        if (e.target.closest('.dash-dropdown, [class*="dash-dropdown"], [role="combobox"], div[class*="-control"], button.dash-dropdown')) {
            triggerOpen();
        }
    }, true);
})();
