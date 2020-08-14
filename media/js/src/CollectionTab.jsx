/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import CollectionListView from './CollectionListView';
import GridAsset from './GridAsset';
import AssetFilter from './filters/AssetFilter';
import AssetDetail from './assetDetail/AssetDetail';
import LoadingAssets from './alerts/LoadingAssets';
import NoAssetsFound from './alerts/NoAssetsFound';

import {getAssets, getCourseUrl, updateAsset} from './utils';

export default class CollectionTab extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            viewMode: 'grid',
            selectedAsset: null
        };

        this.setViewMode = this.setViewMode.bind(this);
        this.enterAssetDetailView = this.enterAssetDetailView.bind(this);
        this.leaveAssetDetailView = this.leaveAssetDetailView.bind(this);
        this.onUpdateAsset = this.onUpdateAsset.bind(this);
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevProps.asset !== this.props.asset) {
            this.setState({
                selectedAsset: this.props.asset
            });
        }
    }

    setViewMode(mode) {
        this.setState({viewMode: mode});
    }

    followLink(e) {
        // If this was an <a> link, prevent default behavior.
        if (e) {
            e.preventDefault();
            window.history.pushState(null, null, e.target.href);
        }
    }

    enterAssetDetailView(e, asset) {
        this.followLink(e);

        jQuery('.collection-header')
            .removeClass('d-flex')
            .addClass('d-none');

        this.setState({
            selectedAsset: asset
        }, function() {
            // Scroll to top when entering asset detail view.
            window.scrollTo(0, 0);
        });
    }

    leaveAssetDetailView(e) {
        jQuery('.collection-header')
            .removeClass('d-none')
            .addClass('d-flex');

        this.followLink(e);

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
            // Sync the selected asset with the state of the
            // collection's assets, in case the user added, edited, or
            // removed any selections on this asset.
            const newAssets = updateAsset(
                this.props.assets, this.state.selectedAsset);
            this.props.onUpdateAssets(newAssets);
        }

        this.setState({
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

            if (assets.length === 0) {
                assetsDom = <NoAssetsFound />;
            } else {
                assetsDom = <div>{assets}</div>;
            }
        } else if (assetList && this.state.viewMode === 'list') {
            assetsDom = (
                <CollectionListView
                    assets={assetList}
                    enterAssetDetailView={this.enterAssetDetailView}
                    onUpdateAssets={this.props.onUpdateAssets} />
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
                    <AssetFilter
                        items={this.props.assets}
                        itemCount={this.props.assetCount}
                        hidePagination={false}
                        owners={this.props.owners}
                        tags={this.props.tags}
                        terms={this.props.terms}
                        viewMode={this.state.viewMode}
                        onUpdateItems={this.props.onUpdateAssets}
                        setViewMode={this.setViewMode}
                    />
                )}

                <div className="assets">
                    {assetsDom}
                </div>
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
