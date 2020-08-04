
/* global CitationView: true, djangosherd: true, CollectionList: true */
/* global MediaThread: true */
/* global tinymce: true, tinymceSettings: true, showMessage: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

var DiscussionPanelHandler = function(el, $parent, panel, space_owner) {
    var self = this;
    self.el = el;
    self.$el = jQuery(self.el);
    self.panel = panel;
    self.$parentContainer = $parent;
    self.space_owner = space_owner;
    self.form = self.$el.find('form.threaded_comments_form')[0];
    self.max_comment_length = 3000;

    djangosherd.storage.json_update(panel.context);

    // hook up behaviors

    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': panel.context.discussion.id + '-videoclipbox',
        'presentation': 'default',
        'clipform': true,
        'winHeight': function() {
            var elt = self.$el.find('div.asset-view-published')[0];
            return jQuery(elt).height() -
                (jQuery(elt).find('div.annotation-title').height() +
                 jQuery(elt).find('div.asset-title').height() + 15);
        }
    });
    self.citationView.decorateLinks(self.$el.attr('id'));

    jQuery(this.form).bind('submit', {
        self: this
    }, this.submit);
    jQuery('.btn.cancel').bind('click', {
        self: this
    }, this.cancel);

    if (jQuery(this.form.elements.name).attr('value') === '') {
        jQuery(this.form.elements.name).attr('value', this.space_owner);
    }

    if (jQuery(this.form.elements.email).attr('value') === '') {
        jQuery(this.form.elements.email).attr('value', 'null@example.com');
    }

    // decorate respond listeners
    jQuery('.respond_prompt', self.el).click(function(evt) {
        self.open_respond(evt);
    });
    jQuery('.edit_prompt', self.el).click(function(evt) {
        self.open_edit(evt);
    });

    // if there's only one comment, and i'm the author and the content is empty
    // then open the edit form
    if (self.panel.context.discussion.thread.length === 1 &&
        self.panel.context.discussion.thread[0].author_username ===
            self.space_owner &&
        self.panel.context.discussion.thread[0].content.length < 1) {
        var elt = self.$el.find('.edit_prompt')[0];
        jQuery(elt).trigger('click');
    } else {
        self.hide_comment_form(false);
    }
};

DiscussionPanelHandler.prototype.isEditing = function() {
    var self = this;
    return jQuery(self.form).css('display') === 'block';
};

DiscussionPanelHandler.prototype.onTinyMCEInitialize = function(instance) {
    var self = this;

    if (instance && instance.id === 'id_comment' && !self.tinymce) {

        self.tinymce = instance;
        // Reset tinymce width to 100% via javascript. TinyMCE doesn't resize
        // properly
        // if this isn't completed AFTER instantiation
        jQuery('#id_comment_tbl').css('width', '100%');

        self.tinymce.focus();

        self.collectionList = new CollectionList({
            '$parent': self.$el,
            'template': 'collection',
            'template_label': 'collection_table',
            'create_annotation_thumbs': true,
            'space_owner': self.space_owner,
            'citable': true,
            'owners': self.panel.owners,
            'view_callback': function() {
                var newAssets = self.collectionList.getAssets();
                self.tinymce.plugins.citation.decorateCitationAdders(
                    newAssets);

                // Fired by CollectionList & AnnotationList
                jQuery(window).bind('assets.refresh', {'self': self},
                    function(event, html) {
                        var newAssets = self.collectionList.getAssets();
                        self.tinymce.plugins.citation.decorateCitationAdders(
                            newAssets);
                    });
            }
        });
    }
};

DiscussionPanelHandler.prototype.onClosePanel = function() {
    // close any outstanding citation windows
    if (this.tinymce) {
        this.tinymce.plugins.editorwindow._closeWindow();
    }
};

DiscussionPanelHandler.prototype.set_comment_content = function(content) {
    var self = this;

    content = content || {
        comment: '<p></p>'
    };
    self.form.elements.comment.value = content.comment;

    try {
        if (self.tinymce) {
            self.tinymce.setContent(content.comment);
        }
    } catch (e) {
        /*
         * IE totally SUX: throws some object error here. probably tinymce's
         * fault
         */
    }
};

DiscussionPanelHandler.prototype.open_respond = function(evt) {
    var self = this;

    jQuery(self.form).addClass('response');
    jQuery(self.form).children('h3').show();
    jQuery(self.form).find('.btn.cancel').show();

    var elt = evt.srcElement || evt.target || evt.originalTarget;
    self.form.elements.parent.value = elt.getAttribute('data-comment');
    self.form.elements['edit-id'].value = '';
    self.mode = 'post';

    var li = jQuery(elt).parents('li.comment-thread')[0];
    jQuery('div.respond_to_comment_form_div').hide();

    var comment_div = jQuery(li).children('div.comment')[0];
    self.open_comment_form(comment_div, true);
};

DiscussionPanelHandler.prototype.open_edit = function(evt, focus) {
    var self = this;

    jQuery(self.form).removeClass('response');
    jQuery(self.form).children('h3').hide();

    if (evt === undefined) {
        self.form.elements.parent.value = '';
        self.open_comment_form();
    } else {
        var elt = evt.srcElement || evt.target || evt.originalTarget;

        var id = elt.getAttribute('data-comment');
        self.form.elements['edit-id'].value = id;
        self.set_comment_content(self.read({
            html: jQuery('#comment-' + id).get(0)
        }));

        var li = jQuery(elt).parents('li.comment-thread')[0];
        var myText = jQuery(li).find('div.threaded_comment_text')[0];
        jQuery(myText).hide();
        // hide all toolbars until this one is saved or cancelled
        jQuery('div.respond_to_comment_form_div').hide();

        elt = jQuery(li).find('div.threaded_comment_header')[0];
        jQuery(self.form).find('.btn.cancel').show();

        self.open_comment_form(elt);
    }
};

DiscussionPanelHandler.prototype.open_comment_form = function(insertAfter,
    scroll) {
    var self = this;

    if (insertAfter) {
        self.tinymce = null;
        tinymce.execCommand('mceRemoveEditor', false, 'id_comment');
        jQuery(self.form).insertAfter(insertAfter);

        tinymce.settings = jQuery.extend(tinymceSettings, {
            init_instance_callback: function(editor) {
                self.onTinyMCEInitialize(editor);
            },
            height: 400
        });

        tinymce.execCommand('mceAddEditor', true, 'id_comment');
    }

    jQuery(self.form).show('fast', function() {
        var top = jQuery('.threaded_comments_form').position().top - 20;
        jQuery('html, body').animate({scrollTop: top}, 200);
    });

    // Switch to an Edit View
    // Unload any citations
    self.citationView.unload();
    self.$el.find('div.asset-view-published').hide();
    self.$el.find('div.collection-materials').show();
};

DiscussionPanelHandler.prototype.hide_comment_form = function() {
    var self = this;

    self.$el.find('div.threaded_comment_header')
        .removeClass('opacity_fiftypercent');
    self.$el.find('div.threaded_comment_text')
        .removeClass('opacity_fiftypercent');
    self.$el.find('div.threaded_comment_text')
        .find('a.materialCitation').removeClass('disabled');

    // Switch to a readonly view
    if (self.tinymce) {
        self.tinymce.plugins.editorwindow._closeWindow();
    }

    jQuery(self.form).hide('fast', function() {
        // Switch to a readonly view
        self.$el.find('div.collection-materials').hide();

        self.$el.find('div.asset-view-published').show();
    });
};

DiscussionPanelHandler.prototype._bind = function($parent, elementSelector,
    event, handler) {
    var elements = $parent.find(elementSelector);
    if (elements.length) {
        jQuery(elements[0]).bind(event, handler);
        return true;
    } else {
        return false;
    }
};

DiscussionPanelHandler.prototype.cancel = function(evt) {
    var self = evt.data.self;

    self.set_comment_content();// empty it
    self.hide_comment_form(true);
    jQuery('div.threaded_comment_text').show();
    jQuery('div.respond_to_comment_form_div').show();
};

DiscussionPanelHandler.prototype.submit = function(evt) {
    var self = evt.data.self;

    self.tinymce.save();
    evt.preventDefault();

    if (self.max_comment_length &&
        self.form.elements.comment.value.length > self.max_comment_length) {
        showMessage('Your comment is above the allowed maximum length of ' +
              self.max_comment_length +
              ' characters (which includes HTML).  Your comment is ' +
              self.form.elements.comment.value.length + ' characters long.');
        return;
    }

    var serializedForm = jQuery(self.form).serializeArray();

    var info = {
        'edit-id': self.form.elements['edit-id'].value
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
        type: 'POST',
        url: info.url,
        data: serializedForm,
        dataType: 'html',
        success: self.oncomplete,
        error: self.onfail,
        context: {
            'self': self,
            'form_val_array': serializedForm,
            'info': info
        }
    });
};

DiscussionPanelHandler.prototype.oncomplete = function(responseText,
    textStatus,
    xhr) {
    var self = this.self;
    var form_vals = {};
    for (var i = 0; i < this.form_val_array.length; i++) {
        form_vals[this.form_val_array[i].name] = this.form_val_array[i].value;
    }

    var res = self.parseResponse(xhr);
    if (xhr.status === 200 && !res.error) {
        if (res.comment_id) {
            // /1. insert new comment into DOM
            var newObj = {
                'id': res.comment_id,
                'comment': res.comment || form_vals.comment,
                'name': self.space_owner,
                'timestamp': new Date().toLocaleString()
            };

            switch (this.info.mode) {
            case 'post':
                var parentHtml = jQuery(
                    '#comment-' + form_vals.parent).get(0);
                if (!parentHtml) {
                    parentHtml = self.$el.find(
                        'div.threadedcomments-container')[0];
                }
                var ul = this.info.target = document.createElement('ul');
                ul.setAttribute('class', 'comment-thread');
                parentHtml.appendChild(ul);
                /* eslint-disable no-unsafe-innerhtml/no-unsafe-innerhtml */
                ul.innerHTML = self.create(newObj).text;
                /* eslint-enable no-unsafe-innerhtml/no-unsafe-innerhtml */

                // decorate respond listener
                jQuery('.respond_prompt', ul).click(function(evt) {
                    self.open_respond(evt);
                });
                jQuery('.edit_prompt', ul).click(function(evt) {
                    self.open_edit(evt);
                });
                break;
            case 'update':
                var comment_html = jQuery(
                    '#comment-' + form_vals['edit-id']).get(0);
                var comp = self.components(comment_html);
                self.update(newObj, comment_html);
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
            jQuery('div.threaded_comment_text').show();
            jQuery('div.respond_to_comment_form_div').show();

            // 6. scroll to the updated or new element
            var top = jQuery('li#comment-' + res.comment_id).position().top;
            jQuery('html, body').animate({
                scrollTop: top
            }, 200);
        }
    } else {
        self.onfail(xhr, textStatus, res.error);
    }
};

DiscussionPanelHandler.prototype.onfail = function(xhr, textStatus, error) {
    showMessage('There was an error submitting your comment! ' +
                'Please report this to the system administrator: ' +
                error);
};

DiscussionPanelHandler.prototype.parseResponse = function(xhr) {
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

    return rv;
};

DiscussionPanelHandler.prototype.read = function(found_obj) {
    // found_obj = {html:<DOM>}
    var c = this.components(found_obj.html);
    var comment = c.comment.cloneNode(true);
    jQuery('.postupdate', comment).remove();
    return {
        'name': c.author.firstChild.nodeValue,
        'comment': comment.innerHTML,
        'id': String(c.top.id).substr(8), // comment- chopped
        'editable': Boolean(c.edit_button),
        'base_comment': !c.parent
    };
};

DiscussionPanelHandler.prototype.update = function(obj, html_dom, components) {
    var success = 0;
    components = components || this.components(html_dom);

    if (obj.comment) {
        success += jQuery(components.comment).html(obj.comment).length;
    }
    return success;
};

DiscussionPanelHandler.prototype.components = function(html_dom, create_obj) {
    return {
        'top': html_dom,
        'comment': jQuery('.threaded_comment_text:first', html_dom).get(0),
        'author': jQuery('.threaded_comment_author:first', html_dom)
            .get(0),
        'edit_button': jQuery(
            '.respond_to_comment_form_div:first .edit_prompt',
            html_dom).get(0),
        'parent': jQuery(html_dom).parents('li.comment-thread').get(0)
    };
};

DiscussionPanelHandler.prototype.create = function(obj, doc) {
    var html =
        '<li id="comment-{{current_comment.id}}" class="comment-thread">' +
        '<div class="comment new-comment mb-5">' +
        '<div class="threaded_comment_header">' +
        '    <div class="threaded_comment_author">' +
        '        {{current_comment.name}}' +
        '    </div>' +
        '</div>' +
        '<div class="threaded_comment_text mt-3">' +
        '    {{current_comment.comment|safe}}' +
        '</div>' +
        '<div class="respond_to_comment_form_div">' +
        '    <span class="comment-date text-muted">' +
        '        {{current_comment.timestamp}}' +
        '    </span>' +
        '    <span class="text-separator"></span>' +
        '    <button class="edit_prompt comment_action btn btn-link pl-0"' +
        '        data-comment="{{current_comment.id}}"' +
        '        title="Click to edit this comment">' +
        '        Edit' +
        '    </button>' +
        '    <span class="text-separator"></span>' +
        '    <button class="respond_prompt comment_action btn btn-link pl-0"' +
        '        data-comment="{{current_comment.id}}"' +
        '        title="Click to respond to this comment">' +
        '        Reply' +
        '    </button>' +
        '</div>' +
        '</li>';

    var text = html.replace(/\{\{current_comment\.id\}\}/g, obj.id).replace(
        /\{\{current_comment.name\}\}/g, obj.name).replace(
        /\{\{current_comment.title\}\}/g, obj.title || '').replace(
        /\{\{current_comment.timestamp\}\}/g, obj.timestamp || '').replace(
        /\{\{current_comment\.comment\|safe\}\}/g, obj.comment);
    return {
        htmlID: 'comment-' + obj.id,
        object: obj,
        text: text
    };
};

DiscussionPanelHandler.prototype.readonly = function() {
    var self = this;

    // Unload any citations
    // Close any tinymce windows
    self.citationView.unload();

    if (self.tinymce) {
        self.tinymce.plugins.editorwindow._closeWindow();
    }

    if (!jQuery(self.form).is(':visible')) {
        // Switch to Edit View
        self.$el.find('div.asset-view-published').hide();

        // Kill the asset view
        self.citationView.unload();

        self.$el.find('div.collection-materials').show();
        self.$el.find('.participants_toggle').show();

        self.tinymce.show();
    } else {
        // Switch to a readonly view
        self.$el.find('div.collection-materials').hide();

        self.$el.find('div.asset-view-published').show();
    }

    return false;
};
