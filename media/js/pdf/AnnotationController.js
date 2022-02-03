/* global SVG */
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
import {convertPointsToXYWH} from './utils.js';

/**
 * AnnotationController
 *
 * Handle creating an annotation.
 */
export default class AnnotationController {
    constructor() {
        this.rect = null;

        this.page = 1;

        this.state = {
            isMakingRect: false,
            x: 0,
            y: 0,
            scale: 1
        };
    }

    onMouseMove(x, y, page=1) {
        this.state.x = x / this.state.scale;
        this.state.y = y / this.state.scale;

        // Don't allow multi-page annotations
        if (this.state.isMakingRect && this.page === page) {
            this.updateRect();
        }
    }

    onMouseUp(x, y, page) {
        if (this.state.isMakingRect) {
            this.state.isMakingRect = false;
            this.closeRect(
                x / this.state.scale,
                y / this.state.scale,
                page
            );
        }
    }

    onMouseDown(x, y, page) {
        this.state.isMakingRect = true;

        if (page !== this.page) {
            // Clear the old page
            this.clearRect(this.page);
        }

        this.startRect(
            x / this.state.scale,
            y / this.state.scale,
            page
        );

        // Tell the parent application that drawing has started.
        window.top.postMessage({
            message: 'pdfAnnotationRectStarted'
        }, '*');
    }

    getSVG(page) {
        const pageEl = document.querySelector(
            '.page[data-page-number="' + page + '"]');
        const svg = pageEl.querySelector('svg');

        if (svg) {
            const draw = SVG(svg).addTo('#pdfjs-page-' + page);

            return draw;
        }

        return null;
    }

    makeRect(x, y, width, height) {
        const draw = this.getSVG(this.page);

        draw.clear();

        const rect = draw.rect(width, height)
            .move(x, y)
            .stroke({color: '#22f', width: 3})
            .fill('none');

        return rect;
    }

    clearRect(page=null) {
        if (!page) {
            page = this.page;
        }

        const draw = this.getSVG(page);

        if (draw) {
            draw.clear();
        } else {
            console.error('draw.clear() failed, couldn\'t find SVG.');
        }
    }

    updateRect() {
        const coords = convertPointsToXYWH(
            this.rect.coords[0][0],
            this.rect.coords[0][1],
            this.state.x, this.state.y,
            this.state.scale
        );

        this.state.svgRect.attr({
            x: coords[0],
            y: coords[1],
            width: coords[2],
            height: coords[3]
        });
    }

    startRect(x, y, page=1) {
        if (!isNaN(page)) {
            this.page = page;
        }

        this.rect = {
            coords: [[x, y]],
            page: parseInt(this.page)
        };

        this.displayRect(
            x, y, this.state.x, this.state.y,
            this.state.scale
        );
    }

    closeRect(x, y) {
        this.rect.coords.push([x, y]);

        // Tell the parent application about the new rectangle.
        window.top.postMessage({
            message: 'pdfAnnotationRectCreated',
            rect: this.rect
        }, '*');
    }

    displayRect(x1, y1, x2, y2, scale=1) {
        const coords = convertPointsToXYWH(x1, y1, x2, y2, scale);

        this.state.svgRect = this.makeRect(...coords);
    }

    onPageRendered() {
        if (!this.rect) {
            return;
        }

        this.displayRect(
            this.rect.coords[0][0],
            this.rect.coords[0][1],
            this.rect.coords[1][0],
            this.rect.coords[1][1],
            this.state.scale
        );
    }

    onZoomChange(scale) {
        this.state.scale = scale;
    }
}
