/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import CollectionListView from './CollectionListView';
import GridAsset from './GridAsset';
import AssetFilter from './AssetFilter';
import AssetDetail from './assetDetail/AssetDetail';
import LoadingAssets from './alerts/LoadingAssets';
import NoAssetsFound from './alerts/NoAssetsFound';

export default class CollectionTab extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            viewMode: 'grid',
            selectedAsset: null
        };

        this.setViewMode = this.setViewMode.bind(this);
        this.toggleAssetView = this.toggleAssetView.bind(this);
        this.onUpdateAsset = this.onUpdateAsset.bind(this);
    }

    componentDidUpdate(prevProps) {
        if (prevProps.asset !== this.props.asset) {
            this.setState({selectedAsset: this.props.asset});
        }
    }

    setViewMode(mode) {
        this.setState({viewMode: mode});
    }

    toggleAssetView(asset, e) {
        // If this was an <a> link, prevent default behavior.
        if (e) {
            e.preventDefault();
            window.history.pushState(null, null, e.target.href);
        }

        if (!this.state.selectedAsset && asset) {
            this.setState({selectedAsset: asset});

            // Scroll to top when entering asset detail view.
            window.scrollTo(0, 0);
        } else {
            this.setState({selectedAsset: null});
        }
    }
    onUpdateAsset(asset) {
        this.setState({selectedAsset: asset});
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
                    toggleAssetView={this.toggleAssetView}
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
                        toggleAssetView={me.toggleAssetView}
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
                    onUpdateAssets={this.props.onUpdateAssets} />
            );
        }

        let backButton = null;
        if (this.state.selectedAsset) {
            const courseUrl = window.location.href.replace(
                /\/react\/asset\/\d+/, '');
            backButton = (
                <div
                    className="btn-group mb-1" role="group"
                    aria-label="View Toggle">
                    <a
                        href={courseUrl}
                        onClick={this.toggleAssetView}
                        title="Back"
                        className="btn btn-outline-secondary btn-sm">
                        <svg className="bi bi-caret-left-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3.86 8.753l5.482 4.796c.646.566 1.658.106 1.658-.753V3.204a1 1 0 00-1.659-.753l-5.48 4.796a1 1 0 000 1.506z"></path>
                        </svg>
                        Back to Full Collection View
                    </a>
                </div>
            );
        }

        return (
            <div role="tabpanel">
                <h1 className="page-title">Collection</h1>

                {backButton}

                <AssetFilter
                    assets={this.props.assets}
                    assetCount={this.props.assetCount}
                    hidePagination={!!this.state.selectedAsset}
                    owners={this.props.owners}
                    tags={this.props.tags}
                    terms={this.props.terms}
                    viewMode={this.state.viewMode}
                    onUpdateAssets={this.props.onUpdateAssets}
                    setViewMode={this.setViewMode} />

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
