/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import Alert from 'react-bootstrap/Alert';
import Creatable from 'react-select/creatable';
import Select from 'react-select';

export default class CreateSelection extends React.Component {
    constructor(props) {
        super(props);

        this.tagsRef = React.createRef();
        this.termsRef = React.createRef();
        this.onCreateSelection = this.onCreateSelection.bind(this);
    }
    onCreateSelection(e) {
        // Get the tags and terms values from the react-select
        // components.
        const rawTags = this.tagsRef.current.state.value;
        const rawTerms = this.termsRef.current.state.value;

        // Tags are handled as a space-separated CharField, while
        // Terms are handled with primary keys.
        let tags = '';
        rawTags.forEach(function(tag) {
            tags += tag.value + ' ';
        });

        if (tags.length) {
            tags = tags.slice(0, -1);
        }

        const terms = [];
        rawTerms.forEach(function(term) {
            if (term && term.data) {
                terms.push(term.data.id);
            }
        });


        return this.props.onCreateSelection(e, tags, terms);
    }
    render() {
        let tagsOptions = [];
        if (this.props.tags) {
            tagsOptions = this.props.tags.map(function(tag) {
                return {
                    value: tag.name,
                    label: `${tag.name} (${tag.count})`
                };
            });
        }

        let termsOptions = [];
        if (this.props.terms) {
            termsOptions = this.props.terms.map(function(term) {
                let termOptions = [];
                term.term_set.forEach(function(t) {
                    const data = t;
                    data.vocab_id = term.id;

                    termOptions.push({
                        label: `${t.display_name} (${t.count})`,
                        value: t.name,
                        data: data
                    });
                });

                return {
                    value: term.name,
                    label: term.name,
                    options: termOptions
                };
            });
        }

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

        return (
            <React.Fragment>
                <h3>Additional Selection Information</h3>

                <Alert
                    variant="danger" show={this.props.showCreateError}
                    id="create-error-alert">
                    <Alert.Heading>Error creating selection.</Alert.Heading>
                    <p>
                        {this.props.createError}
                    </p>
                </Alert>

                <div className="card w-100">
                    <div
                        id="collapseZero"
                        className="collapse show"
                        aria-labelledby="headingZero"
                        data-parent="#selectionAccordion">
                        <div className="card-body">
                            <form>
                                <div className="form-group">
                                    <label htmlFor="newSelectionTitle">
                                        Title
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="newSelectionTitle" />
                                </div>

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

                                <div>
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
            </React.Fragment>
        );
    }
}

CreateSelection.propTypes = {
    asset: PropTypes.object,
    tags: PropTypes.array,
    terms: PropTypes.array,
    selectionStartTime: PropTypes.number,
    selectionEndTime: PropTypes.number,
    onStartTimeUpdate: PropTypes.func.isRequired,
    onEndTimeUpdate: PropTypes.func.isRequired,
    onStartTimeClick: PropTypes.func.isRequired,
    onEndTimeClick: PropTypes.func.isRequired,
    onCreateSelection: PropTypes.func.isRequired,
    showCreateError: PropTypes.bool.isRequired,
    createError: PropTypes.string
};
