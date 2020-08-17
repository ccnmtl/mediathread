import React from 'react';

export default class EmptyCollection extends React.Component {
    render() {
        return (
            <div
                className="alert alert-warning alert-dismissible fade show"
                role="alert">
                <strong>Hmmm.</strong> You have not collected any
                items. Click&nbsp;
                <strong>Add to Collection</strong> to get started or
                search for items your
                classmates have collected using the <strong>Owner</strong> list.
                <button
                    type="button" className="close"
                    data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">×</span>
                </button>
            </div>
        );
    }
}
