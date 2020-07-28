import React from 'react';
import PropTypes from 'prop-types';

import Creatable from 'react-select/creatable';
import Select from 'react-select';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

import {
    tagsToReactSelect, termsToReactSelect, termsToReactSelectValues
} from '../utils';

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
    })
};

export default class EditSelectionForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            validated: false,

            title: this.props.selection.title,
            tags: this.props.selection.tags,
            terms: this.props.selection.terms,
            notes: this.props.selection.body
        };

        this.tagsRef = React.createRef();
        this.termsRef = React.createRef();
        this.titleFieldRef = React.createRef();

        this.handleTitleChange = this.handleTitleChange.bind(this);
        this.onSaveSelection = this.onSaveSelection.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit(e) {
        const form = e.currentTarget;
        if (form.checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
        } else {
            return this.onSaveSelection(e);
        }

        return this.setState({validated: true});
    }

    handleTitleChange(e) {
        if (!e) {
            return;
        }

        this.setState({title: e.target.value});
    }

    onSaveSelection(e) {
        // Get the tags and terms values from the react-select
        // components.
        const rawTags = this.tagsRef.current.state.value;
        const rawTerms = this.termsRef.current.state.value;

        // Tags are handled as a space-separated CharField, while
        // Terms are handled with primary keys.
        let tags = '';
        if (rawTags) {
            rawTags.forEach(function(tag) {
                tags += tag.value + ' ';
            });
        }

        if (tags.length) {
            tags = tags.slice(0, -1);
        }

        const terms = [];
        if (rawTerms) {
            rawTerms.forEach(function(term) {
                if (term && term.data) {
                    terms.push(term.data.id);
                }
            });
        }

        return this.props.onSaveSelection(
            e, this.props.selection.id, tags, terms);
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

        return (
            <Form
                noValidate
                validated={this.state.validated}
                onSubmit={this.handleSubmit}>
                <Form.Group controlId="newSelectionTitle">
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

                <Form.Group>
                    <label htmlFor="newSelectionTags">Tags</label>
                    <Creatable
                        id="newSelectionTags"
                        ref={this.tagsRef}
                        menuPortalTarget={document.body}
                        styles={reactSelectStyles}
                        className="react-select form-control"
                        onChange={this.handleTagsChange}
                        isMulti
                        defaultValue={selectedTags}
                        options={tagsOptions} />
                </Form.Group>

                <Form.Group>
                    <label htmlFor="newSelectionTerms">Terms</label>
                    <Select
                        id="newSelectionTerms"
                        ref={this.termsRef}
                        menuPortalTarget={document.body}
                        styles={reactSelectStyles}
                        className="react-select form-control"
                        onChange={this.handleTermsChange}
                        isMulti
                        defaultValue={selectedTerms}
                        options={termsOptions} />
                </Form.Group>

                <Form.Group>
                    <label
                        htmlFor="newSelectionNotes">
                        Notes
                    </label>
                    <textarea
                        className="form-control"
                        id="newSelectionNotes"
                        defaultValue={this.props.selection.metadata.body}
                        rows="3"
                    >
                    </textarea>
                </Form.Group>

                <Button
                    variant="danger" size="sm"
                    onClick={() => this.props.onClickDelete(
                        this.props.selection.id)}>
                    Delete
                </Button>

                <div className="float-right">
                    <Button
                        variant="secondary" size="sm"
                        onClick={this.props.onClickCancel}>
                        Cancel
                    </Button>&nbsp;
                    <Button type="submit" size="sm">
                        Save
                    </Button>
                </div>
            </Form>
        );
    }

    componentDidMount() {
        const me = this;

        const titleField = this.titleFieldRef.current;
        titleField.addEventListener('invalid', function(e) {
            me.props.onShowValidationError(
                'Please specify a selection title.');
        });
    }
}

EditSelectionForm.propTypes = {
    type: PropTypes.string.isRequired,
    selection: PropTypes.object.isRequired,
    tags: PropTypes.array,
    terms: PropTypes.array,
    onClickCancel: PropTypes.func.isRequired,
    onSaveSelection: PropTypes.func.isRequired,
    onClickDelete: PropTypes.func.isRequired,
    onShowValidationError: PropTypes.func.isRequired
};
