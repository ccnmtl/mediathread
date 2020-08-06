/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';

import find from 'lodash/find';

import EditSelectionForm from '../forms/EditSelectionForm';
import {groupByAuthor, groupByTag, formatTimecode, getDuration} from '../utils';

export default class ViewSelections extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            groupBy: 'author',
            isEditing: null
        };

        this.onClickEdit = this.onClickEdit.bind(this);
        this.onClickCancel = this.onClickCancel.bind(this);
        this.onClickDelete = this.onClickDelete.bind(this);
        this.onDeleteSelection = this.onDeleteSelection.bind(this);
        this.onSaveSelection = this.onSaveSelection.bind(this);
    }

    onSelectGrouping(e, grouping) {
        e.preventDefault();
        this.setState({groupBy: grouping});
    }

    onClickEdit(e, s) {
        e.preventDefault();
        this.setState({isEditing: s});
    }

    onClickCancel(e) {
        e.preventDefault();
        this.setState({isEditing: null});
    }

    onClickDelete(selectionId) {
        this.props.showDeleteDialog(selectionId);
    }

    onDeleteSelection(e) {
        this.setState({isEditing: false});
        return this.props.onDeleteSelection(e);
    }

    onSaveSelection(e, selectionId, tags, terms) {
        this.setState({isEditing: false});
        return this.props.onSaveSelection(
            e, selectionId, tags, terms);
    }

    renderSelection(s, key, tags, terms) {
        const isAuthor = parseInt(
            window.MediaThread.current_user, 10
        ) === parseInt(s.author.id, 10);

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
                    data-title={s.title}
                    data-selectionid={s.id}
                    data-parent="#selectionsAccordion">
                    <div className="card-body">
                        {this.props.type === 'video' && (
                            <>
                                <p className="card-text">
                                    {formatTimecode(s.range1)}
                                    {String.fromCharCode(160)}
                                    {String.fromCharCode(8212)}
                                    {String.fromCharCode(160)}
                                    {formatTimecode(s.range2)}
                                </p>
                                <p className="card-text">
                                    Duration: <strong>{formatTimecode(getDuration(s.range1, s.range2))}</strong>
                                </p>
                            </>
                        )}

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
                            {isAuthor && (
                                <a
                                    onClick={(e) => this.onClickEdit(e, s)}
                                    href="#"
                                    className="btn btn-secondary btn-sm mr-2">
                                    Edit
                                </a>
                            )}

                            {this.props.type === 'video' && (
                                <button
                                    onClick={this.props.onPlaySelection}
                                    className="btn btn-primary btn-sm">
                                    Play
                                    <svg
                                        width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-play-fill ml-1"
                                        fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>
                                    </svg>
                                </button>
                            )}
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
        for (const key in selections) {
            let selectionGroup = selections[key];
            let tagName = null;

            if (
                Object.prototype.hasOwnProperty.call(
                    selectionGroup, 'selections')
            ) {
                tagName = selectionGroup.tagName;
                selectionGroup = selectionGroup.selections;
            }

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
                                {tagName}
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
                    s.vocabulary.forEach(function(vocab) {
                        vocab.terms.forEach(function(term) {
                            terms.push(
                                <React.Fragment key={`termfragment-${reactKey}-${term.id}`}>
                                    <a href="#">
                                        {term.display_name}
                                    </a>,&nbsp;
                                </React.Fragment>
                            );
                        });
                    });
                }

                groupedSelections.push(me.renderSelection(
                    s, reactKey, tags, terms));

            });
        }

        return groupedSelections;
    }


    renderEditForm(selection) {
        return (
            <React.Fragment>
                <h3>Edit Details</h3>
                <EditSelectionForm
                    type={this.props.type}
                    selection={selection}
                    tags={this.props.tags}
                    terms={this.props.terms}
                    onClickCancel={this.onClickCancel}
                    onSaveSelection={this.onSaveSelection}
                    onClickDelete={this.onClickDelete}
                    onShowValidationError={this.props.onShowValidationError}
                />

                <Modal
                    show={this.props.showDeleteDialogBool}
                    onHide={this.props.hideDeleteDialog}>
                    <Modal.Header closeButton>
                        <Modal.Title>Delete Selection</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>Delete this selection?</Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={this.props.hideDeleteDialog}>
                            Cancel
                        </Button>
                        <Button
                            variant="danger"
                            onClick={this.onDeleteSelection}>
                            Delete
                        </Button>
                    </Modal.Footer>
                </Modal>
            </React.Fragment>
        );
    }

    render() {
        if (this.state.isEditing) {
            return this.renderEditForm(this.state.isEditing);
        }

        let selections = {};
        if (this.state.groupBy === 'author') {
            selections = groupByAuthor(this.props.filteredSelections);
        } else {
            selections = groupByTag(this.props.filteredSelections);
        }

        const groupedSelections = this.renderSelectionGroup(selections);

        let noSelections = true;
        if (
            this.props.filteredSelections &&
                this.props.filteredSelections.length
        ) {
            noSelections = false;
        }

        return (
            <React.Fragment>
                <h4>
                    Selections
                </h4>

                <div className="d-flex">
                    <div
                        className="btn-group mb-2" role="group"
                        aria-label="View Toggle">
                        <button
                            type="button"
                            className={'btn btn-outline-secondary btn-sm ' + (
                                this.state.groupBy === 'author' ? 'active' : ''
                            )}
                            onClick={(e) => this.onSelectGrouping(e, 'author')}>
                            Group by author
                        </button>
                        <button
                            type="button"
                            className={'btn btn-outline-secondary btn-sm ' + (
                                this.state.groupBy === 'tag' ? 'active' : ''
                            )}
                            onClick={(e) => this.onSelectGrouping(e, 'tag')}>
                            Group by tag
                        </button>
                    </div>

                    <form className="form-inline">
                        <div className="form-group">
                            <label htmlFor="annotationFilter" className="ml-2">
                                Filter by:
                            </label>
                            <input
                                id="annotationFilter"
                                className="form-control form-control-sm ml-1"
                                type="search"
                            />
                        </div>
                    </form>
                </div>

                <Alert variant="warning" show={noSelections}>
                    There are no selections of this item.&nbsp;
                    <Alert.Link href="#">Create a selection</Alert.Link> now to begin.
                </Alert>

                <div className="accordion" id="selectionsAccordion">
                    {groupedSelections}
                </div>
            </React.Fragment>
        );
    }

    /**
     * Returns true if the selections according doesn't have any
     * annotations selected.
     */
    isCollapsed() {
        return jQuery(
            '#selectionsAccordion .card .collapse.show'
        ).length === 0;
    }

    registerAccordionEvents() {
        const me = this;
        const $selectionsAccordion = jQuery('#selectionsAccordion');

        $selectionsAccordion.on('shown.bs.collapse', function(e) {
            const $target = jQuery(e.target);
            const title = $target.data('title');
            let sId = $target.data('selectionid');
            if (sId) {
                sId = parseInt(sId, 10);
            }
            me.props.onSelectSelection(title, sId);
            jQuery(e.target).parent().addClass('active');
        });

        $selectionsAccordion.on('show.bs.collapse', function(e) {
            const selectionId = parseInt(
                jQuery(e.target).data('selectionid'), 10);
            const selection = find(me.props.filteredSelections, function(s) {
                return s.id === selectionId;
            });
            me.props.onViewSelection(e, selection);
        });

        $selectionsAccordion.on('hidden.bs.collapse', function(e) {
            if (me.isCollapsed()) {
                me.props.onSelectSelection(null);
                jQuery(e.target).parent().removeClass('active');
            }
        });
    }

    componentDidUpdate(prevProps, prevState) {
        if (
            prevState.isEditing !== this.state.isEditing &&
                !this.state.isEditing
        ) {
            // When coming out of the isEditing state, re-register the
            // accordion event listeners.
            this.registerAccordionEvents();
        }
    }

    componentDidMount() {
        this.registerAccordionEvents();
    }
}

ViewSelections.propTypes = {
    type: PropTypes.string.isRequired,
    tags: PropTypes.array,
    terms: PropTypes.array,
    filteredSelections: PropTypes.array,
    onSelectSelection: PropTypes.func.isRequired,
    onViewSelection: PropTypes.func.isRequired,
    onPlaySelection: PropTypes.func.isRequired,
    onSaveSelection: PropTypes.func.isRequired,
    onDeleteSelection: PropTypes.func.isRequired,
    onShowValidationError: PropTypes.func.isRequired,
    hideDeleteDialog: PropTypes.func.isRequired,
    showDeleteDialog: PropTypes.func.isRequired,
    showDeleteDialogBool: PropTypes.bool.isRequired
};
