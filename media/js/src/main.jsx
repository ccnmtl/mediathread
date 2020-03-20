import React from 'react';
import ReactDOM from 'react-dom';
import {getAsset, getAssets} from './utils';
import CollectionTab from './CollectionTab';


class Main extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // Collection tab is default
            activeTab: 'collection',
            asset: null,
            assets: null,
            // Total number of this collection's assets, ignoring
            // pagination.
            assetCount: null,
            assetError: null,
            owners: null
        };

        let assetId = null;
        const re = /\/asset\/(\d+)\/$/;
        const match = window.location.pathname.match(re);
        if (match && match.length >= 2) {
            assetId = parseInt(match[1], 10);
        }

        const me = this;

        if (assetId) {
            getAsset(assetId).then(function(d) {
                console.log('d', d);
                me.setState({
                    asset: d.assets[assetId],
                    assetCount: 1
                });
            }, function(e) {
                me.setState({
                    assetError: e
                });
            });
        } else {
            getAssets().then(function(d) {
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

        this.clickTab = this.clickTab.bind(this);
        this.onUpdateAssets = this.onUpdateAssets.bind(this);
    }

    clickTab(e) {
        e.preventDefault();
        const clicked = e.target.text.toLowerCase();
        this.setState({activeTab: clicked});
    }

    onUpdateAssets(assets, assetCount=null) {
        if (assetCount === null) {
            assetCount = this.state.assetCount;
        }
        this.setState({
            assets: assets,
            assetCount: assetCount
        });
    }

    render() {
        return (
            <div>
                <nav className="nav nav-pills nav-justified" role="tablist">
                    <a
                        className={'nav-link ' + (
                            this.state.activeTab === 'collection' ?
                                'active' : ''
                        )}
                        role="tab"
                        aria-controls="collection"
                        onClick={this.clickTab}
                        title="Collection"
                        href="collection/">
                        Collection
                    </a>
                    <a
                        className={'nav-link ' + (
                            this.state.activeTab === 'assignments' ?
                                'active' : ''
                        )}
                        role="tab"
                        aria-controls="assignments"
                        onClick={this.clickTab}
                        title="Assignments"
                        href="assignments/">
                        Assignments
                    </a>
                    <a
                        className={'nav-link ' + (
                            this.state.activeTab === 'projects' ?
                                'active' : ''
                        )}
                        role="tab"
                        aria-controls="projects"
                        onClick={this.clickTab}
                        title="Projects"
                        href="projects/">
                        Projects
                    </a>
                </nav>

                <div className="tab-content">
                    {this.state.activeTab === 'collection' &&

                     <CollectionTab
                         asset={this.state.asset}
                         assets={this.state.assets}
                         assetCount={this.state.assetCount}
                         onUpdateAssets={this.onUpdateAssets}
                         owners={this.state.owners}
                         tags={this.state.tags}
                         terms={this.state.terms}
                         assetError={this.state.assetError}
                         currentUser={this.state.currentUser} />}
                </div>
            </div>
        );
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const domContainer = document.querySelector('#react-container');
    ReactDOM.render(<Main />, domContainer);
});
