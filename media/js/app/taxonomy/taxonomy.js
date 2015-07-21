/* jshint loopfunc: true */
/* global _: true, Backbone: true, showMessage: true */

(function(jQuery) {
    // saveAll dirty models in a collection. Uses jQuery when/then to chain
    // http://stackoverflow.com/questions/5014216/
    //     best-practice-for-saving-an-entire-collection
    Backbone.Collection.prototype.saveAll = function(options) {
        return jQuery.when.apply(jQuery, _.map(this.models, function(m) {
           return m.save(options).then(_.identity);
        }));
    };

    var Term = Backbone.Model.extend({
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
            return this.find(function(term) {
                return term.get("display_name") === name;
            });
        }
    });

    var Vocabulary = Backbone.Model.extend({
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
            return this.get('term_set').getByDisplayName(termName);
        },
        addTerm: function(termName) {
            if (!this.hasTerm(termName)) {
                var term = new Term({display_name: termName});
                this.get('term_set').add(term);
            }
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
            this.forEach(function(item) {
                a.push(item.toTemplate());
            });
            return a;
        },
        getByDataId: function(id) {
            var internalId = this.urlRoot + id + '/';
            return this.get(internalId);
        },
        getByDisplayName: function(displayName) {
            return this.find(function(vocab) {
                return vocab.get("display_name") === displayName;
            });
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
            this.collection.on("sync", this.render);
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
            var display_name = jQuery(elt).val();
            if (display_name === undefined || display_name.trim().length < 1) {
                showMessage("Please name your concept.", undefined, "Error");
                return;
            }

            display_name = display_name.trim();
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
                    var text =  jQuery.type(response) == 'object' ?
                        response.responseText : response;
                    var the_json = jQuery.parseJSON(text);
                    showMessage(the_json.vocabulary.error_message[0],
                        undefined, "Error");
                }
            });

            return false;
        },
        updateVocabulary: function(evt) {
            evt.preventDefault();
            var self = this;
            var parent = jQuery(evt.currentTarget).parent();

            var elt = jQuery(parent).find('input[name="display_name"]')[0];
            var display_name = jQuery(elt).val();
            if (display_name === undefined || display_name.length < 1) {
                showMessage("Please name your concept.", undefined, "Error");
                return;
            }

            var id = jQuery(parent).find('input[name="vocabulary_id"]').val();
            var v = this.collection.getByDataId(id);
            if (v.get('display_name') !== display_name) {
                v.save({'display_name': display_name}, {
                    success: function() {
                        self.render();
                    },
                    error: function(model, response) {
                        var text =  jQuery.type(response) == 'object' ?
                            response.responseText : response;
                        var the_json = jQuery.parseJSON(text);
                        showMessage(the_json.vocabulary.error_message,
                            undefined, "Error");
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
                var opts = '.edit-term-submit,.create-term-submit';
                jQuery(evt.currentTarget).nextAll(opts).click();
            }
        },
        createTerm: function(evt) {
            evt.preventDefault();
            var self = this;

            // currentTarget could be the input box (if user hit return) or
            // the + button right next door
            var elt = evt.currentTarget;
            if (!jQuery(elt).is('input:text')) {
                elt = jQuery(evt.currentTarget).prev()[0];
            }

            //if you want to create a term from user input
            var display_name = jQuery(elt).val();
            if (display_name === undefined || display_name.trim().length < 1) {
                showMessage("Please enter a term name.", undefined, "Error");
                return;
            }

            display_name = display_name.trim();
            
            if (self.selected.hasTerm(display_name)) {
                showMessage(display_name + " term already exists. Please choose a new name.", undefined, "Error");
                return;
            }

            var t = new Term({
                'display_name': display_name,
                'vocabulary': this.selected.get('resource_uri')
            });
            t.save({}, {
                success: function() {
                    self.selected.get('term_set').add(t);
                    self.render();
                },
                error: function(model, response) {
                    var text =  jQuery.type(response) == 'object' ?
                        response.responseText : response;
                    var the_json = jQuery.parseJSON(text);
                    showMessage(the_json.term.error_message,
                        undefined, "Error");
                }
            });
            return false;
        },
        updateTerm: function(evt) {
            evt.preventDefault();
            var self = this;
            var elt = jQuery(evt.currentTarget).prevAll("input[type='text']");
            var display_name = jQuery(elt).val();
            if (display_name === undefined || display_name.trim().length < 1) {
                showMessage("Please enter a term name.", undefined, "Error");
                return;
            }

            display_name = display_name.trim();
            
            if (self.selected.hasTerm(display_name)) {
                showMessage(display_name + " term already exists. Please choose a new name.", undefined, "Error");
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
                        var text =  jQuery.type(response) == 'object' ?
                            response.responseText : response;
                        var the_json = jQuery.parseJSON(text);
                        showMessage(the_json.term.error_message,
                            undefined, "Error");
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
        createOnomyVocabulary: function(evt) {
            evt.preventDefault();
            var elt = jQuery(evt.currentTarget).prevAll("input[name='onomy_url']")[0];

            var value = jQuery(elt).val().trim();

            // split the url.
            var urls = value.split(',');
            for (var i = 0; i < urls.length; i++) {
                if (urls[i].length < 1) {
                    showMessage("Please enter a valid Onomy JSON url.", undefined, "Error");
                    return;
                }
                if (!urls[i].contains('test.json')) { // testing
                    var the_regex = /onomy.org\/published\/(\d+)\/json/g;
                    var match = the_regex.exec(urls[i]);
                    if (match.length < 0) {
                       // display error message
                       showMessage(urls[i] + " is not valid. Please enter an Onomy JSON Url.", undefined, "Error");
                       return;
                    }
                }
            }

            for (var j = 0; j < urls.length; j++) {
                this.getTheOnomy(urls[j], this.selected);
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
                var parents = {};
                for (var i = 0; i < data.terms.length; i++) {
                    var pL = data.terms[i]['rdfs:parentLabel'].trim();
                    var display = data.terms[i]['rdfs:label'].trim();

                    if (typeof pL !== undefined && pL.length > 0) {
                        var search = parents.hasOwnProperty(pL);
                        if (!search) {
                            /*
                             * create the 'vocabulary' object
                             * the reason for making this a non vocabulary object is you have to dig
                             * down deeper into the Vocabulary model to get display_name etc.
                            */
                            var temp = {
                                'display_name': pL,
                                'term_set': [],
                                'content_type_id': self.context.content_type_id,
                                'object_id': self.context.course_id,
                                'onomy_url': 'child'
                            };
                            temp.term_set.push({'display_name': display});
                            parents[temp.display_name] = temp;
                        } else {
                            //add the term to the Vocabulary in parents
                            parents[pL].term_set.push({'display_name': display});
                        }

                    } else if (display !== undefined && display.length > 0) {
                        var urls = selectedVocabulary.getOnomyUrls();
                        //if this vocabulary doesn't contain the url we punched in
                        if (!_.contains(urls, onomyURL)) {
                            //add it to our array we made and save it in the vocab
                            urls.push(onomyURL);
                            selectedVocabulary.set("onomy_url", urls.toString());
                        }
                        //we create our term if it doesn't already exist
                        selectedVocabulary.addTerm(display);
                    }
                }

                // loop over the array.
                for (var key in parents){
                    if (!parents.hasOwnProperty(key)) {
                        continue;
                    }
                    var existingVocab = self.collection.getByDisplayName(key);
                    if (existingVocab === undefined) {
                        // if we cant find the vocab in the collection create a new one.
                        var vocab = new Vocabulary({
                            'display_name': key,
                            'content_type_id': self.context.content_type_id,
                            'object_id': self.context.course_id,
                            'term_set': new TermList(),
                            'onomy_url': 'child',
                            'self': undefined
                        });

                        for (var z = 0; z < parents[key].term_set.length; z++) {
                            vocab.addTerm(parents[key].term_set[z].display_name);
                        }

                        self.collection.add(vocab);
                    } else if (_.size(parents) > 0) {
                        // if the vocab is in the collection, just add the term
                        for (var q = 0; q < parents[key].term_set.length; q++) {
                            var term = parents[key].term_set[q].display_name;
                            existingVocab.addTerm(term);
                        }
                    }
                }
                
                self.collection.saveAll();
            });
        }
    });
}(jQuery));
