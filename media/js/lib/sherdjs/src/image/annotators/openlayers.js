if (!Sherd) { Sherd = {}; }
if (!Sherd.Image) { Sherd.Image = {}; }
if (!Sherd.Image.Annotators) { Sherd.Image.Annotators = {}; }
if (!Sherd.Image.Annotators.OpenLayers) {
    Sherd.Image.Annotators.OpenLayers = function () {
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
            return {};
        };

        this.setState = function (obj, options) {
            if (typeof obj === 'object') {
                //because only one annotation is allowed at once.
                ///At the moment, we could do a better job of saving 'all' features
                /// in an annotation rather than overwriting with the last one
                /// but then we run into confusion where people think they're making
                /// a lot of annotations, but really made one.
                
                if (options && options.mode && options.mode === "reset") {
                    self.openlayers.editingtoolbar = undefined;
                } else {
                    self.mode = null;
                    // options.mode == null||'create'||'browse'||'edit'||'copy'
                    if (self.openlayers.editingtoolbar) {
                        if (!options || !options.mode || options.mode === 'browse') {
                            // whole asset view. no annotations. or, just browsing
                            self.openlayers.editingtoolbar.deactivate();
                            self.mode = "browse";
                        } else {
                            // create, edit, copy
                            self.openlayers.editingtoolbar.activate();
                            self.mode = options.mode;
                        }
                    }
                }
            }
        };

        this.initialize = function (create_obj) {
            if (!self.openlayers.editingtoolbar) {
                self.openlayers.editingtoolbar = new self.openlayers.CustomEditingToolbar(
                        self.targetview.openlayers.vectorLayer.getLayer()
                );
                self.targetview.openlayers.map.addControl(self.openlayers.editingtoolbar);
                self.openlayers.editingtoolbar.deactivate();

                //Q: this doubles mousewheel listening, e.g. why did we need it?
                //A: needed for not showing toolbar until clicking on an annotation
                //self.openlayers.editingtoolbar.sherd.navigation.activate();
                //Solution: just send signals or whatever.
                OpenLayers.Control.prototype.activate.call(
                        self.openlayers.editingtoolbar.sherd.navigation
                );
            }

            //on creation of an annotation
            self.openlayers.editingtoolbar.featureAdded = function (feature) {
                var current_state = self.targetview.getState();
                var geojson = self.targetview.openlayers.feature2json(feature);
                //copy feature properties to current_state
                for (var a in geojson) {
                    if (geojson.hasOwnProperty(a)) {
                        current_state[a] = geojson[a];
                    }
                }
                //use geojson object as annotation
                geojson.preserveCurrentFocus = true;
                self.targetview.setState(geojson);
                self.storage.update(current_state);
            };

            /// button listeners
            self.events.connect(self.components.center, 'click', function (evt) {
                self.targetview.setState({feature: self.targetview.currentfeature});
            });
        };
        this.openlayers = {
            CustomEditingToolbar: OpenLayers.Class(
            OpenLayers.Control.EditingToolbar, {
                initialize: function (layer, options) {
                    //copied, just removing Path-drawing
                    var self = this;
                    OpenLayers.Control.Panel.prototype.initialize.apply(this, [options]);
                    //keep our own stuff contained;
                    this.sherd = {};
                    this.sherd.navigation = new OpenLayers.Control.Navigation({autoActivate: true});
                    this.sherd.pointHandler = new OpenLayers.Control.DrawFeature(
                        layer,
                        OpenLayers.Handler.Point,
                        {'displayClass': 'olControlDrawFeaturePoint'}
                    );
                    this.sherd.polygonHandler = new OpenLayers.Control.DrawFeature(
                        layer,
                        OpenLayers.Handler.Polygon,
                        {'displayClass': 'olControlDrawFeaturePolygon'}
                    );
                    this.sherd.squareHandler = new OpenLayers.Control.DrawFeature(
                        layer,
                        OpenLayers.Handler.RegularPolygon,
                        { 'displayClass': 'olControlDrawFeatureSquare',
                            /*note, this is not supported by openlayers--we need to make our own icons*/
                            'handlerOptions': {sides: 4, irregular: true}
                        }
                    );
                    function featureAdded() {
                        if (typeof self.featureAdded === 'function') {
                            self.featureAdded.apply(self, arguments);
                        }
                    }
                    this.sherd.pointHandler.featureAdded = featureAdded;
                    this.sherd.polygonHandler.featureAdded = featureAdded;
                    this.sherd.squareHandler.featureAdded = featureAdded;
                    this.addControls([this.sherd.navigation,
                                      this.sherd.pointHandler,
                                      this.sherd.squareHandler,
                                      this.sherd.polygonHandler
                                      ]);
                }
            })
        };//end this.openlayers

        this.storage = {
            'update': function (obj, just_downstream) {
                if (!just_downstream) {
                    self.setState(obj, { 'mode': self.mode });
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
                    text: '<div id="' + id + '">' +
                    '<p style="display:none;" id="instructions" class="sherd-instructions">' +
                    'To create a selection of an image, choose a drawing tool, located on the upper, ' +
                    'right-hand side of the image. The polygon tool works by clicking on the points of ' +
                    'the polygon and then double-clicking the last point.<br /><br />' +
                    'Add title, tags and notes. If a Course Vocabulary has been enabled by ' +
                    'the instructor, apply vocabulary terms. Click Save when you are finished.' +                                        
                    '</p></div>'
                };
            },
            'components': function (html_dom, create_obj) {
                return {
                    'top': html_dom,
                    'center': document.getElementById("btnCenter"),
                };
            }
        };
    };//END Sherd.Image.Annotators.OpenLayers
}//END if (!Sherd.Image.Annotators.OpenLayers)


