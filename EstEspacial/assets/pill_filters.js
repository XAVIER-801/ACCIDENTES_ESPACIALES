(function() {
    /* ═══════════════════════════════════════════════
       PILL-BAR FILTER LOGIC (CLEANED)
       Manages panel open/close, search input filtering
       and click listeners. Checklist state and chip rendering
       are handled exclusively by Dash/React to prevent
       DOM conflicts and Virtual DOM crashes.
       ═══════════════════════════════════════════════ */

    var FILTERS = ['depts', 'years', 'vias', 'clases'];

    function getPillBar(fid)   { return document.getElementById('pill-bar-' + fid); }
    function getPillPanel(fid) { return document.getElementById('pill-panel-' + fid); }
    function getOptsList(fid)  { return document.getElementById('pill-opts-' + fid); }

    /* Open a panel using fixed positioning so it overlays everything */
    function openPanel(fid) {
        var bar   = getPillBar(fid);
        var panel = getPillPanel(fid);
        var rect  = bar.getBoundingClientRect();

        panel.style.position = 'fixed';
        panel.style.top      = (rect.bottom + 6) + 'px';
        panel.style.left     = rect.left + 'px';
        panel.style.zIndex   = '9999999';
        panel.style.display  = 'block';
        bar.classList.add('open');
    }

    /* Close all panels and reset their positioning */
    function closeAllPanels() {
        FILTERS.forEach(function(f) {
            var p = getPillPanel(f);
            var b = getPillBar(f);
            if (p) {
                p.style.display  = 'none';
                p.style.position = 'absolute';  /* restore CSS default */
                p.style.top      = '';
                p.style.left     = '';
                p.style.zIndex   = '';
            }
            if (b) {
                b.classList.remove('open');
            }
        });
    }

    /* Toggle open/close of a panel */
    function togglePanel(fid) {
        var panel  = getPillPanel(fid);
        if (!panel) return;
        var isOpen = panel.style.display !== 'none';
        closeAllPanels();
        if (!isOpen) {
            openPanel(fid);
        }
    }

    /* Close all panels when clicking outside */
    document.addEventListener('click', function(e) {
        // If clicking a search input, don't close the panel
        if (e.target && e.target.classList.contains('pill-search')) {
            return;
        }
        // If the target element is detached from the DOM (e.g. re-rendered by React/Dash),
        // we should not close the panels.
        if (e.target && !document.body.contains(e.target)) {
            return;
        }
        var inBar   = e.target.closest('.pill-filter-bar');
        var inPanel = e.target.closest('.pill-panel');
        if (!inBar && !inPanel) {
            closeAllPanels();
        }
    });

    /* Initialize after DOM is ready */
    function initPillFilters() {
        FILTERS.forEach(function(fid) {
            var bar   = getPillBar(fid);
            var panel = getPillPanel(fid);
            if (!bar || !panel) return;

            /* Click on bar toggles panel */
            bar.addEventListener('click', function(e) {
                if (e.target.classList.contains('pill-clear-btn')) return;
                togglePanel(fid);
            });
        });
    }

    /* Search is handled by Dash clientside_callbacks — no JS needed here */

    /* Close panels on scroll ONLY when the scroll happens OUTSIDE an open panel's options list.
       scroll events do NOT bubble, so we use capture:true. We skip closure when the
       scrolled element is the .pill-options-list (the scrollable div inside the panel). */
    window.addEventListener('scroll', function(e) {
        var t = e.target;
        // If scrolling inside the options list of an open dropdown — keep the panel open
        if (t && t.classList && t.classList.contains('pill-options-list')) {
            return;
        }
        // Also keep open if scroll target is a child inside the options list
        if (t && t.closest && t.closest('.pill-options-list')) {
            return;
        }
        closeAllPanels();
    }, true);  /* capture:true required because scroll events don't bubble */

    /* Wait for Dash to finish rendering */
    var _initAttempts = 0;
    function tryInit() {
        var ready = FILTERS.every(function(fid) { return !!getPillBar(fid); });
        if (ready) {
            initPillFilters();
        } else if (_initAttempts < 30) {
            _initAttempts++;
            setTimeout(tryInit, 300);
        }
    }
    tryInit();

})();
