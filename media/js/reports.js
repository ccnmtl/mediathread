//requires Protovis: http://vis.stanford.edu/protovis/

function do_proto(json) {
    var w = jQuery('#reports-graph-link').width(),//document.body.clientWidth,
        h = jQuery(window).height()-300,
        colors = pv.Colors.category10(),
        domain_colors = pv.Colors.category19()


    var vis = new pv.Panel({canvas:'reports-graph-visualization'})
    .canvas('reports-graph-visualization')
    .width(w)
    .height(h)
    .fillStyle("white")
    .event("mousedown", pv.Behavior.pan())
    .event("mousewheel", pv.Behavior.zoom(
        //clearly protovis default is calibrated for firefox
        (/Firefox/.test(navigator.userAgent) ? 1 : 3)
    ));
    
    var force = vis.add(pv.Layout.Force)
    .nodes(json.nodes)
    .links(json.links);

    force.link.add(pv.Line);

    force.node.add(pv.Dot)
    .size(function(d) {return (d.linkDegree + 4) * Math.pow(this.scale, -1.5)})
    .fillStyle(function(d) {
        return d.domain ? domain_colors(d.domain) : colors(d.group);
    })
    .strokeStyle(function() {return this.fillStyle().darker()})
    .lineWidth(1)
    .shape(function(d) {switch (d.group) {
    case 1:
    case 2:return 'circle'
    case 3:return 'square'
    case 4:return 'cross'
    }})
    .title(function(d) {return d.nodeName + (d.domain? ' ('+d.domain+')' : '') })
    .event("mousedown", pv.Behavior.drag())
    .event("drag", force);

    vis.render();
}

var report_done = false;
window['hs_onshow_reports-graph'] = function() {
    if (report_done) return
    report_done = true;
    jQuery.ajax({
        url:'/reports/class_summary/graph.json?nocache='+Number(new Date())+location.search.replace(/^./,'&'),
        dataType:'json',
        success:function(json){
            do_proto(json);
        }
    })
}