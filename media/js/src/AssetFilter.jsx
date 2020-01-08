import React from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';

export default class AssetFilter extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            titleFilter: '',
            selectedOwner: 'all'
        };
        this.handleChange = this.handleChange.bind(this);
    }
    handleChange(e) {
        console.log('handleChange');
    }
    render() {
        const { selectedOwner } = this.state;

        return (
            <div className="container mb-3">
                <div className="row">
                    <div className="col-md-4">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">
                                    <svg
                                        className="bi bi-search"
                                        width="1em" height="1em"
                                        viewBox="0 0 20 20" fill="currentColor"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path
                                            fillRule="evenodd"
                                            d={'M12.442 12.442a1 1 0 ' +
                                               '011.415 0l3.85 3.85a1 1 ' +
                                               '0 01-1.414 ' +
                                               '1.415l-3.85-3.85a1 1 0 ' +
                                               '010-1.415z'}
                                            clipRule="evenodd" />
                                        <path
                                            fillRule="evenodd"
                                            d={'M8.5 14a5.5 5.5 0 100-11 ' +
                                               '5.5 5.5 0 000 11zM15 ' +
                                               '8.5a6.5 6.5 0 11-13 0 ' +
                                               '6.5 6.5 0 0113 0z'}
                                            clipRule="evenodd" />
                                    </svg>
                                </span>
                            </div>
                            <input
                                type="text" name="title"
                                className="form-control"
                                onChange={this.props.handleTitleFilterChange}
                                defaultValue={this.state.titleFilter}
                                placeholder="Title of items and selections"
                                aria-label="Title" />
                            <div className="input-group-append">
                                <button
                                    className="btn btn-outline-secondary"
                                    type="button" id="button-addon2">
                                    Go
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">Owner</span>
                            </div>
                            <Select
                                className="react-select"
                                onChange={this.handleChange}
                                value={selectedOwner}
                                options={[
                                    { value: 'all', label: 'All Class Members' }
                                ]} />
                        </div>

                    </div>

                    <div className="col-md-4">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">Tags</span>
                            </div>
                            <Select
                                className="react-select"
                                onChange={this.handleChange} options={[]} />
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">Terms</span>
                            </div>
                            <Select
                                className="react-select"
                                onChange={this.handleChange} options={[]} />
                        </div>
                    </div>

                    <div className="col">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">Date</span>
                            </div>
                            <Select
                                className="react-select"
                                onChange={this.handleChange} options={[]} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

AssetFilter.propTypes = {
    handleTitleFilterChange: PropTypes.func.isRequired
};
