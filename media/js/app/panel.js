/* global AssetPanelHandler: true, getVisibleContentHeight: true */
/* global DiscussionPanelHandler: true, MediaThread: true */
/* global Mustache: true, panelFactory: true, ProjectPanelHandler: true */
/* global tinymce: true, tinymceSettings: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function() {
    var PanelFactory = function() {
        this.create = function(el, parent, type, panels, space_owner) {
            // Instantiate the panel's handler
            var handler = null;
            if (type === 'project') {
                handler = new ProjectPanelHandler(el, parent, panels,
                                                  space_owner);
            } else if (type === 'discussion') {
                handler = new DiscussionPanelHandler(el, parent, panels,
                                                     space_owner);
            } else if (type === 'asset') {
                handler = new AssetPanelHandler(el, parent, panels,
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
            self.el = jQuery('#' + options.container)[0];

            jQuery.ajax({
                url: options.url,
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

            jQuery(window).resize(function() {
                self.resize();
            });
        };

        this.count = function() {
            return self.panelHandlers.length;
        };

        this.resize = function() {
            var visible = getVisibleContentHeight();
            jQuery(self.el).css('height', visible + 'px');
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
            var slidePanelCallback = function(event) {
                self.slidePanel(this, event);
            };

            for (var i = 0; i < self.panels.length; i++) {
                var panel = self.panels[i];
                if (!panel.hasOwnProperty('loaded')) {

                    // Add these new columns to the table, before the last
                    // column. The last column is reserved for a placeholder td
                    // that eats space and makes the sliding UI work nicely
                    var $lastCell = jQuery('#' + self.options.container +
                                          ' tr:first td:last');
                    $lastCell.before(
                        Mustache.render(MediaThread.templates[panel.template],
                                        panel));

                    var newCell = $lastCell.prev().prev()[0];
                    var handler = panelFactory.create(
                        newCell,
                        self.el,
                        self.panels[i].context.type,
                        self.panels[i],
                        self.space_owner);
                    self.panelHandlers.push(handler);

                    // enable open/close controls on subpanel
                    jQuery(newCell)
                        .find('.pantab-container')
                        .on('click',
                            {handler: handler, isSubpanel: true},
                            slidePanelCallback);

                    // enable open/close controls on parent panels
                    jQuery(newCell)
                        .next('.pantab-container')
                        .on('click',
                            {handler: handler, isSubpanel: false},
                            slidePanelCallback);

                    // @todo -- update history to reflect this new view

                    panel.loaded = true;

                    self.verifyLayout(newCell);
                }
            }
        };

        this.slidePanel = function(pantab_container, event) {
            // Open/close this panhandle's panel
            var panel = jQuery(pantab_container).prevAll(
                'td.panel-container')[0];

            var param;
            var panelTab;
            if (jQuery(panel).hasClass('minimized') ||
                    jQuery(panel).hasClass('maximized')) {
                param = jQuery(panel).hasClass('minimized') ?
                    'maximized' : 'minimized';
                jQuery(panel).toggleClass('minimized maximized');
                jQuery(panel).trigger('panel_state_change', [param]);

                panelTab = jQuery(pantab_container).children('div.pantab')[0];
                jQuery(panelTab).toggleClass('minimized maximized');

                if (param === 'maximized') {
                    jQuery(panel).siblings('td.panel-container').hide();
                    jQuery(panel).css('display', 'table-cell');
                } else {
                    jQuery(panel).siblings('td.panel-container').show();
                }

                self.verifyLayout(panel);
                jQuery(window).trigger('resize');
            } else {
                param = jQuery(panel).hasClass('open') ? 'closed' : 'open';
                jQuery(panel).toggleClass('open closed');
                jQuery(panel).trigger('panel_state_change', [param]);

                panelTab = jQuery(pantab_container).children('div.pantab')[0];
                jQuery(panelTab).toggleClass('open closed');

                self.verifyLayout(panel);
                jQuery(window).trigger('resize');
            }
        };

        this.openSubPanel = function(subpanel) {
            if (subpanel) {
                jQuery(subpanel).removeClass('closed').addClass('open');
                jQuery(subpanel).trigger('panel_state_change', ['open']);

                var container =
                    jQuery(subpanel).nextAll('td.pantab-container');
                var panelTab = jQuery(container[0]).children('div.pantab');
                jQuery(panelTab[0]).removeClass('closed');
                jQuery(panelTab[0]).addClass('open');

                self.verifyLayout(subpanel);
                jQuery(window).trigger('resize');
            }
        };

        this.closeSubPanel = function(view) {
            var subpanel = jQuery(view.el).find('td.panel-container.open')[0];

            jQuery(subpanel).removeClass('open').addClass('closed');
            jQuery(subpanel).trigger('panel_state_change', ['closed']);

            var panelTab = jQuery(subpanel).next()
                                           .next()
                                           .children('div.pantab')[0];
            jQuery(panelTab).toggleClass('open closed');

            self.verifyLayout(subpanel);
            jQuery(window).trigger('resize');
        };

        this.verifyLayout = function(panel) {
            var screenWidth = jQuery(window).width();
            var tableWidth = jQuery(self.el).width();

            var elts = jQuery(panel).parents('td.panel-container.open');
            var parent = elts.length > 0 ? elts[0] : null;

            // Try really minimizing the minimized guys first
            var a = jQuery(self.el).find(
                'table.panel-subcontainer td.panel-container.minimized');
            for (var i = 0; i < a.length && tableWidth > screenWidth; i++) {
                var subcontainer = a[i];
                jQuery(subcontainer).css('display', 'none');
                tableWidth = jQuery(self.el).width();
            }

            // Try closing the subpanels first
            a = jQuery(self.el).find(
                'table.panel-subcontainer tbody tr td.panel-container.open')
                .not('.alwaysopen');
            for (i = 0; i < a.length && tableWidth > screenWidth; i++) {
                var p = a[i];
                if (panel !== p) {
                    // close it
                    jQuery(p).removeClass('open').addClass('closed');
                    jQuery(p).trigger('panel_state_change', ['closed']);

                    var container = jQuery(p).nextAll('td.pantab-container');
                    var panelTab = jQuery(container[0]).children('div.pantab');
                    jQuery(panelTab[0]).removeClass('open').addClass('closed');

                    tableWidth = jQuery(self.el).width();
                }
            }

            // Then go for the parent panels
            a = jQuery(self.el).find('tr.sliding-content-row')
                .children('td.panel-container.open:visible')
                .not('.alwaysopen');
            if (a.length > 1) {
                for (i = 0; i < a.length && tableWidth > screenWidth; i++) {

                    if (a[i] !== panel && a[i] !== parent) {
                        // close it
                        jQuery(a[i]).removeClass('open').addClass('closed');
                        jQuery(a[i]).trigger('panel_state_change', ['closed']);

                        var parentContainer =
                            jQuery(a[i]).nextAll('td.pantab-container')[0];
                        var parentPanelTab =
                            jQuery(parentContainer).children('div.pantab')[0];
                        jQuery(parentPanelTab).removeClass('open')
                                              .addClass('closed');

                        tableWidth = jQuery(self.el).width();
                    }
                }
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

        this.openPanel = function(panel) {
            // Open this panel
            if (jQuery(panel).hasClass('closed')) {
                jQuery(panel).removeClass('closed').addClass('open');
                jQuery(panel).trigger('panel_state_change', ['open']);

                var panelTab = jQuery(panel).next().children('div.pantab')[0];
                jQuery(panelTab).toggleClass('open closed');

                self.verifyLayout(panel);
                jQuery(window).trigger('resize');
            }
        };

        this.maximizePanel = function(panel) {
            if (jQuery(panel).hasClass('minimized')) {
                jQuery(panel).removeClass('minimized').addClass('maximized');
                jQuery(panel).siblings('td.panel-container').hide();

                var panelTab = jQuery(panel).next().children('div.pantab')[0];
                jQuery(panelTab).parent()
                                .removeClass('minimized')
                                .addClass('maximized');
                jQuery(panelTab).removeClass('minimized')
                                .addClass('maximized');

                self.verifyLayout(panel);
                jQuery(window).trigger('resize');
            }
        };
    };
    window.panelManager = new PanelManager();
})();
