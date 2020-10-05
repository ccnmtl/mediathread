import React from 'react';
import ReactDOM from 'react-dom';
import {getAsset, getAssets} from './utils';
import CollectionTab from './CollectionTab';
import {defineTimecodeSpinner} from './timecodeSpinner.js';


class Main extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            asset: null,
            assets: null,
            // Total number of this collection's assets, ignoring
            // pagination.
            assetCount: null,
            assetError: null,
            owners: null,
            tags: null,
            terms: null
        };

        let assetId = null;
        const re = /\/asset\/(\d+)\//;
        const match = window.location.pathname.match(re);
        if (match && match.length >= 2) {
            assetId = parseInt(match[1], 10);
        }
        this.assetId = assetId;

        const me = this;
        if (assetId) {
            getAsset(assetId).then(function(d) {
                me.setState({
                    asset: d.assets[assetId],
                    assetCount: 1,
                    tags: d.active_tags,
                    terms: d.active_vocabulary
                });
            }, function(e) {
                me.setState({
                    assetError: e
                });
            });
        } else {
            getAssets(
                '',
                window.MediaThread.current_username
            ).then(function(d) {
                me.setState({
                    assets: d.assets,
                    assetCount: d.asset_count,
                    tags: d.active_tags,
                    terms: d.active_vocabulary,
                    currentUser: d.space_viewer.id
                });
            }, function(e) {
                me.setState({
                    assetError: e
                });
            });
        }

        // Get collection metadata. For populating all the owners, for
        // example.
        getAsset().then(function(d) {
            if (d.panels.length > 0) {
                me.setState({owners: d.panels[0].owners});
            }
        }, function(e) {
            console.error('getAsset error', e);
        });

        this.onUpdateAssets = this.onUpdateAssets.bind(this);

        defineTimecodeSpinner();
    }

    /**
     * Update the current state of the assets array with the given
     * assets.
     *
     * Optionally, you can also update tags, terms, and current user
     * with this method, too.
     */
    onUpdateAssets(
        assets, assetCount=null,
        tags=null, terms=null, currentUser=null
    ) {
        let newState = {assets: assets};

        if (assetCount) {
            newState.assetCount = assetCount;
        }

        if (tags) {
            newState.tags = tags;
        }

        if (terms) {
            newState.terms = terms;
        }

        if (currentUser) {
            newState.currentUser = currentUser;
        }

        this.setState(newState);
    }

    render() {
        return (
            <div className="tab-content">
                <CollectionTab
                    asset={this.state.asset}
                    assets={this.state.assets}
                    assetCount={this.state.assetCount}
                    onUpdateAssets={this.onUpdateAssets}
                    owners={this.state.owners}
                    tags={this.state.tags}
                    terms={this.state.terms}
                    assetError={this.state.assetError}
                    currentUser={this.state.currentUser} />
            </div>
        );
    }

    componentDidMount() {
        if (this.assetId) {
            jQuery('.collection-header')
                .removeClass('d-flex')
                .addClass('d-none');
            jQuery('.collectionAdd')
                .removeClass('show');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const loadingMsg = document.querySelector('.react-loading-msg');
    loadingMsg.remove();

    const domContainer = document.querySelector('#react-container');
    ReactDOM.render(<Main />, domContainer);
});
