function AjaxCommentForm(options) {
    this.el = options.el;
    this.form = options.form;
    this.parent = options.parent;
    this.username = options.space_owner;
    this.citationView = options.citationView;
    this.max_comment_length = parseInt(this.form.getAttribute('data-maxlength'), 10);

    this.capabilities = {
        'edit': jQuery('.capabilities .can-edit').length
    };
    
    this.post_comment_url = String(this.form.action);

    jQuery(this.form).bind('submit', {self: this}, this.submit);
    jQuery("input.cancel").bind('click', { self: this }, this.cancel);
    
    if (jQuery(this.form.elements.name).attr("value") === "") {
        jQuery(this.form.elements.name).attr("value", this.username);
    }
    
    if (jQuery(this.form.elements.email).attr("value") === "") {
        jQuery(this.form.elements.email).attr("value", "null@example.com");
    }
}

AjaxCommentForm.prototype.cancel = function (evt) {
    var self = evt.data.self;
    var elt = evt.srcElement || evt.target || evt.originalTarget;
    
    self.parent.set_comment_content();//empty it
    self.parent.hide_comment_form();
    jQuery("div.threaded_comment_text").show();
    jQuery("div.respond_to_comment_form_div").show();
};

AjaxCommentForm.prototype.submit = function (evt) {
    var self = evt.data.self;
    
    tinyMCE.triggerSave();
    evt.preventDefault();
    
    if (self.max_comment_length &&
        self.form.elements.comment.value.length > self.max_comment_length) {
        alert('Your comment is above the allowed maximum length of ' + self.max_comment_length + ' characters (which includes HTML).  Your comment is ' + self.form.elements.comment.value.length + ' characters long.');
        return;
    }

    var frm = jQuery(self.form);
    var form_val_array = frm.serializeArray();
    var info = {'edit-id': self.form.elements['edit-id'].value};

    info.mode = ((info['edit-id'] === '') ? 'post' : 'update');
    switch (info.mode) {
    case 'update':
        info.url = MediaThread.urls['edit-comment'](info['edit-id']);
        break;
    case 'post':
        info.url = MediaThread.urls['create-comment']();
        break;
    }
    jQuery.ajax({
        type: 'POST',
        url: info.url,
        data: form_val_array,//default will serialize?
        dataType: 'html',
        success: self.oncomplete,
        error: self.onfail,
        context: {'self': self, 'form_val_array': form_val_array, 'info': info}
    });
};

AjaxCommentForm.prototype.oncomplete = function (responseText, textStatus, xhr) {
    var self = this.self;
    var form_vals = {};
    for (var i = 0; i < this.form_val_array.length; i++) {
        form_vals[this.form_val_array[i].name] = this.form_val_array[i].value;
    }

    var res = self.parseResponse(xhr);
    if (xhr.status === 200  && !res.error) {
        if (res.comment_id) {
            ///1. insert new comment into DOM
            var new_obj = {
                'id': res.comment_id,
                'comment': res.comment || form_vals.comment,
                'name': self.username,
                'title': res.title || ''
            };
            
            switch (this.info.mode) {
            case 'post':
                var parent_html = jQuery('#comment-' + form_vals.parent).get(0);
                if (!parent_html) {
                    parent_html = self.el; //jQuery(self.el).find('div.threadedcomments-container')[0],
                }
                var ul = this.info.target = document.createElement('ul');
                ul.setAttribute('class', 'comment-thread');
                parent_html.appendChild(ul);
                ul.innerHTML = self.create(new_obj).text;
                //decorate respond listener
                jQuery('span.respond_prompt', ul).click(function (evt) { self.parent.open_respond(evt); });
                jQuery('span.edit_prompt', ul).click(function (evt) { self.parent.open_edit(evt); });
                break;
            case 'update':
                var comment_html = jQuery('#comment-' + form_vals['edit-id']).get(0);
                var comp = self.components(comment_html);
                self.update(new_obj, comment_html);
                this.info.target = comp.comment;
                break;
            }
            ///2. decorate citations
            self.citationView.decorateLinks(this.info.target);

            ///3. reset form and set new validation key
            self.parent.set_comment_content();//empty it
            if (res.security_hash) {
                self.form.elements.timestamp.value = res.timestamp;
                self.form.elements.security_hash.value = res.security_hash;
            }
            ///4. hide form
            self.parent.hide_comment_form();
            ///5. show respond/edit controls again
            jQuery("div.threaded_comment_text").show();
            jQuery("div.respond_to_comment_form_div").show();
            document.location = '#comment-' + res.comment_id;
        }
    } else {
        self.onfail(xhr, textStatus, res.error);
    }
};

AjaxCommentForm.prototype.onfail = function (xhr, textStatus, errorThrown) {
    alert("There was an error submitting your comment!  Please report this to the system administrator: " + errorThrown);
};

AjaxCommentForm.prototype.parseResponse = function (xhr) {
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
    var timestamp = String(xhr.responseText).match(/name="timestamp"\s+value="(\d+)"/);
    if (timestamp !== null) {
        rv.timestamp = timestamp[1];
    }
    var security = String(xhr.responseText).match(/name="security_hash"\s+value="(\w+)"/);
    if (security !== null) {
        rv.security_hash = security[1];
    }
    var comment_text = String(xhr.responseText).match(/id="commentposted">((.|\n)*)<!--endposted/);
    if (comment_text !== null) {
        rv.comment = comment_text[1];
    }
    var comment_title = String(xhr.responseText).match(/id="commenttitle">(.+)<\/h2>/);
    if (comment_title !== null) {
        rv.title = comment_title[1];
    }

    return rv;
};

AjaxCommentForm.prototype.read = function (found_obj) {
    //found_obj = {html:<DOM>}
    var c = this.components(found_obj.html);
    var comment = c.comment.cloneNode(true);
    jQuery('.postupdate', comment).remove();
    return {
        'name': c.author.firstChild.nodeValue,
        'comment': comment.innerHTML,
        'title': (c.title) ? c.title.innerHTML : '',
        'id': String(c.top.id).substr(8), //comment- chopped
        'editable': Boolean(c.edit_button),
        'base_comment': !c.parent
    };
};

AjaxCommentForm.prototype.update = function (obj, html_dom, components) {
    var success = 0;
    components = components || this.components(html_dom);

    if (obj.comment) {
        success += jQuery(components.comment).html(obj.comment).length;
    }
    if (obj.title) {
        success += jQuery(components.title).html(obj.title).length;
        if (!components.parent) { //if base_comment
            jQuery('#discussion-subject-title').html(obj.title);
            document.title = 'Discussion of ' + obj.title;
        }
    }
    return success;
};

AjaxCommentForm.prototype.components = function (html_dom, create_obj) {
    return {'top': html_dom,
            'comment': jQuery('div.threaded_comment_text:first', html_dom).get(0),
            'title': jQuery('div.threaded_comment_title', html_dom).get(0),
            'author': jQuery('span.threaded_comment_author:first', html_dom).get(0),
            'edit_button': jQuery('div.respond_to_comment_form_div:first span.edit_prompt', html_dom).get(0),
            'parent': jQuery(html_dom).parents('li.comment-thread').get(0)
    };
};

AjaxCommentForm.prototype.create = function (obj, doc) {
    //microformat for a comment.  SYNC with templates/discussion/show_discussion.html
    // '<ul class="comment-thread">';
    //{{current_comment.id}}
    //{{current_comment.name}}
    //{{current_comment.comment|safe}}
    var html = '<li id="comment-{{current_comment.id}}"'
        +          'class="comment-thread">'
        + '<div class="comment new-comment">'
        + ' <div class="threaded_comment_header">'
        +    '<span class="threaded_comment_author">{{current_comment.name}}</span>&nbsp;'
        +      '<a class="comment-anchor" href="#comment-{{current_comment.id}}">said:</a>'
        +    '<div class="respond_to_comment_form_div" id="respond_to_comment_form_div_id_{{current_comment.id}}">'
        +      '<span class="respond_prompt comment_action" data-comment="{{current_comment.id}}" title="Click to show or hide the comment form">'
        +        'Respond<!-- to comment {{current_comment.id}}: --></span>'
        +    ' <span class="edit_prompt comment_action" data-comment="{{current_comment.id}}" title="Click to show or hide the edit comment form">Edit</span>'
        +      '<div class="comment_form_space"></div>'
        +    '</div>'
        + ' </div>'
        + '<div class="threaded_comment_title">{{current_comment.title}}</div>'
        +    '<div class="threaded_comment_text">'
        +      '{{current_comment.comment|safe}}'
        +    '</div>'
        + '</div>'
        +'</li>';
    '</ul>';
    
    var text = html
    .replace(/\{\{current_comment\.id\}\}/g, obj.id)
    .replace(/\{\{current_comment.name\}\}/g, obj.name)
    .replace(/\{\{current_comment.title\}\}/g, obj.title||'')
    .replace(/\{\{current_comment\.comment\|safe\}\}/g, obj.comment);
    return { htmlID: 'comment-' + obj.id,
             object: obj,
             text: text
    };
};