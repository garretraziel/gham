var renderValues = function (svg, color, values, x_scale, y_scale) {
    if (values.length === 0) {
        // TODO: render no data
        return;
    }

    var max_date = values[values.length - 1].distance;
    var max_count = d3.max(values, function (v) { return v.count; });

    x_scale = x_scale || d3.scale.linear()
        .domain([0, max_date])
        .range([0, svg.attr("width")]);

    y_scale = y_scale || d3.scale.linear()
        .domain([0, max_count])
        .range([0, svg.attr("height")]);

    var lineFunction = d3.svg.line()
        .x(function (d) {
            return x_scale(d.distance);
        })
        .y(function (d) {
            return svg.attr("height") - y_scale(d.count);
        })
        .interpolate("linear");

    svg.append("path")
        .attr("d", lineFunction(values))
        .attr("stroke", color)
        .attr("stroke-width", 2)
        .attr("fill", "none");
};

$.ajax({
    url: window.location.pathname + "/commits"
}).done(function (commits) {
    var svg = d3.select("#commits_graph");
    renderValues(svg, "blue", commits);
});

$.ajax({
    url: window.location.pathname + "/issues"
}).done(function (i) {
    var svg = d3.select("#issues_graph");

    var max_date_i = i.issues[i.issues.length - 1].distance;
    var max_date_ci = i.closed_issues[i.closed_issues.length - 1].distance;
    var max_date_ct = i.closed_time[i.closed_time.length - 1].distance;
    var max_date = Math.max(max_date_i, max_date_ci, max_date_ct);

    var max_count_i = d3.max(i.issues, function (v) { return v.count; });
    var max_count_c = d3.max(i.closed_issues, function (v) { return v.count; });
    var max_count = Math.max(max_count_i, max_count_c);

    var x_scale = d3.scale.linear()
        .domain([0, max_date])
        .range([0, svg.attr("width")]);

    var y_scale = d3.scale.linear()
        .domain([0, max_count])
        .range([0, svg.attr("height")]);

    renderValues(svg, "blue", i.issues, x_scale, y_scale);
    renderValues(svg, "yellow", i.closed_issues, x_scale, y_scale);
    renderValues(svg, "red", i.closed_time, x_scale);

});

$.ajax({
    url: window.location.pathname + "/pulls"
}).done(function (i) {
    var svg = d3.select("#pulls_graph");

    var max_date_i = i.pulls[i.pulls.length - 1].distance;
    var max_date_ci = i.closed_pulls[i.closed_pulls.length - 1].distance;
    var max_date_ct = i.closed_time[i.closed_time.length - 1].distance;
    var max_date = Math.max(max_date_i, max_date_ci, max_date_ct);

    var max_count_i = d3.max(i.pulls, function (v) { return v.count; });
    var max_count_c = d3.max(i.closed_pulls, function (v) { return v.count; });
    var max_count = Math.max(max_count_i, max_count_c);

    var x_scale = d3.scale.linear()
        .domain([0, max_date])
        .range([0, svg.attr("width")]);

    var y_scale = d3.scale.linear()
        .domain([0, max_count])
        .range([0, svg.attr("height")]);

    renderValues(svg, "blue", i.pulls, x_scale, y_scale);
    renderValues(svg, "yellow", i.closed_pulls, x_scale, y_scale);
    renderValues(svg, "red", i.closed_time, x_scale);

});

$.ajax({
    url: window.location.pathname + "/forks"
}).done(function (forks) {
    var svg = d3.select("#forks_graph");
    renderValues(svg, "blue", forks);
});
