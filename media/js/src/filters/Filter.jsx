/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';
import {tagsToReactSelect, termsToReactSelect, getFilters} from '../utils';

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
    })
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
 * General search filter components with title, owner, tags, etc.
 *
 * This class can be used to filter assets or selections by extending
 * it.
 */
export default class Filter extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currentPage: 0,
            pageCount: 1
        };

        this.offset = 20;

        this.handleOwnerChange = this.handleOwnerChange.bind(this);
        this.handleTagsChange = this.handleTagsChange.bind(this);
        this.handleTermsChange = this.handleTermsChange.bind(this);
        this.handleTitleChange = this.handleTitleChange.bind(this);
        this.handleTitleSearch = this.handleTitleSearch.bind(this);
        this.handleTitleFilterSearch = this.handleTitleFilterSearch.bind(this);
        this.handleDateChange = this.handleDateChange.bind(this);
    }

    setPageAndUpdateAssets(pageNumber) {
        this.props.onUpdateItems(null);

        const me = this;
        this.setState({
            currentPage: pageNumber
        }, function() {
            me.filterItems(getFilters(me.props));
        });
    }
    onPageClick(page) {
        this.props.onUpdateItems(null);

        const me = this;
        this.setState({
            currentPage: page
        }, function() {
            me.filterItems(getFilters(me.props));
        });
    }
    handleTagsChange(e) {
        this.setState({currentPage: 0});
        this.props.onUpdateFilter({tags: e});
    }
    handleTermsChange(e) {
        this.setState({currentPage: 0});
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
        const query = e.target.value.trim().toLowerCase();
        this.setState({currentPage: 0});
        this.props.onUpdateFilter({title: query});
    }
    handleOwnerChange(e) {
        let newOwner = e.value;
        if (newOwner === 'me') {
            newOwner = window.MediaThread.current_username;
        }

        this.setState({currentPage: 0});
        this.props.onUpdateFilter({owner: newOwner});
    }
    handleDateChange(e) {
        this.setState({date: e.value});
        this.props.onUpdateFilter({date: e.value});
    }

    /**
     * Filter this.props.items into this.state.filteredItems, based
     * on the current state of this component's search filters.
     *
     * This must be implemented in the subclass.
     */
    filterItems(filters) {
    }

    componentDidUpdate(prevProps) {
        if (prevProps.items !== this.props.items) {
            this.setState({filteredItems: this.props.items});
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
                <div>
                    <span>{data.label}</span>
                </div>
            );
        };

        const pages = [];
        for (let i = 0; i < this.state.pageCount; i++) {
            const disabled = this.state.currentPage === i ? 'disabled' : '';
            pages.push(
                <li key={i} className={`page-item ${disabled}`}>
                    <a
                        className="page-link" href="#"
                        onClick={this.onPageClick.bind(this, i)}>
                        {i + 1}
                    </a>
                </li>
            );
        }

        let pagination = null;
        if (!this.props.hidePagination) {
            pagination = (
                <div id="view-pagination" className="row">
                    <div className="col-md-6">
                        <div
                            id="view-toggle" className="btn-group"
                            role="group" aria-label="View Toggle">
                            <button
                                type="button"
                                data-testid="viewtoggle-grid"
                                onClick={() => this.props.setViewMode('grid')}
                                className={'btn btn-outline-primary btn-sm ' + (
                                    this.props.viewMode === 'grid' ? 'active' : ''
                                )}>
                                Grid
                            </button>
                            <button
                                type="button"
                                data-testid="viewtoggle-list"
                                onClick={() => this.props.setViewMode('list')}
                                className={'btn btn-outline-primary btn-sm ' + (
                                    this.props.viewMode === 'list' ? 'active' : ''
                                )}>
                                List
                            </button>
                        </div>
                    </div>
                    <div className="col-md-6">
                        <ul
                            className="pagination nav justify-content-end btn-sm"
                            style={{padding: 0}}>
                            <li className={'page-item ' + (
                                this.state.currentPage <= 0 ? 'disabled' : ''
                            )}>
                                <a
                                    className="page-link" href="#"
                                    aria-label="First"
                                    onClick={this.firstPage}>
                                    First
                                </a>
                            </li>
                            <li className={'page-item ' + (
                                this.state.currentPage <= 0 ? 'disabled' : ''
                            )}>
                                <a
                                    className="page-link" href="#"
                                    aria-label="Previous"
                                    onClick={this.prevPage}>
                                    Previous
                                </a>
                            </li>
                            <li className="page-item active">
                                <div className="page-link">
                                    {this.state.currentPage + 1} of {
                                        Math.max(this.state.pageCount, 1)}
                                    <span className="sr-only">(current)</span>
                                </div>
                            </li>
                            <li className={'page-item ' + (
                                this.state.currentPage >= this.state.pageCount - 1 ?
                                    'disabled' : ''
                            )}>
                                <a
                                    className="page-link" href="#"
                                    aria-label="Next"
                                    onClick={this.nextPage}>
                                    Next
                                </a>
                            </li>
                            <li className={'page-item ' + (
                                this.state.currentPage >= this.state.pageCount - 1 ?
                                    'disabled' : ''
                            )}>
                                <a
                                    className="page-link" href="#"
                                    aria-label="Last"
                                    onClick={this.lastPage}>
                                    Last
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
            );
        }

        return (
            <React.Fragment>
                <form id="search-well">
                    <div className="form-row">
                        <div className="form-group col-md-4">
                            <label htmlFor="filter-search">Title</label>
                            <div className="input-group mb-3">
                                <input
                                    id="filter-search"
                                    type="text"
                                    className="form-control form-control-sm"
                                    placeholder="Search for..."
                                    onChange={this.handleTitleChange}
                                    onKeyDown={this.handleTitleSearch}
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
                            <label htmlFor="owner-filter">Owner</label>
                            <Select
                                id="owner-filter"
                                menuPortalTarget={document.body}
                                styles={reactSelectStyles}
                                menuContainerStyle={{ zIndex: 5 }}
                                className={
                                    'react-select form-control form-control-sm'
                                }
                                onChange={this.handleOwnerChange}
                                defaultValue={meOption}
                                options={this.getOwnersOptions()} />
                        </div>
                        <div className="form-group col-md-2">
                            <label htmlFor="tag-filter">Tag</label>
                            <Select
                                id="tag-filter"
                                menuPortalTarget={document.body}
                                styles={reactSelectStyles}
                                className={
                                    'react-select form-control form-control-sm'
                                }
                                onChange={this.handleTagsChange}
                                isMulti
                                options={tagsOptions} />
                        </div>
                        <div className="form-group col-md-2">
                            <label htmlFor="term-filter">Term</label>
                            <Select
                                id="term-filter"
                                menuPortalTarget={document.body}
                                styles={reactSelectStyles}
                                className={
                                    'react-select form-control form-control-sm'
                                }
                                onChange={this.handleTermsChange}
                                isMulti
                                formatGroupLabel={termGroupLabel}
                                options={termsOptions} />
                        </div>
                        <div className="form-group col-md-2">
                            <label htmlFor="filter-date">Date</label>
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
                    </div>
                </form>
                {pagination}
            </React.Fragment>
        );
    }
}

Filter.propTypes = {
    items: PropTypes.array,
    itemCount: PropTypes.number,
    hidePagination: PropTypes.bool.isRequired,
    owners: PropTypes.array,
    allTags: PropTypes.array,
    allTerms: PropTypes.array,
    viewMode: PropTypes.string.isRequired,
    onUpdateItems: PropTypes.func.isRequired,
    setViewMode: PropTypes.func.isRequired,
    onUpdateFilter: PropTypes.func.isRequired,

    // Filter vals
    owner: PropTypes.string,
    title: PropTypes.string,
    tags: PropTypes.array,
    terms: PropTypes.array,
    date: PropTypes.string
};
