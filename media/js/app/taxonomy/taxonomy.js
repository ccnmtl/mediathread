(function (jQuery) {

    Term = Backbone.Model.extend({
        urlRoot: '/api/term/',
        toTemplate: function () {
            return _(this.attributes).clone();
        }
    });

    var TermList = Backbone.Collection.extend({
        urlRoot: '/api/term/',
        model: Term,
        comparator: function (obj) {
            return obj.get("display_name");
        },
        toTemplate: function () {
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
        parse: function (response) {

            if (response) {
                response.term_set = new TermList(response.term_set);
            }

            return response;
        },
        toTemplate: function () {
            var json = _(this.attributes).clone();
            json.term_set = this.get('term_set').toTemplate();
            return json;
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
        comparator: function (obj) {
            return obj.get("display_name");
        },
        parse: function (response) {
            return response.objects || response;
        },
        toTemplate: function () {
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
	    'focus input[name="onomy_url"]': 'focusTermName',
            'blur input[name="term_name"]': 'blurTermName',
	    'blur input[name="onomy_url"]': 'blurTermName',
            'click a.create-term-submit': 'createTerm',
            'keypress input[name="term_name"]': 'keypressTermName',
            'click a.edit-term-submit': 'updateTerm',
            'click a.edit-term-open': 'showEditTerm',
            'click a.edit-term-close': 'hideEditTerm',
            'click a.delete-term': 'deleteTerm',
            'click a.onomy-terms-submit': 'createOnomyVocabulary',
            'click a.refresh-button-submit' : 'refreshOnomy'
        },
        initialize: function (options) {
            _.bindAll(this,
                "render",
                "createVocabulary",
                "updateVocabulary",
                "deleteVocabulary",
                "createTerm",
                "keypressTermName",
                "updateTerm",
                "deleteTerm",
                "createOnomyVocabulary",
                "refreshOnomy",
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
        activateTab: function (evt, ui) {
            jQuery(ui.oldTab).find("div.vocabulary-edit, div.vocabulary-create").hide();
            jQuery(ui.oldTab).find("div.vocabulary-display").show();
            var vid = jQuery(ui.newTab).data("id");
            this.selected = this.collection.getByDataId(vid);
        },
        render: function () {
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
        toggleCreateVocabulary: function (evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("li")[0];
            jQuery(parent).find("div.vocabulary-display, div.vocabulary-create").toggle();
            return false;
        },
        toggleEditVocabulary: function (evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("li")[0];
            jQuery(parent).find("div.vocabulary-display, div.vocabulary-edit").toggle();
            jQuery(parent).find("input[name='display_name']").focus();
            return false;
        },
        createVocabulary: function (evt) {
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
                'term_set': undefined,
                'onomy_url': ""
            });
            console.log(v);
            v.save({}, {

                success: function () {
                    self.selected = v;
                    self.collection.add(v);
                    console.log('success');
                },
                error: function (model, response) {
                    var responseText = jQuery.parseJSON(response.responseText);
                    showMessage(responseText.vocabulary.error_message, undefined, "Error");
                }
            });

            return false;
        },
        updateVocabulary: function (evt) {
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
                    success: function () {
                        self.render();
                    },
                    error: function (model, response) {
                        var responseText = jQuery.parseJSON(response.responseText);
                        showMessage(responseText.vocabulary.error_message, undefined, "Error");
                    }
                });
            }
            return false;
        },
        deleteVocabulary: function (evt) {
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
                close: function (event, ui) {
                    jQuery(dom).removeClass('about-to-delete');
                },
                buttons: {
                    "Cancel": function () {
                        jQuery(this).dialog("close");
                    },
                    "OK": function () {
                        jQuery(this).dialog("close");
                        self.collection.remove(vocabulary);
                        vocabulary.destroy();
                    }
                }
            });
            return false;
        },
        focusVocabularyName: function (evt) {
            if (jQuery(evt.currentTarget).hasClass("default")) {
                jQuery(evt.currentTarget).removeClass("default");
                jQuery(evt.currentTarget).attr("value", "");
            }
        },
        blurVocabularyName: function (evt) {
            if (jQuery(evt.currentTarget).attr("value") === '') {
                jQuery(evt.currentTarget).addClass("default");
                jQuery(evt.currentTarget).attr("value", "Type concept name here");
            }
        },
        showEditTerm: function (evt) {
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
        hideEditTerm: function (evt) {
            evt.preventDefault();
            var parent = jQuery(evt.currentTarget).parents("div.term")[0];
            jQuery(parent).find("div.term-display").show();
            jQuery(parent).find("div.term-edit").hide();
            return false;
        },
        keypressTermName: function (evt) {
            var self = this;
            if (evt.which == 13) {
                evt.preventDefault();
                jQuery(evt.currentTarget).next().click();
            }
        },
        createTerm: function (evt) {
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
                    success: function () {
                        self.selected.get('term_set').add(t);
                        self.render();
                    },
                    error: function (model, response) {
                        var responseText = jQuery.parseJSON(response.responseText);
                        showMessage(responseText.term.error_message, undefined, "Error");
                    }
                });
                return false;

        },
        updateTerm: function (evt) {
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
                    success: function () {
                        self.render();
                    },
                    error: function (model, response) {
                        var responseText = jQuery.parseJSON(response.responseText);
                        showMessage(responseText.term.error_message, undefined, "Error");
                    }
                });
            }
            return false;
        },
        deleteTerm: function (evt) {
            evt.preventDefault();
            var self = this;

            var id = jQuery(evt.currentTarget).attr('href');
            console.log(jQuery(evt.currentTarget));
            console.log(id);
            var term = self.selected.get('term_set').getByDataId(id);
            console.log(term);
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
                close: function (event, ui) {
                    jQuery(dom).removeClass('about-to-delete');
                },
                buttons: {
                    "Cancel": function () {
                        jQuery(this).dialog("close");
                    },
                    "OK": function () {
                        jQuery(this).dialog("close");
                        self.selected.get('term_set').remove(term);
                        term.destroy();
                        self.render();
                    }
                }
            });
            return false;
        },
        focusTermName: function (evt) {
            if (jQuery(evt.currentTarget).hasClass("default")) {
                jQuery(evt.currentTarget).removeClass("default");
                jQuery(evt.currentTarget).attr("value", "");
            }
        },
        blurTermName: function (evt) {
            if (jQuery(evt.currentTarget).attr("value") === '' && jQuery(evt.currentTarget).attr("name") !== 'onomy_url') {
                jQuery(evt.currentTarget).addClass("default");
                jQuery(evt.currentTarget).attr("value", "Type new term name here");
            }else if(jQuery(evt.currentTarget).attr("value") === '' && jQuery(evt.currentTarget).attr("name") === "onomy_url") {
	        jQuery(evt.currentTarget).addClass("default");
		jQuery(evt.currentTarget).attr("value", "Enter an Onomy URL here");
	    }
        }
        ,
        createOnomyVocabulary: function (evt) {
            evt.preventDefault();
            var et = jQuery(evt.currentTarget).prev();

            var self = this;
            var vocabulary_id;
            vocabulary_id = this.selected.get('id');
            //'http://www.corsproxy.com/' +
            //this should be sanitized in the future.
            onomyURL = jQuery(et).attr("value").trim();
            console.log(onomyURL);
            getTheOnomy(onomyURL, self);

        },
        refreshOnomy: function(evt)
        {
            var self = this;
            urlArray = _.map(self.collection.models, function(model){return model.attributes.onomy_url});
            var address;
            for (var i = 0; i < urlArray.length; i++)
            {
                address = urlArray[i].toString();
                if (!address == "")
                {
                    getTheOnomy(address, self);
                }

            }

//            console.log(self.collection);
//            var urlcsv = self.selected.get('onomy_url');
//            url = urlcsv.split(',');
//            url.push('http://testthis.com/allegedly/onomy');
//            //self.selected.get('onomy_url').add(urlcsv);
//            console.log(self.selected.get('onomy_url'));
        }





    });
    function findUtil(array, thing){
        return jQuery.grep(array, function(item){
            return item.display_name == thing;
        });
    };
    function getTheOnomy(dirtyURL, self)
    {
        var test;
        var onomyURL;
        var onomy_index;
        
	//this is to sanitize the url entered by the user.
	//checks to see if it contains onomy and json
	test = dirtyURL.search(('onomy' | 'json'));
	if (test != -1)
	{
	  //grab the numbers from the url entered
	  onomy_index = /\d+/g.exec(dirtyURL);
	}
	else
	{
	  //display error message
	  showMessage("Enter a valid Onomy URL", undefined, "Error");
	  return;
	}
	//all of the onomyURL's should fit this so i just strip the numbers from user
	//input and add it to the format
	onomyURL = 'http://onomy.org/published/' + onomy_index + '/json';
        var vocabulary_id;
        vocabulary_id = self.selected.get('id');
        jQuery.get(onomyURL,
                function (data) {
                    var x;
                    x = JSON.parse(data);

                    var MAX;
                    var parents = [];
                    MAX = x.terms.length; //change to x.terms.length after done testing
                    for (var i = 0; i < MAX; i++) {
                        var pL;
                        var display;
                        pL = x.terms[i]['rdfs:parentLabel'].trim();
                        display = x.terms[i]['rdfs:label'].trim();
                        console.log(pL);
                        console.log(display);
                        //demorgans law
                        if (!(pL === undefined || pL.length < 1)) {
                            var search = undefined;
                            parents.forEach(function(a){if(a.display_name == pL){search = a;}});
                            if(search === undefined)
                            {
                                //create the Vocabulary
                                temp = {'display_name': pL, 'term_set':[], 'self':undefined};
                                parents.push(temp);
                                parents[parents.indexOf(temp)].term_set.push({'display_name': display});
                            }
                            else
                            {
                                //add the term to the Vocabulary in parents
                                v = search;
                                parents[parents.indexOf(v)].term_set.push({'display_name': display});
                            }
                            if(i == MAX -1)
                            {
                                var tempV;
                                for (var j = 0; j < parents.length; j++)
                                {
                                    model_search = _.find(self.collection.models, function(model){return model.attributes.display_name == parents[j].display_name});
                                    if(model_search === undefined)
                                    {
                                        //if we cant find the vocab in the collection we create a new one.

                                        tempV = new Vocabulary({
                                            'display_name': parents[j].display_name,
                                            'content_type_id': 14,
                                            'object_id': 1,
                                            'term_set': undefined,
                                            'onomy_url': onomyURL
                                        });

                                        tempV._save({},{
                                            success: function(it){
                                                self.selected = it;
                                                console.log(parents);
                                                parents[parents.indexOf(findUtil(parents, it.attributes['display_name'])[0])].self = self.selected;
                                                self.collection.add(it);
                                                console.log('it');
                                                console.log(it);
                                                for (var z = 0; z < parents[parents.indexOf(findUtil(parents, it.attributes['display_name'])[0])].term_set.length; z ++)
                                                {
                                                    tempT = new Term({
                                                        'display_name':parents[parents.indexOf(findUtil(parents, it.attributes['display_name'])[0])].term_set[z].display_name,
                                                        'vocabulary_id': it.attributes['id']
                                                    });
                                                    tempT._save({},{
                                                        success: function (itT) {
                                                            parents[parents.indexOf(findUtil(parents, it.attributes['display_name'])[0])].self.get('term_set').add(itT);
                                                            self.render();
                                                        }
                                                    });
                                                }
                                            }});
                                    } else {
                                        //we do find the model. we just add the term to it.
                                        self.selected = model_search;
                                        var urlcsv;
                                        var url;
                                        urlcsv = self.selected.get('onomy_url');
                                        url = urlcsv.split(',');
                                        if(!(_.contains(url, onomyURL)))
                                        {
                                            url.push(onomyURL);
                                            model_search.save({'onomy_url': url.toString()});
                                        }

                                        for (var z = 0; z < parents[parents.indexOf(findUtil(parents, model_search.attributes['display_name'])[0])].term_set.length; z ++)
                                        {
                                            tempT = new Term({
                                                'display_name':parents[parents.indexOf(findUtil(parents, model_search.attributes['display_name'])[0])].term_set[z].display_name,
                                                'vocabulary_id': model_search.attributes['id']
                                            });
                                            tempT._save({},{
                                                success: function (itT) {
                                                    self.selected.get('term_set').add(itT);
                                                    self.render();
                                                }

                                            });
                                        }

                                    }



                                }
                            }

                        } else {

                            if (display === undefined || display.length < 1) {
                                continue;
                            }
                            var id;
                            var v;
                            var urlcsv;
                            var url;
                            console.log(self.selected);
                            id = self.selected.attributes.id;
                            v = self.collection.getByDataId(id);
                            urlcsv = self.selected.get('onomy_url');
                            url = urlcsv.split(',');

                            //if this vocabulary doesn't contain the url we punched in
                            if(!(_.contains(url, onomyURL)))
                            {
                                //add it to our array we made and save it in the vocab
                                url.push(onomyURL);
                                v.save({'onomy_url': url.toString()});
                            }
                            //we create our term
                            var t;
                            t = new Term({
                                'display_name': display,
                                'vocabulary_id': vocabulary_id
                            });
                            //then save it with our overriden queued save
                            t._save({}, {
                                wait: true,
                                success: function (it) {
                                    //add it to our term
                                    self.selected.get('term_set').add(it);
                                    self.render();
                                }
                            });
                        }
                    }
                });
    };


}(jQuery));


