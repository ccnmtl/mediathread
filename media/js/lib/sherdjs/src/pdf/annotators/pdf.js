/* global Sherd: true */
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
            showCancel: true
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
                    coordinates: this.state.pdfRect.coords,
                    page: this.state.pdfRect.page
                }
            };
        };

        this.current_state = null;

        // Called by asset.js
        this.setState = function (obj, options) {
            if (typeof obj === 'object') {
                self.current_state = obj;

                self.mode = null;
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
            };

            ///button listeners
            self.events.connect(self.components.rect, 'click', function (evt) {
                const iframe = window.jQuery('iframe.pdfjs')[0];
                if (iframe) {
                    iframe.contentWindow.postMessage(
                        'enableRectangleTool', '*');
                }
            });

            self.events.connect(self.components.cancel, 'click', function (evt) {
                const iframe = window.jQuery('iframe.pdfjs')[0];
                if (iframe) {
                    iframe.contentWindow.postMessage(
                        'disableRectangleTool', '*');
                }
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
                    text: '<div id="' + id + '">' +
                        '<button type="button" class="btn btn-secondary mr-1 rectangle-button">' +
                        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-square" viewBox="0 0 16 16"><path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"></path></svg>' +
                        ' Rectangle' +
                        '</button>' +

                        '<button type="button" class="btn btn-danger cancel-button">' +
                        'Cancel' +
                        '</button>' +
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
                    'cancel': document.querySelector('.cancel-button')
                };
            }
        };
    };
}
