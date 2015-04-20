$(document).ready(function () {
    "use strict";
    setInterval(function () {
        $.ajax({
            url: "/activity/status"
        }).done(function (response) {
            for (var i = 0; i < response.length; i++) {
                if (response[i].status) {
                    var result_html = '<a href="' + response[i].url + '">' + response[i].name + '</a>';
                    var element = $("#" + response[i].id);
                    element.html(result_html);
                    element.removeClass("disabled");
                } else {
                    element = $("#" + response[i].id);
                    element.html(response[i].name);
                    element.addClass("disabled");
                }
            }
        });
    }, 5000);
});
