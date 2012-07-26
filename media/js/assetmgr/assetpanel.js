var AssetPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    
    self.el = el;
    self.panel = panel;
    self.parentContainer = parent;
    self.space_owner = space_owner;
    
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
            jQuery(self.el).find(".asset-thumb-metadata h6 a").bind("click", { self: self }, self.onClickAssetTitle);
            jQuery(self.el).find("div.gallery-item").bind("mouseenter", { self: self }, self.onMouseEnterAsset);
            jQuery(self.el).find("div.gallery-item").bind("mouseleave", { self: self }, self.onMouseLeaveAsset);
            
            var container = jQuery(self.el).find('div.asset-table')[0];
            jQuery(container).masonry({
                itemSelector : '.gallery-item',
                columnWidth: 25
            });
        }
    });
};


AssetPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();
    
    visible -= jQuery("#footer").height(); // padding
    
    jQuery(self.el).find('div.asset-view-published').css('height', (visible + 23) + "px");
    
    // Resize the collections box, subtracting its header elements
    visible -= jQuery(self.el).find("div.filter-widget").outerHeight();
    jQuery(self.el).find('div.collection-assets').css('height', visible + "px");
};

AssetPanelHandler.prototype.onClickAssetTitle = function (evt) {
    try {

        var self = evt.data.self;
        
        jQuery(self.el).find('td.panel-container.collection').removeClass('fluid').addClass('fixed');
        jQuery(self.el).find('td.panel-container.asset').show();
        jQuery(self.el).find('td.panel-container.asset-details').show();
        
        var srcElement = evt.srcElement || evt.target || evt.originalTarget;
        self.citationView.openCitation(srcElement);
        
        var bits = srcElement.href.split('/');
        
        // Setup the edit view
        AnnotationList.init({
            "asset_id": bits[bits.length - 2],
            "level": "item",
            //,"edit_state": "{{request.GET.edit_state}}"
        });
    } catch (Exception) {}
        
    return false;
};

AssetPanelHandler.prototype.onMouseEnterAsset = function () {
    var metadata = jQuery(this).children('.asset-thumb-metadata')[0];
    jQuery(metadata).fadeIn('fast');
};

AssetPanelHandler.prototype.onMouseLeaveAsset = function () {
    var metadata = jQuery(this).children('.asset-thumb-metadata')[0];
    jQuery(metadata).fadeOut('fast', function () {
        jQuery(metadata).hide();
    });
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


