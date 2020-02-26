/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Map from 'ol/Map';
import View from 'ol/View';
import {getCenter} from 'ol/extent';
import ImageLayer from 'ol/layer/Image';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Projection from 'ol/proj/Projection';
import Static from 'ol/source/ImageStatic';

import Asset from './Asset';

export default class AssetDetail extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            annotationLayer: new VectorLayer({
                source: new VectorSource()
            }),
            selectedAnnotation: null
        };

        this.asset = new Asset(this.props.asset);
    }

    render() {
        const selections = [];

        const me = this;
        this.props.asset.annotations.forEach(function(s) {
            selections.push(
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

        const type = this.asset.getType();

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
            media = (
                <img
                    style={{'maxWidth': '100%'}}
                    className="img-fluid"
                    alt={'Video thumbnail for: ' +
                         this.props.asset.title}
                    src={this.asset.getThumbnail()} />
            );
            thumbnail = media;
        }

        const createNewSelection = (
            <div
                className="accordion" id="accordionExample1"
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
                                Create a New Selection
                            </button>
                        </h2>
                    </div>
                    <div
                        id="collapseZero"
                        className="collapse show"
                        aria-labelledby="headingZero"
                        data-parent="#accordionExample1">
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
                                                <div className="form-group">
                                                    <label htmlFor="exampleFormControlInput1">Selection Title</label>
                                                    <input type="email" className="form-control" id="exampleFormControlInput1" />
                                                </div>
                                                <div className="form-group">
                                                    <label
                                                        htmlFor="exampleFormControlTextarea1">
                                                        Notes
                                                    </label>
                                                    <textarea
                                                        className="form-control"
                                                        id="exampleFormControlTextarea1"
                                                        rows="3"></textarea>
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
                                                    <button type="button" className="btn btn-sm btn-secondary">Cancel</button> <button type="button" className="btn btn-sm btn-primary">Save</button>
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

                        <button className="btn btn-light dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> Display Selections </button>
                        <div className="dropdown-menu">
                            <form className="px-4 py-3">
                                <div className="form-group">
                                    <label htmlFor="exampleDropdownFormEmail1">Group selections by:</label>
                                    <div className="form-check">
                                        <input className="form-check-input" type="radio" name="exampleRadios" id="exampleRadios1" value="option1" checked readOnly />
                                        <label className="form-check-label" htmlFor="exampleRadios1"> author </label>
                                    </div>
                                    <div className="form-check">
                                        <input className="form-check-input" type="radio" name="exampleRadios" id="exampleRadios2" value="option2" />
                                        <label className="form-check-label" htmlFor="exampleRadios2"> tag </label>
                                    </div>
                                </div>
                                <div className="dropdown-divider">
                                </div>
                                <div className="form-group">
                                    <div className="form-check">
                                        <input type="checkbox" className="form-check-input" id="dropdownCheck" />
                                        <label className="form-check-label" htmlFor="dropdownCheck">
                                            Display all selections.
                                            <br />
                                            <small className="text-muted">
                                                This option shows all
                                                selections graphically
                                                on the video to the
                                                left.
                                            </small>
                                        </label>
                                    </div>
                                </div>
                            </form>
                        </div>

                        <div className="accordion" id="accordionExample2">
                            <div className="card">
                                <div className="card-header" id="headingOne">
                                    <h2 className="mb-0">
                                        <button className="btn btn-link" type="button" data-toggle="collapse" data-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne"> Marc</button>
                                    </h2>
                                </div>
                                <div id="collapseOne" className="collapse hide" aria-labelledby="headingOne" data-parent="#accordionExample2">
                                    {selections}
                                </div>
                            </div>
                        </div>
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
    toggleAssetView: PropTypes.func.isRequired
};
