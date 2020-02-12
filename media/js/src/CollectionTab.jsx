import React from 'react';
import PropTypes from 'prop-types';
import CollectionListView from './CollectionListView';
import GridAsset from './GridAsset';
import AssetFilter from './AssetFilter';

export default class CollectionTab extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            viewMode: 'grid',
            titleFilter: ''
        };

        this.toggleViewMode = this.toggleViewMode.bind(this);
    }
    toggleViewMode() {
        let newMode = 'list';
        if (this.state.viewMode === 'list') {
            newMode = 'grid';
        }
        this.setState({viewMode: newMode});
    }
    render() {
        let assets = [];
        let assetsDom = 'Loading Assets...';
        const me = this;

        let assetList = this.props.assets;

        if (this.props.assetError) {
            // Display error to user
            assetsDom = <strong>{this.props.assetError}</strong>;
        } else if (assetList && this.state.viewMode === 'grid') {
            assetList.forEach(function(asset) {
                assets.push(
                    <GridAsset
                        key={asset.id} asset={asset}
                        currentUser={me.props.currentUser} />);
            });

            if (assets.length === 0) {
                assetsDom = 'No assets found.';
            } else {
                assetsDom = <div className="card-columns">{assets}</div>;
            }
        } else if (assetList && this.state.viewMode === 'list') {
            assetsDom = <CollectionListView assetList={assetList} />;
        }

        const alternateViewMode =
            this.state.viewMode === 'grid' ? 'List' : 'Grid';

        return (
            <div role="tabpanel" aria-labelledby="collection-tab">
                <h1>Collection</h1>
                <h1>All Items</h1>
                <button
                    className="button-sm float-right"
                    data-testid="viewtoggle"
                    onClick={this.toggleViewMode}>
                    {alternateViewMode} view
                </button>
                <p>Select an item to create a selection from it.</p>

                <AssetFilter
                    assets={this.props.assets}
                    onUpdateAssets={this.props.onUpdateAssets}
                    tags={this.props.tags}
                    terms={this.props.terms} />

                <div className="assets">
                    {assetsDom}
                </div>
            </div>
        );
    }
}

CollectionTab.propTypes = {
    assets: PropTypes.array,
    onUpdateAssets: PropTypes.func.isRequired,
    tags: PropTypes.array,
    terms: PropTypes.array,
    assetError: PropTypes.string,
    currentUser: PropTypes.number
};
