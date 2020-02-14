import React from 'react';
import ReactDOM from 'react-dom';
import {getAssets} from './utils';
import CollectionTab from './CollectionTab';


class Main extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // Collection tab is default
            activeTab: 'collection',
            assets: null,
            // Total number of this collection's assets, ignoring
            // pagination.
            assetCount: null,
            assetError: null
        };

        const me = this;
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
                         assets={this.state.assets}
                         assetCount={this.state.assetCount}
                         onUpdateAssets={this.onUpdateAssets}
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
