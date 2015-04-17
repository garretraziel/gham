var w = 400;
var h = 200;

var renderValues = function (svg, color, values, x_scale, y_scale) {
    if (values.length == 0) {
        return;
    }

    var max_date = values[values.length - 1].distance;
    var max_count = 0;
    for (var i = 0; i < values.length; i++) {
        if (values[i].count > max_count) {
            max_count = values[i].count;
        }
    }
    x_scale = x_scale || d3.scale.linear()
        .domain([0, max_date])
        .range([0, w]);

    y_scale = y_scale || d3.scale.linear()
        .domain([0, max_count])
        .range([0, h]);

    svg.attr("width", w).attr("height", h);
    var lineFunction = d3.svg.line()
        .x(function (d) {
            return x_scale(d.distance);
        })
        .y(function (d) {
            return h - y_scale(d.count);
        })
        .interpolate("linear");

    svg.append("path")
        .attr("d", lineFunction(values))
        .attr("stroke", color)
        .attr("stroke-width", 2)
        .attr("fill", "none");
};

var svg = d3.select("body").append("svg");
renderValues(svg, "blue", commits);

var max_date_i = issues[issues.length - 1].distance;
var max_date_ci = closedissues[closedissues.length - 1].distance;
var max_date_ct = closedissuestime[closedissuestime.length - 1].distance;
var max_date = Math.max(max_date_i, max_date_ci, max_date_ct);

var max_count = 0;
for (var i = 0; i < issues.length; i++) {
    if (issues[i].count > max_count) {
        max_count = issues[i].count;
    }
}
for (i = 0; i < closedissues.length; i++) {
    if (closedissues[i].count > max_count) {
        max_count = closedissues[i].count;
    }
}
var x_scale = d3.scale.linear()
    .domain([0, max_date])
    .range([0, w]);

var y_scale = d3.scale.linear()
    .domain([0, max_count])
    .range([0, h]);

svg = d3.select("body").append("svg");
renderValues(svg, "blue", issues, x_scale, y_scale);
renderValues(svg, "yellow", closedissues, x_scale, y_scale);
renderValues(svg, "red", closedissuestime, x_scale);

max_date_i = pulls[pulls.length - 1].distance;
max_date_ci = closedpulls[closedpulls.length - 1].distance;
max_date_ct = closedpullstime[closedpullstime.length - 1].distance;
max_date = Math.max(max_date_i, max_date_ci, max_date_ct);

max_count = 0;
for (i = 0; i < pulls.length; i++) {
    if (pulls[i].count > max_count) {
        max_count = pulls[i].count;
    }
}
for (i = 0; i < closedpulls.length; i++) {
    if (closedpulls[i].count > max_count) {
        max_count = closedpulls[i].count;
    }
}
x_scale = d3.scale.linear()
    .domain([0, max_date])
    .range([0, w]);

y_scale = d3.scale.linear()
    .domain([0, max_count])
    .range([0, h]);

svg = d3.select("body").append("svg");
renderValues(svg, "blue", pulls, x_scale, y_scale);
renderValues(svg, "yellow", closedpulls, x_scale, y_scale);
renderValues(svg, "red", closedpullstime, x_scale);

svg = d3.select("body").append("svg");
renderValues(svg, "blue", forks);