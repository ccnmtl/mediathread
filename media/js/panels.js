(function() {
    
    window.PanelManager = new (function PanelManager(){
        var self = this;
        
        this.init = function() {
            jQuery(".sliding-panel-closed").click(self.slidePanelClick);
        }
        
        this.slidePanelClick = function(evt) {
            if (jQuery(this).hasClass("sliding-panel-open")) {
                jQuery(this).toggleClass("sliding-panel-open sliding-panel-closed");
            } else {
                // open me
                var screenWidth = jQuery(document).width();
                
                jQuery(this).toggleClass("sliding-panel-open sliding-panel-closed");
                
                var totalPanelWidth = 0;
                jQuery(".sliding-panel-open").each(function() { totalPanelWidth += jQuery(this).width() });
                
                if (totalPanelWidth > screenWidth) {
                    var siblings = jQuery(this).siblings(".sliding-panel-open");
                    
                    // close on the left or right?
                    if (jQuery(this).prev(".sliding-panel-open").length > 0) {
                        jQuery(siblings[0]).toggleClass("sliding-panel-open sliding-panel-closed");
                        
                        // close on the left
                    } else if (jQuery(this).next(".sliding-panel-open").length > 0) {
                        // close on the right
                        jQuery(siblings[siblings.length - 1]).toggleClass("sliding-panel-open sliding-panel-closed");
                    }
                }
                
                jQuery(".sliding-panel").unbind("click");
                jQuery(".sliding-panel-closed").bind("click", self.slidePanelClick);
            }
        }
    });
        
    jQuery(document).ready(function() {
        PanelManager.init();        
    });

})();