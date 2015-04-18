$(document).ready(function () {
    setInterval(function () {
        $.ajax({
            url: "/activity/status"
        }).done(function (response) {
            for (var i = 0; i < response.length; i++) {
                if (response[i].status) {
                    var result_html = '<a href="' + response[i].url + '">' + response[i].name + '</a>';
                    $("#" + response[i].id).html(result_html);
                }
            }
        });
    }, 5000);
});
