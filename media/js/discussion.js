jQuery(function discussion_init() {
    var next_response_loc = false,
        frm = jQuery('#comment-form').get(0),
        commenter,
        mode='post';

    function open_respond(evt) {
        var respond = evt.target; 
        frm.elements['parent'].value = respond.getAttribute("data-comment"); 
        frm.elements['edit-id'].value = '';
        open_comment_form(respond);
        if (mode=='update') {
            set_comment_content();//empty it
        }
        mode='post';
    }
    function open_edit(evt,focus) {
        mode='update';
        var edit = evt.target;
        frm.elements['parent'].value = '';
        var id = frm.elements['edit-id'].value = edit.getAttribute("data-comment");

        open_comment_form(edit,focus);

        set_comment_content(commenter.read({html:jQuery('#comment-'+id).get(0)}));
    }

    function comment_form_space(button) {
        return jQuery('div.comment_form_space',button.parentNode).get(0);
    }

    function set_comment_content(content) {
        content = content || {comment:'<p></p>'};
        frm.elements['comment'].value = content.comment;
        frm.elements['title'].value = content.title || '';
        var action = (content.title||content.base_comment) ? 'show' : 'hide';
        jQuery('.formtitle')[action]();
        try {
            tinyMCE.execInstanceCommand('id_comment','mceSetContent',false,content.comment,false);
        }catch(e) {/*IE totally SUX: throws some object error here. probably tinymce's fault */}
    }
    set_comment_content();

    function open_comment_form(evt_target,focus) {
        if (!next_response_loc) {
	    next_response_loc = evt_target;
            comment_form_space(evt_target).appendChild(frm);
            jQuery(frm).show();
            jQuery('#id_comment').focus();

            ///makes it resizable--somewhat hacking tinyMCE.init()
            tinyMCE.settings.theme_advanced_statusbar_location="bottom";

            tinyMCE.execCommand("mceAddControl", false, "id_comment");
            jQuery(evt_target).addClass('control-open');
        } else { //actually, CLOSE form
	    if (next_response_loc == evt_target) {
		next_response_loc = false;
                jQuery(evt_target).removeClass('control-open');
	    } else {
                next_response_loc = evt_target;
                jQuery('span.control-open').removeClass('control-open');
                jQuery(evt_target).addClass('control-open');
	    }
            tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
            tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
        }
        if (focus && focus.select) {
            var focused = false;
            tinyMCE.onAddEditor.add(function(manager, ed) {
                if (!focused) {
                    setTimeout(function() {
                        focus.select();
                        focus.focus();
                    },1000);
                }
                focused = true;
            });
        }
    }

    function hide_comment_form() {
        next_response_loc = false;
        tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
        tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
        jQuery('span.control-open').removeClass('control-open');
    }

    jQuery('.respond_prompt').click(open_respond);
    jQuery('.edit_prompt').click(open_edit);

    tinyMCE.onRemoveEditor.add(function(manager, ed) {
        //logDebug("third focus");
	if (next_response_loc) {
            comment_form_space(next_response_loc).appendChild(document.forms[0]);
            tinyMCE.execCommand("mceAddControl", false, "id_comment");
	} else {
            jQuery('#comment-form').hide();
            jQuery('#asset_browse_col').parent().removeClass('annotation-embedding');
	}
    });
    tinyMCE.onAddEditor.add(function(manager, ed) {
        ed.onInit.add(function(editor) {
            tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
            jQuery('#asset_browse_col').parent().addClass('annotation-embedding');
        });
    });

function AjaxComment(form) {
    this.form = form;
    this.username = jQuery('#logged_in_name').text();

    this.max_comment_length = parseInt(form.getAttribute('data-maxlength'));

    this.capabilities = {
        'edit': jQuery('.capabilities .can-edit').length
    }

    this.update_comment_url = '/discussion/comment/{id}';
    this.post_comment_url = String(this.form.action);

    jQuery(form).bind('submit',{self:this},this.submit);
}

AjaxComment.prototype.submit = function(evt) {    
    var self = evt.data.self;
    tinyMCE.triggerSave();
    evt.preventDefault();

    if (self.max_comment_length &&
        self.form.elements['comment'].value.length > self.max_comment_length) {
        alert('Your comment is above the allowed maximum length of '+self.max_comment_length+' characters (which includes HTML).  Your comment is '+self.form.elements['comment'].value.length+' characters long.');
        return;
    }

    var frm = jQuery(self.form);
    form_val_array = frm.serializeArray();
    
    var info = {'edit-id':self.form.elements['edit-id'].value};

    info['mode'] = ((info['edit-id']=='') ?'post':'update');
    switch (info['mode']) {
    case 'update':
        info['url'] = self.update_comment_url.replace('{id}',info['edit-id']); break;
    case 'post':
        info['url'] = self.post_comment_url; break;
    }
    jQuery.ajax({
        type: 'POST',
        url: info.url,
        data: form_val_array,//default will serialize?
        dataType: 'html',
        success: self.oncomplete,
        error: self.onfail,
        context: {'self':self,'form_val_array':form_val_array,'info':info}
    });
}

AjaxComment.prototype.oncomplete = function(responseText, textStatus, xhr) {
    var self = this.self;
    var form_vals = {};
    for (var i=0;i<this.form_val_array.length;i++) {
        form_vals[this.form_val_array[i].name] = this.form_val_array[i].value;
    }

    var res = self.parseResponse(xhr);
    if (xhr.status ==200  && !res.error) {
        if (res.comment_id) {
            ///1. insert new comment into DOM
            var new_obj = {
                'id':res.comment_id,
                'comment':res.comment || form_vals.comment,
                'name':self.username,
                'title':res.title || ''
            };
            switch(this.info.mode) {
            case 'post':
                var parent_html = jQuery('#comment-' +form_vals['parent']).get(0);
                var ul = this.info.target = document.createElement('ul');
                ul.setAttribute('class','comment-thread');
                parent_html.appendChild(ul);
                ul.innerHTML = self.create(new_obj).text;
                //decorate respond listener
                jQuery('span.respond_prompt',ul).click(open_respond);
                jQuery('span.edit_prompt',ul).click(open_edit);
                break;
            case 'update':
                var comment_html = jQuery('#comment-' +form_vals['edit-id']).get(0);
                var comp = self.components(comment_html);
                self.update(new_obj, comment_html);
                this.info.target = comp.comment;
                break;
            }
            ///2. decorate citations
            DjangoSherd_decorate_citations( this.info.target);

            ///3. reset form and set new validation key
            set_comment_content();//empty it
            if (res.security_hash) {
                frm.elements['timestamp'].value = res.timestamp;
                frm.elements['security_hash'].value = res.security_hash;
            }
            ///4. hide form
            hide_comment_form();
            document.location = '#comment-'+res.comment_id;
        }
    } else {
        self.onfail(xhr, textStatus, res.error);
    }
}

AjaxComment.prototype.onfail = function(xhr, textStatus, errorThrown) {
    alert("There was an error submitting your comment!  Please report this to the system administrator: "+errorThrown);
    console.log('error:'+errorThrown);
    console.log(xhr);    
}

AjaxComment.prototype.parseResponse = function(xhr) {
    var rv = {};
    var error_regex = /class="error"\s+>[^>]+>([\w ]+)<\/label/g;
    var error = error_regex.exec(xhr.responseText);
    if (error != null) {
        rv["error"] = 'Required Fields: ';
        do {
            rv["error"]+= error[1] + ';';
        } while ((error = error_regex.exec(xhr.responseText)) != null);
    }
    var new_comment = String(xhr.responseText).match(/#comment-(\d+)/);
    if (new_comment != null) {
        rv["comment_id"] = new_comment[1];
    }
    var timestamp = String(xhr.responseText).match(/name="timestamp"\s+value="(\d+)"/);
    if (timestamp != null) {
        rv["timestamp"] = timestamp[1];
    }
    var security = String(xhr.responseText).match(/name="security_hash"\s+value="(\w+)"/);
    if (security != null) {
        rv["security_hash"] = security[1];
    }
    var comment_text = String(xhr.responseText).match(/id="commentposted">((.|\n)*)<!--endposted/)
    if (comment_text != null) {
        rv["comment"] = comment_text[1];
    }
    var comment_title = String(xhr.responseText).match(/id="commenttitle">(.+)<\/h2>/);
    if (comment_title != null) {
        rv["title"] = comment_title[1];
    }

    return rv;
}

AjaxComment.prototype.read = function(found_obj) {
    //found_obj = {html:<DOM>}
    var c = this.components(found_obj.html);
    var comment = c.comment.cloneNode(true);
    jQuery('.postupdate',comment).remove();
    return {
        'name':c.author.firstChild.nodeValue,
        'comment':comment.innerHTML,
        'title':(c.title)?c.title.innerHTML:'',
        'id':String(c.top.id).substr(8),//comment- chopped
        'editable':Boolean(c.edit_button),
        'base_comment':!c.parent
    }
}

AjaxComment.prototype.update = function(obj,html_dom,components) {
    var success = 0;
    components = components || this.components(html_dom);

    if (obj.comment) {
        success+=jQuery(components.comment).html(obj.comment).length;
    }
    if (obj.title) {
        success+=jQuery(components.title).html(obj.title).length;
        if (! components.parent) {//if base_comment
            jQuery('#discussion-subject-title').html(obj.title);
            document.title = 'Discussion of '+obj.title;
        }
    }
    return success;
}

AjaxComment.prototype.components = function(html_dom,create_obj) {
    return {'top':html_dom,
            'comment':jQuery('div.threaded_comment_text:first',html_dom).get(0),
            'title':jQuery('div.threaded_comment_title',html_dom).get(0),
            'author':jQuery('span.threaded_comment_author:first',html_dom).get(0),
            'edit_button':jQuery('div.respond_to_comment_form_div:first span.edit_prompt',html_dom).get(0),
            'parent':jQuery(html_dom).parents('li.comment-thread').get(0)
           }
}

AjaxComment.prototype.create = function(obj,doc) {
    //microformat for a comment.  SYNC with templates/discussion/show_discussion.html

    '<ul class="comment-thread">';
    //{{current_comment.id}}
    //{{current_comment.name}}
    //{{current_comment.comment|safe}}
    var html = '<li id="comment-{{current_comment.id}}"'
        +          'class="comment-thread">'
        + '<div class="comment new-comment">'
        + ' <div class="threaded_comment_header">'
        +    '<span class="threaded_comment_author">{{current_comment.name}}</span>'
        +      '<a class="comment-anchor" href="#comment-{{current_comment.id}}">said:</a>'
        + ' </div>'
        + '<div class="threaded_comment_title">{{current_comment.title}}</div>'
        +    '<div class="threaded_comment_text">'
        +      '{{current_comment.comment|safe}}'
        +    '</div>'
        +    '<div class="respond_to_comment_form_div" id="respond_to_comment_form_div_id_{{current_comment.id}}">'
        +      '<span class="respond_prompt comment_action" data-comment="{{current_comment.id}}" title="Click to show or hide the comment form">'
        +        'Respond<!-- to comment {{current_comment.id}}: --></span>'
        +    ' <span class="edit_prompt comment_action" data-comment="{{current_comment.id}}" title="Click to show or hide the edit comment form">Edit</span>'
        +      '<div class="comment_form_space"></div>'
        +    '</div>'
        + '</div>'
        +'</li>';
    '</ul>';
    var text = html
    .replace(/\{\{current_comment\.id\}\}/g,obj.id)
    .replace(/\{\{current_comment.name\}\}/g,obj.name)
    .replace(/\{\{current_comment.title\}\}/g,obj.title||'')
    .replace(/\{\{current_comment\.comment\|safe\}\}/g,obj.comment);
    return {htmlID:'comment-'+obj.id,
            object:obj,
            text: text
           };
}


/** INIT **/    
  commenter = new AjaxComment(frm);
  window.commenter = commenter;

});
