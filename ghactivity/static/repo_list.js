$(document).ready(function () {
    setInterval(function () {
        $.ajax({
            url: "/activity/status"
        }).done(function (response) {
            for (var i = 0; i < response.val.length; i++) {
                if (response.val[i]["status"]) {
                    var result_html = '<a href="' + response.val[i]["url"] + '">' + response.val[i]["name"] + '</a>';
                    $("#" + response.val[i]["id"]).html(result_html);
                }
            }
        });
    }, 5000);
});