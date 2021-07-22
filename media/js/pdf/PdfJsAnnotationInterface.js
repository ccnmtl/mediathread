/*
 * PdfJsAnnotationInterface
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
 * PdfJsAnnotationInterface
 *
 * Custom Mediathread PDF viewer events on top of PDF.js's viewer.
 *
 * A black-box re-implementation of Dropbox's ideas from 2016.
 * https://dropbox.tech/application/annotations-on-document-previews
 *
 * This class handles co-ordinate translation from the DOM into PDF
 * annotation co-ordinates ready for the database.
 */
class PdfJsAnnotationInterface {
    constructor(annotationController) {
        this.annotationController = annotationController;
        this.x = 0;
        this.y = 0;
        this.page = 1;

        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseUp = this.onMouseUp.bind(this);
    }

    // Given an event.target, return the page number it happened on.
    getPage(el) {
        const pageEl = el.closest('.page');
        const pageNumber = pageEl.dataset.pageNumber;
        return pageNumber;
    }

    onMouseMove(e) {
        this.x = e.layerX;
        this.y = e.layerY;
        this.annotationController.onMouseMove(this.x, this.y);
    }

    // The layerY co-ordinates are off in this event for some reason,
    // so use the latest layerX/Y co-ordinates from onMouseMove.
    onMouseUp(e) {
        e.preventDefault();
        this.annotationController.onMouseUp(this.x, this.y, this.page);
    }

    onPageRendered(e) {
        const pageNumber = e.source.div.dataset.pageNumber;
        const pageEl = document.querySelector(
            '.page[data-page-number="' + pageNumber + '"]');
        pageEl.setAttribute('id', 'pdfjs-page-' + pageNumber);

        SVG().addTo('#pdfjs-page-' + pageNumber)
            .size('100%', '100%');
    }
}
