/* global CitationView: true, djangosherd: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

/**
 * Listens For:
 * assets.refresh > trigger a resize event
 * asset.edit > open asset edit dialog
 *
 * annotation.edit > open annotation edit dialog
 * annotation.create > open create annotation dialog
 * annotation.on_cancel > close create/save dialog
 * annotation.on_save > close create/save dialog
 *
 *
 * Signals:
 * Nothing
 */

var AssetPanelHandler = function(el, $parent, panel, space_owner) {
    var self = this;

    self.$el = jQuery(el);
    self.panel = panel;
    self.$parentContainer = $parent;
    self.space_owner = space_owner;

    djangosherd.storage.json_update(panel.context);

    self.$el.find('div.tabs').tabs();

    jQuery(window).on('annotation.create', {'self': self}, self.dialog);
    jQuery(window).on('annotation.edit', {'self': self}, self.dialog);

    jQuery(window).on('annotation.on_cancel',
        {'self': self}, self.closeDialog);
    jQuery(window).on('annotation.on_save',
        {'self': self}, self.closeDialog);
    jQuery(window).on('annotation.on_create',
        {'self': self}, self.closeDialog);
};

AssetPanelHandler.prototype.closeDialog = function(event) {
    var self = event.data.self;

    self.$quickEditView.fadeOut(function() {
        self.$collectionView.fadeIn();
    });
};

AssetPanelHandler.prototype.dialog = function(
    event, target, assetId, annotationId) {

    var self = event.data.self;

    self.$collectionView = jQuery(target).parents('.collection-materials');
    self.$quickEditView = self.$collectionView.prev();
    self.$quickEditView.find('.asset-view-published').show();

    let $parent = self.$quickEditView.find('#asset-workspace-panel-container');

    // Setup the media display window.
    self.quickEditCitation = new CitationView();
    self.quickEditCitation.init({
        'targets': {
            'asset': $parent.find('#asset-workspace-videoclipbox').get()[0]
        },
        'presentation': 'small',
        'clipform': true,
        'autoplay': false,
        'pdf_iframe': true
    });

    // Setup the edit view
    window.annotationList.init({
        'parent': $parent,
        'asset_id': assetId,
        'annotation_id': annotationId,
        'edit_state': event.type + '.' + event.namespace,
        'update_history': false,
        'vocabulary': self.panel.vocabulary,
        'view_callback': function() {
            self.quickEditCitation.openCitationById(
                null, assetId, annotationId);
        }
    });

    self.$collectionView.fadeOut(function() {
        self.$quickEditView.fadeIn();
    });
    return false;
};

AssetPanelHandler.prototype.editItem = function(evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;

    var bits = srcElement.parentNode.href.split('/');
    self.showAsset(bits[bits.length - 2], null);
    return false;
};
