/* global MediaThread: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function() {
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
        'asset-json': function(assetId, withAnnotations, parentId) {
            if (parentId !== undefined) {
                return '/api/project/' + parentId + '/' + assetId + '/';
            } else {
                return '/api/asset/' + assetId +
                    (withAnnotations ? '/?annotations=true' : '/');
            }
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

    /**
     * Load a Mustache template from the /media/templates/
     * directory and put it in the MediaThread.templates
     * dictionary.
     *
     * Returns a promise.
     */
    MediaThread.loadTemplate = function(templateName) {
        if (typeof MediaThread.templates[templateName] === 'undefined') {
            return jQuery.ajax({
                url: '/media/templates/' +
                    templateName + '.mustache?nocache=v2',
                dataType: 'text',
                cache: false,
                success: function(text) {
                    MediaThread.templates[templateName] = text;
                }
            });
        } else {
            // The template was already loaded, so just resolve this
            // promise.
            var dfd = jQuery.Deferred();
            return dfd.resolve(MediaThread.templates[templateName]);
        }
    };

    /**
     * Load all the templates, given an array of template names.
     *
     * Returns an array of jqXHR objects.
     */
    MediaThread.loadTemplates = function(templates) {
        var promises = [];

        for (var i = 0; i < templates.length; i++) {
            promises.push(MediaThread.loadTemplate(templates[i]));
        }

        return promises;
    };

    /**
     * A collection of helper functions for rendering our mustache
     * templates.
     *
     * See: https://github.com/janl/mustache.js#functions
     *
     * These functions aren't able to take any parameters passed
     * in via the template. If we need that functionality we can
     * switch to handlebars.
     */
    MediaThread.mustacheHelpers = {
        lower: function() {
            return function(text, render) {
                return render(text).toLowerCase();
            };
        }
    };
})();
