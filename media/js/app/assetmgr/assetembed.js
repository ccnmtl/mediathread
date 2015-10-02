/* global _: true, Backbone: true, CitationView: true, CollectionList: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function(jQuery) {
    var global = this;

    global.AssetEmbedView = Backbone.View.extend({
        events: {
            'click .btn-embed-item': 'onEmbedItem',
            'click .btn-show-submit': 'onShowSubmitDialog',
            'click .toggle-feedback': 'onToggleFeedback',
            'click .save-feedback': 'onSaveFeedback'
        },
        initialize: function(options) {
            _.bindAll(this, 'render');

            this.collectionList = new CollectionList({
                'parent': this.el,
                'template': 'embed',
                'template_label': 'collection_table',
                'create_annotation_thumbs': true,
                'space_owner': options.space_owner,
                'owners': options.owners,
                'citable': true,
                'current_asset': null
            });
        }
    });
}(jQuery));
