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
            validated: false
        };
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

        return this.props.onSaveSelection(e, tags, terms);
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
                validated={this.state.validated}
                onSubmit={this.handleSubmit}>
                <Form.Group controlId="newSelectionTitle">
                    <Form.Label>
                        Title
                    </Form.Label>
                    <Form.Control
                        required
                        type="text"
                        value={this.props.selection.title}
                        onChange={function() {}}
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
                        rows="3">
                        {this.props.selection.body}
                    </textarea>
                </Form.Group>

                <Button
                    variant="secondary" size="sm"
                    onClick={this.props.onClickCancel}>
                    Cancel
                </Button>&nbsp;
                <Button type="submit" size="sm">
                    Save
                </Button>
            </Form>
        );
    }
}

EditSelectionForm.propTypes = {
    selection: PropTypes.object,
    tags: PropTypes.array,
    terms: PropTypes.array,
    onClickCancel: PropTypes.func.isRequired,
    onSaveSelection: PropTypes.func.isRequired
};
