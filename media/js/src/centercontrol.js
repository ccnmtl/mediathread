import {Control} from 'ol/control';

const CenterControl = /*@__PURE__*/(function(Control) {
    function CenterControl(opt_options) {
        var options = opt_options || {};

        var button = document.createElement('button');
        button.innerHTML = '[ ]';

        var element = document.createElement('div');
        element.className = 'center-btn ol-unselectable ol-control';
        element.appendChild(button);

        Control.call(this, {
            element: element,
            target: options.target,
        });

        button.addEventListener('click', this.handleCenter.bind(this), false);
    }

    if (Control) CenterControl.__proto__ = Control;
    CenterControl.prototype = Object.create(Control && Control.prototype);
    CenterControl.prototype.constructor = CenterControl;

    return CenterControl;
}(Control));

export {
    CenterControl
};
