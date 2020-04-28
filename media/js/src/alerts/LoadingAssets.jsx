import React from 'react';

export default class LoadingAssets extends React.Component {
    render() {
        return (
            <div className="alert alert-info" role="alert">
                <span
                    className="spinner-border spinner-border-sm text-dark"
                    role="status" aria-hidden="true"></span>&nbsp;
                <strong>Just a moment.</strong>&nbsp;
                Mediathread is currently loading all of
                the items within this collection.
            </div>
        );
    }
}
