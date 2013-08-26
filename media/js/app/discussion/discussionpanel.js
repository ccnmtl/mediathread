var DiscussionPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    self.el = el;
    self.panel = panel;
    self.parentContainer = parent;
    self.space_owner = space_owner;
    self.form = jQuery(self.el).find("form.threaded_comments_form")[0];
    self.max_comment_length = parseInt(self.form.getAttribute('data-maxlength'), 10);
    
    djangosherd.storage.json_update(panel.context);

    jQuery(window).resize(function () {
        self.resize();
    });

    // hook up behaviors
    jQuery(window).bind('tinymce_init_instance', function (event, instance, param2) {
        self.onTinyMCEInitialize(instance);
    });
    
    self._bind(self.el, "td.panel-container", "panel_state_change", function () {
        self.onClosePanel(jQuery(this).hasClass("subpanel"));
    });

    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target' : panel.context.discussion.id + "-videoclipbox",
        'onPrepareCitation' : self.onPrepareCitation,
        'presentation' : "medium",
        'clipform': true,
        'winHeight': function () {
            var elt = jQuery(self.el).find("div.asset-view-published")[0];
            return jQuery(elt).height() -
                (jQuery(elt).find("div.annotation-title").height() +
                 jQuery(elt).find("div.asset-title").height() +
                 jQuery(elt).find("div.discussion-toolbar-row").height() + 15);
        }
    });
    self.citationView.decorateLinks(self.el.id);

    jQuery(this.form).bind('submit', {
        self : this
    }, this.submit);
    jQuery("input.cancel").bind('click', {
        self : this
    }, this.cancel);

    if (jQuery(this.form.elements.name).attr("value") === "") {
        jQuery(this.form.elements.name).attr("value", this.space_owner);
    }

    if (jQuery(this.form.elements.email).attr("value") === "") {
        jQuery(this.form.elements.email).attr("value", "null@example.com");
    }

    // decorate respond listeners
    jQuery('span.respond_prompt', self.el).click(function (evt) {
        self.open_respond(evt);
    });
    jQuery('span.edit_prompt', self.el).click(function (evt) {
        self.open_edit(evt);
    });

    // if there's only one comment, and i'm the author and the content is empty,
    // then open the edit form
    if (self.panel.context.discussion.thread.length === 1 &&
        self.panel.context.discussion.thread[0].author_username === self.space_owner &&
        self.panel.context.discussion.thread[0].content.length < 1) {
        var elt = jQuery(self.el).find("span.edit_prompt")[0];
        jQuery(elt).trigger("click");
    } else {
        self.hide_comment_form(false);
    }
    
    jQuery(window).trigger("resize");
};

DiscussionPanelHandler.prototype.isEditing = function () {
    var self = this;
    return jQuery(self.form).css("display") === "block";
};

DiscussionPanelHandler.prototype.isSubpanelOpen = function () {
    var self = this;
    return jQuery(self.el).find("td.panel-container.collection").hasClass("open");
};


DiscussionPanelHandler.prototype.onTinyMCEInitialize = function (instance) {
    var self = this;

    if (instance && instance.id === "id_comment" && !self.tinyMCE) {

        self.tinyMCE = instance;
        // Reset tinyMCE width to 100% via javascript. TinyMCE doesn't resize
        // properly
        // if this isn't completed AFTER instantiation
        jQuery('#id_comment_tbl').css('width', "100%");

        if (jQuery("#id_title").is(":visible")) {
            jQuery("#id_title").focus();
        } else {
            self.tinyMCE.focus();
        }
        
        self.collectionList = new CollectionList({
            'parent' : self.el,
            'template' : 'collection',
            'template_label' : "collection_table",
            'create_annotation_thumbs' : true,
            'space_owner' : self.space_owner,
            'citable': true,
            'owners': self.panel.owners,
            'view_callback': function () {
                var newAssets = self.collectionList.getAssets();
                self.tinyMCE.plugins.citation.decorateCitationAdders(newAssets);
            }
        });

        self.resize();
    }
};

DiscussionPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();
    
    jQuery(self.el).find('tr td.panel-container div.panel').css('height', (visible) + "px");

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

    visible += 45;
    jQuery(self.el).find('div.threadedcomments-container').css('height', (visible + 30) + "px");
    
    // Resize the collections box, subtracting its header elements
    jQuery(self.el).find('div.collection-assets').css('height', (visible - 50) + "px");
    
    // Resize the media display window
    jQuery(self.el).find('div.asset-view-published').css('height', (visible + 30) + "px");

    // For IE
    jQuery(self.el).find('tr.discussion-content-row').css('height', (visible) + "px");
    jQuery(self.el).find('tr.discussion-content-row').children('td.panhandle-stripe').css('height', (visible - 10) + "px");

};

DiscussionPanelHandler.prototype.onClosePanel = function () {
    var self = this;
    // close any outstanding citation windows
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    self.render();
};

DiscussionPanelHandler.prototype.render = function () {
    var self = this;
    
    // Give precedence to media view IF the subpanel is open and we're in readonly mode
    
    if (!self.isEditing() && self.isSubpanelOpen()) {
        jQuery(self.el).find(".panel-content").removeClass("fluid").addClass("fixed");
        jQuery(self.el).find("td.panel-container.collection").removeClass("fixed").addClass("fluid");
    } else {
        jQuery(self.el).find(".panel-content").removeClass("fixed").addClass("fluid");
        jQuery(self.el).find("td.panel-container.collection").removeClass("fluid").addClass("fixed");
    }
    
    jQuery(window).trigger("resize");
};

DiscussionPanelHandler.prototype.onPrepareCitation = function (target) {
    jQuery(target).parent().css("background", "none");
    
    var a = jQuery(target).parents("td.panel-container.collection");
    if (a && a.length) {
        PanelManager.openSubPanel(a[0]);
    }
};

DiscussionPanelHandler.prototype.set_comment_content = function (content) {
    var self = this;

    content = content || {
        comment : '<p></p>'
    };
    self.form.elements.comment.value = content.comment;
    self.form.elements.title.value = content.title || '';

    try {
        if (self.tinyMCE) {
            self.tinyMCE.setContent(content.comment);
        }
    } catch (e) {
        /*
         * IE totally SUX: throws some object error here. probably tinymce's
         * fault
         */
    }
};

DiscussionPanelHandler.prototype.open_respond = function (evt) {
    var self = this;

    jQuery(self.form).addClass("response");
    jQuery(self.form).children("h3").show();
    jQuery(self.form).find("input.cancel").show();

    var elt = evt.srcElement || evt.target || evt.originalTarget;
    self.form.elements.parent.value = elt.getAttribute("data-comment");
    self.form.elements['edit-id'].value = '';
    self.mode = 'post';

    var li = jQuery(elt).parents("li.comment-thread")[0];
    jQuery("div.respond_to_comment_form_div").hide();

    var comment_div = jQuery(li).children("div.comment")[0];
    self.open_comment_form(comment_div, true);
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
        self.set_comment_content(self.read({
            html : jQuery('#comment-' + id).get(0)
        }));

        var li = jQuery(elt).parents("li.comment-thread")[0];
        var myText = jQuery(li).find("div.threaded_comment_text")[0];
        jQuery(myText).hide();
        jQuery("div.respond_to_comment_form_div").hide(); // hide all toolbars until this one is saved or cancelled

        elt = jQuery(li).find("div.threaded_comment_header")[0];
        jQuery(self.form).find("input.cancel").show();

        self.open_comment_form(elt);

        if (self.panel.can_edit_title &&
            self.panel.root_comment_id.toString() === self.form.elements['edit-id'].value) {
            jQuery(self.form.elements.title).show();
        }
    }
};

DiscussionPanelHandler.prototype.open_comment_form = function (insertAfter, scroll) {
    var self = this;
    
    jQuery(self.el).find("div.threaded_comment_header").addClass("opacity_fiftypercent");
    jQuery(self.el).find("div.threaded_comment_text").addClass("opacity_fiftypercent");
    jQuery(self.el).find("div.threaded_comment_text").find("a.materialCitation").addClass("disabled");

    
    if (insertAfter) {
        self.tinyMCE = null;
        tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
        jQuery(self.form).insertAfter(insertAfter);
        
        ///makes it resizable--somewhat hacking tinyMCE.init()
        tinyMCE.settings.theme_advanced_statusbar_location = "bottom";
        tinyMCE.settings.theme_advanced_resize_vertical = true;

        tinyMCE.execCommand("mceAddControl", false, "id_comment");
    }
    jQuery(self.form).show('fast', function () {
        if (scroll) {
            var elt = jQuery(self.el).find("div.threadedcomments-container")[0];
            jQuery(elt).animate({
                scrollTop: jQuery(elt).scrollTop() + jQuery(self.form).parent().position().top + 20
            }, 500);
        }
    });
    

    // Switch to an Edit View
    // Unload any citations
    self.citationView.unload();
    jQuery(self.el).find("div.asset-view-published").hide();
    jQuery(self.el).find("td.panhandle-stripe div.label").html("Insert Selections");
    jQuery(self.el).find("div.collection-materials").show();
    self.render();
};

DiscussionPanelHandler.prototype.hide_comment_form = function () {
    var self = this;
    
    jQuery(self.el).find("div.threaded_comment_header").removeClass("opacity_fiftypercent");
    jQuery(self.el).find("div.threaded_comment_text").removeClass("opacity_fiftypercent");
    jQuery(self.el).find("div.threaded_comment_text").find("a.materialCitation").removeClass("disabled");
    
    // Switch to a readonly view
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    
    jQuery(self.form).hide('fast', function () {
        jQuery(self.form.elements.title).hide();
    
        // Switch to a readonly view
        jQuery(self.el).find("div.collection-materials").hide();
    
        jQuery(self.el).find("td.panhandle-stripe div.label")
                .html("View Inserted Selections");
        jQuery(self.el).find("div.asset-view-published").show();
        
        self.render();
    });
};

DiscussionPanelHandler.prototype._bind = function (parent, elementSelector,
        event, handler) {
    var elements = jQuery(parent).find(elementSelector);
    if (elements.length) {
        jQuery(elements[0]).bind(event, handler);
        return true;
    } else {
        return false;
    }
};

DiscussionPanelHandler.prototype.cancel = function (evt) {
    var self = evt.data.self;
    var elt = evt.srcElement || evt.target || evt.originalTarget;

    self.set_comment_content();// empty it
    self.hide_comment_form(true);
    jQuery("div.threaded_comment_text").show();
    jQuery("div.respond_to_comment_form_div").show();
};

DiscussionPanelHandler.prototype.submit = function (evt) {
    var self = evt.data.self;

    self.tinyMCE.save();
    evt.preventDefault();

    if (self.max_comment_length &&
        self.form.elements.comment.value.length > self.max_comment_length) {
        showMessage('Your comment is above the allowed maximum length of ' +
              self.max_comment_length +
              ' characters (which includes HTML).  Your comment is ' +
              self.form.elements.comment.value.length + ' characters long.');
        return;
    }

    var frm = jQuery(self.form);
    var form_val_array = frm.serializeArray();
    var info = {
        'edit-id' : self.form.elements['edit-id'].value
    };

    info.mode = ((info['edit-id'] === '') ? 'post' : 'update');
    switch (info.mode) {
    case 'update':
        info.url = MediaThread.urls['comment-edit'](info['edit-id']);
        break;
    case 'post':
        info.url = MediaThread.urls['comment-create']();
        break;
    }
    jQuery.ajax({
        type : 'POST',
        url : info.url,
        data : form_val_array, // default will serialize?
        dataType : 'html',
        success : self.oncomplete,
        error : self.onfail,
        context : {
            'self' : self,
            'form_val_array' : form_val_array,
            'info' : info
        }
    });
};

DiscussionPanelHandler.prototype.oncomplete = function (responseText, textStatus, xhr) {
    var self = this.self;
    var form_vals = {};
    for (var i = 0; i < this.form_val_array.length; i++) {
        form_vals[this.form_val_array[i].name] = this.form_val_array[i].value;
    }

    var res = self.parseResponse(xhr);
    if (xhr.status === 200 && !res.error) {
        if (res.comment_id) {
            // /1. insert new comment into DOM
            var new_obj = {
                'id' : res.comment_id,
                'comment' : res.comment || form_vals.comment,
                'name' : self.space_owner,
                'title' : res.title || ''
            };

            switch (this.info.mode) {
            case 'post':
                var parent_html = jQuery('#comment-' + form_vals.parent).get(0);
                if (!parent_html) {
                    parent_html = jQuery(self.el).find(
                            'div.threadedcomments-container')[0];
                }
                var ul = this.info.target = document.createElement('ul');
                ul.setAttribute('class', 'comment-thread');
                parent_html.appendChild(ul);
                ul.innerHTML = self.create(new_obj).text;
                // decorate respond listener
                jQuery('span.respond_prompt', ul).click(function (evt) {
                    self.open_respond(evt);
                });
                jQuery('span.edit_prompt', ul).click(function (evt) {
                    self.open_edit(evt);
                });
                break;
            case 'update':
                var comment_html = jQuery('#comment-' + form_vals['edit-id'])
                        .get(0);
                var comp = self.components(comment_html);
                self.update(new_obj, comment_html);
                this.info.target = comp.comment;
                break;
            }
            // 2. decorate citations
            self.citationView.decorateElementLinks(this.info.target);

            // 3. reset form and set new validation key
            self.set_comment_content();// empty it
            if (res.security_hash) {
                self.form.elements.timestamp.value = res.timestamp;
                self.form.elements.security_hash.value = res.security_hash;
            }
            
            // 4. hide form
            self.hide_comment_form(false);
            
            // 5. show respond/edit controls again
            jQuery("div.threaded_comment_text").show();
            jQuery("div.respond_to_comment_form_div").show();

            document.location = '#comment-' + res.comment_id;
        }
    } else {
        self.onfail(xhr, textStatus, res.error);
    }
};

DiscussionPanelHandler.prototype.onfail = function (xhr, textStatus, errorThrown) {
    showMessage("There was an error submitting your comment!  Please report this to the system administrator: " +
          errorThrown);
};

DiscussionPanelHandler.prototype.parseResponse = function (xhr) {
    var rv = {};
    var error_regex = /class="error"\s+>[^>]+>([\w ]+)<\/label/g;
    var error = error_regex.exec(xhr.responseText);
    if (error !== null) {
        rv.error = 'Required Fields: ';
        do {
            rv.error += error[1] + ';';
        } while ((error = error_regex.exec(xhr.responseText)) !== null);
    }
    var new_comment = String(xhr.responseText).match(/#comment-(\d+)/);
    if (new_comment !== null) {
        rv.comment_id = new_comment[1];
    }
    var timestamp = String(xhr.responseText).match(
            /name="timestamp"\s+value="(\d+)"/);
    if (timestamp !== null) {
        rv.timestamp = timestamp[1];
    }
    var security = String(xhr.responseText).match(
            /name="security_hash"\s+value="(\w+)"/);
    if (security !== null) {
        rv.security_hash = security[1];
    }
    var comment_text = String(xhr.responseText).match(
            /id="commentposted">((.|\n)*)<!--endposted/);
    if (comment_text !== null) {
        rv.comment = comment_text[1];
    }
    var comment_title = String(xhr.responseText).match(
            /id="commenttitle">(.+)<\/h2>/);
    if (comment_title !== null) {
        rv.title = comment_title[1];
    }

    return rv;
};

DiscussionPanelHandler.prototype.read = function (found_obj) {
    // found_obj = {html:<DOM>}
    var c = this.components(found_obj.html);
    var comment = c.comment.cloneNode(true);
    jQuery('.postupdate', comment).remove();
    return {
        'name' : c.author.firstChild.nodeValue,
        'comment' : comment.innerHTML,
        'title' : (c.title) ? c.title.innerHTML : '',
        'id' : String(c.top.id).substr(8), // comment- chopped
        'editable' : Boolean(c.edit_button),
        'base_comment' : !c.parent
    };
};

DiscussionPanelHandler.prototype.update = function (obj, html_dom, components) {
    var self = this;
    var success = 0;
    components = components || this.components(html_dom);

    if (obj.comment) {
        success += jQuery(components.comment).html(obj.comment).length;
    }
    if (obj.title) {
        success += jQuery(components.title).html(obj.title).length;
        if (!components.parent) { // if base_comment
            document.title = obj.title;
            jQuery(self.el).find("h1.discussion-title").html(obj.title);
        }
    }
    return success;
};

DiscussionPanelHandler.prototype.components = function (html_dom, create_obj) {
    return {
        'top' : html_dom,
        'comment' : jQuery('div.threaded_comment_text:first', html_dom).get(0),
        'title' : jQuery('div.threaded_comment_title', html_dom).get(0),
        'author' : jQuery('span.threaded_comment_author:first', html_dom)
                .get(0),
        'edit_button' : jQuery(
                'div.respond_to_comment_form_div:first span.edit_prompt',
                html_dom).get(0),
        'parent' : jQuery(html_dom).parents('li.comment-thread').get(0)
    };
};

DiscussionPanelHandler.prototype.create = function (obj, doc) {
    // microformat for a comment. SYNC with
    // templates/discussion/show_discussion.html
    // '<ul class="comment-thread">';
    // {{current_comment.id}}
    // {{current_comment.name}}
    // {{current_comment.comment|safe}}
    var html = '<li id="comment-{{current_comment.id}}"' +
        'class="comment-thread">' +
        '<div class="comment new-comment">' +
        ' <div class="threaded_comment_header">' +
        '<span class="threaded_comment_author">{{current_comment.name}}</span>&nbsp;' +
        'said:' +
        '<div class="respond_to_comment_form_div" id="respond_to_comment_form_div_id_{{current_comment.id}}">' +
        '<span class="respond_prompt comment_action" data-comment="{{current_comment.id}}" title="Click to show or hide the comment form">' +
        'Respond<!-- to comment {{current_comment.id}}: --></span>' +
        ' <span class="edit_prompt comment_action" data-comment="{{current_comment.id}}" title="Click to show or hide the edit comment form">Edit</span>' +
        '<div class="comment_form_space"></div>' +
        '</div>' +
        ' </div>' +
        '<div class="threaded_comment_title">{{current_comment.title}}</div>' +
        '<div class="threaded_comment_text">' +
        '{{current_comment.comment|safe}}' + '</div>' + '</div>' +
        '</li>';
    //'</ul>';

    var text = html.replace(/\{\{current_comment\.id\}\}/g, obj.id).replace(
            /\{\{current_comment.name\}\}/g, obj.name).replace(
            /\{\{current_comment.title\}\}/g, obj.title || '').replace(
            /\{\{current_comment\.comment\|safe\}\}/g, obj.comment);
    return {
        htmlID : 'comment-' + obj.id,
        object : obj,
        text : text
    };
};

DiscussionPanelHandler.prototype.readonly = function () {
    var self = this;

    // Unload any citations
    // Close any tinymce windows
    self.citationView.unload();

    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }

    if (!jQuery(self.form).is(":visible")) {
        // Switch to Edit View
        jQuery(self.el).find("td.panhandle-stripe div.label").html(
                "Insert Selections");
        jQuery(self.el).find("div.asset-view-published").hide();

        // Kill the asset view
        self.citationView.unload();

        jQuery(self.el).find("div.collection-materials").show();
        jQuery(self.el).find("input.project-title").show();
        jQuery(self.el).find("input.participants_toggle").show();

        self.tinyMCE.show();
    } else {
        // Switch to a readonly view
        jQuery(self.el).find("div.collection-materials").hide();

        jQuery(self.el).find("td.panhandle-stripe div.label").html(
                "View Inserted Selections");
        jQuery(self.el).find("div.asset-view-published").show();
    }

    jQuery(self.el).find("td.panel-container").toggleClass("media collection");
    jQuery(self.el).find("td.panhandle-stripe").toggleClass("media collection");
    jQuery(self.el).find("div.pantab").toggleClass("media collection");

    jQuery(window).trigger("resize");

    return false;
};
