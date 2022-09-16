import {Control} from 'ol/control';

const CenterControl = /*@__PURE__*/(function(Control) {
    function CenterControl(opt_options) {
        var options = opt_options || {};

        var button = document.createElement('button');
        button.setAttribute('aria-label', 'center image button');

        var centerIcon = '<svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 432.2 432.2"><defs><style>.cls-1{fill:#fff;}</style></defs><circle class="cls-1" cx="388.29" cy="295.08" r="54.25" transform="translate(-214.44 -12.98) rotate(-9.22)"/><path class="cls-1" d="M575.51,266.21H544.45A159.23,159.23,0,0,0,417.16,138.92V107.86A28.88,28.88,0,0,0,388.28,79h0a28.87,28.87,0,0,0-28.87,28.88v31.06A159.23,159.23,0,0,0,232.13,266.21H201.07a28.88,28.88,0,1,0,0,57.75h31.06A159.22,159.22,0,0,0,359.41,451.24v31.07a28.87,28.87,0,0,0,28.87,28.87h0a28.88,28.88,0,0,0,28.88-28.87V451.25A159.23,159.23,0,0,0,544.45,324h31.06a28.88,28.88,0,1,0,0-57.75ZM417.16,412.37v-6.14a28.88,28.88,0,0,0-28.88-28.88h0a28.87,28.87,0,0,0-28.87,28.88v6.13A121.2,121.2,0,0,1,271,324h6.14a28.88,28.88,0,0,0,0-57.75H271a121.23,121.23,0,0,1,88.4-88.41v6.14a28.86,28.86,0,0,0,28.87,28.87h0a28.87,28.87,0,0,0,28.88-28.87V177.8a121.21,121.21,0,0,1,88.41,88.41h-6.14a28.88,28.88,0,0,0,0,57.75h6.14A121.22,121.22,0,0,1,417.16,412.37Z" transform="translate(-172.19 -78.98)"/></svg>';

        button.innerHTML = centerIcon;

        var element = document.createElement('div');
        element.className = 'center-btn ol-unselectable ol-control';
        element.appendChild(button);

        Control.call(this, {
            element: element,
            target: options.target,
        });
        if(this.handleCenter){
            button.addEventListener(
                'click', this.handleCenter.bind(this), false);
        }
    }

    if (Control) CenterControl.__proto__ = Control;
    CenterControl.prototype = Object.create(Control && Control.prototype);
    CenterControl.prototype.constructor = CenterControl;

    return CenterControl;
}(Control));

export {
    CenterControl
};
