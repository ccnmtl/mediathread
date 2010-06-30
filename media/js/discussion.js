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
    function open_edit(evt) {
        mode='update';
        var edit = evt.target;
        frm.elements['parent'].value = '';
        var id = frm.elements['edit-id'].value = edit.getAttribute("data-comment");

        open_comment_form(edit);

        set_comment_content(commenter.read({html:jQuery('#comment-'+id).get(0)}));
    }

    function comment_form_space(button) {
        return jQuery('div.comment_form_space',button.parentNode).get(0);
    }

    function set_comment_content(content) {
        content = content || {comment:'<p></p>'};
        frm.elements['comment'].value = content.comment;
        frm.elements['title'].value = content.title || '';
        var action = (content.title) ? 'show' : 'hide';
        jQuery('.formtitle')[action]();
        tinyMCE.execInstanceCommand('id_comment','mceSetContent',false,content.comment,false);
    }
    set_comment_content();

    function open_comment_form(evt_target) {
        if (!next_response_loc) {
	    next_response_loc = evt_target;
            comment_form_space(evt_target).appendChild(frm);
            jQuery(frm).show();
            jQuery('#id_comment').focus();
            tinyMCE.execCommand("mceAddControl", false, "id_comment");
        } else {
	    if (next_response_loc == evt_target) {
		next_response_loc = false;
	    } else {
                next_response_loc = evt_target;
	    }
            tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
            tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
        }
    }

    function hide_comment_form() {
        next_response_loc = false;
        tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
        tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
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
	}
    });
    tinyMCE.onAddEditor.add(function(manager, ed) {
        ed.onInit.add(function(editor) {
            tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
        });
    });

    if (window.djangosherd) {
        djangosherd.onOpenCitation = function(id,ann_obj,options,targets) {
            if (targets.top == 'videoclipbox') {
                updateVerticalHeight(null,{'materials':260});
            }
        }
    }

function AjaxComment(form) {
    this.form = form;
    this.username = jQuery('#logged_in_name').text();

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
                'name':self.username
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
                self.update(new_obj, comment_html);
                this.info.target = self.components(comment_html).comment;
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
        'title':c.title.innerHTML,
        'id':String(c.top.id).substr(8)//comment- chopped
    }
}

AjaxComment.prototype.update = function(obj,html_dom) {
    if (obj.comment) {
        if (jQuery('.threaded_comment_text:first',html_dom)
            .html(obj.comment).length) {
            return true;
        }
    }
    return false; // if it fails
}

AjaxComment.prototype.components = function(html_dom,create_obj) {
    return {'top':html_dom,
            'comment':jQuery('div.threaded_comment_text:first',html_dom).get(0),
            'title':jQuery('div.threaded_comment_title',html_dom).get(0),
            'author':jQuery('span.threaded_comment_author:first',html_dom).get(0)
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
        +    '<span class="threaded_comment_author">{{current_comment.name}} </span>'
        +      '<a class="comment-anchor" href="#comment-{{current_comment.id}}">said:</a>'
        + ' </div>'
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
    .replace(/\{\{current_comment\.comment\|safe\}\}/g,obj.comment);
    return {htmlID:'comment-'+obj.id,
            object:obj,
            text: text
           };
}

    commenter = new AjaxComment(frm);

});
