var DiscussionPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    self.el = el;
    self.panel = panel;
    self.parentContainer = parent;
    self.space_owner = space_owner;
    
    jQuery(window).resize(function () {
        self.resize();
    });
    
    // There should only be one per view.
    // Could get hairy once discussion is added to the mix.
    self.collection_list = new CollectionList({
        'parent': self.el,
        'template': 'collection',
        'template_label': "collection_table",
        'create_annotation_thumbs': true,
        'space_owner': self.space_owner
    });
    
    // hook up behaviors
    jQuery(window).bind('tinymce_init_instance', function (event, param1, param2) {
        self.postInitialize(param1);
    });
    
    tinyMCE.execCommand("mceAddControl", false, "id_comment");
    
    self.resize();
};

DiscussionPanelHandler.prototype.postInitialize = function (tinymce_instance_id) {
    if (tinymce_instance_id === "id_comment") {
        // do something here
    }
};

DiscussionPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();
    
    visible -= jQuery(self.el).find(".project-toolbar-row").height();
    visible -= jQuery(self.el).find(".project-participant-row").height();
    visible -= 35; // padding
    
    if (self.tinyMCE) {
        var editorHeight = visible - 15;
        // tinyMCE project editing window. Make sure we only resize ourself.
        jQuery(self.el).find("table.mceLayout").css('height', (editorHeight) + "px");
        jQuery(self.el).find("iframe").css('height', (editorHeight) + "px");
    }
    
    jQuery(self.el).find("div.essay-space").css('height', (visible) + "px");
    jQuery(self.el).find('tr.project-content-row').css('height', (visible) + "px");
    jQuery(self.el).find('tr.project-content-row').children('td.panhandle-stripe').css('height', (visible) + "px");
    jQuery(self.el).find('div.panel').css('height', (visible - 200) + "px");
};




