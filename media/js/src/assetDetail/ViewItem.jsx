/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Form from 'react-bootstrap/Form';

import find from 'lodash/find';

import {
    getAssetReferences, removeAsset, getTags, getTerms, updateAssetTitle
} from '../utils';

export default class ViewItem extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            references: null,
            validated: false,
            isRenaming: false,
            assetTitleEditing: this.props.asset ? this.props.asset.title : null,
            assetTitle: this.props.asset ? this.props.asset.title : null
        };

        const me = this;
        getAssetReferences(this.props.asset.id).then(function(data) {
            if ('references' in data) {
                me.setState({references: data['references']});
            }
        });

        this.onClickRename = this.onClickRename.bind(this);
        this.onClickCancel = this.onClickCancel.bind(this);
        this.onClickRemove = this.onClickRemove.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.onChangeTitle = this.onChangeTitle.bind(this);
    }

    onClickRename(e) {
        this.setState({isRenaming: true});
    }

    onClickCancel(e) {
        this.setState({isRenaming: false});
    }

    onClickRemove(e) {
        const r = window.confirm('Remove this asset from your collection?');

        if (r === true) {
            const me = this;
            return removeAsset(this.props.asset.id)
                .then(function() {
                    return me.props.leaveAssetDetailView();
                }).then(function() {
                    window.scrollTo(0, 0);
                });
        }

        return null;
    }

    handleSubmit(e) {
        e.preventDefault();

        const form = e.currentTarget;
        if (form.checkValidity() === false) {
            e.stopPropagation();
            this.props.onShowValidationError('Please specify an item title.');
        } else {
            const me = this;
            return updateAssetTitle(this.props.asset.id, this.state.assetTitleEditing)
                .then(function() {
                    me.setState({
                        isRenaming: false,
                        assetTitle: me.state.assetTitleEditing
                    });
                    me.props.onUpdateAssetTitle(me.state.assetTitleEditing);
                });
        }

        return this.setState({validated: true});
    }

    onChangeTitle(e) {
        this.setState({assetTitleEditing: e.target.value});
    }

    render() {
        let authorId = null;
        if (this.props.asset && this.props.asset.author) {
            authorId = this.props.asset.author.id;
        }

        let userIsAuthor = false;
        if (window.MediaThread && window.MediaThread.current_user) {
            userIsAuthor = authorId === window.MediaThread.current_user;
        }

        const references = [];
        if (this.state.references) {
            this.state.references.forEach(function(reference, idx) {
                references.push(
                    <li key={idx}>
                        <a href={reference.url}>{reference.title}</a>
                    </li>
                );
            });
        }

        let tags = 'There are no tags.';
        let terms = 'There are no vocabulary terms.';
        if (this.props.asset && this.props.asset.annotations) {
            const tagsArray = getTags(this.props.asset.annotations);
            if (tagsArray.length > 0) {
                tags = tagsArray.join(', ');
            }

            const termsArray = getTerms(this.props.asset.annotations);
            if (termsArray.length > 0) {
                terms = termsArray.join(', ');
            }
        }

        let description = null;
        if (this.props.asset && this.props.asset.metadata) {
            let desc = find(this.props.asset.metadata, {key: 'Description'});
            if (desc) {
                desc = desc.value;
            }
            if (desc && desc.length) {
                description = desc[0];
            }
        }

        const permalink = window.location.href;

        return (
            <div className="tab-content" id="pills-tabContent">
                <h3>Tags</h3>
                <p>
                    {tags}
                </p>

                <hr />

                <h3>Course Vocabulary</h3>
                <p>
                    {terms}
                </p>

                <hr />

                <h3>Course References</h3>
                {this.state.references && this.state.references.length === 0 && (
                    <div>There are no references in this course.</div>
                )}

                {this.state.references && this.state.references.length > 0 && (
                    <ul>
                        {references}
                    </ul>
                )}

                <hr />

                <h3>Additional Information (Metadata)</h3>
                <table className="table table-sm table-borderless mt-1 table-metadata">
                    <tbody>
                        <tr>
                            <th scope="row">Item Name</th>
                            <td>
                                {this.state.isRenaming && (
                                    <Form
                                        noValidate
                                        validated={this.state.validated}
                                        onSubmit={this.handleSubmit}>
                                        <Form.Group className="mb-3">
                                            <Form.Control
                                                required
                                                type="text"
                                                aria-label="Item Name"
                                                size="sm"
                                                className="mb-1"
                                                onChange={this.onChangeTitle}
                                                value={this.state.assetTitleEditing} />
                                            <button
                                                onClick={this.onClickCancel}
                                                type="button"
                                                className="btn btn-sm btn-secondary mr-1">
                                                Cancel
                                            </button>
                                            <button
                                                type="submit"
                                                className="btn btn-sm btn-primary">
                                                Save
                                            </button>
                                        </Form.Group>
                                    </Form>
                                )}

                                {!this.state.isRenaming && (
                                    <>
                                        {this.state.assetTitle}
                                        &nbsp;
                                        {userIsAuthor && (
                                            <button
                                                type="submit"
                                                onClick={this.onClickRename}
                                                className="btn btn-secondary btn-sm d-block my-1">
                                                Rename this item
                                            </button>
                                        )}
                                    </>
                                )}
                            </td>
                        </tr>
                        <tr>
                            <th scope="row">Permalink</th>
                            <td className="text-break">
                                <a href={permalink}>
                                    {permalink}
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <th scope="row">Creator</th>
                            <td>
                                {this.props.asset.author.public_name} ({this.props.asset.author.username})
                            </td>
                        </tr>
                        {this.props.asset && this.props.asset.sources && this.props.asset.sources.url && (
                            <tr>
                                <th scope="row">Link</th>
                                <td>
                                    <a href={this.props.asset.sources.url.url} target="_blank" rel="noopener noreferrer">
                                       Original Source
                                    </a>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>

                {description && (
                    <div>
                        <div className="font-weight-bold">Description</div>
                        <p className="description">
                            {description}
                        </p>
                    </div>
                )}

                {this.props.asset && this.props.asset.editable && (
                    <button
                        type="button"
                        className="btn btn-danger btn-sm float-right"
                        onClick={this.onClickRemove}>
                        Remove from my Collection
                    </button>
                )}
            </div>
        );

    }
}

ViewItem.propTypes = {
    asset: PropTypes.object,
    onUpdateAssetTitle: PropTypes.func.isRequired,
    onShowValidationError: PropTypes.func.isRequired,
    leaveAssetDetailView: PropTypes.func.isRequired
};
