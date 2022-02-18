/* global PDFViewerApplication */
/*
 * main.js
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
import AnnotationController from './AnnotationController.js';
import PdfJsAnnotationInterface from './PdfJsAnnotationInterface.js';

/**
 * This is the startup script for PDF annotation - all setup and
 * instantiation happens here.
 */

const annotationController = new AnnotationController();
const annotationInterface = new PdfJsAnnotationInterface(annotationController);

const state = {
    pagesLoaded: false,
    pageNumber: null,
    annotationTop: null,
    annotationLeft: null
};

const scrollToPage = function(page=1, top=0, left=0) {
    const margin = 40;
    const scale = annotationController.state.scale;

    // Scroll page into view.
    PDFViewerApplication.page = page;
    const pageDiv = document.querySelector(
        `.page[data-page-number="${page}"]`);
    PDFViewerApplication.pdfViewer._scrollIntoView({
        pageDiv: pageDiv,
        pageNumber: page,
        pageSpot: {
            top: (top - margin) * scale,
            left: left * scale
        }
    });
};

const viewSelection = function(e) {
    if (e.data.coordinates.length < 2) {
        return;
    }

    // Clear the page of the current selection, if there is one.
    if (annotationController.page) {
        annotationController.clearRect(annotationController.page);
    }

    const page = parseInt(e.data.page) || 1;
    annotationController.page = page;
    annotationController.rect = {
        coords: e.data.coordinates
    };

    const top = Math.min(e.data.coordinates[0][1], e.data.coordinates[1][1]);
    const left = Math.min(e.data.coordinates[0][0], e.data.coordinates[1][0]);

    // Scroll to the right page if the pages are loaded
    if (state.pagesLoaded) {
        scrollToPage(page, top, left);
    } else {
        // Otherwise, set state so this can be handled in the
        // pagesloaded event handler.
        state.pageNumber = page;
        state.annotationTop = top;
        state.annotationLeft = left;
    }

    annotationController.displayRect(
        e.data.coordinates[0][0],
        e.data.coordinates[0][1],
        e.data.coordinates[1][0],
        e.data.coordinates[1][1],
        annotationController.state.scale
    );
};

// Wait for the PDFViewerApplication to initialize
// https://stackoverflow.com/a/68489111/173630
PDFViewerApplication.initializedPromise.then(function() {
    PDFViewerApplication.eventBus.on('pagesloaded', function(e) {
        state.pagesLoaded = true;
        // Tell the react app that the PDF is loaded, in case anything
        // needs to happen there.
        window.top.postMessage({
            message: 'pdfLoaded'
        }, '*');

        if (state.pageNumber) {
            // This 200-millisecond setTimeout before scroll prevents
            // a pdf.js viewer debounce timing error. It's necessary
            // until I sort out a more elegant way to execute this at
            // the right time.
            setTimeout(function() {
                scrollToPage(
                    state.pageNumber,
                    state.annotationTop,
                    state.annotationLeft);
            }, 200);
        }
    });

    PDFViewerApplication.eventBus.on('pagerendered', function(e) {
        annotationInterface.onPageRendered(e);
        annotationController.onPageRendered();
    });

    PDFViewerApplication.eventBus.on('scalechanging', function(e) {
        annotationController.onZoomChange(e.scale);
    });
});

// iframe parent interaction
window.onmessage = function(e) {
    if (e.data === 'enableRectangleTool') {
        const svgEls = document.querySelectorAll('svg');
        svgEls.forEach(function(el) {
            el.style.cursor = 'crosshair';
            el.addEventListener(
                'mousemove', annotationInterface.onMouseMove);
            el.addEventListener(
                'mouseup', annotationInterface.onMouseUp);
            el.addEventListener(
                'mousedown', annotationInterface.onMouseDown);

            annotationController.clearRect();
        });
    } else if (e.data === 'disableRectangleTool') {
        const svgEls = document.querySelectorAll('svg');
        svgEls.forEach(function(el) {
            el.style.cursor = 'default';

            el.removeEventListener(
                'mousemove', annotationInterface.onMouseMove);
            el.removeEventListener(
                'mouseup', annotationInterface.onMouseUp);
            el.removeEventListener(
                'mousedown', annotationInterface.onMouseDown);

            annotationController.clearRect();
        });
    } else if (e.data === 'onClearSelection') {
        annotationController.clearRect();
    } else if (e.data.message && e.data.message === 'onViewSelection') {
        viewSelection(e);
    }
};
