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
            titleFilter: '',
            filteredAssets: this.props.assets
        };

        this.toggleViewMode = this.toggleViewMode.bind(this);
        this.handleTitleFilterChange = this.handleTitleFilterChange.bind(this);
        this.handleTitleFilterSearch = this.handleTitleFilterSearch.bind(this);
    }
    toggleViewMode() {
        let newMode = 'list';
        if (this.state.viewMode === 'list') {
            newMode = 'grid';
        }
        this.setState({viewMode: newMode});
    }
    handleTitleFilterChange(e) {
        const query = e.target.value.trim().toLowerCase();
        this.setState({titleFilter: query});
    }
    handleTitleFilterSearch(e) {
        if (this.state.titleFilter.trim() === '') {
            this.setState({filteredAssets: this.props.assets});
            return;
        }

        let filteredAssets = [];
        const me = this;

        this.props.assets.some(function(asset) {
            if (
                asset.title.toLowerCase().indexOf(
                    me.state.titleFilter
                ) > -1
            ) {
                filteredAssets.push(asset);
                return true;
            }

            asset.annotations.some(function(annotation) {
                if (
                    annotation.title.toLowerCase().indexOf(
                        me.state.titleFilter) > -1
                ) {
                    filteredAssets.push(asset);
                    return true;
                }
            });
            me.setState({filteredAssets: filteredAssets});
        });
    }
    render() {
        let assets = [];
        let assetsDom = 'Loading Assets...';
        const me = this;

        let assetList = this.props.assets;
        if (this.state.filteredAssets) {
            assetList = this.state.filteredAssets;
        }

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
            <div>
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
                    tags={this.props.tags}
                    terms={this.props.terms}
                    handleTitleFilterChange={this.handleTitleFilterChange}
                    handleTitleFilterSearch={this.handleTitleFilterSearch} />

                <div className="assets">
                    {assetsDom}
                </div>
            </div>
        );
    }
}

CollectionTab.propTypes = {
    assets: PropTypes.array,
    tags: PropTypes.array,
    terms: PropTypes.array,
    assetError: PropTypes.string,
    currentUser: PropTypes.number
};
