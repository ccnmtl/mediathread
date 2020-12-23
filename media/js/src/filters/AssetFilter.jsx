/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';
import capitalize from 'lodash/capitalize';
import find from 'lodash/find';
import {
    ASSETS_PER_PAGE,
    tagsToReactSelect, termsToReactSelect, getFilters,
    getAssets
} from '../utils';

// Make the react-select inputs look like Bootstrap's
// form-control-sm.
//
// https://react-select.com/styles#style-object
//
const reactSelectStyles = {
    container: (provided, state) => ({
        ...provided,
        padding: 0,
        height: 'fit-content',
        zIndex: 5
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
    }),
    menuPortal: (provided, state) => ({
        ...provided,
        zIndex: 4
    }),
    indicatorsContainer: (provided, state) => ({
        ...provided,
        height: '29px'
    }),
    input: (provided, state) => ({
        ...provided,
        height: '21px'
    }),
    option: (provided, state) => ({
        ...provided,
        paddingLeft: '20px'
    })
};

const getDateValue = function(date) {
    if (date === 'lastweek') {
        return {
            value: date,
            label: 'Within the last week'
        };
    }

    return {
        value: date,
        label: capitalize(date)
    };
};

const meOption = {
    value: 'me',
    label: 'Me'
};

const allOption = {
    value: 'all',
    label: 'All Class Members'
};

/**
 * Given an owner string and an array of owner objects, return the
 * appropriate owner object.
 */
const getOwnerValue = function(str, owners) {
    if (window.MediaThread && str === window.MediaThread.current_username) {
        return meOption;
    } else if (str === 'all') {
        return allOption;
    }

    const owner = find(owners, function(o) {
        return o.username === str;
    });

    if (owner) {
        return {
            value: owner.username,
            label: owner.public_name
        };
    }

    return null;
};

/**
 * General search filter components with title, owner, tags, etc.
 *
 * This class can be used to filter assets or selections by extending
 * it.
 */
export default class AssetFilter extends React.Component {
    constructor(props) {
        super(props);

        this.handleOwnerChange = this.handleOwnerChange.bind(this);
        this.handleTagsChange = this.handleTagsChange.bind(this);
        this.handleTermsChange = this.handleTermsChange.bind(this);
        this.handleTitleChange = this.handleTitleChange.bind(this);
        this.handleTitleSearch = this.handleTitleSearch.bind(this);
        this.handleTitleFilterSearch = this.handleTitleFilterSearch.bind(this);
        this.handleDateChange = this.handleDateChange.bind(this);
    }

    handleTagsChange(e) {
        this.props.onUpdateFilter({tags: e});
    }
    handleTermsChange(e) {
        this.props.onUpdateFilter({terms: e});
    }
    handleTitleSearch(e) {
        if (e.key === 'Enter') {
            this.handleTitleFilterSearch();
        }
    }
    handleTitleFilterSearch() {
        this.filterItems(getFilters(this.props));
    }
    handleTitleChange(e) {
        const query = e.target.value.toLowerCase();
        this.props.onUpdateFilter({title: query});
    }
    handleOwnerChange(e) {
        let newOwner = e.value;
        if (newOwner === 'me') {
            newOwner = window.MediaThread.current_username;
        }

        this.props.onUpdateFilter({owner: newOwner});
    }
    handleDateChange(e) {
        this.setState({date: e.value});
        this.props.onUpdateFilter({date: e.value});
    }

    filterItems(filters={}) {
        this.props.onUpdateItems(null);

        const me = this;
        getAssets(
            filters.title, filters.owner, filters.tags,
            filters.terms, filters.date,
            this.props.currentPage * ASSETS_PER_PAGE
        ).then(function(d) {
            me.props.onUpdateItems(
                d.assets,
                d.asset_count,
                d.active_tags,
                d.active_vocabulary
            );
            me.props.updatePageCount(d.asset_count);
        }, function(e) {
            console.error('asset get error!', e);
        });
    }

    componentDidUpdate(prevProps) {
        if (prevProps.items !== this.props.items) {
            this.setState({filteredItems: this.props.items});
        }

        if (
            prevProps.owner !== this.props.owner ||
                prevProps.tags !== this.props.tags ||
                prevProps.terms !== this.props.terms ||
                prevProps.date !== this.props.date
        ) {
            this.filterItems(getFilters(this.props));
        }
    }

    getOwnersOptions() {
        let ownersOptions = [meOption, allOption];

        if (this.props.owners) {
            this.props.owners.forEach(function(owner) {
                if (owner.id === window.MediaThread.current_user) {
                    return false;
                }

                const option = {
                    label: owner.public_name,
                    value: owner.username
                };

                ownersOptions.push(option);
            });
        }

        return ownersOptions;
    }

    render() {
        const tagsOptions = tagsToReactSelect(this.props.allTags);
        const termsOptions = termsToReactSelect(this.props.allTerms);

        const termGroupLabel = function(data) {

            return (
                <div className="font-weight-bold h6">
                    <span>{data.label}</span>
                </div>
            );
        };

        return (
            <React.Fragment>
                <form id="search-well">
                    <div className="form-row">
                        <div className="form-group col-md-3">
                            <label htmlFor="filter-search">Title</label>
                            <div className="input-group mb-3">
                                <input
                                    id="filter-search"
                                    type="text"
                                    className="form-control form-control-sm"
                                    placeholder="Search for..."
                                    onChange={this.handleTitleChange}
                                    onKeyDown={this.handleTitleSearch}
                                    value={this.props.title || ''}
                                />
                                <div className="input-group-append">
                                    <a
                                        href="#"
                                        className="btn btn-secondary btn-sm"
                                        type="button"
                                        onClick={this.handleTitleFilterSearch}>
                                        Search
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div className="form-group col-md-2">
                            <label htmlFor="react-select-2-input">Owner</label>
                            <Select
                                id="owner-filter"
                                menuPortalTarget={document.body}
                                styles={reactSelectStyles}
                                menuContainerStyle={{ zIndex: 5 }}
                                className={
                                    'react-select form-control form-control-sm'
                                }
                                onChange={this.handleOwnerChange}
                                value={getOwnerValue(
                                    this.props.owner, this.props.owners)}
                                options={this.getOwnersOptions()} />
                        </div>
                        <div className="form-group col-md-2">
                            <label htmlFor="react-select-3-input">Tag</label>
                            <Select
                                id="tag-filter"
                                menuPortalTarget={document.body}
                                styles={reactSelectStyles}
                                className={
                                    'react-select form-control form-control-sm'
                                }
                                onChange={this.handleTagsChange}
                                value={this.props.tags}
                                isMulti
                                options={tagsOptions} />
                        </div>

                        {window.MediaThread && window.MediaThread.current_course_has_vocab && (
                            <div className="form-group col-md-2">
                                <label htmlFor="react-select-4-input">Course Vocabulary</label>
                                <Select
                                    id="term-filter"
                                    menuPortalTarget={document.body}
                                    styles={reactSelectStyles}
                                    className={
                                        'react-select form-control form-control-sm'
                                    }
                                    onChange={this.handleTermsChange}
                                    value={this.props.terms}
                                    isMulti
                                    formatGroupLabel={termGroupLabel}
                                    options={termsOptions} />
                            </div>
                        )}

                        <div className="form-group col-md-2">
                            <label htmlFor="react-select-5-input">Date</label>
                            <Select
                                id="filter-date"
                                menuPortalTarget={document.body}
                                styles={reactSelectStyles}
                                className={
                                    'react-select form-control form-control-sm'
                                }
                                onChange={this.handleDateChange}
                                defaultValue={{
                                    value: 'all', label: 'All'
                                }}
                                value={getDateValue(this.props.date)}
                                options={[
                                    { value: 'all', label: 'All' },
                                    { value: 'today', label: 'Today' },
                                    { value: 'yesterday', label: 'Yesterday' },
                                    {
                                        value: 'lastweek',
                                        label: 'Within the last week'
                                    }
                                ]} />
                        </div>
                        <div className="form-group col-md-1">
                            <label htmlFor="react-select-5-input">&nbsp;</label>
                            <div className="input-group mb-3">
                                <a
                                    href="#"
                                    className="btn btn-secondary btn-sm btn-block"
                                    type="button"
                                    onClick={this.props.onClearFilter}>
                                Clear
                                </a>
                            </div>
                        </div>
                    </div>
                </form>
            </React.Fragment>
        );
    }
}

AssetFilter.propTypes = {
    items: PropTypes.array,
    itemCount: PropTypes.number,
    owners: PropTypes.array,
    currentPage: PropTypes.number.isRequired,
    updatePageCount: PropTypes.func.isRequired,
    allTags: PropTypes.array,
    allTerms: PropTypes.array,
    onUpdateItems: PropTypes.func.isRequired,
    onUpdateFilter: PropTypes.func.isRequired,
    onClearFilter: PropTypes.func.isRequired,

    // Filter vals
    owner: PropTypes.string,
    title: PropTypes.string,
    tags: PropTypes.array,
    terms: PropTypes.array,
    date: PropTypes.string
};
