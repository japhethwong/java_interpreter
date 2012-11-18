
var counter = 1;

$(document).ready(function() {

    $('#add-method-btn').click(add_method);
    $('#compile-btn').click(compile);
});

var method_panel1 = '<div class="method-panel">public void <input type="text" name="method-name';
var method_panel2 = '" size=10 value="example">() {<br/><textarea class="method';
var method_panel3 ='" rows=5 cols=64>// TODO your code here</textarea><br/>}</div>';

function add_method(){
    var s = method_panel1 + counter + method_panel2 + counter++ + method_panel3;
    $('.method-panel').last().after(s);
}

function type(){
    var s = $("input[name='interpreter-bar']").val();
    $("#interpreter-history").append(s);
}


function compile(){
    var data = $("input[name='class-name']").val();
    var fields = $("textarea.fields").val();
    var name0 = $("input[name='method-name0']").val();
    var bind0 = $("textarea#method0").val();
    $.ajax({
        type: 'POST',
        url: '/compile',
        dataType: 'text',
        data: {'class_name': data,
               'fields': fields,
               'name0': name0,
               'bind0': bind0,
        },
        success: function(msg) {
            alert(msg);
        }
    });
}

