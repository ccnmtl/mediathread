/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';
import {getAssets} from './utils';

export default class AssetFilter extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currentPage: 0
        };
        this.filters = {
            owner: 'all',
            title: null,
            tags: [],
            terms: [],
            date: 'all'
        };

        this.offset = 20;
        this.updatePageCount();

        this.handleOwnerChange = this.handleOwnerChange.bind(this);
        this.handleTagsChange = this.handleTagsChange.bind(this);
        this.handleTermsChange = this.handleTermsChange.bind(this);
        this.handleTitleChange = this.handleTitleChange.bind(this);
        this.handleTitleSearch = this.handleTitleSearch.bind(this);
        this.handleTitleFilterSearch = this.handleTitleFilterSearch.bind(this);
        this.handleDateChange = this.handleDateChange.bind(this);
        this.nextPage = this.nextPage.bind(this);
        this.prevPage = this.prevPage.bind(this);
        this.lastPage = this.lastPage.bind(this);
        this.firstPage = this.firstPage.bind(this);

        this.allOption = {
            value: 'all',
            label: 'All Class Members'
        };
    }
    setPageAndUpdateAssets(pageNumber) {
        this.props.onUpdateAssets(null);

        const me = this;
        this.setState({
            currentPage: pageNumber
        }, function() {
            me.filterAssets(me.filters);
        });
    }
    lastPage() {
        this.setPageAndUpdateAssets(this.pageCount - 1);
    }
    firstPage() {
        this.setPageAndUpdateAssets(0);
    }
    nextPage() {
        const page = Math.min(this.state.currentPage + 1, this.pageCount - 1);
        this.setPageAndUpdateAssets(page);
    }
    prevPage() {
        const page = Math.max(this.state.currentPage - 1, 0);
        this.setPageAndUpdateAssets(page);
    }
    onPageClick(page) {
        this.props.onUpdateAssets(null);

        const me = this;
        this.setState({
            currentPage: page
        }, function() {
            me.filterAssets(me.filters);
        });
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
        this.props.onUpdateAssets(null);

        const me = this;
        getAssets(
            filters.title, filters.owner, filters.tags,
            filters.terms, filters.date,
            this.state.currentPage * this.offset
        ).then(function(d) {
            me.props.onUpdateAssets(d.assets, d.asset_count);
        }, function(e) {
            console.error('asset get error!', e);
        });
    }
    updatePageCount() {
        this.pageCount = Math.ceil(this.props.assetCount / this.offset);
    }
    componentDidUpdate(prevProps) {
        if (prevProps.assets !== this.props.assets) {
            this.setState({filteredAssets: this.props.assets});
        }
        if (prevProps.assetCount !== this.props.assetCount) {
            this.updatePageCount();
        }
    }
    render() {
        let ownersOptions = [this.allOption];
        if (this.props.owners) {
            this.props.owners.forEach(function(owner) {
                ownersOptions.push({
                    label: owner.public_name,
                    value: owner.username
                });
            });
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

        const pages = [];
        for (let i = 0; i < this.pageCount; i++) {
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
                            <a
                                href="#"
                                data-testid="viewtoggle-grid"
                                onClick={() => this.props.setViewMode('grid')}
                                className={'btn btn-outline-primary btn-sm ' + (
                                    this.props.viewMode === 'grid' ? 'active' : ''
                                )}>
                                Grid
                            </a>
                            <a
                                href="#"
                                data-testid="viewtoggle-list"
                                onClick={() => this.props.setViewMode('list')}
                                className={'btn btn-outline-primary btn-sm ' + (
                                    this.props.viewMode === 'list' ? 'active' : ''
                                )}>
                                List
                            </a>
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
                                        Math.max(this.pageCount, 1)}
                                    <span className="sr-only">(current)</span>
                                </div>
                            </li>
                            <li className={'page-item ' + (
                                this.state.currentPage >= this.pageCount - 1 ?
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
                                this.state.currentPage >= this.pageCount - 1 ?
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
                                    onKeyDown={this.handleTitleSearch} />
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
                                defaultValue={this.allOption}
                                options={ownersOptions} />
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

AssetFilter.propTypes = {
    assets: PropTypes.array,
    assetCount: PropTypes.number,
    hidePagination: PropTypes.bool.isRequired,
    owners: PropTypes.array,
    tags: PropTypes.array,
    terms: PropTypes.array,
    viewMode: PropTypes.string.isRequired,
    onUpdateAssets: PropTypes.func.isRequired,
    setViewMode: PropTypes.func.isRequired
};
