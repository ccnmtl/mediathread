/* global Sherd: true, djangosherd: true */
function DjangoSherd_NoteForm() {
    var self = this;
    Sherd.Base.DomObject.apply(this, arguments);// inherit
    this.form_name = 'edit-annotation-form';
    this.f = function (field) {
        //returns field from form, but without keeping pointers around
        return document.forms[self.form_name].elements[field];
    };
    this.storage = {
        update : function (obj) {
            var range1 = '0';
            var range2 = '0';
            function numOrEmpty(v) {
                return v || ((v === 0) ? v: '');
            }
            ///if isNaN, then it's an empty value to be saved as null
            if (obj.start || obj.end) {// video
                range1 = numOrEmpty(obj.start);
                range2 = numOrEmpty(obj.end);
            } else if (obj.x) {// image
                range1 = numOrEmpty(obj.x);
                range2 = numOrEmpty(obj.y);
            }
            // top is the form
            self.f('annotation-range1').value = range1;
            self.f('annotation-range2').value = range2;
            self.f('annotation-annotation_data').value = JSON.stringify(obj);
        }
    };
}

// requires jQuery
if (typeof window.djangosherd === 'undefined') {
    const djangosherd = {
        storage: new DjangoSherd_Storage(),
        noteform: new DjangoSherd_NoteForm()
    };
    window.djangosherd = djangosherd;
}

// /assetview: html.pull,html.push,html.remove,setState,getState,&OPTIONAL:play
// / pull,push are supported by Base.AssetView, but in, turn, call:
// / id, microformat.update, microformat.write, microformat.create
// / when attached to clipform: media.duration,media.timescale (and probably
// media.time)

function djangosherd_adaptAsset(asset) {
    if (asset.flv || asset.flv_pseudo ||
            asset.mp4 || asset.mp4_pseudo || asset.mp4_rtmp ||
            asset.flv_rtmp || asset.video_pseudo || asset.video_rtmp ||
            asset.video || asset.mp3 || asset.mp4_audio ||
            asset.mp4_panopto) {
        asset.type = 'flowplayer';
    } else if (asset.youtube) {
        asset.type = 'youtube';
    } else if (asset.vimeo) {
        asset.type = 'vimeo';
    } else if (asset.ogg) {
        asset.type = 'videotag';
    } else if (asset.image) {
        asset.type = 'image';
        asset.thumbable = true;
    } else if ((asset.image_fpx || asset.image_fpxid) && asset.fsiviewer) {
        asset.type = 'fsiviewer';
        asset.thumbable = true;
    } else if (asset.pdf) {
        asset.type = 'pdf';
        asset.thumbable = true;
    } else if (asset.archive) {
        asset.type = "NONE";
    }
    return asset;
}

//Object: DjangSherd_AssetMicroFormat
//Find and Return the assets listed in the page
//Assets are within a div called "asset-links"
//asset-primary -- the actual link to the media (image/video/etc.)
//assetlabel-X -- tells you what type the asset is. e.g. assetlabel-youtube is
//youtube, assetlabel-url is the "viewable" link to the media
function DjangoSherd_AssetMicroFormat() {
    this.find = function (dom) {
        dom = dom || document;
        return jQuery('div.asset-links', dom).map(function () {
            return {"html": this };
        }).get();
    };
    this.create = function (obj, doc) {
        var wrapperID = Sherd.Base.newID('djangoasset');
        return {
            object: obj,
            htmlID: wrapperID,
            text: '<div id="' + wrapperID + '" class="asset-links"></div>'
        };
    };
    this.read = function (found_obj) {
        var rv = {};
        jQuery('a.assetsource', found_obj.html).each(function (index, elt) {
            var reg = String(elt.className).match(/assetlabel-(\w+)/);
            if (reg !== null) {
                // /ASSUMES: only one source for each label
                // /use getAttribute rather than href, to avoid
                // urlencodings
                /// unescape necessary for IE7 (and sometimes 8)
                rv[reg[1]] = decodeURI(elt.getAttribute('href'));
                // /TODO: maybe look for some data attributes here, too,
                // when we put them there.
                var metadata = elt.getAttribute('data-metadata');
                if (metadata !== null) {
                    var wh = metadata.match(/w(\d+)h(\d+)/);
                    rv[reg[1] + '-metadata'] = {
                        width: Number(wh[1]),
                        height: Number(wh[2])
                    };
                    if (jQuery(elt).hasClass('asset-primary')) {
                        rv.width = Number(wh[1]);
                        rv.height = Number(wh[2]);
                    }
                }
            }
        });
        return djangosherd_adaptAsset(rv);//in-place
    };
}


function DjangoSherd_AnnotationMicroFormat() {
    var asset_mf = new DjangoSherd_AssetMicroFormat();
    var video = new Sherd.Video.Helpers();
    this.find = function (dom) {
        dom = dom || document;
        return jQuery('div.annotation', dom).map(function () {
            return {"html" : this };
        }).get();
    };
    this.create = function (obj, doc) {
        ///NOTE: currently only makes header, rather than a full serialization of the object
        var wrapperID = Sherd.Base.newID('djangoannotation');
        var return_text = '';
        if (obj.title) {
            return_text += '<div class="annotation-title">' + obj.title + '</div>';
        }

        if (obj.asset && obj.asset.title) {
            return_text += '<div class="asset-title">';
            return_text += '<span class="asset-title-prefix">from </span><a href="' + obj.asset.local_url + '">' + obj.asset.title + '</a>';
            return_text += '</div>';
        }

        return {
            object: obj,
            htmlID: wrapperID,
            text: '<div id="' + wrapperID + '" class="annotation">' + return_text + '</div>'
        };
    };
    this.read = function (found_obj) {
        var rv = {
            metadata : {},
            view : {},
            annotations : []
        };
        var asset_elts = asset_mf.find(found_obj.html);
        if (asset_elts.length) {
            // /NOT compatible with many
            rv.asset = asset_mf.read(asset_elts[0]);
        }

        var data_elt = jQuery('div.annotation-data', found_obj.html).get(0);
        var ann_title = jQuery('div.annotation-title', found_obj.html).first()
        .each(function () {
            rv.metadata.title = this.textContent;
        });


        try {
            var ann_data = JSON.parse(
                data_elt.getAttribute('data-annotation'));

            // /TODO: remove these--maybe we can with no problem
            ann_data.start = parseInt(data_elt.getAttribute('data-begin'), 10);// CHOP
            ann_data.end = parseInt(data_elt.getAttribute('data-end'), 10);// CHOP
            ann_data.startCode = video.secondsToCode(ann_data.start);// CHOP
            ann_data.endCode = video.secondsToCode(ann_data.end);// CHOP
            rv.annotations.push(ann_data);
        } catch (e) { //non-valid json?
            Sherd.Base.log(e);
        }
        return rv;
    };
}

function DjangoSherd_Asset_Config() {
    var ds = djangosherd;
    ds.assetMicroFormat = new DjangoSherd_AssetMicroFormat();
    ds.annotationMicroformat = new DjangoSherd_AnnotationMicroFormat();
    ds.noteform = new DjangoSherd_NoteForm();// see below
    ds.storage = new DjangoSherd_Storage();

    // /# Find assets.
    ds.dom_assets = ds.assetMicroFormat.find();
    if (!ds.dom_assets.length) {
        return;// no assets!
    }
    // GenericAssetView is a wrapper in ../assets.js.
    ds.assetview = new Sherd.GenericAssetView({
        'clipform': true,
        'clipstrip': true,
        'storage': ds.noteform,
        'targets': {clipstrip: 'clipstrip-display'}
    });

    ds.assetview.html.push(
        jQuery('div.asset-display').get(0), // id=videoclip
        {
            asset : ds.assetMicroFormat.read(ds.dom_assets[0])
        });

    // /# load asset into note-form
    var clipform = $('clipform-display');
    if (clipform) {
        ds.assetview.clipform.html.push('clipform-display', {
            asset : {}
        }); // write videoform
    }
}

var CitationView = function () {
    var self = this;
    self.citation_link = 'a.materialCitation';
    self.options = {autoplay: true, presentation: 'small', targets: {}};
};

CitationView.prototype.init = function (options) {
    var self = this;

    if (options) {
        // copy in options so default are not overwritten
        for (var a in options) {
            if (options.hasOwnProperty(a)) {
                self.options[a] = options[a];
            }
        }
    }

    if (self.options.default_target) {
        self.options.targets.asset =
            document.getElementById(self.options.default_target);
    }

    // Create an assetview.
    // @todo - We have potentially more than 1 assetview on the project page. The singleton nature in the
    // core architecture means the two views are really sharing the underlying code.
    // Consider how to resolve this contention. (It's a big change in the core.)

    // This may be DANGEROUS in any sense. The old assetview should be destroyed first?
    if (!djangosherd.assetview) {
        var clipform = options.hasOwnProperty('clipform') ? options.clipform : false;
        var clipplay = options.hasOwnProperty('clipplay') ? options.clipplay : false;

        if (!clipform) {
            djangosherd.assetview = new Sherd.GenericAssetView({
                clipform: false,
                clipstrip: true,
                'clipplay': clipplay
            });
        } else {
            // GenericAssetView is a wrapper in ../assets.js.
            djangosherd.assetview = new Sherd.GenericAssetView({
                'clipform': true,
                'clipstrip': true,
                'storage': djangosherd.noteform,
                'targets': {
                    clipstrip: 'clipstrip-display',
                    clipplay: 'clipplay'
                }
            });
        }
    }
};

CitationView.prototype.decorateLinks = function (parent) {
    var self = this;

    ///decorate LINKS to OPEN annotations within a specified div or the whole document
    var elt = parent ? document.getElementById(parent) : document;
    return self.decorateElementLinks(elt);
};

CitationView.prototype.decorateElementLinks = function (element) {
    var self = this;

    var links = jQuery(element).find(self.citation_link);

    var clickHandler = function (evt) {
        try {
            self.openCitation(this);

            jQuery('.active-annotation').removeClass('active-annotation');
            jQuery(this).addClass('active-annotation');
        } catch (e) {
            if (window.console) {
                window.console.log('ERROR opening citation:' + e.message);
            }
        }
        evt.preventDefault();
    };

    for (var i = 0; i < links.length; i++) {
        var link = links[i];
        if (jQuery(link).data().events === undefined || jQuery(link).data().events.click === undefined) {
            jQuery(link).click(clickHandler);
        }
    }
};

CitationView.prototype.openCitation = function (anchor) {
    var self = this;

    var url = anchor.href;

    var asset_url = url.match(/(asset)\/(\d+)\//);
    var asset_id = asset_url.pop();

    var ann_url = url.match(/(annotations)\/(\d+)\/$/);
    var annotation_id = (ann_url && ann_url.pop()) || null;

    return self.openCitationById(anchor, asset_id, annotation_id);
};

CitationView.prototype.openCitationById = function (anchor, asset_id, annotation_id) {
    var self = this;
    self.asset_id = asset_id;
    self.annotation_id = annotation_id;

    if (anchor && jQuery(anchor).hasClass("disabled")) {
        return;
    }

    var return_value = {};
    var id, type;
    if (annotation_id) {
        id = annotation_id;
        type = "annotations";
    } else {
        id = asset_id;
        type = "asset";
    }

    djangosherd.storage.get({
        id: id, type: type
    }, function (ann_obj) {
        self.options.deleted = false;
        return_value = self.displayCitation(anchor, ann_obj, id);
    }, null, function (error) {
        console.error(error);
        if (type === "annotations") {
            // attempt to get asset level
            djangosherd.storage.get({
                id: asset_id, type: 'asset'
            }, function (asset_obj) {
                self.options.deleted = true;
                return_value = self.displayCitation(anchor, asset_obj, id);
            }, null, function (error) {
                var obj = { 'asset': null, 'metadata': { 'title': 'Item Deleted' } };
                return_value = self.displayCitation(anchor, obj, null);
            });
        } else {
            var obj = {
                asset: null,
                metadata: {
                    title: 'Item Deleted'
                }
            };
            return_value = self.displayCitation(anchor, obj, null);
        }
    });

    return return_value;
};

CitationView.prototype.displayCitation = function (anchor, ann_obj, id) {
    var self = this;

    var asset_target = ((self.options.targets && self.options.targets.asset) ?
            self.options.targets.asset
            : document.getElementById("videoclipbox"));

    if (typeof self.options.onPrepareCitation === 'function') {
        self.options.onPrepareCitation(asset_target);
    }

    if (anchor && !self.options.default_target) {
        var display_position = self.options.position || null;
        if (!display_position) {
            display_position = jQuery(anchor).offset();
            display_position.top += jQuery(anchor).height();
        }
        asset_target.style.left = display_position.left + "px";

        var linkHeight = 20;

        var above_position = display_position.top - linkHeight - jQuery(asset_target).height();
        var show_above = (display_position.top + jQuery(asset_target).height()) > jQuery("body").height();

        if (show_above && above_position >= 0) {
            asset_target.style.top = above_position + "px";
        } else {
            asset_target.style.top = display_position.top + "px";
        }
    }

    jQuery(asset_target).show();
    var targets = {
        "top": asset_target,
        "clipstrip": jQuery(asset_target).find('div.clipstrip-display').get(0),
        "clipplay": jQuery(asset_target).find('div.clipplay').get(0),
        "asset": jQuery(asset_target).find('div.asset-display').get(0),
        "asset_title": jQuery(asset_target).find('div.asset-title').get(0),
        "annotation_title": jQuery(asset_target).find('div.annotation-title').get(0)
    };

    if (targets.annotation_title) {
        if (self.options.deleted) {
            targets.annotation_title.innerHTML = "Selection Deleted";
        } else {
            targets.annotation_title.innerHTML =
                ((ann_obj.metadata && ann_obj.metadata.title) ?
                        '' + ann_obj.metadata.title + '' : '');
            if (ann_obj.annotation.startCode) {
                var duration = new Date(ann_obj.annotation.duration * 1000)
                    .toISOString().substr(11, 8);
                targets.annotation_title.innerHTML +=
                    '<br />' + ann_obj.annotation.startCode + ' - ' +
                     ann_obj.annotation.endCode +
                    ' (' + duration + ')';
            }
        }
    }

    var asset_obj = ann_obj.hasOwnProperty("asset") ? ann_obj.asset : ann_obj;
    if (asset_obj) {
        asset_obj.autoplay = (self.options.autoplay) ? self.options.autoplay : false;
        asset_obj.presentation = self.options.presentation || 'small';

        if (targets.asset_title) {
            if (targets.annotation_title.innerHTML === "") {
                targets.annotation_title.innerHTML = '<a href="' + asset_obj.local_url + '">' + asset_obj.title + '</a>';
                targets.asset_title.innerHTML = '&nbsp;';
            } else {
                targets.asset_title.innerHTML =
                    ((asset_obj.title && asset_obj.local_url) ?
                            'from <a href="' + asset_obj.local_url + '">' + asset_obj.title + '</a>'
                            : '');
                if (asset_obj.xmeml && window.is_staff) {
                    targets.asset_title.innerHTML += ' (<a href="/annotations/xmeml/' + id + '/">download FinalCut xml</a>)';
                }
            }
        }
        djangosherd.assetview.html.push(targets.asset, {
            asset : asset_obj,
            targets: {
                clipstrip: targets.clipstrip,
                clipplay: targets.clipplay
            },
            functions: { winHeight: self.options.winHeight }
        });

        if (ann_obj.hasOwnProperty("annotations") && ann_obj.annotations.length > 0 && ann_obj.annotations[0] !== null) {
            var ann_data = ann_obj.annotations[0];// ***
            if (!ann_data.hasOwnProperty("start")) {
                ann_data.start = 0;
            }
            djangosherd.assetview.setState(
                ann_data, {
                    autoplay: self.options.autoplay
                });
        } else {
            djangosherd.assetview.setState({
                start: 0
            }, {
                autoplay: self.options.autoplay
            });
        }
    } else {
        djangosherd.assetview.html.remove();
        targets.asset_title.innerHTML = "";
    }

    jQuery(window).trigger("resize");

    var return_value = {};
    return_value.onUnload = self.unload;
    return_value.view = djangosherd.assetview;
    return_value.object = ann_obj;
    return_value.id = id;
    return_value.target = asset_target;
    return return_value;
};

CitationView.prototype.unload = function () {
    if (djangosherd.assetview) {
        djangosherd.assetview.html.remove();
    }
};

function DjangoSherd_Storage() {
    /* read-only storage repo for annotation objects from MediaThread
     */
    var self = this,
         _cache = {
            'annotations': {},
            'asset': {},
            'project': {}
        };
    this._cache = _cache;

    // Retrieve data from server & stash in the cache
    this.get = function (subject, callback, list_callback, errorCallback) {
        ///currently obj_type in [annotations, asset, project]
        /// that is used for the URL and a reference to the _cache{} section
        var id = parseInt(subject.id, 10);
        var obj_type = subject.type || 'annotations';
        var ann_obj = null;
        var delay = false;

        if (id || subject.url) {
            if (id in _cache[obj_type] && !list_callback) {
                ann_obj = _cache[obj_type][id];
            } else {
                var url =
                    subject.url || MediaThread.urls['asset-json'](id, true);
                jQuery.ajax({
                    url: url,
                    dataType: 'json',
                    cache: false,
                    success: function (json) {
                        var new_id = self.json_update(json, obj_type);
                        if (callback) {
                            id = (typeof new_id !== 'boolean') ? new_id : id;
                            callback(_cache[obj_type][id]);
                        }
                        if (typeof list_callback === 'function') {
                            list_callback(json);
                        }
                    },
                    error: function (xhr, textStatus, errorThrown) {
                        if (errorCallback) {
                            errorCallback();
                        }
                        if (window.console) {
                            window.console.log(textStatus);
                        }
                    }
                });
                delay = true;
            }
        }
        if (!delay && callback) {
            callback(ann_obj);
        }
    };

    this.json_update = function (json) {
        var new_id = true;
        if (json.project) {
            _cache.project[json.project.id] = json.project;
            new_id = json.project.id;
        }
        if (json.assets) {
            for (var i in json.assets) {
                if (json.assets.hasOwnProperty(i)) {
                    var a = json.assets[i];
                    for (var j in a.sources) {
                        if (a.sources.hasOwnProperty(j)) {
                            a[j] = a.sources[j].url;

                            if (a.sources[j].width) {
                                if (a.sources[j].primary) {
                                    a.width = a.sources[j].width;
                                    a.height = a.sources[j].height;
                                }
                                a[a.sources[j].label + '-metadata'] = {
                                    'width': Number(a.sources[j].width),
                                    'height': Number(a.sources[j].height)
                                };
                            }
                        }
                    }
                    djangosherd_adaptAsset(a); //in-place
                    _cache.asset[a.id] = a;

                    if (a.hasOwnProperty('annotations')) {
                        for (var l in a.annotations) {
                            if (a.annotations.hasOwnProperty(l)) {
                                var ann1 = jQuery.extend({}, a.annotations[l]);
                                ann1.asset = jQuery.extend({}, a);
                                delete ann1.asset.annotations;
                                delete ann1.asset.global_annotation;
                                ann1.annotations = [ann1.annotation];
                                _cache.annotations[ann1.id] = ann1;
                            }
                        }
                    }
                }
            }
            if (json.annotations) {
                for (var k = 0; k < json.annotations.length; k++) {
                    var ann = json.annotations[k];
                    ann.asset = json.assets[ann.asset_key];
                    ann.annotations = [ann.annotation];
                    _cache.annotations[ann.id] = ann;
                    if (json.type === 'asset' && k === 0) {
                        _cache.asset[ann.asset_id] = ann;
                    }
                }
            }
        }
        return new_id;
    };
}

function DjangoSherd_NoteList() {
}

window.DjangoSherd_Colors = {
    get: function (str) {
        return (this.current_colors[str] ||
                (this.current_colors[str] = this.mapping(++this.last_color)));
    },
    mapping: function (num) {
        //would like to get purple = 270or280 in (green is currently over represented)
        var hue = (num * 45) % 240;
        var sat = 100 - (parseInt(num * 30 / 240, 10) % 3 * 40);
        var lum = 55 + 5 * ((parseInt(num * 30 / 240 / 3, 10) % 5));
        return this.hsl2rgb(hue, sat, lum);
    },
    reset: function () {
        this.last_color = -1;
        this.current_colors = {};
    },
    hueToRgb: function(m1, m2, hue) {
        var v;
        if (hue < 0) {
            hue += 1;
        } else if (hue > 1) {
            hue -= 1;
        }
        if (6 * hue < 1) {
            v = m1 + (m2 - m1) * hue * 6;
        } else if (2 * hue < 1) {
            v = m2;
        } else if (3 * hue < 2) {
            v = m1 + (m2 - m1) * (2 / 3 - hue) * 6;
        } else {
            v = m1;
        }
        return 255 * v;
    },
    hsl2rgb: function(h, s, l) {
        var m1, m2, hue;
        var r, g, b;
        s /= 100;
        l /= 100;
        if (s === 0) {
            r = g = b = (l * 255);
        } else {
            if (l <= 0.5) {
                m2 = l * (s + 1);
            } else {
                m2 = l + s - l * s;
            }
            m1 = l * 2 - m2;
            hue = h / 360;
            r = this.hueToRgb(m1, m2, hue + 1 / 3);
            g = this.hueToRgb(m1, m2, hue);
            b = this.hueToRgb(m1, m2, hue - 1 / 3);
        }
        return {r: r, g: g, b: b};
    }

};

window.DjangoSherd_Colors.reset();

window.CitationView = CitationView;
