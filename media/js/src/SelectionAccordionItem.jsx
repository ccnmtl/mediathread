/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import {formatTimecode} from './utils';

export default class SelectionAccordionItem extends React.Component {
    render() {
        const selection = this.props.selection;

        return (
            <div
                key={selection.id}
                className="card" style={{'maxWidth': '540px'}}>
                <div className="row no-gutters">
                    <div className="col-md-4">
                        <img
                            src={this.props.asset.thumb_url}
                            className="card-img" alt="..." />
                    </div>

                    <div className="col-md-8">
                        <div className="card-body">
                            <button
                                className="btn btn-sm btn-danger"
                                data-id={selection.id}
                                onClick={() => this.props.showDeleteDialog(selection.id)}>
                                <svg className="bi bi-trash-fill" width="1em" height="1em" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                    <path fillRule="evenodd" d="M4.5 3a1 1 0 00-1 1v1a1 1 0 001 1H5v9a2 2 0 002 2h6a2 2 0 002-2V6h.5a1 1 0 001-1V4a1 1 0 00-1-1H12a1 1 0 00-1-1H9a1 1 0 00-1 1H4.5zm3 4a.5.5 0 01.5.5v7a.5.5 0 01-1 0v-7a.5.5 0 01.5-.5zM10 7a.5.5 0 01.5.5v7a.5.5 0 01-1 0v-7A.5.5 0 0110 7zm3 .5a.5.5 0 00-1 0v7a.5.5 0 001 0v-7z" clipRule="evenodd"></path>
                                </svg>
                            </button>

                            <button
                                className="ml-1 btn btn-sm btn-secondary"
                                data-id={selection.id}>
                                <svg className="bi bi-pencil" width="1em" height="1em" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                    <path fillRule="evenodd" d="M13.293 3.293a1 1 0 011.414 0l2 2a1 1 0 010 1.414l-9 9a1 1 0 01-.39.242l-3 1a1 1 0 01-1.266-1.265l1-3a1 1 0 01.242-.391l9-9zM14 4l2 2-9 9-3 1 1-3 9-9z" clipRule="evenodd"></path>
                                    <path fillRule="evenodd" d="M14.146 8.354l-2.5-2.5.708-.708 2.5 2.5-.708.708zM5 12v.5a.5.5 0 00.5.5H6v.5a.5.5 0 00.5.5H7v.5a.5.5 0 00.5.5H8v-1.5a.5.5 0 00-.5-.5H7v-.5a.5.5 0 00-.5-.5H5z" clipRule="evenodd"></path>
                                </svg>
                            </button>

                            {this.props.type === 'video' && (
                                <React.Fragment>
                                    <button
                                        className="ml-1 btn btn-sm btn-secondary"
                                        data-id={selection.id}
                                        onClick={() => this.props.onClickPlay(selection)}>
                                        <svg className="bi bi-play-fill" width="1em" height="1em" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M13.596 10.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V6.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 010 1.393z"></path>
                                        </svg>
                                    </button>

                                    <small className="ml-2">
                                        {formatTimecode(selection.range1)} &ndash; {formatTimecode(selection.range2)}
                                    </small>
                                </React.Fragment>
                            )}

                            <h5 className="card-title">
                                <a href="#" onClick={() => this.props.onClickSelection(selection)}>
                                    {selection.title}
                                </a>
                            </h5>

                            <p className="card-text">
                                {selection.metadata.body}
                            </p>

                            <p className="card-text">
                                <small className="text-muted">
                                    {selection.metadata.modified}
                                </small>
                            </p>

                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

SelectionAccordionItem.propTypes = {
    asset: PropTypes.object.isRequired,
    type: PropTypes.string.isRequired,
    selection: PropTypes.object.isRequired,
    onClickPlay: PropTypes.func.isRequired,
    onClickSelection: PropTypes.func.isRequired,
    showDeleteDialog: PropTypes.func.isRequired
};
