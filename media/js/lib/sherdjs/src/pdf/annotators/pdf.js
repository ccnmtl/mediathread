/* global Sherd: true */

import {
    pdfjsScale, isValidAnnotation, drawAnnotation, renderPage
} from '../../../../../pdf/utils.js';

if (!Sherd) { Sherd = {}; }
if (!Sherd.Pdf) { Sherd.Pdf = {}; }
if (!Sherd.Pdf.Annotators) { Sherd.Pdf.Annotators = {}; }
if (!Sherd.Pdf.Annotators.Pdf) {
    Sherd.Pdf.Annotators.Pdf = function () {
        var self = this;
        Sherd.Base.AssetView.apply(this, arguments);//inherit

        this.state = {
            pdfRect: null,
            showClear: false,
            showCancel: false
        };

        this.attachView = function (view) {
            self.targetview = view;
        };
        this.targetstorage = [];
        this.addStorage = function (stor) {
            this.targetstorage.push(stor);
        };

        this.getState = function () {
            if (!this.state.pdfRect) {
                return 'missing pdfRect';
            }

            return {
                type: 'Rectangle',
                geometry: {
                    coordinates: this.state.pdfRect.coords ||
                        this.state.pdfRect.coordinates,
                    page: this.state.pdfRect.page
                }
            };
        };

        this.current_state = null;

        // Called by asset.js
        this.setState = function (obj, options) {
            if (typeof obj === 'object') {
                self.current_state = obj;

                if (obj.geometry) {
                    self.state.pdfRect = obj.geometry;
                }

                self.mode = null;

                if (isValidAnnotation(obj)) {
                    const data = obj.geometry;
                    data.message = 'onViewSelection';
                    if (document.forms['annotation-list-filter']) {
                        data.showall = document.forms['annotation-list-filter']
                            .elements.showall.checked;
                    }

                    const iframe = window.jQuery('iframe.pdfjs')[0];
                    if (iframe) {
                        iframe.addEventListener('load', function(e) {
                            e.target.contentWindow.postMessage(data, '*');
                        });
                    }
                }
            }
        };

        self.refreshButtons = function() {
            const $cancel = jQuery('.quickedit-cancel-button');
            const $clear = jQuery('.quickedit-clear-button');

            if (self.state.showCancel) {
                $cancel.show();
            } else {
                $cancel.hide();
            }

            if (self.state.showClear) {
                $clear.show();
            } else {
                $clear.hide();
            }
        };

        this.initialize = function (create_obj) {
            window.onmessage = function(e) {
                if (
                    e.data.message &&
                        e.data.message === 'pdfAnnotationRectCreated'
                ) {
                    self.state.pdfRect = e.data.rect;
                    self.state.showCancel = false;
                    self.state.showClear = true;
                } else if (
                    e.data.message &&
                        e.data.message === 'pdfAnnotationRectStarted'
                ) {
                    self.state.showCancel = false;
                    self.state.showClear = true;
                }

                self.refreshButtons();
            };

            ///button listeners
            self.events.connect(self.components.rect, 'click', function (evt) {
                const iframe = window.jQuery('iframe.pdfjs')[0];
                if (iframe) {
                    iframe.contentWindow.postMessage(
                        'enableRectangleTool', '*');
                }

                self.state.showCancel = true;
                self.state.showClear = false;
                self.refreshButtons();
            });

            self.events.connect(self.components.cancel, 'click', function (evt) {
                const iframe = window.jQuery('iframe.pdfjs')[0];
                if (iframe) {
                    iframe.contentWindow.postMessage(
                        'disableRectangleTool', '*');
                }

                self.state.showCancel = false;
                self.refreshButtons();
            });

            self.events.connect(self.components.clear, 'click', function (evt) {
                const iframe = window.jQuery('iframe.pdfjs')[0];
                if (iframe) {
                    iframe.contentWindow.postMessage(
                        'onClearSelection', '*');
                }

                self.state.showClear = false;
                self.refreshButtons();
            });
        };
        this.storage = {
            'update': function (obj, just_downstream) {
                if (!just_downstream) {
                    self.setState(obj);
                }
                for (var i = 0; i < self.targetstorage.length; i++) {
                    self.targetstorage[i].storage.update(obj);
                }
            }
        };
        this.microformat = {
            'create': function () {
                var id = Sherd.Base.newID('pdfjs-annotator');
                return {
                    htmlID: id,
                    text: '<div id="' + id + '" class="toolbar-annotations toolbar-annotation p-3 bg-dark text-white">' +
                        '<form>' +
                        '<div class="form-row align-items-center">' +

                    '<button type="button" class="btn btn-secondary mr-1 rectangle-button">' +
                        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-square" viewBox="0 0 16 16"><path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"></path></svg>' +
                        ' Rectangle' +
                        '</button>' +

                    '<button type="button" ' +
                        'style="display: none;" ' +
                        'class="ml-auto btn btn-danger quickedit-cancel-button">' +
                        'Cancel' +
                        '</button>' +

                    '<button type="button" ' +
                        'style="display: none;" ' +
                        'class="ml-auto btn btn-danger quickedit-clear-button">' +
                        'Clear' +
                        '</button>' +

                    '</div>' +
                        '</form>' +
                        '</div>'
                };
            },
            'components': function (html_dom, create_obj) {
                if (!html_dom) {
                    return {};
                }

                return {
                    'top': html_dom,
                    'rect': document.querySelector('.rectangle-button'),
                    'cancel': document.querySelector(
                        '.quickedit-cancel-button'),
                    'clear': document.querySelector('.quickedit-clear-button')
                };
            }
        }

        this.viewAllSelections = function(selections) {
            const data = {
                selections: selections.map(x => x.annotation.geometry)
            };
            data.message = 'onViewAllSelections';

            const iframe = window.jQuery('iframe.pdfjs')[0];
            if (iframe) {
                iframe.contentWindow.postMessage(data, '*');
            }
        };

        this.clearAllSelections = function(selections) {
            self.state.pdfRect = null;

            let pages = [];

            selections.forEach(function(e) {
                if (
                    e.annotation.geometry.page &&
                        !pages.includes(e.annotation.geometry.page)
                ) {
                    pages.push(e.annotation.geometry.page);
                }
            });

            const data = {
                pages: pages
            }
            data.message = 'onClearAllSelections';

            const iframe = window.jQuery('iframe.pdfjs')[0];
            if (iframe) {
                iframe.contentWindow.postMessage(data, '*');
            }
        };
    };
}
