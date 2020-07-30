import React from 'react';
import PropTypes from 'prop-types';
import {getCourseUrl} from './utils';

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

        // TODO: link to annotation, not just asset.
        const courseUrl = getCourseUrl();
        const annotationLink = `${courseUrl}react/asset/` +
              selectedAnnotation.asset_id +
              '/annotations/' + selectedAnnotation.id + '/';

        return (
            <div>
                <p className="card-text">
                    <a
                        href={annotationLink}
                        title={selectedAnnotation.title}>
                        {selectedAnnotation.title}
                    </a>
                </p>


                <nav aria-label="Annotation navigation">
                    <ul className="pagination btn-sm">
                        <li className={
                            'page-item ' + (
                                this.state.currentAnnotation > 0 ?
                                    '' : 'disabled'
                            )
                        }>
                            <a
                                className="page-link" href="#"
                                onClick={this.onPrevClick}
                                aria-label="Previous">
                                <span aria-hidden="true">«</span>
                            </a>
                        </li>
                        <li className="page-item">
                            <a className="page-link" href="#">
                                {this.state.currentAnnotation + 1} of&nbsp;
                                {this.props.annotations.length}
                            </a>
                        </li>
                        <li className={
                            'page-item ' + (
                                (this.state.currentAnnotation <
                                 (this.props.annotations.length - 1)) ?
                                    '' : 'disabled'
                            )
                        }>
                            <a
                                className="page-link" href="#"
                                onClick={this.onNextClick}
                                aria-label="Next">
                                <span aria-hidden="true">»</span>
                            </a>
                        </li>
                    </ul>
                </nav>
            </div>
        );
    }
    componentDidMount() {
        this.showAnnotation();
    }
}

AnnotationScroller.propTypes = {
    annotations: PropTypes.array.isRequired,
    onSelectedAnnotationUpdate: PropTypes.func.isRequired
};
