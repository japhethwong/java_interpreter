

$(document).ready(function() {

    $('#add-method-btn').click(add_method);
    $('#compile-btn').click(compile);
});

method_panel = '<div class="method-panel">public void <input type="text" name="method-name" size=10 value="example">() {<br/><textarea class="method" rows=5 cols=64>// TODO your code here</textarea><br/>}</div>'

function add_method(){
    $('.method-panel').last().after(method_panel);
}


function compile(){
    $.ajax({
        type: 'POST',
        url: 'runprogram.py',
        dataType: 'html'
    }).done(function(msg) {
        alert(msg);
    });
}

