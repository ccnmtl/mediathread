import {formatTimecode, parseTimecode} from './utils.js';

export function defineTimecodeSpinner() {
    if (typeof jQuery === 'undefined') {
        return;
    }

    jQuery.widget('ui.timecodespinner', jQuery.ui.spinner, {
        options: {
            // One 'step' is a second. This widget represents the
            // timecode in centiseconds.
            step: 100,
            // page-up / page-down will change the minute.
            page: 60
        },
        _parse: function(value) {
            if (typeof value === 'string') {
                // already a timestamp
                if (Number(value) == value) {
                    return Number(value);
                }

                return parseTimecode(value) * 100;
            }
            return value;
        },
        _format: function(value) {
            const formatted = formatTimecode(value / 100);
            return formatted;
        }
    });
}
