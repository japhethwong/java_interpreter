
var counter = 1;

$(document).ready(function() {
    $('#compile-btn').click(compile);
    $('textarea').keydown(handle_tab);
    $('input[name="interpreter-bar"]').keydown(function(e) {
        if (e.keyCode == 13) {
            interpret();
        }
    });
    var s = $("#interpreter-history").val('Java interpreter\n');

});

function type(){
    var s = $("input[name='interpreter-bar']").val();
    $("#interpreter-history").append(s);
}

function handle_tab(e) {
    var tab = '\t';
    if(e.keyCode == 9) {
        var start = this.selectionStart;
        var end = this.selectionEnd;
        var value = $(this).val();
        $(this).val(value.substring(0, start) + tab + value.substring(end ));
        this.selectionStart = this.selectionEnd = start + 1;
        e.preventDefault();
    }

}

function compile(){
    var data = $("#class-panel").val();
    $.ajax({
        type: 'POST',
        url: '/compile',
        dataType: 'text',
        data: {'data': data },
        success: function(msg) {
            alert(msg);
        }
    });
}

function interpret() {
    var data = $("input[name='interpreter-bar']").val();
    $.ajax({
        type: 'POST',
        url: 'interpret',
        dataType: 'text',
        data: {'data': data },
        success: function(msg) {
            var s = $("#interpreter-history").val();
            $("#interpreter-history").val(s + 'Java> ' + msg + '\n');
        }
    });
}

