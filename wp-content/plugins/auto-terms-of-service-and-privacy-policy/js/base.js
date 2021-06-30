(function () {
    var handlers = [];
    var ran = false;

    function runHandlers() {
        if (ran) {
            return;
        }
        ran = true;
        for (var k in handlers) {
            handlers[k](jQuery);
        }
    }

    wp.domReady(runHandlers);

    function wpAutoTermsDomReady(fn) {
        handlers.push(fn);
    }

    window.wpAutoTermsDomReady = wpAutoTermsDomReady;
    window.onerror = runHandlers;
    jQuery.readyException = runHandlers;
})();
