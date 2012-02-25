(function() {
    
    window.CollectionList = new (function CollectionListAbstract() {
        var self = this;
                
        this.init = function(config) {
            self.template_label = config.template_label;
            self.view_callback = config.view_callback;
            self.create_annotation_thumbs = config.create_annotation_thumbs;
            self.project_id = config.project_id;
            self.parent = config.parent;

            self.switcher_context = {}
            self.switcher_context.enable_project_selection = config.enable_project_selection;
            
            // add some flair to the collection table
            jQuery("div#" + config.template_label).ajaxStart(function(){
                jQuery(this).addClass("ajaxLoading");
            });
            
            jQuery("div#" + config.template_label).ajaxStop(function(){
                jQuery(this).removeClass("ajaxLoading");
            });

            
            jQuery.ajax({
                url:'/site_media/templates/' + config.template + '.mustache?nocache=v2',
                dataType:'text',
                cache: false, // Chrome && Internet Explorer has aggressive caching policies.
                success:function(text) {
                    MediaThread.templates[config.template] = Mustache.template(config.template,text);
                    
                    // Retrieve the full asset w/annotations from storage
                    if (config.view == 'all' || !config.space_owner) {
                        url = MediaThread.urls['all-space'](config.tag)
                    } else {
                        url = MediaThread.urls['your-space'](config.space_owner, config.tag)
                    }  
                    djangosherd.storage.get({
                            type:'asset',
                            url: url
                        },
                        false,
                        function(the_records) {
                            self.updateAssets(the_records);
                        });
                    }
                });
            
            return this;
        }

        this.selectOwner = function(username) {
            djangosherd.storage.get({
                type:'asset',
                url: username ? MediaThread.urls['your-space'](username) : MediaThread.urls['all-space']()
            },
            false,
            function(the_records) {
                self.updateAssets(the_records);
                
                jQuery("#project_view").hide();
                jQuery("#asset_table").show();
                jQuery("#switcher-collection-filter").show();
            });
            
            return false;
        }
        
        this.selectProject = function(username) {
            // update selected label & switcher choices
            self.switcher_context.selected_label = self.current_project.project.title;
            self.switcher_context.showing_all_items = false;
            self.switcher_context.showing_my_items = false;
            self.updateSwitcher();
            
            // hide assets, show project
            jQuery("#asset_table").hide();
            jQuery("#project_view").show();
            jQuery("#switcher-collection-filter").hide();
            
            return false;
        }
        
        this.deleteAsset = function(asset_id) {
            var url = MediaThread.urls['asset-delete'](self.current_records.space_viewer.username, asset_id);
            return ajaxDelete(null, 'record-' + asset_id, { 'href': url });
        }
        
        this.deleteAnnotation = function(annotation_id) {
            var asset_id = jQuery('#annotation-' + annotation_id).parents("div.record").children("input.record").attr("value");
            var url = MediaThread.urls['annotation-delete'](asset_id, annotation_id);
            return ajaxDelete(null, 'annotation-' + annotation_id, { 'href': url });
        }
        
        this.clearFilter = function(filterName) {
            var active_tag = null;
            var active_modified = null;
                
            if (filterName == 'tag')
                active_modified = ('modified' in self.current_records.active_filters) ? self.current_records.active_filters.modified : null;
            else if (filterName == 'modified')
                active_tag = ('tag' in self.current_records.active_filters) ? self.current_records.active_filters.tag : null;
            
            djangosherd.storage.get({
                type:'asset',
                url: self.getSpaceUrl(active_tag, active_modified)
            },
            false,
            function(the_records) {
                self.updateAssets(the_records);
            });
            
            return false;
        }
        
        this.filterByDate = function(modified) {
            var active_tag = ('tag' in self.current_records.active_filters) ? self.current_records.active_filters.tag : null;
            djangosherd.storage.get({
                type:'asset',
                url:self.getSpaceUrl(active_tag, modified)
            },
            false,
            function(the_records) {
                self.updateAssets(the_records);
            });
            
            return false;
        }
        
        this.filterByTag = function(tag) {
            var active_modified = ('modified' in self.current_records.active_filters) ? self.current_records.active_filters.modified : null;
            djangosherd.storage.get({
                type:'asset',
                url:self.getSpaceUrl(tag, active_modified)
            },
            false,
            function(the_records) {
                self.updateAssets(the_records);
            });
            
            return false;
        }

        this.getShowingAllItems = function(json) {
            return !json.hasOwnProperty('space_owner'); 
        }
        
        this.getSpaceUrl = function(active_tag, active_modified) {
           if (self.getShowingAllItems(self.current_records))
                return MediaThread.urls['all-space'](active_tag, active_modified)
           else
                return MediaThread.urls['your-space'](self.current_records.space_owner.username, active_tag, active_modified)
        }
        
        this.createThumbs = function(assets) {
            djangosherd.thumbs = [];
            for (var i = 0; i < assets.length; i++) {
                var asset = assets[i];
                DjangoSherd_adaptAsset(asset); //in-place
                if (asset.thumbable && asset.annotations) {
                    for (var j = 0; j < asset.annotations.length; j++) {
                        ann = asset.annotations[j];
                        
                        var view;
                        switch(asset.type) {
                        case 'image':
                            view = new Sherd.Image.OpenLayers();
                            break;
                        case 'fsiviewer':
                            view = new Sherd.Image.FSIViewer();
                            break;
                        }
                        djangosherd.thumbs.push(view);
                        var obj_div = document.createElement('div');
                        obj_div.setAttribute('class','annotation-thumb');
        
                        var target_div = document.getElementById("annotation-thumb-" + ann.id);
                        target_div.appendChild(obj_div);
                        // should probably be in .view
                        asset.presentation = 'thumb';

                        ann.asset = asset;
                        view.html.push(obj_div, ann);
                        view.setState(ann.annotation);
                    }
                }
            }
        }
        
        this.updateProject = function() {
            var url = MediaThread.urls['project-workspace'](self.project_id);
            
            // retrieve project json
            djangosherd.storage.get({
                type:'project',
                url: url
            }, 
            false,
            function(the_project) {
                self.current_project = the_project;
                self.switcher_context.project = the_project.project;
                
                if (self.switcher_context.enable_project_selection) {
                    // push the body of the project into a div
                    Mustache.update("project_view", the_project, { post:function(elt) {
                        var cv = new CitationView();
                        cv.init({});
                        cv.decorateLinks('project_view');
                        
                        self.selectProject();
                    }});
                } else {
                    self.updateSwitcher();
                }
            });
        }
        
        this.updateSwitcher = function() {
            self.switcher_context.display_switcher_extras = self.enable_project_selection || !self.switcher_context.showing_my_items || (self.current_project && self.current_project.project.participants.length > 1);
            Mustache.update("switcher_collection_chooser", self.switcher_context);
        }
        
        this.updateAssets = function(the_records) {
            self.switcher_context.owners = the_records.owners;
            self.switcher_context.space_viewer = the_records.space_viewer;
            
            if (self.getShowingAllItems(the_records)) {
                self.switcher_context.selected_label = "All Class Members";
                self.switcher_context.showing_all_items = true;
                self.switcher_context.showing_my_items = false;
                the_records.showing_all_items = true;
            } else if (the_records.space_owner.username == the_records.space_viewer.username) {
                self.switcher_context.selected_label = "Me";
                self.switcher_context.showing_my_items = true;
                self.switcher_context.showing_all_items = false;
                the_records.showing_my_items = true;
            } else {
                self.switcher_context.showing_my_items = false;
                self.switcher_context.showing_all_items = false;
                self.switcher_context.selected_label = the_records.space_owner.public_name;
            }
            
            self.current_records = the_records;
            
            n = _propertyCount(the_records.active_filters);
            if (n > 0)
                the_records.active_filter_count = n;
            
            Mustache.update(self.template_label, the_records, {
                parent: self.parent,
                pre:function(elt) { jQuery(elt).hide(); },
                post:function(elt) {
                    if (self.create_annotation_thumbs)
                        self.createThumbs(the_records.assets);
                    
                    if (self.project_id && !self.current_project) 
                        self.updateProject();
                    else
                        self.updateSwitcher();
                    
                    jQuery(elt).fadeIn("slow");
                    
                    jQuery("body").trigger("resize");
                    
                    var editors = jQuery(self.parent).find("textarea.mceEditor");
                    if (editors.length) {
                        var ed = tinyMCE.get(editors[0].id);

                        var new_assets = jQuery(self.parent).find('.asset-table').get(0);
                           
                        ed.plugins.citation.decorateCitationAdders(new_assets);
                        jQuery(new_assets.parentNode).addClass('annotation-embedding');
                    }
                    
                    if (self.view_callback) 
                        self.view_callback();
            }});
        }
    })();
})();
    