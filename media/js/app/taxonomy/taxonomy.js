(function (jQuery) {
    
    Term = Backbone.Model.extend({
        urlRoot: '/api/term/',
        toTemplate: function() {
            return _(this.attributes).clone();
        }        
    });    

    var TermList = Backbone.Collection.extend({
        urlRoot: '/api/term/',
        model: Term,
        comparator: function(obj) {
            return obj.get("display_name");
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
    
    Vocabulary = Backbone.Model.extend({
        urlRoot: '/api/vocabulary/',
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
        urlRoot: '/api/vocabulary/',
        model: Vocabulary,
        comparator: function(obj) {
            return obj.get("display_name");
        },
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
    
    window.VocabularyListView = Backbone.View.extend({
        events: {
            'click a.delete-vocabulary': 'deleteVocabulary',
            'click a.create-vocabulary-open': 'toggleCreateVocabulary',
            'click a.create-vocabulary-close': 'toggleCreateVocabulary',            
            'click a.edit-vocabulary-open': 'toggleEditVocabulary',
            'click a.edit-vocabulary-close': 'toggleEditVocabulary',
            'click a.create-vocabulary-submit': 'createVocabulary',
            'click a.edit-vocabulary-submit': 'updateVocabulary',
            'focus input[name="display_name"]': 'focusVocabularyName',
            'blur input[name="display_name"]': 'blurVocabularyName',
            'focus input[name="term_name"]': 'focusTermName',
            'blur input[name="term_name"]': 'blurTermName',
            'click a.create-term-submit': 'createTerm',
            'keypress input[name="term_name"]': 'keypressTermName',
            'click a.edit-term-submit': 'updateTerm',
            'click a.edit-term-open': 'showEditTerm',
            'click a.edit-term-close': 'hideEditTerm',            
            'click a.delete-term': 'deleteTerm'
        },
        initialize: function(options) {
            _.bindAll(this,
                    "render",
                    "createVocabulary",
                    "updateVocabulary",
                    "deleteVocabulary",
                    "createTerm",
                    "keypressTermName",
                    "updateTerm",
                    "deleteTerm",
                    "activateTab");
            
            this.context = options;
            this.vocabularyTemplate =
                _.template(jQuery("#vocabulary-template").html());
            
            this.collection = new VocabularyList();
            this.collection.on("add", this.render);
            this.collection.on("remove", this.render);
            this.collection.on("reset", this.render);            
            this.collection.fetch();
        },
        activateTab: function(evt, ui) {
            jQuery(ui.oldTab).find("div.vocabulary-edit, div.vocabulary-create").hide();
            jQuery(ui.oldTab).find("div.vocabulary-display").show();
            var vid = jQuery(ui.newTab).data("id");
            this.selected = this.collection.getByDataId(vid);
        },
        render: function() {
            this.context.vocabularies = this.collection.toTemplate();
            var markup = this.vocabularyTemplate(this.context);
            jQuery(this.el).html(markup);
            
            var elt = jQuery(this.el).find("div.vocabularies");
            jQuery(elt).tabs({
                'activate': this.activateTab
            });
            // remove the default tabs key processing
            jQuery(elt).find('li').off('keydown');
            jQuery(elt).addClass("ui-tabs-vertical ui-helper-clearfix");
            jQuery(this.el).find("div.vocabularies li").removeClass("ui-corner-top").addClass( "ui-corner-left");
            
            if (this.selected !== undefined) {
                var idx = this.collection.indexOf(this.selected);
                jQuery(elt).tabs("option", "active", idx);
            } else {
                this.selected = this.collection.at(0);
            }            
        },
        toggleCreateVocabulary: function(evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("li")[0];
            jQuery(parent).find("div.vocabulary-display, div.vocabulary-create").toggle();
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
            var elt = jQuery(parent).find('input[name="display_name"]')[0];
            if (jQuery(elt).hasClass("default")) {    
                showMessage("Please name your concept.", undefined, "Error");
                return;
            }
            
            var display_name = jQuery(elt).attr("value").trim();            
            if (display_name === undefined || display_name.length < 1) {
                showMessage("Please name your concept.", undefined, "Error");
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
                },
                error: function(model, response) {
                    var responseText = jQuery.parseJSON(response.responseText);
                    showMessage(responseText.vocabulary.error_message, undefined, "Error");
                }
            });
            return false;
        },
        updateVocabulary: function(evt) {
            evt.preventDefault();
            var self = this;
            var parent = jQuery(evt.currentTarget).parent();
            
            var elt = jQuery(parent).find('input[name="display_name"]')[0];
            if (jQuery(elt).hasClass("default")) {    
                showMessage("Please name your concept.", undefined, "Error");
                return;
            }
            
            var display_name = jQuery(elt).attr("value").trim();            
            if (display_name === undefined || display_name.length < 1) {
                showMessage("Please name your concept.", undefined, "Error");
                return;
            }
            
            var id = jQuery(parent).find('input[name="vocabulary_id"]').attr("value").trim();
            var v = this.collection.getByDataId(id);
            if (v.get('display_name') !== 'display_name') {
                v.save({'display_name': display_name}, {
                    success: function() {
                        self.render();
                    },
                    error: function(model, response) {
                        var responseText = jQuery.parseJSON(response.responseText);
                        showMessage(responseText.vocabulary.error_message, undefined, "Error");
                    }
                });
            }
            return false;
        },
        deleteVocabulary: function(evt) {
            var self = this;
            
            var id = jQuery(evt.currentTarget).attr('href');
            var vocabulary = self.collection.getByDataId(id);

            var msg = "Deleting <b>" + vocabulary.get('display_name') + "</b>" +
                " removes its terms" + 
                " from all associated course items.";
            
            var dom = jQuery(evt.currentTarget).parents('li');
            jQuery(dom).addClass('about-to-delete');
            
            jQuery("#dialog-confirm").html(msg);            
            jQuery("#dialog-confirm").dialog({
                resizable: false,
                modal: true,
                title: "Are you sure?",
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
        },
        focusVocabularyName: function(evt) {
            if (jQuery(evt.currentTarget).hasClass("default")) {
                jQuery(evt.currentTarget).removeClass("default");
                jQuery(evt.currentTarget).attr("value", "");
            }
        },
        blurVocabularyName: function(evt) {
            if (jQuery(evt.currentTarget).attr("value") === '') {
                jQuery(evt.currentTarget).addClass("default");
                jQuery(evt.currentTarget).attr("value", "Type concept name here");
            }
        },
        showEditTerm: function(evt) {
            evt.preventDefault();
            var container = jQuery(evt.currentTarget).parents("div.terms");
            jQuery(container).find("div.term-display").show();
            jQuery(container).find("div.term-edit").hide();
            
            var parent = jQuery(evt.currentTarget).parents("div.term")[0];
            jQuery(parent).find("div.term-display").hide();
            jQuery(parent).find("div.term-edit").show();
            jQuery(parent).find("input[name='display_name']").focus();
            return false;    
        },        
        hideEditTerm: function(evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("div.term")[0];
            jQuery(parent).find("div.term-display").show();
            jQuery(parent).find("div.term-edit").hide();
            return false;    
        },        
        keypressTermName: function(evt) {
            var self = this;
            if (evt.which == 13) {
                evt.preventDefault();                
                jQuery(evt.currentTarget).next().click();
            }
        },
        createTerm: function(evt) {
            evt.preventDefault();
            var self = this;
            var elt = jQuery(evt.currentTarget).prev();
            if (jQuery(elt).hasClass("default")) {    
                showMessage("Please enter a term name.", undefined, "Error");
                return;
            }
            
            var display_name = jQuery(elt).attr("value").trim();            
            if (display_name === undefined || display_name.length < 1) {
                showMessage("Please enter a term name.", undefined, "Error");
                return;
            }
            
            var t = new Term({
                'display_name': display_name,
                'vocabulary_id': this.selected.get('id')
            });
            t.save({}, {
                success: function() {
                    self.selected.get('term_set').add(t);
                    self.render();
                },
                error: function(model, response) {
                    var responseText = jQuery.parseJSON(response.responseText);
                    showMessage(responseText.term.error_message, undefined, "Error");
                }
            });
            return false;            
        },
        updateTerm: function(evt) {
            evt.preventDefault();
            var self = this;
            var elt = jQuery(evt.currentTarget).prevAll("input[type='text']");
            if (jQuery(elt).hasClass("default")) {
                showMessage("Please enter a term name.", undefined, "Error");
                return;
            }
            
            var display_name = jQuery(elt).attr("value").trim();            
            if (display_name === undefined || display_name.length < 1) {
                showMessage("Please enter a term name.", undefined, "Error");
                return;
            }
            
            var tid = jQuery(evt.currentTarget).data('id');
            var term = this.selected.get("term_set").getByDataId(tid);
            
            if (term.get('display_name') !== 'display_name') {
                term.set('display_name', display_name);
                term.save({}, {
                    success: function() {
                        self.render();
                    },
                    error: function(model, response) {
                        var responseText = jQuery.parseJSON(response.responseText);
                        showMessage(responseText.term.error_message, undefined, "Error");
                    }
                });
            }
            return false; 
        },
        deleteTerm: function(evt) {
            evt.preventDefault();
            var self = this;
            
            var id = jQuery(evt.currentTarget).attr('href');
            var term = self.selected.get('term_set').getByDataId(id);

            var msg = "Deleting the term <b>" + term.get('display_name') + "</b>" +
                " removes this term" + 
                " from all associated course items.";
            
            var dom = jQuery(evt.currentTarget).parents('div.term');
            jQuery(dom).addClass('about-to-delete');
            
            jQuery("#dialog-confirm").html(msg);            
            jQuery("#dialog-confirm").dialog({
                resizable: false,
                modal: true,
                title: "Are you sure?",
                close: function(event, ui) {
                    jQuery(dom).removeClass('about-to-delete');
                },
                buttons: {
                    "Cancel": function() {
                        jQuery(this).dialog("close");             
                    },
                    "OK": function() {
                        jQuery(this).dialog("close");
                        self.selected.get('term_set').remove(term);
                        term.destroy();
                        self.render();
                    }
                }
            });
            return false;
        },
        focusTermName: function(evt) {
            if (jQuery(evt.currentTarget).hasClass("default")) {
                jQuery(evt.currentTarget).removeClass("default");
                jQuery(evt.currentTarget).attr("value", "");
            }
        },
        blurTermName: function(evt) {
            if (jQuery(evt.currentTarget).attr("value") === '') {
                jQuery(evt.currentTarget).addClass("default");
                jQuery(evt.currentTarget).attr("value", "Type new term name here");
            }
        }        
    });
    
}(jQuery));    