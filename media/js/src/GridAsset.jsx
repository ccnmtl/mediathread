import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import AnnotationScroller from './AnnotationScroller';

import Map from 'ol/Map';
import View from 'ol/View';
import {getCenter} from 'ol/extent';
import ImageLayer from 'ol/layer/Image';
import Projection from 'ol/proj/Projection';
import Static from 'ol/source/ImageStatic';

class MySelections extends React.Component {
    render() {
        let annotationsDom = null;
        let annotations = [];

        const me = this;
        this.props.annotations.forEach(function(annotation) {
            if (annotation.author.id === me.props.currentUser) {
                annotations.push(annotation);
            }
        });

        if (annotations.length > 0) {
            annotationsDom = <React.Fragment>
                <div className="dropdown-divider"></div>
                <div className="card-body">
                    <h5 className="card-title">My Annotations</h5>
                    <AnnotationScroller annotations={annotations} />
                </div>
            </React.Fragment>;
        }

        return annotationsDom;
    }
}

MySelections.propTypes = {
    annotations: PropTypes.array,
    currentUser: PropTypes.number.isRequired
};

class ClassSelections extends React.Component {
    render() {
        let annotationsDom = null;
        let annotations = [];

        const me = this;
        this.props.annotations.forEach(function(annotation) {
            if (annotation.author.id !== me.props.currentUser) {
                annotations.push(annotation);
            }
        });

        if (annotations.length > 0) {
            annotationsDom = <React.Fragment>
                <div className="dropdown-divider"></div>
                <div className="card-body">
                    <h5 className="card-title">Class Annotations</h5>
                    <AnnotationScroller annotations={annotations} />
                </div>
            </React.Fragment>;
        }

        return annotationsDom;
    }
}

ClassSelections.propTypes = {
    annotations: PropTypes.array,
    currentUser: PropTypes.number.isRequired
};

export default class GridAsset extends React.Component {
    render() {
        const thumbnail = this.props.asset.thumb_url ||
                          this.props.asset.sources.image.url;

        return <div className="card" key={this.props.asset.id}>
            <div className="image-overlay">
                <div id={`map-${this.props.asset.id}`}
                     className="ol-map"></div>
                <span className="badge badge-secondary">
                    {this.props.asset.primary_type}
                </span>
            </div>

            <div className="card-body">
                <h5 className="card-title">
                    <a href={this.props.asset.local_url}>
                        {this.props.asset.title}
                    </a>
                </h5>
            </div>
            <MySelections
                annotations={this.props.asset.annotations}
                currentUser={this.props.currentUser} />
            <ClassSelections
                annotations={this.props.asset.annotations}
                currentUser={this.props.currentUser} />
        </div>;
    }
    componentDidMount() {
        const thumbnail = this.props.asset.thumb_url ||
                          this.props.asset.sources.image.url;

        const extent = [
            0, 0,
            this.props.asset.sources.image.width,
            this.props.asset.sources.image.height
        ];
        const projection = new Projection({
            code: 'xkcd-image',
            units: 'pixels',
            extent: extent
        });

        new Map({
            target: `map-${this.props.asset.id}`,
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

GridAsset.propTypes = {
    asset: PropTypes.object.isRequired,
    currentUser: PropTypes.number.isRequired
};
