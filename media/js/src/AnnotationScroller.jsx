import React from 'react';
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
            const newAnnotation = this.state.currentAnnotation - 1;
            this.setState({
                currentAnnotation: newAnnotation
            });

            this.props.onSelectedAnnotationUpdate(newAnnotation);
        }
    }
    onNextClick(e) {
        e.preventDefault();
        if (this.state.currentAnnotation < this.props.annotations.length - 1) {
            const newAnnotation = this.state.currentAnnotation + 1;
            this.setState({
                currentAnnotation: newAnnotation
            });

            this.props.onSelectedAnnotationUpdate(newAnnotation);
        }
    }
    showAnnotation() {
        /*const selectedAnnotation =
              this.props.annotations[this.state.currentAnnotation];
        const annotationData = JSON.parse(selectedAnnotation.annotation_data);*/
    }
    render() {
        const selectedAnnotation =
              this.props.annotations[this.state.currentAnnotation];
        return <div>
            <small>
                {this.state.currentAnnotation + 1} of&nbsp;
                {this.props.annotations.length}
            </small>

            <div>
                <strong>
                    {selectedAnnotation.title}
                </strong>
            </div>

            <a href="#" title="Previous annotation"
                onClick={this.onPrevClick}>&lt; Previous</a>
            <span className="pipe-divider">|</span>
            <a href="#" title="Next annotation"
                onClick={this.onNextClick}>Next &gt;</a>
        </div>;
    }
    componentDidMount() {
        this.showAnnotation();
    }
}

AnnotationScroller.propTypes = {
    annotations: PropTypes.array.isRequired,
    onSelectedAnnotationUpdate: PropTypes.func.isRequired
};
