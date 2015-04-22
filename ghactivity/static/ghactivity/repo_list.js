$(document).ready(function () {
    "use strict";
    setInterval(function () {
        $.ajax({
            url: "/activity/status"
        }).done(function (response) {
            for (var i = 0; i < response.length; i++) {
                var element = $("#" + response[i].id);
                if (response[i].status && element.hasClass("disabled")) {
                    var result_html = '<a href="' + response[i].url + '">' + response[i].name + '</a>';
                    element.html(result_html);
                    element.removeClass("disabled");
                } else if (!response[i].status && !element.hasClass("disabled")) {
                    element.html(response[i].name);
                    element.addClass("disabled");
                }
            }
        });
    }, 5000);
});
