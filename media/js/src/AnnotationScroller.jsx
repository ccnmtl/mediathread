import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';

export default class AnnotationScroller extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currentAnnotation: 0
        };

        this.onPrevClick = this.onPrevClick.bind(this);
        this.onNextClick = this.onNextClick.bind(this);
    }
    onPrevClick(e) {
        e.preventDefault();
        if (this.state.currentAnnotation > 0) {
            this.setState({
                currentAnnotation: this.state.currentAnnotation - 1
            });
        }
    }
    onNextClick(e) {
        e.preventDefault();
        if (this.state.currentAnnotation < this.props.annotations.length - 1) {
            this.setState({
                currentAnnotation: this.state.currentAnnotation + 1
            });
        }
    }
    render() {
        const selectedAnnotation = this.props.annotations[this.state.currentAnnotation];
        return <div>
            <small>
                {this.state.currentAnnotation + 1} of {this.props.annotations.length}
            </small>

            <div>
                <strong>
                    {selectedAnnotation.title}
                </strong>
            </div>

            <a href="#" onClick={this.onPrevClick}>&lt; Previous</a>
            <span className="pipe-divider">|</span>
            <a href="#" onClick={this.onNextClick}>Next &gt;</a>
        </div>;
    }
}

AnnotationScroller.propTypes = {
    annotations: PropTypes.array.isRequired,
};
