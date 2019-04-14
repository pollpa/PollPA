var blue = "#003c7f";
var lighterBlue = d3.color(blue).brighter(0.5).hex();

/*
  Bar Chart
*/

function drawBarChart(currentThis, data){
  var margin = {top: 20, right: 20, bottom: 50, left: 60},
      height = 300 - margin.top - margin.bottom,
      width = d3.select("#questions").node().offsetWidth - margin.left - margin.right;

  // Clear existing elements in graph
  d3.select(currentThis).select('svg').selectAll("*").remove();
  d3.select(currentThis).select('.bar-label').remove();

  // Create SVG
  svg = d3.select(currentThis).select("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Set Domain & Range
  x = d3.scaleBand().range([0, width]).paddingInner(0.2);
  y = d3.scaleLinear().range([height, 0]);

  x.domain(data.map(function(d) { return d.x; }));
  y.domain([0, d3.max(data, function(d) { return d.y; })]);

  // Add Bars
  svg.selectAll(".bar")
      .data(data)
    .enter().append("rect")
      .style("fill", blue)
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.x); })
      .attr("width", x.bandwidth())
      .attr("y", function(d) { return y(d.y); })
      .attr("height", function(d) { return height - y(d.y); });

  // Tooltip
  var mouse,
      tooltip = d3.select(currentThis).select(".tooltip");

  svg.selectAll(".bar").on("mousemove", function(d){
    d3.select(this).style("fill", lighterBlue);
    mouse = d3.mouse(currentThis);

    tooltipText = "<strong>" + d.x + "</strong><br>" + currentThis.dataset.ylabel + ": " + d.y;
    tooltip.html(tooltipText)
      .classed("is-hidden", false)
      .style("left", mouse[0] - tooltip.node().offsetWidth / 2.0 + "px")
      .style("top", mouse[1] - tooltip.node().offsetHeight - 12 + "px");
  })
  .on("mouseout", function(d){
    d3.select(this).style("fill", blue);
    tooltip.classed("is-hidden", true);
  });

  // Add X Axis
  svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x));

  // Add Y Axis
  svg.append("g")
    .call(d3.axisLeft(y).ticks(5));

  //Labels
  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("class", "label")
    .attr("y", -1 * margin.left)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text(currentThis.dataset.ylabel);

  svg.append("text")
    .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.top + 20) + ")")
    .attr("class", "label")
    .style("text-anchor", "middle")
    .text(currentThis.dataset.xlabel);
}

function drawBarCharts(){
  d3.selectAll(".bar-chart").each(function(d, i){
    var data = JSON.parse(this.dataset.values.replace(/'/g, "\""));
    data.forEach(function(d){
      return +d.y;
    });
    drawBarChart(this, data);
  });
}

/*
  Pie Chart
*/

function drawPieChart(currentThis, data){
  var margin = {top: 20, right: 20, bottom: 50, left: 60},
      radius = 150,
      height = radius * 2,
      width = radius * 2;

  var colors = d3.scaleLinear().domain([0, data.length - 1, data.length])
    .interpolate(d3.interpolateHcl)
    .range(["white", blue, "#112030"]);

  var pie = d3.pie()
    .value(function(d){
      return d.y;
    }).sort(null);

  var arc = d3.arc()
    .outerRadius(radius)
    .innerRadius(radius / 1.7);

  var mouse,
      tooltip = d3.select(currentThis).select(".tooltip"),
      tooltipText;

  var total = 0;
  data.forEach(function(d){
    total += d.y;
  });

  var pieChart = d3.select(currentThis).select("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
      .attr("transform", "translate(" + (width - radius) + "," + (height - radius) + ")")
      .selectAll("path").data(pie(data))
      .enter().append("path")
        .attr("fill", function(d, i){
          return colors(i + 1);
        })
        .attr("stroke", "white")
        .attr("d", arc)
        .on("mouseover", function(d, i){
          d3.select(this).attr("fill", d3.color(colors(i + 1)).brighter(0.5).hex());

          tooltipText = "<strong>" + d.data.x + "</strong><br>" + (100 * d.data.y / total).toFixed(2) + "% (" + d.data.y + ")";
          tooltip.html(tooltipText);
        })
        .on("mousemove", function(d){
          mouse = d3.mouse(currentThis);

          tooltip.classed("is-hidden", false)
            .style("left", mouse[0] - Math.round(tooltip.node().offsetWidth / 2) + "px")
            .style("top", mouse[1] - Math.round(tooltip.node().offsetHeight) - 12 + "px");
        })
        .on("mouseout", function(d, i){
          d3.select(this).attr("fill", colors(i + 1));
          tooltip.classed("is-hidden", true);
        });

  //Add labels underneath pie chart
  d3.select(currentThis).select(".pie-label").append("p")
    .attr("class", "is-size-7 has-text-gray is-italic")
    .style("margin-bottom", "10px")
    .html("Select any section of the chart for more information.<br>");

  var pieLabel = d3.select(currentThis).select(".pie-label").selectAll("span")
    .data(data)
    .enter().append("span")
      .html(function(d, i){
        return "<div class = 'bubble' style = 'background:" + colors(i + 1) + "'></div>" + d.x;
      }).append("br");
}

function drawPieCharts(){
  d3.selectAll(".pie-chart").each(function(d, i){
    var data = JSON.parse(this.dataset.values.replace(/'/g, "\""));
    data.forEach(function(d){
      return +d.y;
    });
    drawPieChart(this, data);
  });
}

/*
  Binary Slider
*/

function drawBinarySlider(currentThis, data){
  var slider = d3.select(currentThis);
  var total = data[0].y + data[1].y,
      yes = 100 * data[0].y / total,
      no = 100 * data[1].y / total;

  slider.select(".yes-half")
    .style("width", Math.floor(yes) + "%")
    .html("<p class = 'heading is-size-6'>YES</p><p class = 'is-size-5'>" + yes.toFixed(2) + "%</p>");

  slider.select(".no-half")
    .style("width", Math.floor(no) + "%")
    .html("<p class = 'heading is-size-6'>NO</p><p class = 'is-size-5'>" + no.toFixed(2) + "%</p>");
}

function drawBinarySliders(){
  d3.selectAll(".binary-slider").each(function(d, i){
    var data = JSON.parse(this.dataset.values.replace(/'/g, "\""));
    data.forEach(function(d){
      return +d.y;
    });

    drawBinarySlider(this, data);
  });
}

/*
  INITIALIZE
*/

drawBarCharts();
drawPieCharts();
drawBinarySliders();

/*
  RESIZE
*/

var resizeId;
d3.select(window).on('resize', function(){
  resizeId = setTimeout(function(){
    drawBarCharts();
  }, 200);
});
