(function() {
    
    window.PanelManager = new (function PanelManager(){
        var self = this;
        var sliding_duration = 500;
        
        this.init = function() {
            jQuery(".sliding-panel-tab").click(self.slidePanelClick);
        }
        
        this.slidePanelClick = function(evt) {
            if (jQuery(this).hasClass("sliding-panel-open")) {
                console.log("click on open");
                //jQuery(this).toggleClass("sliding-panel-open sliding-panel-closed");
            } else {
                // open me
                var panel = jQuery(this).next()[0];
                
                var screenWidth = jQuery(document).width();
                console.log("Screen Width: " + screenWidth);
                
                var totalPanelWidth = 0;
                var siblings = jQuery(panel).siblings(".sliding-panel-open, .sliding-panel-tab");
                jQuery(siblings).each(function() { totalPanelWidth += jQuery(this).width() });
                
                jQuery(panel).switchClass("sliding-panel-closed", "sliding-panel-open", self.sliding_duration);
                
                setTimeout(function() {
                    totalPanelWidth += jQuery(panel).width();
                    console.log("Total Panel Width: " + totalPanelWidth);
                    
                    var prevPanels = jQuery(panel).prevAll(".sliding-panel-open");
                    var nextPanels = jQuery(panel).nextAll(".sliding-panel-open");
                        
                    if (totalPanelWidth > screenWidth) {
                        // close on the left or right? limited to one close for the moment.
                        var sib = null;
                        if (prevPanels.length > 0) {
                            // close on the left -- furthest out
                            sib = prevPanels[prevPanels.length-1];
                        } else if (nextPanels.length > 0) {
                            // close on the right -- furthest out
                            sib = nextPanels[nextPanels.length-1];
                        }
                            
                        if (sib) {
                            jQuery(sib).animate({width: '0px'}, self.sliding_duration, function() {
                                jQuery(sib).toggleClass("sliding-panel-open sliding-panel-closed");
                                jQuery(sib).removeAttr("style");
                            });
                        }
                    }
                }, self.sliding_duration);
            }
        }
    });
        
    jQuery(document).ready(function() {
        PanelManager.init();        
    });

})();