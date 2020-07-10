/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import {groupByAuthor, groupByTag, getTagName} from '../utils';

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

    renderSelection(s, key, tags, terms) {
        return (
            <div key={key} className="card">
                <div className="card-header">
                    <h2 className="card-title mb-0">
                        <button
                            className="btn btn-link btn-block text-left collapsed"
                            type="button"
                            data-toggle="collapse"
                            data-target={`#selectionCollapse-${key}`}
                            aria-expanded="false">
                            {s.title}
                        </button>
                    </h2>
                </div>
                <div
                    id={`selectionCollapse-${key}`}
                    className="collapse"
                    data-parent="#selectionsAccordion">
                    <div className="card-body">
                        {tags.length > 0 && (
                            <p className="card-text">
                                Tags: {tags}
                            </p>
                        )}

                        {terms.length > 0 && (
                            <p className="card-text">
                                Terms: {terms}
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


    /**
     * Given an object containing grouped selections, render this to a
     * react element list.
     */
    renderSelectionGroup(selections) {
        const me = this;
        const groupedSelections = [];
        let i = 0;
        for (const key in selections) {
            const selectionGroup = selections[key];

            selectionGroup.forEach(function(s, idx) {
                const reactKey = `${key}-${s.id}`;
                if (idx === 0) {
                    if (me.state.groupBy === 'author') {
                        groupedSelections.push(
                            <h5 key={'title-' + reactKey}>
                                {s.author.public_name}
                            </h5>);
                    } else {
                        groupedSelections.push(
                            <h5 key={'title-' + reactKey}>
                                {getTagName(key, s)}
                            </h5>);
                    }
                }

                const tags = [];
                if (s.metadata && s.metadata.tags) {
                    s.metadata.tags.forEach(function(tag, idx) {
                        const isNotLast = idx < s.metadata.tags.length - 1;
                        tags.push(
                            <React.Fragment key={`tagfragment-${reactKey}-${tag.id}`}>
                                <a href="#">
                                    {tag.name}
                                </a>{isNotLast && ', '}
                            </React.Fragment>
                        );
                    });
                }

                const terms = [];
                if (s.vocabulary) {
                    s.vocabulary.forEach(function(term, idx) {
                        const isNotLast = idx < s.vocabulary.length - 1;
                        terms.push(
                            <React.Fragment key={`termfragment-${reactKey}-${term.id}`}>
                                <a href="#">
                                    {term.display_name}
                                </a>{isNotLast && ', '}
                            </React.Fragment>
                        );
                    });
                }

                groupedSelections.push(me.renderSelection(
                    s, reactKey, tags, terms));

                if (
                    idx >= selectionGroup.length - 1 &&
                        i < Object.keys(selections).length - 1
                ) {
                    groupedSelections.push(<hr key={'hr-' + reactKey} />);
                }
            });

            i++;
        }

        return groupedSelections;
    }

    render() {
        const checkmark = (
            <svg
                width="1em" height="1em" viewBox="0 0 16 16"
                className="bi bi-caret-right-fill mr-1"
                fill="currentColor"
                xmlns="http://www.w3.org/2000/svg">
                <path d="M12.14 8.753l-5.482 4.796c-.646.566-1.658.106-1.658-.753V3.204a1 1 0 0 1 1.659-.753l5.48 4.796a1 1 0 0 1 0 1.506z"/>
            </svg>
        );

        let selections = {};
        if (this.state.groupBy === 'author') {
            selections = groupByAuthor(this.props.asset.annotations);
        } else {
            selections = groupByTag(this.props.asset.annotations);
        }

        const groupedSelections = this.renderSelectionGroup(selections);

        let noSelections = true;
        if (
            this.props.asset &&
                this.props.asset.annotations &&
                this.props.asset.annotations.length
        ) {
            noSelections = false;
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

                <Alert variant="warning" show={noSelections}>
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
