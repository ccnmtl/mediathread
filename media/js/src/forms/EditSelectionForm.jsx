import PropTypes from 'prop-types';

import SelectionForm from './SelectionForm';

export default class EditSelectionForm extends SelectionForm {
    constructor(props) {
        super(props);

        this.onSaveSelection = this.onSaveSelection.bind(this);
    }

    onSubmitForm(e) {
        return this.onSaveSelection(e);
    }

    onSaveSelection(e) {
        // Get the tags and terms values from the react-select
        // components.
        const rawTags = this.tagsRef.current.state.value;

        // Tags are handled as a comma-separated CharField, while
        // Terms are handled with primary keys.
        let tags = '';
        if (rawTags) {
            rawTags.forEach(function(tag) {
                tags += tag.value + ',';
            });
        }

        let terms = null;
        if (this.termsRef && this.termsRef.current) {
            const rawTerms = this.termsRef.current.state.value;

            terms = [];
            if (rawTerms) {
                rawTerms.forEach(function(term) {
                    if (term && term.data) {
                        terms.push(term.data.id);
                    }
                });
            }
        }

        return this.props.onSaveSelection(
            e, this.props.selection.id, tags, terms);
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
