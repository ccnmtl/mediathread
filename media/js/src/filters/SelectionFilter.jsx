import PropTypes from 'prop-types';
import Filter from './Filter';


export default class SelectionFilter extends Filter {
    filterItems(filters) {
        let filteredSelections = [];
        if (this.props.asset) {
            this.props.asset.annotations.forEach(function(s) {
                let passesFilters = true;

                if (filters.title) {
                    if (
                        !s.title.toLowerCase().includes(
                            filters.title.toLowerCase())
                    ) {
                        passesFilters = false;
                    }
                }

                if (filters.owner && filters.owner !== 'all') {
                    if (s.author.username !== filters.owner) {
                        passesFilters = false;
                    }
                }

                if (passesFilters) {
                    filteredSelections.push(s);
                }
            });
        }

        return this.props.onUpdateItems(filteredSelections);
    }
}

SelectionFilter.propTypes = {
    asset: PropTypes.object.isRequired
};
