import GeoJSON from 'ol/format/GeoJSON';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import {
    Circle as CircleStyle, Fill, Stroke, Style
} from 'ol/style';
import MultiPoint from 'ol/geom/MultiPoint';

/**
 * objectProportioned()
 *
 * Return an extent appropriate for the given width and height of an
 * image. This is used in the projections (both initial and GeoJSON
 * annotation projections) in order for the co-ordinates to match up
 * on the source image correctly.
 *
 * This was taken Juxtapose / SherdJS.
 */
const objectProportioned = function(width, height) {
    let dim = {w: 180, h: 90};
    const w = width || 180;
    const h = height || 90;
    if (w / 2 > h) {
        dim.h = Math.ceil(180 * h / w);
    } else {
        dim.w = Math.ceil(90 * w / h);
    }
    return [-dim.w, -dim.h, dim.w, dim.h];
};

/**
 * Get annotation/selection display openlayers styles.
 */
const getCoordStyles = function() {
    return [
        new Style({
            stroke: new Stroke({
                color: 'blue',
                width: 3
            }),
            fill: new Fill({
                color: 'rgba(0, 0, 255, 0.1)'
            })
        }),
        new Style({
            image: new CircleStyle({
                radius: 4,
                fill: new Fill({
                    color: 'orange'
                })
            }),
            geometry: function(feature) {
                // return the coordinates of the first ring of
                // the polygon
                var coordinates =
                    feature.getGeometry().getCoordinates()[0];
                return new MultiPoint(coordinates);
            }
        })
    ];
};

const getfreeformStyles = function() {
    return [
        new Style({
            stroke: new Stroke({
                color: 'blue',
                width: 3
            }),
            fill: new Fill({
                color: 'rgba(0, 0, 255, 0.1)'
            })
        }),
        new Style({
            image: new CircleStyle({
                radius: 2,
                fill: new Fill({
                    color: 'blue'
                })
            }),
            geometry: function(feature) {
                // return the coordinates of the first ring of
                // the polygon
                var coordinates =
                    feature.getGeometry().getCoordinates()[0];
                return new MultiPoint(coordinates);
            }
        })
    ];
};
/**
 * Display the given selection on the given OpenLayers map.
 *
 * Returns the new VectorLayer.
 */
const displaySelection = function(a, map) {
    let styles = null;
    const tool = a.annotation.tool;
    if(tool === 'polygon') {
        styles = getCoordStyles();
    } else {
        styles = getfreeformStyles();
    }

    const geometry = a.annotation.geometry;
    const view = map.getView();
    const projection = view.getProjection();
    const source = new VectorSource({
        features: [
            new GeoJSON({
                dataProjection: projection,
                featureProjection: projection
            }).readFeature({
                type: 'Feature',
                geometry: geometry
            })
        ]
    });

    const newLayer = new VectorLayer({
        source: source,
        style: styles
    });

    map.addLayer(newLayer);

    // Fit the selection in the view
    const feature = source.getFeatures()[0];
    const polygon = feature.getGeometry();
    if (polygon) {
        view.fit(polygon, {padding: [20, 20, 20, 20]});
    }
    return newLayer;
};

/**
 * Given an openlayers Source object, clear all features from it.
 */
const clearSource = function(source) {
    if (source) {
        source.getFeatures().forEach(function(feature) {
            source.removeFeature(feature);
        });
    }
};

/**
 * Given a selection source, return true if it has a feature (vector
 * shape) on it.
 */
const hasSelection = function(source) {
    if (source) {
        const features = source.getFeatures();
        return features && features.length > 0;
    }

    return false;
};

/**
 * Given an openlayers map, its selection source, and the source
 * image, reset its view to that image.
 *
 * Remove all polygon vectors and fit the view appropriately.
 */
const resetMap = function(map, source, img) {
    clearSource(source);

    const extent = objectProportioned(img.width, img.height);
    const view = map.getView();
    view.fit(extent);
};

export {
    objectProportioned, getCoordStyles, displaySelection,
    clearSource, hasSelection, resetMap
};
