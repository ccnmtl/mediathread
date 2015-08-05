/* global MediaThread: true, Mustache: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function() {
    var global = this;

    ///MUSTACHE CODE
    if (window.Mustache) {
        Mustache.set_pragma_default('EMBEDDED-PARTIALS', true);
        Mustache.set_pragma_default('FILTERS', true);
        Mustache.set_pragma_default('DOT-SEPARATORS', true);
        Mustache.set_pragma_default('?-CONDITIONAL', true);

        MediaThread.urls = {
            'annotation-form': function(assetId, annotationId) {
                return '/asset/' + assetId + '/annotations/' + annotationId;
            },
            'home-space': function(username) {
                return '/?username=' + username;
            },
            'your-projects': function(username) {
                return '/api/project/user/' + username + '/';
            },
            'all-projects': function() {
                return '/api/project/';
            },
            'sort-projects': function() {
                return '/project/sort/';
            },
            'your-space': function(username, tag, modified, citable) {
                return '/api/asset/user/' + username + '/?' +
                    (citable ? '&annotations=true' : '') +
                    (tag ? '&tag=' + tag : '') +
                    (modified ? '&modified=' + modified : '') +
                    (citable ? '&citable=' + citable : '');
            },
            'all-space': function(tag, modified, citable) {
                return '/api/asset/?' +
                    (tag ? '&tag=' + tag : '') +
                    (modified ? '&modified=' + modified : '') +
                    (citable ? '&citable=' + citable : '');
            },
            'asset-workspace': function(assetId, annotationId) {
                var base = '/asset/';
                if (assetId) {
                    base += assetId + '/';
                    if (annotationId) {
                        base += 'annotations/' + annotationId + '/';
                    }
                }
                return base;
            },
            'assets': function(username, withAnnotations) {
                return '/annotations/' + (username ? username + '/' : '');
            },
            'asset-delete': function(assetId) {
                return '/asset/delete/' + assetId + '/';
            },
            'asset-view': function(assetId) {
                return '/asset/' + assetId + '/';
            },
            'asset-json': function(assetId, withAnnotations) {
                return '/api/asset/' + assetId +
                    (withAnnotations ? '/?annotations=true' : '/');
            },
            'annotation-create': function(assetId) {
                // a.k.a. server-side annotation-containers
                return '/asset/create/' + assetId + '/annotations/';
            },
            'annotation-create-global': function(assetId) {
                // a.k.a. server-side annotation-containers
                return '/asset/create/' + assetId + '/global/';
            },
            'annotation-edit': function(assetId, annotationId) {
                // server-side annotation-form assetmgr:views.py:annotationview
                return '/asset/save/' + assetId +
                    '/annotations/' + annotationId + '/';
            },
            'annotation-delete': function(assetId, annotationId) {
                return '/asset/delete/' + assetId +
                    '/annotations/' + annotationId + '/';
            },
            'project-view': function(projectId) {
                return '/project/view/' + projectId + '/';
            },
            'project-feedback': function(projectId) {
                return '/project/view/' + projectId + '/feedback/';
            },
            'project-readonly': function(projectId, version) {
                return '/project/view/' + projectId +
                    '/version/' + version + '/';
            },
            'project-create': function() {
                return '/project/create/';
            },
            'project-save': function(projectId) {
                return '/project/save/' + projectId + '/';
            },
            'project-revisions': function(projectId) {
                return '/project/revisions/' + projectId + '/';
            },
            'discussion-view': function(discussionId) {
                return '/discussion/' + discussionId + '/';
            },
            'discussion-create': function() {
                return '/discussion/create/';
            },
            'comment-edit': function(commentId) {
                return '/discussion/comment/' + commentId + '/';
            },
            'comment-create': function() {
                return '/comments/post/';
            },
            'tags': function() {
                return '/api/tag/';
            },
            'references': function(asset) {
                return '/asset/references/' + asset.id + '/';
            },
            'selection-assignment-workspace': function(assetId) {
                return '/asset/' + assetId + '/?standalone=1';
            }
        };

        Mustache.Renderer.prototype.filters_supported.url =
            function(name, context, args) {
                var urlArgs = this.map(args, function(a) {
                        return this.get_object(a, context, this.context);
                    }, this);
                return MediaThread.urls[name].apply(this, urlArgs);
            };
        Mustache.Renderer.prototype.filters_supported.ellipses =
            function(name, context, args) {
                var length = parseInt(args[0], 10);
                var str = this.get_object(name, context, this.context);
                var value = String(str || '');
                if (value.length > length) {
                    value = value.substring(0, length) + '...';
                }
                return value;
            };
        Mustache.Renderer.prototype.filters_supported.upper =
            function(name, context, args) {
                var str = this.get_object(name, context, this.context);
                var value = String(str || '');
                return value.toUpperCase();
            };
        Mustache.Renderer.prototype.filters_supported.lower =
            function(name, context, args) {
                var str = this.get_object(name, context, this.context);
                var value = String(str || '');
                return value.toLowerCase();
            };
        Mustache.Renderer.prototype.filters_supported.default =
            function(name, context, args) {
                var lookup = this.get_object(name, context, this.context);
                if (lookup) {
                    return lookup;
                } else {
                    return args[0];
                }
            };
    }//END MUSTACHE CODE

})();
