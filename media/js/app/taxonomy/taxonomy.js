(function(jQuery) {

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
            this.forEach(function(item) {
                a.push(item.toTemplate());
            });
            return a;
        },
        getByDataId: function(id) {
            var internalId = this.urlRoot + id + '/';
            return this.get(internalId);
        },
        getByDisplayName: function(name) {
            var filtered = this.filter(function(term) {
                return term.get("display_name") === name;
            });
            return filtered;
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
        },
        getOnomyUrls: function() {
            // the onomy url field was conceived as a comma-delimited list
            // of urls. reconstitute as an array here for easier searching
            // and adding new urls
            var urls = [];
            var str = this.get('onomy_url');
            if (str.length > 0) {
                urls = str.split(',');
            }
            return urls;
        },
        hasTerm: function(termName) {
            return this.get('term_set').getByDisplayName(termName).length > 0;
        }
    });

    function proxyAjaxEvent(event, options, dit) {
        var eventCallback = options[event];
        options[event] = function() {
            // check if callback for event exists and if so pass on request
            if (eventCallback) { eventCallback(arguments) }
            dit.processQueue(); // move onto next save request in the queue
        }
    };
    Backbone.Model.prototype._save = Backbone.Model.prototype.save;
    Backbone.Model.prototype.save = function( attrs, options ) {
        if (!options) { options = {}; }
        if (this.saving) {
            this.saveQueue = this.saveQueue || new Array();
            this.saveQueue.push({ attrs: _.extend({}, this.attributes, attrs), options: options });
        } else {
            this.saving = true;
            proxyAjaxEvent('success', options, this);
            proxyAjaxEvent('error', options, this);
            Backbone.Model.prototype._save.call( this, attrs, options );
        }
    };
    Backbone.Model.prototype.processQueue = function() {
        if (this.saveQueue && this.saveQueue.length) {
            var saveArgs = this.saveQueue.shift();
            proxyAjaxEvent('success', saveArgs.options, this);
            proxyAjaxEvent('error', saveArgs.options, this);
            Backbone.Model.prototype._save.call( this, saveArgs.attrs, saveArgs.options );
        } else {
            this.saving = false;
        }
    };

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
            this.forEach(function(item) {
                a.push(item.toTemplate());
            });
            return a;
        },
        getByDataId: function(id) {
            var internalId = this.urlRoot + id + '/';
            return this.get(internalId);
        }
    });

    window.VocabularyListView = Backbone.View.extend({
        events: {
            'click a.delete-vocabulary': 'deleteVocabulary',
            'click a.create-vocabulary-open': 'toggleCreateVocabulary',
            'click a.create-vocabulary-close': 'toggleCreateVocabulary',
            'click a.import-vocabulary-open': 'toggleImportVocabulary',
            'click a.import-vocabulary-close': 'toggleImportVocabulary',
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
            'click a.delete-term': 'deleteTerm',
            'click a.import-vocabulary-submit': 'createOnomyVocabulary',
            'click a.refresh-onomy': 'refreshOnomy',
            'click a.edit-onomy-urls': 'createOnomyVocabulary'
        },
        initialize: function(options) {
            _.bindAll(this,
                "render",
                "createVocabulary", "updateVocabulary", "deleteVocabulary",
                "createTerm", "keypressTermName", "updateTerm", "deleteTerm",
                "createOnomyVocabulary", "refreshOnomy",
                "getTheOnomy", "activateTab",
                "toggleCreateVocabulary", "toggleImportVocabulary");

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
            jQuery(this.el).find(".vocabulary-import").hide();
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
            jQuery(this.el).find("div.vocabularies li").removeClass("ui-corner-top").addClass("ui-corner-left");

            if (this.selected !== undefined) {
                var idx = this.collection.indexOf(this.selected);
                jQuery(elt).tabs("option", "active", idx);
            } else {
                this.selected = this.collection.at(0);
            }
        },
        toggleImportVocabulary: function(evt) {
            evt.preventDefault();
            jQuery(this.el).find(".vocabulary-import").toggle();
            return false;
        },
        toggleCreateVocabulary: function(evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("li")[0];
            jQuery(parent).find(".vocabulary-display, .vocabulary-create").toggle();
            return false;
        },
        toggleEditVocabulary: function(evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("li")[0];
            jQuery(parent).find(".vocabulary-display, .vocabulary-edit").toggle();
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
                'content_type_id': this.context.content_type_id,
                'object_id': this.context.course_id,
                'term_set': undefined,
                'onomy_url': ""
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
            var et = jQuery(evt.currentTarget).prev();
            if (jQuery(et).hasClass("default")) {
                //when both fields are left blank on submit
                showMessage("Please enter a term name", undefined, "Error");
                return;
            }
            //if you want to create a term from user input
            var display_name = jQuery(et).attr("value").trim();
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
                error: function(args) {
                    var response = args[1];
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
                    error: function(args) {
                        var response = args[1];
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
        },
        createOnomyVocabulary: function(evt) {
            evt.preventDefault();
            var elt = jQuery(evt.currentTarget).prevAll("input[name='onomy_url']")[0];
            
            var value = jQuery(elt).val().trim();
            
            // split the url.
            var urls = value.split(',');
            for (var i= 0; i < urls.length; i++) {
                if (urls[i].length < 1) {
                    showMessage("Please enter a valid Onomy JSON url.", undefined, "Error");
                    return;
                }
                
                var the_regex = /onomy.org\/published\/(\d+)\/json/g;
                var match = the_regex.exec(urls[i]);
                if (match.length < 0) {
                    // display error message
                    showMessage(urls[i] + " is not valid. Please enter an Onomy JSON Url.", undefined, "Error");
                    return;
                }
            }
            
            for (var i= 0; i < urls.length; i++) {
                this.getTheOnomy(urls[i], this.selected);
            }
        },
        refreshOnomy: function(evt) {
            var urls = this.selected.getOnomyUrls();
            for (var i = 0; i < urls.length; i++) {
                this.getTheOnomy(urls[i], this.selected);
            }
        },
        findUtil: function(array, thing){
            return jQuery.grep(array, function(item){
                return item.display_name == thing;
            });
        },
        getTheOnomy: function(onomyURL, selectedVocabulary) {
            var self = this;

            jQuery.get(onomyURL, function(data) {
                 var x = JSON.parse(data);

                 var parents = [];
                 var MAX = x.terms.length; //change to x.terms.length after done testing
                 for (var i = 0; i < MAX; i++) {
                     var pL = x.terms[i]['rdfs:parentLabel'].trim();
                     var display = x.terms[i]['rdfs:label'].trim();
                       
                     //demorgans law
                     if (!(pL === undefined || pL.length < 1)) {
                         var search = undefined;
                         parents.forEach(function(a) {
                             if (a.display_name == pL) {
                                 search = a;
                             }
                         });
                         if (search === undefined) {
                             // create the Vocabulary
                             var temp = {'display_name': pL,
                                         'term_set': [],
                                         'content_type_id': self.context.content_type_id,
                                         'object_id': self.context.course_id,
                                         'onomy_url': 'child',
                                         'self': undefined};
                             parents.push(temp);
                             parents[parents.indexOf(temp)].term_set.push({'display_name': display});
                         } else {
                             //add the term to the Vocabulary in parents
                             v = search;
                             parents[parents.indexOf(v)].term_set.push({'display_name': display});
                         }
                                   
                         if (i == MAX - 1) {
                             for (var j = 0; j < parents.length; j++) {
                                 var model_search = _.find(self.collection.models, function(model) {
                                     return model.attributes.display_name == parents[j].display_name
                                 });
                                 if (model_search === undefined) {
                                     // if we cant find the vocab in the collection we create a new one.

                                     var tempV = new Vocabulary({
                                         'display_name': parents[j].display_name,
                                         'content_type_id': self.context.content_type_id,
                                         'object_id': self.context.course_id,
                                         'term_set': undefined,
                                         'onomy_url': 'child'
                                     });

                                     tempV._save({}, {
                                         success: function(it) {
                                             parents[parents.indexOf(self.findUtil(parents, it.attributes['display_name'])[0])].self = it;
                                             self.collection.add(it);
                                             for (var z = 0; z < parents[parents.indexOf(self.findUtil(parents, it.attributes['display_name'])[0])].term_set.length; z++) {
                                                 var tempT = new Term({
                                                     'display_name': parents[parents.indexOf(self.findUtil(parents, it.attributes['display_name'])[0])].term_set[z].display_name,
                                                     'vocabulary_id': it.attributes['id']
                                                 });
                                                 tempT._save({}, {
                                                     success: function(itT) {
                                                         parents[parents.indexOf(self.findUtil(parents, it.attributes['display_name'])[0])].self.get('term_set').add(itT);
                                                         self.render();
                                                     }
                                                 });
                                             }
                                         }
                                     });
                                 } else {
                                     for (var z = 0; z < parents[parents.indexOf(self.findUtil(parents, model_search.attributes['display_name'])[0])].term_set.length; z++) {
                                         var tempT = new Term({
                                             'display_name': parents[parents.indexOf(self.findUtil(parents, model_search.attributes['display_name'])[0])].term_set[z].display_name,
                                             'vocabulary_id': model_search.attributes['id']
                                         });
                                         tempT._save({}, {
                                             success: function(itT) {
                                                 model_search.get('term_set').add(itT);
                                                 self.render();
                                             }
                                         });
                                     }
                                 }
                             }
                         }
                     } else if (display !== undefined && display.length > 0) {
                         var urls = selectedVocabulary.getOnomyUrls();

                         //if this vocabulary doesn't contain the url we punched in
                         if (!_.contains(urls, onomyURL)) {
                             //add it to our array we made and save it in the vocab
                             urls.push(onomyURL);
                             selectedVocabulary.save({'onomy_url': urls.toString()});
                         }
                         //we create our term if it doesn't already exist
                         if (!selectedVocabulary.hasTerm(display)) {
                             var t = new Term({
                                 'display_name': display,
                                 'vocabulary_id': selectedVocabulary.get('id')
                             });
                             //then save it with our overriden queued save
                             t._save({}, {
                                 wait: true,
                                 success: function(newTerm) {
                                     //add it to the term set
                                     selectedVocabulary.get('term_set').add(newTerm);
                                     self.render();
                                 }
                             });
                         }
                     }
                 }
            });
        }        
    });
}(jQuery));


