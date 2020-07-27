/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Creatable from 'react-select/creatable';
import Select from 'react-select';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

import {tagsToReactSelect, termsToReactSelect} from '../utils';
import {hasSelection} from '../openlayersUtils';

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

const noSelectionError =
      'Please select a portion of the media using the selections tools.';

export default class CreateSelection extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            validated: false
        };

        this.tagsRef = React.createRef();
        this.termsRef = React.createRef();
        this.titleFieldRef = React.createRef();

        this.onCreateSelection = this.onCreateSelection.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit(e) {
        // Before checking the HTML5 form's validity, do a custom
        // validation check to make sure the user has made a
        // selection.
        if (
            (
                this.props.type === 'image' &&
                    !hasSelection(this.props.selectionSource)
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
            return this.onCreateSelection(e);
        }

        return this.setState({validated: true});
    }

    onCreateSelection(e) {
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

        return this.props.onCreateSelection(e, tags, terms);
    }

    render() {
        const tagsOptions = tagsToReactSelect(this.props.tags);
        const termsOptions = termsToReactSelect(this.props.terms);

        return (
            <React.Fragment>
                <h3>2. Add Details</h3>

                <div className="card w-100">
                    <div className="card-body">
                        <Form
                            noValidate
                            validated={this.state.validated}
                            onSubmit={this.handleSubmit}>
                            <Form.Group controlId="newSelectionTitle">
                                <Form.Label>
                                    Title
                                </Form.Label>
                                <Form.Control
                                    required type="text"
                                    ref={this.titleFieldRef} />
                            </Form.Group>

                            <div className="form-group">
                                <label htmlFor="newSelectionTags">Tags</label>
                                <Creatable
                                    id="newSelectionTags"
                                    ref={this.tagsRef}
                                    menuPortalTarget={document.body}
                                    styles={reactSelectStyles}
                                    className="react-select form-control"
                                    onChange={this.handleTagsChange}
                                    isMulti
                                    options={tagsOptions} />
                            </div>

                            <div className="form-group">
                                <label htmlFor="newSelectionTerms">Terms</label>
                                <Select
                                    id="newSelectionTerms"
                                    ref={this.termsRef}
                                    menuPortalTarget={document.body}
                                    styles={reactSelectStyles}
                                    className="react-select form-control"
                                    onChange={this.handleTermsChange}
                                    isMulti
                                    options={termsOptions} />
                            </div>

                            <Form.Group>
                                <label
                                    htmlFor="newSelectionNotes">
                                    Notes
                                </label>
                                <textarea
                                    className="form-control"
                                    id="newSelectionNotes"
                                    rows="3">
                                </textarea>
                            </Form.Group>

                            <Form.Group>
                                <Button type="submit" size="sm">Save</Button>
                            </Form.Group>
                        </Form>
                    </div>
                </div>
            </React.Fragment>
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

CreateSelection.propTypes = {
    type: PropTypes.string.isRequired,
    tags: PropTypes.array,
    terms: PropTypes.array,
    selectionSource: PropTypes.object,
    selectionStartTime: PropTypes.number,
    selectionEndTime: PropTypes.number,
    onStartTimeClick: PropTypes.func.isRequired,
    onEndTimeClick: PropTypes.func.isRequired,
    onCreateSelection: PropTypes.func.isRequired,
    onShowValidationError: PropTypes.func.isRequired
};
