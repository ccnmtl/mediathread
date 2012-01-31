(function() {
    window.PanelManager = new (function PanelManagerAbstract(){
        var self = this;
      
        this.init = function(config) {
            jQuery(window).resize(function () {  
                self.onResize();
            });
            
            jQuery(".panhandle-stripe").click(function(event) {
                self.onClickPanelLeftHandle(this, event);
            });
            
            jQuery(".pantab-container").click(function(event) {
                self.onClickPanelRightHandle(this, event);
            });

            
            // figure out which panels get shown/hidden
            // config should contain the rules
            // panels ordered by show/hide behavior?
        }
        
        this.onClickPanelLeftHandle = function(element, event) {
            // Open the panhandle's panel
            var panel = jQuery(element).nextAll("td.panel-container");
            jQuery(panel[0]).toggleClass("open closed");
            
            var panelTabContainer = jQuery(panel).nextAll("td.pantab-container");
            var panelTab = jQuery(panelTabContainer[0]).children("div.pantab");
            jQuery(panelTab[0]).toggleClass("open closed");
            
            var screenWidth = jQuery(window).width();
            console.log("The screen is: " + screenWidth);
            jQuery("table.panel").css("width", screenWidth);
            
            // Figure out if any other panels need to be closed
            // Add up widths on all the fixed panels + min-width on fluid panels
            //var width = 0;
            //var panels = jQuery(".fixed");
            //for (var i = 0; i < panels.length; i++) {
            //    width += parseInt(jQuery(panels[i]).css("width").replace('px', ''));
            //}
            
            //panels = jQuery(".fluid");
            //for (i = 0; i < panels.length; i++) {
            //    width += parseInt(jQuery(panels[i]).css("min-width").replace('px', ''));
            //}
            
            //if (width > screenWidth) {
                // Something needs to close...
            //}
        }
        
        this.onClickPanelRightHandle = function(element, event) {
            // Open/close this panhandle's panel
            var panel = jQuery(element).prevAll("td.panel-container");
            jQuery(panel[0]).toggleClass("open closed");
            
            var panelTab = jQuery(element).children("div.pantab");
            jQuery(panelTab[0]).toggleClass("open closed");
        }
        
        this.onResize = function() {
        }
        
        this.openSubPanel = function(element) {
            if (element && !element.hasClass("open")) {
                jQuery(element).toggleClass("open closed");
                
                var container = jQuery(element).nextAll("td.pantab-container");
                var panelTab = jQuery(container[0]).children("div.pantab");
                jQuery(panelTab[0]).toggleClass("open closed");
            }
        }
        
    })();
})();