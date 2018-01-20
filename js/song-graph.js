var makeGraph = function(graphName) {
  d3.csv("data/"+graphName+"-graph-data.csv", function(error, data) {
    // console.log(data);

    var n = data.length, // number of layers
        m = Object.keys(data[0]).length-2; // number of samples per layer

    var backgroundColor = window.getComputedStyle(
                  document.getElementsByTagName("body")[0]).backgroundColor;

    var stack = d3.stack().keys(d3.range(n)).order(d3.stackOrderInsideOut).offset(d3.stackOffsetWiggle),
        layers = stack(d3.transpose(d3.range(n).map(function(i) {
          // console.log(data);
          a = [];
          // console.log(i);
          // console.log(data[i])
          for (var j = 0; j < m; j++) {
            a.push(data[i]["x"+j]);
          }
          return a;
        })));

    var svg = d3.select("#"+graphName+"-graph-svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    var x = d3.scaleLinear()
        .domain([0, m])
        .range([0, width]);

    var y = d3.scaleLinear()
        .domain([d3.min(layers, stackMin), d3.max(layers, stackMax)])
        .range([height, 0]);

    var z = d3.interpolateCool;

    var area = d3.area()
        .x(function(d, i) { return x(i); })
        .y0(function(d) { return y(d[0]); })
        .y1(function(d) { return y(d[1]); });

    var infoName = "", infoCount = 0;

    svg.selectAll("path")
      .data(layers)
      .enter().append("path")
        .attr("d", area)
        .attr("fill", (d,i) => z((i/5.0) % 1.0))
        .attr("stroke", backgroundColor)
        .attr("stroke-width", height*0.005)
        .on("mouseover", (d,i) => {
          infoName = data[i].name;
          infoCount = data[i].count;
        })
        .on("mouseout", (d,i) => {
          if (infoName == data[i].name) {
            infoName = ""
            infoCount = 0
          }
        });
        // .append("title")
        //   .text((d,i) => data[i].name+" ["+data[i].count+" listens]");

    function stackMax(layer) {
      return d3.max(layer, function(d) { return d[1]; });
    }

    function stackMin(layer) {
      return d3.min(layer, function(d) { return d[0]; });
    }

    svg_dom = document.querySelector("#"+graphName+"-graph-svg");
    svg_dom.addEventListener('mousemove', evt => {
      var pt = svg_dom.createSVGPoint();
      pt.x = evt.clientX;
      pt.y = evt.clientY;
      var loc = pt.matrixTransform(svg_dom.getScreenCTM().inverse());

      nDays = (loc.x * m / width).toFixed(0);
      infoDaysAgo = m - nDays;
      dateObj = new Date();
      dateObj.setDate(dateObj.getDate() - infoDaysAgo);
      p = document.getElementById(""+graphName+"-graph-info")
      p.textContent = "date: " + dateObj.toDateString().slice(4);
      p.textContent += "  |  "+graphName+": " + infoName;
      p.textContent += "  |  listen count: " + infoCount;
    });

  });
}

makeGraph("song");
makeGraph("artist");
