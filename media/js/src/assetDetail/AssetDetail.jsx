/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import ReactPlayer from 'react-player';
import Alert from 'react-bootstrap/Alert';
import Nav from 'react-bootstrap/Nav';

import Map from 'ol/Map';
import View from 'ol/View';
import {getCenter} from 'ol/extent';
import Draw from 'ol/interaction/Draw';
import ImageLayer from 'ol/layer/Image';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Projection from 'ol/proj/Projection';
import GeoJSON from 'ol/format/GeoJSON';
import Static from 'ol/source/ImageStatic';

import Asset from '../Asset';
import {
    getAsset, createSherdNote, deleteSelection,
    formatTimecode, parseTimecode, getCoordStyles,
    transform
} from '../utils';
import CreateSelection from './CreateSelection';
import ViewSelections from './ViewSelections';
import ViewItem from './ViewItem';

export default class AssetDetail extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            playing: false,

            // For creating a new selection
            selectionStartTime: 0,
            selectionEndTime: 0,

            deletingSelectionId: null,
            showDeleteDialog: false,
            showDeletedDialog: false,

            createdSelectionTitle: '',
            showCreatedDialog: false,

            showCreateError: false,
            createError: null,

            tab: 'viewSelections'
        };

        this.draw = null;


        this.playerRef = null;
        this.selection = null;

        this.asset = new Asset(this.props.asset);
        this.onStartTimeClick = this.onStartTimeClick.bind(this);
        this.onEndTimeClick = this.onEndTimeClick.bind(this);
        this.onPlayerPlay = this.onPlayerPlay.bind(this);
        this.onCreateSelection = this.onCreateSelection.bind(this);
        this.onDeleteSelection = this.onDeleteSelection.bind(this);
        this.showDeleteDialog = this.showDeleteDialog.bind(this);
        this.hideDeleteDialog = this.hideDeleteDialog.bind(this);
        this.hideDeletedDialog = this.hideDeletedDialog.bind(this);
        this.hideCreatedDialog = this.hideCreatedDialog.bind(this);

        this.onStartTimeUpdate = this.onStartTimeUpdate.bind(this);
        this.onEndTimeUpdate = this.onEndTimeUpdate.bind(this);

        this.onViewSelection = this.onViewSelection.bind(this);

        this.onSelectTab = this.onSelectTab.bind(this);

        this.addInteraction = this.addInteraction.bind(this);
    }

    onCreateSelection(e) {
        e.preventDefault();
        const me = this;
        const type = this.asset.getType();

        const selectionTitle = document.getElementById('newSelectionTitle').value;

        let promise = null;

        if (type === 'image') {
            const features = this.selectionSource.getFeatures();
            const coords = [];
            let extent = null;
            features.forEach(function(feature) {
                const geometry = feature.getGeometry();
                coords.push(geometry.getCoordinates());

                if (extent) {
                    extent = geometry.getExtent().extend(extent);
                } else {
                    extent = geometry.getExtent();
                }
            });

            promise = createSherdNote(this.asset.asset.id, {
                title: selectionTitle,
                tags: document.getElementById('newSelectionTags').value,
                body: document.getElementById('newSelectionNotes').value,
                range1: -2,
                range2: -1,
                annotation_data: {
                    geometry: {
                        type: 'Polygon',
                        coordinates: coords
                    },
                    default: false,
                    x: -2,
                    y: -1,
                    zoom: 1,
                    extent: extent
                }
            });
        } else if (type === 'video') {
            promise = createSherdNote(this.asset.asset.id, {
                title: selectionTitle,
                tags: document.getElementById('newSelectionTags').value,
                body: document.getElementById('newSelectionNotes').value,
                range1: this.state.selectionStartTime,
                range2: this.state.selectionEndTime,
                annotation_data: {
                    startCode: formatTimecode(this.state.selectionStartTime),
                    endCode: formatTimecode(this.state.selectionEndTime),
                    duration: this.state.selectionEndTime -
                        this.state.selectionStartTime,
                    timeScale: 1,
                    start: this.state.selectionStartTime,
                    end: this.state.selectionEndTime
                }
            });
        }

        return promise.then(function() {
            me.setState({
                createdSelectionTitle: selectionTitle,
                showCreatedDialog: true,
                tab: 'viewSelections'
            }, function() {
                const elt = document.getElementById('create-success-alert');
                elt.scrollIntoView();
            });

            // Refresh the selections.
            return getAsset(me.asset.asset.id).then(function(d) {
                me.props.onUpdateAsset(d.assets[me.asset.asset.id]);


            });
        }, function(errorText) {
            me.setState({
                showCreateError: true,
                createError: errorText
            }, function() {
                const elt = document.getElementById('create-error-alert');
                elt.scrollIntoView();
            });
        });
    }

    onDeleteSelection(e) {
        e.preventDefault();
        const me = this;

        deleteSelection(
            this.asset.asset.id,
            this.state.deletingSelectionId
        ).then(function() {
            me.hideDeleteDialog();
            me.setState({showDeletedDialog: true});

            // Refresh the selections.
            getAsset(me.asset.asset.id).then(function(d) {
                me.props.onUpdateAsset(d.assets[me.asset.asset.id]);
            });
        });
    }

    pause() {
        const player = this.playerRef.getInternalPlayer();
        if (player && player.pauseVideo) {
            player.pauseVideo();
        }
    }

    onPlayerPlay() {
        this.setState({playing: true});
    }

    onPlayerProgress(d) {
        if (!this.selection) {
            return;
        }

        // Compare progress to the currently playing selection
        if (d.playedSeconds > this.selection.range2) {
            this.pause();
        }
    }

    onStartTimeUpdate(e) {
        const str = e.target.value;
        this.setState({selectionStartTime: parseTimecode(str)});
    }

    onEndTimeUpdate(e) {
        const str = e.target.value;
        this.setState({selectionEndTime: parseTimecode(str)});
    }

    onStartTimeClick(e) {
        e.preventDefault();
        const player = this.playerRef.getInternalPlayer();
        const time = player.getCurrentTime();
        this.setState({selectionStartTime: time});
    }
    onEndTimeClick(e) {
        e.preventDefault();
        const player = this.playerRef.getInternalPlayer();
        const time = player.getCurrentTime();
        this.setState({selectionEndTime: time});
    }

    showDeleteDialog(selectionId) {
        this.setState({
            deletingSelectionId: selectionId,
            showDeleteDialog: true
        });
    }

    hideDeleteDialog() {
        this.setState({
            deletingSelectionId: null,
            showDeleteDialog: false
        });
    }

    hideDeletedDialog() {
        this.setState({showDeletedDialog: false});
    }

    hideCreatedDialog() {
        this.setState({showCreatedDialog: false});
    }

    onViewSelection(e, a) {
        e.preventDefault();

        const type = this.asset.getType();

        if (type === 'image') {
            if (this.selectionLayer) {
                this.map.removeLayer(this.selectionLayer);
            }

            const img = this.asset.getImage();
            const geometry = transform(
                a.annotation.geometry,
                img.width, img.height,
                a.annotation.zoom
            );
            const geojsonObject = {
                type: 'FeatureCollection',
                crs: {
                    type: 'name',
                    properties: {
                        name: 'Flatland:1'
                    }
                },
                features: [
                    {
                        type: 'Feature',
                        geometry: geometry
                    }
                ]
            };

            const source = new VectorSource({
                features: new GeoJSON().readFeatures(geojsonObject)
            });

            const newLayer = new VectorLayer({
                source: source,
                style: getCoordStyles()
            });

            this.selectionLayer = newLayer;
            this.map.addLayer(newLayer);

            // Fit the selection in the view
            const feature = source.getFeatures()[0];
            const polygon = feature.getGeometry();
            const view = this.map.getView();
            view.fit(polygon, {padding: [20, 20, 20, 20]});
        } else if (type === 'video') {
            const player = this.playerRef;
            player.seekTo(a.range1, 'seconds');
            this.setState({playing: true});
        }
    }

    onSelectTab(tabName) {
        this.setState({tab: tabName});
    }

    render() {
        const type = this.asset.getType();

        let media = null;
        if (type === 'image') {
            let annotationTools = null;
            if (this.state.tab === 'createSelection') {
                annotationTools = (
                    <div className="toolbar-annotations toolbar-annotation p-3 bg-dark text-white">
                        <form>
                            <div className="form-row align-items-center">
                                <div className="col-sm-4">
                                    <div className="input-group">
                                        <div className="form-check form-control-sm">
                                            <input className="form-check-input" type="checkbox" value="" id="defaultCheck1" disabled="" />
                                            <label className="form-check-label" htmlFor="defaultCheck1">
                                                Overlay All Selection Graphics
                                            </label>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-sm-8">
                                    <button
                                        type="button" className="btn btn-outline-light btn-sm mr-2"
                                        onClick={() => this.addInteraction('Polygon')}>
                                        <svg className="bi bi-pentagon-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M8 0l8 6.5-3 9.5H3L0 6.5 8 0z"></path>
                                        </svg> Polygon
                                    </button>
                                    <button type="button" className="btn btn-outline-light btn-sm mr-2">
                                        <svg className="bi bi-plus-circle-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path fillRule="evenodd" d="M16 8A8 8 0 110 8a8 8 0 0116 0zM8.5 4a.5.5 0 00-1 0v3.5H4a.5.5 0 000 1h3.5V12a.5.5 0 001 0V8.5H12a.5.5 0 000-1H8.5V4z" clipRule="evenodd"></path>
                                        </svg> Zoom In
                                    </button>
                                    <button type="button" className="btn btn-outline-light btn-sm">
                                        <svg className="bi bi-dash-circle-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path fillRule="evenodd" d="M16 8A8 8 0 110 8a8 8 0 0116 0zM4 7.5a.5.5 0 000 1h8a.5.5 0 000-1H4z" clipRule="evenodd"></path>
                                        </svg> Zoom Out
                                    </button>
                                </div>

                            </div>
                        </form>
                    </div>
                );
            }

            media = (
                <React.Fragment>
                    {annotationTools}
                    <div
                        id={`map-${this.props.asset.id}`}
                        className="ol-map"></div>
                </React.Fragment>
            );
        } else if (type === 'video') {
            let annotationTools = null;
            if (this.state.tab === 'createSelection') {
                annotationTools = (
                    <div className="toolbar-annotations toolbar-annotation p-3 bg-dark text-white">
                        <form>
                            <div className="form-row align-items-center">
                                <div className="col-sm-4">
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <button
                                                onClick={this.onStartTimeClick}
                                                type="button"
                                                className="btn btn-outline-light btn-sm">
                                                Start&nbsp;
                                                <svg className="bi bi-skip-backward-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                    <path fillRule="evenodd" d="M.5 3.5A.5.5 0 000 4v8a.5.5 0 001 0V4a.5.5 0 00-.5-.5z" clipRule="evenodd"></path> <path d="M.904 8.697l6.363 3.692c.54.313 1.233-.066 1.233-.697V4.308c0-.63-.692-1.01-1.233-.696L.904 7.304a.802.802 0 000 1.393z"></path> <path d="M8.404 8.697l6.363 3.692c.54.313 1.233-.066 1.233-.697V4.308c0-.63-.693-1.01-1.233-.696L8.404 7.304a.802.802 0 000 1.393z"></path>
                                                </svg>
                                            </button>
                                        </div>
                                        <input
                                            value={formatTimecode(this.state.selectionStartTime)}
                                            readOnly
                                            type="text"
                                            className="form-control form-control-sm"
                                            id="inlineFormInputStartTime" />
                                    </div>
                                </div>
                                <div className="col-sm-4">
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <button
                                                onClick={this.onEndTimeClick}
                                                type="button"
                                                className="btn btn-outline-light btn-sm">
                                                Stop&nbsp;
                                                <svg className="bi bi-skip-forward-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                    <path fillRule="evenodd" d="M15.5 3.5a.5.5 0 01.5.5v8a.5.5 0 01-1 0V4a.5.5 0 01.5-.5z" clipRule="evenodd"></path> <path d="M7.596 8.697l-6.363 3.692C.693 12.702 0 12.322 0 11.692V4.308c0-.63.693-1.01 1.233-.696l6.363 3.692a.802.802 0 010 1.393z"></path> <path d="M15.096 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.693-1.01 1.233-.696l6.363 3.692a.802.802 0 010 1.393z"></path>
                                                </svg>
                                            </button>
                                        </div>
                                        <input
                                            value={formatTimecode(this.state.selectionEndTime)}
                                            readOnly
                                            type="text"
                                            className="form-control form-control-sm"
                                            id="inlineFormInputEndTime" />
                                    </div>
                                </div>
                                <div className="col-sm-2">
                                    <button
                                        onClick={this.onPlayerPlay}
                                        type="button"
                                        className="btn btn-outline-light btn-sm">
                                        Play
                                        <svg className="bi bi-play-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 010 1.393z"></path>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                );
            }

            media = (
                <React.Fragment>
                    {annotationTools}
                    <div className="embed-responsive embed-responsive-4by3">
                        <ReactPlayer
                            className="react-player embed-responsive-item"
                            width="auto"
                            height="auto"
                            onPlay={this.onPlayerPlay.bind(this)}
                            onProgress={this.onPlayerProgress.bind(this)}
                            playing={this.state.playing}
                            ref={r => this.playerRef = r}
                            url={this.asset.getVideo()}
                            controls={true} />
                    </div>
                </React.Fragment>
            );
        }

        return (
            <div className="tab-content asset-detail">
                <Alert
                    variant="success" show={this.state.showCreatedDialog}
                    onClose={this.hideCreatedDialog} dismissible
                    id="create-success-alert">
                    <Alert.Heading>
                        Selection &quot;{this.state.createdSelectionTitle}&quot; created.
                    </Alert.Heading>
                </Alert>

                <Alert
                    variant="danger" show={this.state.showDeletedDialog}
                    onClose={this.hideDeletedDialog} dismissible>
                    <Alert.Heading>Selection deleted.</Alert.Heading>
                </Alert>

                <Alert
                    variant="danger" show={this.state.showCreateError}
                    id="create-error-alert">
                    <Alert.Heading>Error creating selection.</Alert.Heading>
                    <p>
                        {this.state.createError}
                    </p>
                </Alert>

                <h1 className="text-center">
                    {this.props.asset.title}
                </h1>

                <Nav
                    className="justify-content-center mb-4"
                    variant="pills" defaultActiveKey="/">
                    <Nav.Item>
                        <Nav.Link
                            onClick={() => this.onSelectTab('viewSelections')}
                            active={this.state.tab === 'viewSelections'}>
                            View Selections from Search
                        </Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                        <Nav.Link
                            onClick={() => this.onSelectTab('createSelection')}
                            active={this.state.tab === 'createSelection'}>
                            Create a New Selection
                        </Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                        <Nav.Link
                            onClick={() => this.onSelectTab('viewItem')}
                            active={this.state.tab === 'viewItem'}>
                            View the Original Item
                        </Nav.Link>
                    </Nav.Item>
                </Nav>

                <div className="row">

                    <div className="col-sm-6">
                        {media}
                        {this.state.tab === 'viewItem' && (
                            <React.Fragment>
                                <table className="table mt-1">
                                    <tbody>
                                        <tr>
                                            <th scope="row">Item Name</th>
                                            <td>
                                                {this.props.asset.title}
                                                &nbsp;
                                                <button type="submit" className="btn btn-secondary btn-sm">Rename</button>
                                            </td>
                                        </tr>
                                        <tr>
                                            <th scope="row">Permalink</th>
                                            <td>
                                                <a href="">
                                                    {window.location.href}
                                                </a>
                                            </td>
                                        </tr>
                                        <tr>
                                            <th scope="row">Creator</th>
                                            <td>
                                                {this.props.asset.author.public_name} ({this.props.asset.author.username})
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                                <button type="submit" className="btn btn-danger btn-sm">
                                    Delete
                                </button>
                            </React.Fragment>
                        )}
                    </div>

                    <div className="col-sm-6">
                        {this.state.tab === 'viewSelections' && (
                            <ViewSelections
                                asset={this.props.asset}
                                onViewSelection={this.onViewSelection}
                                hideDeleteDialog={this.hideDeleteDialog}
                                showDeleteDialog={this.showDeleteDialog}
                                showDeleteDialogBool={this.state.showDeleteDialog}
                            />
                        )}
                        {this.state.tab === 'createSelection' && (
                            <CreateSelection
                                asset={this.props.asset}
                                selectionStartTime={this.state.selectionStartTime}
                                selectionEndTime={this.state.selectionEndTime}
                                onStartTimeUpdate={this.onStartTimeUpdate}
                                onEndTimeUpdate={this.onEndTimeUpdate}
                                onStartTimeClick={this.onStartTimeClick}
                                onEndTimeClick={this.onEndTimeClick}
                                onCreateSelection={this.onCreateSelection}
                            />
                        )}
                        {this.state.tab === 'viewItem' && (
                            <ViewItem asset={this.props.asset} />
                        )}
                    </div>

                </div>
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

            this.selectionSource = new VectorSource({wrapX: false});
            const selectionLayer = new VectorLayer({
                source: this.selectionSource
            });

            this.map = new Map({
                target: `map-${this.props.asset.id}`,
                layers: [
                    new ImageLayer({
                        source: new Static({
                            url: thumbnail,
                            projection: projection,
                            imageExtent: extent
                        })
                    }),
                    selectionLayer
                ],
                view: new View({
                    projection: projection,
                    center: getCenter(extent),
                    zoom: 1
                })
            });

        }
    }

    addInteraction(drawType) {
        if (this.draw) {
            this.map.removeInteraction(this.draw);
        }

        this.draw = new Draw({
            source: this.selectionSource,
            type: 'Polygon'
        });

        this.map.addInteraction(this.draw);
    }
}

AssetDetail.propTypes = {
    asset: PropTypes.object,
    toggleAssetView: PropTypes.func.isRequired,
    onUpdateAsset: PropTypes.func.isRequired
};
