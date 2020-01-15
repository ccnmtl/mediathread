import React from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';

export default class AssetFilter extends React.Component {
    constructor(props) {
        super(props);

        this.handleOwnerChange = this.handleOwnerChange.bind(this);
        this.handleTitleSearch = this.handleTitleSearch.bind(this);

        this.allOption = {
            value: 'all',
            label: 'All Class Members'
        };
    }
    handleTitleSearch(e) {
        if (e.key === 'Enter') {
            this.props.handleTitleFilterSearch();
        }
    }
    handleOwnerChange(e) {
    }
    render() {
        let ownersOptions = [this.allOption];
        if (this.props.assets) {
            ownersOptions = this.props.assets.reduce(function(a, asset) {
                // If a already contains this user, skip it.
                if (a.find(e => e.value === asset.author.username)) {
                    return a;
                }

                // Insert this owner at the right position in a.
                // Skip the first element ('all'), because this should
                // always be at the top.
                for (let i = 0; i < a.length; i++) {
                    const newEl = {
                        label: asset.author.public_name,
                        value: asset.author.username
                    };
                    if (
                        a.length === 1 ||
                            asset.author.username < a[i].value
                    ) {
                        a.splice(Math.max(i, 1), 0, newEl);
                        break;
                    } else if (i === (a.length - 1)) {
                        // If this is reached, newEl belongs at
                        // the end of the array.
                        a.push(newEl);
                        break;
                    }
                }

                return a;
            }, ownersOptions);
        }

        let tagsOptions = [];
        if (this.props.tags) {
            tagsOptions = this.props.tags.map(function(tag) {
                return {
                    value: tag.name,
                    label: `${tag.name} (${tag.count})`
                };
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
            termsOptions = this.props.terms.map(function(term) {
                let termOptions = [];
                term.term_set.forEach(function(t) {
                    termOptions.push({
                        label: `${t.display_name} (${t.count})`,
                        value: t.name
                    });
                });

                return {
                    value: term.name,
                    label: term.name,
                    options: termOptions
                };
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
                                defaultValue={this.allOption}
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
                                defaultValue={{
                                    value: 'all', label: 'All'
                                }}
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
