/**
 * Created by nolan on 2017/8/24.
 */

$(".comment").click(function (){
    var a_id = $(this).parents("div.list-group-item").attr("id");
    var url = "/comment/" + a_id;
    window.location.href = url;
});


$("#comment-submit").click(function () {
    var uploadFormData = new FormData($('#CommentForm')[0]);
    var a_id = $(".list-group-item").attr("id");
    $.ajax({
        cache: true,
        type: "POST",
        url: "/comment/" + a_id,
        data: uploadFormData,
        async: true,
        contentType: false,
        processData:false,
        error: function(res) {
            alert(res['msg']);
        },
        success: function(res) {
            if(!res['success']){
                alert(res['msg']);
            }else{
                window.location.href = "/detail/" + a_id;
            }
        }
    });
});


$(".like").click(function () {
    var like_icon = $(this);
    var a_id = $(this).parents("div.list-group-item").attr("id");
    var url = "/like/" + a_id;
    var like_cout = $(this).text();
    var new_count = like_cout*1 + 1;
    $.ajax({
        cache: true,
        type: "GET",
        url: url,
        async: true,
        contentType: false,
        processData:false,
        error: function(res) {
            alert(res['msg']);
        },
        success: function(res) {
            if(!res['success']){
                alert(res['msg']);
            }else{
                like_icon.text(new_count);
            }
        }
    });
});


$(".c-like").click(function () {
    var clike_icon = $(this);
    var c_id = $(this).parents("div.list-group-item").attr("id");
    var url = "/comment/like/" + c_id;
    var like_cout = $(this).text();
    var new_count = like_cout*1 + 1;
    $.ajax({
        cache: true,
        type: "GET",
        url: url,
        async: true,
        contentType: false,
        processData:false,
        error: function(res) {
            alert(res['msg']);
        },
        success: function(res) {
            if(!res['success']){
                alert(res['msg']);
            }else{
                clike_icon.text(new_count);
            }
        }
    });
});