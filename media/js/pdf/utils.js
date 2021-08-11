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

/**
 * Given co-ordinates for two points, return the co-ordinates that
 * Canvas or SVG expects:: top-left point x/y, then width/height.
 */
const convertPointsToXYWH = function(x1, y1, x2, y2, scale=1) {
    x1 = x1 * scale;
    y1 = y1 * scale;
    x2 = x2 * scale;
    y2 = y2 * scale;

    return [
        Math.min(x1, x2), Math.min(y1, y2),
        Math.abs(x2 - x1), Math.abs(y2 - y1)
    ];
};

export {convertPointsToXYWH};
