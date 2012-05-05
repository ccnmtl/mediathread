var DiscussionPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    self.el = el;
    self.panel = panel;
    self.parentContainer = parent;
    self.space_owner = space_owner;
    self.form = jQuery(self.el).find("form.threaded_comments_form")[0];
    
    jQuery(window).resize(function () {
        self.resize();
    });
    
    // hook up behaviors
    jQuery(window).bind('tinymce_init_instance', function (event, instance, param2) {
        self.postInitialize(instance);
    });
    
    // Add the tinyMCE control to the comment field.
    tinyMCE.execCommand("mceAddControl", false, "id_comment");
    
    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': panel.context.discussion.id + "-videoclipbox",
        'onPrepareCitation': self.onPrepareCitation,
        'presentation': "medium"
    });
    //self.citationView.decorateLinks(self.essaySpace.id);
    
    self.resize();
};

DiscussionPanelHandler.prototype.postInitialize = function (instance) {
    var self = this;
    
    if (instance.id === "id_comment") {
        
        self.tinyMCE = instance;
        self.tinyMCE.focus();
        
        // Reset tinyMCE width to 100% via javascript. TinyMCE doesn't resize properly
        // if this isn't completed AFTER instantiation
        jQuery('#id_comment_tbl').css('width', "100%");
                
        if (!self.collection_list) {
            self.collection_list = new CollectionList({
                'parent': self.el,
                'template': 'collection',
                'template_label': "collection_table",
                'create_annotation_thumbs': true,
                'space_owner': self.space_owner
            });
            
            self.commentForm = new AjaxCommentForm({
                form: self.form,
                el: jQuery(self.el).find('div.threadedcomments-container')[0],
                space_owner: self.space_owner,
                parent: self,
                citationView: self.citationView
            });
            
            var threads = jQuery('li.comment-thread');
            if (threads.length === 0) {
                self.open_edit();
            }
        }
        self.resize();
    }
};

DiscussionPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();
    
    visible -= jQuery(self.el).find(".discussion-toolbar-row").height();
    visible -= jQuery(self.el).find(".discussion-participant-row").height();
    visible -= 80; // padding
    
    if (self.tinyMCE) {
        var threads = jQuery('li.comment-thread');
        var editorHeight = visible;
        if (threads.length === 0) {
            editorHeight -= 35;
        } else {
            editorHeight = 150;
        }
            
        // tinyMCE project editing window. Make sure we only resize ourself.
        jQuery(self.el).find("table.mceLayout").css('height', (editorHeight) + "px");
        jQuery(self.el).find("iframe").css('height', (editorHeight) + "px");
    }
    
    visible += 25;
    jQuery(self.el).find('tr.discussion-content-row').css('height', (visible) + "px");
    jQuery(self.el).find('tr.discussion-content-row').children('td.panhandle-stripe').css('height', (visible) + "px");
    jQuery(self.el).find('div.panel').css('height', (visible - 100) + "px");
    jQuery(self.el).find('div.threadedcomments-container').css('height', (visible) + "px");
};

ProjectPanelHandler.prototype.onPrepareCitation = function (target) {
    var a = jQuery(target).parents("td.panel-container.media");
    if (a && a.length) {
        PanelManager.openSubPanel(a[0]);
    }
};

DiscussionPanelHandler.prototype.set_comment_content = function (content) {
    var self = this;
    
    content = content || { comment: '<p></p>' };
    self.form.elements.comment.value = content.comment;
    self.form.elements.title.value = content.title || '';
    
    try {
        if (self.tinyMCE) {
            self.tinyMCE.setContent(content.comment);
        }
    } catch (e) {
        /*IE totally SUX: throws some object error here. probably tinymce's fault */
    }
};

DiscussionPanelHandler.prototype.open_respond = function (evt) {
    var self = this;
    
    jQuery(self.form).addClass("response");
    jQuery(self.form).children("h3").show();
    jQuery(self.form).children("input.cancel").show();

    var elt = evt.srcElement || evt.target || evt.originalTarget;
    self.form.elements.parent.value = elt.getAttribute("data-comment");
    self.form.elements['edit-id'].value = '';
    self.mode = 'post';
    
    var li = jQuery(elt).parents("li.comment-thread")[0];
    jQuery(li).find("div.respond_to_comment_form_div").hide();
    
    self.open_comment_form(li);
};

DiscussionPanelHandler.prototype.open_edit = function (evt, focus) {
    var self = this;
    
    jQuery(self.form).removeClass("response");
    jQuery(self.form).children("h3").hide();

    if (evt === undefined) {
        self.form.elements.parent.value = '';
        self.open_comment_form();
    } else {
        var elt = evt.srcElement || evt.target || evt.originalTarget;
    
        var id = elt.getAttribute("data-comment");
        self.form.elements['edit-id'].value = id;
        self.set_comment_content(self.commentForm.read({ html: jQuery('#comment-' + id).get(0)}));
        
        var li = jQuery(elt).parents("li.comment-thread")[0];
        var myText = jQuery(li).find("div.threaded_comment_text")[0];
        jQuery(myText).hide();
        var myToolbar = jQuery(li).find("div.respond_to_comment_form_div")[0];
        jQuery(myToolbar).hide();

        elt = jQuery(li).find("div.threaded_comment_header")[0];
        self.open_comment_form(elt);
    }
};

DiscussionPanelHandler.prototype.open_comment_form = function (insertAfter) {
    var self = this;
    if (insertAfter) {
        self.tinyMCE = null;
        tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
        jQuery(self.form).insertAfter(insertAfter);
        tinyMCE.execCommand("mceAddControl", false, "id_comment");
    }
    jQuery(self.form).show();
    
    var elt = jQuery(self.form).find("#comment-form-submit")[0];
    jQuery(self.el).find("div.threadedcomments-container").animate({scrollTop: jQuery(elt).offset().top}, 500);
    
};


DiscussionPanelHandler.prototype.hide_comment_form = function () {
    var self = this;
    jQuery(self.form).hide();
};

DiscussionPanelHandler.prototype._bind = function (parent, elementSelector, event, handler) {
    var elements = jQuery(parent).find(elementSelector);
    if (elements.length) {
        jQuery(elements[0]).bind(event, handler);
        return true;
    } else {
        return false;
    }
};


