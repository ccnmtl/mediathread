var AssetPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    
    self.el = el;
    self.panel = panel;
    self.parentContainer = parent;
    self.space_owner = space_owner;
    
    djangosherd.storage.json_update(panel.context);
    
    jQuery(window).resize(function () {
        self.resize();
    });
    
    self._bind(self.el, "td.panel-container", "panel_state_change", function () {
        self.onClosePanel(jQuery(this).hasClass("subpanel"));
    });
    
    
    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': "asset-workspace-videoclipbox",
        'presentation': "medium",
        'clipform': true,
        'autoplay': false,
        'winHeight': function () {
            var elt = jQuery(self.el).find("div.asset-view-published")[0];
            return jQuery(elt).height() -
                (jQuery(elt).find("div.annotation-title").height() + jQuery(elt).find("div.asset-title").height() + 15);
        }
    });

    self.collectionList = new CollectionList({
        'parent': self.el,
        'template': 'gallery',
        'template_label': "media_gallery",
        'create_annotation_thumbs': false,
        'create_asset_thumbs': true,
        'space_owner': self.space_owner,
        'view_callback': function () {
            jQuery(self.el).find(".asset-thumb-title a").bind("click", { self: self }, self.onClickAssetTitle);
            jQuery(self.el).find(".expand").bind("click", { self: self }, self.onToggleFullCollection);
            
            var container = jQuery(self.el).find('div.asset-table')[0];
            jQuery(container).masonry({
                itemSelector : '.gallery-item',
                columnWidth: 25
            });
            
            if (self.panel.current_asset) {
                jQuery(self.el).find('div.expand').show();
            }
            
            jQuery(window).trigger("resize");
        }
    });
    
    if (self.panel.current_asset) {
        self.showAsset(self.panel.current_asset, self.panel.current_annotation);
    }
};

AssetPanelHandler.prototype.showAsset = function (asset_id, annotation_id) {
    var self = this;

    jQuery(self.el).find('td.panel-container.collection').removeClass('fluid').addClass('fixed');
    jQuery(self.el).find('td.panel-container.asset').show();
    jQuery(self.el).find('td.panel-container.asset-details').show();
    jQuery(self.el).find('div.expand').show();
    
    self.citationView.openCitationById(null, asset_id, annotation_id);
    
    jQuery(self.el).find("a.filterbyclasstag").unbind();

    // Setup the edit view
    AnnotationList.init({
        "asset_id": asset_id,
        "annotation_id": annotation_id,
        "view_callback": function () {
            jQuery(self.el).find("a.filterbyclasstag").bind("click", { self: self }, self.onFilterByClassTag);
            jQuery(self.el).find("div.tabs").tabs();
        }
    });
};

AssetPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();
    
    visible -= jQuery("#footer").height(); // padding

    // Resize the collections box, subtracting its header elements
    var collectionHeight = visible - jQuery(self.el).find("div.filter-widget").outerHeight() - jQuery(self.el).find('div.expand').height();
    jQuery(self.el).find('div.collection-assets').css('height', collectionHeight + 35 + "px");
    
    visible = visible - jQuery(self.el).find('div.asset-view-header').height() - 20;
    jQuery(self.el).find('div.asset-view-container').css('height', (visible) + "px");
    jQuery(self.el).find('div.asset-view-published').css('height', (visible + 4) + "px");
    jQuery(self.el).find('div.asset-view-details').css('height', (visible) + "px");
    
    jQuery(self.el).find('div#asset-details-annotations').css('height', (visible - 210) + "px");
};

AssetPanelHandler.prototype.onClickAssetTitle = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    
    var bits = srcElement.href.split('/');
    self.showAsset(bits[bits.length - 2]);
        
    return false;
};

AssetPanelHandler.prototype.onFilterByClassTag = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var bits = srcElement.href.split("/");
    
    self.collectionList.filterByClassTag(bits[bits.length - 1]);
    
    return false;
};

AssetPanelHandler.prototype.onToggleFullCollection = function (evt) {
    var self = evt.data.self;
    
    jQuery(self.el).find('td.panel-container.collection').toggleClass('fixed fluid', 100);
    jQuery(self.el).find('td.panel-container.asset').toggle();
    jQuery(self.el).find('td.panel-container.asset-details').toggle();
    
    jQuery(window).trigger("resize");
    return false;
};

AssetPanelHandler.prototype.onClosePanel = function (isSubpanel) {
    var self = this;
};

AssetPanelHandler.prototype._bind = function (parent, elementSelector, event, handler) {
    var elements = jQuery(parent).find(elementSelector);
    if (elements.length) {
        jQuery(elements[0]).bind(event, handler);
        return true;
    } else {
        return false;
    }
};


