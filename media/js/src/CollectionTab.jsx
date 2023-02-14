/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';

import CollectionListView from './CollectionListView';
import GridAsset from './GridAsset';
import AssetFilter from './filters/AssetFilter';
import AssetDetail from './assetDetail/AssetDetail';
import EmptyCollection from './alerts/EmptyCollection';
import LoadingAssets from './alerts/LoadingAssets';
import NoAssetsFound from './alerts/NoAssetsFound';
import Pagination from './Pagination';
import GridListSwitcher from './GridListSwitcher';

import {
    ASSETS_PER_PAGE,
    getAsset, getAssets, getCourseUrl
} from './utils';

const followLink = function(e) {
    if (e) {
        e.preventDefault();

        let href = null;
        if (e.target.href) {
            href = e.target.href;
        } else if (e.currentTarget && e.currentTarget.href) {
            // If the <a> tag is surrounding an <img> tag,
            // currentTarget will be the correct element with the
            // href, as a.target will be the image.
            href = e.currentTarget.href;
        }

        if (href) {
            const oldState = {url: location.pathname};
            window.history.pushState(oldState, null, location.pathname);
            window.history.pushState({url: href}, null, href);
        }
    }
};

export default class CollectionTab extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            viewMode: 'grid',
            selectedAsset: null,

            // Filters
            title: null,
            owner: window.MediaThread ?
                window.MediaThread.current_username :
                'all',
            tags: [],
            terms: [],
            date: 'all',

            // Pagination
            currentPage: 0,
            pageCount: 1
        };

        this.setViewMode = this.setViewMode.bind(this);
        this.enterAssetDetailView = this.enterAssetDetailView.bind(this);
        this.leaveAssetDetailView = this.leaveAssetDetailView.bind(this);
        this.onUpdateAsset = this.onUpdateAsset.bind(this);
        this.onUpdateFilter = this.onUpdateFilter.bind(this);
        this.updatePageCount = this.updatePageCount.bind(this);
        this.updateCurrentPage = this.updateCurrentPage.bind(this);
        this.onClearFilter = this.onClearFilter.bind(this);

        this.filterRef = React.createRef();
    }

    onUpdateFilter(newState) {
        this.setState({
            currentPage: 0,
            ...newState
        });
    }

    onClearFilter() {
        this.setState({
            title: null,
            owner: window.MediaThread ?
                window.MediaThread.current_username :
                'all',
            tags: [],
            terms: [],
            date: 'all',
            currentPage: 0
        });
    }

    updateCurrentPage(pageNumber) {
        this.setState({currentPage: pageNumber});
    }

    updatePageCount(assetCount=null, currentPage=null) {
        if (assetCount === null) {
            assetCount = this.props.assetCount;
        }
        this.setState({
            pageCount: Math.ceil(assetCount / ASSETS_PER_PAGE)
        });
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevProps.asset !== this.props.asset) {
            this.setState({
                selectedAsset: this.props.asset
            });
        }

        if (prevProps.assetCount !== this.props.assetCount) {
            this.updatePageCount();
        }
    }

    componentDidMount() {
        window.addEventListener('popstate', (e) => {
            // When the browser's Back button is pressed, read the
            // state's url data and use that to navigate to the
            // appropriate page, if possible.
            if (e.state && e.state.url) {
                window.location.href = e.state.url;
            }
        });
    }

    setViewMode(mode) {
        this.setState({viewMode: mode});
    }

    enterAssetDetailView(e, asset) {
        followLink(e);

        jQuery('.collection-header')
            .removeClass('d-flex')
            .addClass('d-none');

        jQuery('.collectionAdd')
            .removeClass('show');

        // Need to fetch the asset to get all the selections. The
        // collection view's selections are filtered by AssetFilter.
        const me = this;
        getAsset(asset.id).then(function(d) {
            me.setState({
                selectedAsset: d.assets[asset.id]
            }, function() {
                // Scroll to top when entering asset detail view.
                window.scrollTo(0, 0);
            });
        }, function(e) {
            me.setState({
                assetError: e
            });
        });
    }

    leaveAssetDetailView(e) {
        jQuery('.collection-header')
            .removeClass('d-none')
            .addClass('d-flex');

        followLink(e);

        // If the collection's assets haven't been fetched yet (if the
        // user navigated directly to the item detail page), we need
        // to make sure to fetch the assets.
        if (!this.props.assets || !this.props.assets.length) {
            const me = this;
            getAssets(
                '',
                window.MediaThread.current_username
            ).then(function(d) {
                me.props.onUpdateAssets(
                    d.assets,
                    d.asset_count,
                    d.active_tags,
                    d.active_vocabulary,
                    d.space_viewer.id
                );
            });
        } else {
            // Sync assets and tag/term state with the server.
            const me = this;
            getAssets(
                this.state.title, this.state.owner, this.state.tags,
                this.state.terms, this.state.date
            ).then(function(d) {
                me.props.onUpdateAssets(
                    d.assets, d.asset_count,
                    d.active_tags, d.active_vocabulary
                );

                me.updatePageCount(d.asset_count);
            }, function(e) {
                console.error('asset get error!', e);
            });

        }

        return this.setState({
            selectedAsset: null
        });
    }

    /**
     * onUpdateAsset()
     *
     * This is used to update the asset's selections when a new
     * selection is created by the user.
     */
    onUpdateAsset(asset) {
        this.setState({
            selectedAsset: asset
        });
    }

    render() {
        let assets = [];
        let assetsDom = <LoadingAssets />;
        const me = this;

        let assetList = this.props.assets;

        if (this.state.selectedAsset) {
            assetsDom = (
                <AssetDetail
                    asset={this.state.selectedAsset}
                    tags={this.props.tags}
                    terms={this.props.terms}
                    leaveAssetDetailView={this.leaveAssetDetailView}
                    onUpdateAsset={this.onUpdateAsset} />
            );
        } else if (this.props.assetError) {
            // Display error to user
            assetsDom = <strong>{this.props.assetError}</strong>;
        } else if (assetList && this.state.viewMode === 'grid') {
            let assetGroup = [];
            assetList.forEach(function(asset, idx) {
                // Put the assets in card-groups, three at a time.
                if (assetGroup.length >= 3) {
                    assets.push(
                        <div key={idx} className="card-group">
                            {assetGroup}
                        </div>
                    );
                    assetGroup = [];
                }

                assetGroup.push(
                    <GridAsset
                        key={asset.id} asset={asset}
                        enterAssetDetailView={me.enterAssetDetailView}
                        currentUser={me.props.currentUser} />);
            });

            if (assetGroup.length > 0) {
                assets.push(
                    <div key={assetGroup[0].key} className="card-group">
                        {assetGroup}
                    </div>
                );
            }

            const myUsername = window.MediaThread ? window.MediaThread.current_username : 'me';

            if (
                !this.state.title &&
                    this.state.owner === myUsername &&
                    (!this.state.tags || this.state.tags.length === 0) &&
                    (!this.state.terms || this.state.terms.length === 0) &&
                    this.state.date === 'all' &&
                    assets.length === 0
            ) {
                assetsDom = <EmptyCollection />;
            } else if (assets.length === 0) {
                assetsDom = <NoAssetsFound />;
            } else {
                assetsDom = <div>{assets}</div>;
            }
        } else if (assetList && this.state.viewMode === 'list') {
            assetsDom = (
                <CollectionListView
                    assets={assetList}
                    enterAssetDetailView={this.enterAssetDetailView}
                    onUpdateAssets={this.props.onUpdateAssets}

                    owner={this.state.owner}
                    title={this.state.title}
                    tags={this.state.tags}
                    terms={this.state.terms}
                    date={this.state.date}
                />
            );
        }

        let backButton = null;
        if (this.state.selectedAsset) {
            const courseUrl = getCourseUrl();
            backButton = (
                <div className="row mt-2">
                    <div className="col-md-auto">
                        <nav aria-label="breadcrumb">
                            <ol className="breadcrumb bg-light mb-0">
                                <li className="breadcrumb-item" aria-current="page">
                                    <a
                                        href={courseUrl}
                                        onClick={this.leaveAssetDetailView}
                                        title="Back to Collection">
                                        Back to the collection
                                    </a>
                                </li>
                            </ol>
                        </nav>
                    </div>
                </div>
            );
        }

        return (
            <div role="tabpanel">

                {backButton}

                {!this.state.selectedAsset && (
                    <>
                        <AssetFilter
                            ref={this.filterRef}
                            items={this.props.assets}
                            itemCount={this.props.assetCount}
                            currentPage={this.state.currentPage}
                            updatePageCount={this.updatePageCount}
                            owners={this.props.owners}
                            allTags={this.props.tags}
                            allTerms={this.props.terms}
                            onUpdateItems={this.props.onUpdateAssets}

                            onUpdateFilter={this.onUpdateFilter}
                            onClearFilter={this.onClearFilter}
                            owner={this.state.owner}
                            title={this.state.title}
                            tags={this.state.tags}
                            terms={this.state.terms}
                            date={this.state.date}
                        />

                        <div className="row mb-1">
                            <GridListSwitcher
                                viewMode={this.state.viewMode}
                                setViewMode={this.setViewMode} />
                            <Pagination
                                onUpdateItems={this.props.onUpdateAssets}
                                currentPage={this.state.currentPage}
                                pageCount={this.state.pageCount}
                                updatePageCount={this.updatePageCount}
                                updateCurrentPage={this.updateCurrentPage}

                                owner={this.state.owner}
                                title={this.state.title}
                                tags={this.state.tags}
                                terms={this.state.terms}
                                date={this.state.date}
                            />
                        </div>
                    </>
                )}

                <div className="assets">
                    {assetsDom}
                </div>

                {!this.state.selectedAsset && (
                    <div className="row mt-1">
                        <GridListSwitcher
                            viewMode={this.state.viewMode}
                            setViewMode={this.setViewMode} />
                        <Pagination
                            onUpdateItems={this.props.onUpdateAssets}
                            currentPage={this.state.currentPage}
                            pageCount={this.state.pageCount}
                            updatePageCount={this.updatePageCount}
                            updateCurrentPage={this.updateCurrentPage}

                            owner={this.state.owner}
                            title={this.state.title}
                            tags={this.state.tags}
                            terms={this.state.terms}
                            date={this.state.date}
                        />
                    </div>
                )}
            </div>
        );
    }
}

CollectionTab.propTypes = {
    asset: PropTypes.object,
    assets: PropTypes.array,
    assetCount: PropTypes.number,
    onUpdateAssets: PropTypes.func.isRequired,
    owners: PropTypes.array,
    tags: PropTypes.array,
    terms: PropTypes.array,
    assetError: PropTypes.string,
    currentUser: PropTypes.number
};
