if (!Sherd) { Sherd = {}; }
if (!Sherd.Image) { Sherd.Image = {}; }
if (!Sherd.Image.Annotators) { Sherd.Image.Annotators = {}; }
if (!Sherd.Image.Annotators.FSIViewer) {
    Sherd.Image.Annotators.FSIViewer = function () {
        var self = this;
        Sherd.Base.AssetView.apply(this, arguments);//inherit

        this.attachView = function (view) {
            self.targetview = view;
        };
        this.targetstorage = [];
        this.addStorage = function (stor) {
            this.targetstorage.push(stor);
        };

        this.getState = function () {
            return self.targetview.getState();
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
            ///button listeners
            self.events.connect(self.components.center, 'click', function (evt) {
                self.targetview.setState(self.current_state);
            });
            self.events.connect(self.components.redo, 'click', function (evt) {
                var current_state = self.targetview.getState();
                self.storage.update(current_state);
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
                var id = Sherd.Base.newID('openlayers-annotator');
                return {
                    htmlID: id,
                    text: '<div id="' + id + '"><p style="display:none;" id="instructions" class="sherd-instructions">' +
                    'To create a selection of an ARTstor image, use tools at the top of the image to zoom into the desired region.' + 
                    '<br /><br />' +
                    'Add title, tags and notes. If a Course Vocabulary has been enabled by the instructor, apply vocabulary terms. ' +
                    'Click Save when you are finished.' +
                    '</p></div>'
                };
            },
            'components': function (html_dom, create_obj) {
                if (!html_dom) {
                    return {};
                }

                var buttons = html_dom.getElementsByTagName('button');
                return {
                    'top': html_dom,
                    'image': html_dom.getElementsByTagName('img')[0],
                    'center': document.getElementById('btnCenter'),
                };
            }
        };
    };//END Sherd.Image.Annotators.OpenLayers
}//END if (!Sherd.Image.Annotators.OpenLayers)


