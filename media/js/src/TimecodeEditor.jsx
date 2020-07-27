import React from 'react';
import PropTypes from 'prop-types';
import isFinite from 'lodash/isFinite';
import {formatTimecode, parseTimecode} from './utils.js';

/**
 * TimecodeEditor is a form widget that handles updating a
 * timestamp value. It doesn't handle its own state. See:
 * https://facebook.github.io/react/docs/lifting-state-up.html#lifting-state-up
 */
export default class TimecodeEditor extends React.Component {
    constructor(props) {
        super(props);
        this.spinnerRef = React.createRef();
    }
    render() {
        let timecode = 0;
        if (this.props.timecode) {
            timecode = formatTimecode(this.props.timecode);
        }
        return (
            <div className="jux-timecode-editor">
                <input
                    ref={this.spinnerRef}
                    min={this.props.min}
                    required
                    defaultValue={timecode} />
            </div>
        );
    }
    componentDidUpdate(props) {
        // Because this is an uncontrolled input, we need to manually
        // update the value of the input when the active element is
        // updated.
        if (!this.spinnerRef) {
            return;
        }

        const spinner = this.spinnerRef.current;
        if (parseTimecode(spinner.value) !== props.timecode) {
            spinner.value = formatTimecode(props.timecode);
        }
    }
    componentDidMount() {
        if (!this.spinnerRef) {
            return;
        }

        const me = this;
        const spinner = this.spinnerRef.current;
        jQuery(spinner).timecodespinner({
            change: function(e) {
                const seconds = parseTimecode(e.target.value);
                if (isFinite(seconds)) {
                    me.props.onChange(seconds);
                }

                if (me.props.timecode !== spinner.value) {
                    // Update the input value from the application state
                    // when the user puts it in an invalid state.
                    spinner.value = formatTimecode(
                        me.props.timecode);
                }
            },
            spin: function(e, ui) {
                const seconds = ui.value / 100;
                if (isFinite(seconds)) {
                    me.props.onChange(seconds);
                }
                if (me.props.timecode !== spinner.value) {
                    // Lock down the value on spin as well.
                    spinner.value = formatTimecode(
                        me.props.timecode);
                    return false;
                }
            }
        });
    }
    componentWillUnmount() {
        if (!this.spinnerRef) {
            return;
        }

        jQuery(this.spinnerRef.current).timecodespinner('destroy');
    }
}

TimecodeEditor.propTypes = {
    min: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
    timecode: PropTypes.number
};
