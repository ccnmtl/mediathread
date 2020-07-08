/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import groupBy from 'lodash.groupby';

export default class ViewSelections extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            groupBy: 'author'
        };
    }

    onSelectGrouping(e, grouping) {
        e.preventDefault();
        this.setState({groupBy: grouping});
    }

    renderSelection(s, idx, tags, terms) {
        return (
            <div key={idx} className="card">
                <div className="card-header">
                    <h2 className="card-title mb-0">
                        <button
                            className="btn btn-link btn-block text-left collapsed"
                            type="button"
                            data-toggle="collapse"
                            data-target={`#selectionCollapse-${idx}`}
                            aria-expanded="false">
                            {s.title}
                        </button>
                    </h2>
                </div>
                <div
                    id={`selectionCollapse-${idx}`}
                    className="collapse"
                    data-parent="#selectionsAccordion">
                    <div className="card-body">
                        {tags.length > 0 && (
                            <p className="card-text">
                                {tags}
                            </p>
                        )}

                        {terms.length > 0 && (
                            <p className="card-text">
                                {terms}
                            </p>
                        )}

                        {s.metadata && s.metadata.body && (
                            <p className="card-text">
                                {s.metadata.body}
                            </p>
                        )}

                        <p className="card-text">
                            <a href="#" className="btn btn-secondary btn-sm">
                                Edit
                            </a>&nbsp;
                            <a href="#" className="btn btn-secondary btn-sm">
                                Copy
                            </a>&nbsp;
                            <a
                                href="#" className="btn btn-primary btn-sm"
                                onClick={(e) => this.props.onViewSelection(e, s)}>
                                View
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    render() {
        const me = this;

        const checkmark = (
            <svg
                width="1em" height="1em" viewBox="0 0 16 16"
                className="bi bi-check" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path
                    fillRule="evenodd"
                    d="M10.97 4.97a.75.75 0 0 1 1.071 1.05l-3.992 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.236.236 0 0 1 .02-.022z" />
            </svg>
        );

        const selections = groupBy(
            this.props.asset.annotations,
            function(s) {
                return s.author.id;
            }
        );

        const groupedSelections = [];
        for (const key in selections) {
            const selectionGroup = selections[key];

            selectionGroup.forEach(function(s, idx) {
                if (idx === 0) {
                    groupedSelections.push(
                        <h5 key={'title-' + idx}>{s.author.public_name}</h5>
                    );
                }

                const tags = [];
                if (s.metadata && s.metadata.tags) {
                    s.metadata.tags.forEach(function(tag, idx) {
                        tags.push(<a key={idx} href="#">{tag.name}</a>);
                    });
                }

                const terms = [];
                if (s.vocabulary) {
                    s.vocabulary.forEach(function(term, idx) {
                        terms.push(<a key={idx} href="#">{term.name}</a>);
                    });
                }

                groupedSelections.push(me.renderSelection(s, idx, tags, terms));
            });
        }


        return (
            <React.Fragment>
                <h3>
                    Selections
                </h3>
                <div className="btn-group mb-2">
                    <a
                        className="btn btn-light dropdown-toggle"
                        data-toggle="dropdown" aria-haspopup="true"
                        aria-expanded="false">Group </a>
                    <div className="dropdown-menu">
                        <a
                            className="dropdown-item"
                            onClick={(e) => this.onSelectGrouping(e, 'author')}>
                            {this.state.groupBy === 'author' && checkmark}
                            by author
                        </a>
                        <a
                            className="dropdown-item"
                            onClick={(e) => this.onSelectGrouping(e, 'tag')}>
                            {this.state.groupBy === 'tag' && checkmark}
                            by tag
                        </a>
                    </div>
                </div>

                <Alert variant="warning" show={!selections.length}>
                    There are no selections of this item.&nbsp;
                    <Alert.Link href="#">Create a selection</Alert.Link> now to begin.
                </Alert>

                <div className="accordion" id="selectionsAccordion">
                    {groupedSelections}
                </div>

                <Modal
                    show={this.props.showDeleteDialogBool}
                    onHide={this.props.hideDeleteDialog}>
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
            </React.Fragment>
        );

    }
}

ViewSelections.propTypes = {
    asset: PropTypes.object,
    onViewSelection: PropTypes.func.isRequired,
    hideDeleteDialog: PropTypes.func.isRequired,
    showDeleteDialog: PropTypes.func.isRequired,
    showDeleteDialogBool: PropTypes.bool.isRequired
};
