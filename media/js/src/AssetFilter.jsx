import React from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';
import {getAssets} from './utils';

export default class AssetFilter extends React.Component {
    constructor(props) {
        super(props);
        this.filters = {
            owner: 'all',
            title: null,
            tags: [],
            terms: [],
            date: 'all'
        };

        this.handleOwnerChange = this.handleOwnerChange.bind(this);
        this.handleTagsChange = this.handleTagsChange.bind(this);
        this.handleTermsChange = this.handleTermsChange.bind(this);
        this.handleTitleChange = this.handleTitleChange.bind(this);
        this.handleTitleSearch = this.handleTitleSearch.bind(this);
        this.handleTitleFilterSearch = this.handleTitleFilterSearch.bind(this);
        this.handleDateChange = this.handleDateChange.bind(this);

        this.allOption = {
            value: 'all',
            label: 'All Class Members'
        };
    }
    handleTagsChange(e) {
        this.filters.tags = e;
        this.filterAssets(this.filters);
    }
    handleTermsChange(e) {
        this.filters.terms = e;
        this.filterAssets(this.filters);
    }
    handleTitleSearch(e) {
        if (e.key === 'Enter') {
            this.handleTitleFilterSearch();
        }
    }
    handleTitleFilterSearch() {
        this.filterAssets(this.filters);
    }
    handleTitleChange(e) {
        const query = e.target.value.trim().toLowerCase();
        this.filters.title = query;
    }
    handleOwnerChange(e) {
        this.filters.owner = e.value;
        this.filterAssets(this.filters);
    }
    handleDateChange(e) {
        this.filters.date = e.value;
        this.filterAssets(this.filters);
    }
    /**
     * Filter this.props.assets into this.state.filteredAssets, based
     * on the current state of this component's search filters.
     */
    filterAssets(filters) {
        const me = this;
        console.log(filters);
        getAssets(
            filters.title, filters.owner, filters.tags,
            filters.terms, filters.date
        ).then(function(d) {
            me.props.onUpdateAssets(d.assets);
        }, function(e) {
            console.error('asset get error!', e);
        });
    }
    componentDidUpdate(prevProps) {
        if (prevProps.assets !== this.props.assets) {
            this.setState({filteredAssets: this.props.assets});
        }
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
                                onChange={this.handleTitleChange}
                                onKeyDown={this.handleTitleSearch}
                                aria-label="Title" />
                            <div className="input-group-append">
                                <button
                                    className="btn btn-outline-secondary"
                                    onClick={this.handleTitleFilterSearch}
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
                                onChange={this.handleTagsChange}
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
                                onChange={this.handleTermsChange}
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
                                onChange={this.handleDateChange}
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
    assets: PropTypes.array,
    onUpdateAssets: PropTypes.func.isRequired,
    tags: PropTypes.array,
    terms: PropTypes.array
};
