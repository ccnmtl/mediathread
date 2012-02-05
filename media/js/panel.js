(function() {
    window.PanelManager = new (function PanelManagerAbstract(){
        var self = this;
      
        this.init = function(config) {
            self.config = config;
            
            jQuery(".pantab-container").click(function(event) {
                self.slidePanel(this, event);
            });
        }
        
        this.slidePanel = function(pantab_container, event) {
            // Open/close this panhandle's panel
            var panel = jQuery(pantab_container).prevAll("td.panel-container");
            jQuery(panel[0]).toggleClass("open closed");
            
            var panelTab = jQuery(pantab_container).children("div.pantab");
            jQuery(panelTab[0]).toggleClass("open closed");
            
            self.verifyLayout(panel[0]);
        }
        
        this.openSubPanel = function(subpanel) {
            if (subpanel && !jQuery(subpanel).hasClass("open")) {
                jQuery(subpanel).toggleClass("open closed");
                
                var container = jQuery(subpanel).nextAll("td.pantab-container");
                var panelTab = jQuery(container[0]).children("div.pantab");
                jQuery(panelTab[0]).toggleClass("open closed");
                
                self.verifyLayout(subpanel);
            }
        }
        
        this.close = function() {
        }
        
        this.verifyLayout = function(panel) {
            if (jQuery(panel).hasClass("open")) {
                // Is there enough room? Does anything need to be closed?
                var screenWidth = jQuery(window).width();
                var tableWidth = jQuery("#"+self.config.container).width();
                
                if (tableWidth > screenWidth) {
                    var parent = panel;
                    
                    var parents = jQuery(panel).parents("td.panel-container");
                    if (parents && parents.length)
                        parent = parents[0];

                    var a = jQuery("#"+self.config.container).find("td.panel-container.open");
                    for (var i = a.length - 1; i >= 0 && tableWidth > screenWidth; i--) {
                        var p = a[i];
                        if (panel != p && parent != p) {
                            // close it
                            jQuery(p).toggleClass("open closed");
                            
                            var container = jQuery(p).nextAll("td.pantab-container");
                            var panelTab = jQuery(container[0]).children("div.pantab");
                            jQuery(panelTab[0]).toggleClass("open closed");
                            
                            tableWidth = jQuery("#"+self.config.container).width();
                        }
                    }
                    
                    // @todo -- once discussion is in place and we have a 3 column solution 
                    // Code should break on panel != parent, then start closing from the right, rather than from the left.
                }
            }
        }
        
    })();
})();