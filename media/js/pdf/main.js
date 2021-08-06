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

// Wait for the PDFViewerApplication to initialize
// https://stackoverflow.com/a/68489111/173630
PDFViewerApplication.initializedPromise.then(function() {
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
        });
    } else if (e.data === 'onClearSelection') {
        annotationController.clearRect();
    } else if (e.data.message && e.data.message === 'onViewSelection') {
        if (e.data.coordinates.length < 2) {
            return;
        }

        const page = parseInt(e.data.page);
        annotationController.page = page;
        annotationController.rect = {
            coords: e.data.coordinates
        };

        annotationController.displayRect(
            e.data.coordinates[0][0],
            e.data.coordinates[0][1],
            e.data.coordinates[1][0],
            e.data.coordinates[1][1],
            annotationController.state.scale
        );

        // Scroll selection into view.
        const pageDiv = document.getElementById('pdfjs-page-' + (page || 1));
        if (pageDiv) {
            PDFViewerApplication.pdfViewer._scrollIntoView({
                pageDiv: pageDiv
            });
        }
    }
};
