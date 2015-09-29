function onkeypressed(evt, input) {
    var code = evt.charCode || evt.keyCode;
    if (code == 27) {
        input.value = '';
    }
}

function set_affix() {
    $('#selected-panel').affix({
        offset: {
        top: 635,
        // bottom: function () {
        //     // console.log($(document).height());
        //   // return (this.bottom = $(document).height());
        //   return 0;
        // }
      }
    });
}
