import React from 'react';

export default class NoAssetsFound extends React.Component {
    render() {
        return (
            <div
                className="alert alert-warning alert-dismissible fade show"
                role="alert">
                <strong>Hmmm.</strong> There are no matching
                items to your search request. Please try
                again.
                <button
                    type="button" className="close"
                    data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">×</span>
                </button>
            </div>
        );
    }
}
