import React from 'react';
import PropTypes from 'prop-types';

import Asset from '../Asset';

export default class ViewItem extends React.Component {
    constructor(props) {
        super(props);
        this.asset = new Asset(this.props.asset);
    }

    render() {
        let thumbnail = null;
        const type = this.asset.getType();
        if (type === 'image') {
            thumbnail = (
                <img
                    className="img-fluid"
                    alt={'Thumbnail for: ' +
                         this.props.asset.title}
                    src={this.asset.getThumbnail()} />
            );
        } else if (type === 'video') {
            thumbnail = (
                <img
                    style={{'maxWidth': '100%'}}
                    className="img-fluid"
                    alt={'Video thumbnail for: ' +
                         this.props.asset.title}
                    src={this.asset.getThumbnail()} />
            );
        }
        return (
            <div className="tab-content" id="pills-tabContent">
                <div
                    className="tab-pane fade show active"
                    id="pills-details"
                    role="tabpanel"
                    aria-labelledby="pills-details-tab">
                    <div className="row no-gutters align-items-center">
                        <div className="col-md-4">
                            <div className="card-body">
                                {thumbnail}
                            </div>
                        </div>
                        <div className="col-md-8">
                            <div className="card-body">
                                <h5 className="card-title">
                                    {this.props.asset.title}
                                </h5>
                                <p className="card-text">
                                    This is a wider card
                                    with supporting text
                                    below as a natural
                                    lead-in to additional
                                    content. This content
                                    is a little bit
                                    longer.
                                </p>
                                <p className="card-text">
                                    <small>
                                        <a href="#">Tag</a>
                                        <a href="#">Tag</a>
                                    </small>
                                </p>
                                <p className="card-text">
                                    <small>
                                        <a href="#">Term</a>
                                        <a href="#">Term</a>
                                    </small>
                                </p>
                                <div>
                                    <button
                                        type="button"
                                        className="btn btn-sm btn-primary">
                                        Edit
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        );

    }
}

ViewItem.propTypes = {
    asset: PropTypes.object
};
