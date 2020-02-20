/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

export default class AssetDetail extends React.Component {
    render() {
        const selections = [];

        const me = this;
        this.props.asset.annotations.forEach(function(s) {
            selections.push(
                <div
                    key={s.id}
                    className="card mb-3" style={{'maxWidth': '540px'}}>
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
                                            <img
                                                src="https://dummyimage.com/1600x900/000000/ffffff&text=Item&nbsp;Thumbnail"
                                                className="img-fluid"
                                                alt="Responsive image" />
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
                        <div>box</div>
                    </div>

                    <div className="col-sm-6">
                        <h2>Selections from &quot;{this.props.asset.title}&quot;</h2>

                        {createNewSelection}

                        {selections}
                    </div>

                </div>

            </div>
        );
    }
}

AssetDetail.propTypes = {
    asset: PropTypes.object,
    toggleAssetView: PropTypes.func.isRequired
};
