import React from 'react';
import PropTypes from 'prop-types';

import {updateAsset, truncateString} from '../utils';

export default class TranscriptForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            isEditing: false,
            transcript: this.props.asset.transcript
        };
        this.onClickEdit = this.onClickEdit.bind(this);
        this.onClickCancel = this.onClickCancel.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    onClickEdit() {
        this.setState({isEditing: true});
    }

    onClickCancel() {
        this.setState({isEditing: false});
    }

    handleSubmit(e) {
        e.preventDefault();

        const form = e.currentTarget;
        let newTranscript = form.querySelector('textarea').value;
        if (newTranscript) {
            newTranscript = newTranscript.trim();
        }

        const me = this;
        return updateAsset(this.props.asset.id, {
            transcript: newTranscript
        }).then(function() {
            me.setState({
                isEditing: false,
                transcript: newTranscript
            });

            me.props.onUpdateAssetTranscript(newTranscript);
        });
    }

    render() {
        let transcriptArea = (
            <React.Fragment>
                {truncateString(this.state.transcript, 40)}
                <button
                    className="btn btn-sm btn-secondary d-block"
                    onClick={this.onClickEdit}>
                    Edit Transcript
                </button>
            </React.Fragment>
        );
        if (this.state.isEditing) {
            transcriptArea = (
                <form onSubmit={this.handleSubmit}>
                    <textarea
                        className="form-control mb-1"
                        id="assetTranscriptInput"
                        rows="4"
                        defaultValue={this.state.transcript}>
                    </textarea>
                    <button
                        className="btn btn-sm btn-secondary"
                        onClick={this.onClickCancel}
                        type="button">
                        Cancel
                    </button>
                    <button
                        className="btn btn-sm btn-primary ml-1"
                        onClick={this.onClickSave}
                        type="submit">
                        Save
                    </button>
                </form>
            );
        }

        return (
            <tr>
                <th scope="row">
                    <label
                        htmlFor="assetTranscriptInput">
                        Transcript
                    </label>
                </th>
                <td>
                    {transcriptArea}
                </td>
            </tr>
        );
    }
}

TranscriptForm.propTypes = {
    asset: PropTypes.object.isRequired,
    onUpdateAssetTranscript: PropTypes.func.isRequired
};
