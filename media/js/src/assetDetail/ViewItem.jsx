import React from 'react';
import PropTypes from 'prop-types';

export default class ViewItem extends React.Component {
    render() {
        return (
            <div className="tab-content" id="pills-tabContent">
                <h3>
                    Item References within Course
                </h3>
            </div>
        );

    }
}

ViewItem.propTypes = {
    asset: PropTypes.object
};
