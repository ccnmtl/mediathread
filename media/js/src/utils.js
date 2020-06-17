import isFinite from 'lodash/isFinite';
import {
    Circle as CircleStyle, Fill, Stroke, Style
} from 'ol/style';
import MultiPoint from 'ol/geom/MultiPoint';

/**
 * A wrapper for `fetch` that passes along auth credentials.
 */
const authedFetch = function(url, method='get', data=null) {
    const elt = document.getElementById('csrf-token');
    const token = elt ? elt.getAttribute('content') : '';
    return fetch(url, {
        method: method,
        headers: {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': token
        },
        body: data,
        credentials: 'same-origin'
    });
};

const getAssets = function(
    title='', owner='', tags=[], terms=[], date='all',
    offset=0, orderBy='title'
) {
    const params = new URLSearchParams();

    // Pagination
    params.append('limit', 20);
    params.append('offset', offset);

    // Ordering
    // https://django-tastypie.readthedocs.io/en/latest/resources.html#ordering
    params.append('order_by', orderBy);

    // Always include the annotations
    params.append('annotations', true);

    if (title) {
        params.append('search_text', title);
    }

    if (date !== 'all') {
        params.append('modified', date);
    }

    if (tags && tags.length > 0) {
        params.append('tag', tags.map(tag => tag.value));
    }

    if (terms && terms.length > 0) {
        terms.forEach(function(term) {
            params.append(`vocabulary-${term.data.vocab_id}`, term.data.id);
        });
    }

    let basePath = '/api/asset/';
    if (owner && owner !== 'all') {
        basePath = `/api/asset/user/${owner}/`;
    }

    return authedFetch(basePath + '?' + params.toString())
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading assets: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

/**
 * Get annotation metadata.
 */
const getAsset = function(id=null) {
    let url = '/asset/';
    if (id) {
        url = `/api/asset/${id}/?annotations=true`;
    }
    return authedFetch(url)
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading asset: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

const getAssetReferences = function(id=null) {
    let url = `/asset/references/${id}/`;

    return authedFetch(url)
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading asset: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

const createSelection = function(assetId, data) {
    return authedFetch(
        `/asset/create/${assetId}/annotations/`,
        'post',
        JSON.stringify(data)
    ).then(function(response) {
        if (response.status === 200) {
            return response.json();
        } else {
            throw 'Error making selection: ' +
                `(${response.status}) ${response.statusText}`;
        }
    });
};

const createSherdNote = function(assetId, data) {
    return authedFetch(
        `/asset/${assetId}/sherdnote/create/`,
        'post',
        JSON.stringify(data)
    ).then(function(response) {
        if (response.status === 201) {
            return response.json();
        } else {
            return response.json().then(json => {
                let errorText = '';

                for (let key in json) {
                    errorText += `${key}: ${json[key]}\n`;
                }
                errorText = errorText.slice(0, -1);

                throw errorText;
            });
        }
    });
};

const deleteSelection = function(assetId, selectionId) {
    return authedFetch(
        `/asset/delete/${assetId}/annotations/${selectionId}/`,
        'post'
    ).then(function(response) {
        if (response.status === 200) {
            return response.json();
        } else {
            throw 'Error deleting selection: ' +
                `(${response.status}) ${response.statusText}`;
        }
    });
};

const getHours = function(totalSeconds) {
    return Math.floor(totalSeconds / 3600);
};

const getMinutes = function(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const seconds = totalSeconds - (hours * 3600);
    return Math.floor(seconds / 60);
};

const getSeconds = function(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
    const seconds = totalSeconds - (hours * 3600) - (minutes * 60);
    return Math.floor(seconds);
};

/**
 * Given a number of seconds as a float, return an array
 * containing [hours, minutes, seconds].
 */
const getSeparatedTimeUnits = function(totalSeconds) {
    return [
        getHours(totalSeconds),
        getMinutes(totalSeconds),
        getSeconds(totalSeconds)
    ];
};

const parseTimecode = function(str) {
    const parts = str.split(':');
    const col1 = Number(parts[0]);
    const col2 = Number(parts[1]);
    const col3 = Number(parts[2]);
    if (isFinite(col1) && isFinite(col2) && isFinite(col3)) {
        return (col1 * 60) + col2 + (col3 / 100);
    } else {
        return null;
    }
};

const pad2 = function(number) {
    return (number < 10 ? '0' : '') + number;
};

const formatTimecode = function(totalSeconds) {
    const units = getSeparatedTimeUnits(totalSeconds);
    return pad2(units[0]) + ':' + pad2(units[1]) + ':' + pad2(units[2]);
};

const capitalizeFirstLetter = function(str) {
    return str.length ?
        str.charAt(0).toUpperCase() + str.slice(1)
        : str;
};

/**
 * Display the day of an annotation object's modified time.
 * e.g. 05.08.2018
 *
 * Returns a string.
 */
const formatDay = function(obj) {
    const dateStr = obj.added;
    const date = new Date(Date.parse(dateStr));
    return date.toLocaleDateString(undefined, {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric'
    }).replace(/\//g, '.');
};

/**
 * Get asset type.
 *
 * This corresponds to Asset.primary_labels in
 * mediathread/assetmgr/models.py
 */
const getAssetType = function(primaryType) {
    let type = primaryType;

    if (
        primaryType === 'youtube' ||
            primaryType === 'vimeo' ||
            primaryType === 'mp4_pseudo' ||
            primaryType === 'mp4_panopto' ||
            primaryType === 'quicktime' ||
            primaryType === 'video_pseudo'
    ) {
        type = 'video';
    } else if (primaryType === 'image_fpxid' || primaryType === 'image_fpx') {
        type = 'image';
    }

    return type;
};

const handleBrokenImage = function(assetType) {
    this.src = `/media/img/thumb_${assetType}.png`;
};

/**
 * Get annotation/selection display openlayers styles.
 */
const getCoordStyles = function() {
    return [
        new Style({
            stroke: new Stroke({
                color: 'blue',
                width: 3
            }),
            fill: new Fill({
                color: 'rgba(0, 0, 255, 0.1)'
            })
        }),
        new Style({
            image: new CircleStyle({
                radius: 4,
                fill: new Fill({
                    color: 'orange'
                })
            }),
            geometry: function(feature) {
                // return the coordinates of the first ring of
                // the polygon
                var coordinates =
                    feature.getGeometry().getCoordinates()[0];
                return new MultiPoint(coordinates);
            }
        })
    ];
};

/**
 * Transform a relative geometry object to absolute, given a width,
 * height, and zoom.
 */
const transform = function(geometry, width, height, zoom) {
    return {
        type: geometry.type,
        coordinates: [
            geometry.coordinates[0].map(function(el) {
                return [
                    (width / 2) + (el[0] * (zoom * 2)),
                    (height / 2) + (el[1] * (zoom * 2))
                ];
            })
        ]
    };
};

export {
    getAssets, getAsset, getAssetReferences,
    createSelection, createSherdNote,
    deleteSelection,
    getHours, getMinutes, getSeconds,
    pad2, getSeparatedTimeUnits, formatTimecode, parseTimecode,
    capitalizeFirstLetter, formatDay, getAssetType,
    handleBrokenImage, getCoordStyles, transform
};
