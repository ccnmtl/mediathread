import Filter from './Filter';
import {getAssets} from '../utils';

export default class AssetFilter extends Filter {
    constructor(props) {
        super(props);
        this.nextPage = this.nextPage.bind(this);
        this.prevPage = this.prevPage.bind(this);
        this.lastPage = this.lastPage.bind(this);
        this.firstPage = this.firstPage.bind(this);
    }
    setPageAndUpdateAssets(pageNumber) {
        this.props.onUpdateItems(null);

        const me = this;
        this.setState({
            currentPage: pageNumber
        }, function() {
            me.filterItems(me.filters);
        });
    }
    lastPage() {
        this.setPageAndUpdateAssets(this.state.pageCount - 1);
    }
    firstPage() {
        this.setPageAndUpdateAssets(0);
    }
    nextPage() {
        const page = Math.min(
            this.state.currentPage + 1,
            this.state.pageCount - 1);
        this.setPageAndUpdateAssets(page);
    }
    prevPage() {
        const page = Math.max(this.state.currentPage - 1, 0);
        this.setPageAndUpdateAssets(page);
    }
    onPageClick(page) {
        this.props.onUpdateItems(null);

        const me = this;
        this.setState({
            currentPage: page
        }, function() {
            me.filterItems(me.filters);
        });
    }
    /**
     * Filter this.props.assets into this.state.filteredAssets, based
     * on the current state of this component's search filters.
     */
    filterItems(filters={}) {
        this.props.onUpdateItems(null);

        const me = this;
        getAssets(
            filters.title, filters.owner, filters.tags,
            filters.terms, filters.date,
            this.state.currentPage * this.offset
        ).then(function(d) {
            me.props.onUpdateItems(d.assets, d.asset_count);
            me.updatePageCount(d.asset_count);
        }, function(e) {
            console.error('asset get error!', e);
        });
    }
    updatePageCount(itemCount=null) {
        if (itemCount === null) {
            itemCount = this.props.itemCount;
        }
        this.setState({
            pageCount: Math.ceil(itemCount / this.offset)
        });
    }
    componentDidUpdate(prevProps) {
        if (prevProps.assets !== this.props.assets) {
            this.setState({filteredAssets: this.props.assets});
        }
        if (prevProps.itemCount !== this.props.itemCount) {
            this.updatePageCount();
        }
    }
}
