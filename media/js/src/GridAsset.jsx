import React from 'react';
import PropTypes from 'prop-types';

import Feature from 'ol/Feature';
import Map from 'ol/Map';
import View from 'ol/View';
import {getCenter} from 'ol/extent';
import ImageLayer from 'ol/layer/Image';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Polygon from 'ol/geom/Polygon';
import Projection from 'ol/proj/Projection';
import Static from 'ol/source/ImageStatic';
import {RegularShape, Fill, Stroke, Style} from 'ol/style';

import AnnotationScroller from './AnnotationScroller';
import Asset from './Asset';

class MySelections extends React.Component {
    render() {
        let annotationsDom = null;
        let annotations = [];

        const me = this;
        this.props.asset.annotations.forEach(function(annotation) {
            if (annotation.author.id === me.props.currentUser) {
                annotations.push(annotation);
            }
        });

        if (annotations.length > 0) {
            annotationsDom = <React.Fragment>
                <div className="dropdown-divider"></div>
                <div className="card-body">
                    <h5 className="card-title">My Annotations</h5>
                    <AnnotationScroller
                        annotations={annotations}
                        onSelectedAnnotationUpdate={
                            this.props.onSelectedAnnotationUpdate}
                    />
                </div>
            </React.Fragment>;
        }

        return annotationsDom;
    }
}

MySelections.propTypes = {
    asset: PropTypes.object,
    onSelectedAnnotationUpdate: PropTypes.func.isRequired,
    currentUser: PropTypes.number.isRequired
};

class ClassSelections extends React.Component {
    render() {
        let annotationsDom = null;
        let annotations = [];

        const me = this;
        this.props.asset.annotations.forEach(function(annotation) {
            if (annotation.author.id !== me.props.currentUser) {
                annotations.push(annotation);
            }
        });

        if (annotations.length > 0) {
            annotationsDom = <React.Fragment>
                <div className="dropdown-divider"></div>
                <div className="card-body">
                    <h5 className="card-title">Class Annotations</h5>
                    <AnnotationScroller
                        annotations={annotations}
                        onSelectedAnnotationUpdate={
                            this.props.onSelectedAnnotationUpdate}
                    />
                </div>
            </React.Fragment>;
        }

        return annotationsDom;
    }
}

ClassSelections.propTypes = {
    asset: PropTypes.object,
    onSelectedAnnotationUpdate: PropTypes.func.isRequired,
    currentUser: PropTypes.number.isRequired
};

export default class GridAsset extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            annotationLayer: new VectorLayer({
                source: new VectorSource()
            }),
            selectedAnnotation: null
        };

        this.asset = new Asset(this.props.asset);

        this.onSelectedAnnotationUpdate =
            this.onSelectedAnnotationUpdate.bind(this);
    }
    onSelectedAnnotationUpdate(annotation) {
        const type = this.asset.getType();
        const a = this.props.asset.annotations[annotation];
        if (type === 'image') {
            const stroke = new Stroke({color: 'black', width: 2});
            const fill = new Fill({color: 'red'});
            const style = new Style({
                image: new RegularShape({
                    fill: fill,
                    stroke: stroke,
                    points: 4,
                    radius: 10,
                    angle: Math.PI / 4
                })
            });

            const poly = new Polygon(a.annotation.geometry.coordinates);

            const feature = new Feature({
                geometry: poly,
                name: a.title
            });
            feature.setStyle(style);

            this.map.removeLayer(this.state.annotationLayer);

            const newLayer = new VectorLayer({
                source: new VectorSource({
                    features: [feature]
                })
            });

            this.setState({newLayer});
            this.map.addLayer(newLayer);

            const view = this.map.getView();
            const center = getCenter(poly.getExtent());
            view.setCenter(center);
        } else if (type === 'video') {
            this.setState({selectedAnnotation: a});
        }
    }
    render() {
        const type = this.asset.getType();

        let annotationDom = null;
        if (type === 'video' && this.state.selectedAnnotation) {
            annotationDom = (
                <div className="vid-timecode">
                    {this.state.selectedAnnotation.annotation.startCode}
                    &nbsp;-&nbsp;
                    {this.state.selectedAnnotation.annotation.endCode}
                </div>
            );
        }

        return (
            <div className="card" key={this.props.asset.id}>
                <div className="image-overlay">
                    {type === 'image' && (
                        <div
                            id={`map-${this.props.asset.id}`}
                            className="ol-map"></div>
                    )}
                    {type === 'video' && (
                        <img
                            style={{'maxWidth': '100%'}}
                            src={this.asset.getThumbnail()} />
                    )}
                    {annotationDom}
                    <span className="badge badge-secondary">{type}</span>
                </div>

                <div className="card-body">
                    <h5 className="card-title">
                        <a href={this.props.asset.local_url}
                           title={this.props.asset.title}>
                            {this.props.asset.title}
                        </a>
                    </h5>
                </div>
                <MySelections
                    asset={this.props.asset}
                    onSelectedAnnotationUpdate={this.onSelectedAnnotationUpdate}
                    currentUser={this.props.currentUser} />
                <ClassSelections
                    asset={this.props.asset}
                    onSelectedAnnotationUpdate={this.onSelectedAnnotationUpdate}
                    currentUser={this.props.currentUser} />
            </div>
        );
    }
    componentDidMount() {
        if (this.asset.getType() === 'image') {
            const thumbnail = this.asset.getThumbnail();
            const img = this.asset.getImage();

            const extent = [
                0, 0,
                img.width, img.height
            ];

            const projection = new Projection({
                code: 'xkcd-image',
                units: 'pixels',
                extent: extent
            });

            this.map = new Map({
                target: `map-${this.props.asset.id}`,
                controls: [],
                interactions: [],
                layers: [
                    new ImageLayer({
                        source: new Static({
                            url: thumbnail,
                            projection: projection,
                            imageExtent: extent
                        })
                    })
                ],
                view: new View({
                    projection: projection,
                    center: getCenter(extent),
                    zoom: 1
                })
            });
        }
    }
}

GridAsset.propTypes = {
    asset: PropTypes.object.isRequired,
    currentUser: PropTypes.number.isRequired
};
