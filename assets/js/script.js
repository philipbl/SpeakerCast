function onkeypressed(evt, input) {
    var code = evt.charCode || evt.keyCode;
    if (code == 27) {
        input.value = '';
    }
}

function set_affix() {
    var top;
    var bottom;

    if ($(window).width() > 768) {
        top = $("#feed-section").offset().top - 10;
    }
    else {
        top = $("#intro-section").offset().top + $("#intro-section").outerHeight() - 20;
    }

    bottom = $('.footer-section').outerHeight(true) + 40;
    console.log(bottom);

    // Unset affix
    $(window).off('.affix')
    $('#selected-panel').removeData('bs.affix').removeClass('affix affix-top affix-bottom')

    // Re-set affix
    $('#selected-panel').affix({
        offset: {
            top: top,
            bottom: bottom
        }
    });
}

set_affix();
$(window).resize(function() {
    set_affix();
});
