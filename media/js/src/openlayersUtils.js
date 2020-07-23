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

/**
 * Display the given selection on the given OpenLayers map.
 *
 * Returns the new VectorLayer.
 */
const displaySelection = function(a, map) {
    const styles = getCoordStyles();

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
    view.fit(polygon, {padding: [20, 20, 20, 20]});
    return newLayer;
};

const clearVectorLayer = function(map) {
    // Remove all features from the vector layer.
    const layers = map.getLayers().getArray();

    // There should always be at least two layers, with the vector
    // layer as the second one.
    if (layers.length > 1) {
        const vectorLayer = layers[1];
        const source = vectorLayer.getSource();

        source.getFeatures().forEach(function(feature) {
            source.removeFeature(feature);
        });
    }
};

/**
 * Given an openlayers map and image, reset its view to that image.
 *
 * Remove all polygon vectors and fit the view appropriately.
 */
const resetMap = function(map, img) {
    clearVectorLayer(map);

    const extent = objectProportioned(img.width, img.height);
    const view = map.getView();
    view.fit(extent);
};

export {
    objectProportioned, getCoordStyles, displaySelection,
    clearVectorLayer, resetMap
};
