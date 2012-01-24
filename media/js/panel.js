(function() {
    window.PanelManager = new (function PanelManagerAbstract(){
        var self = this;
      
        this.init = function(config) {
            jQuery(window).resize(function () {  
                self.onResize();
            });
            
            jQuery(".panhandle").click(function(event) {
                self.onClickPanhandle(this, event);
            });
            
            // figure out which panels get shown/hidden
            // config should contain the rules
            // panels ordered by show/hide behavior?
        }
        
        this.onClickPanhandle = function(element, event) {
            // Open the panhandle's panel
            var panel = jQuery(element).nextAll(".panel");
            jQuery(panel[0]).toggleClass("open closed");
            
            var screenWidth = jQuery(window).width();
            console.log("The screen is: " + screenWidth);
            
            // Figure out if any other panels need to be closed
            // Add up widths on all the fixed panels + min-width on fluid panels
            var width = 0;
            var panels = jQuery(".fixed");
            for (var i = 0; i < panels.length; i++) {
                width += parseInt(jQuery(panels[i]).css("width").replace('px', ''));
            }
            
            panels = jQuery(".fluid");
            for (i = 0; i < panels.length; i++) {
                width += parseInt(jQuery(panels[i]).css("min-width").replace('px', ''));
            }
            
            if (width > screenWidth) {
                // Something needs to close...
            }
        }
        
        this.onResize = function() {
        }
        
        
    })();
})();