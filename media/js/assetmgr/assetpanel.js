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
        'winHeight': function () {
            var elt = jQuery(self.el).find("div.asset-view-published")[0];
            return jQuery(elt).height() -
                (jQuery(elt).find("div.annotation-title").height() + jQuery(elt).find("div.asset-title").height() + 15);
        }
    });
    
/**
    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': panel.context.project.id + "-videoclipbox",
        'presentation': "default"
    });
    
    jQuery(window).bind('beforeunload', function () {
        return self.beforeUnload();
    });
**/
    
    self.collectionList = new CollectionList({
        'parent': self.el,
        'template': 'collection',
        'template_label': "collection_table",
        'create_annotation_thumbs': true,
        'space_owner': self.space_owner,
        'view_callback': function () {
            jQuery(self.el).find("a.asset-title-link").bind("click", { self: self }, self.onClickAssetTitle);
            jQuery(self.el).find("a.materialCitationLink").bind("click", { self: self}, self.onClickAssetTitle);
            
            jQuery(self.el).find("a.annotate-asset").bind("click", { self: self }, self.onZoomInAsset);
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

AssetPanelHandler.prototype.onZoomInAnnotation = function(evt) {
    
};

AssetPanelHandler.prototype.onZoomInAsset = function (evt) {
    
    try {
        var self = evt.data.self;
        var srcElement = evt.srcElement || evt.target || evt.originalTarget;
        var bits = srcElement.parentNode.href.split('/');

        // Open the citation to the right
        self.citationView.openCitation(srcElement.parentNode);

        // Setup the edit view
        AnnotationList.init({
            "asset_id": bits[bits.length - 2],
            "level": "item",
            //,"edit_state": "{{request.GET.edit_state}}"
        });
        
    } catch (Exception) {
        
    }
    return false;
};

AssetPanelHandler.prototype.onClickAssetTitle = function (evt) {
    try {
        var self = evt.data.self;
        var srcElement = evt.srcElement || evt.target || evt.originalTarget;
        self.citationView.openCitation(srcElement);
    } catch (Exception) {}
        
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


