function circlePackSummary (div_id, json_url, bg_url) {
  var svg = d3.select(div_id),
    margin = 20,
    diameter = +svg.attr("width"),
    g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

  var color = d3.scaleLinear()
    .domain([-1, 5])
    .range(["hsl(206,30%,47%)", "hsl(205,55%,30%)"])
    .interpolate(d3.interpolateHcl);

  var pack = d3.pack()
    .size([diameter - margin, diameter - margin])
    .padding(2);

  d3.json(json_url, function(error, root) {
    if (error) throw error;

    root = d3.hierarchy(root)
        .sum(function(d) { return (d.size / 200) + 5; })
        .sort(function(a, b) { return b.value - a.value; });

    var focus = root,
        nodes = pack(root).descendants(),
        view;

    svg.append("defs")
      .data(nodes)
      .enter()
      .append("pattern")
        .attr("id", function(d) { return "dyn" + d.data.name; })
        .attr("patternUnits", "userSpaceOnUse")
        .attr("x", function (d) { return root.x; })
        .attr("y", function (d) { return root.y; })
        .attr("height", diameter - margin)
        .attr("width", diameter - margin)
        .append("image")
          .attr("id", function(d) { return "dyn" + d.data.name + ".jpg"; })
          .attr("preserveAspectRatio", "xMidYMid")
          .attr ("x", (diameter - margin) * -1)
          .attr ("y", (diameter - margin) * -1)
          .attr ("height", (diameter - margin) * 4)
          .attr ("width", (diameter - margin) * 4)
          .attr("xlink:href", function(d) {
            var base_url = "http://astrocloud-dev.wr.usgs.gov/dataset/examples/d3/chooserimages/";
            if (d.data.name == 'Planetary Nomenlature') return base_url + "MOON.jpg";
            return base_url + d.data.name + ".jpg"; });

    var circle = g.selectAll("circle")
      .data(nodes)
      .enter().append("circle")
        .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
        // .style("fill", function(d) { return d.children ? color(d.depth) : '#' + d.data.name; })
        .attr("fill", function(d) { return "url(#dyn" + d.data.name + ")"; })
        .on("click", function(d) { if (focus !== d) zoom(d), d3.event.stopPropagation(); });


    //Create a wrapper for everything inside a leaf circle
    // var barWrapperOuter = g.append("g")
    //       .attr("id", function(d) {
    //         if (d.ID != undefined) return d.ID;
    //         else return "node";
    //        })
    //       .style("opacity", 0)
    //       .attr("class", "barWrapperOuter");

    var text = g.selectAll("text")
      .data(nodes)
      .enter()
        .append("text")
        .attr("class", "label")
        .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
        .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
        .text(function(d) { return d.data.name; });

    var text = g.selectAll("circle")
      .data(nodes)
      .enter()
      .append("svg:foreignObject")
        .attr("width", diameter - margin)
        .attr("height", diameter - margin);

    var node = svg.selectAll("circle,text");

    svg
        .style("background-image", "url('" + bg_url + "')")
        .on("click", function() { zoom(root); });

    zoomTo([root.x, root.y, root.r * 2 + margin]);

    function zoom(d) {
      var focus0 = focus; focus = d;

      d3.select("#target_details")
        .style("display", "none")
        .html("");

      var transition = d3.transition()
          .duration(d3.event.altKey ? 7500 : 750)
          .tween("zoom", function(d) {
            var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
            return function(t) { zoomTo(i(t)); };
          });

      transition.selectAll("text")
        .filter(function(d) { return d.parent === focus || this.style.display === "inline"; })
          .style("fill-opacity", function(d) { return d.parent === focus ? 1 : 0; })
          .on("start", function(d) { if (d.parent === focus) this.style.display = "inline"; })
          .on("end", function(d) { if (d.parent !== focus) this.style.display = "none"; });

      d3.select("#target_details")
        .style("display", "none")
        .style("left", (root.x - 7*margin) + "px")
        .style("top", (root.y - 6*margin) + "px")
        .html(insetText(d.data));

      $('#target_details').show(1000);
    }

    function zoomTo(v) {
      var k = diameter / v[2]; view = v;
      node.attr("transform", function(d) {
        d3.select("#dyn" + d.data.name + ".jpg")
          .attr ("x", d.x - v[0] * k)
          .attr ("y", d.x - v[0] * k)
          .attr ("height", d.r * k)
          .attr ("width", d.r * k);
        return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
      circle.attr("r", function(d) { return d.r * k; });
    }

    function insetText(d) {
      var content = '';

      var loopuntil = 0;
      if (d.features) loopuntil = d.features.length;
      else return content;

      var paddingFactor = (1 / loopuntil) * 100;

      var content = "<div class='title-container' style='padding-top:" + paddingFactor + "px;' >";
      content += "<div><p style='padding-left:40px; padding-right:10px;'>" + d.name + "</p></div>";
      content += "<div>";
      content += "<img src='chooserimages/" + d.name + ".png' title='" + d.name + "' height='80px'/>";
      content += "</div></div>";
      content += "<div class='featuretypes-container'>";
      content += "<ul class='featuretypes-list'>";
      for (var i=0; i < loopuntil; i++) {
        item = d.features[i];
        content += "<li><a href='" + item.url + "'>" + item.name + "</a> (" + item.size + ")</li>";
      }

      content += "</ul></div>";

      console.log(content);

      return content;
    }
  });
}
