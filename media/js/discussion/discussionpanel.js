var DiscussionPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    self.el = el;
    self.panel = panel;
    self.parentContainer = parent;
    
    jQuery(window).resize(function () {
        self.resize();
    });
    
    // There should only be one per view.
    // Could get hairy once discussion is added to the mix.
    self.collection_list = CollectionList.init({
        'parent': self.el,
        'template': 'collection',
        'template_label': "collection_table",
        'create_annotation_thumbs': true,
        'space_owner': self.space_owner
    });
    
    self.resize();
};

DiscussionPanelHandler.prototype.postInitialize = function () {
    var self = this;
};

DiscussionPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();
    
    jQuery(self.el).find('tr.project-content-row').css('height', (visible) + "px");
    jQuery(self.el).find('div.panel').css('height', (visible - 100) + "px");
};




