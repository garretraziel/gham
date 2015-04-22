$(document).ready(function () {
    "use strict";
    setInterval(function () {
        $.ajax({
            url: "/activity/status"
        }).done(function (response) {
            for (var i = 0; i < response.length; i++) {
                var element = $("#" + response[i].id);
                if (response[i].status && element.hasClass("disabled")) {
                    element.removeClass("disabled");
                } else if (!response[i].status && !element.hasClass("disabled")) {
                    element.addClass("disabled");
                }
            }
        });
    }, 5000);
});
