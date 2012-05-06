(function() {
    var global = this;
    
    ///MUSTACHE CODE
    if (window.Mustache) {
        Mustache.set_pragma_default('EMBEDDED-PARTIALS', true);
        Mustache.set_pragma_default('FILTERS', true);
        Mustache.set_pragma_default('DOT-SEPARATORS', true);
        Mustache.set_pragma_default('?-CONDITIONAL', true);
        
        MediaThread.urls = {
            'annotation-form': function (asset_id, annotation_id) {
                return '/asset/' + asset_id + '/annotations/' + annotation_id;
            },
            'home-space': function (username) {
                return '/?username=' + username;
            },
            'your-space': function (username, tag, modified) {
                return '/yourspace/' + username + '/asset/?annotations=true' + (tag ? '&tag=' + tag : '') + (modified ? '&modified=' + modified : '');
            },
            'all-space': function (tag, modified) {
                return '/yourspace/all/asset/?' + (tag ? '&tag=' + tag : '') + (modified ? '&modified=' + modified : '');
            },
            'asset-delete': function (username, asset_id) {
                return '/yourspace/' + username + '/asset/' + asset_id + '/?delete';
            },
            'annotation-delete': function (asset_id, annotation_id) {
                return '/asset/' + asset_id + '/annotations/' + annotation_id + '/?delete';
            },
            'asset-view': function (asset_id) {
                return '/asset/' + asset_id + '/';
            },
            'asset-json': function (asset_id, with_annotations) {
                return '/asset/json/' + asset_id + (with_annotations ? '/?annotations=true' : '/');
            },
            'assets': function (username, with_annotations) {
                return '/annotations/' + (username ? username + '/' : '');
            },
            'create-annotation': function (asset_id) {
                // a.k.a. server-side annotation-containers
                return '/asset/' + asset_id + '/annotations/';
            },
            'edit-annotation': function (asset_id, annotation_id) {
                // a.k.a server-side annotation-form assetmgr:views.py:annotationview
                return '/asset/' + asset_id + '/annotations/' + annotation_id + '/';
            },
            'project-view': function (project_id) {
                return '/project/view/' + project_id + '/';
            },
            'project-readonly': function (project_id, version) {
                return '/project/view/' + project_id + '/version/' + version + '/';
            },
            'project-create': function () {
                return '/project/create/';
            },
            'discussion-create': function () {
                return '/discussion/new/';
            },
            'comment-edit': function (comment_id) {
                return '/discussion/comment/' + comment_id;
            },
            'comment-create': function () {
                return '/comments/post/';
            }
        };

        Mustache.Renderer.prototype.filters_supported.url = function (name, context, args) {
            var url_args = this.map(args, function (a) { return this.get_object(a, context, this.context); }, this);
            return MediaThread.urls[name].apply(this, url_args);
        };
        
        Mustache.Renderer.prototype.filters_supported['default'] = function (name, context, args) {
            var lookup = this.get_object(name, context, this.context);
            if (lookup) {
                return lookup;
            } else {
                return args[0];
            }
        };
    }//END MUSTACHE CODE

})();
