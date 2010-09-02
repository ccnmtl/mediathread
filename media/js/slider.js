DjangoSherd_createThumbs = function(){} //REMOVE: minimize js processing while debugging

var SherdSlider = new (function() {
    var self = this;
    this.components = {};
    this.columns = {
        'asset_details': {
            title:'Asset Details',
            min_width:400
        },
        'asset_large': {
            title:'',
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
    this.queue = [];
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
        self.components['top'] = self.components['original'] = jQuery('#slider-top').get(0);
        
        self.components['secondary'] = self.components['non-original'] = jQuery('<table class="slider-top"><tbody><tr></tr></tbody></table>').appendTo('#slider-parent').get(0);

        jQuery('#slider-top td.slider-cell').each(function(index) {
            var a = this.id.substr('slider-cell-'.length);
            self.columns[a].html = this;
            self.columns[a].inner_dom = jQuery('div',this).get(0);
            self.columns[a].index = self.order.push(a) -1;
            if (jQuery(this).hasClass('slider-active')) {
                self.columns[a].active = true;
                self.signal('onLoad',a,self.columns[a].html);
                self.edges['right'] = index;
                if (self.edges['left'] == null) 
                    self.edges['left'] = index;
            }
        });
        var getClickListener = function(lr) {
            //factory to avert closure failure on lr variable
            return function(evt) {
                if (self.edges[lr]!=failon) {
                    self.showPane(self.order[ self.edges[lr]+self.links[lr].dir ]);
                }
            }
        }
        for (a in self.links) {
            self.links[a].html = document.getElementById('slider-edge-'+a);
            var failon = Math.min(self.links[a].max, self.order.length-1);
            jQuery(self.links[a].html).parent().click(getClickListener(a));
        }

        self.onResize();
        jQuery(window).resize(self.onResize);
        self.updateLinks();
    }
    this.onResize = function(evt) {
        self.winwidth = jQuery('#block').width();
        jQuery('#slider-parent').width(self.winwidth);
        for (var i=0;i<self.order.length;i++) {
            var c = self.columns[self.order[i]];
            c.width = jQuery(c.html).width() || c.min_width;
        }
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
    this.show = function(col) {
        self.columns[col].active = true;
        jQuery(self.columns[col].inner_dom).show();
        //jQuery(self.columns[col].html).addClass('slider-active')
        //.css({width:width})
    }
    this.hide = function(col) {
        self.columns[col].active = false;
        jQuery(self.columns[col].inner_dom).hide();
        //jQuery(self.columns[col].html).removeClass('slider-active')
    }
    this.currentFitWidth = function() {
        ///maybe we should return actual?
        var w = 0;
        for (var i=self.edges.left;i<=self.edges.right;i++) {
            w+= self.columns[self.order[i]].min_width;
        }
        return w;
    }
    this.forEachColumn = function(func, init, max) {
        max = (typeof max=='number') ? max : self.order.length;
        var res = init || 0;
        for (var i=0;i<max;i++) {
            res += func.call(self, self.columns[self.order[i]], self.order[i]);
        }
        return res;
    }
    this.edge = function(dir,is_opposite) {
        var d = (is_opposite ? self.opp(dir) : dir);
        return self.order[self.edges[d]];
    }
    this.opp =function(dir) {
        return ((dir=='left')?'right':'left');
    }

    this.updateLinks = function() {
        var b = {
            'left':self.edges['left']-1,
            'right':self.edges['right']+1
        };
        for (a in self.links) {
            if (b[a]>=0 && b[a]<self.order.length && self.columns[ self.order[b[a]] ].title) {
                jQuery(self.links[a].html)
                .html(self.columns[ self.order[b[a]] ].title)
                .parent().show();            
            } else {
                jQuery(self.links[a].html).parent().hide();
            }
        }
    }

    this.slide = function(direction,col) {
        /* This may be overly complex.  Basically we swap the new column
           into a secondary table and then move both tables into the space
           This is meant to stop disruption based on the new column getting weird
           widths (and thus bumping the content that's shown before animation)
         */
        if ((direction=='left' && self.edges['left']==0)
            || (direction=='right' && self.edges['right']==self.order.length-1))
            return;//no place to slide to

        var dir = ((direction=='left')?'+':'-'),
            new_col = self.columns[col],
            opp = self.edge(direction,'opposite'),
            will_fit = (self.currentFitWidth()+new_col.min_width < self.winwidth),
            width = new_col.min_width;
        if (direction=='right') {
            width = self.columns[opp].width;
            if (!will_fit) {
                new_col.width = Math.max(new_col.min_width, 
                                         self.winwidth
                                         -self.columns[self.edge('right')].width);
            }
        } else if (!will_fit && direction=='left') {
            width = new_col.width = Math.max(new_col.min_width, 
                                             self.winwidth
                                             -self.columns[self.edge('left')].width)
        } 

        //TODO: this will need to be more sophisticated
        /// we'll need to decide what/when to scrunch,
        var left_pos = self.forEachColumn(function(c){return -c.width;},
                                          0,/*upto=*/self.edges['left'])
        ///update which columns are at the edges  ??TODO: confirm this is correct
        self.edges[direction] += self.links[direction].dir
        self.edges[self.opp(direction)] += self.links[direction].dir


        jQuery(self.components.secondary).width(
            self.forEachColumn(function(c){return c.width;})
        )
        var tr = jQuery(self.components.secondary)
                 .css({position:'absolute',left:left_pos+'px'})
                 .find('tr').empty().get(0)
        
        ///this will be multiple: all but current
        self.forEachColumn(function(c) {
            jQuery(tr).append('<td class="slider-cell" style="width:'+c.width+'px"></td>')
        })
        if (new_col.inner_dom) {
            jQuery( tr.childNodes.item(new_col.index) ).append(new_col.inner_dom)
        }
        self.show(col)
        self.preserveHeight(true)
        jQuery(self.components.top).css({position:'absolute'});


        self.queue.push(function() {
            if (!will_fit)
                self.hide(opp);
                    
                    self.forEachColumn(function(c,cname) {
                        if (cname == col) return;
                        c.html = tr.childNodes.item(c.index);
                        if (c.inner_dom) 
                            c.html.appendChild(c.inner_dom);
                    });
                    //switch
                    var s = self.components.secondary;
                    self.components.secondary = self.components.top;
                    self.components.top = s;
                    self.updateLinks();
        });
        jQuery(self.components['original']).animate({left:dir+"="+width+'px'},{
            complete:function() {
                var w;
                while (w = self.queue.shift()) {
                    w();
                }
            }
        });
        jQuery(self.components['non-original']).animate({left:dir+"="+width+'px'});
    }
    var indexOf= function(arr,val) {
        if (arr.indexOf) return arr.indexOf(val)
        ///IE SUX
        else for (var i=0;i<arr.length;i++) {
            if (arr[i]==val) return i;
        }
    }
    this.direction = function(colname, from) {
        var ind = indexOf(self.order,colname);
        if (!from) {
            if (ind < self.edges.left) return 'left';
            if (ind > self.edges.right) return 'right';
        } else {
            var frm_ind = indexOf(self.order,from);
            return ((ind < frm_ind)?'left':'right');
        }
    }
    
    this.showPane = function(colname, args) {
        self.signal('load',colname,args);
        if (!self.columns[colname].active) {
            var doThis = function() {
                self.slide(self.direction(colname), colname);
            }
            if (self.queue.length) {
                self.queue.push(doThis);
            } else {
                doThis();
            }
        }
    }

    this.junk = function() {
        jQuery('#slider-parent').width();
        jQuery('#slider-cell-asset_large').animate({width:'620px'});
        jQuery('#slider-cell-reflection').hide();
    }

})();

