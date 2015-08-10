/* global _: true, Backbone: true */
/* global annotationList: true, CitationView: true */

/**
 * Listens For:
 * Nothing
 *
 * Signals:
 * Nothing
 */

(function(jQuery) {
    var global = this;

    global.SelectionAssignmentView = Backbone.View.extend({
        events : {
        },
        initialize: function(options) {
            //_.bindAll(this);
    
            // Setup the media display window.
            this.citationView = new CitationView();
            this.citationView.init({
                'default_target': 'asset-workspace-videoclipbox',
                'presentation': 'medium',
                'clipform': true,
                'autoplay': false
            });
    
            this.citationView.openCitationById(null, options.itemId, null);
            
            // @todo Setup the edit view -- anotationList.init
        }
    });
}(jQuery));