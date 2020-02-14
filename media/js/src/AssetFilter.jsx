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

        this.allOption = {
            value: 'all',
            label: 'All Class Members'
        };
    }
    nextPage() {
        const me = this;
        this.setState({
            currentPage: Math.min(
                this.state.currentPage + 1, this.pageCount - 1)
        }, function() {
            me.filterAssets(me.filters);
        });
    }
    prevPage() {
        const me = this;
        this.setState({
            currentPage: Math.max(this.state.currentPage - 1, 0)
        }, function() {
            me.filterAssets(me.filters);
        });
    }
    onPageClick(page) {
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

        const pagination = (
            <nav aria-label="Page navigation example">
                <ul className="pagination mt-2">
                    <li className={
                        'page-item ' +
                            (this.state.currentPage <= 0 ? 'disabled' : '')
                    }>
                        <a
                            className="page-link" href="#"
                            onClick={this.prevPage}
                            aria-label="Previous">
                            <span aria-hidden="true">&laquo;</span>
                        </a>
                    </li>
                    {pages}
                    <li className={
                        'page-item ' + (
                            this.state.currentPage >= this.pageCount - 1 ?
                                'disabled' : ''
                        )
                    }>
                        <a
                            className="page-link" href="#"
                            onClick={this.nextPage}
                            aria-label="Next">
                            <span aria-hidden="true">&raquo;</span>
                        </a>
                    </li>
                </ul>
            </nav>
        );

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
                                        value: 'lastweek',
                                        label: 'Within the last week'
                                    }
                                ]} />
                        </div>
                    </div>
                </div>
                {pagination}
            </div>
        );
    }
}

AssetFilter.propTypes = {
    assets: PropTypes.array,
    assetCount: PropTypes.number,
    onUpdateAssets: PropTypes.func.isRequired,
    owners: PropTypes.array,
    tags: PropTypes.array,
    terms: PropTypes.array
};
