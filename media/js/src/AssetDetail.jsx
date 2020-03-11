/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import ReactPlayer from 'react-player';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';

import Map from 'ol/Map';
import View from 'ol/View';
import {getCenter} from 'ol/extent';
import ImageLayer from 'ol/layer/Image';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Projection from 'ol/proj/Projection';
import Static from 'ol/source/ImageStatic';

import Asset from './Asset';
import {getAsset, createSelection, deleteSelection} from './utils';

export default class AssetDetail extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            selectionLayer: new VectorLayer({
                source: new VectorSource()
            }),
            selectedSelection: null,
            selectionStartTime: 0,
            selectionEndTime: 0,

            deletingSelectionId: null,
            showDeleteDialog: false,
            showDeletedDialog: false,

            createdSelectionTitle: '',
            showCreatedDialog: false
        };

        this.playerRef = null;

        this.asset = new Asset(this.props.asset);
        this.toggleVideoPlay = this.toggleVideoPlay.bind(this);
        this.onStartTimeClick = this.onStartTimeClick.bind(this);
        this.onEndTimeClick = this.onEndTimeClick.bind(this);
        this.onCreateSelection = this.onCreateSelection.bind(this);
        this.onDeleteSelection = this.onDeleteSelection.bind(this);
        this.showDeleteDialog = this.showDeleteDialog.bind(this);
        this.hideDeleteDialog = this.hideDeleteDialog.bind(this);
        this.hideDeletedDialog = this.hideDeletedDialog.bind(this);
        this.hideCreatedDialog = this.hideCreatedDialog.bind(this);
    }

    onCreateSelection(e) {
        e.preventDefault();
        const me = this;

        const selectionTitle = document.getElementById('newSelectionTitle').value;

        createSelection(this.asset.asset.id, {
            'annotation-title': selectionTitle,
            'annotation-tags': document.getElementById('newSelectionTags').value,
            'annotation-body': document.getElementById('newSelectionNotes').value,
            'annotation-range1': 0,
            'annotation-range2': 99,
            'annotation-annotation_data': {
                startCode: this.state.selectionStartTime,
                endCode: this.state.selectionEndTime,
                duration: 251,
                timeScale: 1,
                start: 0,
                end: 99
            }
        }).then(function() {
            me.setState({
                createdSelectionTitle: selectionTitle,
                showCreatedDialog: true
            });

            // Refresh the selections.
            getAsset(me.asset.asset.id).then(function(d) {
                me.props.onUpdateAsset(d.assets[me.asset.asset.id]);
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

    onPlayerReady() {
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

    toggleVideoPlay(e) {
        e.preventDefault();
        const player = this.playerRef.getInternalPlayer();
        if (!this.playerRef.player.isPlaying) {
            player.playVideo();
        } else {
            player.pauseVideo();
        }
    }

    showDeleteDialog(e) {
        const selectionId = jQuery(e.target).closest('button')[0].dataset.id;
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

    render() {
        const type = this.asset.getType();

        const selectionsByAuthor = {};
        const selectionsByAuthorDom = [];

        const me = this;

        // Group the selections by author.
        this.props.asset.annotations.forEach(function(s) {
            if (selectionsByAuthor[s.author.id]) {
                selectionsByAuthor[s.author.id].push(s);
            } else {
                selectionsByAuthor[s.author.id] = [s];
            }
        });

        for (let [key, selections] of Object.entries(selectionsByAuthor)) {
            let selectionsDom = [];
            selections.forEach(function(s) {
                selectionsDom.push(
                    <div
                        key={s.id}
                        className="card" style={{'maxWidth': '540px'}}>
                        <div className="row no-gutters">
                            <div className="col-md-4">
                                <img
                                    src={me.props.asset.thumb_url}
                                    className="card-img" alt="..." />
                            </div>

                            <div className="col-md-8">
                                <div className="card-body">
                                    <button
                                        className="pull-right btn btn-danger"
                                        data-id={s.id}
                                        onClick={me.showDeleteDialog}>
                                        <svg className="bi bi-trash-fill" width="1em" height="1em" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path fillRule="evenodd" d="M4.5 3a1 1 0 00-1 1v1a1 1 0 001 1H5v9a2 2 0 002 2h6a2 2 0 002-2V6h.5a1 1 0 001-1V4a1 1 0 00-1-1H12a1 1 0 00-1-1H9a1 1 0 00-1 1H4.5zm3 4a.5.5 0 01.5.5v7a.5.5 0 01-1 0v-7a.5.5 0 01.5-.5zM10 7a.5.5 0 01.5.5v7a.5.5 0 01-1 0v-7A.5.5 0 0110 7zm3 .5a.5.5 0 00-1 0v7a.5.5 0 001 0v-7z" clipRule="evenodd"></path>
                                        </svg>
                                    </button>

                                    <h5 className="card-title">{s.title}</h5>

                                    <p className="card-text">
                                        {s.metadata.body}
                                    </p>

                                    <p className="card-text">
                                        <small className="text-muted">
                                            {s.metadata.modified}
                                        </small>
                                    </p>

                                </div>
                            </div>
                        </div>
                    </div>
                );
            });

            let authorName = selections[0].author.public_name ||
                selections[0].author.username;

            let authorAccordion = (
                <div key={key} className="accordion" id="accordionExample2">
                    <div className="card">
                        <div className="card-header" id="headingOne">
                            <h2 className="mb-0">
                                <button
                                    className="btn btn-link" type="button"
                                    data-toggle="collapse" data-target="#collapseOne"
                                    aria-expanded="true" aria-controls="collapseOne">
                                    {authorName}
                                </button>
                            </h2>
                        </div>
                        <div
                            id="collapseOne"
                            className="collapse hide"
                            aria-labelledby="headingOne"
                            data-parent="#accordionExample2">
                            {selectionsDom}
                        </div>
                    </div>
                </div>
            );

            selectionsByAuthorDom.push(authorAccordion);
        }

        let thumbnail = null;
        let media = null;
        if (type === 'image') {
            media = (
                <div
                    id={`map-${this.props.asset.id}`}
                    className="ol-map"></div>
            );
            thumbnail = (
                <img
                    className="img-fluid"
                    alt={'Thumbnail for: ' +
                         this.props.asset.title}
                    src={this.asset.getThumbnail()} />
            );
        } else if (type === 'video') {
            const source = this.props.asset.sources.url.url ||
                  this.props.asset.sources.youtube.url;
            media = (
                <ReactPlayer
                    onReady={this.onPlayerReady}
                    ref={r => this.playerRef = r}
                    url={source}
                    controls={true} width={480} />
            );
            thumbnail = (
                <img
                    style={{'maxWidth': '100%'}}
                    className="img-fluid"
                    alt={'Video thumbnail for: ' +
                         this.props.asset.title}
                    src={this.asset.getThumbnail()} />
            );
        }

        const createNewSelection = (
            <div
                className="accordion" id="selectionAccordion"
                style={{margin: '1em 0em 1em 0em'}}>

                <div className="card">
                    <div className="card-header" id="headingZero">
                        <h2 className="mb-0">
                            <button
                                className="btn btn-link"
                                type="button"
                                data-toggle="collapse"
                                data-target="#collapseZero"
                                aria-expanded="true"
                                aria-controls="collapseZero">
                                + Create a New Selection
                            </button>
                        </h2>
                    </div>
                    <div
                        id="collapseZero"
                        className="collapse show"
                        aria-labelledby="headingZero"
                        data-parent="#selectionAccordion">
                        <div className="card-body">
                            <div className="card mb-3 bg-highlight">
                                <div
                                    className="row no-gutters align-items-center">
                                    <div className="col-md-4">
                                        <div className="card-body">
                                            {thumbnail}
                                        </div>
                                    </div>
                                    <div className="col-md-8">
                                        <div className="card-body">
                                            <form>
                                                {type === 'video' && (
                                                    <table>
                                                        <tbody>
                                                            <tr>
                                                                <td span="0">
                                                                    <div><label htmlFor="annotation-title">Selection Times</label></div>
                                                                </td>
                                                            </tr>
                                                            <tr className="sherd-clipform-editing">
                                                                <td>
                                                                    <input
                                                                        type="button" className="btn-primary"
                                                                        onClick={this.onStartTimeClick}
                                                                        readOnly value="Start Time" id="btnClipStart" />
                                                                </td>
                                                                <td width="10px">&nbsp;</td>
                                                                <td>
                                                                    <input
                                                                        type="button" className="btn-primary"
                                                                        onClick={this.onEndTimeClick}
                                                                        readOnly value="End Time" id="btnClipEnd" /> </td>
                                                                <td>&nbsp;
                                                                </td>
                                                            </tr>
                                                            <tr className="sherd-clipform-editing">
                                                                <td>
                                                                    <input
                                                                        type="text" className="timecode" id="clipStart" readOnly
                                                                        value={this.state.selectionStartTime} /><div className="helptext timecode">HH:MM:SS</div></td>
                                                                <td style={{width: '10px', textAlign: 'center'}}>-</td>
                                                                <td>
                                                                    <input
                                                                        type="text" className="timecode" id="clipEnd" readOnly
                                                                        value={this.state.selectionEndTime} /><div className="helptext timecode">HH:MM:SS</div>
                                                                </td>
                                                                <td className="sherd-clipform-play">
                                                                    <input
                                                                        type="image"
                                                                        title="Play Clip"
                                                                        className="regButton videoplay"
                                                                        onClick={this.toggleVideoPlay}
                                                                        src="/media/img/icons/meth_video_play.png" />

                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                )}
                                                <div className="form-group">
                                                    <label htmlFor="newSelectionTitle">
                                                        Selection Title
                                                    </label>
                                                    <input type="text" className="form-control" id="newSelectionTitle" />
                                                </div>
                                                <div className="form-group">
                                                    <label
                                                        htmlFor="newSelectionNotes">
                                                        Notes
                                                    </label>
                                                    <textarea
                                                        className="form-control"
                                                        id="newSelectionNotes"
                                                        rows="3"></textarea>
                                                </div>
                                                <div className="form-group">
                                                    <label htmlFor="newSelectionTags">Tags</label>
                                                    <input type="text" className="form-control" id="newSelectionTags" />
                                                </div>
                                                <div className="form-group">
                                                    <label htmlFor="newSelectionTerms">Terms</label>
                                                    <select multiple className="form-control" id="newSelectionTerms">
                                                        <option>1</option>
                                                        <option>2</option>
                                                        <option>3</option>
                                                        <option>4</option>
                                                        <option>5</option>
                                                    </select>
                                                </div>
                                                <div>
                                                    <button
                                                        type="button"
                                                        className="btn btn-sm btn-secondary">
                                                        Cancel
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={this.onCreateSelection}
                                                        className="btn btn-sm btn-primary ml-2">
                                                        Save
                                                    </button>
                                                </div>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );

        return (
            <div className="container">
                <Alert
                    variant="success" show={this.state.showCreatedDialog}
                    onClose={this.hideCreatedDialog} dismissible>
                    <Alert.Heading>
                        Selection &quot;{this.state.createdSelectionTitle}&quot; created.
                    </Alert.Heading>
                </Alert>

                <Alert
                    variant="danger" show={this.state.showDeletedDialog}
                    onClose={this.hideDeletedDialog} dismissible>
                    <Alert.Heading>Selection deleted.</Alert.Heading>
                </Alert>

                <button
                    onClick={this.props.toggleAssetView}
                    className="btn btn-secondary btn-sm mt-2">
                    <svg
                        className="octicon octicon-arrow-left octicon-before"
                        viewBox="0 0 10 16" version="1.1" width="10" height="16"
                        aria-hidden="true">
                        <path
                            fillRule="evenodd" fill="white"
                            d="M6 3L0 8l6 5v-3h4V6H6z"></path>
                    </svg> Back
                </button>
                <div className="row">

                    <div className="col-sm-6">
                        <h1>
                            <a href="#">
                                {this.props.asset.title}
                            </a>
                        </h1>

                        {media}

                        <ul className="nav nav-pills nav-fill" id="pills-tab" role="tablist">
                            <li className="nav-item"> <a className="nav-link active" id="pills-details-tab" data-toggle="pill" href="#pills-details" role="tab" aria-controls="pills-details" aria-selected="true">Details</a> </li>
                            <li className="nav-item"> <a className="nav-link" id="pills-source-tab" data-toggle="pill" href="#pills-source" role="tab" aria-controls="pills-source" aria-selected="false">Source</a> </li>
                            <li className="nav-item"> <a className="nav-link" id="pills-references-tab" data-toggle="pill" href="#pills-references" role="tab" aria-controls="pills-references" aria-selected="false">References</a> </li>
                        </ul>

                        <div className="tab-content" id="pills-tabContent">
                            <div className="tab-pane fade show active" id="pills-details" role="tabpanel" aria-labelledby="pills-details-tab">
                                <div className="row no-gutters align-items-center">
                                    <div className="col-md-4">
                                        <div className="card-body">
                                            {thumbnail}
                                        </div>
                                    </div>
                                    <div className="col-md-8">
                                        <div className="card-body">
                                            <h5 className="card-title">
                                                {this.props.asset.title}
                                            </h5>
                                            <p className="card-text">
                                                This is a wider card
                                                with supporting text
                                                below as a natural
                                                lead-in to additional
                                                content. This content
                                                is a little bit
                                                longer.
                                            </p>
                                            <p className="card-text">
                                                <small><a href="#">Tag</a> <a href="#">Tag</a></small>
                                            </p>
                                            <p className="card-text">
                                                <small><a href="#">Term</a> <a href="#">Term</a></small>
                                            </p>
                                            <div>
                                                <button type="button" className="btn btn-sm btn-primary">Edit</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <hr />
                        <div className="row no-gutters align-items-center">
                            <div className="col-md-4">
                                <div className="card-body">
                                    {thumbnail}
                                </div>
                            </div>
                            <div className="col-md-8">
                                <div className="card-body">
                                    <form>
                                        <div className="form-group">
                                            <label htmlFor="exampleFormControlInput1">Item Title</label>
                                            <input type="email" className="form-control" id="exampleFormControlInput1" />
                                        </div>
                                        <div className="form-group">
                                            <label htmlFor="exampleFormControlTextarea1">Notes</label> <textarea className="form-control" id="exampleFormControlTextarea1" rows="3"></textarea>
                                        </div>
                                        <div className="form-group">
                                            <label htmlFor="exampleFormControlInput1">Tags</label>
                                            <input type="email" className="form-control" id="exampleFormControlInput1" />
                                        </div>
                                        <div className="form-group">
                                            <label htmlFor="exampleFormControlSelect2">Terms</label>
                                            <select multiple className="form-control" id="exampleFormControlSelect2">
                                                <option>1</option>
                                                <option>2</option>
                                                <option>3</option>
                                                <option>4</option>
                                                <option>5</option>
                                            </select>
                                        </div>
                                        <div>
                                            <button type="button" className="btn btn-sm btn-secondary">Cancel</button> <button type="button" className="btn btn-sm btn-primary">Save</button> <button type="button" className="btn btn-sm btn-danger">Delete</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>

                    </div>

                    <div className="col-sm-6">
                        <h2>Selections from &quot;{this.props.asset.title}&quot;</h2>

                        {createNewSelection}

                        {selectionsByAuthorDom}
                    </div>

                </div>

                <Modal show={this.state.showDeleteDialog} onHide={this.hideDeleteDialog}>
                    <Modal.Header closeButton>
                        <Modal.Title>Delete annotation</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>Delete this annotation?</Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={this.hideDeleteDialog}>
                            Cancel
                        </Button>
                        <Button variant="danger" onClick={this.onDeleteSelection}>
                            Delete
                        </Button>
                    </Modal.Footer>
                </Modal>
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

AssetDetail.propTypes = {
    asset: PropTypes.object,
    toggleAssetView: PropTypes.func.isRequired,
    onUpdateAsset: PropTypes.func.isRequired
};
