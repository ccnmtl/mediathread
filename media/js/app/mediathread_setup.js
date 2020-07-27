/* global MediaThread: true, STATIC_URL: true */
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
        'your-space': function(username, tag, modified, citable, mediaType) {
            return '/api/asset/user/' + username + '/?' +
                (tag ? '&tag=' + tag : '') +
                (modified ? '&modified=' + modified : '') +
                (citable ? '&annotations=true' : '') +
                (citable ? '&citable=' + citable : '') +
                (mediaType ? '&media_type=' + mediaType : '');
        },
        'all-space': function(tag, modified, citable, mediaType) {
            return '/api/asset/?' +
                (tag ? '&tag=' + tag : '') +
                (modified ? '&modified=' + modified : '') +
                (citable ? '&annotations=true' : '') +
                (citable ? '&citable=' + citable : '') +
                (mediaType ? '&media_type=' + mediaType : '');
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
        'annotation-copy': function(assetId, annotationId) {
            return '/asset/copy/' + assetId +
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
        'project-response': function(courseId, projectId) {
            return '/course/' + courseId + '/project/response/'
                + projectId + '/';
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
                url: STATIC_URL + 'templates/' +
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
     * {{ellipsis}}
     * Truncate the input string and removes all HTML tags
     *
     * @param  {String} str      The input string.
     * @param  {Number} limit    The number of characters to limit the string.
     * @param  {String} append   The string to append if charaters are omitted.
     * @return {String}          The truncated string.
     */
    var ellipsis = function(str, limit, append) {
        if (typeof append === 'undefined') {
            append = '…';
        }

        var sanitized = str.replace(/(<([^>]+)>)/g, '');
        if (sanitized.length > limit) {
            return sanitized.substr(0, limit - append.length) + append;
        } else {
            return sanitized;
        }
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
        staticUrl: function() {
            return function(text, render) {
                return render(STATIC_URL);
            };
        },
        ellipsis18: function() {
            return function(text, render) {
                return ellipsis(render(text), 18);
            };
        },
        ellipsis35: function() {
            return function(text, render) {
                return ellipsis(render(text), 35);
            };
        },
        lower: function() {
            return function(text, render) {
                return render(text).toLowerCase();
            };
        },
        getCourseId: function() {
            return MediaThread.current_course;
        },
        addressableCourses: MediaThread.addressable_courses
    };

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    jQuery.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                var csrftoken = jQuery('[name="csrf-token"]');
                if (csrftoken.length > 0) {
                    var csrftokenval = csrftoken[0].content;
                    xhr.setRequestHeader('X-CSRFToken', csrftokenval);
                }
            }
        }
    });
})();
