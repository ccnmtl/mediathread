//requires Protovis: http://vis.stanford.edu/protovis/

var SherdReport = (new (function() {
    var self = this;
    this.started = false;

    this.nodeMouseDown = function(node) {
        jQuery('#reports-graph-chosenlink')
        .html(node.nodeName)
        .attr('href',node.href)

        self.innerMouseDown.apply(this,arguments);
    }

    this.init = function (json) {
        var w = jQuery('#reports-graph-link').width(),//document.body.clientWidth,
            h = jQuery(window).height()-300,
            colors = pv.Colors.category10(),
            domain_colors = pv.Colors.category20()
        

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
        
        self.links = force.link.add(pv.Line)
        .strokeStyle(function(n,lnk){
            var g = (lnk.bare ? .2 : .5 )
            return 'rgba(0,0,0,'+g+')'
        })
        //.lineWidth(function(d){window.sky = Array.prototype.slice.call(arguments);})
        
        self.innerMouseDown = pv.Behavior.drag();

        self.nodes = force.node.add(pv.Dot)
        .size(function(d) {return 3+(d.linkDegree + 4) * Math.pow(this.scale, -1.5)})
        .fillStyle(function(d) {
            var color;
            switch (d.group) {
            case 2: return domain_colors(d.domain);
            case 3: return new pv.Color.Rgb(0,100,256,1) //project
            case 4: return new pv.Color.Rgb(0,100,0,1) //comment
            }
        })
        .strokeStyle(function(d) {
            return (d.faculty ? this.fillStyle().brighter() : this.fillStyle().darker())
        })
        .lineWidth(function(d) {return (d.faculty ? 3 : 1)})
        .shape(function(d) {
            switch (d.group) {
            case 1:
            case 2:return 'circle' //asset
            case 3:return 'square' //project
            case 4:return 'diamond' //comment
            }})
        .title(function(d) {return d.nodeName + (d.domain? ' ('+d.domain+')' : '') })
        .event("mousedown", self.nodeMouseDown)
        .event("drag", force);

        vis.render();

        self.vis = vis;
        self.force = force;
        
        ///User summary actions
        jQuery('#reports-student-tbody tr').click(function(evt) {
            jQuery('#reports-student-tbody tr').removeClass('highlight')

            var user = jQuery(this).addClass('highlight').attr('data-username');
            
            self.nodes.lineWidth(function(d) {
                return (d.users && d.users[user] ? 10 : (d.faculty ? 3 : 1))
            });
        });
        
    }
})()); //end SherdReport



var report_done = false;
window['hs_onshow_reports-graph'] = function() {
    if (SherdReport.started) return
    SherdReport.started = true;
    jQuery.ajax({
        url:'/reports/class_summary/graph.json?nocache='+Number(new Date())+location.search.replace(/^./,'&'),
        dataType:'json',
        success:SherdReport.init
    })
}