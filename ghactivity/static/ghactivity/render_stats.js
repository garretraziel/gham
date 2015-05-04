var width = 800;
var height = 400;
var aspect = height / width;
var legend_x = 70;
var legend2_x = width - 250;

var renderSingleValues = function (svg, values, name, color, scaling_id) {
    "use strict";

    var padding = 40;
    var real_width = $(scaling_id).width();
    svg.attr("preserveAspectRatio", "xMidYMid")
        .attr("viewBox", "0 0 800 400")
        .attr("width", real_width)
        .attr("height", real_width * aspect);

    if (values.length === 0) {
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("font-family", "sans-serif")
            .attr("font-size", "20px")
            .attr("fill", color)
            .attr("text-anchor", "middle")
            .text("NO DATA");
        return;
    }

    var maxDate = values[values.length - 1].distance;
    var maxCount = d3.max(values, function (v) {
        return v.count;
    });

    var firstDate = new Date(values[0].date);

    var xScale = d3.scale.linear()
        .domain([0, maxDate])
        .range([padding, width - padding]);

    var yScale = d3.scale.linear()
        .domain([0, maxCount])
        .range([height - padding, padding]);

    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .ticks(6)
        .tickFormat(function (d) {
            var date = new Date(firstDate.getTime() + d * 24 * 60 * 60 * 1000);
            if ((Date.now() - firstDate.getTime()) / 1000 / 60 / 60 / 24 / 365 > 1) {
                return (date.getMonth() + 1) + " " + date.getFullYear();
            } else {
                return date.getDate() + " " + (date.getMonth() + 1) + " " + date.getFullYear();
            }
        });

    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left")
        .ticks(5);

    var lineFunction = d3.svg.line()
        .x(function (d) {
            return xScale(d.distance);
        })
        .y(function (d) {
            return yScale(d.count);
        })
        .interpolate("linear");

    var legendFunction = d3.svg.line()
        .x(function (d) {
            return d.x;
        })
        .y(function (d) {
            return d.y;
        })
        .interpolate("linear");

    svg.append("path")
        .attr("d", lineFunction(values))
        .attr("stroke", color)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("path")
        .attr("d", legendFunction([{x: legend_x, y: 10}, {x: legend_x + 100, y: 10}]))
        .attr("stroke", color)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("text")
        .attr("x", legend_x + 110)
        .attr("y", 15)
        .attr("font-family", "sans-serif")
        .attr("font-size", "15px")
        .attr("fill", "black")
        .text(name);

    svg.append("g")
        .attr("class", "axis")
        .attr("stroke-width", 2)
        .attr("transform", "translate(0," + (height - padding) + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "axis")
        .attr("stroke-width", 2)
        .attr("transform", "translate(" + padding + ",0)")
        .call(yAxis);
};

var renderThreeValues = function (svg, scaling_id, values_a, color_a, name_a, values_b, color_b, name_b, values_c, color_c, name_c) {
    "use strict";

    var real_width = $(scaling_id).width();
    svg.attr("preserveAspectRatio", "xMidYMid")
        .attr("viewBox", "0 0 800 400")
        .attr("width", real_width)
        .attr("height", real_width * aspect);

    if (values_a.length === 0 && values_b.length === 0 && values_c.length === 0) {
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("font-family", "sans-serif")
            .attr("font-size", "20px")
            .attr("fill", color_a)
            .attr("text-anchor", "middle")
            .text("NO DATA");
        return;
    }

    var maxDateI = 0,
        maxDateCi = 0,
        maxDateCt = 0;
    var padding = 40;

    if (values_a.length !== 0) {
        maxDateI = values_a[values_a.length - 1].distance;
    }
    if (values_b.length !== 0) {
        maxDateCi = values_b[values_b.length - 1].distance;
    }
    if (values_c.length !== 0) {
        maxDateCt = values_c[values_c.length - 1].distance;
    }
    var maxDate = Math.max(maxDateI, maxDateCi, maxDateCt);

    var maxCountI = d3.max(values_a, function (v) {
        return v.count;
    });
    var maxCountC = d3.max(values_b, function (v) {
        return v.count;
    });
    var maxCount = Math.max(maxCountI, maxCountC);

    var maxTime = d3.max(values_c, function (v) {
        return v.count;
    });

    var firstDate = new Date(values_a[0].date);

    var xScale = d3.scale.linear()
        .domain([0, maxDate])
        .range([padding, width - padding]);

    var yScaleC = d3.scale.linear()
        .domain([0, maxCount])
        .range([height - padding, padding]);

    var yScaleT = d3.scale.linear()
        .domain([0, maxTime])
        .range([height - padding, padding]);

    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .ticks(6)
        .tickFormat(function (d) {
            var date = new Date(firstDate.getTime() + d * 24 * 60 * 60 * 1000);
            if ((Date.now() - firstDate.getTime()) / 1000 / 60 / 60 / 24 / 365 > 1) {
                return (date.getMonth() + 1) + " " + date.getFullYear();
            } else {
                return date.getDate() + " " + (date.getMonth() + 1) + " " + date.getFullYear();
            }
        });

    var yAxisL = d3.svg.axis()
        .scale(yScaleC)
        .orient("left")
        .ticks(5)
        .tickSize(12);

    var yAxisR = d3.svg.axis()
        .scale(yScaleT)
        .orient("right")
        .ticks(5);

    var lineFunction1 = d3.svg.line()
        .x(function (d) {
            return xScale(d.distance);
        })
        .y(function (d) {
            return yScaleC(d.count);
        })
        .interpolate("linear");

    var lineFunction2 = d3.svg.line()
        .x(function (d) {
            return xScale(d.distance);
        })
        .y(function (d) {
            return yScaleT(d.count);
        })
        .interpolate("linear");

    var legendFunction = d3.svg.line()
        .x(function (d) {
            return d.x;
        })
        .y(function (d) {
            return d.y;
        })
        .interpolate("linear");

    svg.append("path")
        .attr("d", lineFunction1(values_a))
        .attr("stroke", color_a)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("path")
        .attr("d", lineFunction1(values_b))
        .attr("stroke", color_b)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("path")
        .attr("d", lineFunction2(values_c))
        .attr("stroke", color_c)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("path")
        .attr("d", legendFunction([{x: legend_x, y: 10}, {x: legend_x + 100, y: 10}]))
        .attr("stroke", color_a)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("text")
        .attr("x", legend_x + 110)
        .attr("y", 15)
        .attr("font-family", "sans-serif")
        .attr("font-size", "15px")
        .attr("fill", "black")
        .text(name_a);

    svg.append("path")
        .attr("d", legendFunction([{x: legend_x, y: 30}, {x: legend_x + 100, y: 30}]))
        .attr("stroke", color_b)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("text")
        .attr("x", legend_x + 110)
        .attr("y", 35)
        .attr("font-family", "sans-serif")
        .attr("font-size", "15px")
        .attr("fill", "black")
        .text(name_b);

    svg.append("path")
        .attr("d", legendFunction([{x: legend2_x, y: 10}, {x: legend2_x + 100, y: 10}]))
        .attr("stroke", color_c)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("text")
        .attr("x", legend2_x + 110)
        .attr("y", 15)
        .attr("font-family", "sans-serif")
        .attr("font-size", "15px")
        .attr("fill", "black")
        .text(name_c);

    svg.append("g")
        .attr("class", "axis")
        .attr("stroke-width", 2)
        .attr("transform", "translate(0," + (height - padding) + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "axis")
        .attr("stroke-width", 2)
        .attr("transform", "translate(" + padding + ",0)")
        .call(yAxisL);

    svg.append("g")
        .attr("class", "axis")
        .attr("stroke-width", 2)
        .attr("transform", "translate(" + (width - padding) + ",0)")
        .call(yAxisR);
};

$.ajax({
    url: window.location.pathname + "/commits"
}).done(function (response) {
    "use strict";
    $("#commits_footer").append("Total commits count: " + response.count);
    var svg = d3.select("#commits_graph");
    renderSingleValues(svg, response.commits, "commits", "blue", "#cgraph");
});

$.ajax({
    url: window.location.pathname + "/issues"
}).done(function (response) {
    "use strict";
    $("#issues_footer").append("Total issues count: " + response.issues_count + ", closed issues count: " + response.closed_count);
    var svg = d3.select("#issues_graph");
    renderThreeValues(svg, "#igraph", response.issues, "blue", "issues", response.closed_issues, "green", "closed issues", response.closed_time, "red", "avg close time");
});

$.ajax({
    url: window.location.pathname + "/pulls"
}).done(function (response) {
    "use strict";
    $("#pulls_footer").append("Total pull requests count: " + response.pulls_count + ", closed pull requests count: " + response.closed_count);
    var svg = d3.select("#pulls_graph");
    renderThreeValues(svg, "#pgraph", response.pulls, "blue", "pull requests", response.closed_pulls, "green", "closed pull requests", response.closed_time, "red", "avg close time");
});

$.ajax({
    url: window.location.pathname + "/forks"
}).done(function (response) {
    "use strict";
    $("#forks_footer").append("Total forks count: " + response.count);
    var svg = d3.select("#forks_graph");
    renderSingleValues(svg, response.forks, "forks", "blue", "#fgraph");
});

$(document).ready(function () {
    "use strict";
    $(window).resize(function () {
        var real_width = $("#cgraph").width();
        var svg = d3.select("#commits_graph");
        svg.attr("width", real_width);
        svg.attr("height", real_width * aspect);
        real_width = $("#fgraph").width();
        svg = d3.select("#forks_graph");
        svg.attr("width", real_width);
        svg.attr("height", real_width * aspect);
        real_width = $("#igraph").width();
        svg = d3.select("#issues_graph");
        svg.attr("width", real_width);
        svg.attr("height", real_width * aspect);
        real_width = $("#pgraph").width();
        svg = d3.select("#pulls_graph");
        svg.attr("width", real_width);
        svg.attr("height", real_width * aspect);
    });
});
