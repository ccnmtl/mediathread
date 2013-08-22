(function () {
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
            'your-projects': function (username) {
                return '/yourspace/projects/' + username + '/';
            },
            'all-projects': function () {
                return '/yourspace/projects/';
            },
            'sort-projects': function () {
                return '/project/sort/';
            },
            'your-space': function (username, tag, modified, citable) {
                return '/asset/json/user/' + username + '/?' +
                    (citable ? '&annotations=true' : '') +
                    (tag ? '&tag=' + tag : '') +
                    (modified ? '&modified=' + modified : '') +
                    (citable ? '&citable=' + citable : '');
            },
            'all-space': function (tag, modified, citable) {
                return '/asset/json/course/?' +
                    (tag ? '&tag=' + tag : '') +
                    (modified ? '&modified=' + modified : '') +
                    (citable ? '&citable=' + citable : '');
            },
            'asset-workspace': function (asset_id, annotation_id) {
                var base = '/asset/';
                if (asset_id) {
                    base += asset_id + '/';
                    if (annotation_id) {
                        base += 'annotations/' + annotation_id + '/';
                    }
                }
                return base;
            },
            'assets': function (username, with_annotations) {
                return '/annotations/' + (username ? username + '/' : '');
            },
            'asset-delete': function (asset_id) {
                return '/asset/delete/' + asset_id + '/';
            },
            'asset-view': function (asset_id) {
                return '/asset/' + asset_id + '/';
            },
            'asset-json': function (asset_id, with_annotations) {
                return '/asset/json/' + asset_id + (with_annotations ? '/?annotations=true' : '/');
            },
            'annotation-create': function (asset_id) {
                // a.k.a. server-side annotation-containers
                return '/asset/create/' + asset_id + '/annotations/';
            },
            'annotation-create-global': function (asset_id) {
                // a.k.a. server-side annotation-containers
                return '/asset/create/' + asset_id + '/global/';
            },
            'annotation-edit': function (asset_id, annotation_id) {
                // a.k.a server-side annotation-form assetmgr:views.py:annotationview
                return '/asset/save/' + asset_id + '/annotations/' + annotation_id + '/';
            },
            'annotation-delete': function (asset_id, annotation_id) {
                return '/asset/delete/' + asset_id + '/annotations/' + annotation_id + '/';
            },
            'project-view': function (project_id) {
                return '/project/view/' + project_id + '/';
            },
            'project-feedback': function (project_id) {
                return '/project/view/' + project_id + '/feedback/';
            },
            'project-readonly': function (project_id, version) {
                return '/project/view/' + project_id + '/version/' + version + '/';
            },
            'project-create': function () {
                return '/project/create/';
            },
            'discussion-view': function (discussion_id) {
                return '/discussion/' + discussion_id + "/";
            },
            'discussion-create': function () {
                return '/discussion/create/';
            },
            'comment-edit': function (comment_id) {
                return '/discussion/comment/' + comment_id + '/';
            },
            'comment-create': function () {
                return '/comments/post/';
            },
            'tags': function () {
                return '/_main/api/v1/tag/';
            },
            'references': function (asset) {
                return '/asset/references/' + asset.id + '/';
            }
        };

        Mustache.Renderer.prototype.filters_supported.url = function (name, context, args) {
            var url_args = this.map(args, function (a) { return this.get_object(a, context, this.context); }, this);
            return MediaThread.urls[name].apply(this, url_args);
        };
        
        Mustache.Renderer.prototype.filters_supported.ellipses = function (name, context, args) {
            var length = parseInt(args[0], 10);
            var value = String(this.get_object(name, context, this.context) || '');
            if (value.length > length) {
                value = value.substring(0, length) + "...";
            }
            return value;
        };
        Mustache.Renderer.prototype.filters_supported.upper = function (name, context, args) {
            var value = String(this.get_object(name, context, this.context) || '');
            return value.toUpperCase();
        };
        Mustache.Renderer.prototype.filters_supported.lower = function (name, context, args) {
            var value = String(this.get_object(name, context, this.context) || '');
            return value.toLowerCase();
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
