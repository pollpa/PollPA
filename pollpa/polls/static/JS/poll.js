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
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.x); })
      .attr("width", x.bandwidth())
      .style("fill", "blue")
      .attr("y", function(d) { return y(d.y); })
      .attr("height", function(d) { return height - y(d.y); });

  var mouse;

  //Labels for mouseover
  // svg.selectAll(".bar").on("mouseover", function(d, i){
  //   if(className == "barchart-grouped"){
  //     if(isPercentageChart) tooltipText = "<h4>" + d.label + ": " + currentThis.dataset.labels.split(",")[d.key] + "</h4><p><strong>" + d.value.toFixed(1) + "%</strong></p>";
  //     else tooltipText = generateTooltip({title: d.label + ": " +  currentThis.dataset.labels.split(",")[d.key], responses: d.value, percentage: d.value / total});
  //   }
  //   else{
  //     if(isPercentageChart) tooltipText = "<h4>" + d.label + "</h4><p><strong>" + d.y.toFixed(1) + "%</strong></p>";
  //     else tooltipText = generateTooltip({title: d.label, responses: d.y, percentage: d.y / total});
  //   }
  //   tooltip.classed("hidden", false).html(tooltipText);
  //
  //   if(className == "barchart-horizontal" || className == "barchart-vertical") d3.select(this).style("fill", d3.rgb(d3.color(accent).brighter(0.5)));
  //
  //   mouse = d3.mouse(currentThis);
  //   tooltip.style("left", mouse[0] - tooltip.node().offsetWidth / 2.0 + "px")
  //     .style("top", mouse[1] - tooltip.node().offsetHeight - 12 + "px");
  // })
  // .on("mousemove", function(d){
  //   mouse = d3.mouse(currentThis);
  //   tooltip.style("left", mouse[0] - tooltip.node().offsetWidth / 2.0 + "px")
  //     .style("top", mouse[1] - tooltip.node().offsetHeight - 12 + "px");
  // })
  // .on("mouseout", function(d){
  //   //if(d3.event.toElement.parentNode.className.indexOf("tooltip") == -1){
  //     tooltip.classed("hidden", true);
  //   //}
  //   d3.select(this).style("fill", accent);
  // });

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
    .attr("y", -1 * margin.left)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text(currentThis.dataset.ylabel);

  svg.append("text")
    .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.top + 20) + ")")
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

drawBarCharts();

var resizeId;
d3.select(window).on('resize', function(){
  resizeId = setTimeout(function(){
    drawBarCharts();
  }, 200);
});
