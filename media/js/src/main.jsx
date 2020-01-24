import React from 'react';
import ReactDOM from 'react-dom';
import {getAssetData} from './utils';
import CollectionTab from './CollectionTab';


class Main extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // Collection tab is default
            activeTab: 'collection',
            assets: null,
            assetError: null
        };

        const me = this;
        getAssetData().then(function(d) {
            me.setState({
                assets: d.assets,
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
    }

    clickTab(e) {
        e.preventDefault();
        const clicked = e.target.text.toLowerCase();
        this.setState({activeTab: clicked});
    }

    render() {
        return (
            <div>
                <nav className="nav nav-pills nav-justified">
                    <a
                        className={'nav-link ' + (
                            this.state.activeTab === 'collection' ?
                                'active' : ''
                        )}
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
                        onClick={this.clickTab}
                        title="Projects"
                        href="projects/">
                        Projects
                    </a>
                </nav>

                {this.state.activeTab === 'collection' &&
                 <CollectionTab
                     assets={this.state.assets}
                     tags={this.state.tags}
                     terms={this.state.terms}
                     assetError={this.state.assetError}
                     currentUser={this.state.currentUser} />}
            </div>
        );
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const domContainer = document.querySelector('#react-container');
    ReactDOM.render(<Main />, domContainer);
});
