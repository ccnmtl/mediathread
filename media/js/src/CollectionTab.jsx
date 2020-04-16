import React from 'react';
import PropTypes from 'prop-types';
import CollectionListView from './CollectionListView';
import GridAsset from './GridAsset';
import AssetFilter from './AssetFilter';
import AssetDetail from './AssetDetail';

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
        let assetsDom = (
            <div className="alert alert-info" role="alert">
                <strong>Just a moment.</strong>&nbsp;
                Mediathread is currently loading all of
                the items within this collection.
            </div>);
        const me = this;

        let assetList = this.props.assets;

        if (this.state.selectedAsset) {
            assetsDom = (
                <AssetDetail
                    asset={this.state.selectedAsset}
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
                    <div key={assetGroup.length} className="card-group">
                        {assetGroup}
                    </div>
                );
            }

            if (assets.length === 0) {
                assetsDom = 'No assets found.';
            } else {
                assetsDom = <div>{assets}</div>;
            }
        } else if (assetList && this.state.viewMode === 'list') {
            assetsDom = <CollectionListView assetList={assetList} />;
        }

        return (
            <div role="tabpanel">
                <h1 className="page-title">Collection</h1>

                <AssetFilter
                    assets={this.props.assets}
                    assetCount={this.props.assetCount}
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
