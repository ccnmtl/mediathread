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
import Static from 'ol/source/ImageStatic';
import {defaults as defaultControls} from 'ol/control';
import {defaults as defaultInteractions} from 'ol/interaction';

import Asset from '../Asset';
import {
    getAsset, createSherdNote, updateSherdNote,
    deleteSelection,
    formatTimecode, parseTimecode,
    getPlayerTime, openSelectionAccordionItem
} from '../utils';
import {
    objectProportioned, displaySelection, clearSource, resetMap
} from '../openlayersUtils';
import CreateSelection from './CreateSelection';
import ViewSelections from './ViewSelections';
import ViewItem from './ViewItem';
import TimecodeEditor from '../TimecodeEditor';

/**
 * Update the path to the given selection, using pushState.
 */
const updateSelectionUrl = function(selectionId) {
    const basePath = window.location.pathname.replace(
        /annotations\/\d+\//, '');

    let newPath = basePath;
    if (selectionId) {
        newPath = basePath + `annotations/${selectionId}/`;
    }

    window.history.pushState(null, null, newPath);
};

export default class AssetDetail extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // For creating a new selection
            selectionStartTime: 0,
            selectionEndTime: 0,

            deletingSelectionId: null,
            showDeleteDialog: false,
            showDeletedDialog: false,

            validationError: null,

            activeSelection: null,

            tab: 'viewSelections',

            isDrawing: false
        };

        this.draw = null;

        this.playerRef = null;
        this.selection = null;

        this.polygonButtonRef = React.createRef();
        this.startButtonRef = React.createRef();

        this.asset = new Asset(this.props.asset);
        this.type = this.asset.getType();
        this.onStartTimeClick = this.onStartTimeClick.bind(this);
        this.onEndTimeClick = this.onEndTimeClick.bind(this);
        this.onCreateSelection = this.onCreateSelection.bind(this);
        this.onSaveSelection = this.onSaveSelection.bind(this);
        this.onDeleteSelection = this.onDeleteSelection.bind(this);

        this.showDeleteDialog = this.showDeleteDialog.bind(this);
        this.hideDeleteDialog = this.hideDeleteDialog.bind(this);
        this.hideDeletedDialog = this.hideDeletedDialog.bind(this);

        this.onShowValidationError = this.onShowValidationError.bind(this);
        this.hideValidationError = this.hideValidationError.bind(this);

        this.onClearActiveSelection = this.onClearActiveSelection.bind(this);

        this.onStartTimeUpdate = this.onStartTimeUpdate.bind(this);
        this.onEndTimeUpdate = this.onEndTimeUpdate.bind(this);

        this.onSelectSelection = this.onSelectSelection.bind(this);
        this.onViewSelection = this.onViewSelection.bind(this);

        this.onSelectTab = this.onSelectTab.bind(this);

        this.onDrawEnd = this.onDrawEnd.bind(this);

        this.onClearVectorLayer = this.onClearVectorLayer.bind(this);

        this.addInteraction = this.addInteraction.bind(this);
    }

    onCreateSelection(e, tags, terms) {
        // Clear the validation errors here since apparently the form
        // passed validation.
        this.setState({validationError: null});

        e.preventDefault();
        const me = this;
        const selectionTitle = document.getElementById('newSelectionTitle').value;

        let promise = null;

        if (this.type === 'image') {
            // Only allow one feature per selection
            const feature = this.selectionSource.getFeatures()[0];

            const geometry = feature.getGeometry();
            const coords = geometry.getCoordinates();
            const extent = geometry.getExtent();

            promise = createSherdNote(this.asset.asset.id, {
                title: selectionTitle,
                tags: tags,
                terms: terms,
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
        } else if (this.type === 'video') {
            promise = createSherdNote(this.asset.asset.id, {
                title: selectionTitle,
                tags: tags,
                terms: terms,
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

        return promise.then(function(createdSelection) {
            return me.setState({
                activeSelection: createdSelection.title,
                tab: 'viewSelections'
            }, function() {
                // Refresh the selections.
                return getAsset(me.asset.asset.id)
                    .then(function(d) {
                        return me.props.onUpdateAsset(
                            d.assets[me.asset.asset.id]);
                    }).then(function() {
                        // Open this selection's accordion item.
                        openSelectionAccordionItem(
                            jQuery('#selectionsAccordion'),
                            createdSelection.id
                        );
                    });
            });
        });
    }

    onSaveSelection(e, selectionId, tags, terms) {
        // Clear the validation errors here since apparently the form
        // passed validation.
        this.setState({validationError: null});

        e.preventDefault();
        const me = this;

        const selectionTitle = document.getElementById('newSelectionTitle').value;

        return updateSherdNote(
            this.asset.asset.id,
            selectionId,
            {
                title: selectionTitle,
                tags: tags,
                terms: terms,
                body: document.getElementById('newSelectionNotes').value
            })
            .then(function(data) {
                // Refresh the selections.
                return getAsset(me.asset.asset.id)
                    .then(function(d) {
                        return me.props.onUpdateAsset(
                            d.assets[me.asset.asset.id]);
                    }).then(function() {
                        // Open this selection's accordion item.
                        openSelectionAccordionItem(
                            jQuery('#selectionsAccordion'),
                            selectionId
                        );
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

                me.onClearActiveSelection();
            });
        });
    }

    pause() {
        const player = this.playerRef.getInternalPlayer();
        if (player && player.pauseVideo) {
            player.pauseVideo();
        }
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
        const time = getPlayerTime(this.playerRef);

        if (typeof time === 'number') {
            this.setState({selectionStartTime: time});
        } else if (time.then) {
            const me = this;
            time.then(function(t) {
                me.setState({selectionStartTime: t});
            });
        }
    }

    onEndTimeClick(e) {
        e.preventDefault();
        const time = getPlayerTime(this.playerRef);

        if (typeof time === 'number') {
            this.setState({selectionEndTime: time});
        } else if (time.then) {
            const me = this;
            time.then(function(t) {
                me.setState({selectionEndTime: t});
            });
        }
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

    onShowValidationError(errorMsg) {
        this.setState({validationError: errorMsg});
    }

    hideValidationError() {
        this.setState({validationError: null});
    }

    onSelectSelection(selectionTitle, selectionId=null) {
        this.setState({activeSelection: selectionTitle});
        updateSelectionUrl(selectionId);
    }

    onClearActiveSelection() {
        if (this.type === 'image') {
            if (this.draw) {
                this.map.removeInteraction(this.draw);
            }

            if (this.selectionLayer) {
                this.map.removeLayer(this.selectionLayer);
            }

            resetMap(this.map, this.selectionSource, this.asset.getImage());
        } else if (this.type === 'video') {
            const player = this.playerRef;
            player.seekTo(0, 'seconds');
            this.setState({
                selectionStartTime: null,
                selectionEndTime: null
            });
        }

        this.setState({activeSelection: null});
    }

    onViewSelection(e, a) {
        if (this.type === 'image') {
            if (this.selectionLayer) {
                this.map.removeLayer(this.selectionLayer);
            }
            const newLayer = displaySelection(a, this.map);
            this.selectionLayer = newLayer;
        } else if (this.type === 'video') {
            const player = this.playerRef;
            player.seekTo(a.range1, 'seconds');
            this.setState({
                selectionStartTime: a.range1,
                selectionEndTime: a.range2
            });
        }
    }

    onSelectTab(tabName) {
        this.setState({tab: tabName});

        // Clear active selection when switching to any tab.
        this.onClearActiveSelection();
        updateSelectionUrl(null);
    }

    onClearVectorLayer() {
        if (this.selectionSource) {
            clearSource(this.selectionSource);
        }
    }

    render() {
        let media = null;
        if (this.type === 'image') {
            const annotationTools = (
                <div className="toolbar-annotations toolbar-annotation p-3 bg-dark text-white">
                    <form>
                        <div className="form-row align-items-center">
                            {this.state.tab === 'viewSelections' && (
                                <div className="input-group">
                                    <div className="form-check form-control-sm">
                                        <input className="form-check-input" type="checkbox" id="overlayAllCheckbox" />
                                        <label className="form-check-label" htmlFor="overlayAllCheckbox">
                                            Overlay all selections
                                        </label>
                                    </div>
                                </div>
                            )}
                            {this.state.tab === 'createSelection' && (
                                <React.Fragment>
                                    <button
                                        type="button"
                                        autoFocus={true}
                                        ref={this.polygonButtonRef}
                                        className="btn btn-outline-light btn-sm mr-2 polygon-button"
                                        onClick={this.addInteraction}>
                                        <svg className="bi bi-pentagon-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M8 0l8 6.5-3 9.5H3L0 6.5 8 0z"></path>
                                        </svg> Shape
                                    </button>

                                    <button
                                        type="button"
                                        className="btn btn-outline-light btn-sm"
                                        onClick={this.onClearVectorLayer}>
                                        Clear
                                    </button>
                                </React.Fragment>
                            )}
                        </div>
                    </form>
                </div>
            );

            media = (
                <React.Fragment>
                    {annotationTools}
                    <div
                        id={`map-${this.props.asset.id}`}
                        className="ol-map"></div>
                </React.Fragment>
            );
        } else if (this.type === 'video') {
            const annotationTools = (
                <div className="toolbar-annotations toolbar-annotation p-3 bg-dark text-white">
                    {this.state.tab === 'createSelection' && (
                        <form>
                            <div className="form-row align-items-center">
                                <div className="col-md-10">
                                    <div className="input-group">
                                        {this.state.tab === 'createSelection' && (
                                            <button
                                                onClick={this.onStartTimeClick}
                                                ref={this.startButtonRef}
                                                type="button"
                                                className="btn btn-outline-light btn-sm">
                                                Selection Start
                                            </button>
                                        )}
                                        <TimecodeEditor
                                            min={0}
                                            onChange={this.onStartTimeUpdate}
                                            timecode={this.state.selectionStartTime}
                                        />

                                        {String.fromCharCode(160)}
                                        {String.fromCharCode(8212)}
                                        {String.fromCharCode(160)}

                                        {this.state.tab === 'createSelection' && (
                                            <button
                                                onClick={this.onEndTimeClick}
                                                type="button"
                                                className="btn btn-outline-light btn-sm">
                                                Selection Stop
                                            </button>
                                        )}
                                        <TimecodeEditor
                                            min={0}
                                            onChange={this.onEndTimeUpdate}
                                            timecode={this.state.selectionEndTime}
                                        />
                                    </div>
                                </div>
                                <div className="col-md-2">
                                    Duration
                                </div>
                            </div>
                        </form>
                    )}
                </div>
            );

            const source = this.asset.extractSource();
            let vidUrl = null;
            if (source) {
                vidUrl = source.url;
            }

            media = (
                <React.Fragment>
                    {annotationTools}
                    <div className="embed-responsive embed-responsive-16by9">
                        <ReactPlayer
                            className="react-player embed-responsive-item"
                            width="100%"
                            height="100%"
                            style={{backgroundColor: 'black'}}
                            onProgress={this.onPlayerProgress.bind(this)}
                            ref={r => this.playerRef = r}
                            url={vidUrl}
                            controls={true} />
                    </div>
                </React.Fragment>
            );
        }

        let leftColumnHeader = 'Original Item';
        if (this.state.tab === 'createSelection') {
            leftColumnHeader = '1. Make a Selection';
        } else if (
            this.state.tab === 'viewSelections' &&
                this.state.activeSelection
        ) {
            leftColumnHeader = this.state.activeSelection;
        }

        return (
            <div className="tab-content asset-detail">
                <h2 className="text-center">
                    {this.props.asset.title}
                </h2>

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
                            Create Selection
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

                <div className="col-md-6 offset-md-3">
                    <Alert
                        dismissible
                        variant="danger"
                        onClose={this.hideValidationError}
                        show={!!this.state.validationError}>
                        {this.state.validationError}
                    </Alert>

                    <Alert
                        dismissible
                        variant="primary"
                        show={this.state.showDeletedDialog}
                        onClose={this.hideDeletedDialog}>
                        <Alert.Heading>Selection deleted.</Alert.Heading>
                    </Alert>
                </div>

                <div className="row">
                    <div className="col-sm-7">
                        <h3>{leftColumnHeader}</h3>
                        <div className="sticky-top">
                            {media}
                        </div>
                    </div>

                    <div className="col-sm-5">
                        {this.state.tab === 'viewSelections' && (
                            <ViewSelections
                                type={this.type}
                                tags={this.props.tags}
                                terms={this.props.terms}
                                filteredSelections={this.props.filteredSelections}
                                onSelectSelection={this.onSelectSelection}
                                onViewSelection={this.onViewSelection}
                                onSaveSelection={this.onSaveSelection}
                                onShowValidationError={this.onShowValidationError}
                                onDeleteSelection={this.onDeleteSelection}
                                hideDeleteDialog={this.hideDeleteDialog}
                                showDeleteDialog={this.showDeleteDialog}
                                showDeleteDialogBool={this.state.showDeleteDialog}
                            />
                        )}
                        {this.state.tab === 'createSelection' && (
                            <CreateSelection
                                type={this.type}
                                tags={this.props.tags}
                                terms={this.props.terms}
                                selectionSource={this.selectionSource}
                                selectionStartTime={this.state.selectionStartTime}
                                selectionEndTime={this.state.selectionEndTime}
                                onStartTimeClick={this.onStartTimeClick}
                                onEndTimeClick={this.onEndTimeClick}
                                onCreateSelection={this.onCreateSelection}
                                onShowValidationError={this.onShowValidationError}
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

    componentDidUpdate(prevProps, prevState) {
        const me = this;

        if (
            prevState.tab !== this.state.tab &&
                this.state.tab === 'createSelection'
        ) {
            if (this.type === 'image') {
                this.polygonButtonRef.current.focus();
            } else if (this.type === 'video') {
                this.startButtonRef.current.focus();
            }
        }

        if (prevState.isDrawing !== this.state.isDrawing) {
            // Turn off the openlayers map controls when isDrawing
            // changes from false to true.
            if (this.state.isDrawing) {
                this.map.getControls().forEach(function(control) {
                    me.map.removeControl(control);
                });
                this.map.getInteractions().forEach(function(interaction) {
                    me.map.removeInteraction(interaction);
                });
            } else {
                defaultControls().forEach(function(control) {
                    me.map.addControl(control);
                });
                defaultInteractions().forEach(function(interaction) {
                    me.map.addInteraction(interaction);
                });
            }
        }
    }

    componentDidMount() {
        // If the path contains a selection ID, open the appropriate
        // selection accordion item.
        const match = window.location.pathname.match(/annotations\/(\d+)\//);
        if (match && match.length > 1) {
            const sId = parseInt(match[1], 10);
            openSelectionAccordionItem(
                jQuery('#selectionsAccordion'), sId, true);
        }

        if (this.type === 'image') {
            const thumbnail = this.asset.getThumbnail();
            const img = this.asset.getImage();

            const extent = objectProportioned(img.width, img.height);

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

    onDrawEnd() {
        this.setState({isDrawing: false});
    }

    addInteraction() {
        if (this.draw) {
            this.map.removeInteraction(this.draw);
        }

        this.setState({isDrawing: true});

        this.draw = new Draw({
            source: this.selectionSource,
            type: 'Polygon'
        });

        // Every time a drawing is started, clear the vector
        // layer. Each selection only has a single shape, for now.
        this.draw.on('drawstart', this.onClearVectorLayer);
        this.draw.on('drawend', this.onDrawEnd);
        this.draw.on('drawabort', this.onDrawEnd);

        this.map.addInteraction(this.draw);
    }
}

AssetDetail.propTypes = {
    asset: PropTypes.object,
    tags: PropTypes.array,
    terms: PropTypes.array,
    filteredSelections: PropTypes.array,
    onUpdateAsset: PropTypes.func.isRequired
};
