/* eslint max-len: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import {getAssetUrl, getCourseUrl} from './utils';

export default class AnnotationScroller extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // -1 here represents the original item, so start there.
            currentAnnotation: -1
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
        } else {
            this.setState({currentAnnotation: -1});
            this.props.onSelectedAnnotationUpdate(null);
        }
    }
    onNextClick(e) {
        e.preventDefault();
        if (this.state.currentAnnotation < this.props.asset.annotations.length - 1) {
            const newAnnotation = this.state.currentAnnotation + 1;
            this.setState({
                currentAnnotation: newAnnotation
            });

            this.props.onSelectedAnnotationUpdate(newAnnotation);
        }
    }
    render() {
        const selectedAnnotation = (
            this.state.currentAnnotation >= 0 ?
                this.props.asset.annotations[
                    this.state.currentAnnotation] :
                null
        );

        const courseUrl = getCourseUrl();

        let activeLink = getAssetUrl(this.props.asset.id);
        let activeTitle = 'Original Item';
        if (selectedAnnotation) {
            activeLink = `${courseUrl}react/asset/` +
                  selectedAnnotation.asset_id +
                '/annotations/' + selectedAnnotation.id + '/';
            activeTitle = selectedAnnotation.title;
        }

        const showSelectionCount = this.props.asset.annotations &&
              this.props.asset.annotations.length > 0 &&
              this.state.currentAnnotation > -1;

        return (
            <div>
                <nav aria-label="Annotation navigation">
                    <ul className="pagination btn-sm selection-spinner">
                        <li className={
                            'page-item ' + (
                                this.state.currentAnnotation > -1 ?
                                    '' : 'disabled'
                            )
                        }>
                            <a
                                className="page-link" href="#"
                                onClick={this.onPrevClick}
                                title="Previous Selection"
                                aria-label="Previous Selection">
                                <span aria-hidden="true">
                                    <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-caret-left-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M3.86 8.753l5.482 4.796c.646.566 1.658.106 1.658-.753V3.204a1 1 0 0 0-1.659-.753l-5.48 4.796a1 1 0 0 0 0 1.506z"/>
                                    </svg>
                                </span>
                            </a>
                        </li>

                        <li className="page-item w-100 text-center">
                            <a className="page-link" href={activeLink}>
                                {activeTitle}
                            </a>
                        </li>

                        <li className={
                            'page-item ' + (
                                (this.state.currentAnnotation <
                                 (this.props.asset.annotations.length - 1)) ?
                                    '' : 'disabled'
                            )
                        }>
                            <a
                                className="page-link" href="#"
                                onClick={this.onNextClick}
                                title="Next Selection"
                                aria-label="Next Selection">
                                <span aria-hidden="true">
                                    <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-caret-right-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12.14 8.753l-5.482 4.796c-.646.566-1.658.106-1.658-.753V3.204a1 1 0 0 1 1.659-.753l5.48 4.796a1 1 0 0 1 0 1.506z"/>
                                    </svg>
                                </span>
                            </a>
                        </li>
                    </ul>
                    <div className={'text-center ' + (showSelectionCount ? '' : 'invisible')}>
                        Selection {this.state.currentAnnotation + 1} of&nbsp;
                        {this.props.asset.annotations.length}
                    </div>
                </nav>
            </div>
        );
    }
}

AnnotationScroller.propTypes = {
    asset: PropTypes.object.isRequired,
    onSelectedAnnotationUpdate: PropTypes.func.isRequired
};
