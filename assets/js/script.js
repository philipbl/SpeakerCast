function onkeypressed(evt, input) {
    var code = evt.charCode || evt.keyCode;
    if (code == 27) {
        input.value = '';
    }
}
