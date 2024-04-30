// 引入d3.js库
<script src="https://d3js.org/d3.v7.min.js"></script>

// 创建SVG容器
var svg = d3.select("body")
  .append("svg")
  .attr("width", 800)
  .attr("height", 400);

// 定义甘特图的数据
var tasks = [
  { start: new Date("2022-01-01"), end: new Date("2022-01-05") },
  { start: new Date("2022-01-06"), end: new Date("2022-01-10") },
  { start: new Date("2022-01-11"), end: new Date("2022-01-15") }
];

// 计算甘特图的布局
var xScale = d3.scaleTime()
  .domain([new Date("2022-01-01"), new Date("2022-01-15")])
  .range([0, 800]);

// 绘制甘特图的轴线
var xAxis = d3.axisBottom(xScale);
svg.append("g")
  .attr("transform", "translate(0, 50)")
  .call(xAxis);

// 绘制甘特图的任务条
var taskRects = svg.selectAll("rect")
  .data(tasks)
  .enter()
  .append("rect")
  .attr("x", function(d) { return xScale(d.start); })
  .attr("y", 100)
  .attr("width", function(d) { return xScale(d.end) - xScale(d.start); })
  .attr("height", 20)
  .attr("fill", "steelblue");

// 绘制顶部的多条线
var topLines = svg.selectAll("line")
  .data(tasks)
  .enter()
  .append("line")
  .attr("x1", function(d) { return xScale(d.start); })
  .attr("y1", 80)
  .attr("x2", function(d) { return xScale(d.end); })
  .attr("y2", 80)
  .attr("stroke", "red")
  .attr("stroke-width", 2);