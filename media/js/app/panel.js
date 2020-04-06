/* global AssetPanelHandler: true */
/* global DiscussionPanelHandler: true, MediaThread: true */
/* global Mustache: true, panelFactory: true, ProjectPanelHandler: true */
/* global urlWithCourse */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function() {
    var PanelFactory = function() {
        this.create = function(el, $parent, type, panel, space_owner) {
            // Instantiate the panel's handler
            var handler = null;
            if (type === 'project') {
                handler = new ProjectPanelHandler(el, $parent, panel,
                    space_owner);
            } else if (type === 'discussion') {
                handler = new DiscussionPanelHandler(el, $parent, panel,
                    space_owner);
            } else if (type === 'asset') {
                handler = new AssetPanelHandler(el, $parent, panel,
                    space_owner);
            }

            return handler;
        };
    };
    window.panelFactory = new PanelFactory();

    var PanelManager = function() {
        var self = this;

        this.init = function(options, panels) {
            self.options = options;
            self.panelHandlers = [];
            self.$el = jQuery('#' + options.container);

            jQuery.ajax({
                url: urlWithCourse(options.url),
                method: 'GET',
                dataType: 'json',
                cache: false, // Chrome & IE cache aggressively
                success: function(json) {
                    self.panels = json.panels;
                    self.space_owner = json.space_owner;

                    var templates = [];
                    jQuery.each(self.panels, function(idx, e) {
                        templates.push(e.template);
                    });

                    jQuery.when.apply(
                        this,
                        MediaThread.loadTemplates(templates)
                    ).then(function() {
                        self.loadContent();
                    });
                }
            });
        };

        this.loadTemplates = function(idx) {
            if (idx === self.panels.length) {
                // done. load content.
                self.loadContent();
            } else if (MediaThread.templates[self.panels[idx].template]) {
                // it's already cached
                self.loadTemplates(++idx);
            } else {
                // pull it off the wire
                MediaThread.loadTemplate(self.panels[idx].template)
                    .then(function() {
                        self.loadTemplates(++idx);
                    });
            }
        };

        this.loadContent = function() {
            for (var i = 0; i < self.panels.length; i++) {
                var panel = self.panels[i];
                var $elt = jQuery('#' + panel.context.type + '-container');
                panel = jQuery.extend({}, panel, MediaThread.mustacheHelpers);
                var section = Mustache.render(
                    MediaThread.templates[panel.template], panel);
                $elt.append(section);

                var handler = panelFactory.create(
                    $elt,
                    self.$el,
                    self.panels[i].context.type,
                    self.panels[i],
                    self.space_owner);
                self.panelHandlers.push(handler);
                self.panels[i].loaded = true;
            }
        };

        this.newPanel = function(options) {
            jQuery.ajax({
                type: 'POST',
                url: options.url,
                dataType: 'json',
                data: options.params,
                success: function(json) {
                    if (options.callback) {
                        options.callback(json);
                    } else {
                        var length = self.panels.push(json);
                        self.loadTemplates(length - 1);
                    }
                }
            });
        };
    };
    window.panelManager = new PanelManager();
})();
