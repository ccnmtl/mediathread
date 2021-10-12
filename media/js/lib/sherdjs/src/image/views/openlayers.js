/* global Sherd: true, OpenLayers: true */
/****
An annotation looks like this:
///1
{"type":"Feature",
 "id":"OpenLayers.Feature.Vector_92",
 "properties":{},
 "geometry":{"type":"Polygon",
             "coordinates":[[ [-37.8125, 17.1875],
                              [-37.5, -2.5],
                              [-2.8125, 11.25],
                              [-37.8125, 17.1875]
                           ]]
            },
 "crs":{"type":"OGC",
        "properties":{"urn":"urn:ogc:def:crs:OGC:1.3:CRS84"}}
}

///2
{"type":"Feature",
 "id":"OpenLayers.Feature.Vector_78",
 "properties":{},
 "geometry":{"type":"Point",
             "coordinates":[0.3125, -2.96875]
            },
 "crs":{"type":"OGC",
        "properties":{"urn":"urn:ogc:def:crs:OGC:1.3:CRS84"}}
}


 ***/

if (!Math.log2) {
    var div = Math.log(2);
    Math.log2 = function(x) {
        return Math.log(x) / div;
    };
}
if (!window.console) {
    window.console = { log: function() {} };
}
if (!Sherd) { Sherd = {}; }
if (!Sherd.Image) { Sherd.Image = {}; }
if (!Sherd.Image.OpenLayers) {
    /*reference files
     * openlayers/openlayers/examples/image-layer.html
     * openlayers/openlayers/examples/modify-feature.html
     * openlayers/openlayers/examples/vector-formats.html
     */
    Sherd.Image.OpenLayers = function() {
        var self = this;
        Sherd.Base.AssetView.apply(this, arguments); //inherit

        this.presentation = null;

        this.events.connect(window, 'resize', function() {
            if (self.presentation) {
                self.presentation.resize();
            }
        });

        this.openlayers = {
            'features': [],
            'feature2json': function(feature) {
                if (self.openlayers.GeoJSON) {
                    return {
                        'geometry': self.openlayers.GeoJSON.extract.geometry.call(
                            self.openlayers.GeoJSON, feature.geometry)
                    };
                }
            },
            'features2svg': function() {
                throw new Error('not implemented correctly');
                ///This gets it from the vectorLayer, which is
                /// abandoned for a Rootcontainer object, which will be different
                /// also the svg will be relative to the MapContainer div's pos-style
                //var x = new OpenLayers.Format.XML();
                //return x.write(self.openlayers.vectorLayer.v.renderer.rendererRoot);
            },
            'frag2feature': function(obj, map) {
                console.log('frag2feature', obj, map);
                var extent = self.openlayers.map.getMaxExtent().toArray(); //left,?bottom,right,top
                var geow = extent[2] - extent[0],
                    geoh = extent[3] - extent[1];

                if (self.current_obj.type === 'xyztile') {
                    ///bottom extent is not reliable, so we use 1000px = 90deg
                    geoh = self.current_obj.dim.height * 90 / 1000;
                }
                switch (obj.xywh.units) {
                case 'pixel':
                    geow /= self.current_obj.dim.width;
                    geoh /= self.current_obj.dim.height;
                    break;
                case 'percent':
                    geow /= 100;
                    geoh /= 100;
                    break;
                default:
                    return false; //unsupported type
                }
                var topleft = [
                    extent[0] + obj.xywh.x * geow,
                    extent[3] - obj.xywh.y * geoh
                ];
                var geometry = {type: 'Polygon', coordinates: []};
                if (obj.xywh.w === 0 && obj.xywh.h === 0) {
                    geometry.type = 'Point';
                    geometry.coordinates = topleft;
                } else {
                    var right = topleft[0] + geow * obj.xywh.w;
                    var bottom = topleft[1] - geoh * obj.xywh.h;
                    geometry.coordinates.push([topleft,
                        [right, topleft[1]], //topright
                        [right, bottom], //bottomright
                        [topleft[0], bottom], //bottomleft
                        topleft]); //return to topleft
                }
                return self.openlayers.GeoJSON.parseFeature({geometry: geometry});
            },
            'object_proportioned': function(object) {
                var dim = {w: 180, h: 90};
                var w = object.width || 180;//76.23;//
                var h = object.height || 90;
                if (w / 2 > h) {
                    dim.h = Math.ceil(180 * h / w);
                } else {
                    dim.w = Math.ceil(90 * w / h);
                }
                return dim;
            },
            'object2bounds': function(object) {
                ///TODO:figure these out better
                ///should fail without w/h better
                ///test image: 466x550, 1694x2000
                ///180/2000.0 * 1694 = 152.46 (/2 = 76.23)
                var dim = self.openlayers.object_proportioned(object);
                return new OpenLayers.Bounds(-dim.w,
                    -dim.h,
                    dim.w,
                    dim.h
                );
            }
        };

        this.Layer = function() {};
        this.Layer.prototype = {
            all_layers: [],
            root: { hover: false, click: false, layers: {} },
            _adoptIntoRootContainer: function(new_layer, opts) {
                /* In order to get mouse events through layers, they need to
               all exist within the same SVG object.  In OpenLayers, this is done
               with OpenLayers/Layer/Vector/RootContainer.js which can only
               be instantiated through SelectFeature (which we use anyway)

               This means each added layer, we need to recreate a global SelectFeature
               so it can consolidate all of the layers.
                 */
                var layerSelf = this;
                if (this.root.globalMouseListener &&
                    this.root.globalMouseListener.map) {
                    this.root.globalMouseListener.destroy();
                }
                var listeners = this.root.layers[new_layer.v.id] = {me: new_layer};

                this.all_layers.push(new_layer.v);
                this.all_layers.sort(function(a, b) {
                    return a.sherd_layerapi.zIndex - b.sherd_layerapi.zIndex;
                });
                //setting the setLayerIndex reorders the map array, so we respect opts.zIndex
                //setting the .index allows clinical removal in .remove();
                for (var i = 0, l = this.all_layers.length; i < l; i++) {
                    var layer = this.all_layers[i];
                    this.root.layers[layer.id].index = i;
                    layer.map.setLayerIndex(layer, i + 1);//+1 for the baseLayer
                }
                if (opts.onmouseenter) {
                    this.root.hover = true;
                    listeners.onmouseenter = opts.onmouseenter;
                }
                if (opts.onmouseleave) {
                    this.root.hover = true;
                    listeners.onmouseleave = opts.onmouseleave;
                }
                if (opts.onclick) {
                    this.root.click = true;
                    listeners.onclick = opts.onclick;
                }

                this.root.globalMouseListener = new OpenLayers.Control.SelectFeature(this.all_layers, {
                    'hover': this.root.hover,
                    overFeature: function(feature) {
                        var lay = layerSelf.root.layers[feature.layer.id];
                        if (lay.onmouseenter) {
                            lay.onmouseenter(feature.sherd_id, feature.layer.sherd_layername);
                        }
                    },
                    clickFeature: function(feature) {
                        var lay = layerSelf.root.layers[feature.layer.id];
                        if (lay.onclick) {
                            lay.onclick(feature.sherd_id, feature.layer.sherd_layername);
                        }
                    },
                    outFeature: function(feature) {
                        var lay = layerSelf.root.layers[feature.layer.id];
                        if (lay.onmouseleave) {
                            lay.onmouseleave(feature.sherd_id, feature.layer.sherd_layername);
                        }
                    },
                    highlightOnly: true,
                    renderIntent: "temporary"
                });
                self.openlayers.map.addControl(this.root.globalMouseListener);
                this.root.globalMouseListener.activate();

            },
            create: function(name, opts) {
                /* opts = {title, onclick(ann_id, layer_name), onhover(ann_id, layer_name), }
                 */
                this.v = new OpenLayers.Layer.Vector(name || "Annotations", { projection: 'Flatland:1',
                    rendererOptions: { zIndexing: true }
                });
                this.name = name;
                this._anns = {};
                this.v.styleMap = new OpenLayers.StyleMap(self.openlayers.styles);
                this.zIndex = (opts && opts.zIndex) || 200; //used to order layers
                this.v.setZIndex(this.zIndex);
                this.v.sherd_layername = name;
                this.v.sherd_layerapi = this;

                self.openlayers.map.addLayer(this.v);
                if (opts.controls) {
                    this._adoptIntoRootContainer(this, opts);
                }

                return this;
            },
            destroyAll: function() {
                //remove from mouselistener obj
                for (var i = 0; i < this.all_layers.length; i++) {
                    layer = this.all_layers[i];
                    delete this.root.layers[layer.id];
                }
                this.all_layers = [];
                for (var ann_id in this._anns) {
                    if (this._anns.hasOwnProperty(ann_id)) {
                        delete this._anns[ann_id];
                    }
                }
            },
            add: function(ann, opts) {
                if (!this.v) {
                    throw new Error('layer not created yet');
                }
                var feature_bg = self.openlayers.GeoJSON.parseFeature(ann);
                var feature_fg = feature_bg.clone();
                var features = [feature_bg, feature_fg];
                feature_bg.renderIntent = 'blackbg';
                feature_fg.renderIntent = 'defaulta';

                if (opts) {
                    if (opts.id) {
                        this._anns[opts.id] = {
                            'f': features,
                            'opts': opts
                        };
                        feature_fg.sherd_id = opts.id;
                        feature_bg.sherd_id = opts.id;
                    }
                    if (opts.color) {
                        if (opts.color in this.v.styleMap.styles) {
                            feature_fg.renderIntent = opts.color;
                        } else if (feature_fg.geometry) {
                            //unique to each feature, for graphicZIndex
                            var feature_style = feature_fg.id + ':' + opts.color;
                            //feature_fg.geometry.getArea(); //alt zIndex measure
                            this.v.styleMap.styles[feature_style] = new OpenLayers.Style({
                                fillOpacity: 0,
                                strokeWidth: 1,
                                strokeColor: opts.color,
                                pointerEvents: (opts.pointerEvents),
                                graphicZIndex: (opts.zIndex || 300 - parseInt(feature_fg.geometry.getBounds().top, 10))
                            });
                            feature_fg.renderIntent = feature_style;
                        }
                    }
                    if (opts.bgcolor) {//cheating--ASSUME color already exists
                        feature_bg.renderIntent = opts.bgcolor;
                    }
                }
                this.v.addFeatures(features);
            },
            remove: function(ann_id) {
                //returns the opts that were used to add it
                if (this.v && ann_id in this._anns) {
                    this.v.removeFeatures(this._anns[ann_id].f);
                    var o = this._anns[ann_id].opts;
                    delete this._anns[ann_id];
                    return o;
                }
            },
            removeAll: function() {
                if (!this.v) {
                    return;
                }
                this.v.removeAllFeatures();
                for (var ann_id in this._anns) {
                    if (this._anns.hasOwnProperty(ann_id)) {
                        delete this._anns[ann_id];
                    }
                }
            },
            show: function() {
                this.v.setVisibility(true);
            },
            hide: function() {
                this.v.setVisibility(false);
            },
            //extension for internal openlayers stuff
            getLayer: function() {
                return this.v;
            }
        };

        this.presentations = {
            'thumb': {
                height: function() { return '100px'; },
                width: function() { return '100px'; },
                initialize: function(obj, presenter) {
                    ///remove controls
                    var m = presenter.openlayers.map;
                    var controls = m.getControlsByClass('OpenLayers.Control.Navigation');
                    for (var i = 0; i < controls.length; i++) {
                        controls[i].disableZoomWheel();
                        if (controls[i].dragPan) {
                            controls[i].dragPan.deactivate();
                        }
                    }

                    while (m.controls.length) {
                        m.removeControl(m.controls[0]);
                    }
                },
                resize: function() {},
                controls: false
            },
            'gallery': {
                height: function(obj, presenter) {
                    // scale the height
                    return parseInt(this.width(obj, presenter), 10) / obj.width * obj.height + 'px';
                },
                width: function(obj, presenter) {
                    return '200px';
                },
                initialize: function(obj, presenter) {
                    ///remove controls
                    var m = presenter.openlayers.map;
                    var controls = m.getControlsByClass('OpenLayers.Control.Navigation');
                    for (var i = 0; i < controls.length; i++) {
                        controls[i].disableZoomWheel();
                        if (controls[i].dragPan) {
                            controls[i].dragPan.deactivate();
                        }
                    }

                    while (m.controls.length) {
                        m.removeControl(m.controls[0]);
                    }
                },
                resize: function() {},
                controls: false
            },
            'default': {
                height: function(obj, presenter) {
                    return Sherd.winHeight() + 'px';
                },
                width: function(obj, presenter) { return '100%'; },
                initialize: function(obj, presenter) {
                    //remove controls
                    var m = presenter.openlayers.map;
                    var controls = m.getControlsByClass('OpenLayers.Control.Navigation');
                    for (var i = 0; i < controls.length; i++) {
                        controls[i].disableZoomWheel();
                        if (controls[i].dragPan) {
                            controls[i].dragPan.deactivate();
                        }
                    }

                    while (m.controls.length) {
                        m.removeControl(m.controls[0]);
                    }
                },
                resize: function() {
                    self.components.top.style.height = Sherd.winHeight() + 'px';
                },
                controls: false
            },
            'medium': {
                height: function(obj, presenter) {
                    var height = self.components.winHeight ? self.components.winHeight() : Sherd.winHeight();
                    return height + 'px';
                },
                width: function(obj, presenter) { return '100%'; },
                initialize: function(obj, presenter) {
                    //remove controls
                    var m = presenter.openlayers.map;
                    var controls = m.getControlsByClass('OpenLayers.Control.Navigation');
                    for (var i = 0; i < controls.length; i++) {
                        controls[i].disableZoomWheel();
                        if (controls[i].dragPan) {
                            controls[i].dragPan.deactivate();
                        }
                    }
                    while (m.controls.length) {
                        m.removeControl(m.controls[0]);
                    }
                },
                resize: function() {
                    var height = self.components.winHeight ? self.components.winHeight() : Sherd.winHeight();
                    self.components.top.style.height = height + 'px';
                },
                controls: true
            },
            'small': {
                height: function() { return '390px'; },
                width: function() { return '320px'; },
                initialize: function(obj, presenter) {
                    ///remove controls
                    var m = presenter.openlayers.map;
                    var controls = m.getControlsByClass('OpenLayers.Control.Navigation');
                    for (var i = 0; i < controls.length; i++) {
                        controls[i].disableZoomWheel();
                        if (controls[i].dragPan) {
                            controls[i].dragPan.deactivate();
                        }
                    }

                    while (m.controls.length) {
                        m.removeControl(m.controls[0]);
                    }
                },
                resize: function() {},
                controls: false
            }
        };

        this.currentfeature = false;
        this.current_obj = false;
        this.getState = function() {
            var geojson = {};
            if (self.currentfeature) {
                geojson = self.openlayers.feature2json(self.currentfeature);
            }
            var m = self.openlayers.map;
            if (m) {
                var center = m.getCenter();
                geojson['default'] = (!geojson.geometry && center.lon === 0 && center.lat === 0);
                geojson.x = center.lon;
                geojson.y = center.lat;
                geojson.zoom = m.getZoom();
                //TODO:should influence how we do setState() too, since
                ///feature is essentially relative to this
                geojson.extent = m.getMaxExtent().toArray();
            }
            return geojson;
        };
        this.setState = function(obj) {
            var state = {
                /*
                * 'x':0,//center of -180:180
                * 'y':0,//center of -90:90
                */
                'zoom': 2
            };
            if (obj === null) {
                obj = {};
            }
            if (obj === undefined) {
                self.currentfeature = false;
            }

            if (typeof obj === 'object' && obj !== null) {
                if (obj.feature) {
                    self.currentfeature = obj.feature;
                } else if (obj.geometry) {//obj is a json feature
                    self.currentfeature = self.openlayers.GeoJSON.parseFeature(obj);
                } else if (obj.xywh) {//obj is a mediafragment box
                    self.currentfeature = self.openlayers.frag2feature(obj, self.openlayers.map);
                } else {
                    if (obj.x !== undefined) { state.x = obj.x; }
                    if (obj.y !== undefined) { state.y = obj.y; }
                    if (obj.zoom) { state.zoom = obj.zoom; }
                    self.currentfeature = false;
                }
            }
            self.openlayers.vectorLayer.removeAll();
            if (self.currentfeature) {
                self.openlayers.vectorLayer.add(self.openlayers.feature2json(self.currentfeature),
                    { color: 'grey',
                        bgcolor: 'white',
                        //pointerEvents:'none',
                        zIndex: 850//lower than the highlight layer in assets.js
                    });

                var bounds = self.currentfeature.geometry.getBounds();
                if (!obj.preserveCurrentFocus) {
                    if (obj.zoom &&
                        obj.zoom < self.openlayers.map.getZoomForExtent(bounds)) {
                        self.openlayers.map.setCenter(bounds.getCenterLonLat(), obj.zoom);
                        self.openlayers.map.zoomToExtent(bounds);
                    } else {
                        self.openlayers.map.zoomToExtent(bounds);
                    }
                }
            } else if (!obj || !obj.preserveCurrentFocus) {
                if (state.x !== undefined) {
                    self.openlayers.map.setCenter(
                        new OpenLayers.LonLat(state.x, state.y), state.zoom
                    );
                } else {
                    self.openlayers.map.zoomToMaxExtent();
                }
            }
        };
        this.microformat = {};
        this.microformat.create = function(obj, doc, options) {
            var wrapperID = Sherd.Base.newID('openlayers-wrapper');
            ///TODO:zoom-levels might be something more direct on the object?
            if (!obj.options) {
                obj.options = {
                    numZoomLevels: 5,
                    sphericalMercator: false,
                    projection: 'Flatland:1',
                    ///extraneous, for tiling, but ?good? default?
                    ///must be this way for tiling, in any case.
                    maxExtent: new OpenLayers.Bounds(-180, -90, 180, 90)
                //,units:'m'
                };
            }
            if (obj['image-metadata']) {
                obj.options.numZoomLevels = Math.ceil(
                    Math.log2(Math.max(obj['image-metadata'].height,
                        obj['image-metadata'].width)) - 5);
            }
            return {
                object: obj,
                htmlID: wrapperID,
                text: '<center><div id="' + wrapperID + '" class="sherd-openlayers-map"></div></center>',
                winHeight: options && options.functions && options.functions.winHeight ? options.functions.winHeight : Sherd.winHeight
            };
        };
        this.microformat.update = function(obj, html_dom) {
            ///1. test if something exists in components now (else return false)
            ///2. assert( obj ~= from_obj) (else return false)
            //map is destroyed during .deinitialize(), so we don't need to
        };
        this.deinitialize = function() {
            if (this.openlayers.map) {
                this.Layer.prototype.destroyAll();
                this.openlayers.map.destroy();
            }
        };
        this.initialize = function(create_obj) {
            if (!create_obj) {
                return;
            }

            var top = document.getElementById(create_obj.htmlID);

            var presentation;
            switch (typeof create_obj.object.presentation) {
            case 'string':
                presentation = self.presentations[create_obj.object.presentation];
                break;
            case 'object':
                presentation = create_obj.object.presentation;
                break;
            case 'undefined':
                presentation = self.presentations['default'];
                break;
            }
            top.style.width = presentation.width(create_obj.object, self);
            top.style.height = presentation.height(create_obj.object, self);

            self.openlayers.map =  new OpenLayers.Map(create_obj.htmlID);
            var objopt = create_obj.object.options;
            if (create_obj.object.xyztile &&
                // Always use an untiled version for digitaltibet. This
                // came about during the migration of this site from
                // Drupal 5 to Hugo.
                !/amazonaws.com\/ccnmtl-digitaltibet-static-prod/.test(
                    create_obj.object.image)
            ) {
                ///DOC: Tile x0,y0 upper left starts at (-180,80)
                ///DOC: whereas single images start at (-180,90)
                var md = create_obj.object['xyztile-metadata'];
                if (create_obj.object['xyztile-metadata']) {
                    objopt.numZoomLevels = Math.ceil(
                        Math.log2(Math.max(md.height, md.width)) - 7);
                    var dim = self.openlayers.object_proportioned(md);
                    var px2deg = 180 / Math.pow(2, objopt.numZoomLevels + 6);
                    /*
                      Somehow the maxExtent.bottom affects positioning of annotations across
                      zoom levels, Futhermore, the top seems to matter also
                      (setting to 90 also breaks at different places)
                    */
                    objopt.maxExtent = new OpenLayers.Bounds(-180,
                        -280,//80-Math.ceil(md.height*px2deg),
                        -180 + Math.ceil(md.width * px2deg),
                        80);
                } else {
                    //everything should fit in this?
                    objopt.maxExtent = new OpenLayers.Bounds(-180, (80 - 360), 180, 80);
                }
                self.openlayers.graphic = new OpenLayers.Layer.XYZ(
                    create_obj.object.title || 'Image',
                    create_obj.object.xyztile,
                    //"http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/Portland/ESRI_LandBase_WebMercator/MapServer/tile/${z}/${y}/${x}",
                    objopt
                );
                self.openlayers.map.maxExtent = objopt.maxExtent;
                ///HACK: to make the tiler work for partial tiles (e.g. not exactly 256x256)
                self.openlayers.graphic.getImageSize = function() { return null; };
                self.openlayers.graphic.zoomToMaxExtent = function() {
                    self.openlayers.map.setCenter(this.maxExtent.getCenterLonLat());
                };
                self.current_obj = {
                    create_obj: create_obj,
                    dim: md,
                    type: 'xyztile'
                };
                ///HACK: to support Zoomify XYZ tiling as seen at thlib.org
                /* Zoomify groups tiles into directories each with a maximum of
                   256 tiles.  This code changes the 'TileGroup' based on x,y,z
                   tile coordinates.
                */

                if (/TileGroup\d/.test(create_obj.object.xyztile)) {
                    self.current_obj.zoomify = true;
                    var tiles_x = Math.ceil(md.width / 256) * 2;
                    var tiles_y = Math.ceil(md.height / 256) * 2;
                    var tiles = [];
                    while (tiles_x > 1 && tiles_y > 1) {
                        tiles_x = Math.ceil(tiles_x / 2);
                        tiles_y = Math.ceil(tiles_y / 2);
                        tiles.push({
                            'all': tiles_x * tiles_y,
                            'x': tiles_x
                        });
                    }
                    tiles.push({all: 1, x: 1}); //z=0
                    tiles = tiles.reverse();

                    self.openlayers.graphic.getURL = function(bounds) {
                        var res = this.map.getResolution();
                        var x = Math.round((bounds.left - this.maxExtent.left) /
                                           (res * this.tileSize.w));
                        var y = Math.round((this.maxExtent.top - bounds.top) /
                                           (res * this.tileSize.h));
                        var z = this.map.getZoom();
                        var url = this.url;
                        ///BEGIN different from XYZ.js
                        var tile_sum = tiles[z].x * y + x;
                        for (var i = 0; i < z; i++) {
                            tile_sum += tiles[i].all;
                        }
                        var tilegroup = Math.floor(tile_sum / 256);
                        if (tilegroup) {
                            url = url.replace(/TileGroup\d/, 'TileGroup' + tilegroup);
                        }
                        ///END different from XYZ.js
                        var path = OpenLayers.String.format(url, {'x': x, 'y': y, 'z': z});
                        return path;
                    };
                }
            } else {
                var o2b = self.openlayers.object2bounds;
                var bounds = o2b(create_obj.object);
                ///TODO: if no create_obj.object.width, test with createElement('img')
                var odim = self.openlayers.object_proportioned(create_obj.object);

                objopt.maxExtent = o2b(create_obj.object);
                self.openlayers.graphic = new OpenLayers.Layer.Image(
                    create_obj.object.title || 'Image',
                    create_obj.object.image,//url of image
                    bounds,
                    //just proportional size: probably much smaller than the actual image
                    ///this allows us to 'zoom out' to smaller than actual image size
                    new OpenLayers.Size(odim.w, odim.h),
                    objopt
                );
                self.current_obj = {
                    create_obj: create_obj,
                    dim: create_obj.object['image-metadata'],
                    type: 'image'
                };
            }

            var projection = 'Flatland:1';//also 'EPSG:4326' and Spherical Mercator='EPSG:900913'
            self.openlayers.styles  = {
                'highlight': new OpenLayers.Style({
                    fillOpacity: 0,
                    strokeWidth: 6,
                    strokeColor: '#ffffff',
                    pointerEvents: 'none',
                    labelSelect: false,
                    graphicZIndex: 1
                }),
                'grey': new OpenLayers.Style({
                    fillOpacity: 0,
                    strokeWidth: 2,
                    strokeColor: '#905050',
                    pointerEvents: 'none',
                    graphicZIndex: 5
                }),
                'blackbg': new OpenLayers.Style({
                    fillOpacity: 0,
                    strokeWidth: 3,
                    strokeColor: '#000000',
                    pointerEvents: 'none',
                    graphicZIndex: 0
                }),
                'defaulta': new OpenLayers.Style({
                    fillOpacity: 0,
                    strokeWidth: 2,
                    graphicZIndex: 0
                }),
                /*pointerEvents is 'none', so the event can be captured by a Layer underneath */
                'white': new OpenLayers.Style({
                    fillOpacity: 0,
                    strokeWidth: 4,
                    strokeColor: '#ffffff',
                    pointerEvents: 'none',
                    labelSelect: false,
                    graphicZIndex: 0
                }),
                'defaultx': new OpenLayers.Style({
                    fillOpacity: 0,
                    strokeWidth: 2,
                    pointerEvents: 'none',
                    labelSelect: false,
                    graphicZIndex: 0
                })
            };

            self.openlayers.map.addControl(new OpenLayers.Control.MousePosition());
            self.openlayers.map.addLayers([self.openlayers.graphic]);
            self.openlayers.vectorLayer = new self.Layer().create('annotating', {
                zIndex: 1000, controls: presentation.controls
            });

            self.openlayers.GeoJSON = new OpenLayers.Format.GeoJSON({
                'internalProjection': self.openlayers.map.baseLayer.projection,
                'externalProjection': new OpenLayers.Projection(projection)
            });

            presentation.initialize(create_obj.object, self);
            self.presentation = presentation;
        };
        this.microformat.components = function(html_dom, create_obj) {
            return {
                'top': html_dom,
                'winHeight': create_obj.winHeight
            };
        };

        this.queryformat = {
            find: function(str) {
                var xywh = String(str).match(/xywh=((\w+):)?([.\d]+),([.\d]+),([.\d]+),([.\d]+)/);
                if (xywh !== null) {
                    var ann = {
                        xywh: {
                            x: Number(xywh[3]),
                            y: Number(xywh[4]),
                            w: Number(xywh[5]),
                            h: Number(xywh[6]),
                            units: xywh[2] || 'pixel'
                        }
                    };
                    return [ann];
                }
                return [];
            }
        };

    };//END Sherd.Image.OpenLayers

}//END if (!Sherd.Image.OpenLayers)
