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
window.onmessage = function(e){
    if (e.data === 'enableRectangleTool') {
        const svgEls = document.querySelectorAll('svg');
        svgEls.forEach(function(el) {
            el.style.cursor = 'crosshair';
            el.addEventListener(
                'mousemove', annotationInterface.onMouseMove);
            el.addEventListener(
                'mouseup', annotationInterface.onMouseUp);
        });
    } else if (e.data === 'disableRectangleTool') {
        const svgEls = document.querySelectorAll('svg');
        svgEls.forEach(function(el) {
            el.style.cursor = 'default';

            el.removeEventListener(
                'mousemove', annotationInterface.onMouseMove);
            el.removeEventListener(
                'mouseup', annotationInterface.onMouseUp);
        });
    }
};
