import PropTypes from 'prop-types';
import SelectionForm from '../forms/SelectionForm';

export default class CreateSelection extends SelectionForm {
    constructor(props) {
        super(props);

        this.onCreateSelection = this.onCreateSelection.bind(this);
    }

    onSubmitForm(e) {
        return this.onCreateSelection(e);
    }

    onCreateSelection(e) {
        // Get the tags and terms values from the react-select
        // components.
        const rawTags = this.tagsRef.current.state.selectValue;

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
            const rawTerms = this.termsRef.current.state.selectValue;

            terms = [];
            if (rawTerms) {
                rawTerms.forEach(function(term) {
                    if (term && term.data) {
                        terms.push(term.data.id);
                    }
                });
            }
        }

        return this.props.onCreateSelection(e, tags, terms);
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
