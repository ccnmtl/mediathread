/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Alert from 'react-bootstrap/Alert';

export default class CreateSelection extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <React.Fragment>
                <h3>Additional Selection Information</h3>

                <Alert
                    variant="danger" show={this.props.showCreateError}
                    id="create-error-alert">
                    <Alert.Heading>Error creating selection.</Alert.Heading>
                    <p>
                        {this.props.createError}
                    </p>
                </Alert>

                <div className="card w-100">
                    <div
                        id="collapseZero"
                        className="collapse show"
                        aria-labelledby="headingZero"
                        data-parent="#selectionAccordion">
                        <div className="card-body">
                            <form>
                                <div className="form-group">
                                    <label htmlFor="newSelectionTitle">
                                        Title
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="newSelectionTitle" />
                                </div>

                                <div className="form-group">
                                    <label htmlFor="newSelectionTerms">Terms</label>
                                    <select multiple className="form-control" id="newSelectionTerms">
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label htmlFor="newSelectionTags">Tags</label>
                                    <input type="text" className="form-control" id="newSelectionTags" />
                                </div>

                                <div className="form-group">
                                    <label
                                        htmlFor="newSelectionNotes">
                                        Notes
                                    </label>
                                    <textarea
                                        className="form-control"
                                        id="newSelectionNotes"
                                        rows="3">
                                    </textarea>
                                </div>

                                <div>
                                    <button
                                        type="button"
                                        onClick={this.props.onCreateSelection}
                                        className="btn btn-sm btn-primary ml-2">
                                        Save
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        );

    }
}

CreateSelection.propTypes = {
    asset: PropTypes.object,
    selectionStartTime: PropTypes.number,
    selectionEndTime: PropTypes.number,
    onStartTimeUpdate: PropTypes.func.isRequired,
    onEndTimeUpdate: PropTypes.func.isRequired,
    onStartTimeClick: PropTypes.func.isRequired,
    onEndTimeClick: PropTypes.func.isRequired,
    onCreateSelection: PropTypes.func.isRequired,
    showCreateError: PropTypes.bool.isRequired,
    createError: PropTypes.string
};
