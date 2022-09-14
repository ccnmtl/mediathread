import React from 'react';
import PropTypes from 'prop-types';

export default class GridListSwitcher extends React.Component {
    render() {
        return (
            <div className="col-md-6">
                <div
                    id="view-toggle" className="btn-group"
                    role="group" aria-label="View Toggle">
                    <button
                        type="button"
                        id="viewtoggle-grid"
                        data-testid="viewtoggle-grid"
                        onClick={() => this.props.setViewMode('grid')}
                        className={'btn btn-outline-primary btn-sm ' + (
                            this.props.viewMode === 'grid' ? 'active' : ''
                        )}>
                        Grid
                    </button>
                    <button
                        type="button"
                        id="viewtoggle-list"
                        data-testid="viewtoggle-list"
                        onClick={() => this.props.setViewMode('list')}
                        className={'btn btn-outline-primary btn-sm ' + (
                            this.props.viewMode === 'list' ? 'active' : ''
                        )}>
                        List
                    </button>
                </div>
            </div>
        );
    }
}

GridListSwitcher.propTypes = {
    viewMode: PropTypes.string.isRequired,
    setViewMode: PropTypes.func.isRequired
};
