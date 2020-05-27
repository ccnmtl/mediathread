/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Asset from '../Asset';

import {formatTimecode} from '../utils';

export default class CreateSelection extends React.Component {
    constructor(props) {
        super(props);
        this.asset = new Asset(this.props.asset);
    }

    render() {
        let thumbnail = null;
        const type = this.asset.getType();
        if (type === 'image') {
            thumbnail = (
                <img
                    className="img-fluid"
                    alt={'Thumbnail for: ' +
                         this.props.asset.title}
                    src={this.asset.getThumbnail()} />
            );
        } else if (type === 'video') {
            thumbnail = (
                <img
                    style={{'maxWidth': '100%'}}
                    className="img-fluid"
                    alt={'Video thumbnail for: ' +
                         this.props.asset.title}
                    src={this.asset.getThumbnail()} />
            );
        }

        return (
            <React.Fragment>
                <h2>Selections from &quot;{this.props.asset.title}&quot;</h2>
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
                                                                            value="End Time" id="btnClipEnd" /> </td>
                                                                    <td>&nbsp;
                                                                    </td>
                                                                </tr>
                                                                <tr className="sherd-clipform-editing">
                                                                    <td>
                                                                        <input
                                                                            type="text" className="timecode form-control"
                                                                            id="clipStart" onChange={this.onStartTimeUpdate}
                                                                            value={formatTimecode(this.state.selectionStartTime)} />
                                                                        <div className="helptext timecode">HH:MM:SS</div>
                                                                    </td>
                                                                    <td style={{width: '10px', textAlign: 'center'}}>-</td>
                                                                    <td>
                                                                        <input
                                                                            type="text" className="timecode form-control"
                                                                            id="clipEnd" onChange={this.onEndTimeUpdate}
                                                                            value={formatTimecode(this.state.selectionEndTime)} />
                                                                        <div className="helptext timecode">HH:MM:SS</div>
                                                                    </td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    )}
                                                    <div className="form-group">
                                                        <label htmlFor="newSelectionTitle">
                                                            Selection Title
                                                        </label>
                                                        <input
                                                            type="text"
                                                            className="form-control"
                                                            id="newSelectionTitle" />
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
            </React.Fragment>
        );

    }
}

CreateSelection.propTypes = {
    asset: PropTypes.object
};
