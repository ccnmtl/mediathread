DjangoSherd_createThumbs = function(){} //REMOVE: minimize js processing while debugging

var SherdSlider = new (function() {
    var self = this;
    this.components = {};
    this.columns = {
        'asset_details': {
            title:'Details',
            min_width:400
        },
        'asset_large': {
            title:'Asset',
            min_width:620,
            max_space:true,
            load:function(url) {
                
            }
        },
        'asset_column': {
            title:'Analysis',
            min_width:404,
            onLoad:function(elt) {
                jQuery('a.asset-title-link',elt).click(function(evt){
                    self.showPane('asset_large',this.href);
                    evt.preventDefault();
                })
            }
        },
        'reflection': {
            title:'Reflection',
            min_width:420,
            max_space:true
        }
    }
    this.links = {
        'left':{
            active:false,
            name:'',
            max:0,
            dir:-1
        },
        'right':{
            active:false,
            name:'',
            max:100,
            dir:+1
        }
    }
    this.order = [];//'asset_details','asset_large','asset_column','reflection'
    this.edges = {'left':null,'right':null};

    this.setTitle = function(name,title) {
        self.columns[name].title = title;
        for (a in self.links) {
            if (name == self.links[a].name) {
                self.links[a].html.innerHTML = title;
            }
        }
    }
    this.init = function() {
        jQuery('#slider-top td.slider-cell').each(function(index) {
            var a = this.id.substr('slider-cell-'.length);
            self.columns[a].html = this;
            self.columns[a].index = self.order.push(a) -1;
            if (jQuery(this).hasClass('slider-active')) {
                self.columns[a].active = true;
                self.signal('onLoad',a,self.columns[a].html);
                self.edges['right'] = index;
                if (self.edges['left'] == null) 
                    self.edges['left'] = index;
            }

            
        });
        for (a in self.links) {
            self.links[a].html = document.getElementById('slider-edge-'+a);
            var failon = Math.min(self.links[a].max, self.order.length-1);
            var aa = a; //so we can use it in a closure
            jQuery(self.links[a].html).parent().click(function(evt) {
                if (self.edges[aa]!=failon) {
                    self.showPane(self.order[ self.edges[aa]+self.links[aa].dir ])
                }
            });
        }

        self.onResize();
        jQuery(window).resize(self.onResize);
        self.components = {
            'top':jQuery('#slider-top').get(0),
            'secondary':jQuery('<table class="slider-top"><tbody><tr></tr></tbody></table>').appendTo('#slider-parent').get(0)
        }
    }
    this.onResize = function(evt) {
        self.winwidth = jQuery('#block').width();
        jQuery('#slider-parent').width(self.winwidth);
    }

    this.options = {
        "minimum_width":1024 //fit them in to here, even if you have a smaller width
        ,"duration":1.0 //seconds
    };
    this.signal = function(func,colname,args) {
        if (self.columns[colname][func]) {
            self.columns[colname][func](args);
        }
    }
    this.preserveHeight = function(start) {
        if (start) {
            var height = jQuery('#slider-parent').height();
            jQuery('#slider-parent').height(height+'px');
        } else {
            jQuery('#slider-parent').height('auto');
        }
    }
    this.show = function(col,width) {
        self.columns[col].active = true;
        jQuery(self.columns[col].html)
        //.addClass('slider-active')
        .css({width:width})
        .show();
    }
    this.hide = function(col) {
        self.columns[col].active = false;
        jQuery(self.columns[col].html)
        .removeClass('slider-active')
        .hide();
    }
    this.currentFitWidth = function() {
        ///maybe we should return actual?
        var w = 0;
        for (var i=self.edges.left;i<self.edges.right;i++) {
            w+= self.order[i].min_width;
        }
        return w;
    }
    this.edge = function(dir,is_opposite) {
        var d = (is_opposite ? self.opp(dir) : dir);
        return self.order[self.edges[d]];
    }
    this.opp =function(dir) {
        return ((dir=='left')?'right':'left');
    }
    this.slide = function(direction,col) {
        console.log('slide');
        if ((direction=='left' && self.edges['left']==0)
            || (direction=='right' && self.edges['right']==self.order.length-1))
            return;//no place to slide to

        console.log(direction);

        var dir = ((direction=='left')?'+=':'-='),
            opp = self.edge(direction,'opposite'),
            will_fit = (self.currentFitWidth()
                        +self.columns[col].min_width < self.winwidth),
            width = ((will_fit || direction=='left')
                     ? self.columns[col].min_width
                     : self.columns[opp].min_width //TODO: actual width
                    )+ 'px';
            //TODO: this will need to be more sophisticated
            /// we'll need to decide what/when to scrunch,
        console.log(will_fit);
        ///update which columns are at the edges  ??TODO: confirm this is correct
        self.edges[direction] += self.links[direction].dir;
        self.edges[self.opp(direction)] += self.links[direction].dir;
        console.log(self.edges);

        self.preserveHeight(true);
        console.log(self.components);        
        console.log(width);        

        jQuery(self.components.top)
        .css({position:'absolute'})
        .animate({left:dir+width},{
            complete:function() {
                console.log('hi');
                self.show(col);
                self.hide(opp);
                //jQuery(self.components.top).css({position:'static'});
                //self.preserveHeight(false);
            }
        });
    }

    this.direction = function(colname, from) {
        var ind = self.order.indexOf(colname);
        if (!from) {
            if (ind < self.edges.left) return 'left';
            if (ind > self.edges.right) return 'right';
        } else {
            var frm_ind = self.order.indexOf(from);
            return ((ind < frm_ind)?'left':'right');
        }
    }
    
    this.showPane = function(colname, args) {
        console.log(colname);
        if (!self.columns[colname].active) {
            self.slide(self.direction(colname), colname);
        }
        self.signal('load',colname,args);
    }

    this.junk = function() {
        jQuery('#slider-parent').width();
        jQuery('#slider-cell-asset_large').animate({width:'620px'});
        jQuery('#slider-cell-reflection').hide();
    }

})();

