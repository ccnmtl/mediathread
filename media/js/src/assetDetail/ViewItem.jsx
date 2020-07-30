/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Alert from 'react-bootstrap/Alert';

import {getAssetReferences} from '../utils';

export default class ViewItem extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            references: null
        };

        const me = this;
        getAssetReferences(this.props.asset.id).then(function(data) {
            if ('references' in data) {
                me.setState({references: data['references']});
            }
        });
    }
    render() {
        const references = [];

        let authorId = null;
        if (this.props.asset && this.props.asset.author) {
            authorId = this.props.asset.author.id;
        }

        let userIsAuthor = false;
        if (window.MediaThread && window.MediaThread.current_user) {
            userIsAuthor = authorId === window.MediaThread.current_user;
        }

        if (this.state.references) {
            this.state.references.forEach(function(reference, idx) {
                references.push(
                    <div className="card w-100 card-selection" key={idx}>
                        <div className="card-body">
                            <h5 className="card-title">
                                <div>
                                    {reference.title}
                                </div>
                            </h5>
                            <h6>
                                Assignment
                            </h6>
                            <p className="card-text">
                                Collected 12/19/15 01:02 AM
                            </p>
                            <a href="#" className="btn btn-primary btn-sm">
                                View
                            </a>
                        </div>
                    </div>
                );
            });
        }

        return (
            <div className="tab-content" id="pills-tabContent">
                <table className="table mt-1">
                    <tbody>
                        <tr>
                            <th scope="row">Item Name</th>
                            <td>
                                {this.props.asset.title}
                                &nbsp;
                                {userIsAuthor && (
                                    <button type="submit" className="btn btn-secondary btn-sm">
                                        Rename
                                    </button>
                                )}
                            </td>
                        </tr>
                        <tr>
                            <th scope="row">Permalink</th>
                            <td>
                                <a href="">
                                    {window.location.href}
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <th scope="row">Creator</th>
                            <td>
                                {this.props.asset.author.public_name} ({this.props.asset.author.username})
                            </td>
                        </tr>
                    </tbody>
                </table>

                <button type="submit" className="btn btn-danger btn-sm mb-2">
                    Remove from my Collection
                </button>

                <h4>
                    Item References within Course
                </h4>

                <div className="btn-group">
                    <a
                        className="btn btn-light dropdown-toggle"
                        data-toggle="dropdown" aria-haspopup="true"
                        aria-expanded="false">
                        Sort by
                    </a>
                    <div className="dropdown-menu">
                        <a className="dropdown-item" href="#">
                            Title, A &ndash; Z
                        </a>
                        <a className="dropdown-item" href="#">
                            Title, Z &ndash; A
                        </a>
                    </div>
                </div>

                <Alert variant="warning" show={
                    this.state.references && this.state.references.length === 0
                }>
                    There are no references in this course.
                </Alert>

                {references}
            </div>
        );

    }
}

ViewItem.propTypes = {
    asset: PropTypes.object
};
