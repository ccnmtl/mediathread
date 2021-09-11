/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import find from 'lodash/find';
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
import Zoom from 'ol/control/Zoom';

import {defaults as defaultInteractions} from 'ol/interaction';

import Asset from '../Asset';
import {
    getAsset, createSherdNote, updateSherdNote,
    deleteSelection,
    formatTimecode, parseTimecode, getDuration,
    getPlayerTime, openSelectionAccordionItem
} from '../utils';
import {CenterControl} from '../centercontrol';
import {
    objectProportioned, displayImageSelection, clearSource, resetMap,
    getdisplayStyle
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

        // If there's a selection in the URL, start at the
        // viewSelections tab.
        let activeSelectionId = null;
        let hasSelection = false;
        if (window && window.location && window.location.pathname) {
            activeSelectionId =
                window.location.pathname.match(/annotations\/(\d+)\//);
            hasSelection = !!activeSelectionId;
            if (hasSelection) {
                activeSelectionId = window.parseInt(activeSelectionId[1], 10);
            }
        }

        // Set the activeSelection based on the url.
        let activeSelection = null;
        if (hasSelection) {
            // Find the active selection in the annotations array.
            activeSelection =
                find(this.props.asset.annotations, {id: activeSelectionId});
        }

        this.state = {
            // For creating a new selection
            selectionStartTime: activeSelection ? activeSelection.range1 : 0,
            selectionEndTime: activeSelection ? activeSelection.range2 : 0,

            assetTitle: this.props.asset ? this.props.asset.title : null,

            deletingSelectionId: null,
            showDeleteDialog: false,
            showDeletedDialog: false,

            validationError: null,

            activeSelection: activeSelection ? activeSelection.title : null,

            tab: 'viewSelections',

            isDrawing: false,
            isEditing: null,

            annotationTool: null,
            showCancel: false,
            showClear: false,
            toolType: null,

            pdfRect: null
        };

        this.draw = null;

        this.playerRef = React.createRef();
        this.polygonButtonRef = React.createRef();
        this.freeformShapeButtonRef = React.createRef();
        this.drawlineButtonRef = React.createRef();
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
        this.onPlaySelection = this.onPlaySelection.bind(this);

        this.onSelectTab = this.onSelectTab.bind(this);

        this.onDrawEnd = this.onDrawEnd.bind(this);
        this.onDrawStart = this.onDrawStart.bind(this);
        this.onUpdateIsEditing = this.onUpdateIsEditing.bind(this);

        this.onClearVectorLayer = this.onClearVectorLayer.bind(this);

        this.addInteraction = this.addInteraction.bind(this);
        this.addFreeformInteraction = this.addFreeformInteraction.bind(this);
        this.addDrawlineInteraction = this.addDrawlineInteraction.bind(this);
        this.onUpdateAssetTitle = this.onUpdateAssetTitle.bind(this);
        this.onDrawCancel = this.onDrawCancel.bind(this);
        this.onClickClear = this.onClickClear.bind(this);
        this.onClickCancel = this.onClickCancel.bind(this);
        this.onRectangleClicked = this.onRectangleClicked.bind(this);
    }

    onUpdateIsEditing(newVal, activeSelection=null) {
        let newState = {isEditing: newVal};

        // If we're leaving editing mode, clear the vector layer,
        if (!newVal) {
            newState.isDrawing = false;

            // and select the selection that was being edited.
            if (activeSelection) {
                newState.activeSelection = activeSelection.title;
            }
        }

        this.setState(newState, function() {
            if (activeSelection) {
                openSelectionAccordionItem(
                    jQuery('#selectionsAccordion'),
                    activeSelection.id,
                    true);
            }
        });
    }

    onUpdateAssetTitle(newTitle) {
        this.setState({assetTitle: newTitle});
    }

    onCreateSelection(e, tags, terms) {
        // Clear the validation errors here since apparently the form
        // passed validation.
        this.setState({
            validationError: null,
            showCancel: false,
            showClear: false,
            toolType: null
        });

        e.preventDefault();
        const me = this;
        const selectionTitle = document.getElementById('newSelectionTitle').value;

        let selectionData = {
            title: selectionTitle,
            tags: tags,
            terms: terms,
            body: document.getElementById('newSelectionNotes').value
        };
        let annotationData = {};

        if (this.type === 'image') {
            // Only allow one feature per selection
            const feature = this.selectionSource.getFeatures()[0];

            const geometry = feature.getGeometry();
            const coords = geometry.getCoordinates();
            const extent = geometry.getExtent();

            selectionData.range1 = -2;
            selectionData.range2 = -1;

            if (this.state.annotationTool === 'polygon') {
                annotationData = {
                    geometry: {
                        type: 'Polygon',
                        coordinates: coords
                    },
                    default: false,
                    x: -2,
                    y: -1,
                    zoom: 1,
                    extent: extent,
                    tool: 'polygon',
                };
            } else if (this.state.annotationTool === 'freeformShape') {
                annotationData = {
                    geometry: {
                        type: 'Polygon',
                        coordinates: coords
                    },
                    default: false,
                    x: -2,
                    y: -1,
                    zoom: 1,
                    extent: extent,
                    tool: 'freeformShape'
                };
            }
            else if (this.state.annotationTool === 'drawline') {
                annotationData = {
                    geometry: {
                        type: 'LineString',
                        coordinates: coords
                    },
                    default: false,
                    x: -2,
                    y: -1,
                    zoom: 1,
                    extent: extent,
                    tool: 'drawline'
                };
            }
        } else if (this.type === 'video') {
            selectionData.range1 = this.state.selectionStartTime || 0;
            selectionData.range2 = this.state.selectionEndTime;

            annotationData = {
                startCode: formatTimecode(this.state.selectionStartTime || 0),
                endCode: formatTimecode(this.state.selectionEndTime),
                duration: this.state.selectionEndTime -
                    (this.state.selectionStartTime || 0),
                timeScale: 1,
                start: this.state.selectionStartTime || 0,
                end: this.state.selectionEndTime
            };
        } else if (this.type === 'pdf') {
            annotationData = {
                geometry: {
                    type: 'Rectangle',
                    page: this.state.pdfRect.page,
                    coordinates: this.state.pdfRect.coords
                }
            };
        }

        selectionData.annotation_data = annotationData;

        return createSherdNote(this.asset.asset.id, selectionData)
            .then(function(createdSelection) {
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
                            openSelectionAccordionItem(
                                jQuery('#selectionsAccordion'),
                                createdSelection.id,
                                true);
                        });
                });
            });
    }

    onSaveSelection(e, selectionId, tags, terms) {
        // Clear the validation errors here since apparently the form
        // passed validation.
        this.setState({
            validationError: null,
            showCancel: false,
            showClear: false,
            toolType: null
        });

        e.preventDefault();
        const me = this;

        const selectionTitle = document.getElementById('newSelectionTitle').value;

        let annotationData = null;
        let newData = {
            title: selectionTitle,
            tags: tags,
            terms: terms,
            body: document.getElementById('newSelectionNotes').value
        };

        if (
            this.type === 'image' &&
                this.selectionSource &&
                this.selectionSource.getFeatures().length
        ) {
            const feature = this.selectionSource.getFeatures()[0];

            const geometry = feature.getGeometry();
            const coords = geometry.getCoordinates();
            const extent = geometry.getExtent();
            if (this.state.annotationTool === 'polygon') {
                annotationData = {
                    geometry: {
                        type: 'Polygon',
                        coordinates: coords
                    },
                    default: false,
                    x: -2,
                    y: -1,
                    zoom: 1,
                    extent: extent,
                    tool: 'polygon'
                };
            } else if (this.state.annotationTool === 'freeformShape') {
                annotationData = {
                    geometry: {
                        type: 'Polygon',
                        coordinates: coords
                    },
                    default: false,
                    x: -2,
                    y: -1,
                    zoom: 1,
                    extent: extent,
                    tool: 'freeformShape'
                };
            }
            else if (this.state.annotationTool === 'drawline') {
                annotationData = {
                    geometry: {
                        type: 'LineString',
                        coordinates: coords
                    },
                    default: false,
                    x: -2,
                    y: -1,
                    zoom: 1,
                    extent: extent,
                    tool: 'drawline'
                };
            }
        } else if (this.type === 'video') {
            newData.range1 = this.state.selectionStartTime || 0;
            newData.range2 = this.state.selectionEndTime;

            annotationData = {
                startCode: formatTimecode(this.state.selectionStartTime || 0),
                endCode: formatTimecode(this.state.selectionEndTime),
                duration: this.state.selectionEndTime -
                    (this.state.selectionStartTime || 0),
                timeScale: 1,
                start: this.state.selectionStartTime || 0,
                end: this.state.selectionEndTime
            };
        } else if (this.type === 'pdf') {
            annotationData = {
                geometry: {
                    type: 'Rectangle',
                    page: this.state.pdfRect.page,
                    coordinates: this.state.pdfRect.coords
                }
            };
        }

        if (annotationData) {
            newData.annotation_data = JSON.stringify(annotationData);
        }

        return updateSherdNote(
            this.asset.asset.id, selectionId, newData
        ).then(function(data) {
            // Refresh the selections.
            return getAsset(me.asset.asset.id)
                .then(function(d) {
                    return me.props.onUpdateAsset(
                        d.assets[me.asset.asset.id]);
                }).then(function() {
                    openSelectionAccordionItem(
                        jQuery('#selectionsAccordion'),
                        selectionId,
                        true);
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
        const player = this.playerRef.current.getInternalPlayer();
        if (player && player.pauseVideo) {
            player.pauseVideo();
        } else if (player && player.pause) {
            player.pause();
        }
    }

    onPlayerProgress(d) {
        if (!this.state.selectionEndTime) {
            return;
        }

        // Compare progress to the currently playing selection
        if (d.playedSeconds > this.state.selectionEndTime) {
            this.pause();
        }
    }

    onStartTimeUpdate(e) {
        let n = e;

        if (e.target) {
            n = parseTimecode(e.target.value);
        }

        this.setState({selectionStartTime: n});
    }

    onEndTimeUpdate(e) {
        let n = e;

        if (e.target) {
            n = parseTimecode(e.target.value);
        }

        this.setState({selectionEndTime: n});
    }

    onStartTimeClick(e) {
        e.preventDefault();
        const time = getPlayerTime(this.playerRef.current.getInternalPlayer());

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
        const time = getPlayerTime(this.playerRef.current.getInternalPlayer());

        if (typeof time === 'number') {
            this.setState({selectionEndTime: time});
        } else if (time.then) {
            const me = this;
            time.then(function(t) {
                me.setState({selectionEndTime: t});
            });
        }

        this.pause();
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
        if (selectionTitle === null && selectionId === null) {
            this.onClearActiveSelection();
        }
        this.setState({activeSelection: selectionTitle});
        updateSelectionUrl(selectionId);
    }

    onClearActiveSelection() {
        let newState = {
            activeSelection: null
        };

        if (this.type === 'image') {
            if (this.draw) {
                this.map.removeInteraction(this.draw);
            }

            if (this.selectionLayer) {
                this.map.removeLayer(this.selectionLayer);
            }

            resetMap(this.map, this.selectionSource, this.asset.getImage());
        } else if (this.type === 'video') {
            newState.selectionStartTime = null;
            newState.selectionEndTime = null;
        } else if (this.type === 'pdf') {
            const iframe = window.jQuery('iframe.pdfjs')[0];

            if (iframe) {
                iframe.contentWindow.postMessage('onClearSelection', '*');
            }
        }

        this.setState(newState);
    }

    onViewSelection(e, a) {
        if (this.type === 'image') {
            if (this.selectionLayer) {
                this.map.removeLayer(this.selectionLayer);
            }
            const newLayer = displayImageSelection(a, this.map);
            this.selectionLayer = newLayer;
        } else if (this.type === 'video') {
            const player = this.playerRef.current;
            player.seekTo(a.range1, 'seconds');
            this.setState({
                selectionStartTime: a.range1,
                selectionEndTime: a.range2
            });
        } else if (this.type === 'pdf') {
            const iframe = window.jQuery('iframe.pdfjs')[0];

            const data = a.annotation.geometry;
            data.message = 'onViewSelection';

            if (iframe) {
                iframe.contentWindow.postMessage(data, '*');
            }
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

        if (this.selectionLayer) {
            this.map.removeLayer(this.selectionLayer);
        }
    }

    onClickClear() {
        this.onClearVectorLayer();
        this.onClearActiveSelection();
        this.setState({
            isDrawing: false,
            showClear: false,
            annotationTool: null,
            toolType: null
        });
    }

    onPlaySelection(e) {
        e.preventDefault();
        // Queue the selection, if it's not queued already.
        const internalPlayer = this.playerRef.current.getInternalPlayer();
        const currentTime = getPlayerTime(internalPlayer);
        if (Math.round(currentTime) !== Math.round(this.state.selectionStartTime)) {
            this.playerRef.current.seekTo(this.state.selectionStartTime, 'seconds');
        }

        if (internalPlayer && internalPlayer.playVideo) {
            // YouTube
            internalPlayer.playVideo();
        } else if (internalPlayer && internalPlayer.play) {
            // Vimeo and <video> element
            internalPlayer.play();
        }
    }

    onClickCancel(e, selection) {
        e.preventDefault();
        this.onUpdateIsEditing(null, selection);
        this.onClearActiveSelection();
        this.setState({annotationTool: null, toolType: null});
    }

    onRectangleClicked() {
        this.setState({
            toolType: 'rect',
            showCancel: true,
            showClear: false
        });

        const iframe = window.jQuery('iframe.pdfjs')[0];
        if (iframe) {
            iframe.contentWindow.postMessage('enableRectangleTool', '*');
        }
    }

    render() {
        let media = null;

        let invisibleEl = null;
        if (this.state.tab === 'viewMetadata') {
            invisibleEl = (
                <div className="input-group">
                    <div className="form-check form-control-sm invisible">
                        <input className="form-check-input" type="checkbox" />
                    </div>
                </div>
            );
        }

        if (this.type === 'image') {
            const annotationTools = (
                <div className="toolbar-annotations toolbar-annotation p-3 bg-dark text-white">
                    <form>
                        <div className="form-row align-items-center">
                            {invisibleEl}
                            {(this.state.tab === 'createSelection' ||
                              (this.state.tab === 'viewSelections' && this.state.isEditing)) && (
                                <React.Fragment>
                                    <p className="av-selections">Draw Selection</p>
                                    <button
                                        type="button"
                                        ref={this.polygonButtonRef}
                                        className={'btn btn-light btn-sm mr-2 polygon-button ' + (this.state.toolType === 'polygon' ? 'bg-warning' : '')}
                                        onClick={this.addInteraction}>
                                        <svg className="bi bi-pentagon" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path fillRule="evenodd" d="M8 1.288l-6.842 5.56L3.733 15h8.534l2.575-8.153L8 1.288zM16 6.5L8 0 0 6.5 3 16h10l3-9.5z"></path>
                                        </svg> Polygon
                                    </button>
                                    <button
                                        type="button"
                                        ref={this.freeformShapeButtonRef}
                                        className={'btn btn-light btn-sm mr-2 freeformShape-button ' + (this.state.toolType === 'freeformShape' ? 'bg-warning' : '')}
                                        onClick={this.addFreeformInteraction}>
                                        <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-pencil" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path fillRule="evenodd" d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5L13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175l-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                                        </svg> Freeform Shape
                                    </button>
                                    <button
                                        type="button"
                                        ref={this.drawlineButtonRef}
                                        className={'btn btn-light btn-sm mr-2 drawline-button ' + (this.state.toolType === 'drawline' ? 'bg-warning' : '')}
                                        onClick={this.addDrawlineInteraction}>
                                        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" className="bi bi-brush" viewBox="0 0 16 16">
                                            <path d="M15.825.12a.5.5 0 0 1 .132.584c-1.53 3.43-4.743 8.17-7.095 10.64a6.067 6.067 0 0 1-2.373 1.534c-.018.227-.06.538-.16.868-.201.659-.667 1.479-1.708 1.74a8.118 8.118 0 0 1-3.078.132 3.659 3.659 0 0 1-.562-.135 1.382 1.382 0 0 1-.466-.247.714.714 0 0 1-.204-.288.622.622 0 0 1 .004-.443c.095-.245.316-.38.461-.452.394-.197.625-.453.867-.826.095-.144.184-.297.287-.472l.117-.198c.151-.255.326-.54.546-.848.528-.739 1.201-.925 1.746-.896.126.007.243.025.348.048.062-.172.142-.38.238-.608.261-.619.658-1.419 1.187-2.069 2.176-2.67 6.18-6.206 9.117-8.104a.5.5 0 0 1 .596.04zM4.705 11.912a1.23 1.23 0 0 0-.419-.1c-.246-.013-.573.05-.879.479-.197.275-.355.532-.5.777l-.105.177c-.106.181-.213.362-.32.528a3.39 3.39 0 0 1-.76.861c.69.112 1.736.111 2.657-.12.559-.139.843-.569.993-1.06a3.122 3.122 0 0 0 .126-.75l-.793-.792zm1.44.026c.12-.04.277-.1.458-.183a5.068 5.068 0 0 0 1.535-1.1c1.9-1.996 4.412-5.57 6.052-8.631-2.59 1.927-5.566 4.66-7.302 6.792-.442.543-.795 1.243-1.042 1.826-.121.288-.214.54-.275.72v.001l.575.575zm-4.973 3.04.007-.005a.031.031 0 0 1-.007.004zm3.582-3.043.002.001h-.002z"/>
                                        </svg> Line
                                    </button>
                                    {(this.state.showCancel) && (
                                        <button
                                            type="button"
                                            id='cancel-btn'
                                            className="btn btn-danger btn-sm ml-auto"
                                            onClick={this.onDrawCancel}>
                                            Cancel
                                        </button>
                                    )}
                                    {(this.state.showClear && !this.state.isEditing) && (
                                        <button
                                            type="button"
                                            id="clear-btn"
                                            className="btn btn-danger btn-sm ml-auto"
                                            onClick={this.onClickClear}>
                                            Clear
                                        </button>
                                    )}
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
            const showDuration = this.state.tab === 'createSelection' ||
                  (this.state.activeSelection &&
                   this.state.tab === 'viewSelections');
            const annotationTools = (
                <div className="toolbar-annotations toolbar-annotation p-3 bg-dark text-white">
                    <form>
                        <div className="form-row">
                            {invisibleEl}

                            {(this.state.tab === 'createSelection' || this.state.tab === 'viewSelections') && (
                                <>
                                    <div className="col-md-10">
                                        <div className="input-group">

                                            {this.state.activeSelection &&
                                             this.state.tab === 'viewSelections' &&
                                             !this.state.isEditing && (
                                                <>
                                                    <label className="av-selections mt-1">Selection</label>
                                                    <div className="mt-1">
                                                        {formatTimecode(this.state.selectionStartTime)}

                                                        {String.fromCharCode(160)}
                                                        {String.fromCharCode(8212)}
                                                        {String.fromCharCode(160)}

                                                        {formatTimecode(this.state.selectionEndTime)}
                                                    </div>
                                                </>
                                            )}

                                            {(this.state.tab === 'createSelection' || this.state.isEditing) && (
                                                <>
                                                    <label className="av-selections mt-1" htmlFor="juxTimecode">Selection</label>
                                                    <button
                                                        onClick={this.onStartTimeClick}
                                                        ref={this.startButtonRef}
                                                        type="button"
                                                        className="btn btn-light btn-sm mr-1">
                                                        Start
                                                    </button>
                                                    <TimecodeEditor
                                                        min={0}
                                                        onChange={this.onStartTimeUpdate}
                                                        timecode={this.state.selectionStartTime}
                                                    />

                                                    <button
                                                        onClick={this.onEndTimeClick}
                                                        type="button"
                                                        className="btn btn-light btn-sm ml-2 mr-1">
                                                        Stop
                                                    </button>
                                                    <TimecodeEditor
                                                        min={0}
                                                        onChange={this.onEndTimeUpdate}
                                                        timecode={this.state.selectionEndTime}
                                                    />
                                                </>
                                            )}
                                            <div className={'ml-2 ' + 'mt-1 ' + (showDuration ? '' : 'invisible')}>
                                                {String.fromCharCode(8226)} Length:{String.fromCharCode(160)}
                                                <strong>{formatTimecode(getDuration(
                                                    this.state.selectionStartTime,
                                                    this.state.selectionEndTime))}
                                                </strong>
                                            </div>
                                        </div>
                                    </div>

                                    <div className={'col-md-2 text-right' + (showDuration ? '' : 'invisible')}>
                                        {
                                            (this.state.tab === 'createSelection' ||
                                             (this.state.activeSelection && this.state.tab === 'viewSelections')
                                            ) && (
                                                <button
                                                    onClick={this.onPlaySelection}
                                                    type="button"
                                                    disabled={
                                                        this.state.selectionStartTime >=
                                                            this.state.selectionEndTime
                                                    }
                                                    className="btn btn-primary btn-sm">
                                                    Play
                                                    <svg
                                                        width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-play-fill ml-1"
                                                        fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                        <path d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>
                                                    </svg>
                                                </button>
                                            )}
                                    </div>
                                </>
                            )}
                        </div>
                    </form>
                </div>
            );

            const source = this.asset.extractSource();
            let vidUrl = null;
            if (source) {
                vidUrl = source.url;
            }

            let extraConfig = {file: {attributes: {}}};
            if (!window.MediaThread.allow_item_download) {
                extraConfig.file.attributes.controlsList = 'nodownload';
            }
            const captionTrack = this.asset.getCaptionTrack();
            if (captionTrack) {
                extraConfig.file.attributes = {crossOrigin: 'true'};
                extraConfig.file.tracks =
                    [{kind: 'subtitles', src: captionTrack, default: true}];
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
                            ref={this.playerRef}
                            url={vidUrl}
                            controls={true}
                            config={extraConfig}
                        />
                    </div>
                </React.Fragment>
            );
        } else if (this.type === 'pdf') {
            const annotationTools = (
                <div className="toolbar-annotations toolbar-annotation p-3 bg-dark text-white">
                    <form>
                        <div className="form-row align-items-center">
                            {invisibleEl}
                            {(this.state.tab === 'createSelection' ||
                              (this.state.tab === 'viewSelections' && this.state.isEditing)) && (
                                <React.Fragment>
                                    <p className="av-selections">Draw Selection</p>
                                    <button
                                        type="button"
                                        onClick={this.onRectangleClicked}
                                        className={'btn btn-light btn-sm mr-2 polygon-button ' + (this.state.toolType === 'rect' ? 'bg-warning' : '')}>
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-square" viewBox="0 0 16 16">
                                            <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
                                        </svg> Rectangle
                                    </button>
                                    {(this.state.showCancel) && (
                                        <button
                                            type="button"
                                            id='cancel-btn'
                                            className="btn btn-danger btn-sm ml-auto"
                                            onClick={this.onDrawCancel}>
                                            Cancel
                                        </button>
                                    )}
                                    {(this.state.showClear && !this.state.isEditing) && (
                                        <button
                                            type="button"
                                            id="clear-btn"
                                            className="btn btn-danger btn-sm ml-auto"
                                            onClick={this.onClickClear}>
                                            Clear
                                        </button>
                                    )}
                                </React.Fragment>
                            )}
                        </div>
                    </form>
                </div>
            );

            media = (
                <>
                    {annotationTools}
                    <div className="d-flex">
                        <iframe
                            className="flex-fill pdfjs"
                            src={`/asset/pdfjs/${this.asset.asset.id}`}
                            style={{height: '600px'}}>
                        </iframe>
                    </div>
                </>
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
                <div className="d-flex justify-content-between align-items-center flex-wrap">
                    <h2 className="col-md-7 asset-detail-title">
                        {this.state.assetTitle}
                    </h2>

                    <Nav
                        className="col-md-5 justify-content-end mb-2"
                        variant="pills" defaultActiveKey="/">
                        <Nav.Item>
                            <Nav.Link
                                onClick={() => this.onSelectTab('viewSelections')}
                                active={this.state.tab === 'viewSelections'}>
                                View Selections
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
                                onClick={() => this.onSelectTab('viewMetadata')}
                                active={this.state.tab === 'viewMetadata'}>
                                View Metadata
                            </Nav.Link>
                        </Nav.Item>
                    </Nav>
                </div>

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
                        Selection deleted.
                    </Alert>
                </div>

                <div className="row">
                    <div className="col-sm-7">
                        <h4>{leftColumnHeader}</h4>
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
                                selectionSource={this.selectionSource}
                                selectionStartTime={this.state.selectionStartTime}
                                selectionEndTime={this.state.selectionEndTime}
                                filteredSelections={this.props.asset.annotations}
                                isEditing={this.state.isEditing}
                                onUpdateIsEditing={this.onUpdateIsEditing}
                                onSelectSelection={this.onSelectSelection}
                                onSelectTab={this.onSelectTab}
                                onViewSelection={this.onViewSelection}
                                onPlaySelection={this.onPlaySelection}
                                onSaveSelection={this.onSaveSelection}
                                onShowValidationError={this.onShowValidationError}
                                onDeleteSelection={this.onDeleteSelection}
                                hideDeleteDialog={this.hideDeleteDialog}
                                showDeleteDialog={this.showDeleteDialog}
                                showDeleteDialogBool={this.state.showDeleteDialog}
                                onClickCancel={this.onClickCancel}
                                onClearVectorLayer={this.onClearVectorLayer}
                            />
                        )}
                        {this.state.tab === 'createSelection' && (
                            <>
                                <h4>2. Add Details</h4>
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
                            </>
                        )}
                        {this.state.tab === 'viewMetadata' && (
                            <ViewItem
                                asset={this.props.asset}
                                onUpdateAssetTitle={this.onUpdateAssetTitle}
                                onShowValidationError={this.onShowValidationError}
                                leaveAssetDetailView={this.props.leaveAssetDetailView}
                            />
                        )}
                    </div>

                </div>
            </div>
        );
    }

    componentDidUpdate(prevProps, prevState) {
        const me = this;
        const centerControl = new CenterControl();
        const zoomControl = new Zoom();

        if (
            prevState.tab !== this.state.tab &&
                this.state.tab === 'createSelection'
        ) {
            if (this.type === 'video') {
                this.startButtonRef.current.focus();
            }
        } else if (
            this.type === 'pdf' &&
                prevState.tab === 'createSelection' &&
                prevState.tab !== this.state.tab
        ) {
            const iframe = window.jQuery('iframe.pdfjs')[0];
            if (iframe) {
                iframe.contentWindow.postMessage('disableRectangleTool', '*');
            }
        }

        if (prevState.isDrawing !== this.state.isDrawing) {
            // Turn off the openlayers map controls when isDrawing
            // changes from false to true.
            if (this.state.isDrawing) {

                this.map.getControls().clear();
                this.map.getInteractions().clear();
                this.map.addInteraction(this.draw);

            } else {

                this.map.addControl(zoomControl);
                this.map.addControl(centerControl);

                defaultInteractions().forEach(function(interaction) {
                    me.map.addInteraction(interaction);
                });
            }
        }
    }

    componentDidMount() {
        const me = this;

        // If the path contains a selection ID, open the appropriate
        // selection accordion item.
        const match = window.location.pathname.match(/annotations\/(\d+)\//);
        let sId = null;
        if (match && match.length > 1) {
            sId = parseInt(match[1], 10);
            openSelectionAccordionItem(
                jQuery('#selectionsAccordion'), sId, true);
        }

        if (this.type === 'image') {
            const img = this.asset.getImage();

            const extent = objectProportioned(img.width, img.height);

            const projection = new Projection({
                code: 'xkcd-image',
                units: 'pixels',
                extent: extent
            });

            CenterControl.prototype.handleCenter = function handleCenter() {
                this.getMap().getView().setCenter(getCenter(extent));
                this.getMap().getView().setZoom(1);
            };

            this.selectionSource = new VectorSource({wrapX: false});
            const selectionLayer = new VectorLayer({
                source: this.selectionSource
            });

            this.map = new Map({
                target: `map-${this.props.asset.id}`,
                controls: [new Zoom(), new CenterControl()],
                keyboardEventTarget: document,
                layers: [
                    new ImageLayer({
                        source: new Static({
                            url: img.url,
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
            if (sId) {
                const selection = find(this.props.asset.annotations, {
                    id: sId
                });
                this.onViewSelection(null, selection);
            }
        } else if (this.type === 'pdf') {
            window.onmessage = function(e) {
                if (
                    e.data.message &&
                        e.data.message === 'pdfAnnotationRectCreated'
                ) {
                    me.setState({
                        pdfRect: e.data.rect,
                        toolType: null,
                        showCancel: false,
                        showClear: true
                    });
                } else if (e.data.message && e.data.message === 'pdfLoaded') {
                    if (sId) {
                        const selection = find(me.props.asset.annotations, {
                            id: sId
                        });
                        me.onViewSelection(null, selection);
                    }
                }
            };
        }
    }

    onDrawEnd(event) {
        this.setState({
            showCancel: false,
            isDrawing: false,
            toolType: null
        });

        const feat = event.feature;
        feat.setStyle(getdisplayStyle);
        if (this.draw) {
            this.map.removeInteraction(this.draw);
        }
    }

    onDrawCancel() {
        this.setState({
            showCancel: false,
            isDrawing: false,
            annotationTool: null,
            toolType: null
        });

        if (this.draw) {
            this.map.removeInteraction(this.draw);
        }

        if (this.type === 'pdf') {
            const iframe = window.jQuery('iframe.pdfjs')[0];
            if (iframe) {
                iframe.contentWindow.postMessage('disableRectangleTool', '*');
            }
        }
    }

    onDrawStart() {
        this.setState({
            isDrawing: true,
            showCancel: false,
            showClear: true
        });
        this.onClearVectorLayer();
    }


    addInteraction() {
        this.setState({
            annotationTool: 'polygon',
            showCancel: true,
            showClear: false,
            toolType: 'polygon'
        });

        this.onClearVectorLayer();

        if (this.draw) {
            this.map.removeInteraction(this.draw);
        }

        this.setState({isDrawing: true});

        this.draw = new Draw({
            source: this.selectionSource,
            stopClick: true,
            type: 'Polygon'
        });

        // Every time a drawing is started, clear the vector
        // layer. Each selection only has a single shape, for now.
        this.draw.on('drawstart', this.onDrawStart);
        this.draw.on('drawend', this.onDrawEnd);
        this.draw.on('drawabort', this.onDrawEnd);

        this.map.addInteraction(this.draw);
    }

    addFreeformInteraction() {
        this.setState({
            annotationTool: 'freeformShape',
            showCancel: true,
            showClear: false,
            toolType: 'freeformShape'
        });
        this.onClearVectorLayer();

        if (this.draw) {
            this.map.removeInteraction(this.draw);
        }

        this.setState({isDrawing: true});

        this.draw = new Draw({
            source: this.selectionSource,
            type: 'Polygon',
            freehand: true
        });

        // Every time a drawing is started, clear the vector
        // layer. Each selection only has a single shape, for now.
        this.draw.on('drawstart', this.onDrawStart);
        this.draw.on('drawend', this.onDrawEnd);
        this.draw.on('drawabort', this.onDrawEnd);

        this.map.addInteraction(this.draw);
    }

    addDrawlineInteraction() {
        this.setState({
            annotationTool: 'drawline',
            showCancel: true,
            showClear: false,
            toolType: 'drawline'
        });
        this.onClearVectorLayer();

        if (this.draw) {
            this.map.removeInteraction(this.draw);
        }

        this.setState({isDrawing: true});

        this.draw = new Draw({
            source: this.selectionSource,
            type: 'LineString',
            freehand: true
        });

        // Every time a drawing is started, clear the vector
        // layer. Each selection only has a single shape, for now.
        this.draw.on('drawstart', this.onDrawStart);
        this.draw.on('drawend', this.onDrawEnd);
        this.draw.on('drawabort', this.onDrawEnd);

        this.map.addInteraction(this.draw);
    }
}

AssetDetail.propTypes = {
    asset: PropTypes.object,
    tags: PropTypes.array,
    terms: PropTypes.array,
    leaveAssetDetailView: PropTypes.func.isRequired,
    onUpdateAsset: PropTypes.func.isRequired
};
