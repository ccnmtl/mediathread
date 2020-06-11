import React from 'react';
import PropTypes from 'prop-types';

export default class ViewItem extends React.Component {
    render() {
        return (
            <div className="tab-content" id="pills-tabContent">
                <h3>
                    Item References within Course
                </h3>

                <div className="btn-group">
                    <a
                        className="btn btn-light dropdown-toggle"
                        data-toggle="dropdown" aria-haspopup="true"
                        aria-expanded="false">
                        Sort by
                    </a>
                    <div className="dropdown-menu">
                        <a className="dropdown-item" href="#">
                            Title, A &ndash; Z
                        </a>
                        <a className="dropdown-item" href="#">
                            Title, Z &ndash; A
                        </a>
                        <a className="dropdown-item" href="#">
                            Something else
                        </a>
                    </div>
                </div>
            </div>
        );

    }
}

ViewItem.propTypes = {
    asset: PropTypes.object
};
