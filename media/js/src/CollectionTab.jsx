import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';

class MySelections extends React.Component {
    render() {
        let annotationsDom = null;
        let annotations = [];

        const me = this;
        this.props.annotations.forEach(function(annotation) {
            if (annotation.author.id === me.props.currentUser) {
                annotations.push(
                    <div key={annotation.id}
                         className="card-body">
                        {annotation.title}
                    </div>
                );
            }
        });

        if (annotations.length > 0) {
            annotationsDom = <div>
                <h5>My Annotations</h5>
                {annotations}
            </div>;
        }

        return annotationsDom;
    }
}

MySelections.propTypes = {
    annotations: PropTypes.array,
    currentUser: PropTypes.number.isRequired
};

class ClassSelections extends React.Component {
    render() {
        let annotationsDom = null;
        let annotations = [];

        const me = this;
        this.props.annotations.forEach(function(annotation) {
            if (annotation.author.id !== me.props.currentUser) {
                annotations.push(
                    <div key={annotation.id}
                         className="card-body">
                        {annotation.title}
                    </div>
                );
            }
        });

        if (annotations.length > 0) {
            annotationsDom = <div>
                <h5>Class Annotations</h5>
                {annotations}
            </div>;
        }

        return annotationsDom;
    }
}

ClassSelections.propTypes = {
    annotations: PropTypes.array,
    currentUser: PropTypes.number.isRequired
};

class GridAsset extends React.Component {
    render() {
        const thumbnail = this.props.asset.thumb_url ||
                          this.props.asset.sources.image.url;

        return <div className="card" key={this.props.asset.id}>
            <img src={thumbnail}
                 className="card-img-top" />

            <span className="badge badge-secondary">
                {this.props.asset.primary_type}
            </span>

            <div className="card-body">
                <h5 className="card-title">
                    <a href={this.props.asset.local_url}>
                        {this.props.asset.title}
                    </a>
                </h5>
            </div>
            <MySelections
                annotations={this.props.asset.annotations}
                currentUser={this.props.currentUser} />
            <ClassSelections
                annotations={this.props.asset.annotations}
                currentUser={this.props.currentUser} />
        </div>
    }
}

GridAsset.propTypes = {
    asset: PropTypes.object.isRequired,
    currentUser: PropTypes.number.isRequired
};

class AssetRow extends React.Component {
    render() {
        const thumbnail = this.props.asset.thumb_url ||
                          this.props.asset.sources.image.url;
        return <tr>
            <td>
                {this.props.asset.title}
                <span className="float-right">
                    <img src={thumbnail}
                         alt={'Thumbnail for ' + this.props.asset.title}
                         height="75" />
                </span>
            </td>
            <td>{this.props.asset.primary_type}</td>
            <td>{this.props.asset.author.public_name}</td>
            <td>{this.props.asset.modified}</td>
        </tr>
    }
}

AssetRow.propTypes = {
    asset: PropTypes.object.isRequired
};

export default class CollectionTab extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            viewMode: 'grid'
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

        if (this.props.assetError) {
            // Display error to user
            assetsDom = <strong>{this.props.assetError}</strong>;
        } else if (this.props.assets && this.state.viewMode === 'grid') {
            this.props.assets.forEach(function(asset) {
                assets.push(<GridAsset key={asset.id} asset={asset}
                                       currentUser={me.props.currentUser} />);
            });

            if (assets.length === 0) {
                assetsDom = 'No assets found.'
            } else {
                assetsDom = <div className="card-columns">{assets}</div>;
            }
        } else if (this.props.assets && this.state.viewMode === 'list') {
            this.props.assets.forEach(function(asset) {
                assets.push(<AssetRow key={asset.id} asset={asset} />)
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
                        onClick={this.toggleViewMode}>
                    {alternateViewMode} view
                </button>
                <p>Select an item to create a selection from it.</p>

                <div className="input-group mb-3">
                    <label>
                        Title
                        <input type="text" className="form-control"
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
