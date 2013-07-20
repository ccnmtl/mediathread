(function (jQuery) {
    
    Term = Backbone.Model.extend({
        urlRoot: '/_main/api/v1/term/',
        toTemplate: function() {
            return _(this.attributes).clone();
        }        
    });    

    var TermList = Backbone.Collection.extend({
        urlRoot: '/_main/api/v1/term/',
        model: Term,
        toTemplate: function() {
            var a = [];
            this.forEach(function (item) {
                a.push(item.toTemplate());
            });
            return a;
        }
    });
    
    Vocabulary = Backbone.Model.extend({
        urlRoot: '/_main/api/v1/vocabulary/',
        parse: function(response) {
            if (response) {
                response.term_set = new TermList(response.term_set);
            }
            return response;
        },        
        toTemplate: function() {
            var json = _(this.attributes).clone();
            json.term_set = this.get('term_set').toTemplate();
            return json;
        }
    });
    
    var VocabularyList = Backbone.Collection.extend({
        urlRoot: '/_main/api/v1/vocabulary/',
        model: Vocabulary,
        parse: function(response) {
            return response.objects || response;
        },
        toTemplate: function() {
            var a = [];
            this.forEach(function (item) {
                a.push(item.toTemplate());
            });
            return a;
        },
        getByDataId: function (id) {
            var internalId = this.urlRoot + id + '/';
            return this.get(internalId);
        }
    });
    
    window.TermListView = Backbone.View.extend({
        initialize: function(options) {
            _.bindAll(this,
                      "render",
                      "unrender");
            
            this.parentView = options.parentView;
            this.model.bind("destroy", this.unrender);
            this.render();            
        },
        render: function () {
            var self = this; 
        },
        unrender: function () {
        }
    });
    
    window.VocabularyListView = Backbone.View.extend({
        events: {
            'click a.delete-vocabulary': 'onDeleteVocabulary',
            'click a.create-vocabulary-open': 'toggleCreateVocabulary',
            'click a.create-vocabulary-close': 'toggleCreateVocabulary',            
            'click a.create-vocabulary-submit': 'createVocabulary',
            'click a.edit-vocabulary-open': 'toggleEditVocabulary',
            'click a.edit-vocabulary-close': 'toggleEditVocabulary'
        },
        initialize: function(options) {
            _.bindAll(this,
                    "render",
                    "onDeleteVocabulary",
                    "createVocabulary");
            
            this.vocabularyTemplate =
                _.template(jQuery("#vocabulary-template").html());
            
            this.context = {
                'course_id': options.course_id,
                'content_type_id': options.content_type_id
            };
            
            this.collection = new VocabularyList();
            this.collection.comparator = function(obj) {
                return obj.get("display_name");
            };
            this.collection.on("add", this.render);
            this.collection.on("remove", this.render);
            this.collection.on("reset", this.render);            
            this.collection.fetch();
        },
        render: function() {
            this.context.vocabularies = this.collection.toTemplate();
            var markup = this.vocabularyTemplate(this.context);
            jQuery(this.el).html(markup);
            
            var elt = jQuery(this.el).find("div.vocabularies");
            jQuery(elt).tabs();
            jQuery(elt).addClass("ui-tabs-vertical ui-helper-clearfix");
            jQuery(this.el).find("div.vocabularies li").removeClass("ui-corner-top").addClass( "ui-corner-left");
            
            if (this.selected !== undefined) {
                var sel = jQuery("#vocabulary-wrapper-" + this.selected.get('id'));
                var tabIndex = jQuery(sel).attr('tabindex');
                jQuery(elt).tabs("option", "active", tabIndex);
            }
        },
        toggleCreateVocabulary: function(evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("li")[0];
            jQuery(parent).find("div.vocabulary-display, div.vocabulary-create").toggle();
            jQuery(parent).find("input[name='display_name']").focus();
            return false;    
        },
        toggleEditVocabulary: function(evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("li")[0];
            jQuery(parent).find("div.vocabulary-display, div.vocabulary-edit").toggle();
            jQuery(parent).find("input[name='display_name']").focus();
            return false;    
        },
        createVocabulary: function(evt) {
            evt.preventDefault();
            var self = this;
            var parent = jQuery(evt.currentTarget).parent();
            var display_name = jQuery(parent).find('input[name="display_name"]').attr("value").trim();
            
            if (display_name === undefined || display_name.length < 1) {
                showMessage("Please name your concept.");
                return;
            }
            
            var v = new Vocabulary({
                'display_name': display_name,
                'content_type_id': jQuery(parent).find('input[name="content_type_id"]').attr("value"),
                'object_id': jQuery(parent).find('input[name="object_id"]').attr("value"),
                'term_set': undefined
            });
            v.save({}, {
                success: function() {
                    self.selected = v;
                    self.collection.add(v);
                }
            });
            return false;
        },
        onDeleteVocabulary: function(evt) {
            var self = this;
            
            var id = jQuery(evt.currentTarget).attr('href');
            var vocabulary = self.collection.getByDataId(id);

            var msg = "Are you sure you want to delete the " +
                vocabulary.get('display_name') +
                " vocabulary? Deleting a vocabulary removes its terms " + 
                "from all associated course items.";
            
            var dom = jQuery(evt.currentTarget).parents('li');
            jQuery(dom).addClass('about-to-delete');
            
            jQuery("#dialog-confirm").html(msg);            
            jQuery("#dialog-confirm").dialog({
                resizable: false,
                modal: true,
                title: "Confirm action",
                close: function(event, ui) {
                    jQuery(dom).removeClass('about-to-delete');
                },
                buttons: {
                    "Cancel": function() {
                        jQuery(this).dialog("close");             
                    },
                    "OK": function() {
                        jQuery(this).dialog("close");
                        self.collection.remove(vocabulary);
                        vocabulary.destroy();
                    }
                }
            });
            return false;
        }
    });
    
}(jQuery));    