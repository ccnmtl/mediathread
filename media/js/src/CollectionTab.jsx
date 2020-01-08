import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import GridAsset from './GridAsset';
import Asset from './Asset';

class RowAsset extends React.Component {
    constructor(props) {
        super(props);
        this.asset = new Asset(this.props.asset);
    }
    render() {
        return <tr>
                   <td>
                       {this.props.asset.title}
                       <span className="float-right">
                           <img src={this.asset.getThumbnail()}
                                alt={'Thumbnail for ' + this.props.asset.title}
                                height="75" />
                       </span>
                   </td>
                   <td>{this.asset.getType()}</td>
                   <td>{this.props.asset.author.public_name}</td>
                   <td>{this.props.asset.modified}</td>
               </tr>;
    }
}

RowAsset.propTypes = {
    asset: PropTypes.object.isRequired
};

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
    }
    toggleViewMode() {
        let newMode = 'list';
        if (this.state.viewMode === 'list') {
            newMode = 'grid';
        }
        this.setState({viewMode: newMode});
    }
    handleTitleFilterChange(e) {
        const str = e.target.value.trim().toLowerCase();
        let filteredAssets = [];
        this.props.assets.some(function(asset) {
            if (asset.title.toLowerCase().indexOf(str) > -1) {
                filteredAssets.push(asset);
                return true;
            }

            asset.annotations.some(function(annotation) {
                if (annotation.title.toLowerCase().indexOf(str) > -1) {
                    filteredAssets.push(asset);
                    return true;
                }
            });
        });
        this.setState({
            titleFilter: str,
            filteredAssets: filteredAssets
        });
    }
    render() {
        let assets = [];
        let assetsDom = 'Loading Assets...';
        const me = this;

        let assetList = this.props.assets;
        if (this.state.titleFilter) {
            assetList = this.state.filteredAssets;
        }

        if (this.props.assetError) {
            // Display error to user
            assetsDom = <strong>{this.props.assetError}</strong>;
        } else if (assetList && this.state.viewMode === 'grid') {
            assetList.forEach(function(asset) {
                assets.push(<GridAsset key={asset.id} asset={asset}
                                       currentUser={me.props.currentUser} />);
            });

            if (assets.length === 0) {
                assetsDom = 'No assets found.'
            } else {
                assetsDom = <div className="card-columns">{assets}</div>;
            }
        } else if (assetList && this.state.viewMode === 'list') {
            assetList.forEach(function(asset) {
                assets.push(<RowAsset key={asset.id} asset={asset} />)
            });

            if (assets.length === 0) {
                assetsDom = 'No assets found.'
            } else {
                assetsDom = <table className="table">
                    <thead>
                        <tr>
                            <th scope="col">Item Title</th>
                            <th scope="col">Item Type</th>
                            <th scope="col">Item Owner</th>
                            <th scope="col">Item Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {assets}
                    </tbody>
                </table>;
            }
        }

        const alternateViewMode =
            this.state.viewMode === 'grid' ? 'List' : 'Grid';

        return (
            <div>
                <h1>Collection</h1>
                <h1>All Items</h1>
                <button className="button-sm float-right"
                        data-testid="viewtoggle"
                        onClick={this.toggleViewMode}>
                    {alternateViewMode} view
                </button>
                <p>Select an item to create a selection from it.</p>

                <div className="input-group mb-3">
                    <label>
                        Title
                        <input type="text" name="title"
                               className="form-control"
                               onChange={this.handleTitleFilterChange}
                               defaultValue={this.state.titleFilter}
                               placeholder="Title of items and selections"
                               aria-label="Title" />
                    </label>
                </div>

                <div className="assets">
                    {assetsDom}
                </div>
            </div>
        );
    }
}

CollectionTab.propTypes = {
    assets: PropTypes.array,
    assetError: PropTypes.string,
    currentUser: PropTypes.number
};
