/* global pv: true */
//requires Protovis: http://vis.stanford.edu/protovis/

/* eslint-disable-next-line no-unused-vars */
var SherdReport = function() {
    var self = this;
    this.started = false;

    this.nodeMouseDown = function(node) {
        jQuery('#contributedTo')
            .html(node.nodeName)
            .attr('href', node.href);

        self.innerMouseDown.apply(this, arguments);
    };

    this.nodeDefaultLineWidth = function(d) {
        return (d.faculty ? 3 : 1);
    };

    this.init = function(json) {
        var w = jQuery('#reports-graph').width();
        var h = Math.max(500, jQuery(window).height() - 300);
        var domainColors = pv.Colors.category20();

        var vis = new pv.Panel({canvas: 'reports-graph-visualization'})
            .canvas('reports-graph-visualization')
            .width(w)
            .height(h)
            .fillStyle('white')
            .event('mousedown', pv.Behavior.pan())
            .event('mousewheel', pv.Behavior.zoom(
                //clearly protovis default is calibrated for firefox
                //or a Mac with those stupid little dots for scroll-wheels
                (/(Firefox|Mac OS X)/.test(navigator.userAgent) ? 1 : 3)
            ));

        var force = vis.add(pv.Layout.Force)
            .nodes(json.nodes)
            .links(json.links);

        self.links = force.link.add(pv.Line)
            .strokeStyle(function(n, lnk) {
                var g = (lnk.bare ? 0.2 : 0.5);
                return 'rgba(0,0,0,' + g + ')';
            });

        self.innerMouseDown = pv.Behavior.drag();

        self.nodes = force.node.add(pv.Dot)
            .size(function(d) {
                return 3 + (d.linkDegree + 4) * Math.pow(this.scale, -1.5);
            })
            .fillStyle(function(d) {
                switch (d.group) {
                case 1:
                    return new pv.Color.Rgb(256, 256, 0, 1); //tag
                case 2:
                    return domainColors(d.domain); //asset
                case 3:
                    return new pv.Color.Rgb(0, 100, 256, 1); //project
                case 4:
                    return new pv.Color.Rgb(0, 100, 0, 1); //comment
                default:
                    return new pv.Color.Rgb(0, 0, 0, 1);
                }
            })
            .strokeStyle(function(d) {
                return (d.faculty ? new pv.Color.Rgb(200, 0, 0, 1) :
                    this.fillStyle().darker());
            })
            .lineWidth(self.nodeDefaultLineWidth)
            .shape(function(d) {
                switch (d.group) {
                case 1:
                case 2:
                    return 'circle'; //asset
                case 3:
                    return 'square'; //project
                case 4:
                    return 'diamond'; //comment
                }
            })
            .title(function(d) { return d.nodeName; })
            .event('mousedown', self.nodeMouseDown)
            .event('drag', force);

        vis.render();

        self.vis = vis;
        self.force = force;

        ///User summary actions
        jQuery('.custom-select').on('change', function(evt) {
            var username = this.value;
            if (username === 'all') {
                self.nodes.lineWidth(self.nodeDefaultLineWidth);
                jQuery(this).siblings().removeClass('active');
            } else {
                jQuery(this).siblings().removeClass('active');
                jQuery(this).addClass('active');
                self.nodes.lineWidth(function(d) {
                    return (
                        d.users &&
                        d.users[username] ? 10 : self.nodeDefaultLineWidth(d));
                });
            }
        });
    };
}; //end SherdReport
