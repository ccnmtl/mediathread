/*
 * AnnotationController
 * Copyright (C) 2021 Nik Nyby
 *
 * This file is part of Mediathread.
 *
 * Mediathread is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Mediathread is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Mediathread.  If not, see <https://www.gnu.org/licenses/>.
 */

/**
 * Given co-ordinates for two points, return the canvas API
 * co-ordinates: top-left point x/y, then width/height.
 */
const getCanvasCoords = function(x1, y1, x2, y2) {
    return [
        Math.min(x1, x2), Math.min(y1, y2),
        Math.abs(x2 - x1), Math.abs(y2 - y1)
    ];
};

/**
 * AnnotationController
 *
 * Handle creating an annotation.
 */
class AnnotationController {
    constructor() {
        this.rect = {
            page: 1,
            coords: []
        };

        this.state = {
            isMakingRect: false,
            x: 0,
            y: 0
        };
    }

    onMouseMove(x, y) {
        this.state.x = x;
        this.state.y = y;

        if (this.state.isMakingRect) {
            this.updateRect();
        }
    }

    onMouseUp(x, y, page) {
        if (!this.state.isMakingRect) {
            this.state.isMakingRect = true;
            this.startRect(x, y, page);
        } else {
            this.state.isMakingRect = false;
            this.closeRect(x, y, page);
        }
    }

    makeRect(x, y, width, height) {
        const pageEl = document.querySelector(
            '.page[data-page-number="' + this.rect.page + '"]');
        const svg = pageEl.querySelector('svg');

        const draw = SVG(svg).addTo('#pdfjs-page-' + this.rect.page);

        draw.clear();

        const rect = draw.rect(width, height)
              .move(x, y)
              .stroke({color: '#22f', width: 3})
              .fill('none');

        return rect;
    }

    updateRect() {
        const coords = getCanvasCoords(
            this.rect.coords[0][0],
            this.rect.coords[0][1],
            this.state.x, this.state.y);

        this.state.svgRect.attr({
            x: coords[0],
            y: coords[1],
            width: coords[2],
            height: coords[3]
        });
    }

    startRect(x, y, page=1) {
        this.rect = {
            page: page,
            coords: [[x, y]]
        };

        const coords = getCanvasCoords(x, y, this.state.x, this.state.y);

        this.state.svgRect = this.makeRect(...coords);
    }

    closeRect(x, y) {
        this.rect.coords.push([x, y]);
    }
}
