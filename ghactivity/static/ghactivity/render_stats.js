var renderSingleValues = function (svg, values, color) {
    "use strict";

    var padding = 30;
    var width = svg.attr("width");
    var height = svg.attr("height");

    if (values.length === 0) {
        svg.append("text")
            .attr("x", svg.attr("width") / 2)
            .attr("y", svg.attr("height") / 2)
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
            var date = new Date(firstDate.getTime() + d*24*60*60*1000);
            return (date.getMonth() + 1) + " " + date.getFullYear();
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

    svg.append("path")
        .attr("d", lineFunction(values))
        .attr("stroke", color)
        .attr("stroke-width", 2)
        .attr("fill", "none");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + (height - padding) + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + padding + ",0)")
        .call(yAxis);
};

var renderThreeValues = function (svg, values_a, color_a, values_b, color_b, values_c, color_c) {
    "use strict";

    if (values_a.length === 0 && values_b.length === 0 && values_c.length === 0) {
        svg.append("text")
            .attr("x", svg.attr("width") / 2)
            .attr("y", svg.attr("height") / 2)
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
    var padding = 30;
    var width = svg.attr("width");
    var height = svg.attr("height");

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
            var date = new Date(firstDate.getTime() + d*24*60*60*1000);
            return (date.getMonth() + 1) + " " + date.getFullYear();
        });

    var yAxisL = d3.svg.axis()
        .scale(yScaleC)
        .orient("left")
        .ticks(5);

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

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + (height - padding) + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + padding + ",0)")
        .call(yAxisL);

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + (width - padding) + ",0)")
        .call(yAxisR);
};

$.ajax({
    url: window.location.pathname + "/commits"
}).done(function (commits) {
    "use strict";
    var svg = d3.select("#commits_graph");
    renderSingleValues(svg, commits, "blue");
});

$.ajax({
    url: window.location.pathname + "/issues"
}).done(function (response) {
    "use strict";
    var svg = d3.select("#issues_graph");
    renderThreeValues(svg, response.issues, "red", response.closed_issues, "green", response.closed_time, "blue");
});

$.ajax({
    url: window.location.pathname + "/pulls"
}).done(function (response) {
    "use strict";
    var svg = d3.select("#pulls_graph");
    renderThreeValues(svg, response.pulls, "red", response.closed_pulls, "green", response.closed_time, "blue");
});

$.ajax({
    url: window.location.pathname + "/forks"
}).done(function (forks) {
    "use strict";
    var svg = d3.select("#forks_graph");
    renderSingleValues(svg, forks, "blue");
});
