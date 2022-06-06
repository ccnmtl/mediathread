import React from 'react';
import PropTypes from 'prop-types';

import Creatable from 'react-select/creatable';
import Select from 'react-select';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

import {
    tagsToReactSelect, termsToReactSelect, termsToReactSelectValues
} from '../utils';
import {hasSelection} from '../openlayersUtils';

const noSelectionError =
      'Please select a portion of the media using the selections tools.';

const reactSelectStyles = {
    container: (provided, state) => ({
        ...provided,
        padding: 0,
        height: 'fit-content',
    }),
    control: (provided, state) => ({
        ...provided,
        borderWidth: 0,
        minHeight: 'fit-content',
        height: 'fit-content'
    }),
    singleValue: (provided, state) => ({
        ...provided,
        top: '45%'
    }),
    placeholder: (provided, state) => ({
        ...provided,
        top: '45%'
    }),
    option: (provided, state) => ({
        ...provided,
        paddingLeft: '20px'
    })
};

export default class SelectionForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            validated: false,

            title: this.props.selection ? this.props.selection.title : '',
            tags: this.props.selection ? this.props.selection.tags : '',
            terms: this.props.selection ? this.props.selection.terms : '',
            notes: this.props.selection ? this.props.selection.body : ''
        };

        this.tagsRef = React.createRef();
        this.termsRef = React.createRef();
        this.titleFieldRef = React.createRef();

        this.handleTitleChange = this.handleTitleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleTitleChange(e) {
        if (!e) {
            return;
        }

        this.setState({title: e.target.value});
    }

    handleSubmit(e) {
        // Before checking the HTML5 form's validity, do a custom
        // validation check to make sure the user has made a
        // selection.
        if (
            (
                this.props.type === 'image' &&
                    (
                        !hasSelection(this.props.selectionSource) &&
                            !this.props.selection
                    )
            ) || (
                this.props.type === 'video' &&
                    !this.props.selectionStartTime &&
                    !this.props.selectionEndTime
            )
        ) {
            e.preventDefault();
            e.stopPropagation();
            this.props.onShowValidationError(noSelectionError);
            return this.setState({validated: true});
        } else if (
            this.props.type === 'video' &&
                (
                    this.props.selectionStartTime >
                        this.props.selectionEndTime
                )
        ) {
            e.preventDefault();
            e.stopPropagation();
            this.props.onShowValidationError(
                'The start time is greater than the end ' +
                    'time. Please specify a valid time range');
            return this.setState({validated: true});
        }

        const form = e.currentTarget;
        if (form.checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
        } else {
            return this.onSubmitForm(e);
        }

        return this.setState({validated: true});
    }

    render() {
        const tagsOptions = tagsToReactSelect(this.props.tags);
        const termsOptions = termsToReactSelect(this.props.terms);

        let selectedTags = [];
        let selectedTerms = [];
        if (this.props.selection) {
            selectedTags = tagsToReactSelect(
                this.props.selection.metadata.tags, true);
            selectedTerms = termsToReactSelectValues(
                this.props.selection.vocabulary);
        }
        const termGroupLabel = function(data) {

            return (
                <div className="font-weight-bold h6">
                    <span>{data.label}</span>
                </div>
            );
        };

        const hasVocab = this.props.terms && this.props.terms.length > 0;

        return (
            <Form
                noValidate
                validated={this.state.validated}
                onSubmit={this.handleSubmit}>
                <Form.Group className="mb-3" controlId="newSelectionTitle">
                    <Form.Label>
                        Title
                    </Form.Label>
                    <Form.Control
                        required
                        type="text"
                        value={this.state.title}
                        onChange={this.handleTitleChange}
                        ref={this.titleFieldRef}
                    />
                </Form.Group>

                <Form.Group className="mb-3">
                    <label htmlFor="react-select-6-input">Tags</label>
                    <Creatable
                        id="newSelectionTags"
                        ref={this.tagsRef}
                        menuPortalTarget={document.body}
                        styles={reactSelectStyles}
                        className="react-select form-control"
                        onChange={this.handleTagsChange}
                        isMulti
                        defaultValue={selectedTags}
                        noOptionsMessage={({inputValue}) => !inputValue ? "" : "No tags found"}
                        options={tagsOptions} />
                </Form.Group>

                {hasVocab && (
                    <Form.Group className="mb-3">
                        <label htmlFor="react-select-7-input">
                            Course Vocabulary</label>
                        <Select
                            id="newSelectionTerms"
                            ref={this.termsRef}
                            menuPortalTarget={document.body}
                            styles={reactSelectStyles}
                            className="react-select form-control"
                            onChange={this.handleTermsChange}
                            isMulti
                            defaultValue={selectedTerms}
                            formatGroupLabel={termGroupLabel}
                            options={termsOptions} />
                    </Form.Group>
                )}

                <Form.Group className="mb-3">
                    <label
                        htmlFor="newSelectionNotes">
                        Notes
                    </label>
                    <textarea
                        className="form-control"
                        id="newSelectionNotes"
                        defaultValue={
                            this.props.selection ?
                                this.props.selection.metadata.body : ''
                        }
                        rows="3"
                    >
                    </textarea>
                </Form.Group>

                {this.props.onClickDelete && this.props.selection && (
                    <Button
                        variant="danger" size="sm"
                        onClick={() => this.props.onClickDelete(
                            this.props.selection.id)}>
                        Delete
                    </Button>
                )}

                <div className="float-right">
                    {this.props.onClickCancel && (
                        <>
                            <Button
                                variant="secondary" size="sm"
                                onClick={(e) => this.props.onClickCancel(
                                    e, this.props.selection)}>
                                Cancel
                            </Button>&nbsp;
                        </>
                    )}
                    <Button type="submit" size="sm">
                        Save
                    </Button>
                </div>
            </Form>
        );
    }
}

SelectionForm.propTypes = {
    type: PropTypes.string.isRequired,
    selection: PropTypes.object,
    tags: PropTypes.array,
    terms: PropTypes.array,
    selectionSource: PropTypes.object,
    selectionStartTime: PropTypes.number,
    selectionEndTime: PropTypes.number,
    onStartTimeClick: PropTypes.func.isRequired,
    onEndTimeClick: PropTypes.func.isRequired,
    onShowValidationError: PropTypes.func.isRequired,
    onClickCancel: PropTypes.func,
    onClickDelete: PropTypes.func
};
