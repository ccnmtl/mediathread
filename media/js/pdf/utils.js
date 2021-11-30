/*
 * utils.js
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

// This is a magic number required by some scaling operations. This
// can be removed or renamed once we figure out what it is / why it's
// necessary.
const pdfjsScale = 0.75;

/**
 * Given co-ordinates for two points, return the co-ordinates that
 * Canvas or SVG expects:: top-left point x/y, then width/height.
 */
const convertPointsToXYWH = function(x1, y1, x2, y2, scale=1) {
    x1 *= scale;
    y1 *= scale;
    x2 *= scale;
    y2 *= scale;

    return [
        Math.min(x1, x2), Math.min(y1, y2),
        Math.abs(x2 - x1), Math.abs(y2 - y1)
    ];
};

/**
 * Render a PDF page, given the pdf.js page object, a canvas, width
 * and/or height, and optionally an annotation.
 *
 * If an annotation is passed in, focus in on that annotation.
 */
const renderPage = function(page, canvas, width, height, annotation=null) {
    // The 'width' argument may come in as null, or the string "100%",
    // if this view doesn't have a set width. In those cases, find the
    // canvas container's width and use that to constrain the PDF
    // view.
    if (!width || typeof width !== 'number') {
        width = jQuery(canvas).closest(
            '.sherd-pdfjs-view,.pdf-container').width();
    }

    // Get unmodified viewport for reference
    const viewport = page.getViewport({scale: 1});

    // Scale to the provided width or height, whichever is provided
    // and is smaller.
    let scale = (height / viewport.height);
    let xScale = width / viewport.width;
    scale = Math.min(xScale, scale);

    let offsetX = 0;
    let offsetY = 0;

    // Center in on annotation co-ordinates, if provided.
    if (annotation && annotation.geometry && annotation.geometry.coordinates) {
        const [ax, ay, aWidth, aHeight] = convertPointsToXYWH(
            annotation.geometry.coordinates[0][0],
            annotation.geometry.coordinates[0][1],
            annotation.geometry.coordinates[1][0],
            annotation.geometry.coordinates[1][1],
            pdfjsScale
        );

        // Amount of space between the zoomed view and the annotation
        // rect.
        const margin = 10;

        // Use either the annotation's width or its height to scale,
        // whichever is more zoomed-out, so we don't cut off portions
        // of it.
        scale = height / (aHeight + (margin * 2));
        let scaleX = width / (aWidth + (margin * 2));
        scale = Math.min(scaleX, scale);

        offsetX = (ax - margin) * scale;
        offsetY = (ay - margin) * scale;
    }

    const scaledViewport = page.getViewport({
        scale: scale,
        offsetX: -offsetX,
        offsetY: -offsetY
    });

    // Support HiDPI-screens.
    const outputScale = window.devicePixelRatio || 1;

    const context = canvas.getContext('2d');

    canvas.width = Math.floor(scaledViewport.width * outputScale);
    canvas.height = Math.floor(scaledViewport.height * outputScale);
    canvas.style.width = Math.floor(scaledViewport.width) + 'px';
    canvas.style.height =  Math.floor(scaledViewport.height) + 'px';

    const transform = outputScale !== 1
        ? [outputScale, 0, 0, outputScale, 0, 0]
        : null;

    const renderContext = {
        canvasContext: context,
        transform: transform,
        viewport: scaledViewport
    };

    return [page.render(renderContext), scale, offsetX, offsetY];
};

/**
 * Draw a rectangle annotation on the provided svgDraw surface, given
 * the annotation data.
 */
const drawAnnotation = function(
    svgDraw, annotation, scale=1, offsetX=0, offsetY=0
) {
    if (
        !annotation || !annotation.geometry ||
            !annotation.geometry.coordinates
    ) {
        console.error(
            'drawAnnotation error: coordinates not present',
            annotation);
        return;
    }

    const [x, y, width, height] = convertPointsToXYWH(
        annotation.geometry.coordinates[0][0],
        annotation.geometry.coordinates[0][1],
        annotation.geometry.coordinates[1][0],
        annotation.geometry.coordinates[1][1],
        pdfjsScale * scale
    );

    return svgDraw.rect(width, height)
        .move(x - offsetX, y - offsetY)
        .stroke({color: '#22f', width: 2})
        .fill('none');
};

export {pdfjsScale, convertPointsToXYWH, renderPage, drawAnnotation};
