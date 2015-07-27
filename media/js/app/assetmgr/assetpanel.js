/* global annotationList: true, CitationView: true, CollectionList: true */
/* global djangosherd: true, getVisibleContentHeight: true */ 

/**
 * Listens For:
 * assets.refresh > trigger a resize/masonry event
 * asset.edit > open asset edit dialog
 * asset.on_delete > update annotation view if required
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

var AssetPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;

    self.el = el;
    self.panel = panel;
    self.parentContainer = parent;
    self.space_owner = space_owner;

    djangosherd.storage.json_update(panel.context);

    jQuery(self.el).find("div.tabs").tabs();

    jQuery(window).resize(function () {
        self.resize();
    });

    jQuery(self.el).delegate("a.asset-title-link", "click", {self: self}, self.onClickAssetTitle);
    jQuery(self.el).delegate("a.edit-asset-inplace", "click", {self: self}, self.editItem);
    jQuery(self.el).delegate("a.filterbyclasstag", "click", {self: self}, self.onFilterByClassTag);
    jQuery(self.el).delegate("a.filterbyvocabulary", "click", {self: self}, self.onFilterByVocabulary);

    // Fired by CollectionList & AnnotationList
    jQuery(window).on('assets.refresh', { 'self': self }, function(event, html) {
        var self = event.data.self;
        var container = jQuery(self.el).find('div.asset-table')[0];
        if (container !== undefined) {
            jQuery(container).masonry('appended', html, true);
        }
        jQuery(window).trigger("resize");
    });

    jQuery(window).on('asset.on_delete', { 'self': self },
        function (event, asset_id) {event.data.self.onDeleteItem(asset_id); });

    jQuery(window).on('asset.edit', { 'self': self }, self.dialog);
    jQuery(window).on('annotation.create', { 'self': self }, self.dialog);
    jQuery(window).on('annotation.edit', { 'self': self }, self.dialog);

    jQuery(window).on('annotation.on_cancel', { 'self': self }, self.closeDialog);
    jQuery(window).on('annotation.on_save', { 'self': self }, self.closeDialog);
    jQuery(window).on('annotation.on_create', { 'self': self }, self.closeDialog);

    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': "asset-workspace-videoclipbox",
        'presentation': "medium",
        'clipform': true,
        'autoplay': false,
        'winHeight': function () {
            if (self.dialogWindow) {
                return 450;
            } else {
                var elt = jQuery(self.el).find("div.asset-view-published")[0];
                return jQuery(elt).height() -
                    (jQuery(elt).find("div.annotation-title").height() + jQuery(elt).find("div.asset-title").height() + 15);
            }
        }
    });

    if (self.panel.show_collection) {
        self.collectionList = new CollectionList({
            'parent': self.el,
            'template': 'gallery',
            'template_label': "media_gallery",
            'create_asset_thumbs': true,
            'space_owner': self.space_owner,
            'owners': self.panel.owners,
            'current_asset': self.panel.current_asset,
            'view_callback': function (assetCount) {
                var self = this;

                if (assetCount > 0) {
                    var container = jQuery(self.el).find('div.asset-table')[0];
                    jQuery(container).masonry({
                        itemSelector : '.gallery-item',
                        columnWidth: 25
                    });
                    jQuery(container).masonry('bindResize');
                } else {
                    jQuery('div.asset-table').css('height', '500px');
                }
            }
        });
    }

    if (self.panel.current_asset) {
        self.showAsset(self.panel.current_asset, self.panel.current_annotation, true);
    }

    jQuery(window).trigger("resize");
};

AssetPanelHandler.prototype.closeDialog = function (event) {
    var self = event.data.self;

    if (self.dialogWindow) {
        jQuery(self.dialogWindow).dialog("close");
    }
};

AssetPanelHandler.prototype.dialog = function (event, assetId, annotationId) {
    var self = event.data.self;

    var title = "Edit Item";
    if (event.type === "annotation") {
        if (event.namespace === "create") {
            title = "Create Selection";
        } else {
            title = "Edit Selection";
        }
    }

    var dlg = jQuery("#asset-workspace-panel-container")[0];
    var elt = jQuery(dlg).find("div.asset-view-tabs").hide();

    self.dialogWindow = jQuery(dlg).dialog({
        open: function () {
            self.dialogWindow = true;
            self.citationView.openCitationById(null, assetId, annotationId);

            // Setup the edit view
            annotationList.init({
                "asset_id": assetId,
                "annotation_id": annotationId,
                "edit_state": event.type + "." + event.namespace,
                "update_history": false,
                "vocabulary": self.panel.vocabulary,
                "view_callback": function () {
                    if (self.dialogWindow) {
                        jQuery(elt).fadeIn("slow");
                    }
                }
            });
        },
        close: function () {
            self.dialogWindow = null;
        },
        title: title,
        draggable: true,
        resizable: true,
        modal: true,
        width: 825,
        height: 600,
        position: "top",
        zIndex: 10000
    });

    return false;
};


AssetPanelHandler.prototype.showAsset = function (asset_id, annotation_id, displayNow) {
    var self = this;

    self.current_asset = parseInt(asset_id, 10);

    if (displayNow) {
        jQuery(self.el).find('td.panel-container.collection').removeClass('maximized').addClass('minimized');
        jQuery(self.el).find('td.pantab-container').removeClass('maximized').addClass('minimized');
        jQuery(self.el).find('div.pantab.collection').removeClass('maximized').addClass('minimized');
        jQuery(self.el).find('td.panel-container.asset').removeClass("closed").addClass("open");
        jQuery(self.el).find('td.panel-container.asset').show();
        jQuery(self.el).find('td.panel-container.asset-details').show();

        self.citationView.openCitationById(null, asset_id, annotation_id);
    }

    // Setup the edit view
    annotationList.init({
        "asset_id": asset_id,
        "annotation_id": annotation_id,
        "update_history": self.panel.update_history,
        "vocabulary": self.panel.vocabulary,
        "view_callback": function () {
            jQuery(self.el).find("div.tabs").fadeIn("fast", function () {
                window.panelManager.verifyLayout(self.el);
                jQuery(window).trigger("resize");
            });
        }
    });
};

AssetPanelHandler.prototype.resize = function () {
    var self = this;

    if (jQuery(self.el).find('td.panel-container.collection').hasClass('minimized')) {
        jQuery("td.asset-view-header").show();
    } else {
        jQuery("td.asset-view-header").hide();
    }

    var collection = jQuery(self.el).find('td.panel-container.collection.subpanel:visible');
    if (collection.length > 0) {
        jQuery("td.collection-view-header").show();
    } else {
        jQuery("td.collection-view-header").hide();
    }

    var pantab = jQuery(self.el).find("div.panel.asset-workspace div.pantab.collection:visible");
    if (pantab.length > 0) {
        jQuery("div.panel.asset-workspace td.panhandle-stripe.collection").show();
    } else {
        jQuery("div.panel.asset-workspace td.panhandle-stripe.collection").hide();
    }

    if (jQuery(self.el).find('td.panel-container.collection').hasClass('minimized') ||
            jQuery(self.el).find('td.panel-container.collection').hasClass('maximized')) {

        var visible = getVisibleContentHeight();
        visible -= jQuery("tr.asset-workspace-title-row").outerHeight();

        // Resize the collections box, subtracting its header elements
        var collectionHeight = visible;
        if (jQuery(self.el).find('td.panel-container.collection').hasClass('minimized')) {
            collectionHeight = visible - jQuery(self.el).find("div.filter-widget").height();
        }
        jQuery(self.el).find('div.collection-assets').css('height', collectionHeight + "px");

        visible += 10;
        jQuery(self.el).find('div.asset-view-container').css('height', (visible) + "px");

        jQuery(self.el).find('div.asset-view-published').css('height', (visible) + "px");

        visible += 2;
        jQuery(self.el).find('div.asset-view-tabs').css('height', (visible) + "px");

        visible -= jQuery('ul.ui-tabs-nav').outerHeight();
        jQuery(self.el).find('.ui-tabs-panel').css('height', (visible - 10) + "px");

        jQuery(self.el).find('form#edit-annotation-form').css('height', (visible - 56) + "px");
        jQuery(self.el).find('form#edit-global-annotation-form').css('height', (visible - 66) + "px");

        visible -= jQuery("div#asset-global-annotation").outerHeight();
        jQuery(self.el).find('div#annotations-organized').css('height', (visible - 5) + "px");

        visible -= jQuery("div#annotations-organized h2").outerHeight() +
            jQuery("div#annotations-organized div.ui-widget-header").outerHeight() + 36;
        jQuery(self.el).find('ul#asset-details-annotations-list').css('height', (visible) + "px");
        jQuery("div.accordion").accordion("refresh");
        
        var container = jQuery(self.el).find('div.asset-table')[0];
        jQuery(container).masonry();

    }
};

AssetPanelHandler.prototype.onClickAssetTitle = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;

    var bits = srcElement.href.split('/');
    self.showAsset(bits[bits.length - 2], null, true);

    return false;
};

AssetPanelHandler.prototype.editItem = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;

    var bits = srcElement.parentNode.href.split('/');
    self.showAsset(bits[bits.length - 2], null, true);
    return false;
};

AssetPanelHandler.prototype.onDeleteItem = function (asset_id) {
    var self = this;

    // if the item being deleted was the current one, then close up shop & show the full asset view
    if (typeof asset_id === "string") {
        asset_id = parseInt(asset_id, 10);
    }

    if (asset_id === self.current_asset) {
        annotationList.refresh({ 'asset_id': asset_id });
    }
};

AssetPanelHandler.prototype.onFilterByClassTag = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var bits = srcElement.href.split("/");

    self.collectionList.filterByClassTag(bits[bits.length - 1]);

    return false;
};

AssetPanelHandler.prototype.onFilterByVocabulary = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    self.collectionList.filterByVocabulary(srcElement);
    return false;
};
