import React from 'react';
import PropTypes from 'prop-types';
import {
    ASSETS_PER_PAGE, getAssets, getFilters
} from './utils';

export default class Pagination extends React.Component {
    constructor(props) {
        super(props);
        this.nextPage = this.nextPage.bind(this);
        this.prevPage = this.prevPage.bind(this);
        this.lastPage = this.lastPage.bind(this);
        this.firstPage = this.firstPage.bind(this);
    }
    setPageAndUpdateAssets(pageNumber) {
        this.props.onUpdateItems(null);
        this.props.updateCurrentPage(pageNumber);

        const filters = getFilters(this.props);
        const me = this;
        getAssets(
            filters.title, filters.owner, filters.tags,
            filters.terms, filters.date,
            pageNumber * ASSETS_PER_PAGE
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
    lastPage() {
        this.setPageAndUpdateAssets(this.props.pageCount - 1);
    }
    firstPage() {
        this.setPageAndUpdateAssets(0);
    }
    nextPage() {
        const page = Math.min(
            this.props.currentPage + 1,
            this.props.pageCount - 1);
        this.setPageAndUpdateAssets(page);
    }
    prevPage() {
        const page = Math.max(this.props.currentPage - 1, 0);
        this.setPageAndUpdateAssets(page);
    }

    render() {
        return (
            <div className="col-md-6">
                <ul
                    className="pagination nav justify-content-end btn-sm"
                    style={{padding: 0}}>
                    <li className={'page-item ' + (
                        this.props.currentPage <= 0 ? 'disabled' : ''
                    )}>
                        <a
                            className="page-link" href="#"
                            aria-label="First"
                            onClick={this.firstPage}>
                            First
                        </a>
                    </li>
                    <li className={'page-item ' + (
                        this.props.currentPage <= 0 ? 'disabled' : ''
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
                            {this.props.currentPage + 1} of {
                                Math.max(this.props.pageCount, 1)}
                            <span className="sr-only">(current)</span>
                        </div>
                    </li>
                    <li className={'page-item ' + (
                        this.props.currentPage >= this.props.pageCount - 1 ?
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
                        this.props.currentPage >= this.props.pageCount - 1 ?
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
        );
    }
}

Pagination.propTypes = {
    currentPage: PropTypes.number.isRequired,
    pageCount: PropTypes.number.isRequired,
    updatePageCount: PropTypes.func.isRequired,
    updateCurrentPage: PropTypes.func.isRequired,
    onUpdateItems: PropTypes.func.isRequired,

    // Filter vals
    owner: PropTypes.string,
    title: PropTypes.string,
    tags: PropTypes.array,
    terms: PropTypes.array,
    date: PropTypes.string
};
