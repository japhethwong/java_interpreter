

$(document).ready(function() {

    $('#add-method-btn').click(add_method);
    $('#compile-btn').click(compile);
});

method_panel = '<div class="method-panel">public void <input type="text" name="method-name" size=10 value="example">() {<br/><textarea class="method" rows=5 cols=64>// TODO your code here</textarea><br/>}</div>'

function add_method(){
    $('.method-panel').last().after(method_panel);
}


function compile(){
    var data = $("input[name='class-name']").val();
    var fields = $("textarea.fields").val();
    $.ajax({
        type: 'POST',
        url: '/hello',
        dataType: 'text',
        data: {'class_name': data,
               'fields': fields},
        success: function(msg) {
            alert(msg);
        }
    });
}

