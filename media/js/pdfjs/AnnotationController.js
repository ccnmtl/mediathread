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
        this.isMakingRectangle = false;

        this.rect = {
            page: 1,
            coords: []
        };
    }

    onMouseMove(x, y) {
    }

    onMouseDown(x, y, page) {
        this.startRectangle(x, y, page);
        this.isMakingRectangle = true;
    }

    onMouseUp(x, y, page, canvas) {
        this.closeRectangle(x, y, page);
        this.isMakingRectangle = false;

        const pageEl = document.querySelector(
            '.page[data-page-number="' + page + '"]');
        const svg = pageEl.querySelector('svg');

        const draw = SVG(svg).addTo('#pdfjs-page-' + page);

        const coords = getCanvasCoords(
            this.rect.coords[0][0], this.rect.coords[0][1],
            this.rect.coords[1][0], this.rect.coords[1][1]
        );

        draw.rect(coords[2], coords[3])
            .move(coords[0], coords[1])
            .stroke('#f06').fill('none')
    }

    startRectangle(x, y, page=1) {
        this.rect = {
            page: page,
            coords: [[x, y]]
        };
    }

    closeRectangle(x, y) {
        this.rect.coords.push([x, y]);
    }
}
