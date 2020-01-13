import React from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';

export default class AssetFilter extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedOwner: 'all'
        };

        this.handleOwnerChange = this.handleOwnerChange.bind(this);
        this.handleTitleSearch = this.handleTitleSearch.bind(this);
    }
    handleTitleSearch(e) {
        if (e.key === 'Enter') {
            this.props.handleTitleFilterSearch();
        }
    }
    handleOwnerChange(e) {
        this.setState({selectedOwner: e.value});
    }
    render() {
        const { selectedOwner } = this.state;

        let ownersOptions = [];
        if (this.props.assets) {
            this.props.assets.forEach(function(asset) {
                const usernames = ownersOptions.map(x => x.value);
                if (!usernames.includes(asset.author.username)) {
                    ownersOptions.push({
                        label: asset.author.public_name,
                        value: asset.author.username
                    });
                }
            });

            ownersOptions.sort(function(a, b) {
                if (a.value < b.value) return -1;
                if (a.value > b.value) return 1;
                return 0;
            });
        }
        ownersOptions.unshift({
            value: 'all',
            label: 'All Class Members'
        });

        let tagsOptions = [];
        if (this.props.tags) {
            this.props.tags.forEach(function(tag) {
                tagsOptions.push({
                    value: tag.name,
                    label: `${tag.name} (${tag.count})`
                });
            });
        }


        const termGroupLabel = function(data) {
            return (
                <div>
                    <span>{data.label}</span>
                </div>
            );
        };

        let termsOptions = [];
        if (this.props.terms) {
            this.props.terms.forEach(function(term) {
                let termOptions = [];
                term.term_set.forEach(function(t) {
                    termOptions.push({
                        label: `${t.display_name} ${t.count}`,
                        value: t.name
                    });
                });

                termsOptions.push({
                    value: term.name,
                    label: term.name,
                    options: termOptions
                });
            });
        }

        return (
            <div className="container mb-3">
                <div className="row">
                    <div className="col-md-4">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">
                                    <svg
                                        className="bi bi-search"
                                        width="1em" height="1em"
                                        viewBox="0 0 20 20" fill="currentColor"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path
                                            fillRule="evenodd"
                                            d={'M12.442 12.442a1 1 0 ' +
                                               '011.415 0l3.85 3.85a1 1 ' +
                                               '0 01-1.414 ' +
                                               '1.415l-3.85-3.85a1 1 0 ' +
                                               '010-1.415z'}
                                            clipRule="evenodd" />
                                        <path
                                            fillRule="evenodd"
                                            d={'M8.5 14a5.5 5.5 0 100-11 ' +
                                               '5.5 5.5 0 000 11zM15 ' +
                                               '8.5a6.5 6.5 0 11-13 0 ' +
                                               '6.5 6.5 0 0113 0z'}
                                            clipRule="evenodd" />
                                    </svg>
                                </span>
                            </div>
                            <input
                                type="text" name="title"
                                className="form-control"
                                placeholder="Title of items and selections"
                                onChange={this.props.handleTitleFilterChange}
                                onKeyDown={this.handleTitleSearch}
                                aria-label="Title" />
                            <div className="input-group-append">
                                <button
                                    className="btn btn-outline-secondary"
                                    onClick={this.props.handleTitleFilterSearch}
                                    type="button" id="button-addon2">
                                    Go
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">Owner</span>
                            </div>
                            <Select
                                className="react-select"
                                onChange={this.handleOwnerChange}
                                defaultValue={selectedOwner}
                                options={ownersOptions} />
                        </div>

                    </div>

                    <div className="col-md-4">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">Tags</span>
                            </div>
                            <Select
                                className="react-select"
                                isMulti
                                options={tagsOptions} />
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">
                                    Terms
                                </span>
                            </div>
                            <Select
                                className="react-select"
                                isMulti
                                formatGroupLabel={termGroupLabel}
                                options={termsOptions} />
                        </div>
                    </div>

                    <div className="col">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">Date</span>
                            </div>
                            <Select
                                className="react-select"
                                options={[
                                    { value: 'all', label: 'All' },
                                    { value: 'today', label: 'Today' },
                                    { value: 'yesterday', label: 'Yesterday' },
                                    {
                                        value: 'within-last-week',
                                        label: 'Within the last week'
                                    }
                                ]} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

AssetFilter.propTypes = {
    handleTitleFilterChange: PropTypes.func.isRequired,
    handleTitleFilterSearch: PropTypes.func.isRequired,
    assets: PropTypes.array,
    tags: PropTypes.array,
    terms: PropTypes.array
};
