/* eslint max-len: 0 */

import React from 'react';
import {Document, Page} from 'react-pdf/dist/esm/entry.webpack';
import PropTypes from 'prop-types';

import Map from 'ol/Map';
import View from 'ol/View';
import {getCenter} from 'ol/extent';
import ImageLayer from 'ol/layer/Image';
import Projection from 'ol/proj/Projection';
import ImageStatic from 'ol/source/ImageStatic';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';

import AnnotationScroller from './AnnotationScroller';
import Asset from './Asset';
import {
    capitalizeFirstLetter, handleBrokenImage, getAssetUrl
} from './utils';
import {
    objectProportioned, displayImageSelection, resetMap
} from './openlayersUtils';

export default class GridAsset extends React.Component {
    constructor(props) {
        super(props);

        const mediaPrefix = typeof MediaThread !== 'undefined' ?
            window.MediaThread.staticUrl : '/media/';

        this.state = {
            selectedAnnotation: null,
            thumbnailUrl: mediaPrefix + 'img/thumb_unknown.png'
        };

        this.selectionSource = new VectorSource();
        this.selectionLayer = new VectorLayer({
            source: this.selectionSource
        });

        this.asset = new Asset(this.props.asset);

        this.onSelectedAnnotationUpdate =
            this.onSelectedAnnotationUpdate.bind(this);
    }

    onSelectedAnnotationUpdate(annotation) {
        const type = this.asset.getType();
        const a = this.props.asset.annotations[annotation];

        this.setState({selectedAnnotation: a});

        if (type === 'image') {
            if (this.selectionLayer) {
                this.map.removeLayer(this.selectionLayer);
            }

            if (a) {
                const newLayer = displayImageSelection(a, this.map);
                this.selectionLayer = newLayer;
            } else {
                resetMap(
                    this.map,
                    this.selectionSource,
                    this.asset.getImage());
            }
        }
    }

    render() {
        const type = this.asset.getType();

        let displayedType;
        if (type === 'pdf') {
            displayedType = 'PDF';
        } else {
            displayedType = capitalizeFirstLetter(type);
        }

        let annotationDom = null;
        if (type === 'video' && this.state.selectedAnnotation) {
            annotationDom = (
                <div className="timecode">
                    <span className="badge badge-dark">
                        {this.state.selectedAnnotation.annotation.startCode}
                        &nbsp;-&nbsp;
                        {this.state.selectedAnnotation.annotation.endCode}
                    </span>
                </div>
            );
        }

        const assetUrl = getAssetUrl(this.props.asset.id);

        return (
            <div className="col-sm-4 border-right-8 border-white mb-4">
                <h5 className="text-nowrap text-truncate">
                    <a
                        onClick={(e) => this.props.enterAssetDetailView(e, this.props.asset)}
                        href={assetUrl}
                        title={this.props.asset.title}
                        dangerouslySetInnerHTML={{
                            __html: this.props.asset.title
                        }}>
                    </a>
                </h5>
                <div key={this.props.asset.id}>
                    <div className="card-thumbnail">
                        <div className="media-type">
                            <span className="badge badge-light">
                                {displayedType}
                            </span>
                        </div>
                        <div className="image-overlay">
                            <a
                                onClick={(e) => this.props.enterAssetDetailView(e, this.props.asset)}
                                href={assetUrl}
                                title={this.props.asset.title}>
                                {type === 'image' && (
                                    <div
                                        className={
                                            'ol-map mx-auto d-block img-fluid'
                                        }
                                        id={`map-${this.props.asset.id}`}></div>
                                )}
                                {type === 'video' && (
                                    <img
                                        className="mx-auto d-block img-fluid"
                                        style={{'maxWidth': '100%'}}
                                        alt={'Video thumbnail for: ' +
                                             this.props.asset.title}
                                        src={this.state.thumbnailUrl}
                                        onError={() => handleBrokenImage(type)} />
                                )}
                                {type === 'audio' && (
                                    <img
                                        className="mx-auto d-block img-fluid"
                                        style={{'maxWidth': '100%'}}
                                        alt={'audio thumbnail for: ' +
                                             this.props.asset.title}
                                        src={this.state.thumbnailUrl}
                                        onError={() => handleBrokenImage(type)} />
                                )}
                                {type === 'pdf' && (
                                    <div className="mx-auto d-block img-fluid text-center">
                                        <Document file={this.state.thumbnailUrl}>
                                            <Page
                                                pageNumber={1}
                                                width={192}
                                                height={192}
                                            />
                                        </Document>
                                    </div>
                                )}
                                {type === 'unknown' && (
                                    <img
                                        className="mx-auto d-block img-fluid"
                                        style={{'maxWidth': '100%'}}
                                        alt={'thumbnail for: ' +
                                             this.props.asset.title}
                                        src={this.state.thumbnailUrl}
                                        onError={() => handleBrokenImage(type)} />
                                )}
                            </a>
                            {annotationDom}
                        </div>
                    </div>

                    <AnnotationScroller
                        asset={this.props.asset}
                        onSelectedAnnotationUpdate={
                            this.onSelectedAnnotationUpdate}
                        enterAssetDetailView={this.props.enterAssetDetailView}
                    />

                </div>
            </div>
        );
    }
    componentDidMount() {
        let thumbnail = this.asset.getThumbnail();
        if (typeof thumbnail === 'string') {
            this.setState({thumbnailUrl: this.asset.getThumbnail()});

        } else if (thumbnail && thumbnail.then) {
            const me = this;
            this.asset.getThumbnail().then(function(url) {
                me.setState({thumbnailUrl: url});
            });
        }

        if (this.asset.getType() === 'image') {
            const img = this.asset.getImage();
            const extent = objectProportioned(img.width, img.height);

            const projection = new Projection({
                code: 'Flatland:1',
                units: 'pixels',
                extent: extent
            });

            this.map = new Map({
                target: `map-${this.props.asset.id}`,
                controls: [],
                interactions: [],
                layers: [
                    new ImageLayer({
                        source: new ImageStatic({
                            url: img.url,
                            projection: projection,
                            imageExtent: extent
                        })
                    })
                ],
                view: new View({
                    projection: projection,
                    center: getCenter(extent),
                    zoom: 0.5
                })
            });
        }
        const mediaPrefix = typeof MediaThread !== 'undefined' ?
            window.MediaThread.staticUrl : '/media/';

        if(this.asset.getType() === 'unknown'){
            this.setState({thumbnailUrl: mediaPrefix + 'img/thumb_unknown.png'});
        }

        if(this.asset.getType() === 'audio'){
            this.setState({thumbnailUrl: mediaPrefix + 'img/thumb_audio.png'});
        }
    }
}

GridAsset.propTypes = {
    asset: PropTypes.object.isRequired,
    currentUser: PropTypes.number.isRequired,
    enterAssetDetailView: PropTypes.func.isRequired
};
